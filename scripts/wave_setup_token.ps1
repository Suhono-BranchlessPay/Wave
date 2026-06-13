# One-command Wave token setup helper
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host ""
Write-Host "Wave token setup" -ForegroundColor Cyan
Write-Host "1) Open developer portal (NOT Integrations page)"
Write-Host "2) Create app + Create token"
Write-Host "3) Paste token here"
Write-Host ""

& (Join-Path $PSScriptRoot "open_wave_developer.ps1")

$response = Read-Host "Sudah dapat token? (y/n)"
if ($response -match '^[yY]') {
    & (Join-Path $PSScriptRoot "wave_paste_token.ps1")
} else {
    Write-Host "Jalankan lagi nanti: .\scripts\wave_paste_token.ps1"
}
