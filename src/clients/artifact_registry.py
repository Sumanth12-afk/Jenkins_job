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
        tags: list[ImageTag] = []
        for version in self._client.list_versions(request=request):
            digest = version.name.rsplit("/", 1)[-1]
            created_at = version.create_time
            if hasattr(created_at, "timestamp"):
                created_at = created_at.replace(tzinfo=timezone.utc)
            related_tags = list(getattr(version, "related_tags", []) or [])
            if related_tags:
                for tag in related_tags:
                    tags.append(ImageTag(tag=tag.tag, created_at=created_at, digest=digest))
            else:
                tags.append(ImageTag(tag=digest, created_at=created_at, digest=digest))
        return tags
