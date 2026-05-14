# ai_token_tracker/__manifest__.py
{
    'name': "AI Token Tracker",
    'version': '19.0.1.0.0',
    'summary': "Monitor AI API usage, cost, energy, and CO2 footprint for CSR and economic impact.",
    'description': """
        A comprehensive solution for businesses to monitor their AI API key usage.
        - Tracks token consumption, costs, and subscriptions.
        - Calculates energy consumption (kWh) and CO2 emissions (g).
        - Provides dashboards, Kanban views, and optimization suggestions.
        - Links AI usage to economic, environmental, and ethical impact.
    """,
    'author': "Hotkeys",
    'website': "https://IfOnlyWeHadAWebsite.com",
    'category': 'Productivity/AI',
    'license': 'OEEL-1',
    'depends': ['base', 'web', 'mail', 'account'],
    'data': [
        'security/ai_token_tracker_security.xml',
        'security/ir.model.access.csv',
        'data/default_user_groups.xml',
        'data/ai_token_tracker_cron.xml',
        'data/ai_token_tracker_grid_intensity.xml',
        'data/ai_providers_models.xml',
        'data/sample_data.xml',
        'views/ai_token_tracker_provider_views.xml',
        'views/ai_token_tracker_model_views.xml',
        'views/ai_token_tracker_subscription_views.xml',
        'views/ai_token_tracker_api_key_views.xml',
        'views/ai_token_tracker_usage_log_views.xml',
        'views/ai_token_tracker_suggestion_views.xml',
        'views/ai_token_tracker_grid_intensity_views.xml',
        'views/ai_token_tracker_menus.xml',
    ],
    'demo': [
        'demo/ai_token_tracker_model.xml',
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'AI_token_tracker/static/src/js/ai_token_tracker_dashboard.js',
            'AI_token_tracker/static/src/xml/ai_token_tracker_dashboard.xml',
            # Note: Chart.js is already included in Odoo 19
        ],
    },
    'external_dependencies': {
        'python': ['Cryptodome'],
    },
    'installable': True,
    'application': True,
    'auto_install': True,
}