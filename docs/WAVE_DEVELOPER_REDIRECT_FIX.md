# Wave developer portal - fix redirect to dashboard

## What happened

You log in → Wave sends you to:

`next.waveapps.com/.../dashboard`

That is **correct for accounting**. It is **not** the developer token page.

Clicking **Sign in** at the top of `developer.waveapps.com` often causes this redirect loop.

---

## Correct flow (2 tabs)

### Tab 1 — keep open

Your dashboard (already logged in):

`https://next.waveapps.com/1adbda9d-e4ee-4db9-8a47-e39b97e5508e/dashboard`

### Tab 2 — open this URL (do NOT click top Sign in)

https://developer.waveapps.com/hc/en-us/articles/360019762711-Manage-Applications

Scroll **down** on that page. You should see an embedded panel:

> Please login to make changes

Click **Get started** / login **inside that panel** (not the header Sign in).

Then:

1. Create application — name: `BranchlessPay Audit Shield`
2. Redirect URI: `http://localhost:8765/oauth/callback`
3. Open app → **Create token**
4. Copy long token → run `.\scripts\wave_paste_token.ps1`

---

## Run helper script

```powershell
cd "C:\Users\Thinkbook\Downloads\Audit Shield\Wave Accounting"
.\scripts\open_wave_developer.ps1
```

---

## WAVE_BUSINESS_ID (already done)

From your dashboard URL — no token needed:

```
WAVE_BUSINESS_ID=QnVzaW5lc3M6MWFkYmRhOWQtZTRlZS00ZGI5LThhNDctZTM5Yjk3ZTU1MDhl
```

Business: **BranchlessPay Inc** (STARTER)

---

## If iframe still will not load

| Option | Action |
|--------|--------|
| Browser | Use Chrome/Edge, disable ad-block on developer.waveapps.com |
| BP team | Email suhono@branchlesspay.com — Wave on STARTER may need Pro for webhooks |
| Wave support | https://developer.waveapps.com/hc/en-us/requests/new |

You can still test collector locally with `simulate_webhook.ps1` while waiting for token.

Contact: suhono@branchlesspay.com
