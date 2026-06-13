# Wave OAuth 2.0 — local callback (alternative to Full Access Token button)
#
# Prerequisites:
#   1. Create app at developer.waveapps.com (Manage Applications)
#   2. Set WAVE_CLIENT_ID + WAVE_CLIENT_SECRET in .env
#   3. Register redirect URI: http://localhost:8765/oauth/callback
#
# Usage:
#   .\scripts\open_wave_developer.ps1
#   .\scripts\wave_oauth.ps1
#   .\scripts\wave_oauth.ps1 -PasteCode "code_from_url"

param(
    [string]$PasteCode,
    [string]$EnvPath,
    [int]$CallbackPort = 8765
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$envFile = Get-DotEnvPath -EnvPath $EnvPath
Import-DotEnv -Path $envFile | Out-Null

$clientId = $env:WAVE_CLIENT_ID
$clientSecret = $env:WAVE_CLIENT_SECRET
$redirectUri = if ($env:WAVE_REDIRECT_URI) { $env:WAVE_REDIRECT_URI.Trim() } else { "http://localhost:8765/oauth/callback" }

if ([string]::IsNullOrWhiteSpace($clientId) -or [string]::IsNullOrWhiteSpace($clientSecret)) {
    Write-Host "Set WAVE_CLIENT_ID and WAVE_CLIENT_SECRET in .env first." -ForegroundColor Red
    Write-Host "Create app at developer.waveapps.com -> copy Client ID + Secret"
    Write-Host "Or use Full Access Token: .\scripts\wave_paste_token.ps1"
    exit 1
}

Set-DotEnvValue -Path $envFile -Updates @{
    WAVE_REDIRECT_URI = $redirectUri
}

$tokenUrl = "https://api.waveapps.com/oauth2/token/"
$scopes = "business:read invoice:read customer:read transaction:read offline_access"
$businessId = $env:WAVE_BUSINESS_ID

function Exchange-CodeForToken {
    param([string]$Code)
    $body = @{
        client_id     = $clientId
        client_secret = $clientSecret
        code          = $Code
        grant_type    = "authorization_code"
        redirect_uri  = $redirectUri
    }
    return Invoke-RestMethod -Method POST -Uri $tokenUrl -Body $body
}

function Save-Tokens {
    param($TokenResponse)
    $updates = @{
        WAVE_ACCESS_TOKEN  = $TokenResponse.access_token
        WAVE_REFRESH_TOKEN = $TokenResponse.refresh_token
    }
    if ($TokenResponse.businessId) {
        $updates["WAVE_BUSINESS_ID"] = $TokenResponse.businessId
    }
    Set-DotEnvValue -Path $envFile -Updates $updates
    Write-Host "Tokens saved to .env" -ForegroundColor Green
}

if ($PasteCode) {
    if ($PasteCode -match '[?&]code=([^&]+)') {
        $PasteCode = [System.Uri]::UnescapeDataString($Matches[1])
    }
    $tokens = Exchange-CodeForToken -Code $PasteCode.Trim()
    Save-Tokens $tokens
    & (Join-Path $PSScriptRoot "test_wave_token.ps1")
    exit 0
}

$authParams = @{
    client_id     = $clientId
    response_type = "code"
    scope         = $scopes
    redirect_uri  = $redirectUri
}
if ($businessId) {
    $authParams["businessId"] = $businessId
}
$query = ($authParams.GetEnumerator() | ForEach-Object {
    "{0}={1}" -f $_.Key, [uri]::EscapeDataString([string]$_.Value)
}) -join "&"
$authUrl = "https://api.waveapps.com/oauth2/authorize/?$query"

Write-Host ""
Write-Host "Wave OAuth - approve in browser" -ForegroundColor Cyan
Write-Host "Redirect URI must be registered in your Wave app:" -ForegroundColor Yellow
Write-Host "  $redirectUri"
Write-Host ""
Write-Host "NOTE: OAuth may require Wave Pro. STARTER plan: use Full Access Token instead." -ForegroundColor DarkYellow
Write-Host "  .\scripts\wave_paste_token.ps1"
Write-Host ""

Add-Type -AssemblyName System.Net.Http
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://127.0.0.1:$CallbackPort/")
$listener.Start()

Start-Process $authUrl
Write-Host "Waiting for callback on http://127.0.0.1:$CallbackPort/ ..." -ForegroundColor Gray

try {
    $context = $listener.GetContext()
    $code = $context.Request.QueryString["code"]
    $errorParam = $context.Request.QueryString["error"]

    $response = $context.Response
    $response.StatusCode = 200
    $html = if ($code) {
        "<html><body><h2>Wave authorized</h2><p>Return to PowerShell.</p></body></html>"
    } else {
        "<html><body><h2>Authorization failed</h2><p>$errorParam</p></body></html>"
    }
    $buffer = [System.Text.Encoding]::UTF8.GetBytes($html)
    $response.ContentLength64 = $buffer.Length
    $response.OutputStream.Write($buffer, 0, $buffer.Length)
    $response.Close()

    if (-not $code) {
        throw "OAuth failed: $errorParam"
    }

    $tokens = Exchange-CodeForToken -Code $code
    Save-Tokens $tokens
    & (Join-Path $PSScriptRoot "test_wave_token.ps1")
} finally {
    $listener.Stop()
}
