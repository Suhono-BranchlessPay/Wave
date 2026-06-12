"""Environment configuration — no hardcoded credentials."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bp_license_key: str
    bp_api_url: str
    wave_client_id: str
    wave_client_secret: str
    wave_access_token: str
    wave_refresh_token: str
    wave_business_id: str
    wave_business_name: str
    wave_business_address: str
    wave_webhook_secret: str
    wave_graphql_url: str
    host: str
    port: int
    skip_signature_verify: bool
    failed_queue_dir: str


def get_settings() -> Settings:
    root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return Settings(
        bp_license_key=os.getenv("BP_LICENSE_KEY", "").strip(),
        bp_api_url=os.getenv(
            "BP_API_URL", "https://branchlesspay.com/api/v1/anchor"
        ).rstrip("/"),
        wave_client_id=os.getenv("WAVE_CLIENT_ID", "").strip(),
        wave_client_secret=os.getenv("WAVE_CLIENT_SECRET", "").strip(),
        wave_access_token=os.getenv("WAVE_ACCESS_TOKEN", "").strip(),
        wave_refresh_token=os.getenv("WAVE_REFRESH_TOKEN", "").strip(),
        wave_business_id=os.getenv("WAVE_BUSINESS_ID", "").strip(),
        wave_business_name=os.getenv("WAVE_BUSINESS_NAME", "").strip(),
        wave_business_address=os.getenv("WAVE_BUSINESS_ADDRESS", "").strip(),
        wave_webhook_secret=os.getenv("WAVE_WEBHOOK_SECRET", "").strip(),
        wave_graphql_url=os.getenv(
            "WAVE_GRAPHQL_URL", "https://gql.waveapps.com/graphql/public"
        ).strip(),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        skip_signature_verify=os.getenv("WAVE_SKIP_SIGNATURE_VERIFY", "0").strip()
        in ("1", "true", "yes"),
        failed_queue_dir=os.getenv(
            "FAILED_QUEUE_DIR", os.path.join(root, "data", "failed_queue")
        ),
    )
