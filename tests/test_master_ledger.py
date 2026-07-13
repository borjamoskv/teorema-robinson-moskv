import sqlite3
import pytest
import aiosqlite
from pathlib import Path
from bft.ledger_actor import BFTLedgerActor, LedgerEvent


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_ledger.db"


@pytest.fixture
def event_factory() -> "Any":

    def _create(idx: int) -> "Any":
        return LedgerEvent(
            stream="test_stream",
            entity_id=f"ent_{idx}",
            event_type="CREATED",
            payload={"foo": "bar", "idx": idx},
            cortex_taint="test_taint",
            source_db="test_db",
            source_table="test_tbl",
            source_pk=f"pk_{idx}",
        )

    return _create


@pytest.mark.asyncio
async def test_ledger_append_and_idempotency(db_path: Path, event_factory):
    async with aiosqlite.connect(db_path) as db:
        schema = Path("core/master_ledger.sql").read_text()
        await db.executescript(schema)
        await db.commit()
    actor = BFTLedgerActor(db_path)
    await actor.start()
    try:
        evt1 = event_factory(1)
        fut1 = actor.append(evt1)
        res1 = await fut1
        assert res1["seq"] == 1
        assert "event_id" in res1
        assert len(res1["entry_hash"]) == 64
        fut2 = actor.append(evt1)
        res2 = await fut2
        assert res2["seq"] == res1["seq"]
        assert res2["event_id"] == res1["event_id"]
        assert res2["entry_hash"] == res1["entry_hash"]
        async with aiosqlite.connect(db_path) as db:
            cur = await db.execute("SELECT COUNT(*) FROM ledger_entries")
            row = await cur.fetchone()
            assert row[0] == 1
        await actor.stop()
        with pytest.raises(RuntimeError, match="Zombie Actor Prevention triggered"):
            actor.append(event_factory(2))
    finally:
        await actor.stop()


@pytest.mark.asyncio
async def test_immutable_triggers(db_path: Path, event_factory):
    async with aiosqlite.connect(db_path) as db:
        schema = Path("core/master_ledger.sql").read_text()
        await db.executescript(schema)
        await db.commit()
    actor = BFTLedgerActor(db_path)
    await actor.start()
    try:
        evt = event_factory(1)
        res = await actor.append(evt)
        seq = res["seq"]
        async with aiosqlite.connect(db_path) as db:
            with pytest.raises(sqlite3.IntegrityError, match="immutable master ledger"):
                await db.execute(
                    "UPDATE ledger_entries SET payload_json = 'foo' WHERE seq = ?",
                    (seq,),
                )
            with pytest.raises(sqlite3.IntegrityError, match="immutable master ledger"):
                await db.execute("DELETE FROM ledger_entries WHERE seq = ?", (seq,))
    finally:
        await actor.stop()
