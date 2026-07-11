from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import os
from cryptography.fernet import Fernet

import aiosqlite

NAMESPACE_UUID = uuid.UUID("9897d6fd-d6a7-4fe9-86bc-f0c312886d5d")
ZERO_HASH = "0" * 64

def _canonical_json(data: Any) -> str:
    # RFC 8785 strict canonicalization barrier approximation for Python
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def _compute_entry_hash(
    event_id: str, stream: str, entity_id: str, event_type: str,
    payload_json: str, source_db: str, source_table: str, source_pk: str,
    cortex_taint: str, lamport_t: int, prev_hash: str, created_at: str
) -> str:
    envelope = {
        "event_id": event_id, "stream": stream, "entity_id": entity_id,
        "event_type": event_type, "payload_json": payload_json, "source_db": source_db,
        "source_table": source_table, "source_pk": source_pk, "cortex_taint": cortex_taint,
        "lamport_t": lamport_t, "prev_hash": prev_hash, "created_at": created_at
    }
    return hashlib.sha256(_canonical_json(envelope).encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class LedgerEvent:
    stream: str
    entity_id: str
    event_type: str
    payload: Dict[str, Any]
    cortex_taint: str
    source_db: str
    source_table: str
    source_pk: str
    created_at: Optional[str] = None

class BFTLedgerActor:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._queue: asyncio.Queue[tuple[LedgerEvent, asyncio.Future]] = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        await self._queue.join()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def append(self, event: LedgerEvent) -> asyncio.Future[Dict[str, Any]]:
        # INV_BFT_07 Zombie Actor Prevention
        if self._task and self._task.done():
            raise RuntimeError("C5 BFT Fail-Fast: Zombie Actor detected. The _worker task has died in silence.")
            
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._queue.put_nowait((event, future))
        return future

    async def _worker(self) -> None:
        async with aiosqlite.connect(self._db_path, isolation_level=None) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA synchronous=FULL")
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("PRAGMA busy_timeout=5000")

            while True:
                try:
                    event, future = await self._queue.get()
                except asyncio.CancelledError:
                    break

                try:
                    await self._process(db, event, future)
                except RuntimeError as exc:
                    if not future.done():
                        future.set_exception(exc)
                finally:
                    self._queue.task_done()

    async def _process(self, db: aiosqlite.Connection, event: LedgerEvent, future: asyncio.Future) -> None:
        payload_json = _canonical_json(event.payload)
        created_at = event.created_at or datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

        idempotent_key = f"{event.source_db}\x1f{event.source_table}\x1f{event.source_pk}\x1f{payload_json}\x1f{event.cortex_taint}"
        event_id = str(uuid.uuid5(NAMESPACE_UUID, idempotent_key))

        try:
            await db.execute("BEGIN IMMEDIATE")

            # INV_BFT_05 Idempotency Masking
            cur = await db.execute("SELECT seq, entry_hash FROM ledger_entries WHERE event_id = ?", (event_id,))
            existing_row = await cur.fetchone()
            if existing_row:
                await db.execute("ROLLBACK")
                future.set_result({"seq": existing_row[0], "event_id": event_id, "entry_hash": existing_row[1]})
                return

            cur = await db.execute("SELECT lamport_t, entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1")
            row = await cur.fetchone()
            prev_lamport = int(row[0]) if row else 0
            prev_hash = row[1] if row else ZERO_HASH

            lamport_t = prev_lamport + 1

            entry_hash = _compute_entry_hash(
                event_id=event_id, stream=event.stream, entity_id=event.entity_id,
                event_type=event.event_type, payload_json=payload_json, source_db=event.source_db,
                source_table=event.source_table, source_pk=event.source_pk,
                cortex_taint=event.cortex_taint, lamport_t=lamport_t, prev_hash=prev_hash, created_at=created_at
            )

            # C5-REAL Encryption 
            vault_key = os.environ.get("CORTEX_VAULT_KEY")
            if vault_key:
                fernet = Fernet(vault_key.encode("utf-8"))
                stored_payload = fernet.encrypt(payload_json.encode("utf-8")).decode("utf-8")
                # Prefix to distinguish encrypted payloads if needed
                stored_payload = f"C5ENC:{stored_payload}"
            else:
                stored_payload = payload_json

            cursor = await db.execute(
                """INSERT INTO ledger_entries (
                    event_id, stream, entity_id, event_type, payload_json,
                    source_db, source_table, source_pk, cortex_taint,
                    lamport_t, prev_hash, entry_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING seq, entry_hash""",
                (
                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,
                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,
                    lamport_t, prev_hash, entry_hash, created_at
                )
            )
            db_row = await cursor.fetchone()
            if db_row is None:
                raise RuntimeError("Insertion failed: event_id not persisted")

            await db.execute("COMMIT")
            future.set_result({"seq": db_row[0], "event_id": event_id, "entry_hash": db_row[1]})
        except RuntimeError as exc:
            try:
                await db.execute("ROLLBACK")
            except RuntimeError as rollback_exc:
                # INV_BFT_06 Cascading Rollback Defense
                await db.close()
                raise RuntimeError(f"C5 BFT Fail-Fast: ROLLBACK failed, closing irrecoverable connection. Root error: {exc}. Rollback error: {rollback_exc}") from exc
            
            if not future.done():
                future.set_exception(exc)
