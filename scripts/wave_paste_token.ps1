# Save Wave Full Access Token to .env and verify via GraphQL
param(
    [string]$Token,
    [string]$EnvPath
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$envFile = Get-DotEnvPath -EnvPath $EnvPath
if (-not (Test-Path $envFile)) {
    throw ".env not found. Copy .env.example to .env first."
}

if (-not $Token) {
    Write-Host ""
    Write-Host "Paste Wave Full Access Token from developer.waveapps.com" -ForegroundColor Cyan
    Write-Host "(Manage Applications -> your app -> Create token)" -ForegroundColor Gray
    Write-Host ""
    $Token = Read-Host "Token"
}

$Token = $Token.Trim()
if ($Token -match '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$') {
    throw "Itu UUID dashboard, bukan API token. Buat token di developer.waveapps.com (Create token)."
}
if ($Token.Length -lt 20) {
    throw "Token terlalu pendek. Pastikan copy Full Access Token lengkap dari Wave."
}

Set-DotEnvValue -Path $envFile -Updates @{
    WAVE_ACCESS_TOKEN = $Token
}

Write-Host "Saved WAVE_ACCESS_TOKEN to .env" -ForegroundColor Green
Import-DotEnv -Path $envFile | Out-Null

& (Join-Path $PSScriptRoot "test_wave_token.ps1")
& (Join-Path $PSScriptRoot "get_wave_business_id.ps1")
