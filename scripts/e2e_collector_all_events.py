"""Live E2E — all four Wave event types through the collector pipeline.

Uses mocked Wave GraphQL fetch (sample documents) and real BranchlessPay API.
Invoice events can also be tested live via anchor_wave_event.ps1 with real Wave IDs.
"""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import patch

from wave_bp_collector.app import create_app
from wave_bp_collector.config import get_settings

SAMPLE_DOCS = {
    "invoice.created": {
        "id": "inv-sample-1",
        "invoiceNumber": "INV-E2E-001",
        "status": "SAVED",
        "total": {"value": "1,500.00", "currency": {"code": "USD"}},
        "customer": {"name": "Microsoft Inc"},
        "dueDate": "2026-06-12",
        "invoiceDate": "2026-06-12",
        "business_name": "BranchlessPay Inc",
    },
    "invoice.updated": {
        "id": "inv-sample-1",
        "invoiceNumber": "INV-E2E-001",
        "status": "SENT",
        "total": {"value": "1,500.00", "currency": {"code": "USD"}},
        "customer": {"name": "Microsoft Inc"},
        "dueDate": "2026-06-12",
        "invoiceDate": "2026-06-12",
        "business_name": "BranchlessPay Inc",
    },
    "payment.created": {
        "id": "pay-sample-1",
        "amount": "500.00",
        "date": "2026-06-12",
        "description": "Payment for INV-E2E-001",
        "customer": {"name": "Microsoft Inc"},
        "business_name": "BranchlessPay Inc",
    },
    "transaction.created": {
        "id": "txn-sample-1",
        "description": "Office supplies",
        "amount": "75.00",
        "date": "2026-06-12",
        "business_name": "BranchlessPay Inc",
    },
}

RESOURCE_IDS = {
    "invoice.created": "inv-sample-1",
    "invoice.updated": "inv-sample-1-upd",
    "payment.created": "pay-sample-1",
    "transaction.created": "txn-sample-1",
}


def run_event(app, client, event_type: str) -> dict:
    document = SAMPLE_DOCS[event_type]
    resource_id = RESOURCE_IDS[event_type]

    def _fetch(*_args, **_kwargs):
        return document

    payload = {
        "data": {
            "businessId": app.config["SETTINGS"].wave_business_id or "biz-e2e",
            "event": {
                "type": event_type,
                "timestamp": "2026-06-13T12:00:00Z",
                "resource": {"id": resource_id},
            },
        }
    }

    with patch(
        "wave_bp_collector.app.WaveClient.fetch_document", side_effect=_fetch
    ), patch("wave_bp_collector.app.AnchorIdempotencyStore") as mock_idem:
        mock_idem.return_value.get.return_value = None
        response = client.post("/webhook/wave", json=payload)

    body = response.get_json() or {}
    return {
        "event_type": event_type,
        "http_status": response.status_code,
        "ok": body.get("ok"),
        "anchor_id": body.get("anchor_id"),
        "verify_url": body.get("verify_url"),
        "error": body.get("error"),
    }


def main() -> int:
    settings = get_settings()
    if not settings.bp_license_key:
        print("BP_LICENSE_KEY is not configured", file=sys.stderr)
        return 1

    app = create_app(settings)
    client = app.test_client()
    results = [run_event(app, client, event_type) for event_type in SAMPLE_DOCS]

    print(json.dumps(results, indent=2))
    failed = [r for r in results if r.get("http_status") not in (200, 202) or not r.get("ok")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
