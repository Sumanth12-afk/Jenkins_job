from __future__ import annotations

from datetime import timedelta

from src.core.models import ImageTag, ThresholdConfig
from src.utils.tag_filter import build_rebuild_tag, is_stale, select_latest_tag


def test_select_latest_tag_respects_prefix(fixed_now):
    tags = [
        ImageTag("dev-1", fixed_now, "a"),
        ImageTag("v1.0.0", fixed_now - timedelta(days=2), "b"),
        ImageTag("v1.1.0", fixed_now - timedelta(days=1), "c"),
    ]

    assert select_latest_tag(tags, "v").tag == "v1.1.0"


def test_is_stale_uses_threshold(fixed_now):
    tag = ImageTag("v1.0.0", fixed_now - timedelta(days=45), "digest")

    assert is_stale(tag, ThresholdConfig(max_image_age_days=45), fixed_now)


def test_is_stale_supports_minute_threshold_for_poc(fixed_now):
    tag = ImageTag("v1.0.0", fixed_now - timedelta(minutes=5), "digest")

    assert is_stale(tag, ThresholdConfig(max_image_age_minutes=5), fixed_now)


def test_build_rebuild_tag_is_stable_for_existing_rebuild_suffix(fixed_now):
    assert build_rebuild_tag("v1.2.3-rebuild-20260101", ThresholdConfig(), fixed_now) == "v1.2.3-rebuild-20260427"
