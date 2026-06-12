# Submission to BranchlessPay — Wave M1–M4

**To:** suhono@branchlesspay.com  
**Subject:** Wave Accounting integration scaffold ready — dev branch

---

## GitHub

https://github.com/Suhono-BranchlessPay/Wave/tree/dev

---

## Summary

- **M1:** Flask webhook `POST /webhook/wave` with Wave-Signature HMAC verification
- **M2:** GraphQL fetch + normalize + BP anchor POST with retry queue
- **M3+M4:** `display/src/waveVerifyMapping.ts` + integration example for verify page

---

## Blockers / next steps

1. BP test token (`BP_LICENSE_KEY`) for live anchor test
2. Wave developer app + OAuth token + business ID
3. ngrok tunnel for webhook registration
4. BP production `VerifyPage.tsx` for Wave UI merge

Contact: suhono@branchlesspay.com
