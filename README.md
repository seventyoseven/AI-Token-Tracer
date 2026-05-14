# AI-CSR Monitor - AI Token Tracker for Odoo 19

## Overview

The AI-CSR Monitor is a comprehensive Odoo 19 module designed to track AI API usage, costs, and Corporate Social Responsibility (CSR) metrics including energy consumption and carbon footprint. This module helps organizations monitor their AI spending, optimize model selection, and measure the environmental impact of their AI operations.

## Features

### 📊 Comprehensive Monitoring
- **Multi-Provider Support**: Track usage across OpenAI, Anthropic, Google AI, Mistral, Cohere, and more
- **Real-Time Tracking**: Monitor API calls, token usage, and costs in real-time
- **Budget Management**: Set monthly budgets with automated alerts
- **Usage Analytics**: Detailed logs with pivot tables, graphs, and dashboards

### 🌱 CSR & Environmental Tracking
- **Energy Consumption**: Track energy usage (kWh) per API call
- **Carbon Footprint**: Calculate CO2 emissions based on data center location
- **Grid Intensity**: Support for region-specific carbon intensity data
- **Sustainability Reports**: Monthly CSR reports with environmental impact metrics

### 💰 Cost Optimization
- **Performance Tiers**: Models categorized by performance level
- **Cost Comparison**: Compare pricing across different models
- **Optimization Recommendations**: API endpoint to suggest cheaper alternatives
- **Budget Alerts**: Automated email notifications when approaching budget limits

### 🔒 Security & Integration
- **API Key Encryption**: Secure AES-256 encryption for API keys
- **Accounting Integration**: Link to Odoo's analytic accounts
- **User Permissions**: Three-tier access control (User, Manager, Administrator)
- **RESTful API**: JSON endpoints for external integrations

## Installation

### Prerequisites

1. **Odoo 19.0** (Community or Enterprise)
2. **Python 3.10+**
3. **pycryptodome** library for encryption

### Install Dependencies

```bash
pip install pycryptodome
```

For Odoo.sh deployments, add to your `requirements.txt`:
```
pycryptodome>=3.19.0
```

### Install Module

1. Copy the `AI_token_tracker` folder to your Odoo addons directory
2. Restart your Odoo server
3. Update the apps list: Go to Apps → Update Apps List
4. Search for "AI-CSR Monitor"
5. Click "Install"

## Configuration

### 1. Set Up Providers

Navigate to **AI Monitor → Configuration → Providers**

The module comes pre-configured with major AI providers:
- OpenAI
- Anthropic
- Google AI
- Mistral AI
- Cohere

### 2. Configure AI Models

Navigate to **AI Monitor → Configuration → AI Models**

Pre-configured models include:
- GPT-4 Turbo, GPT-4, GPT-3.5 Turbo (OpenAI)
- Claude 3 Opus, Sonnet, Haiku (Anthropic)
- Gemini Pro, Ultra (Google)
- Mistral Large, Medium, Small

Each model includes:
- Cost per 1K tokens (input/output)
- Energy consumption data
- Performance tier classification
- Context window size

### 3. Set Up Grid Carbon Intensity

Navigate to **AI Monitor → Configuration → Grid Carbon Intensity**

Pre-configured regions:
- US East (Virginia): 388 gCO2/kWh
- US West (Oregon): 224 gCO2/kWh
- EU West (Ireland): 315 gCO2/kWh
- Asia Pacific (Singapore): 408 gCO2/kWh
- Canada (Montreal): 34 gCO2/kWh

Add custom regions as needed for your data centers.

### 4. Create Subscriptions

Navigate to **AI Monitor → Operations → Subscriptions**

For each AI service subscription:
1. Enter subscription name
2. Select provider
3. Set monthly budget
4. Configure alert threshold (default: 80%)
5. Add API key (encrypted automatically)
6. Select data center region for CO2 calculations
7. Optionally link to an analytic account
8. Activate the subscription

## Usage

### Manual Usage Logging

