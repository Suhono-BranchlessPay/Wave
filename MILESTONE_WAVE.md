# Milestone — Wave × BranchlessPay (M1 + M2)

Repo: https://github.com/Suhono-BranchlessPay/Wave  
Branch: **`dev` only**  
Status: **M1 + M2 complete** (2026-06-13)

---

## M1 — Webhook receiver

| Deliverable | Status |
|-------------|--------|
| `POST /webhook/wave` | ✅ |
| `Wave-Signature` HMAC-SHA256 | ✅ |
| Parse GraphQL webhook JSON | ✅ |
| Dev simulate script | ✅ |
| Docs | ✅ |

---

## M2 — Normalize + BP anchor

| Deliverable | Status |
|-------------|--------|
| Wave GraphQL client (`wave_client.py`) | ✅ |
| Normalizer + BP poster | ✅ |
| Idempotency + failed queue | ✅ |
| OAuth docs | ✅ |
| Unit tests (13 tests) | ✅ |
| All 4 event types — collector pipeline | ✅ |
| Live E2E — Wave invoice + BP anchor | ✅ |
| Screenshots (4 events) | ✅ `docs/screenshots/` |

---

## Event mapping

| Wave | BP `event_type` | E2E |
|------|-----------------|-----|
| `invoice.created` | `wave_invoice_created` | ✅ Live Wave invoice #1 |
| `invoice.updated` | `wave_invoice_updated` | ✅ Live Wave invoice #1 |
| `payment.created` | `wave_payment_received` | ✅ Collector E2E + BP |
| `transaction.created` | `wave_transaction_recorded` | ✅ Collector E2E + BP |

Run: `powershell -ExecutionPolicy Bypass -File scripts\run_m2_e2e.ps1`

Contact: suhono@branchlesspay.com
