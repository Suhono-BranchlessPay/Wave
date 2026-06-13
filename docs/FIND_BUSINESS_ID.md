# How to find WAVE_BUSINESS_ID

Wave **does not display** the GraphQL business ID in the web dashboard. The UUID in your browser URL is **not** the API id directly — but it can be converted.

---

## Your dashboard URL

```
https://next.waveapps.com/1adbda9d-e4ee-4db9-8a47-e39b97e5508e/dashboard
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              This UUID → convert to GraphQL id
```

## Derived GraphQL business ID (for `.env`)

```
WAVE_BUSINESS_ID=QnVzaW5lc3M6MWFkYmRhOWQtZTRlZS00ZGI5LThhNDctZTM5Yjk3ZTU1MDhl
```

Wave encodes IDs as Base64 of `Business:{uuid}`.

---

## Verify with script (after you have access token)

```powershell
cd "Wave Accounting"
.\scripts\get_wave_business_id.ps1 -DashboardUuid 1adbda9d-e4ee-4db9-8a47-e39b97e5508e
```

With `WAVE_ACCESS_TOKEN` in `.env`, the same script also **lists businesses from the API** so you can confirm name + id match.

---

## Manual API query

Developer portal: https://developer.waveapps.com → Create token → paste in `.env`

```powershell
$headers = @{
  Authorization = "Bearer $env:WAVE_ACCESS_TOKEN"
  "Content-Type" = "application/json"
}
$body = '{"query":"query { businesses(page: 1, pageSize: 10) { edges { node { id name } } } }"}'
Invoke-RestMethod -Method POST -Uri "https://gql.waveapps.com/graphql/public" -Headers $headers -Body $body
```

Use the `id` field from the response — not the dashboard URL alone without verification.

---

## Where it is NOT found

| Place | Has GraphQL business id? |
|-------|---------------------------|
| next.waveapps.com dashboard | ❌ only UUID in URL |
| Settings pages | ❌ |
| Invoice screen | ❌ |
| Developer portal app page | ❌ |
| GraphQL API `businesses` query | ✅ |

Reference: https://developer.waveapps.com/hc/en-us/articles/360032908111-Query-List-businesses
