from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.core.models import ServiceConfig, ThresholdConfig


class ConfigError(ValueError):
    """Raised when YAML configuration is missing required values."""


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a YAML mapping")
    return data


def load_services(path: str | Path) -> list[ServiceConfig]:
    data = _load_yaml(path)
    raw_services = data.get("services", [])
    if not isinstance(raw_services, list):
        raise ConfigError("services.yaml must contain a 'services' list")

    services: list[ServiceConfig] = []
    for item in raw_services:
        if not isinstance(item, dict):
            raise ConfigError("Each service entry must be a mapping")
        missing = [
            key
            for key in ("name", "repository", "location", "package", "jenkins_job")
            if not item.get(key)
        ]
        if missing:
            raise ConfigError(f"Service entry is missing: {', '.join(missing)}")
        services.append(
            ServiceConfig(
                name=item["name"],
                repository=item["repository"],
                location=item["location"],
                package=item["package"],
                jenkins_job=item["jenkins_job"],
                tag_prefix=item.get("tag_prefix"),
                base_image=item.get("base_image"),
                git_repo_url=item.get("git_repo_url"),
                git_branch=item.get("git_branch", "main"),
                dockerfile_path=item.get("dockerfile_path", "Dockerfile"),
                build_context=item.get("build_context", "."),
            )
        )
    return services


def load_thresholds(path: str | Path) -> ThresholdConfig:
    data = _load_yaml(path)
    return ThresholdConfig(
        max_image_age_days=int(data.get("max_image_age_days", 45)),
        max_image_age_minutes=(
            int(data["max_image_age_minutes"]) if data.get("max_image_age_minutes") is not None else None
        ),
        rebuild_tag_suffix=str(data.get("rebuild_tag_suffix", "rebuild")),
    )