Navigate to **AI Monitor → Operations → Usage Logs** and create a new record:
- Select subscription
- Select AI model
- Enter input/output tokens
- Cost and CSR metrics are calculated automatically

### API Integration

Use the JSON-RPC API to log usage programmatically:

```python
import requests
import json

url = "http://your-odoo-instance.com/ai_monitor/api/log_usage"
headers = {"Content-Type": "application/json"}

data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "subscription_id": 1,
        "model_id": 5,
        "input_tokens": 1500,
        "output_tokens": 800,
        "application": "My Application",
        "request_id": "req_12345"
    },
    "id": 1
}

response = requests.post(url, headers=headers, data=json.dumps(data))
result = response.json()
print(f"Cost: ${result['result']['cost']:.4f}")
print(f"Energy: {result['result']['energy_kwh']:.4f} kWh")
print(f"CO2: {result['result']['co2_kg']:.4f} kg")
```

### Check Subscription Status

```python
url = "http://your-odoo-instance.com/ai_monitor/api/subscription/status/1"
response = requests.post(url, headers=headers, data=json.dumps({
    "jsonrpc": "2.0",
    "method": "call",
    "params": {},
    "id": 1
}))
status = response.json()['result']['data']
print(f"Budget used: {status['budget_consumption_pct']:.1f}%")
print(f"Over budget: {status['over_budget']}")
```

### Get Model Recommendations

```python
url = "http://your-odoo-instance.com/ai_monitor/api/models/recommend"
data = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "current_model_id": 5
    },
    "id": 1
}
response = requests.post(url, headers=headers, data=json.dumps(data))
recommendations = response.json()['result']['recommendations']
for rec in recommendations:
    print(f"{rec['name']}: {rec['savings_pct']:.1f}% savings")
```

## Dashboard

Navigate to **AI Monitor → Dashboard** to view:
- **Key Metrics**: Active subscriptions, monthly costs, energy usage, CO2 emissions
- **Budget Alerts**: Visual warnings for subscriptions over budget
- **Top Models**: Most frequently used AI models
- **Active Subscriptions**: Budget consumption progress bars
- **Recent Usage**: Latest API calls with cost and token details

## Automated Features

### Budget Alerts

The module automatically checks budgets every hour. When a subscription reaches its alert threshold:
- An email is sent to the subscription creator
- The dashboard displays a warning banner
- Budget consumption is highlighted in red

### Monthly Reports

On the 1st of each month at 9:00 AM, the system sends CSR reports for all active subscriptions including:
- Total API calls
- Total cost and budget consumption
- Energy consumption (kWh)
- Carbon emissions (kg CO2)

### Scheduled Actions

Configure in **Settings → Technical → Automation → Scheduled Actions**:
- `AI Monitor: Check Budget Alerts` (every hour)
- `AI Monitor: Send Monthly Reports` (monthly)
- `AI Monitor: Archive Old Usage Logs` (weekly, disabled by default)

## Security & Permissions

### User Groups

1. **AI Monitor User**
   - View subscriptions and usage logs
   - Create usage logs
   - View dashboard

2. **AI Monitor Manager**
   - All User permissions
   - Create/modify subscriptions
   - Activate/suspend subscriptions
   - Manage providers and models

3. **AI Monitor Administrator**
   - All Manager permissions
   - Manage grid carbon intensity data
   - Configure system settings

### Assigning Permissions

Go to **Settings → Users & Companies → Users**:
1. Select a user
2. Go to the "Access Rights" tab
3. Assign appropriate AI Monitor group

## API Endpoints

