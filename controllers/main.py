# ai_token_tracker/controllers/main.py
from odoo import http
from odoo.http import request
from odoo.tools.date_utils import start_of, end_of
from odoo.tools.misc import format_amount
import datetime

class AITokenTrackerDashboardController(http.Controller):

    def _get_date_range(self, date_filter):
        """Helper to get date ranges."""
        today = datetime.date.today()
        if date_filter == 'last_30_days':
            start_date = today - datetime.timedelta(days=30)
            end_date = today
        elif date_filter == 'this_quarter':
            start_date = start_of(today, 'quarter')
            end_date = end_of(today, 'quarter')
        else: # Default: 'this_month'
            start_date = start_of(today, 'month')
            end_date = end_of(today, 'month')
        return (start_date, end_date)

    @http.route('/ai_token_tracker/get_kpis', type='jsonrpc', auth='user')
    def get_kpis(self, date_filter='this_month'):
        """Fetches the main KPIs for the dashboard."""
        start_date, end_date = self._get_date_range(date_filter)
        domain = [('create_date', '>=', start_date), ('create_date', '<=', end_date)]

        # Read groups are efficient
        usage_data = request.env['ai_token_tracker.usage_log'].read_group(
            domain,
            ['cost_usd:sum', 'energy_consumed_kwh:sum', 'co2_emissions_g:sum'],
            []
        )
          
        savings_data = request.env['ai_token_tracker.suggestion'].read_group(
            [('state', '=', 'implemented'), ('write_date', '>=', start_date), ('write_date', '<=', end_date)],
            ['actual_energy_saving_kwh:sum', 'actual_cost_saving_usd:sum'],
            []
        )
          
        data = usage_data[0] if usage_data else {}
        savings = savings_data[0] if savings_data else {}
          
        total_co2_kg = (data.get('co2_emissions_g', 0) or 0) / 1000.0

        today = datetime.date.today()
        current_spend = data.get('cost_usd', 0) or 0
        current_energy = data.get('energy_consumed_kwh', 0) or 0
        
        # Calculate days elapsed and total days in period
        days_elapsed = (today - start_date).days + 1  # +1 to include today
        total_days = (end_date - start_date).days + 1
        
        # Linear projection
        if days_elapsed > 0 and days_elapsed < total_days:
            daily_spend_rate = current_spend / days_elapsed
            daily_energy_rate = current_energy / days_elapsed
            
            predicted_spend = daily_spend_rate * total_days
            predicted_energy = daily_energy_rate * total_days
        else:
            # If we're at the end of the period, prediction = actual
            predicted_spend = current_spend
            predicted_energy = current_energy
        
        # Calculate budget health across all active subscriptions
        subscriptions = request.env['ai_token_tracker.subscription'].search([
            ('state', '=', 'active')
        ])
        total_budget = sum(subscriptions.mapped('monthly_budget_usd'))
        
        budget_health = 'good'  # Default
        if total_budget > 0:
            projected_utilization = (predicted_spend / total_budget) * 100
            if projected_utilization <= 85:
                budget_health = 'good'
            elif projected_utilization <= 100:
                budget_health = 'warning'
            else:
                budget_health = 'danger'
        
        # Calculate days remaining (for display)
        days_remaining = max(0, (end_date - today).days)

        return {
            'total_cost_usd': f"{data.get('cost_usd', 0) or 0:,.2f}",
            'total_energy_kwh': f"{data.get('energy_consumed_kwh', 0) or 0:,.3f}",
            'total_co2_kg': f"{total_co2_kg:,.2f}",
            'total_savings_kwh': f"{savings.get('actual_energy_saving_kwh', 0) or 0:,.3f}",
            'total_savings_usd': f"{savings.get('actual_cost_saving_usd', 0) or 0:,.2f}",
            # Projected period-end fields
            'predicted_spend': f"{predicted_spend:,.2f}",
            'predicted_energy': f"{predicted_energy:,.3f}",
            'total_budget': f"{total_budget:,.2f}",
            'projected_utilization': f"{projected_utilization:.1f}" if total_budget > 0 else "0.0",
            'budget_health': budget_health,
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
        }

    @http.route('/ai_token_tracker/get_chart_data', type='jsonrpc', auth='user')
    def get_chart_data(self, date_filter='this_month'):
        """Fetches data for all dashboard charts."""
        start_date, end_date = self._get_date_range(date_filter)
        domain = [('create_date', '>=', start_date), ('create_date', '<=', end_date)]

        # Chart 1: Energy by Model
        energy_by_model = request.env['ai_token_tracker.usage_log'].read_group(
            domain,
            ['energy_consumed_kwh:sum'],
            ['model_id']
        )
        model_names = {m['id']: m['name'] for m in request.env['ai_token_tracker.model'].search_read(
            [('id', 'in', [d['model_id'][0] for d in energy_by_model if d['model_id']])], ['name']
        )}
          
        energy_chart_data = {
            'labels': [model_names.get(d['model_id'][0], 'N/A') for d in energy_by_model if d['model_id']],
            'datasets': [{
                'data': [d['energy_consumed_kwh'] for d in energy_by_model if d['model_id']],
                'backgroundColor': '#714b67',
            }]
        }

        # Chart 2: Cost by Purpose
        cost_by_purpose = request.env['ai_token_tracker.usage_log'].read_group(
            domain,
            ['cost_usd:sum'],
            ['purpose_category']
        )
        purpose_labels = dict(request.env['ai_token_tracker.usage_log']._fields['purpose_category'].selection)
          
        cost_chart_data = {
            'labels': [purpose_labels.get(d['purpose_category'], 'N/A') for d in cost_by_purpose if d['purpose_category']],
            'datasets': [{
                'data': [d['cost_usd'] for d in cost_by_purpose if d['purpose_category']],
                'backgroundColor': ['#714b67', '#8a6a93', '#a38bab', '#beadca', '#d9cfe3'],
            }]
        }

        # Chart 3: Cost vs. Savings Over Time (Last 12 Months)
        # This chart ignores the date_filter
          
        #... (Implementation for line chart query - omitted for brevity)...

        return {
            'energy_by_model': energy_chart_data,
            'cost_by_purpose': cost_chart_data,
        }