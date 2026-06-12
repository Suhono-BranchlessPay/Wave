# Simulate Wave webhook (dev — set WAVE_SKIP_SIGNATURE_VERIFY=1)
param(
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$payload = @{
    data = @{
        businessId = "biz-123"
        event = @{
            type = "invoice.created"
            timestamp = "2026-06-12T10:00:00Z"
            resource = @{ id = "inv-1" }
        }
    }
} | ConvertTo-Json -Depth 5 -Compress

Invoke-RestMethod -Method POST -Uri "$BaseUrl/webhook/wave" -Body $payload -ContentType "application/json"
