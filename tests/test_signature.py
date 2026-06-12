import hashlib
import hmac
import json
import time

from wave_bp_collector.signature import compute_signature, verify_signature


def test_wave_signature_roundtrip():
    secret = "wave_test_secret"
    timestamp = str(int(time.time()))
    body = json.dumps(
        {
            "data": {
                "businessId": "biz-123",
                "event": {
                    "type": "invoice.created",
                    "timestamp": "2026-06-12T00:00:00Z",
                    "resource": {"id": "inv-1"},
                },
            }
        }
    )
    signature = "t=%s,v1=%s" % (
        timestamp,
        compute_signature(secret, timestamp, body),
    )
    assert verify_signature(secret, body, signature, now=int(timestamp))


def test_invalid_signature_rejected():
    assert not verify_signature("secret", b"{}", "t=1,v1=bad", now=1)
