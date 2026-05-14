# ai_token_tracker/models/ai_token_tracker_suggestion.py
from odoo import models, fields, api
from odoo.tools.date_utils import start_of

class AiSuggestion(models.Model):
    _name = 'ai_token_tracker.suggestion'
    _description = 'AI Optimization Suggestion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'state, potential_cost_saving_usd desc'

    name = fields.Char(compute='_compute_name', store=True)
      
    # The usage logs that triggered this suggestion
    origin_usage_log_ids = fields.Many2many(
        'ai_token_tracker.usage_log', 
        'ai_suggestion_usage_log_rel',
        'suggestion_id', 'log_id',
        string='Source Usage Logs'
    )
      
    model_to_replace_id = fields.Many2one(
        'ai_token_tracker.model', 
        string='Current Model', 
        required=True
    )
    suggested_model_id = fields.Many2one(
        'ai_token_tracker.model', 
        string='Suggested Model', 
        required=True
    )
      
    state = fields.Selection([
        ('new', 'New'),
        ('reviewing', 'Reviewing'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
    ], string='Status', default='new', required=True, tracking=True)
      
    analysis_date = fields.Date(string='Analysis Date', default=fields.Date.context_today)
      
    # Potential savings (Calculated by cron)
    potential_cost_saving_usd = fields.Float(string='Potential Cost Saving (USD)', readonly=True)
    potential_energy_saving_kwh = fields.Float(string='Potential Energy Saving (kWh)', readonly=True)
      
    # Actual savings (Copied on 'implemented' state change)
    actual_cost_saving_usd = fields.Float(string='Actual Cost Saving (USD)', readonly=True)
    actual_energy_saving_kwh = fields.Float(string='Actual Energy Saving (kWh)', readonly=True)

    rejection_reason = fields.Text(string='Rejection Reason')

    @api.depends('model_to_replace_id.name', 'suggested_model_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Suggest: {rec.model_to_replace_id.name or 'N/A'} -> {rec.suggested_model_id.name or 'N/A'}"
              
    def write(self, vals):
        """
        Overrides write to capture when a suggestion is implemented,
        moving 'potential' savings to 'actual' savings.
        """
        if 'state' in vals and vals['state'] == 'implemented':
            for rec in self:
                if rec.state != 'implemented': # Only on first move to implemented
                    vals['actual_cost_saving_usd'] = rec.potential_cost_saving_usd
                    vals['actual_energy_saving_kwh'] = rec.potential_energy_saving_kwh
        return super(AiSuggestion, self).write(vals)

    def action_reject(self):
        # This could open a wizard to ask for rejection_reason
        self.write({'state': 'rejected'})

    def action_review(self):
        self.write({'state': 'reviewing'})

    # --- Scheduled Action Method ---
      
    @api.model
    def _run_optimization_analysis(self):
        """
        This is the "Data Science" engine. It runs daily via cron
        to find optimization opportunities.
        """
        self.env.cr.execute("SET work_mem = '256MB';") # Optimize for large queries
          
        # 1. Get all available models, tiered for searching
        all_models = self.env['ai_token_tracker.model'].search([('active', '=', True)])
        models_by_tier = {
            'tier_1': all_models.filtered(lambda m: m.performance_tier == 'tier_1'),
            'tier_2': all_models.filtered(lambda m: m.performance_tier == 'tier_2'),
            'tier_3': all_models.filtered(lambda m: m.performance_tier == 'tier_3'),
        }

        # 2. Define search parameters
        analysis_date = fields.Datetime.subtract(fields.Datetime.now(), days=7)
          
        # 3. Find high-volume usage on expensive, general-purpose tasks
        logs = self.env['ai_token_tracker.usage_log'].search([
            ('create_date', '>=', analysis_date),
            ('purpose_category', 'in', ['general', 'support']),
            ('model_id.performance_tier', 'in', ['tier_1', 'tier_2'])
        ])
          
        if not logs:
            return # No work to do

        # 4. Group logs by model
        logs_by_model = {}
        for log in logs:
            if log.model_id not in logs_by_model:
                logs_by_model[log.model_id] = []
            logs_by_model[log.model_id].append(log)

        # 5. Iterate and find savings
        suggestions_to_create = []
        for current_model, model_logs in logs_by_model.items():
            # Find cheaper models in the same or lower tier
            target_tiers = []
            if current_model.performance_tier == 'tier_1':
                target_tiers = ['tier_1', 'tier_2']
            elif current_model.performance_tier == 'tier_2':
                target_tiers = ['tier_2', 'tier_3']
            
            if not target_tiers:
                continue
              
            search_domain = [
                ('performance_tier', 'in', target_tiers),
                ('id', '!=', current_model.id),
                ('cost_per_prompt_token_usd', '<', current_model.cost_per_prompt_token_usd)
            ]
              
            suggested_models = self.env['ai_token_tracker.model'].search(search_domain, order='cost_per_prompt_token_usd ASC', limit=1)
              
            if suggested_models:
                suggested_model = suggested_models
                  
                # 6. Calculate potential savings for this batch of logs
                current_cost = sum(log.cost_usd for log in model_logs)
                current_energy = sum(log.energy_consumed_kwh for log in model_logs)
                  
                potential_cost = 0.0
                potential_energy = 0.0
                  
                for log in model_logs:
                    # Calculate what the cost WOULD have been
                    potential_cost += (log.prompt_tokens * suggested_model.cost_per_prompt_token_usd) + \
                                      (log.completion_tokens * suggested_model.cost_per_completion_token_usd)
                    # Calculate what the energy WOULD have been
                    potential_energy += (log.total_tokens / 1000.0) * suggested_model.energy_kwh_per_1k_tokens

                cost_saving = current_cost - potential_cost
                energy_saving = current_energy - potential_energy

                # 7. Create suggestion if savings are meaningful
                if cost_saving > 1.0 or energy_saving > 0.01:
                    suggestions_to_create.append({
                        'model_to_replace_id': current_model.id,
                        'suggested_model_id': suggested_model.id,
                        'potential_cost_saving_usd': cost_saving,
                        'potential_energy_saving_kwh': energy_saving,
                        'origin_usage_log_ids': [(6, 0, [log.id for log in model_logs])],
                        'state': 'new',
                    })

        # 8. Batch create suggestions
        if suggestions_to_create:
            self.env['ai_token_tracker.suggestion'].create(suggestions_to_create)