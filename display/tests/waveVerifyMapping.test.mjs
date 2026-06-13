import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  buildPdfEvidenceFields,
  buildVerificationInstructions,
  displayOrDash,
  formatCurrency,
  getStatusBadge,
  isWaveAnchor,
  mapBusinessSection,
  mapTransactionSection,
  mapWaveVerifyPage,
  shouldShowDueDate,
  shouldShowStatus,
} from "../src/waveVerifyMapping.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(__dirname, "..", "fixtures");

function loadFixture(name) {
  return JSON.parse(readFileSync(join(fixturesDir, name), "utf8"));
}

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

const liveInvoice = loadFixture("invoice_created_9d938e0d.json");
const livePayment = loadFixture("payment_created_587583dd.json");

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

test("live invoice.created fixture — verify 9d938e0d", () => {
  assert.equal(liveInvoice.anchor_id, "9d938e0d-e64d-44da-91fd-1345e2ab60a4");
  const page = mapWaveVerifyPage(liveInvoice);
  assert.equal(page.businessRows[0].value, "BranchlessPay Inc");
  assert.equal(page.transactionRows.find((r) => r.label === "Reference")?.value, "1");
  assert.equal(page.transactionRows.find((r) => r.label === "Amount")?.value, "$1500.00");
  assert.deepEqual(getStatusBadge("SAVED"), { label: "Saved", variant: "saved" });
  assert.equal(page.statusBadge.label, "Saved");
  assert.match(page.instructions, /Wave Invoice/);
});

test("live payment.created fixture — verify 587583dd", () => {
  assert.equal(livePayment.anchor_id, "587583dd-ef70-47c8-8c6f-ed4480e46ba1");
  const page = mapWaveVerifyPage(livePayment);
  assert.equal(shouldShowDueDate(livePayment), false);
  assert.equal(
    page.transactionRows.some((row) => row.label === "Due Date"),
    false,
  );
  assert.equal(page.transactionRows.find((r) => r.label === "Customer")?.value, "Microsoft Inc");
  assert.equal(page.transactionRows.find((r) => r.label === "Amount")?.value, "$500.00");
  assert.equal(page.statusBadge.label, "Paid");
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
  assert.deepEqual(getStatusBadge("SAVED"), { label: "Saved", variant: "saved" });
});

test("transaction hides status row when not applicable", () => {
  const txn = {
    event_type: "wave_transaction_recorded",
    reference_id: "Office supplies",
    amount: 75,
    currency: "USD",
    metadata: { erp: "wave", document_type: "Transaction", status: "UNKNOWN" },
  };
  assert.equal(shouldShowStatus(txn), false);
  assert.equal(
    mapTransactionSection(txn).find((r) => r.label === "Description")?.value,
    "Office supplies",
  );
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

test("verification instructions mention ERP and date", () => {
  const text = buildVerificationInstructions(liveInvoice);
  assert.match(text, /Wave Accounting/);
  assert.match(text, /Monad blockchain/);
});

test("displayOrDash", () => {
  assert.equal(displayOrDash(null), "-");
  assert.equal(displayOrDash("Acme"), "Acme");
});
