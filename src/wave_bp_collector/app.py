"""Flask webhook receiver — M1 + M2 pipeline."""

import json
import logging
from typing import Any

from flask import Flask, Request, jsonify, request

from .bp_poster import BPPoster
from .config import get_settings
from .idempotency import AnchorIdempotencyStore
from .normalizer import normalize_to_bp_payload
from .queue_store import FailedQueue
from .signature import get_signature_header, verify_signature
from .wave_client import WaveClient
from .webhook_parser import ANCHOR_EVENTS, is_verification_ping, parse_webhook_payload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
_logger = logging.getLogger(__name__)


def create_app(settings=None) -> Flask:
    settings = settings or get_settings()
    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "wave-bp-collector"}), 200

    @app.get("/webhook/wave")
    @app.post("/webhook/wave")
    def wave_webhook():
        if request.method == "GET":
            return jsonify({"ok": True, "verification": "ping"}), 200
        return _handle_webhook(request, settings)

    return app


def _handle_webhook(req: Request, settings) -> tuple[Any, int]:
    raw_body = req.get_data(cache=True)

    try:
        body = json.loads(raw_body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        _logger.warning("Webhook received invalid JSON")
        return jsonify({"ok": False, "error": "invalid json"}), 400

    if is_verification_ping(body):
        _logger.info("Wave verification ping received")
        return jsonify({"ok": True, "verification": "ping"}), 200

    signature_header = get_signature_header(req.headers)
    if not settings.skip_signature_verify:
        if not verify_signature(
            settings.wave_webhook_secret,
            raw_body,
            signature_header,
        ):
            _logger.warning("Invalid Wave webhook signature")
            return jsonify({"ok": False, "error": "unauthorized"}), 401
    else:
        _logger.warning("Signature verification skipped (dev mode)")

    try:
        event = parse_webhook_payload(body)
    except ValueError as exc:
        _logger.warning("Webhook parse error: %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 400

    _logger.info(
        "Webhook received event=%s resource_id=%s business_id=%s",
        event.event_type,
        event.resource_id,
        event.business_id,
    )

    if event.event_type not in ANCHOR_EVENTS:
        _logger.info("Ignoring non-anchor event: %s", event.event_type)
        return jsonify({"ok": True, "ignored": event.event_type}), 200

    idempotency = AnchorIdempotencyStore()
    idem_key = AnchorIdempotencyStore.make_key(
        event.business_id, event.event_type, event.resource_id
    )
    cached = idempotency.get(idem_key)
    if cached:
        _logger.info(
            "Idempotent hit key=%s anchor_id=%s", idem_key, cached.get("anchor_id")
        )
        return jsonify(cached), 202

    if not settings.wave_access_token:
        _logger.error("WAVE_ACCESS_TOKEN not configured")
        return jsonify({"ok": False, "error": "wave not configured"}), 503

    wave_client = WaveClient(
        access_token=settings.wave_access_token,
        graphql_url=settings.wave_graphql_url,
        refresh_token=settings.wave_refresh_token,
        client_id=settings.wave_client_id,
        client_secret=settings.wave_client_secret,
    )

    try:
        document = wave_client.fetch_document(
            event.event_type, event.business_id, event.resource_id
        )
    except Exception as exc:
        _logger.exception("Wave fetch failed: %s", exc)
        return jsonify({"ok": False, "error": "wave fetch failed"}), 502

    try:
        bp_payload = normalize_to_bp_payload(
            event.event_type,
            document,
            business_id=event.business_id or settings.wave_business_id,
            company_name=settings.wave_business_name,
            business_address=settings.wave_business_address,
            webhook_timestamp=event.timestamp,
        )
    except (TypeError, ValueError) as exc:
        _logger.exception("Normalize failed: %s", exc)
        return jsonify({"ok": False, "error": "normalize failed", "detail": str(exc)}), 422

    poster = BPPoster(
        license_key=settings.bp_license_key,
        api_url=settings.bp_api_url,
        queue=FailedQueue(settings.failed_queue_dir),
    )

    try:
        result = poster.post_anchor(bp_payload)
    except Exception as exc:
        _logger.exception("BP post failed: %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 502

    if not result.get("ok"):
        return jsonify(result), 502

    anchor_id = result.get("anchor_id")
    verify_url = (
        "https://branchlesspay.com/verify/%s" % anchor_id if anchor_id else None
    )

    response = {
        "ok": True,
        "event_type": event.event_type,
        "reference_id": bp_payload["reference_id"],
        "anchor_id": anchor_id,
        "verify_url": verify_url,
        "status": result.get("status"),
        "idempotent": False,
    }
    idempotency.save(idem_key, {**response, "idempotent": True})
    _logger.info("Pipeline complete verify_url=%s", verify_url)
    return jsonify(response), 202


if __name__ == "__main__":
    cfg = get_settings()
    create_app(cfg).run(host=cfg.host, port=cfg.port, debug=False)