All endpoints use JSON-RPC 2.0 format and require user authentication.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai_monitor/api/log_usage` | POST | Log an API usage event |
| `/ai_monitor/api/subscription/status/<id>` | GET | Get subscription status |
| `/ai_monitor/api/models/recommend` | POST | Get model recommendations |

## Data Model

### Main Models

- `ai_monitor.provider`: AI service providers
- `ai_monitor.model`: AI models with pricing and energy data
- `ai_monitor.grid_intensity`: Carbon intensity by region
- `ai_monitor.subscription`: User subscriptions with budgets
- `ai_monitor.usage_log`: Individual API call records

### Key Relationships

```
provider (1) -----> (*) model
provider (1) -----> (*) subscription
subscription (1) --> (*) usage_log
model (1) ---------> (*) usage_log
grid_intensity (1) -> (*) subscription
```

## Troubleshooting

### Module Won't Install

**Issue**: Error about missing `Crypto` module

**Solution**: Install pycryptodome:
```bash
pip install pycryptodome
```

### Dashboard Not Loading

**Issue**: JavaScript errors in browser console

**Solution**: 
1. Clear browser cache
2. Restart Odoo in development mode: `--dev=all`
3. Update assets bundle

### Budget Alerts Not Sending

**Issue**: No emails received when threshold reached

**Solution**:
1. Check email server configuration in Odoo
2. Verify scheduled action is active: Settings → Technical → Scheduled Actions
3. Check email template: AI Monitor: Budget Alert

### CO2 Calculations are Zero

**Issue**: CO2 emissions showing as 0.00 kg

**Solution**:
1. Ensure subscription has a data center region selected
2. Verify grid intensity data exists for the region
3. Check that models have energy consumption values configured

## Customization

### Adding New Providers

1. Navigate to **Configuration → Providers**
2. Click "Create"
3. Enter provider details:
   - Name (e.g., "Hugging Face")
   - Code (e.g., "HUGGINGFACE")
   - API Base URL
   - Website

### Adding New Models

1. Navigate to **Configuration → AI Models**
2. Click "Create"
3. Fill in model details:
   - Name, provider, type
   - Performance tier
   - Pricing (input/output cost per 1K tokens)
   - Energy consumption (Wh per 1K tokens)
   - Context window and max output tokens

### Custom Grid Intensity Data

1. Navigate to **Configuration → Grid Carbon Intensity**
2. Click "Create"
3. Enter:
   - Region name
   - Carbon intensity (gCO2/kWh)
   - Data source
   - Notes

## Development

### Module Structure

```
AI_token_tracker/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── ai_monitor_provider.py
│   ├── ai_monitor_grid_intensity.py
│   ├── ai_monitor_model.py
│   ├── ai_monitor_subscription.py
│   └── ai_monitor_usage_log.py
├── views/
│   ├── ai_monitor_provider_views.xml
│   ├── ai_monitor_model_views.xml
│   ├── ai_monitor_subscription_views.xml
│   ├── ai_monitor_usage_log_views.xml
│   ├── ai_monitor_grid_intensity_views.xml
│   ├── ai_monitor_menus.xml
│   └── ai_monitor_dashboard_views.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
│   ├── ai_monitor_provider_data.xml
│   ├── ai_monitor_model_data.xml
│   ├── ai_monitor_grid_intensity_data.xml
│   ├── email_templates.xml
│   └── scheduled_actions.xml
├── demo/
│   └── demo_data.xml
├── controllers/
│   ├── __init__.py
│   └── main.py
├── static/src/
│   ├── components/
│   │   ├── dashboard.js
│   │   └── dashboard.xml
│   └── css/
│       ├── dashboard.css
│       └── kanban.css
└── README.md
```

### Extending the Module

To add custom functionality:

1. Create a new model that inherits from existing models
2. Add computed fields for custom metrics
3. Create custom views and actions
4. Register new API endpoints in controllers

## Support & Contributing

### Getting Help

- Check the documentation in this README
- Review Odoo 19 official documentation
- Contact your organization's Odoo administrator

### Contributing

This module is designed for the Odoo Hackathon 2025 CSR & Sustainability Tracker challenge.

## License

LGPL-3

## Credits

- **Author**: Your Organization
- **Version**: 19.0.1.0.0
- **Odoo Version**: 19.0

---

**Note**: This module is designed for Odoo 19. It uses modern Odoo development patterns including OWL components, proper ORM usage, and follows Odoo coding guidelines.
