"""Map Wave documents to BranchlessPay anchor payload."""

from datetime import datetime, timezone
from typing import Any

EVENT_TYPE_MAP = {
    "invoice.created": "wave_invoice_created",
    "invoice.updated": "wave_invoice_updated",
    "payment.created": "wave_payment_received",
    "transaction.created": "wave_transaction_recorded",
}

DOCUMENT_TYPE_MAP = {
    "invoice.created": "Invoice",
    "invoice.updated": "Invoice",
    "payment.created": "Payment",
    "transaction.created": "Transaction",
}

ERP_DISPLAY_LABEL = "Wave Accounting"


def map_event_type(wave_event: str) -> str:
    mapped = EVENT_TYPE_MAP.get(wave_event)
    if not mapped:
        raise ValueError("Unsupported Wave event: %s" % wave_event)
    return mapped


def normalize_to_bp_payload(
    wave_event: str,
    document: dict[str, Any],
    *,
    business_id: str = "",
    company_name: str = "",
    business_address: str = "",
    webhook_timestamp: str = "",
) -> dict[str, Any]:
    event_type = map_event_type(wave_event)
    document_type = DOCUMENT_TYPE_MAP[wave_event]
    amount, currency = _extract_amount(document)
    reference_id = _extract_reference_id(document, wave_event)
    contact_name = _extract_contact_name(document)
    status = str(document.get("status") or "UNKNOWN").upper()
    business = company_name or _extract_company_name(document)
    address = business_address or _extract_business_address(document)
    voucher_date = _extract_voucher_date(document, wave_event)
    timestamp = _extract_timestamp(document, webhook_timestamp)
    resolved_business_id = business_id or str(document.get("business_id") or "")

    metadata: dict[str, Any] = {
        "erp": "wave",
        "erp_system": ERP_DISPLAY_LABEL,
        "company_name": business,
        "business_name": business,
        "business_address": address,
        "business_id": resolved_business_id,
        "document_type": document_type,
        "contact_name": contact_name,
        "status": status,
        "wave_id": str(document.get("id") or ""),
        "wave_event": wave_event,
        "voucher_date": voucher_date,
        "create_date": voucher_date,
    }

    if wave_event.startswith("invoice."):
        metadata["invoice_number"] = reference_id
        metadata["due_date"] = _extract_due_date(document)
    elif wave_event.startswith("payment."):
        metadata["payment_date"] = voucher_date
    elif wave_event.startswith("transaction."):
        metadata["transaction_date"] = voucher_date

    payload: dict[str, Any] = {
        "event_type": event_type,
        "reference_id": reference_id,
        "amount": amount,
        "currency": currency,
        "voucher_date": voucher_date,
        "timestamp": timestamp,
        "metadata": metadata,
    }

    if business:
        payload["business_name"] = business
    if address:
        payload["business_address"] = address
    if resolved_business_id:
        payload["business_id"] = resolved_business_id
    payload["erp_system"] = ERP_DISPLAY_LABEL

    return payload


def _money_value(money: Any) -> tuple[float, str]:
    if isinstance(money, dict):
        raw = money.get("value") or money.get("raw") or money.get("amount") or 0
        currency_obj = money.get("currency") or {}
        code = (
            currency_obj.get("code")
            if isinstance(currency_obj, dict)
            else money.get("currencyCode")
        ) or "USD"
        return float(raw), str(code)
    if money is not None:
        return float(money), "USD"
    return 0.0, "USD"


def _extract_amount(document: dict[str, Any]) -> tuple[float, str]:
    for key in ("amountDue", "total", "amount", "value"):
        if document.get(key) is not None:
            return _money_value(document[key])
    return 0.0, str(document.get("currency") or "USD")


def _extract_reference_id(document: dict[str, Any], event_type: str) -> str:
    if event_type.startswith("invoice."):
        return str(
            document.get("invoiceNumber")
            or document.get("invoice_number")
            or document.get("number")
            or document.get("id")
            or "unknown"
        )
    if event_type.startswith("transaction."):
        return str(
            document.get("description")
            or document.get("number")
            or document.get("id")
            or "unknown"
        )
    return str(document.get("id") or document.get("number") or "unknown")


def _extract_contact_name(document: dict[str, Any]) -> str:
    customer = document.get("customer")
    if isinstance(customer, dict):
        name = customer.get("name") or customer.get("displayName")
        if name:
            return str(name)
    for key in ("customerName", "contact_name", "vendor"):
        value = document.get(key)
        if value:
            return str(value)
    return "Unknown"


def _extract_company_name(document: dict[str, Any]) -> str:
    for key in ("business_name", "company_name", "name"):
        value = document.get(key)
        if value:
            return str(value)
    return "Wave Business"


def _extract_business_address(document: dict[str, Any]) -> str:
    direct = document.get("business_address") or document.get("address")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    address = document.get("address")
    if isinstance(address, dict):
        parts = []
        for key in (
            "addressLine1",
            "addressLine2",
            "city",
            "postalCode",
            "country",
        ):
            value = address.get(key)
            if isinstance(value, dict):
                value = value.get("name")
            if value:
                parts.append(str(value).strip())
        province = address.get("province")
        if isinstance(province, dict) and province.get("name"):
            parts.insert(2, str(province["name"]))
        joined = ", ".join(parts)
        if joined:
            return joined

    return ""


def _extract_voucher_date(document: dict[str, Any], event_type: str) -> str:
    keys = ("invoiceDate", "create_date", "paymentDate", "date", "createdAt")
    if event_type.startswith("payment."):
        keys = ("paymentDate", "date", "createdAt")
    if event_type.startswith("transaction."):
        keys = ("date", "transactionDate", "createdAt")
    for key in keys:
        value = document.get(key)
        if value:
            return _date_only(str(value))
    return ""


def _extract_due_date(document: dict[str, Any]) -> str:
    value = document.get("dueDate") or document.get("due_date")
    if value:
        return _date_only(str(value))
    return ""


def _extract_timestamp(document: dict[str, Any], webhook_timestamp: str) -> str:
    if webhook_timestamp:
        if "T" in webhook_timestamp:
            return webhook_timestamp.replace(" ", "T")
        return "%sT00:00:00Z" % _date_only(webhook_timestamp)

    for key in ("modifiedAt", "createdAt", "invoiceDate", "paymentDate", "date"):
        value = document.get(key)
        if value:
            if "T" in str(value):
                return str(value).replace(" ", "T")
            return "%sT00:00:00Z" % _date_only(str(value))
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_only(value: str) -> str:
    return value.split("T")[0].split(" ")[0]
