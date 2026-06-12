# Wave OAuth

## Quick start (development)

1. Log in to Wave → **Manage Applications** on developer portal
2. Create application → **Create token** (full access token for your business)
3. Copy token to `.env`:

```
WAVE_ACCESS_TOKEN=your_token_here
WAVE_BUSINESS_ID=your_business_graphql_id
```

## OAuth 2 (production apps)

| Step | URL |
|------|-----|
| Authorize | `https://api.waveapps.com/oauth2/authorize/` |
| Token | `https://api.waveapps.com/oauth2/token/` |
| GraphQL | `https://gql.waveapps.com/graphql/public` |

Required params: `client_id`, `client_secret`, `redirect_uri`, `scope`, `response_type=code`

Store in `.env`:

```
WAVE_CLIENT_ID=
WAVE_CLIENT_SECRET=
WAVE_REDIRECT_URI=http://localhost:8765/oauth/callback
WAVE_ACCESS_TOKEN=
WAVE_REFRESH_TOKEN=
```

## GraphQL example

```powershell
$headers = @{
  Authorization = "Bearer $env:WAVE_ACCESS_TOKEN"
  "Content-Type" = "application/json"
}
$body = @{
  query = "query { user { id defaultEmail } }"
} | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri "https://gql.waveapps.com/graphql/public" -Headers $headers -Body $body
```

Reference: https://developer.waveapps.com/hc/en-us/articles/360019493652-OAuth-Guide
