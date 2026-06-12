"""Wave GraphQL API client with OAuth refresh and retries."""

import logging
import time
from typing import Any

import requests

_logger = logging.getLogger(__name__)

WAVE_TOKEN_URL = "https://api.waveapps.com/oauth2/token/"
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 1.5

INVOICE_QUERY = """
query ($businessId: ID!, $invoiceId: ID!) {
  business(id: $businessId) {
    id
    name
    address {
      addressLine1
      addressLine2
      city
      postalCode
      country { name }
      province { name }
    }
    invoice(id: $invoiceId) {
      id
      invoiceNumber
      status
      dueDate
      invoiceDate
      amountDue { value currency { code } }
      total { value currency { code } }
      customer { name email }
    }
  }
}
"""

PAYMENT_QUERY = """
query ($businessId: ID!, $paymentId: ID!) {
  business(id: $businessId) {
    id
    name
    address {
      addressLine1
      city
      postalCode
      country { name }
      province { name }
    }
    moneyTransaction(id: $paymentId) {
      id
      amount
      date
      description
      customer { name email }
    }
  }
}
"""

TRANSACTION_QUERY = """
query ($businessId: ID!, $transactionId: ID!) {
  business(id: $businessId) {
    id
    name
    address {
      addressLine1
      city
      postalCode
      country { name }
      province { name }
    }
    transaction(id: $transactionId) {
      id
      description
      amount
      date
    }
  }
}
"""


class WaveClient:
    def __init__(
        self,
        access_token: str,
        graphql_url: str,
        refresh_token: str = "",
        client_id: str = "",
        client_secret: str = "",
    ):
        self.access_token = access_token
        self.graphql_url = graphql_url
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": "Bearer %s" % self.access_token,
            "Content-Type": "application/json",
        }

    def refresh_access_token(self) -> None:
        if not all([self.refresh_token, self.client_id, self.client_secret]):
            raise RuntimeError("OAuth refresh credentials not configured")
        response = requests.post(
            WAVE_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]
        _logger.info("Wave access token refreshed")

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        url = self.graphql_url
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    url,
                    json={"query": query, "variables": variables},
                    headers=self._headers,
                    timeout=20,
                )
                if response.status_code == 401 and attempt == 1:
                    self.refresh_access_token()
                    continue
                response.raise_for_status()
                payload = response.json()
                if payload.get("errors"):
                    raise RuntimeError("GraphQL errors: %s" % payload["errors"])
                return payload.get("data") or {}
            except Exception as exc:
                last_error = exc
                _logger.warning(
                    "Wave GraphQL attempt %s/%s failed: %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SEC * attempt)
        raise RuntimeError(
            "Wave GraphQL failed after %s retries: %s" % (MAX_RETRIES, last_error)
        )

    def fetch_document(
        self, event_type: str, business_id: str, resource_id: str
    ) -> dict[str, Any]:
        if event_type.startswith("invoice."):
            data = self._graphql(
                INVOICE_QUERY,
                {"businessId": business_id, "invoiceId": resource_id},
            )
            return _merge_business_document(data, "invoice", business_id)

        if event_type.startswith("payment."):
            data = self._graphql(
                PAYMENT_QUERY,
                {"businessId": business_id, "paymentId": resource_id},
            )
            return _merge_business_document(data, "moneyTransaction", business_id)

        if event_type.startswith("transaction."):
            data = self._graphql(
                TRANSACTION_QUERY,
                {"businessId": business_id, "transactionId": resource_id},
            )
            return _merge_business_document(data, "transaction", business_id)

        raise ValueError("Unsupported event type for fetch: %s" % event_type)


def _merge_business_document(
    data: dict[str, Any], resource_key: str, business_id: str
) -> dict[str, Any]:
    business = data.get("business") or {}
    document = business.get(resource_key) or {}
    if not document:
        raise ValueError("Wave resource not found: %s" % resource_key)

    merged = dict(document)
    merged["business_id"] = business_id
    merged["business_name"] = business.get("name")
    merged["address"] = business.get("address")
    return merged
