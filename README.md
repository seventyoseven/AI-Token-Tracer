# AI-CSR Monitor

**AI token tracking and environmental accountability for Odoo 19.**

Track every API call across OpenAI, Anthropic, Google, Mistral, and Cohere — with real-time cost, energy, and CO₂ metrics built in. Designed for the Odoo Hackathon 2025 CSR & Sustainability Tracker challenge.

---

## Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Permissions](#permissions)
- [Troubleshooting](#troubleshooting)
- [Data Model](#data-model)
- [Development](#development)
- [License](#license)

---

## Features

| Category | What's included |
|---|---|
| **Multi-provider tracking** | OpenAI, Anthropic, Google AI, Mistral, Cohere — extensible to any provider |
| **Cost management** | Per-call cost calculation, monthly budgets, automated email alerts |
| **CSR metrics** | Energy (kWh), CO₂ (kg), region-specific grid carbon intensity |
| **Analytics** | Dashboard, pivot tables, graphs — all native Odoo views |
| **API integration** | JSON-RPC endpoints for programmatic logging and status checks |
| **Security** | AES-256 API key encryption, three-tier access control, analytic account linking |

---

## Prerequisites

- Odoo 19.0 (Community or Enterprise)
- Python 3.10+
- `pycryptodome` for API key encryption

---

## Installation

### 1. Install Python dependency

```bash
pip install pycryptodome
```

For Odoo.sh, add to `requirements.txt`:

```
pycryptodome>=3.19.0
```

### 2. Add the module

Copy the `AI_token_tracker` folder into your Odoo addons directory.

### 3. Install in Odoo

```
Restart Odoo server
→ Apps → Update Apps List
→ Search "AI-CSR Monitor"
→ Install
```

---

## Configuration

### Providers

**AI Monitor → Configuration → Providers**

Five providers are pre-loaded: OpenAI, Anthropic, Google AI, Mistral AI, Cohere. Add custom providers by clicking **Create** and supplying a name, short code, API base URL, and website.

### AI Models

**AI Monitor → Configuration → AI Models**

Pre-loaded models:

| Model | Provider | Tier |
|---|---|---|
| GPT-4 Turbo, GPT-4, GPT-3.5 Turbo | OpenAI | High / Standard / Economy |
| Claude 3 Opus, Sonnet, Haiku | Anthropic | High / Standard / Economy |
| Gemini Ultra, Pro | Google | High / Standard |
| Mistral Large, Medium, Small | Mistral | High / Standard / Economy |

Each model record stores input/output cost per 1K tokens, energy consumption (Wh/1K tokens), context window size, and max output tokens.

### Grid Carbon Intensity

**AI Monitor → Configuration → Grid Carbon Intensity**

Pre-loaded regions and intensities:

| Region | gCO₂/kWh |
|---|---|
| US East (Virginia) | 388 |
| US West (Oregon) | 224 |
| EU West (Ireland) | 315 |
| Asia Pacific (Singapore) | 408 |
| Canada (Montreal) | 34 |

Add custom regions using your data center's published carbon intensity figures.

### Subscriptions

**AI Monitor → Operations → Subscriptions**

Create one subscription per AI service contract:

1. Enter a subscription name and select the provider.
2. Set a monthly budget and alert threshold (default 80%).
3. Paste your API key — it is encrypted with AES-256 on save.
4. Select the data center region used for CO₂ calculations.
5. Optionally link to an Odoo analytic account.
6. Click **Activate**.

---

## Usage

### Manual log entry

**AI Monitor → Operations → Usage Logs → Create**

Select a subscription and model, enter input and output token counts. Cost, energy, and CO₂ fields populate automatically.

### Programmatic logging

POST to the log endpoint from any application:

```python
import requests, json

payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "id": 1,
    "params": {
        "subscription_id": 1,
        "model_id": 5,
        "input_tokens": 1500,
        "output_tokens": 800,
        "application": "My App",
        "request_id": "req_abc123"
    }
}

r = requests.post(
    "https://your-odoo.com/ai_monitor/api/log_usage",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)

result = r.json()["result"]
print(f"Cost:   ${result['cost']:.4f}")
print(f"Energy: {result['energy_kwh']:.4f} kWh")
print(f"CO₂:    {result['co2_kg']:.4f} kg")
```

### Dashboard

**AI Monitor → Dashboard**

At a glance: active subscriptions, month-to-date spend, total energy and CO₂, budget warnings, top models by call volume, and a feed of recent usage entries.

---

## API Reference

All endpoints use JSON-RPC 2.0 and require an authenticated Odoo session or API key.

### `POST /ai_monitor/api/log_usage`

Record a single API call event.

**Request params**

| Field | Type | Required | Description |
|---|---|---|---|
| `subscription_id` | integer | ✓ | ID of the active subscription |
| `model_id` | integer | ✓ | ID of the AI model used |
| `input_tokens` | integer | ✓ | Prompt token count |
| `output_tokens` | integer | ✓ | Completion token count |
| `application` | string | | Calling application name |
| `request_id` | string | | Upstream request identifier |

**Response**

```json
{
  "result": {
    "log_id": 42,
    "cost": 0.0312,
    "energy_kwh": 0.0018,
    "co2_kg": 0.0007
  }
}
```

---

### `GET /ai_monitor/api/subscription/status/<id>`

Fetch budget and usage summary for one subscription.

**Response**

```json
{
  "result": {
    "data": {
      "name": "Production - OpenAI",
      "monthly_budget": 500.0,
      "current_spend": 187.43,
      "budget_consumption_pct": 37.5,
      "over_budget": false
    }
  }
}
```

---

### `POST /ai_monitor/api/models/recommend`

Return cheaper models that could replace the current one.

**Request params**

| Field | Type | Required | Description |
|---|---|---|---|
| `current_model_id` | integer | ✓ | ID of the model to compare against |

**Response**

```json
{
  "result": {
    "recommendations": [
      { "id": 3, "name": "GPT-3.5 Turbo", "savings_pct": 92.0 },
      { "id": 7, "name": "Claude 3 Haiku", "savings_pct": 87.5 }
    ]
  }
}
```

---

## Permissions

Three groups control access. Assign them under **Settings → Users → Access Rights**.

| Group | Capabilities |
|---|---|
| **AI Monitor User** | View subscriptions and logs, create usage log entries, view dashboard |
| **AI Monitor Manager** | All User rights + create/edit subscriptions, activate/suspend, manage providers and models |
| **AI Monitor Administrator** | All Manager rights + manage grid carbon intensity data, configure system settings |

---

## Automated Actions

| Action | Schedule | Purpose |
|---|---|---|
| Check Budget Alerts | Hourly | Emails subscription owner when spend crosses the alert threshold |
| Send Monthly Reports | 1st of month, 09:00 | CSR summary email: calls, cost, kWh, CO₂ |
| Archive Old Usage Logs | Weekly | Disabled by default — enable for data retention compliance |

Manage these under **Settings → Technical → Automation → Scheduled Actions**.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'Crypto'`

Install the correct package — `pycryptodome`, not `pycrypto`:

```bash
pip install pycryptodome
```

If both are installed, remove `pycrypto` first as they conflict.

---

### Dashboard shows blank or JavaScript errors

1. Clear browser cache and hard-reload (`Ctrl+Shift+R`).
2. Restart Odoo with `--dev=all` to force asset regeneration.
3. Check the browser console for specific errors and confirm Odoo 19 OWL components are loading.

---

### Budget alert emails are not arriving

1. Confirm the Odoo outgoing mail server is configured and tested (**Settings → Technical → Outgoing Mail Servers**).
2. Verify the scheduled action is active: **Settings → Technical → Automation → Scheduled Actions → AI Monitor: Check Budget Alerts**.
3. Check that the email template `AI Monitor: Budget Alert` exists and has valid recipients.

---

### CO₂ always shows 0.00 kg

Three fields must all be set:

1. The subscription has a **data center region** selected.
2. That region has a **grid intensity record** with a non-zero gCO₂/kWh value.
3. The AI model has an **energy consumption** value (Wh per 1K tokens) greater than zero.

---

## Data Model

```
ai_monitor.provider       One provider, many models and subscriptions
ai_monitor.model          Pricing, energy, and capability data per model
ai_monitor.grid_intensity Carbon intensity per geographic region
ai_monitor.subscription   Budget, API key, and region per service contract
ai_monitor.usage_log      One record per API call
```

Relationships:

```
provider ──< model
provider ──< subscription
grid_intensity ──< subscription
subscription ──< usage_log
model ──< usage_log
```

---

## Development

### Module structure

```
AI_token_tracker/
├── __manifest__.py
├── models/
│   ├── ai_monitor_provider.py
│   ├── ai_monitor_model.py
│   ├── ai_monitor_grid_intensity.py
│   ├── ai_monitor_subscription.py
│   └── ai_monitor_usage_log.py
├── views/
│   ├── ai_monitor_provider_views.xml
│   ├── ai_monitor_model_views.xml
│   ├── ai_monitor_subscription_views.xml
│   ├── ai_monitor_usage_log_views.xml
│   ├── ai_monitor_grid_intensity_views.xml
│   ├── ai_monitor_dashboard_views.xml
│   └── ai_monitor_menus.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
│   ├── ai_monitor_provider_data.xml
│   ├── ai_monitor_model_data.xml
│   ├── ai_monitor_grid_intensity_data.xml
│   ├── email_templates.xml
│   └── scheduled_actions.xml
├── controllers/
│   └── main.py
└── static/src/
    ├── components/
    │   ├── dashboard.js
    │   └── dashboard.xml
    └── css/
        ├── dashboard.css
        └── kanban.css
```

### Extending the module

To add new metrics or custom views:

1. Create a model that inherits from `ai_monitor.usage_log` or `ai_monitor.subscription`.
2. Add computed fields for your custom metric.
3. Register new views and menu items in XML.
4. Add new JSON-RPC routes in `controllers/main.py`.

---

## License

LGPL-3 — see [Odoo Community Association licensing guidelines](https://odoo-community.org/page/lgpl).

---

## Credits

- **Version**: 19.0.1.0.0
- **Odoo version**: 19.0
- **Challenge**: Odoo Hackathon 2025 — CSR & Sustainability Tracker
