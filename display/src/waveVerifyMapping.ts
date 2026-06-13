/**
 * Wave Accounting verify-page field mapping for BranchlessPay VerifyPage.tsx.
 */

export type WaveStatus =
  | "UNPAID"
  | "PAID"
  | "OVERDUE"
  | "DRAFT"
  | "PARTIAL"
  | "SAVED"
  | "SENT"
  | "VIEWED"
  | string;

export type StatusBadgeVariant =
  | "unpaid"
  | "paid"
  | "overdue"
  | "draft"
  | "partial"
  | "saved"
  | "sent"
  | "unknown";

export interface WaveAnchorMetadata {
  erp?: string;
  erp_system?: string;
  company_name?: string | null;
  business_name?: string | null;
  business_address?: string | null;
  business_id?: string | null;
  document_type?: string | null;
  contact_name?: string | null;
  invoice_number?: string | null;
  status?: WaveStatus | null;
  due_date?: string | null;
  voucher_date?: string | null;
  create_date?: string | null;
  payment_date?: string | null;
  transaction_date?: string | null;
  wave_event?: string | null;
}

export interface WaveAnchorRecord {
  event_type?: string;
  reference_id?: string;
  amount?: number;
  currency?: string;
  voucher_date?: string;
  timestamp?: string;
  business_id?: string;
  business_name?: string;
  business_address?: string;
  erp_system?: string;
  metadata?: WaveAnchorMetadata;
}

export interface VerifyRow {
  label: string;
  value: string;
  hidden?: boolean;
}

export interface StatusBadge {
  label: string;
  variant: StatusBadgeVariant;
}

export interface PdfEvidenceFields {
  documentNumber: string;
  clientName: string;
  dueDate: string | null;
  documentType: string;
  amountFormatted: string;
  currency: string;
}

export interface WaveVerifyPageData {
  businessRows: VerifyRow[];
  transactionRows: VerifyRow[];
  statusBadge: StatusBadge;
  instructions: string;
  pdfFields: PdfEvidenceFields;
}

export const ERP_DISPLAY_LABEL = "Wave Accounting";

export const EVENT_TYPE_LABELS: Record<string, string> = {
  wave_invoice_created: "Wave Invoice",
  wave_invoice_updated: "Wave Invoice (Updated)",
  wave_payment_received: "Wave Payment",
  wave_transaction_recorded: "Wave Transaction",
};

export const STATUS_LABELS: Record<string, string> = {
  UNPAID: "Unpaid",
  PAID: "Paid",
  OVERDUE: "Overdue",
  DRAFT: "Draft",
  PARTIAL: "Partial",
  SAVED: "Saved",
  SENT: "Sent",
  VIEWED: "Viewed",
};

export const STATUS_BADGE_VARIANTS: Record<string, StatusBadgeVariant> = {
  UNPAID: "unpaid",
  PAID: "paid",
  OVERDUE: "overdue",
  DRAFT: "draft",
  PARTIAL: "partial",
  SAVED: "saved",
  SENT: "sent",
  VIEWED: "sent",
};

const INVOICE_EVENT_TYPES = new Set([
  "wave_invoice_created",
  "wave_invoice_updated",
]);

const SUPPORTED_CURRENCIES = new Set(["USD", "CAD"]);

export function isWaveAnchor(anchor: WaveAnchorRecord): boolean {
  const erp = anchor.metadata?.erp?.toLowerCase();
  const eventType = anchor.event_type ?? "";
  return erp === "wave" || eventType.startsWith("wave_");
}

export function displayOrDash(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }
  const trimmed = String(value).trim();
  return trimmed === "" ? "-" : trimmed;
}

export function formatCurrency(amount: number, currency = "USD"): string {
  const code = (currency || "USD").toUpperCase();
  const safeAmount = Number.isFinite(amount) ? amount : 0;
  const fixed = safeAmount.toFixed(2);

  switch (code) {
    case "USD":
      return `$${fixed}`;
    case "CAD":
      return `CA$${fixed}`;
    default:
      return `${code} ${fixed}`;
  }
}

