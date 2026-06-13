# M3 Field Mapping — Wave Verify Page

Implementation: `display/src/waveVerifyMapping.ts`

Sample verify URLs (live QA):

| Event | URL |
|-------|-----|
| `invoice.created` | https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4 |
| `payment.created` | https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1 |

Fixtures: `display/fixtures/`

---

## Business Information

| Label | Source | Fallback |
|-------|--------|----------|
| Business | `metadata.business_name` | `company_name`, `-` |
| Address | `metadata.business_address` | `-` |
| ERP System | hardcoded | `"Wave Accounting"` |

---

## Transaction Details

| Label | Source | Notes |
|-------|--------|-------|
| Reference | `metadata.invoice_number` | else `reference_id` |
| Document Type | event label map | see below |
| Customer | `metadata.contact_name` | Payment/invoice |
| Description | `reference_id` | Transaction only |
| Date | `voucher_date` / `payment_date` / `transaction_date` | Event-specific |
| Due Date | `metadata.due_date` | Invoice events only |
| Amount | `amount` + `currency` | USD/CAD |
| Status | `metadata.status` | Hidden for transactions |

---

## Event labels

| `event_type` | Display |
|--------------|---------|
| `wave_invoice_created` | Wave Invoice |
| `wave_invoice_updated` | Wave Invoice (Updated) |
| `wave_payment_received` | Wave Payment |
| `wave_transaction_recorded` | Wave Transaction |

---

## Status badges

| Wave status | Label | Variant |
|-------------|-------|---------|
| UNPAID | Unpaid | `unpaid` |
| PAID | Paid | `paid` |
| OVERDUE | Overdue | `overdue` |
| DRAFT | Draft | `draft` |
| PARTIAL | Partial | `partial` |
| SAVED | Saved | `saved` |
| SENT | Sent | `sent` |
| VIEWED | Viewed | `sent` |

---

## Helper API

| Function | Purpose |
|----------|---------|
| `isWaveAnchor(anchor)` | Detect Wave records on verify page |
| `mapWaveVerifyPage(anchor)` | Full M3+M4 output for VerifyPage |
| `buildPdfEvidenceFields(anchor)` | PDF audit footer |
| `buildVerificationInstructions(anchor)` | User-facing copy |

See [M4_VERIFY_INTEGRATION.md](M4_VERIFY_INTEGRATION.md) for BP merge steps.
