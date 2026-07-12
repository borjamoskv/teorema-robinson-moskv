from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
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
        self._queue: asyncio.Queue[tuple[LedgerEvent, asyncio.Future[Dict[str, Any]]]] = asyncio.Queue()
        self._task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        if self._task:
            if not self._task.done():
                try:
                    await self._queue.join()
                except RuntimeError:
                    pass
                self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass

    def append(self, event: LedgerEvent) -> asyncio.Future[Dict[str, Any]]:
        # INV_BFT_07 (Zombie Actor Prevention)
        if self._task is None:
            raise RuntimeError("BFTLedgerActor: actor not started")
        if self._task.done():
            exc = self._task.exception()
            raise RuntimeError(
                f"Zombie Actor Prevention triggered: worker task terminated unexpectedly. Exception: {exc}"
            ) from exc

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._queue.put_nowait((event, future))
        return future

    async def verify_chain(self) -> bool:
        """
        Recalculates and verifies the cryptographic SHA-256 hash chain of all entries.
        """
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute("SELECT * FROM ledger_entries ORDER BY seq ASC")
            rows = await cursor.fetchall()
            
            prev_hash = ZERO_HASH
            expected_seq = 1
            last_lamport = 0
            
            for row in rows:
                seq = row[0]
                event_id = row[1]
                stream = row[2]
                entity_id = row[3]
                event_type = row[4]
                payload_json = row[5]
                source_db = row[6]
                source_table = row[7]
                source_pk = row[8]
                cortex_taint = row[9]
                lamport_t = row[10]
                row_prev_hash = row[11]
                entry_hash = row[12]
                created_at = row[13]
                
                if seq != expected_seq:
                    return False
                if lamport_t <= last_lamport:
                    return False
                if row_prev_hash != prev_hash:
                    return False

                vault_key = os.environ.get("CORTEX_VAULT_KEY")
                if vault_key and payload_json.startswith("C5ENC:"):
                    fernet = Fernet(vault_key.encode("utf-8"))
                    payload_json = fernet.decrypt(payload_json[6:].encode("utf-8")).decode("utf-8")
                    
                computed_hash = _compute_entry_hash(
                    event_id=event_id, stream=stream, entity_id=entity_id,
                    event_type=event_type, payload_json=payload_json, source_db=source_db,
                    source_table=source_table, source_pk=source_pk,
                    cortex_taint=cortex_taint, lamport_t=lamport_t, prev_hash=row_prev_hash, created_at=created_at
                )
                
                if entry_hash != computed_hash:
                    return False
                    
                prev_hash = entry_hash
                last_lamport = lamport_t
                expected_seq += 1
                
            return True

    async def _worker(self) -> None:
        async with aiosqlite.connect(self._db_path, isolation_level=None) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA synchronous=FULL")
            await db.execute("PRAGMA foreign_keys=ON")
            await db.execute("PRAGMA busy_timeout=5000")

            await self._init_db(db)

            while True:
                try:
                    event, future = await self._queue.get()
                except asyncio.CancelledError:
                    break

                try:
                    await self._process(db, event, future)
                except ValueError as exc:
                    # Error de validación (INV_BFT_03: cortex_taint vacío).
                    # Se entrega al caller y el worker SOBREVIVE: un input
                    # inválido no debe matar el actor ni colgar el future.
                    # Antes ValueError escapaba de este except (solo cazaba
                    # RuntimeError) → mataba el worker y el await colgaba: el
                    # invariante hacía deadlock en vez de enforcar.
                    if not future.done():
                        future.set_exception(exc)
                except Exception as exc:
                    # Error inesperado (corrupción, rollback fallido): se
                    # entrega al caller y se hace fail-fast (el worker muere →
                    # Zombie Actor Prevention salta en el siguiente append).
                    if not future.done():
                        future.set_exception(exc)
                    raise
                finally:
                    self._queue.task_done()

    async def _init_db(self, db: aiosqlite.Connection) -> None:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ledger_entries (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                stream TEXT NOT NULL CHECK (length(stream) > 0),
                entity_id TEXT NOT NULL CHECK (length(entity_id) > 0),
                event_type TEXT NOT NULL CHECK (length(event_type) > 0),
                payload_json TEXT NOT NULL CHECK (length(payload_json) >= 2),
                source_db TEXT NOT NULL CHECK (length(source_db) > 0),
                source_table TEXT NOT NULL CHECK (length(source_table) > 0),
                source_pk TEXT NOT NULL CHECK (length(source_pk) > 0),
                cortex_taint TEXT NOT NULL CHECK (length(cortex_taint) > 0),
                lamport_t INTEGER NOT NULL UNIQUE CHECK (lamport_t > 0),
                prev_hash TEXT NOT NULL CHECK (length(prev_hash) = 64 AND prev_hash GLOB '[0-9a-f]*'),
                entry_hash TEXT NOT NULL UNIQUE CHECK (length(entry_hash) = 64 AND entry_hash GLOB '[0-9a-f]*'),
                created_at TEXT NOT NULL
            );
        """)
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_ledger_immutable_update BEFORE UPDATE ON ledger_entries
            BEGIN SELECT RAISE(ABORT, 'C5 BFT: immutable master ledger'); END;
        """)
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_ledger_immutable_delete BEFORE DELETE ON ledger_entries
            BEGIN SELECT RAISE(ABORT, 'C5 BFT: immutable master ledger'); END;
        """)

    async def _process(self, db: aiosqlite.Connection, event: LedgerEvent, future: asyncio.Future[Dict[str, Any]]) -> None:
        if not event.cortex_taint or not isinstance(event.cortex_taint, str):
            raise ValueError("INV_BFT_03: cortex_taint must be a non-empty string representing the causal trace")

        payload_json = _canonical_json(event.payload)
        created_at = event.created_at or datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

        idempotent_key = f"{event.source_db}\x1f{event.source_table}\x1f{event.source_pk}\x1f{payload_json}\x1f{event.cortex_taint}"
        event_id = str(uuid.uuid5(NAMESPACE_UUID, idempotent_key))

        try:
            await db.execute("BEGIN IMMEDIATE")

            # Check if event_id already exists to collapse retry peacefully (Split-Brain Mitigation INV_BFT_04)
            cursor = await db.execute("SELECT seq, entry_hash FROM ledger_entries WHERE event_id = ?", (event_id,))
            row = await cursor.fetchone()
            if row:
                await db.execute("COMMIT")
                future.set_result({"seq": row[0], "event_id": event_id, "entry_hash": row[1]})
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
                ON CONFLICT(event_id) DO NOTHING
                RETURNING seq, entry_hash""",
                (
                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,
                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,
                    lamport_t, prev_hash, entry_hash, created_at
                )
            )
            db_row = await cursor.fetchone()
            if db_row is None:
                # Idempotencia: el event_id ya existe, colisión pacífica resuelta en DB.
                cursor = await db.execute("SELECT seq, entry_hash FROM ledger_entries WHERE event_id = ?", (event_id,))
                db_row = await cursor.fetchone()
                if db_row is None:
                    raise RuntimeError("Insertion failed: event_id not persisted and not found")

            await db.execute("COMMIT")
            future.set_result({"seq": db_row[0], "event_id": event_id, "entry_hash": db_row[1]})
        except aiosqlite.IntegrityError as exc:
            # Other constraints (lamport_t, entry_hash) failing will drop here
            try:
                await db.execute("ROLLBACK")
            except RuntimeError as rollback_exc:
                try:
                    await db.close()
                except RuntimeError:
                    pass
                future.set_exception(exc)
                raise RuntimeError("Cascading Rollback Defense triggered: connection aborted during IntegrityError rollback") from rollback_exc
            future.set_exception(exc)
        except RuntimeError as exc:
            try:
                await db.execute("ROLLBACK")
            except RuntimeError as rollback_exc:
                # INV_BFT_06 (Cascading Rollback Defense)
                try:
                    await db.close()
                except RuntimeError:
                    pass
                future.set_exception(exc)
                raise RuntimeError("Cascading Rollback Defense triggered: connection aborted") from rollback_exc
            future.set_exception(exc)
