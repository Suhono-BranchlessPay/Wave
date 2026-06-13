# Validate M3+M4 — live verify URLs + display tests
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=== Display unit tests ===" -ForegroundColor Cyan
Set-Location (Join-Path $root "display")
npm test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Mapping preview (fixtures) ===" -ForegroundColor Cyan
node --experimental-strip-types scripts/preview_verify.mjs

Write-Host ""
Write-Host "=== Live anchor status (sample URLs) ===" -ForegroundColor Cyan
Set-Location $root
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$anchors = @{
  "invoice.created" = "9d938e0d-e64d-44da-91fd-1345e2ab60a4"
  "payment.created" = "587583dd-ef70-47c8-8c6f-ed4480e46ba1"
}

foreach ($event in $anchors.Keys) {
  $id = $anchors[$event]
  try {
    $r = Invoke-RestMethod -Uri "https://branchlesspay.com/api/v1/anchor/$id" `
      -Headers @{ Authorization = "Bearer $env:BP_LICENSE_KEY" } -TimeoutSec 15
    Write-Host ("{0}: status={1}" -f $event, $r.status)
    Write-Host ("  https://branchlesspay.com/verify/{0}" -f $id)
  } catch {
    Write-Host ("{0}: API check failed - {1}" -f $event, $_.Exception.Message) -ForegroundColor Yellow
  }
}

Write-Host ""
Write-Host "M3+M4 validation complete." -ForegroundColor Green
