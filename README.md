# BranchlessPay Audit Shield — Wave Accounting Collector

Immutable audit trail for Wave invoices, payments, and transactions.

| Item | Value |
|------|-------|
| Scope | **M1 + M2** webhook/collector · **M3 + M4** verify display mapping |
| Local webhook | `POST http://127.0.0.1:8080/webhook/wave` |
| BP anchor API | `POST https://branchlesspay.com/api/v1/anchor` |
| GitHub | https://github.com/Suhono-BranchlessPay/Wave |
| Branch | **`dev` only** (private) |

---

## What this does

1. Wave fires a GraphQL webhook (`invoice.created`, `payment.created`, etc.).
2. Collector verifies `Wave-Signature` (HMAC-SHA256).
3. Fetches full document from Wave GraphQL API (OAuth).
4. Normalizes to BranchlessPay anchor format.
5. POSTs to BranchlessPay → verify at `https://branchlesspay.com/verify/[anchor_id]`.

---

## Quick start

```powershell
cd "Wave Accounting"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — BP_LICENSE_KEY, Wave OAuth, webhook secret

$env:PYTHONPATH = "src"
python -m wave_bp_collector.app
```

Health check: http://127.0.0.1:8080/health

Guides: [docs/SETUP.md](docs/SETUP.md) · [docs/WEBHOOK_SETUP.md](docs/WEBHOOK_SETUP.md) · [docs/OAUTH.md](docs/OAUTH.md)

---

## Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```

---

## Project layout

```
Wave Accounting/
├── display/                   # M3+M4 verify-page mapping
├── src/wave_bp_collector/     # M1+M2 Flask webhook pipeline
├── tests/
├── docs/
├── MILESTONE_WAVE.md
└── MILESTONE_M3_M4.md
```

Contact: suhono@branchlesspay.com
