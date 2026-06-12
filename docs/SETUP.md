# Wave Setup Guide

## 1. Prerequisites

| Item | Notes |
|------|-------|
| Wave account | https://waveapps.com (free) |
| Wave developer app | https://developer.waveapps.com |
| ngrok or tunnel | For local webhook testing |
| BP test token | `BP_LICENSE_KEY` via WhatsApp from BP |

## 2. Install

```powershell
cd "Wave Accounting"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## 3. Configure `.env`

| Variable | Source |
|----------|--------|
| `BP_LICENSE_KEY` | BranchlessPay test token |
| `WAVE_ACCESS_TOKEN` | Developer portal full access token or OAuth |
| `WAVE_BUSINESS_ID` | Wave business GraphQL ID |
| `WAVE_WEBHOOK_SECRET` | Wave webhook registration response |

Optional for verify page display:

- `WAVE_BUSINESS_NAME`
- `WAVE_BUSINESS_ADDRESS`

## 4. Run collector

```powershell
$env:PYTHONPATH = "src"
python -m wave_bp_collector.app
```

Or: `powershell -ExecutionPolicy Bypass -File scripts\run_server.ps1`

## 5. Test flow

1. Start ngrok: `ngrok http 8080`
2. Register webhook URL: `https://YOUR-NGROK/webhook/wave`
3. Create test invoice in Wave
4. Watch logs for `Pipeline complete verify_url=...`
5. Open verify URL in browser

See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) and [OAUTH.md](OAUTH.md).
