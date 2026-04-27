from __future__ import annotations

from datetime import datetime, timezone

import pytest


@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2026, 4, 27, tzinfo=timezone.utc)
