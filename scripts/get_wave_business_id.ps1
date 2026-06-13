# Find Wave GraphQL business ID
#
# Wave does NOT show this ID in the dashboard UI. Options:
#   1. Derive from next.waveapps.com URL UUID (see -DashboardUuid)
#   2. List via GraphQL when WAVE_ACCESS_TOKEN is set (recommended verify)

param(
    [string]$DashboardUuid = "",
    [switch]$FromEnv
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

function ConvertTo-WaveBusinessId {
    param([string]$Uuid)
    $Uuid = $Uuid.Trim().ToLower()
    if ($Uuid -match "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$") {
        $raw = "Business:$Uuid"
        return [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($raw))
    }
    throw "Invalid UUID format: $Uuid"
}

function Get-WaveBusinesses {
    param([string]$AccessToken)
    if (-not $AccessToken) {
        throw "WAVE_ACCESS_TOKEN is empty. Create a token at https://developer.waveapps.com"
    }
    $headers = @{
        Authorization  = "Bearer $AccessToken"
        "Content-Type" = "application/json"
    }
    $query = @{
        query = @"
query {
  businesses(page: 1, pageSize: 10) {
    edges {
      node {
        id
        name
        isPersonal
      }
    }
  }
}
"@
    } | ConvertTo-Json -Compress

    $response = Invoke-RestMethod -Method POST `
        -Uri "https://gql.waveapps.com/graphql/public" `
        -Headers $headers `
        -Body $query

    if ($response.errors) {
        throw ("GraphQL error: " + ($response.errors | ConvertTo-Json -Compress))
    }
    return $response.data.businesses.edges
}

Write-Host "=== Wave Business ID helper ===" -ForegroundColor Cyan
Write-Host ""

if ($DashboardUuid) {
    $derived = ConvertTo-WaveBusinessId $DashboardUuid
    Write-Host "From dashboard URL UUID:" -ForegroundColor Yellow
    Write-Host "  UUID:       $DashboardUuid"
    Write-Host "  GraphQL id: $derived"
    Write-Host ""
    Write-Host "Add to .env:"
    Write-Host "  WAVE_BUSINESS_ID=$derived"
    Write-Host ""
} elseif ($env:WAVE_BUSINESS_ID) {
    Write-Host "WAVE_BUSINESS_ID in .env:" -ForegroundColor Yellow
    Write-Host "  $($env:WAVE_BUSINESS_ID)"
    Write-Host ""
}

if ($env:WAVE_ACCESS_TOKEN) {
    Write-Host "Listing businesses from Wave API (verified):" -ForegroundColor Green
    $edges = Get-WaveBusinesses $env:WAVE_ACCESS_TOKEN
    foreach ($edge in $edges) {
        $node = $edge.node
        Write-Host ("  name: {0}" -f $node.name)
        Write-Host ("  id:   {0}" -f $node.id)
        Write-Host ""
    }
    if (-not $DashboardUuid) {
        Write-Host "Copy the matching id to .env as WAVE_BUSINESS_ID"
    }
} else {
    Write-Host "WAVE_ACCESS_TOKEN not set - cannot verify via API yet." -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "Steps:"
    Write-Host "  1. https://developer.waveapps.com -> Manage Applications -> Create token"
    Write-Host "  2. Paste LONG token (not dashboard UUID) into .env:"
    Write-Host "     WAVE_ACCESS_TOKEN=..."
    Write-Host "  3. Run: .\scripts\test_wave_token.ps1"
    Write-Host "  4. Re-run: .\scripts\get_wave_business_id.ps1"
    Write-Host ""
    Write-Host "Guide: docs\WAVE_TOKEN_SETUP.md"
}
