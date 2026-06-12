import json
from unittest.mock import patch

from wave_bp_collector.app import create_app
from wave_bp_collector.config import Settings


def _settings(**overrides):
    base = dict(
        bp_license_key="bp_test_dummy",
        bp_api_url="https://branchlesspay.com/api/v1/anchor",
        wave_client_id="cid",
        wave_client_secret="sec",
        wave_access_token="access",
        wave_refresh_token="refresh",
        wave_business_id="biz-123",
        wave_business_name="Test Business LLC",
        wave_business_address="123 Main St, Austin, TX",
        wave_webhook_secret="wave_test_secret",
        wave_graphql_url="https://gql.waveapps.com/graphql/public",
        host="127.0.0.1",
        port=8080,
        skip_signature_verify=True,
        failed_queue_dir="data/failed_queue",
    )
    base.update(overrides)
    return Settings(**base)


@patch("wave_bp_collector.app.AnchorIdempotencyStore")
@patch("wave_bp_collector.app.WaveClient.fetch_document")
@patch("wave_bp_collector.app.BPPoster.post_anchor")
def test_webhook_pipeline(mock_post, mock_fetch, mock_idem_cls):
    mock_idem_cls.return_value.get.return_value = None
    mock_fetch.return_value = {
        "id": "inv-1",
        "invoiceNumber": "INV-0001",
        "status": "UNPAID",
        "amountDue": {"value": "750.00", "currency": {"code": "USD"}},
        "customer": {"name": "John Smith"},
        "dueDate": "2026-07-12",
        "invoiceDate": "2026-06-12",
        "business_name": "Test Business LLC",
    }
    mock_post.return_value = {
        "ok": True,
        "anchor_id": "test-anchor-id",
        "status": "queued",
    }

    app = create_app(_settings())
    client = app.test_client()
    payload = {
        "data": {
            "businessId": "biz-123",
            "event": {
                "type": "invoice.created",
                "timestamp": "2026-06-12T10:00:00Z",
                "resource": {"id": "inv-1"},
            },
        }
    }
    response = client.post(
        "/webhook/wave",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 202
    body = response.get_json()
    assert body["ok"] is True
    assert body["anchor_id"] == "test-anchor-id"
    assert "verify/" in body["verify_url"]
    posted_payload = mock_post.call_args[0][0]
    assert posted_payload["reference_id"] == "INV-0001"
    assert posted_payload["metadata"]["business_id"] == "biz-123"


def test_verification_ping_returns_200():
    app = create_app(_settings())
    client = app.test_client()
    response = client.post(
        "/webhook/wave",
        json={"challenge": "ping"},
    )
    assert response.status_code == 200


def test_get_verification_ping_returns_200():
    app = create_app(_settings())
    client = app.test_client()
    response = client.get("/webhook/wave")
    assert response.status_code == 200
