# ai_token_tracker/models/ai_token_tracker_model.py
from odoo import models, fields

class AiModel(models.Model):
    _name = 'ai_token_tracker.model'
    _description = 'AI Model Benchmark'
    _order = 'performance_tier, name'

    name = fields.Char(string='Model Name', required=True, help="e.g., 'GPT-4o', 'Llama 3 70B'")
    model_key = fields.Char(string='Model API Key', required=True, help="The string used in the API call, e.g., 'gpt-4o'")
    provider_id = fields.Many2one('ai_token_tracker.provider', string='Provider', required=True)
      
    performance_tier = fields.Selection([
        ('tier_1', 'Tier 1 (Highest Performance)'),
        ('tier_2', 'Tier 2 (General Purpose)'),
        ('tier_3', 'Tier 3 (Fast & Light)'),
    ], string='Performance Tier', required=True, default='tier_2')

    cost_per_prompt_token_usd = fields.Float(
        string='Cost/Prompt Token (USD)', 
        digits=(16, 10), 
        help="Cost in USD for 1 prompt token."
    )
    cost_per_completion_token_usd = fields.Float(
        string='Cost/Completion Token (USD)', 
        digits=(16, 10),
        help="Cost in USD for 1 completion token."
    )
    energy_kwh_per_1k_tokens = fields.Float(
        string='Energy (kWh) per 1k Tokens', 
        digits=(16, 10),
        help="Estimated energy in kWh per 1000 total tokens (prompt + completion)."
    )
    
    # Display fields for list view to avoid scientific notation
    cost_prompt_display = fields.Char(
        string='Cost/Prompt Token', 
        compute='_compute_display_fields',
        help="Formatted cost per prompt token"
    )
    cost_completion_display = fields.Char(
        string='Cost/Completion Token',
        compute='_compute_display_fields', 
        help="Formatted cost per completion token"
    )
    
    def _compute_display_fields(self):
        """Format very small float values to avoid scientific notation"""
        for record in self:
            # Format with 10 decimal places, remove trailing zeros
            record.cost_prompt_display = f"${record.cost_per_prompt_token_usd:.10f}".rstrip('0').rstrip('.')
            record.cost_completion_display = f"${record.cost_per_completion_token_usd:.10f}".rstrip('0').rstrip('.')
      
    grid_intensity_id = fields.Many2one(
        'ai_token_tracker.grid_intensity', 
        string='Data Center Grid Intensity',
        help="The specific grid for this model. Falls back to provider default if empty."
    )
      
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)