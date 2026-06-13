# BranchlessPay Audit Shield — Wave Accounting Collector

Immutable audit trail for Wave invoices, payments, and transactions.

| Item | Value |
|------|-------|
| Scope | **M1 + M2** webhook/collector · **M3 + M4** verify display mapping ✅ |
| Local webhook | `POST http://127.0.0.1:8080/webhook/wave` |
| BP anchor API | `POST https://branchlesspay.com/api/v1/anchor` |
| GitHub | https://github.com/Suhono-BranchlessPay/Wave |
| Branch | **`dev` only** (private) |
| M2 status | **Complete** — all 4 event types verified |
| M3+M4 status | **Complete** — verify mapping + fixtures (BP merge pending) |

---

## What this does

1. Wave fires a GraphQL webhook (`invoice.created`, `invoice.updated`, `payment.created`, `transaction.created`).
2. Collector verifies `Wave-Signature` (HMAC-SHA256).
3. Fetches full document from Wave GraphQL API (OAuth).
4. Normalizes to BranchlessPay anchor format.
5. POSTs to BranchlessPay → verify at `https://branchlesspay.com/verify/[anchor_id]`.
6. **M3+M4:** `display/src/waveVerifyMapping.ts` renders Business + Transaction sections on the verify page.

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

**Important:** After changing `.env`, restart the collector.

---

## M2 E2E — test all event types

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_m2_e2e.ps1
.\scripts\anchor_wave_event.ps1 -EventType invoice.created
```

Screenshots: [docs/screenshots/](docs/screenshots/)

---

## M3 + M4 — Verify page mapping

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_m3_m4_tests.ps1

cd display
npm test
npm run preview
```

| Sample URL | Event |
|------------|-------|
| [verify/9d938e0d…](https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4) | `invoice.created` |
| [verify/587583dd…](https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1) | `payment.created` |

| Doc | Topic |
|-----|-------|
| [M3_FIELD_MAPPING.md](docs/M3_FIELD_MAPPING.md) | Field mapping table |
| [M4_VERIFY_INTEGRATION.md](docs/M4_VERIFY_INTEGRATION.md) | BP VerifyPage merge guide |
| [M3_M4_TEST_RESULTS.md](docs/M3_M4_TEST_RESULTS.md) | Test results |

Implementation: `display/src/waveVerifyMapping.ts` · Example: `display/src/VerifyPageIntegration.example.tsx`

---

## Helper scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_tests.ps1` | Python pytest + display tests |
| `scripts/run_m2_e2e.ps1` | Full M2 verification |
| `scripts/run_m3_m4_tests.ps1` | M3+M4 display tests + live URL check |
| `scripts/anchor_wave_event.ps1` | Live webhook → anchor (any event type) |
| `scripts/list_wave_invoices.ps1` | List Wave invoices via GraphQL |
| `scripts/get_wave_business_id.ps1` | Derive `WAVE_BUSINESS_ID` |
| `scripts/test_wave_token.ps1` | Validate Wave OAuth token |
| `scripts/simulate_webhook.ps1` | Local webhook POST (dev) |

---

## Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```

13 Python tests + 11 display mapping tests.

---

## Docs

| Guide | Topic |
|-------|-------|
| [docs/SETUP.md](docs/SETUP.md) | Install + configure |
| [docs/OAUTH.md](docs/OAUTH.md) | Wave OAuth flow |
| [docs/WAVE_TOKEN_SETUP.md](docs/WAVE_TOKEN_SETUP.md) | Access token + Wave Pro note |
| [docs/FIND_BUSINESS_ID.md](docs/FIND_BUSINESS_ID.md) | Business ID from dashboard URL |
| [docs/WEBHOOK_SETUP.md](docs/WEBHOOK_SETUP.md) | ngrok + webhook registration |
| [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md) | M2 E2E results |
| [MILESTONE_WAVE.md](MILESTONE_WAVE.md) | M1 + M2 checklist |
| [MILESTONE_M3_M4.md](MILESTONE_M3_M4.md) | M3 + M4 checklist |

---

## Project layout

```
Wave Accounting/
├── display/                   # M3+M4 verify-page mapping + fixtures
├── docs/screenshots/          # M2 E2E screenshots
├── src/wave_bp_collector/     # M1+M2 Flask webhook pipeline
├── scripts/
├── tests/
├── MILESTONE_WAVE.md
└── MILESTONE_M3_M4.md
```

Contact: suhono@branchlesspay.com
