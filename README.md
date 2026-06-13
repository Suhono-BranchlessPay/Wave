# BranchlessPay Audit Shield — Wave Accounting Collector

Immutable audit trail for Wave invoices, payments, and transactions.

| Item | Value |
|------|-------|
| Scope | **M1 + M2** webhook/collector · **M3 + M4** verify display mapping |
| Local webhook | `POST http://127.0.0.1:8080/webhook/wave` |
| BP anchor API | `POST https://branchlesspay.com/api/v1/anchor` |
| GitHub | https://github.com/Suhono-BranchlessPay/Wave |
| Branch | **`dev` only** (private) |
| M2 status | **Complete** — all 4 event types verified |

---

## What this does

1. Wave fires a GraphQL webhook (`invoice.created`, `invoice.updated`, `payment.created`, `transaction.created`).
2. Collector verifies `Wave-Signature` (HMAC-SHA256).
3. Fetches full document from Wave GraphQL API (OAuth).
4. Normalizes to BranchlessPay anchor format.
5. POSTs to BranchlessPay → verify at `https://branchlesspay.com/verify/[anchor_id]`.

---

## Event mapping (M2)

| Wave event | BP `event_type` | Document |
|------------|-----------------|----------|
| `invoice.created` | `wave_invoice_created` | Invoice |
| `invoice.updated` | `wave_invoice_updated` | Invoice |
| `payment.created` | `wave_payment_received` | Payment |
| `transaction.created` | `wave_transaction_recorded` | Transaction |

---

## Quick start

```powershell
cd "Wave Accounting"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — BP_LICENSE_KEY, Wave OAuth, WAVE_BUSINESS_ID

$env:PYTHONPATH = "src"
python -m wave_bp_collector.app
```

Health check: http://127.0.0.1:8080/health

**Important:** After changing `.env`, restart the collector. The app reloads `.env` on each start (`load_dotenv(override=True)`).

---

## M2 E2E — test all event types

```powershell
# Unit tests + collector pipeline (all 4 events) + live invoice webhook
powershell -ExecutionPolicy Bypass -File scripts\run_m2_e2e.ps1

# Anchor a specific event (live Wave GraphQL fetch)
.\scripts\anchor_wave_event.ps1 -EventType invoice.created
.\scripts\anchor_wave_event.ps1 -EventType invoice.updated
.\scripts\anchor_wave_event.ps1 -EventType payment.created   # needs WAVE_TEST_PAYMENT_ID
.\scripts\anchor_wave_event.ps1 -EventType transaction.created  # needs WAVE_TEST_TRANSACTION_ID

# Dev simulate (signature skipped when WAVE_SKIP_SIGNATURE_VERIFY=1)
.\scripts\simulate_webhook.ps1 -EventType payment.created -ResourceId pay-test-1
```

### Screenshots (M2 deliverable)

| Event | Verify |
|-------|--------|
| `invoice.created` | [screenshot](docs/screenshots/01_invoice_created.png) · [live verify](https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4) |
| `invoice.updated` | [screenshot](docs/screenshots/02_invoice_updated.png) · [live verify](https://branchlesspay.com/verify/555be781-8795-4549-b865-04d589f45577) |
| `payment.created` | [screenshot](docs/screenshots/03_payment_created.png) · [verify](https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1) |
| `transaction.created` | [screenshot](docs/screenshots/04_transaction_created.png) · [verify](https://branchlesspay.com/verify/80691be3-7f41-4345-8b7e-b466780aaa02) |

See [docs/screenshots/README.md](docs/screenshots/README.md) for details.

---

## Helper scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_tests.ps1` | Python pytest + display tests |
| `scripts/run_m2_e2e.ps1` | Full M2 verification |
| `scripts/anchor_wave_event.ps1` | Live webhook → anchor (any event type) |
| `scripts/list_wave_invoices.ps1` | List Wave invoices via GraphQL |
| `scripts/get_wave_business_id.ps1` | Derive `WAVE_BUSINESS_ID` from dashboard UUID |
| `scripts/test_wave_token.ps1` | Validate Wave OAuth token |
| `scripts/simulate_webhook.ps1` | Local webhook POST (dev) |

---

## Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```

13 Python tests (signature, normalizer ×6, webhook handler ×5) + display mapping tests.

---

## Docs

| Guide | Topic |
|-------|-------|
| [docs/SETUP.md](docs/SETUP.md) | Install + configure |
| [docs/OAUTH.md](docs/OAUTH.md) | Wave OAuth flow |
| [docs/WAVE_TOKEN_SETUP.md](docs/WAVE_TOKEN_SETUP.md) | Access token + Wave Pro note |
| [docs/FIND_BUSINESS_ID.md](docs/FIND_BUSINESS_ID.md) | Business ID from dashboard URL |
| [docs/WEBHOOK_SETUP.md](docs/WEBHOOK_SETUP.md) | ngrok + webhook registration |
| [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md) | Test + E2E results |
| [MILESTONE_WAVE.md](MILESTONE_WAVE.md) | M1 + M2 checklist |

---

## Project layout

```
Wave Accounting/
├── display/                   # M3+M4 verify-page mapping
├── docs/screenshots/          # M2 E2E screenshots (4 events)
├── src/wave_bp_collector/     # M1+M2 Flask webhook pipeline
├── scripts/
├── tests/
├── MILESTONE_WAVE.md
└── MILESTONE_M3_M4.md
```

Contact: suhono@branchlesspay.com
