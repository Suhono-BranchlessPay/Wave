# Test Results — Wave BP Collector

Branch: `dev`  
Date: 2026-06-13

---

## Automated tests

| Suite | Tests | Result |
|-------|-------|--------|
| `tests/test_signature.py` | 1 | PASS |
| `tests/test_normalizer.py` | 6 | PASS |
| `tests/test_webhook_handler.py` | 5 | PASS |
| `display/tests/waveVerifyMapping.test.mjs` | 7 | PASS |

Run: `powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1`

---

## M2 E2E — all event types

Run: `powershell -ExecutionPolicy Bypass -File scripts\run_m2_e2e.ps1`

| Wave event | BP `event_type` | Method | HTTP | Anchor ID | Verify |
|------------|-----------------|--------|------|-----------|--------|
| `invoice.created` | `wave_invoice_created` | Live Wave invoice #1 | 202 | `9d938e0d-e64d-44da-91fd-1345e2ab60a4` | [verify](https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4) |
| `invoice.updated` | `wave_invoice_updated` | Live Wave invoice #1 | 202 | `555be781-8795-4549-b865-04d589f45577` | [verify](https://branchlesspay.com/verify/555be781-8795-4549-b865-04d589f45577) |
| `payment.created` | `wave_payment_received` | Collector E2E + real BP | 202 | `587583dd-ef70-47c8-8c6f-ed4480e46ba1` | [verify](https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1) |
| `transaction.created` | `wave_transaction_recorded` | Collector E2E + real BP | 202 | `80691be3-7f41-4345-8b7e-b466780aaa02` | [verify](https://branchlesspay.com/verify/80691be3-7f41-4345-8b7e-b466780aaa02) |

Screenshots: [docs/screenshots/](screenshots/)

---

## Notes

- Invoice events use live Wave GraphQL fetch (BranchlessPay Inc, invoice #1, $1,500 USD).
- Payment/transaction events validated via `scripts/e2e_collector_all_events.py` (sample Wave documents, real BP API). Set `WAVE_TEST_PAYMENT_ID` / `WAVE_TEST_TRANSACTION_ID` in `.env` for live Wave fetch on those events.
- Wave STARTER plan: GraphQL + manual webhook simulate works; production webhooks may require Wave Pro + ngrok.

Contact: suhono@branchlesspay.com
