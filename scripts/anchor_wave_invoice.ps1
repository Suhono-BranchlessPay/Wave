# Backward-compatible wrapper — use anchor_wave_event.ps1
param(
    [string]$InvoiceId = "",
    [string]$BaseUrl = "http://127.0.0.1:8080",
    [string]$EventType = "invoice.created"
)

$params = @{
    EventType = $EventType
    BaseUrl   = $BaseUrl
}
if ($InvoiceId) {
    $params["ResourceId"] = $InvoiceId
}

& (Join-Path $PSScriptRoot "anchor_wave_event.ps1") @params
