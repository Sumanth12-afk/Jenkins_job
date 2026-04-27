from __future__ import annotations

import re
from datetime import datetime, timezone

from src.core.models import ImageTag, ThresholdConfig


DATE_REBUILD_PATTERN = re.compile(r"-rebuild-\d{8}$")


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def select_latest_tag(tags: list[ImageTag], tag_prefix: str | None = None) -> ImageTag | None:
    filtered = tags
    if tag_prefix:
        filtered = [item for item in tags if item.tag.startswith(tag_prefix)]
    if not filtered:
        return None
    return max(filtered, key=lambda item: normalize_datetime(item.created_at))


def is_stale(tag: ImageTag, thresholds: ThresholdConfig, now: datetime | None = None) -> bool:
    now = normalize_datetime(now or datetime.now(timezone.utc))
    created_at = normalize_datetime(tag.created_at)
    return (now - created_at) >= thresholds.max_age


def build_rebuild_tag(current_tag: str, thresholds: ThresholdConfig, now: datetime | None = None) -> str:
    now = normalize_datetime(now or datetime.now(timezone.utc))
    base_tag = DATE_REBUILD_PATTERN.sub("", current_tag)
    return f"{base_tag}-{thresholds.rebuild_tag_suffix}-{now:%Y%m%d}"
