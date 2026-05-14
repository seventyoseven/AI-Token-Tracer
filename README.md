# AI Token Tracker — Odoo 19 Module

**Version**: 19.0.1.0.0 | **Author**: Hotkeys | **License**: OEEL-1 | **Category**: Productivity/AI

## Description

AI Token Tracker is an Odoo 19 module that gives businesses complete visibility into their AI API spend, environmental footprint, and optimization opportunities — all from within Odoo.

The module lets you register AI subscriptions (OpenAI, Anthropic, Google AI, Mistral, Cohere, and others), attach encrypted API keys, and log token usage either manually or via a JSON-RPC API. Every usage log automatically calculates cost in USD, energy consumed in kWh, and CO2 emissions in grams using immutable benchmark snapshots taken at creation time, so historical records stay accurate even when model pricing changes.

A built-in optimization engine runs daily, analyzes recent usage logs across your subscriptions, and surfaces actionable suggestions to switch from expensive high-tier models to cheaper alternatives for general or support workloads. Suggestions track potential and actual savings separately and move through a review workflow (New → Reviewing → Implemented / Rejected).

The module integrates with Odoo's `mail` module for chatter and activity tracking on subscriptions and suggestions, with `account` for analytic account linking, and ships with a live OWL dashboard showing key metrics, budget health indicators, and top model usage at a glance.

---

## Features

- **Multi-provider support** — Pre-configured data for OpenAI, Anthropic, Google AI, Mistral AI, and Cohere, including per-model pricing and energy benchmarks
- **Usage logging** — Log prompt tokens, completion tokens, cost, energy, and CO2 per API call; categorize by purpose (General, R&D, Support, Marketing, Internal Tools)
- **Immutable cost snapshots** — Benchmark pricing and grid carbon intensity are captured at log creation so historical reports are never affected by future price changes
- **Budget management** — Set monthly USD budgets per subscription; get automated hourly alerts and monthly CSR email reports
- **Spend prediction** — Linear projection of next-month spend based on the current month's daily run rate, with On Track / Approaching Limit / Over Budget health indicator
- **Optimization suggestions** — Daily cron engine identifies high-volume workloads on expensive models and recommends cheaper alternatives with quantified cost and energy savings
- **AES-256 API key encryption** — All API keys stored encrypted via `pycryptodome`
- **Analytic account integration** — Link subscription costs to Odoo analytic accounts for management reporting
- **OWL dashboard** — Real-time key metrics, budget consumption bars, top models, and recent usage logs
- **Three-tier access control** — User, Manager, and Administrator roles with granular record-level permissions
- **RESTful JSON-RPC API** — Endpoints to log usage, query subscription status, and fetch model recommendations from external applications

---

## Requirements

