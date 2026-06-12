# Wave Webhook Setup

## Endpoint (local dev)

| Item | Value |
|------|--------|
| **URL** | `https://YOUR-TUNNEL/webhook/wave` |
| **Method** | POST |
| **Content-Type** | application/json |

Production URL will be provided by BranchlessPay when platform webhook ships.

## Events (M1+M2)

| Wave event | BP `event_type` |
|------------|-----------------|
| `invoice.created` | `wave_invoice_created` |
| `invoice.updated` | `wave_invoice_updated` |
| `payment.created` | `wave_payment_received` |
| `transaction.created` | `wave_transaction_recorded` |

`customer.created` is received but ignored (no anchor).

## Signature verification

Header: `Wave-Signature` (or `x-wave-signature`)

Format: `t={unix_timestamp},v1={hex_hmac}`

Signed payload: `{timestamp}.{raw_request_body}`

Algorithm: HMAC-SHA256 with `WAVE_WEBHOOK_SECRET`

Implementation: `src/wave_bp_collector/signature.py`

Local dev bypass (never in production):

```
WAVE_SKIP_SIGNATURE_VERIFY=1
```

## Simulate locally

```powershell
# With skip signature enabled in .env
powershell -ExecutionPolicy Bypass -File scripts\simulate_webhook.ps1
```

## Wave developer docs

- https://developer.waveapps.com/docs/webhooks
- https://developer.waveapps.com/hc/en-us/articles/47778664499220-Webhooks-Setup-Guide
