from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timezone
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2026, 4, 27, tzinfo=timezone.utc)
