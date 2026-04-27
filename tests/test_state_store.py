from __future__ import annotations

from pathlib import Path

from src.clients.state_store import LocalStateStore
from src.core.models import BuildRecord


def test_local_state_store_upserts_and_reads_record(tmp_path: Path):
    store = LocalStateStore(tmp_path / "state.json")
    record = BuildRecord(
        service_name="svc",
        current_tag="v1",
        new_tag="v1-rebuild-20260427",
        status="QUEUED",
        idempotency_key="svc:v1:v1-rebuild-20260427",
    )

    store.upsert_build(record)

    assert store.get_build(record.idempotency_key).new_tag == record.new_tag
    assert store.has_active_build(record.idempotency_key)
