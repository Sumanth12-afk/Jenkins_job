from __future__ import annotations

from pathlib import Path

from src.utils.config_loader import load_services, load_thresholds


def test_load_services(tmp_path: Path):
    config = tmp_path / "services.yaml"
    config.write_text(
        """
services:
  - name: svc
    repository: repo
    location: us
    package: pkg
    jenkins_job: folder/svc
""",
        encoding="utf-8",
    )

    services = load_services(config)

    assert services[0].name == "svc"
    assert services[0].jenkins_job == "folder/svc"


def test_load_thresholds_defaults(tmp_path: Path):
    config = tmp_path / "thresholds.yaml"
    config.write_text("{}", encoding="utf-8")

    thresholds = load_thresholds(config)

    assert thresholds.max_image_age_days == 45
    assert thresholds.max_image_age_minutes is None
    assert thresholds.rebuild_tag_suffix == "rebuild"


def test_load_thresholds_supports_minutes(tmp_path: Path):
    config = tmp_path / "thresholds.yaml"
    config.write_text("max_image_age_minutes: 5\n", encoding="utf-8")

    thresholds = load_thresholds(config)

    assert thresholds.max_image_age_minutes == 5
