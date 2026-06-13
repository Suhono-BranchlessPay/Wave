# List Wave invoices (GraphQL)
param([int]$PageSize = 10)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

if (-not $env:WAVE_ACCESS_TOKEN) {
    throw "WAVE_ACCESS_TOKEN missing in .env"
}
if (-not $env:WAVE_BUSINESS_ID) {
    throw "WAVE_BUSINESS_ID missing in .env"
}

$headers = @{
    Authorization  = "Bearer $env:WAVE_ACCESS_TOKEN"
    "Content-Type" = "application/json"
}
$body = @{
    query = @"
query (`$id: ID!, `$page: Int!, `$pageSize: Int!) {
  business(id: `$id) {
    name
    invoices(page: `$page, pageSize: `$pageSize) {
      edges {
        node {
          id
          invoiceNumber
          status
          total { value currency { code } }
        }
      }
    }
  }
}
"@
    variables = @{
        id       = $env:WAVE_BUSINESS_ID
        page     = 1
        pageSize = $PageSize
    }
} | ConvertTo-Json -Depth 5 -Compress

$r = Invoke-RestMethod -Method POST -Uri "https://gql.waveapps.com/graphql/public" -Headers $headers -Body $body
if ($r.errors) {
    throw ($r.errors | ConvertTo-Json -Compress)
}

Write-Host ("Business: {0}" -f $r.data.business.name) -ForegroundColor Cyan
$edges = @($r.data.business.invoices.edges)
if ($edges.Count -eq 0) {
    Write-Host "No invoices yet. Create one in Wave: Sales & Payments -> Invoices" -ForegroundColor Yellow
    exit 0
}

$rows = foreach ($edge in $edges) {
    $n = $edge.node
    [PSCustomObject]@{
        invoiceNumber = $n.invoiceNumber
        status        = $n.status
        amount        = "{0} {1}" -f $n.total.value, $n.total.currency.code
        id            = $n.id
    }
}
$rows | Format-Table -AutoSize

Write-Host ""
Write-Host "Anchor first invoice:" -ForegroundColor Green
Write-Host "  .\scripts\anchor_wave_invoice.ps1"
