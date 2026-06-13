# POST webhook for a Wave resource -> local collector -> BP anchor
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet(
        "invoice.created",
        "invoice.updated",
        "payment.created",
        "transaction.created"
    )]
    [string]$EventType = "invoice.created",
    [string]$ResourceId = "",
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

function Invoke-WaveGraphql {
    param([string]$Query, [hashtable]$Variables)
    $headers = @{
        Authorization  = "Bearer $env:WAVE_ACCESS_TOKEN"
        "Content-Type" = "application/json"
    }
    $body = @{
        query     = $Query
        variables = $Variables
    } | ConvertTo-Json -Compress
    return Invoke-RestMethod -Method POST -Uri "https://gql.waveapps.com/graphql/public" -Headers $headers -Body $body
}

if (-not $ResourceId) {
    if ($EventType -like "invoice.*") {
        $r = Invoke-WaveGraphql -Query "query(`$id: ID!) { business(id: `$id) { invoices(page: 1, pageSize: 1) { edges { node { id invoiceNumber } } } } }" -Variables @{ id = $env:WAVE_BUSINESS_ID }
        $ResourceId = $r.data.business.invoices.edges[0].node.id
        if (-not $ResourceId) {
            throw "No invoice found. Create one in Wave first."
        }
        Write-Host ("Using invoice: {0}" -f $r.data.business.invoices.edges[0].node.invoiceNumber)
    }
    elseif ($EventType -eq "payment.created") {
        if ($env:WAVE_TEST_PAYMENT_ID) {
            $ResourceId = $env:WAVE_TEST_PAYMENT_ID
            Write-Host "Using WAVE_TEST_PAYMENT_ID from .env"
        } else {
            throw "Set WAVE_TEST_PAYMENT_ID in .env after recording a payment in Wave, or pass -ResourceId."
        }
    }
    elseif ($EventType -eq "transaction.created") {
        if ($env:WAVE_TEST_TRANSACTION_ID) {
            $ResourceId = $env:WAVE_TEST_TRANSACTION_ID
            Write-Host "Using WAVE_TEST_TRANSACTION_ID from .env"
        } else {
            throw "Set WAVE_TEST_TRANSACTION_ID in .env after creating a transaction in Wave, or pass -ResourceId."
        }
    }
}

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

Write-Host ("POST {0}/webhook/wave event={1}" -f $BaseUrl, $EventType) -ForegroundColor Cyan
try {
    $webResp = Invoke-WebRequest -Method POST -Uri "$BaseUrl/webhook/wave" -Body $payload -ContentType "application/json" -UseBasicParsing
} catch {
    $status = $null
    $bodyText = $null
    if ($_.Exception.Response) {
        $status = [int]$_.Exception.Response.StatusCode
        $stream = $_.Exception.Response.GetResponseStream()
        if ($stream) {
            $reader = New-Object System.IO.StreamReader($stream)
            $bodyText = $reader.ReadToEnd()
            $reader.Close()
        }
    }
    if (-not $bodyText -and $_.ErrorDetails.Message) {
        $bodyText = $_.ErrorDetails.Message
    }
    if ($bodyText) {
        Write-Host ("HTTP {0}" -f $status) -ForegroundColor Red
        try {
            ($bodyText | ConvertFrom-Json) | ConvertTo-Json -Depth 5 | Write-Host
        } catch {
            Write-Host $bodyText
        }
        if ($bodyText -match "Invalid API key") {
            Write-Host ""
            Write-Host "BP_LICENSE_KEY in .env is invalid. Ask suhono@branchlesspay.com for a fresh test token." -ForegroundColor Yellow
        } elseif ($status -eq 500) {
            Write-Host ""
            Write-Host "Restart the collector so it loads the latest code:" -ForegroundColor Yellow
            Write-Host '  $env:PYTHONPATH="src"; python -m wave_bp_collector.app' -ForegroundColor Yellow
        }
    } else {
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    exit 1
}

$resp = $webResp.Content | ConvertFrom-Json
$resp | ConvertTo-Json -Depth 5
if ($resp.verify_url) {
    Write-Host ""
    Write-Host ("Verify: {0}" -f $resp.verify_url) -ForegroundColor Green
}
