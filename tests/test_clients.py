from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import requests

from src.clients.artifact_registry import GCPArtifactRegistryClient
from src.clients.email_client import SendGridEmailClient
from src.clients.jenkins import JenkinsClient
from src.core.models import ServiceConfig


def test_jenkins_client_posts_parameterized_build(monkeypatch):
    response = requests.Response()
    response.status_code = 201
    response.headers["Location"] = "https://jenkins/queue/item/1"
    post = Mock(return_value=response)
    client = JenkinsClient("https://jenkins", "user", "token")
    client.session.post = post

    trigger = client.trigger_build("folder/my-service", {"SERVICE_NAME": "my-service"})

    assert trigger.queue_url == "https://jenkins/queue/item/1"
    post.assert_called_once()
    assert post.call_args.kwargs["params"]["SERVICE_NAME"] == "my-service"


def test_email_client_posts_sendgrid_payload(monkeypatch):
    response = requests.Response()
    response.status_code = 202
    post = Mock(return_value=response)
    monkeypatch.setattr("src.clients.email_client.requests.post", post)

    SendGridEmailClient("key", sender="bot@example.com").send("qa@example.com", "Subject", "<b>Body</b>")

    payload = post.call_args.kwargs["json"]
    assert payload["personalizations"][0]["to"][0]["email"] == "qa@example.com"
    assert payload["subject"] == "Subject"


def test_artifact_registry_client_maps_versions_to_tags(monkeypatch, fixed_now):
    fake_module = SimpleNamespace(ArtifactRegistryClient=Mock())
    fake_client = fake_module.ArtifactRegistryClient.return_value
    fake_client.list_versions.return_value = [
        SimpleNamespace(
            name="projects/p/locations/us/repositories/r/packages/pkg/versions/sha256:abc",
            create_time=fixed_now,
        )
    ]
    fake_client.list_tags.return_value = [
        SimpleNamespace(
            name="projects/p/locations/us/repositories/r/packages/pkg/tags/v1.0.0",
            version="projects/p/locations/us/repositories/r/packages/pkg/versions/sha256:abc",
        )
    ]

    monkeypatch.setitem(__import__("sys").modules, "google.cloud.artifactregistry_v1", fake_module)
    client = GCPArtifactRegistryClient("project")
    service = ServiceConfig("svc", "repo", "us", "pkg", "job")

    tags = client.list_image_tags(service)

    assert tags[0].tag == "v1.0.0"
    assert tags[0].digest == "sha256:abc"
