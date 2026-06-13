# Wave Developer Token — step by step

## Anda di halaman yang SALAH

Screenshot **Integrations** (`next.waveapps.com/.../integrations`) hanya untuk Google Sheets.

**Token API TIDAK ada di sana.** Wave memisahkan:

| Website | Fungsi |
|---------|--------|
| `next.waveapps.com` | Accounting (invoice, dashboard) |
| **`developer.waveapps.com`** | API, Create token, webhooks |

---

## Cara tercepat (script)

```powershell
cd "C:\Users\Thinkbook\Downloads\Audit Shield\Wave Accounting"
.\scripts\wave_setup_token.ps1
```

Atau manual:

```powershell
.\scripts\open_wave_developer.ps1
# ... Create token di browser ...
.\scripts\wave_paste_token.ps1
```

---

## Manual di browser

1. https://developer.waveapps.com/hc/en-us/articles/360019762711-Manage-Applications
2. **Sign in**
3. **Get started** / **Create application**
4. Name: `BranchlessPay Audit Shield`
5. Redirect URI: `http://localhost:8765/oauth/callback`
6. Klik app → **Create token**
7. Copy token panjang (bukan UUID dari URL dashboard)

---

## Plan STARTER vs webhook

| Feature | STARTER | Wave Pro |
|---------|---------|----------|
| Full Access Token + GraphQL | Usually OK | OK |
| OAuth third-party | May need Pro | OK |
| Webhook delivery | Not supported | OK |

Contact: suhono@branchlesspay.com
