from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime, timezone

from src.clients.artifact_registry import ArtifactRegistryClientProtocol, GCPArtifactRegistryClient
from src.clients.jenkins import JenkinsClient, JenkinsClientProtocol
from src.clients.state_store import FirestoreStateStore, LocalStateStore, StateStoreProtocol
from src.core.models import BuildRecord
from src.core.models import RebuildCandidate, ServiceConfig, ThresholdConfig, utc_now
from src.utils.config_loader import load_services, load_thresholds
from src.utils.tag_filter import build_rebuild_tag, is_stale, select_latest_tag

LOGGER = logging.getLogger(__name__)


class ImageRebuildScanner:
    def __init__(
        self,
        artifact_client: ArtifactRegistryClientProtocol,
        jenkins_client: JenkinsClientProtocol,
        state_store: StateStoreProtocol,
        thresholds: ThresholdConfig,
        *,
        dry_run: bool = False,
        now: datetime | None = None,
    ):
        self.artifact_client = artifact_client
        self.jenkins_client = jenkins_client
        self.state_store = state_store
        self.thresholds = thresholds
        self.dry_run = dry_run
        self.now = now or datetime.now(timezone.utc)

    def evaluate_service(self, service: ServiceConfig) -> RebuildCandidate | None:
        tags = self.artifact_client.list_image_tags(service)
        latest = select_latest_tag(tags, service.tag_prefix)
        if latest is None:
            LOGGER.warning("No tags found for service", extra={"service": service.name})
            return None
        if not is_stale(latest, self.thresholds, self.now):
            LOGGER.info("Image is within policy", extra={"service": service.name, "tag": latest.tag})
            return None
        new_tag = build_rebuild_tag(latest.tag, self.thresholds, self.now)
        return RebuildCandidate(
            service=service,
            current_tag=latest.tag,
            new_tag=new_tag,
            image_age_days=(self.now - latest.created_at).days,
            reason=f"image older than {self.thresholds.max_age}",
        )

    def run(self, services: list[ServiceConfig]) -> list[RebuildCandidate]:
        candidates: list[RebuildCandidate] = []
        for service in services:
            try:
                candidate = self.evaluate_service(service)
                if not candidate:
                    continue
                candidates.append(candidate)
                existing = self.state_store.get_build(candidate.idempotency_key)
                if existing and existing.status not in {"FAILURE", "ABORTED"}:
                    LOGGER.info(
                        "Skipping duplicate rebuild",
                        extra={"key": candidate.idempotency_key, "status": existing.status},
                    )
                    continue
                if self.dry_run:
                    LOGGER.info(
                        "Dry run: would trigger Jenkins rebuild",
                        extra={"service": service.name, "new_tag": candidate.new_tag},
                    )
                    continue
                parameters = candidate.jenkins_parameters()
                if os.getenv("GCP_PROJECT_ID"):
                    parameters["GCP_PROJECT_ID"] = os.environ["GCP_PROJECT_ID"]
                if os.getenv("JENKINS_WEBHOOK_URL"):
                    parameters["WEBHOOK_URL"] = os.environ["JENKINS_WEBHOOK_URL"]
                trigger = self.jenkins_client.trigger_build(service.jenkins_job, parameters)
                self.state_store.upsert_build(
                    BuildRecord(
                        service_name=service.name,
                        current_tag=candidate.current_tag,
                        new_tag=candidate.new_tag,
                        status="QUEUED",
                        idempotency_key=candidate.idempotency_key,
                        jenkins_job=service.jenkins_job,
                        jenkins_queue_url=trigger.queue_url,
                        updated_at=utc_now(),
                    )
                )
                LOGGER.info("Triggered Jenkins rebuild", extra={"service": service.name})
            except Exception:
                LOGGER.exception("Failed to process service", extra={"service": service.name})
        return candidates


def build_default_state_store(project_id: str | None, use_firestore: bool) -> StateStoreProtocol:
    if use_firestore:
        if not project_id:
            raise ValueError("GCP_PROJECT_ID is required when using Firestore")
        return FirestoreStateStore(project_id)
    return LocalStateStore(os.getenv("LOCAL_STATE_PATH", "local_state.json"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan Artifact Registry images and trigger stale rebuilds.")
    parser.add_argument("--services-config", default="config/services.yaml")
    parser.add_argument("--thresholds-config", default="config/thresholds.yaml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-firestore", action="store_true")
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    args = parse_args()
    project_id = os.getenv("GCP_PROJECT_ID")
    services = load_services(args.services_config)
    thresholds = load_thresholds(args.thresholds_config)
    scanner = ImageRebuildScanner(
        artifact_client=GCPArtifactRegistryClient(project_id or ""),
        jenkins_client=JenkinsClient(
            os.environ["JENKINS_URL"],
            os.environ["JENKINS_USER"],
            os.environ["JENKINS_API_TOKEN"],
        ),
        state_store=build_default_state_store(project_id, args.use_firestore),
        thresholds=thresholds,
        dry_run=args.dry_run,
    )
    scanner.run(services)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
