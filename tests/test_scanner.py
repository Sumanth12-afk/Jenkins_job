from __future__ import annotations

from datetime import timedelta

from src.core.models import BuildRecord, ImageTag, ServiceConfig, ThresholdConfig
from src.core.scanner import ImageRebuildScanner


class FakeArtifactClient:
    def __init__(self, tags):
        self.tags = tags

    def list_image_tags(self, service):
        return self.tags[service.name]


class FakeJenkinsClient:
    def __init__(self):
        self.calls = []

    def trigger_build(self, job_name, parameters):
        self.calls.append((job_name, parameters))
        return type("Trigger", (), {"queue_url": "https://jenkins/queue/1", "status_code": 201})()


class FakeStateStore:
    def __init__(self, active=False):
        self.active = active
        self.records = []

    def get_build(self, idempotency_key):
        if self.active:
            return BuildRecord(
                service_name="svc",
                current_tag="v1.0.0",
                new_tag="v1.0.0-rebuild-20260427",
                status="QUEUED",
                idempotency_key=idempotency_key,
            )
        return None

    def upsert_build(self, record):
        self.records.append(record)

    def has_active_build(self, idempotency_key):
        return self.active


def service():
    return ServiceConfig(
        name="svc",
        repository="repo",
        location="us",
        package="pkg",
        jenkins_job="folder/svc",
        tag_prefix="v",
    )


def test_scanner_dry_run_finds_stale_without_triggering(fixed_now):
    svc = service()
    artifact = FakeArtifactClient({svc.name: [ImageTag("v1.0.0", fixed_now - timedelta(days=50))]})
    jenkins = FakeJenkinsClient()
    state = FakeStateStore()
    scanner = ImageRebuildScanner(
        artifact,
        jenkins,
        state,
        ThresholdConfig(max_image_age_days=45),
        dry_run=True,
        now=fixed_now,
    )

    candidates = scanner.run([svc])

    assert candidates[0].new_tag == "v1.0.0-rebuild-20260427"
    assert jenkins.calls == []
    assert state.records == []


def test_scanner_triggers_and_records_queued_build(fixed_now):
    svc = service()
    artifact = FakeArtifactClient({svc.name: [ImageTag("v1.0.0", fixed_now - timedelta(days=50))]})
    jenkins = FakeJenkinsClient()
    state = FakeStateStore()
    scanner = ImageRebuildScanner(
        artifact,
        jenkins,
        state,
        ThresholdConfig(max_image_age_days=45),
        now=fixed_now,
    )

    scanner.run([svc])

    assert jenkins.calls[0][0] == "folder/svc"
    assert jenkins.calls[0][1]["IDEMPOTENCY_KEY"] == "svc:v1.0.0:v1.0.0-rebuild-20260427"
    assert state.records[0].status == "QUEUED"


def test_scanner_skips_duplicate_active_build(fixed_now):
    svc = service()
    artifact = FakeArtifactClient({svc.name: [ImageTag("v1.0.0", fixed_now - timedelta(days=50))]})
    jenkins = FakeJenkinsClient()
    state = FakeStateStore(active=True)
    scanner = ImageRebuildScanner(
        artifact,
        jenkins,
        state,
        ThresholdConfig(max_image_age_days=45),
        now=fixed_now,
    )

    scanner.run([svc])

    assert jenkins.calls == []
    assert state.records == []
