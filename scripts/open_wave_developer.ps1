# Fix Wave developer redirect loop
# Problem: clicking "Sign in" on developer.waveapps.com sends you to next.waveapps.com/dashboard
# Fix: stay logged in on dashboard, then open Manage Applications WITHOUT top Sign in

$ErrorActionPreference = "Stop"

$dashboard = "https://next.waveapps.com/1adbda9d-e4ee-4db9-8a47-e39b97e5508e/dashboard"
$manageApps = "https://developer.waveapps.com/hc/en-us/articles/360019762711-Manage-Applications"
$playground = "https://gql.waveapps.com/help-center"
$devHome = "https://developer.waveapps.com/hc/en-us"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " WAVE - FIX REDIRECT KE DASHBOARD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Anda SUDAH login jika bisa lihat dashboard BranchlessPay Inc." -ForegroundColor Green
Write-Host "JANGAN klik 'Sign in' di pojok kanan developer.waveapps.com" -ForegroundColor Red
Write-Host ""
Write-Host "Langkah:" -ForegroundColor Yellow
Write-Host "  TAB 1 - biarkan dashboard terbuka (sudah login)"
Write-Host "  TAB 2 - buka Manage Applications (script buka otomatis)"
Write-Host "  Scroll ke BAWAH halaman -> kotak 'Please login to make changes'"
Write-Host "  Klik login / Get started DI DALAM kotak itu (bukan Sign in header)"
Write-Host "  Create application -> Create token -> copy token"
Write-Host ""
Write-Host "Lalu: .\scripts\wave_paste_token.ps1" -ForegroundColor Green
Write-Host ""

Start-Process $manageApps
Start-Sleep -Seconds 2
Write-Host "Opened: Manage Applications" -ForegroundColor Gray
Write-Host ""
Write-Host "Optional GraphQL playground (butuh token di HTTP Headers):" -ForegroundColor DarkGray
Write-Host "  $playground"
Write-Host ""
Write-Host "Jika kotak iframe tetap kosong / tidak bisa login:" -ForegroundColor Yellow
Write-Host "  1. Coba browser Chrome/Edge (bukan in-app browser)"
Write-Host "  2. Matikan ad-blocker untuk developer.waveapps.com"
Write-Host "  3. Email suhono@branchlesspay.com - minta bantuan Wave API / Pro webhook"
Write-Host "  4. Wave support: $devHome -> Submit a request"
Write-Host ""
