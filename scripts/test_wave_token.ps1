# Test Wave access token and list businesses
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

if (-not $env:WAVE_ACCESS_TOKEN) {
    Write-Host "WAVE_ACCESS_TOKEN is empty in .env" -ForegroundColor Red
    Write-Host "See docs/WAVE_TOKEN_SETUP.md"
    exit 1
}

$token = $env:WAVE_ACCESS_TOKEN.Trim()
if ($token -match "^[0-9a-f]{8}-[0-9a-f]{4}-") {
    Write-Host "ERROR: WAVE_ACCESS_TOKEN looks like a dashboard UUID, not an API token." -ForegroundColor Red
    Write-Host "Create a Full Access Token at https://developer.waveapps.com"
    exit 1
}

$headers = @{
    Authorization  = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = '{"query":"query { user { id defaultEmail } businesses(page:1,pageSize:5) { edges { node { id name } } } }"}'

try {
    $r = Invoke-RestMethod -Method POST -Uri "https://gql.waveapps.com/graphql/public" -Headers $headers -Body $body
} catch {
    Write-Host "API call failed:" $_.Exception.Message -ForegroundColor Red
    exit 1
}

if ($r.errors) {
    Write-Host "GraphQL errors:" ($r.errors | ConvertTo-Json -Compress) -ForegroundColor Red
    exit 1
}

Write-Host "Token OK" -ForegroundColor Green
Write-Host ("User: {0}" -f $r.data.user.defaultEmail)
Write-Host "Businesses:"
foreach ($edge in $r.data.businesses.edges) {
    Write-Host ("  - {0}" -f $edge.node.name)
    Write-Host ("    id: {0}" -f $edge.node.id)
    if ($env:WAVE_BUSINESS_ID -and $edge.node.id -eq $env:WAVE_BUSINESS_ID) {
        Write-Host "    (matches WAVE_BUSINESS_ID in .env)" -ForegroundColor Green
    }
}
