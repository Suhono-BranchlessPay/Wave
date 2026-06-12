import React from "react";

import {
  buildPdfEvidenceFields,
  buildVerificationInstructions,
  getStatusBadge,
  isWaveAnchor,
  mapBusinessSection,
  mapTransactionSection,
  type WaveAnchorRecord,
} from "./waveVerifyMapping";

const BADGE_CLASS: Record<string, string> = {
  unpaid: "badge badge--unpaid",
  paid: "badge badge--paid",
  overdue: "badge badge--overdue",
  draft: "badge badge--draft",
  partial: "badge badge--partial",
  unknown: "badge badge--unknown",
};

export function WaveVerifySections({ anchor }: { anchor: WaveAnchorRecord }) {
  if (!isWaveAnchor(anchor)) {
    return null;
  }

  const businessRows = mapBusinessSection(anchor);
  const transactionRows = mapTransactionSection(anchor);
  const statusBadge = getStatusBadge(anchor.metadata?.status);
  const instructions = buildVerificationInstructions(anchor);
  const pdfFields = buildPdfEvidenceFields(anchor);

  return (
    <div className="wave-verify">
      <section aria-label="Business Information">
        <h2>Business Information</h2>
        {businessRows.map((row) => (
          <div key={row.label} className="verify-row">
            <span>{row.label}</span>
            <span>{row.value}</span>
          </div>
        ))}
      </section>

      <section aria-label="Transaction Details">
        <h2>Transaction Details</h2>
        {transactionRows.map((row) =>
          row.label === "Status" ? (
            <div key={row.label} className="verify-row">
              <span>{row.label}</span>
              <span className={BADGE_CLASS[statusBadge.variant]}>
                {statusBadge.label}
              </span>
            </div>
          ) : (
            <div key={row.label} className="verify-row">
              <span>{row.label}</span>
              <span>{row.value}</span>
            </div>
          ),
        )}
      </section>

      <section aria-label="Verification Instructions">
        <p>{instructions}</p>
      </section>

      <section aria-label="PDF Evidence Fields" hidden>
        <pre>{JSON.stringify(pdfFields, null, 2)}</pre>
      </section>
    </div>
  );
}
