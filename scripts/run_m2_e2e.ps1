# M2 end-to-end verification — unit tests + all four event types
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = "src"

Write-Host "=== 1/3 Unit tests ===" -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "run_tests.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== 2/3 Collector pipeline — all 4 event types (sample docs + real BP) ===" -ForegroundColor Cyan
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
& $python (Join-Path $PSScriptRoot "e2e_collector_all_events.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== 3/3 Live Wave invoice webhook (optional) ===" -ForegroundColor Cyan
try {
    . (Join-Path $PSScriptRoot "load_dotenv.ps1")
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8080/health" -TimeoutSec 3
    if ($health.ok) {
        Write-Host "Collector running — anchoring invoice.created..." -ForegroundColor Green
        & (Join-Path $PSScriptRoot "anchor_wave_event.ps1") -EventType "invoice.created"
        Write-Host "Anchoring invoice.updated..." -ForegroundColor Green
        & (Join-Path $PSScriptRoot "anchor_wave_event.ps1") -EventType "invoice.updated"
    }
} catch {
    Write-Host "Collector not running on :8080 — skipped live invoice webhook." -ForegroundColor Yellow
    Write-Host "Start: `$env:PYTHONPATH='src'; python -m wave_bp_collector.app" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "M2 E2E complete." -ForegroundColor Green
