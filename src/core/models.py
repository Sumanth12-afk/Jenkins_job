from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ServiceConfig:
    name: str
    repository: str
    location: str
    package: str
    jenkins_job: str
    tag_prefix: str | None = None
    base_image: str | None = None
    git_repo_url: str | None = None
    git_branch: str = "main"
    dockerfile_path: str = "Dockerfile"
    build_context: str = "."


@dataclass(frozen=True)
class ThresholdConfig:
    max_image_age_days: int = 45
    max_image_age_minutes: int | None = None
    rebuild_tag_suffix: str = "rebuild"

    @property
    def max_age(self) -> timedelta:
        if self.max_image_age_minutes is not None:
            return timedelta(minutes=self.max_image_age_minutes)
        return timedelta(days=self.max_image_age_days)


@dataclass(frozen=True)
class ImageTag:
    tag: str
    created_at: datetime
    digest: str | None = None

    @property
    def age_days(self) -> int:
        return (utc_now() - self.created_at).days


@dataclass(frozen=True)
class RebuildCandidate:
    service: ServiceConfig
    current_tag: str
    new_tag: str
    image_age_days: int
    reason: str

    @property
    def idempotency_key(self) -> str:
        return f"{self.service.name}:{self.current_tag}:{self.new_tag}"

    def jenkins_parameters(self) -> dict[str, str]:
        parameters = {
            "SERVICE_NAME": self.service.name,
            "CURRENT_IMAGE_TAG": self.current_tag,
            "NEW_IMAGE_TAG": self.new_tag,
            "REBUILD_REASON": self.reason,
            "ARTIFACT_REGISTRY_LOCATION": self.service.location,
            "ARTIFACT_REGISTRY_REPOSITORY": self.service.repository,
            "IMAGE_PACKAGE": self.service.package,
            "GIT_BRANCH": self.service.git_branch,
            "DOCKERFILE_PATH": self.service.dockerfile_path,
            "BUILD_CONTEXT": self.service.build_context,
            "IDEMPOTENCY_KEY": self.idempotency_key,
        }
        if self.service.git_repo_url:
            parameters["GIT_REPO_URL"] = self.service.git_repo_url
        return parameters


@dataclass(frozen=True)
class BuildRecord:
    service_name: str
    current_tag: str
    new_tag: str
    status: str
    idempotency_key: str
    jenkins_job: str | None = None
    jenkins_queue_url: str | None = None
    jenkins_build_url: str | None = None
    error: str | None = None
    updated_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "service_name": self.service_name,
            "current_tag": self.current_tag,
            "new_tag": self.new_tag,
            "status": self.status,
            "idempotency_key": self.idempotency_key,
            "jenkins_job": self.jenkins_job,
            "jenkins_queue_url": self.jenkins_queue_url,
            "jenkins_build_url": self.jenkins_build_url,
            "error": self.error,
            "updated_at": (self.updated_at or utc_now()).isoformat(),
        }
        return {key: value for key, value in data.items() if value is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuildRecord":
        updated_at = data.get("updated_at")
        parsed_updated_at = None
        if updated_at:
            parsed_updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return cls(
            service_name=data["service_name"],
            current_tag=data["current_tag"],
            new_tag=data["new_tag"],
            status=data["status"],
            idempotency_key=data["idempotency_key"],
            jenkins_job=data.get("jenkins_job"),
            jenkins_queue_url=data.get("jenkins_queue_url"),
            jenkins_build_url=data.get("jenkins_build_url"),
            error=data.get("error"),
            updated_at=parsed_updated_at,
        )
