from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from src.clients.email_client import SMTPEmailClient
from src.clients.state_store import BuildRecord, FirestoreStateStore, LocalStateStore
from src.notifications.reporter import build_rebuild_report

LOGGER = logging.getLogger(__name__)


def _state_store():
    project_id = os.getenv("GCP_PROJECT_ID")
    if project_id and os.getenv("USE_FIRESTORE", "true").lower() == "true":
        return FirestoreStateStore(project_id)
    return LocalStateStore(os.getenv("LOCAL_STATE_PATH", "local_state.json"))


def _payload(request: Any) -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Webhook body must be JSON object")
    return data


def jenkins_webhook_receiver(request: Any):
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    data = _payload(request)
    required = ["service_name", "current_tag", "new_tag", "status", "idempotency_key"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        return {"error": f"missing required field(s): {', '.join(missing)}"}, 400

    record = BuildRecord(
        service_name=data["service_name"],
        current_tag=data["current_tag"],
        new_tag=data["new_tag"],
        status=data["status"],
        idempotency_key=data["idempotency_key"],
        jenkins_job=data.get("jenkins_job"),
        jenkins_queue_url=data.get("jenkins_queue_url"),
        jenkins_build_url=data.get("jenkins_build_url"),
        error=data.get("error"),
        updated_at=datetime.now(timezone.utc),
    )

    if dry_run:
        LOGGER.info("Dry run: would update state and send notification", extra=record.to_dict())
        return {"dry_run": True, "record": record.to_dict()}, 200

    store = _state_store()
    store.upsert_build(record)

    qa_email = os.getenv("QA_TEAM_EMAIL")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL", "automation@example.com")

    if qa_email and smtp_server:
        subject, body = build_rebuild_report([record])
        client = SMTPEmailClient(smtp_server, smtp_port, smtp_user or "", smtp_pass or "", sender_email)
        client.send(qa_email, subject, body)
    else:
        LOGGER.warning("Skipping email notification because QA_TEAM_EMAIL or SMTP_SERVER is missing")

    return {"ok": True, "record": record.to_dict()}, 200
