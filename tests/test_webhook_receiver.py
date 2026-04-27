from __future__ import annotations

import os

from cloud_functions.jenkins_webhook_receiver.main import jenkins_webhook_receiver


class FakeRequest:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, silent=True):
        return self.payload


def test_webhook_dry_run_skips_mutations(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "true")
    payload = {
        "service_name": "svc",
        "current_tag": "v1",
        "new_tag": "v1-rebuild-20260427",
        "status": "SUCCESS",
        "idempotency_key": "svc:v1:v1-rebuild-20260427",
    }

    body, status = jenkins_webhook_receiver(FakeRequest(payload))

    assert status == 200
    assert body["dry_run"] is True


def test_webhook_validates_required_payload(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "true")

    body, status = jenkins_webhook_receiver(FakeRequest({}))

    assert status == 400
    assert "missing required" in body["error"]
