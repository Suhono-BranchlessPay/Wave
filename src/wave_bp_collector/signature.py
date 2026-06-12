"""Wave webhook HMAC-SHA256 verification (Wave-Signature header)."""

import hashlib
import hmac
import time
from typing import Mapping


def parse_wave_signature_header(header_value: str) -> tuple[str, list[str]]:
    parts: dict[str, str] = {}
    for segment in header_value.split(","):
        segment = segment.strip()
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        parts[key.strip()] = value.strip()

    timestamp = parts.get("t", "")
    signatures = [value for key, value in parts.items() if key.startswith("v1")]
    if not signatures and "v1" in parts:
        signatures = [parts["v1"]]
    return timestamp, signatures


def compute_signature(webhook_secret: str, timestamp: str, raw_body: bytes | str) -> str:
    if isinstance(raw_body, bytes):
        body_text = raw_body.decode("utf-8")
    else:
        body_text = raw_body
    signed_payload = "%s.%s" % (timestamp, body_text)
    return hmac.new(
        webhook_secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def verify_signature(
    webhook_secret: str,
    raw_body: bytes | str,
    signature_header: str | None,
    *,
    tolerance_sec: int = 300,
    now: int | None = None,
) -> bool:
    if not webhook_secret or not signature_header:
        return False

    timestamp, received_signatures = parse_wave_signature_header(signature_header.strip())
    if not timestamp or not received_signatures:
        return False

    current = now if now is not None else int(time.time())
    try:
        if abs(current - int(timestamp)) > tolerance_sec:
            return False
    except ValueError:
        return False

    expected = compute_signature(webhook_secret, timestamp, raw_body)
    return any(hmac.compare_digest(expected, sig) for sig in received_signatures)


def get_signature_header(headers: Mapping[str, str]) -> str | None:
    for key, value in headers.items():
        lowered = key.lower()
        if lowered in ("wave-signature", "x-wave-signature"):
            return value
    return None
