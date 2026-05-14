# ai_token_tracker/models/ai_token_tracker_grid_intensity.py
from odoo import models, fields

class AiGridIntensity(models.Model):
    _name = 'ai_token_tracker.grid_intensity'
    _description = 'Grid Carbon Intensity Factor'

    name = fields.Char(
        string='Region/Grid Name', 
        required=True, 
        help="e.g., 'US East (Virginia)', 'EU (Ireland)', 'Global Average'"
    )
    co2g_per_kwh = fields.Float(
        string='CO2g per kWh', 
        digits=(10, 4),  # Allows precision for grams
        required=True,
        help="Grams of CO2 equivalent emitted per kilowatt-hour."
    )
    notes = fields.Text(string='Source/Notes')