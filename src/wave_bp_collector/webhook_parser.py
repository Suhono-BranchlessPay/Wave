"""Parse Wave GraphQL webhook JSON payload."""

from dataclasses import dataclass
from typing import Any


ANCHOR_EVENTS = frozenset(
    {
        "invoice.created",
        "invoice.updated",
        "payment.created",
        "transaction.created",
    }
)

SUPPORTED_EVENTS = ANCHOR_EVENTS | frozenset({"customer.created"})


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    resource_id: str
    business_id: str
    timestamp: str
    raw: dict[str, Any]


def parse_webhook_payload(body: dict[str, Any]) -> WebhookEvent:
    data = body.get("data") if isinstance(body.get("data"), dict) else body
    business_id = str(
        data.get("businessId") or data.get("business_id") or ""
    ).strip()

    event = data.get("event") if isinstance(data.get("event"), dict) else {}
    event_type = str(event.get("type") or body.get("type") or "").strip()
    timestamp = str(event.get("timestamp") or body.get("timestamp") or "").strip()

    resource = event.get("resource") if isinstance(event.get("resource"), dict) else {}
    resource_id = str(
        resource.get("id")
        or event.get("resourceId")
        or body.get("resource_id")
        or ""
    ).strip()

    if not event_type:
        raise ValueError("Missing webhook event type")
    if not business_id:
        raise ValueError("Missing businessId")
    if not resource_id and event_type != "customer.created":
        raise ValueError("Missing resource id")

    return WebhookEvent(
        event_type=event_type,
        resource_id=resource_id,
        business_id=business_id,
        timestamp=timestamp,
        raw=body,
    )


def is_verification_ping(body: dict[str, Any]) -> bool:
    if body.get("challenge") or body.get("verification"):
        return True
    event_type = (
        (body.get("data") or {}).get("event", {}).get("type")
        if isinstance(body.get("data"), dict)
        else None
    )
    return event_type in ("webhook.test", "ping")
