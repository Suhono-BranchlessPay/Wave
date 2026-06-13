from wave_bp_collector.normalizer import normalize_to_bp_payload


def test_normalize_invoice_created():
    document = {
        "id": "inv-1",
        "invoiceNumber": "INV-0001",
        "status": "UNPAID",
        "amountDue": {"value": "750.00", "currency": {"code": "USD"}},
        "customer": {"name": "John Smith", "email": "john@example.com"},
        "dueDate": "2026-07-12",
        "invoiceDate": "2026-06-12",
        "business_name": "Test Business LLC",
        "address": {
            "addressLine1": "123 Main St",
            "city": "Austin",
            "province": {"name": "TX"},
            "postalCode": "78701",
            "country": {"name": "USA"},
        },
    }
    payload = normalize_to_bp_payload(
        "invoice.created",
        document,
        business_id="biz-123",
        webhook_timestamp="2026-06-12T10:00:00Z",
    )
    assert payload["event_type"] == "wave_invoice_created"
    assert payload["reference_id"] == "INV-0001"
    assert payload["amount"] == 750.0
    assert payload["currency"] == "USD"
    assert payload["voucher_date"] == "2026-06-12"
    assert payload["metadata"]["business_id"] == "biz-123"
    assert payload["metadata"]["contact_name"] == "John Smith"
    assert payload["metadata"]["due_date"] == "2026-07-12"
    assert payload["erp_system"] == "Wave Accounting"
    assert "123 Main St" in payload["metadata"]["business_address"]


def test_wave_comma_amount():
    document = {
        "id": "inv-1",
        "invoiceNumber": "1",
        "status": "SAVED",
        "total": {"value": "1,500.00", "currency": {"code": "USD"}},
        "customer": {"name": "Microsoft Inc"},
        "invoiceDate": "2026-06-12",
    }
    payload = normalize_to_bp_payload("invoice.created", document, business_id="biz-123")
    assert payload["amount"] == 1500.0


def test_payment_mapping():
    document = {
        "id": "pay-1",
        "amount": "100.00",
        "date": "2026-06-12",
        "customer": {"name": "Jane Doe"},
    }
    payload = normalize_to_bp_payload(
        "payment.created",
        document,
        business_id="biz-123",
    )
    assert payload["event_type"] == "wave_payment_received"
    assert payload["metadata"]["document_type"] == "Payment"
    assert payload["amount"] == 100.0
    assert payload["metadata"]["contact_name"] == "Jane Doe"


def test_invoice_updated():
    document = {
        "id": "inv-1",
        "invoiceNumber": "INV-0001",
        "status": "SENT",
        "total": {"value": "750.00", "currency": {"code": "USD"}},
        "customer": {"name": "John Smith"},
        "invoiceDate": "2026-06-12",
    }
    payload = normalize_to_bp_payload(
        "invoice.updated",
        document,
        business_id="biz-123",
    )
    assert payload["event_type"] == "wave_invoice_updated"
    assert payload["metadata"]["status"] == "SENT"


def test_transaction_created():
    document = {
        "id": "txn-1",
        "description": "Office supplies",
        "amount": "75.00",
        "date": "2026-06-12",
    }
    payload = normalize_to_bp_payload(
        "transaction.created",
        document,
        business_id="biz-123",
    )
    assert payload["event_type"] == "wave_transaction_recorded"
    assert payload["reference_id"] == "Office supplies"
    assert payload["amount"] == 75.0
    assert payload["metadata"]["document_type"] == "Transaction"
