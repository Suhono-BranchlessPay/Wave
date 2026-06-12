# M3 Field Mapping — Wave Verify Page

Implementation: `display/src/waveVerifyMapping.ts`

## Business Information

| Label | Source | Fallback |
|-------|--------|----------|
| Business | `metadata.business_name` | `company_name`, `-` |
| Address | `metadata.business_address` | `-` |
| ERP System | hardcoded | `"Wave Accounting"` |

## Transaction Details

| Label | Source | Notes |
|-------|--------|-------|
| Reference | `metadata.invoice_number` | else `reference_id` |
| Document Type | event label map | see below |
| Party | `metadata.contact_name` | |
| Date | `voucher_date` or `metadata.create_date` | |
| Due Date | `metadata.due_date` | hidden if null |
| Amount | `amount` + `currency` | USD/CAD |
| Status | `metadata.status` | badge map |

## Event labels

| `event_type` | Display |
|--------------|---------|
| `wave_invoice_created` | Wave Invoice |
| `wave_invoice_updated` | Wave Invoice (Updated) |
| `wave_payment_received` | Wave Payment |
| `wave_transaction_recorded` | Wave Transaction |

## Status badges

| Wave status | Variant |
|-------------|---------|
| UNPAID | blue (`unpaid`) |
| PAID | green (`paid`) |
| OVERDUE | red (`overdue`) |
| DRAFT | grey (`draft`) |
| PARTIAL | yellow (`partial`) |

Sample verify reference: https://branchlesspay.com/verify/190023f7-8e9d-404f-a4e3-8a8f63fc46e3
