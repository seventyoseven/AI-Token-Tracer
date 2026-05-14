# ai_token_tracker/models/ai_token_tracker_usage_log.py
from odoo import models, fields, api, _

class AiUsageLog(models.Model):
    _name = 'ai_token_tracker.usage_log'
    _description = 'AI API Usage Log'
    _order = 'create_date desc'

    name = fields.Char(compute='_compute_name', store=True)
    user_id = fields.Many2one(
        'res.users', 
        string='User', 
        default=lambda self: self.env.user,
        index=True
    )
    api_key_id = fields.Many2one(
        'ai_token_tracker.api_key', 
        string='API Key', 
        ondelete='restrict',
        index=True
    )
    model_id = fields.Many2one(
        'ai_token_tracker.model', 
        string='Model Used', 
        ondelete='restrict',
        index=True
    )
      
    purpose_category = fields.Selection([
        ('general', 'General'),
        ('rd', 'R&D'),
        ('support', 'Customer Support'),
        ('marketing', 'Marketing'),
        ('internal', 'Internal Tools'),
    ], string='Purpose', default='general', index=True,
       help="Categorizes the usage for ethical and economic auditing.")

    prompt_tokens = fields.Integer(string='Prompt Tokens')
    completion_tokens = fields.Integer(string='Completion Tokens')
    total_tokens = fields.Integer(
        compute='_compute_total_tokens', 
        store=True
    )
      
    # --- Immutable Benchmark Snapshot Fields ---
    # These are set by the create() override
    benchmark_cost_prompt_at_creation = fields.Float(
        string='Benchmark Cost/Prompt (USD)', 
        digits=(12, 10)
    )
    benchmark_cost_completion_at_creation = fields.Float(
        string='Benchmark Cost/Completion (USD)', 
        digits=(12, 10)
    )
    benchmark_energy_kwh_per_1k_at_creation = fields.Float(
        string='Benchmark Energy (kWh/1k)', 
        digits=(12, 10)
    )
    benchmark_grid_co2g_kwh_at_creation = fields.Float(
        string='Benchmark Grid (gCO2/kWh)', 
        digits=(10, 4)
    )
      
    # --- Computed CSR & Economic Metrics ---
    cost_usd = fields.Float(
        compute='_compute_csr_metrics', 
        store=True, 
        string='Cost (USD)',
        digits=(10, 6)
    )
    energy_consumed_kwh = fields.Float(
        compute='_compute_csr_metrics', 
        store=True, 
        string='Energy (kWh)',
        digits=(12, 10)
    )
    co2_emissions_g = fields.Float(
        compute='_compute_csr_metrics', 
        store=True, 
        string='CO2 (grams)',
        digits=(12, 6)
    )

    @api.depends('prompt_tokens', 'completion_tokens')
    def _compute_total_tokens(self):
        """Computes the total tokens used."""
        for record in self:
            record.total_tokens = record.prompt_tokens + record.completion_tokens

    @api.depends('total_tokens',
                 'prompt_tokens',
                 'completion_tokens',
                 'benchmark_cost_prompt_at_creation', 
                 'benchmark_cost_completion_at_creation', 
                 'benchmark_energy_kwh_per_1k_at_creation', 
                 'benchmark_grid_co2g_kwh_at_creation')
    def _compute_csr_metrics(self):
        """
        Computes the final cost, energy, and CO2
        based on the immutable benchmark data.
        """
        for record in self:
            # 1. Calculate Cost
            cost = (record.prompt_tokens * record.benchmark_cost_prompt_at_creation) + \
                   (record.completion_tokens * record.benchmark_cost_completion_at_creation)
            record.cost_usd = cost
              
            # 2. Calculate Energy
            # Energy benchmark is per 1k tokens
            energy_kwh = (record.total_tokens / 1000.0) * record.benchmark_energy_kwh_per_1k_at_creation
            record.energy_consumed_kwh = energy_kwh
              
            # 3. Calculate CO2
            # CO2 (g) = Energy (kWh) * Grid Intensity (gCO2/kWh)
            co2_g = energy_kwh * record.benchmark_grid_co2g_kwh_at_creation
            record.co2_emissions_g = co2_g

    @api.depends('create_date', 'model_id.name')
    def _compute_name(self):
        for record in self:
            if record.create_date:
                date_str = record.create_date.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = "N/A"
            record.name = f"Log - {record.model_id.name or 'N/A'} - {date_str}"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides create to snapshot benchmark data,
        ensuring historical data integrity.
        """
        for vals in vals_list:
            if vals.get('model_id'):
                model = self.env['ai_token_tracker.model'].browse(vals['model_id'])
                  
                # Set benchmark values at creation time
                vals['benchmark_cost_prompt_at_creation'] = model.cost_per_prompt_token_usd
                vals['benchmark_cost_completion_at_creation'] = model.cost_per_completion_token_usd
                vals['benchmark_energy_kwh_per_1k_at_creation'] = model.energy_kwh_per_1k_tokens
                  
                # Determine grid intensity
                grid_intensity = 0.0
                if model.grid_intensity_id:
                    grid_intensity = model.grid_intensity_id.co2g_per_kwh
                elif model.provider_id.grid_intensity_id:
                    grid_intensity = model.provider_id.grid_intensity_id.co2g_per_kwh
                vals['benchmark_grid_co2g_kwh_at_creation'] = grid_intensity

        return super(AiUsageLog, self).create(vals_list)