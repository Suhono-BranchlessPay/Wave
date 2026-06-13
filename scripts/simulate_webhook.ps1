# Simulate Wave webhook (dev — set WAVE_SKIP_SIGNATURE_VERIFY=1)
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet(
        "invoice.created",
        "invoice.updated",
        "payment.created",
        "transaction.created"
    )]
    [string]$EventType = "invoice.created",
    [string]$ResourceId = "test-resource-1",
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$payload = @{
    data = @{
        businessId = $env:WAVE_BUSINESS_ID
        event = @{
            type      = $EventType
            timestamp = (Get-Date).ToUniversalTime().ToString("o")
            resource  = @{ id = $ResourceId }
        }
    }
} | ConvertTo-Json -Depth 5 -Compress

Write-Host ("POST {0}/webhook/wave event={1} resource={2}" -f $BaseUrl, $EventType, $ResourceId) -ForegroundColor Cyan
Invoke-RestMethod -Method POST -Uri "$BaseUrl/webhook/wave" -Body $payload -ContentType "application/json"
