# Milestone — Wave M3 + M4

Repo: https://github.com/Suhono-BranchlessPay/Wave · branch **`dev`**  
Status: **M3 + M4 complete** (2026-06-13) — pending BP `VerifyPage.tsx` merge

---

## M3 — Field mapping

| Deliverable | Status |
|-------------|--------|
| `display/src/waveVerifyMapping.ts` | ✅ |
| Event labels + status badges (incl. SAVED, SENT) | ✅ |
| Currency USD/CAD | ✅ |
| Live fixtures from M2 anchors | ✅ `display/fixtures/` |
| Integration example | ✅ |
| Mapping doc | ✅ `docs/M3_FIELD_MAPPING.md` |
| Unit tests (11) | ✅ |

---

## M4 — Polish

| Deliverable | Status |
|-------------|--------|
| Missing field handling (`displayOrDash`) | ✅ |
| Payment/transaction date + party labels | ✅ |
| PDF evidence builder | ✅ |
| Verification instructions | ✅ |
| Preview script | ✅ `display/scripts/preview_verify.mjs` |
| BP merge guide | ✅ `docs/M4_VERIFY_INTEGRATION.md` |
| BP `VerifyPage.tsx` merge | ⏳ Pending BP |

---

## Sample verify URLs (QA)

| Event | Verify |
|-------|--------|
| `invoice.created` | https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4 |
| `payment.created` | https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1 |

Run tests: `cd display && npm test`

Contact: suhono@branchlesspay.com
