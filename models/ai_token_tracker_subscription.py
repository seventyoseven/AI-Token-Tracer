# ai_token_tracker/models/ai_token_tracker_subscription.py
from odoo import models, fields, api
from odoo.tools.date_utils import start_of, end_of

class AiSubscription(models.Model):
    _name = 'ai_token_tracker.subscription'
    _description = 'AI API Subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Subscription Name', required=True, tracking=True)
    provider_id = fields.Many2one('ai_token_tracker.provider', string='Provider', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', help="The vendor for this subscription.")
      
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 
        string='Analytic Account',
        help="Link costs from this subscription to an analytic account."
    )
      
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    monthly_budget_usd = fields.Float(string='Monthly Budget (USD)', tracking=True)
      
    api_key_ids = fields.One2many('ai_token_tracker.api_key', 'subscription_id', string="API Keys")
      
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    notes = fields.Text(string='Notes')
      
    total_spend_current_month = fields.Float(
        compute='_compute_spend_current_month',
        string='Current Month Spend (USD)',
        store=True,
    )
    budget_utilization_percent = fields.Float(
        compute='_compute_spend_current_month',
        string='Budget Utilization',
        store=True,
        help="Current spend as a percentage of monthly budget."
    )

    predicted_next_month_spend = fields.Float(
        compute='_compute_predictions',
        string='Predicted Next Month',
        store=False,  # Recompute live each time
        help="Linear projection based on current month's spending rate"
    )

    budget_health = fields.Selection([
        ('good', 'On Track'),
        ('warning', 'Approaching Limit'),
        ('danger', 'Over Budget Risk'),
    ], compute='_compute_predictions', string='Budget Health')

    @api.depends('total_spend_current_month', 'monthly_budget_usd')
    def _compute_predictions(self):
        today = fields.Date.today()
        month_start = start_of(today, 'month')
        days_elapsed = (today - month_start).days + 1  # +1 to include today
        
        # Get actual days in current month
        month_end = end_of(today, 'month')
        days_in_month = (month_end - month_start).days + 1
        
        for sub in self:
            if days_elapsed > 0:
                daily_rate = sub.total_spend_current_month / days_elapsed
                sub.predicted_next_month_spend = daily_rate * days_in_month
                
                # Calculate budget health
                if sub.monthly_budget_usd > 0:
                    projected_utilization = (sub.predicted_next_month_spend / sub.monthly_budget_usd) * 100
                    if projected_utilization <= 85:
                        sub.budget_health = 'good'
                    elif projected_utilization <= 100:
                        sub.budget_health = 'warning'
                    else:
                        sub.budget_health = 'danger'
                else:
                    sub.budget_health = 'good'
            else:
                sub.predicted_next_month_spend = 0.0
                sub.budget_health = 'good'

    @api.depends('api_key_ids.usage_log_ids.cost_usd', 'monthly_budget_usd')
    def _compute_spend_current_month(self):
        today = fields.Date.today()
        month_start = start_of(today, 'month')
        month_end = end_of(today, 'month')
          
        # Aggregate spend per subscription
        spend_data = self.env['ai_token_tracker.usage_log'].read_group(
            [
                ('api_key_id.subscription_id', 'in', self.ids),
                ('create_date', '>=', month_start),
                ('create_date', '<=', month_end)
            ],
            ['cost_usd:sum'],
            ['api_key_id']
        )
        
        # Correctly map spend data from api_key_id to subscription_id
        api_key_to_sub_map = {k.id: k.subscription_id.id for k in self.env['ai_token_tracker.api_key'].search([('subscription_id', 'in', self.ids)])}
        spend_map = {}
        for data in spend_data:
            api_key_id = data['api_key_id'][0]
            sub_id = api_key_to_sub_map.get(api_key_id)
            if sub_id:
                spend_map[sub_id] = spend_map.get(sub_id, 0.0) + data['cost_usd']

        for sub in self:
            spend = spend_map.get(sub.id, 0.0)
            sub.total_spend_current_month = spend
            if sub.monthly_budget_usd > 0:
                sub.budget_utilization_percent = (spend / sub.monthly_budget_usd) * 100.0
            else:
                sub.budget_utilization_percent = 0.0

    def action_activate(self):
        self.write({'state': 'active'})

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_draft(self):
        self.write({'state': 'draft'})