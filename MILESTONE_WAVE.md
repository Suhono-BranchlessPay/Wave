# Milestone — Wave × BranchlessPay (M1 + M2)

Repo: https://github.com/Suhono-BranchlessPay/Wave  
Branch: **`dev` only**  
Status: **In development** — scaffold complete, awaiting Wave trial + BP token E2E

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
| Unit tests | ✅ |
| Live E2E with Wave trial | ⏳ User setup |

---

## Event mapping

| Wave | BP `event_type` |
|------|-----------------|
| `invoice.created` | `wave_invoice_created` |
| `invoice.updated` | `wave_invoice_updated` |
| `payment.created` | `wave_payment_received` |
| `transaction.created` | `wave_transaction_recorded` |

Contact: suhono@branchlesspay.com