export function formatDisplayDate(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  const dateOnly = value.split("T")[0].split(" ")[0];
  const parsed = new Date(`${dateOnly}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

export function getEventTypeLabel(eventType: string | undefined): string {
  if (!eventType) {
    return ERP_DISPLAY_LABEL;
  }
  return EVENT_TYPE_LABELS[eventType] ?? eventType;
}

export function isInvoiceEvent(anchor: WaveAnchorRecord): boolean {
  return INVOICE_EVENT_TYPES.has(anchor.event_type ?? "");
}

export function getStatusBadge(status: WaveStatus | null | undefined): StatusBadge {
  const normalized = String(status ?? "UNKNOWN").toUpperCase();
  const label = STATUS_LABELS[normalized] ?? displayOrDash(status ?? undefined);
  const variant = STATUS_BADGE_VARIANTS[normalized] ?? "unknown";
  return { label, variant };
}

export function getBusinessName(anchor: WaveAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(
    metadata.business_name ?? metadata.company_name ?? anchor.business_name,
  );
}

export function getBusinessAddress(anchor: WaveAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(metadata.business_address ?? anchor.business_address);
}

export function getReferenceId(anchor: WaveAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  if (metadata.invoice_number) {
    return displayOrDash(metadata.invoice_number);
  }
  return displayOrDash(anchor.reference_id);
}

export function getTransactionDate(anchor: WaveAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const eventType = anchor.event_type ?? "";

  let raw: string | undefined;
  if (eventType === "wave_payment_received") {
    raw =
      metadata.payment_date ??
      anchor.voucher_date ??
      metadata.voucher_date ??
      metadata.create_date;
  } else if (eventType === "wave_transaction_recorded") {
    raw =
      metadata.transaction_date ??
      anchor.voucher_date ??
      metadata.voucher_date ??
      metadata.create_date;
  } else {
    raw =
      anchor.voucher_date ??
      metadata.voucher_date ??
      metadata.create_date ??
      anchor.timestamp;
  }

  return formatDisplayDate(raw);
}

export function shouldShowDueDate(anchor: WaveAnchorRecord): boolean {
  if (!isInvoiceEvent(anchor)) {
    return false;
  }
  const dueDate = anchor.metadata?.due_date;
  return Boolean(dueDate && String(dueDate).trim() !== "");
}

export function shouldShowStatus(anchor: WaveAnchorRecord): boolean {
  const status = anchor.metadata?.status;
  if (!status || String(status).trim() === "") {
    return false;
  }
  if (anchor.event_type === "wave_transaction_recorded") {
    return false;
  }
  return true;
}

export function getPartyLabel(anchor: WaveAnchorRecord): string {
  if (anchor.event_type === "wave_transaction_recorded") {
    return "Description";
  }
  return "Customer";
}

export function getPartyValue(anchor: WaveAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  if (anchor.event_type === "wave_transaction_recorded") {
    return displayOrDash(anchor.reference_id ?? metadata.contact_name);
  }
  return displayOrDash(metadata.contact_name);
}

export function mapBusinessSection(anchor: WaveAnchorRecord): VerifyRow[] {
  return [
    { label: "Business", value: getBusinessName(anchor) },
    { label: "Address", value: getBusinessAddress(anchor) },
    { label: "ERP System", value: ERP_DISPLAY_LABEL },
  ];
}

export function mapTransactionSection(anchor: WaveAnchorRecord): VerifyRow[] {
  const metadata = anchor.metadata ?? {};
  const rows: VerifyRow[] = [
    { label: "Reference", value: getReferenceId(anchor) },
    {
      label: "Document Type",
      value: displayOrDash(
        getEventTypeLabel(anchor.event_type) ?? metadata.document_type ?? undefined,
      ),
    },
    { label: getPartyLabel(anchor), value: getPartyValue(anchor) },
    { label: "Date", value: getTransactionDate(anchor) },
  ];

  if (shouldShowDueDate(anchor)) {
    rows.push({
      label: "Due Date",
      value: formatDisplayDate(metadata.due_date),
    });
  }

  rows.push({
    label: "Amount",
    value: formatCurrency(anchor.amount ?? 0, anchor.currency ?? "USD"),
  });

  if (shouldShowStatus(anchor)) {
    const badge = getStatusBadge(metadata.status);
    rows.push({ label: "Status", value: badge.label });
  }

  return rows;
}

export function buildVerificationInstructions(anchor: WaveAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const documentType = metadata.document_type ?? "document";
  const timestamp = formatDisplayDate(anchor.timestamp);
  const businessId = displayOrDash(metadata.business_id ?? anchor.business_id);
  const eventLabel = getEventTypeLabel(anchor.event_type);

  return (
    `This ${eventLabel} (${documentType}) from Wave Accounting was anchored to the Monad blockchain on ${timestamp}. ` +
    `Original record in Wave business ${businessId}. Verify the content hash and transaction hash below.`
  );
}

export function buildPdfEvidenceFields(anchor: WaveAnchorRecord): PdfEvidenceFields {
  const metadata = anchor.metadata ?? {};
  const currency = (anchor.currency ?? "USD").toUpperCase();
  const safeCurrency = SUPPORTED_CURRENCIES.has(currency) ? currency : "USD";

  return {
    documentNumber: getReferenceId(anchor),
    clientName: getPartyValue(anchor),
    dueDate: shouldShowDueDate(anchor)
      ? formatDisplayDate(metadata.due_date)
      : null,
    documentType: displayOrDash(
      metadata.document_type ?? getEventTypeLabel(anchor.event_type),
    ),
    amountFormatted: formatCurrency(anchor.amount ?? 0, safeCurrency),
    currency: safeCurrency,
  };
}

export function mapWaveVerifyPage(anchor: WaveAnchorRecord): WaveVerifyPageData {
  return {
    businessRows: mapBusinessSection(anchor),
    transactionRows: mapTransactionSection(anchor),
    statusBadge: getStatusBadge(anchor.metadata?.status),
    instructions: buildVerificationInstructions(anchor),
    pdfFields: buildPdfEvidenceFields(anchor),
  };
}
