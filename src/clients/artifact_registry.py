from __future__ import annotations

from datetime import timezone
from typing import Protocol

from src.core.models import ImageTag, ServiceConfig


class ArtifactRegistryClientProtocol(Protocol):
    def list_image_tags(self, service: ServiceConfig) -> list[ImageTag]:
        ...


class GCPArtifactRegistryClient:
    def __init__(self, project_id: str):
        self.project_id = project_id
        from google.cloud import artifactregistry_v1

        self._client = artifactregistry_v1.ArtifactRegistryClient()

    def list_image_tags(self, service: ServiceConfig) -> list[ImageTag]:
        package_path = (
            f"projects/{self.project_id}/locations/{service.location}/repositories/"
            f"{service.repository}/packages/{service.package}"
        )
        request = {"parent": package_path}
        version_created_at: dict[str, object] = {}
        for version in self._client.list_versions(request=request):
            created_at = version.create_time
            if hasattr(created_at, "timestamp"):
                created_at = created_at.replace(tzinfo=timezone.utc)
            version_created_at[version.name] = created_at

        tags: list[ImageTag] = []
        for tag in self._client.list_tags(request=request):
            version_name = tag.version
            digest = version_name.rsplit("/", 1)[-1] if version_name else None
            created_at = version_created_at.get(version_name)
            if created_at is None:
                continue
            tags.append(ImageTag(tag=tag.name.rsplit("/", 1)[-1], created_at=created_at, digest=digest))
        return tags
