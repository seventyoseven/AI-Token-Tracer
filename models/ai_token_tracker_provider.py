# ai_token_tracker/models/ai_token_tracker_provider.py
from odoo import models, fields

class AiProvider(models.Model):
    _name = 'ai_token_tracker.provider'
    _description = 'AI Model Provider'

    name = fields.Char(string='Provider Name', required=True)
    website = fields.Char(string='Website')
    notes = fields.Text(string='Notes')
      
    # Default grid for this provider if not specified on the model
    grid_intensity_id = fields.Many2one(
        'ai_token_tracker.grid_intensity', 
        string='Default Grid Intensity'
    )
    model_ids = fields.One2many(
        'ai_token_tracker.model', 
        'provider_id', 
        string='Models'
    )