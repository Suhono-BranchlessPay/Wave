import assert from "node:assert/strict";
import test from "node:test";

import {
  buildPdfEvidenceFields,
  displayOrDash,
  formatCurrency,
  getStatusBadge,
  isWaveAnchor,
  mapBusinessSection,
  mapTransactionSection,
  shouldShowDueDate,
} from "../src/waveVerifyMapping.ts";

const sampleInvoice = {
  event_type: "wave_invoice_created",
  reference_id: "INV-0001",
  amount: 750,
  currency: "USD",
  voucher_date: "2026-06-12",
  timestamp: "2026-06-12T10:00:00Z",
  metadata: {
    erp: "wave",
    company_name: "Test Business LLC",
    business_name: "Test Business LLC",
    business_address: "123 Main St, Austin, TX",
    business_id: "biz-123",
    document_type: "Invoice",
    contact_name: "John Smith",
    invoice_number: "INV-0001",
    status: "UNPAID",
    due_date: "2026-07-12",
  },
};

test("isWaveAnchor detects Wave records", () => {
  assert.equal(isWaveAnchor(sampleInvoice), true);
  assert.equal(isWaveAnchor({ event_type: "freshbooks_invoice_created" }), false);
});

test("business section maps M3 fields", () => {
  const rows = mapBusinessSection(sampleInvoice);
  assert.deepEqual(rows, [
    { label: "Business", value: "Test Business LLC" },
    { label: "Address", value: "123 Main St, Austin, TX" },
    { label: "ERP System", value: "Wave Accounting" },
  ]);
});

test("hide due date when null", () => {
  const payment = {
    ...sampleInvoice,
    event_type: "wave_payment_received",
    metadata: { ...sampleInvoice.metadata, due_date: null, status: "PAID" },
  };
  assert.equal(shouldShowDueDate(payment), false);
  assert.equal(
    mapTransactionSection(payment).some((row) => row.label === "Due Date"),
    false,
  );
});

test("status badges", () => {
  assert.deepEqual(getStatusBadge("UNPAID"), { label: "Unpaid", variant: "unpaid" });
  assert.deepEqual(getStatusBadge("PAID"), { label: "Paid", variant: "paid" });
  assert.deepEqual(getStatusBadge("PARTIAL"), { label: "Partial", variant: "partial" });
});

test("currency USD and CAD", () => {
  assert.equal(formatCurrency(750, "USD"), "$750.00");
  assert.equal(formatCurrency(750, "CAD"), "CA$750.00");
});

test("pdf evidence fields", () => {
  const pdf = buildPdfEvidenceFields(sampleInvoice);
  assert.equal(pdf.documentNumber, "INV-0001");
  assert.equal(pdf.clientName, "John Smith");
  assert.equal(pdf.amountFormatted, "$750.00");
});

test("displayOrDash", () => {
  assert.equal(displayOrDash(null), "-");
  assert.equal(displayOrDash("Acme"), "Acme");
});