- Odoo 19.0 (Community or Enterprise)
- Python 3.10+
- [`pycryptodome`](https://pypi.org/project/pycryptodome/) library

---

## Installation

**1. Install the Python dependency**

```bash
pip install pycryptodome
```

For Odoo.sh, add to `requirements.txt`:

```
pycryptodome>=3.19.0
```

**2. Copy the module**

Place the `AI_token_tracker` folder in your Odoo addons directory.

**3. Install in Odoo**

```
Apps → Update Apps List → search "AI Token Tracker" → Install
```

---

## Configuration

### Providers & Models

Navigate to **AI Monitor → Configuration → Providers** and **AI Models**.

Pre-loaded providers include OpenAI, Anthropic, Google AI, Mistral AI, and Cohere. Each model carries cost-per-token (input/output), energy consumption (Wh per 1k tokens), performance tier, and context window size.

### Grid Carbon Intensity

Navigate to **AI Monitor → Configuration → Grid Carbon Intensity**.

Pre-loaded regions:

| Region | Intensity |
|---|---|
| US East (Virginia) | 388 gCO2/kWh |
| US West (Oregon) | 224 gCO2/kWh |
| EU West (Ireland) | 315 gCO2/kWh |
| Asia Pacific (Singapore) | 408 gCO2/kWh |
| Canada (Montreal) | 34 gCO2/kWh |

Add custom regions as needed.

### Subscriptions

Navigate to **AI Monitor → Operations → Subscriptions**:

1. Enter a subscription name and select a provider
2. Set a monthly budget (USD) and alert threshold (default 80%)
3. Add one or more API keys — they are encrypted automatically with AES-256
4. Select a data center region for CO2 calculations
5. Optionally link to an analytic account
6. Click **Activate**

---

## Usage

### Manual usage logging

Go to **AI Monitor → Operations → Usage Logs → New**, select an API key and model, enter prompt and completion token counts. Cost, energy, and CO2 are computed automatically.

### API integration

Log usage from external systems via JSON-RPC:

```python
import requests, json

url = "http://your-odoo.com/ai_monitor/api/log_usage"
payload = {
    "jsonrpc": "2.0", "method": "call", "id": 1,
    "params": {
        "subscription_id": 1,
        "model_id": 5,
        "input_tokens": 1500,
        "output_tokens": 800,
        "application": "My App",
        "request_id": "req_12345"
    }
}
result = requests.post(url, json=payload).json()["result"]
print(f"Cost: ${result['cost']:.4f} | Energy: {result['energy_kwh']:.4f} kWh | CO2: {result['co2_kg']:.4f} kg")
```

### Other API endpoints

| Endpoint | Description |
|---|---|
| `POST /ai_monitor/api/log_usage` | Log an API usage event |
| `GET /ai_monitor/api/subscription/status/<id>` | Get budget status for a subscription |
| `POST /ai_monitor/api/models/recommend` | Get cheaper model recommendations |

All endpoints use JSON-RPC 2.0 and require Odoo session authentication.

---

## Dashboard

Navigate to **AI Monitor → Dashboard** to view:

- Active subscriptions, monthly cost, total energy, and CO2 at a glance
- Budget consumption bars with color-coded health status
- Top models by usage volume
- Recent usage log entries

---

## Automated Actions

| Action | Schedule |
|---|---|
| Check Budget Alerts | Every hour |
| Send Monthly CSR Reports | 1st of each month at 09:00 |
| Run Optimization Analysis | Daily |
| Archive Old Usage Logs | Weekly (disabled by default) |

Configure under **Settings → Technical → Automation → Scheduled Actions**.

---

## Security & Permissions

| Group | Capabilities |
|---|---|
| AI Monitor User | View subscriptions and logs, create usage logs, view dashboard |
| AI Monitor Manager | All User rights + create/modify/activate subscriptions, manage providers and models |
| AI Monitor Administrator | All Manager rights + manage grid carbon intensity data |

Assign groups under **Settings → Users & Companies → Users → Access Rights**.

---

## Data Model

```
provider (1) ─────────────► (*) model
provider (1) ─────────────► (*) subscription
subscription (1) ──────────► (*) api_key
api_key (1) ───────────────► (*) usage_log
model (1) ─────────────────► (*) usage_log
grid_intensity (1) ────────► (*) model / subscription
model (many) ◄──────────── suggestion ──────────► model (many)
```

### Models

| Technical Name | Description |
|---|---|
| `ai_token_tracker.provider` | AI service providers |
| `ai_token_tracker.model` | AI models with pricing, energy, and tier data |
| `ai_token_tracker.grid_intensity` | Regional carbon intensity (gCO2/kWh) |
| `ai_token_tracker.subscription` | Subscriptions with budgets, API keys, and analytic links |
| `ai_token_tracker.api_key` | AES-256 encrypted API keys, linked to a subscription |
| `ai_token_tracker.usage_log` | Individual API call records with cost, energy, and CO2 |
| `ai_token_tracker.suggestion` | Optimization suggestions from the daily analysis engine |

---

## Module Structure

```
AI_token_tracker/
├── __manifest__.py
├── __init__.py
├── controllers/
│   └── main.py                          # JSON-RPC API endpoints
├── models/
│   ├── ai_token_tracker_provider.py
│   ├── ai_token_tracker_model.py
│   ├── ai_token_tracker_grid_intensity.py
│   ├── ai_token_tracker_api_key.py      # AES-256 encryption logic
│   ├── ai_token_tracker_subscription.py # Budget, spend, predictions
│   ├── ai_token_tracker_usage_log.py    # Token logging & CSR metrics
│   └── ai_token_tracker_suggestion.py  # Optimization engine (cron)
├── views/
│   ├── ai_token_tracker_provider_views.xml
│   ├── ai_token_tracker_model_views.xml
│   ├── ai_token_tracker_subscription_views.xml
│   ├── ai_token_tracker_api_key_views.xml
│   ├── ai_token_tracker_usage_log_views.xml
│   ├── ai_token_tracker_suggestion_views.xml
│   ├── ai_token_tracker_grid_intensity_views.xml
│   └── ai_token_tracker_menus.xml
├── data/
│   ├── ai_providers_models.xml          # Seeded providers and models
│   ├── ai_token_tracker_grid_intensity.xml
│   ├── ai_token_tracker_cron.xml
│   ├── email_templates.xml
│   └── sample_data.xml
├── demo/
│   └── demo_data.xml
├── security/
│   ├── ai_token_tracker_security.xml    # Groups and record rules
│   └── ir.model.access.csv
└── static/src/
    ├── js/ai_token_tracker_dashboard.js # OWL dashboard component
    ├── xml/ai_token_tracker_dashboard.xml
    └── css/
        ├── dashboard.css
        └── kanban.css
```

---

## Troubleshooting

**Module won't install — missing `Crypto` module**
Run `pip install pycryptodome` and restart the Odoo server.

**Dashboard not loading — JavaScript errors in browser console**
Clear browser cache, restart Odoo with `--dev=all`, and update the assets bundle.

**Budget alert emails not sending**
Verify Odoo outgoing mail is configured, check that the `Check Budget Alerts` scheduled action is active, and confirm the `AI Monitor: Budget Alert` email template exists.

**CO2 showing as 0.00 g**
Ensure the subscription has a data center region selected, that grid intensity data exists for that region, and that the model has an energy consumption value set.

---

## Development Notes

- Built for Odoo 19 using OWL components and modern ORM patterns
- Chart.js is included in Odoo 19 and does not need a separate import
- Benchmark fields on `usage_log` are immutable snapshots — they are set in `create()` and should never be written to after creation
- The optimization engine uses `SET work_mem = '256MB'` before its analysis query for performance on large log tables

---

## Credits

- **Module**: AI Token Tracker
- **Author**: Hotkeys
- **Odoo Version**: 19.0
- **Built for**: Odoo Hackathon 2025 — CSR & Sustainability Tracker challenge
