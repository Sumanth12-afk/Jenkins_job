from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from src.core.models import BuildRecord


TERMINAL_STATUSES = {"SUCCESS", "FAILURE", "ABORTED", "UNSTABLE"}
ACTIVE_STATUSES = {"PENDING", "QUEUED", "RUNNING"}


class StateStoreProtocol(Protocol):
    def get_build(self, idempotency_key: str) -> BuildRecord | None:
        ...

    def upsert_build(self, record: BuildRecord) -> None:
        ...

    def has_active_build(self, idempotency_key: str) -> bool:
        ...


class LocalStateStore:
    def __init__(self, path: str | Path = "local_state.json"):
        self.path = Path(path)

    def _read(self) -> dict[str, dict]:
        if not self.path.exists():
            return {"builds": {}}
        with self.path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        data.setdefault("builds", {})
        return data

    def _write(self, data: dict[str, dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    def get_build(self, idempotency_key: str) -> BuildRecord | None:
        data = self._read()["builds"].get(idempotency_key)
        return BuildRecord.from_dict(data) if data else None

    def upsert_build(self, record: BuildRecord) -> None:
        data = self._read()
        data["builds"][record.idempotency_key] = record.to_dict()
        self._write(data)

    def has_active_build(self, idempotency_key: str) -> bool:
        record = self.get_build(idempotency_key)
        return bool(record and record.status in ACTIVE_STATUSES)


class FirestoreStateStore:
    def __init__(self, project_id: str, collection: str = "image_rebuilds"):
        from google.cloud import firestore

        self._client = firestore.Client(project=project_id)
        self._collection = self._client.collection(collection)

    def get_build(self, idempotency_key: str) -> BuildRecord | None:
        snapshot = self._collection.document(idempotency_key).get()
        if not snapshot.exists:
            return None
        return BuildRecord.from_dict(snapshot.to_dict())

    def upsert_build(self, record: BuildRecord) -> None:
        self._collection.document(record.idempotency_key).set(record.to_dict(), merge=True)

    def has_active_build(self, idempotency_key: str) -> bool:
        record = self.get_build(idempotency_key)
        return bool(record and record.status in ACTIVE_STATUSES)
