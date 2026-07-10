import asyncio
import os
import sqlite3
import pytest
from pathlib import Path
from bft.ledger_actor import BFTLedgerActor, LedgerEvent, ZERO_HASH, _canonical_json, _compute_entry_hash

DB_PATH = Path("test_ledger.db")

@pytest.fixture(autouse=True)
def cleanup():
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
        except OSError:
            pass
    yield
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
        except OSError:
            pass

@pytest.mark.asyncio
async def test_basic_append_and_chaining():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        event1 = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.created",
            payload={"value": 42},
            cortex_taint="test_actor_basic",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-1"
        )
        
        fut1 = actor.append(event1)
        res1 = await fut1
        
        assert res1["seq"] == 1
        assert "event_id" in res1
        assert len(res1["entry_hash"]) == 64

        # Read from database to verify values
        import aiosqlite
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT * FROM ledger_entries WHERE seq = 1")
            row = await cur.fetchone()
            assert row is not None
            assert row[1] == res1["event_id"]
            assert row[2] == "stream-1"
            assert row[3] == "entity-A"
            assert row[4] == "test.created"
            assert row[5] == _canonical_json({"value": 42})
            assert row[6] == "test_db"
            assert row[7] == "test_table"
            assert row[8] == "pk-1"
            assert row[9] == "test_actor_basic"
            assert row[10] == 1  # lamport_t
            assert row[11] == ZERO_HASH
            assert row[12] == res1["entry_hash"]

        # Append second event and verify chaining
        event2 = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.updated",
            payload={"value": 100},
            cortex_taint="test_actor_basic",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-2"
        )
        res2 = await actor.append(event2)
        assert res2["seq"] == 2
        
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT * FROM ledger_entries WHERE seq = 2")
            row = await cur.fetchone()
            assert row is not None
            assert row[10] == 2  # lamport_t
            assert row[11] == res1["entry_hash"]
            assert row[12] == res2["entry_hash"]

    finally:
        await actor.stop()

@pytest.mark.asyncio
async def test_concurrent_appends():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        events = [
            LedgerEvent(
                stream="stream-concurrency",
                entity_id="entity-C",
                event_type="test.concurrency",
                payload={"index": i},
                cortex_taint=f"test_concurrency_{i}",
                source_db="test_db",
                source_table="test_table",
                source_pk=f"pk-con-{i}"
            )
            for i in range(10)
        ]

        futures = [actor.append(ev) for ev in events]
        results = await asyncio.gather(*futures)

        assert len(results) == 10
        seqs = [r["seq"] for r in results]
        assert sorted(seqs) == list(range(1, 11))

        # Check cryptographic chain and lamport clock sequence
        import aiosqlite
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT seq, lamport_t, prev_hash, entry_hash FROM ledger_entries ORDER BY seq ASC")
            rows = await cur.fetchall()
            assert len(rows) == 10
            
            for idx, row in enumerate(rows):
                seq, lamport_t, prev_hash, entry_hash = row
                assert seq == idx + 1
                assert lamport_t == idx + 1
                if idx == 0:
                    assert prev_hash == ZERO_HASH
                else:
                    assert prev_hash == rows[idx - 1][3]

    finally:
        await actor.stop()

@pytest.mark.asyncio
async def test_immutability_triggers():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        event = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.created",
            payload={"value": 42},
            cortex_taint="test_immutability",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-1"
        )
        res = await actor.append(event)
        
        # Test manual update is blocked
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            with pytest.raises(sqlite3.IntegrityError) as excinfo:
                cursor.execute("UPDATE ledger_entries SET stream = 'corrupt' WHERE seq = 1")
            assert "immutable master ledger" in str(excinfo.value)

            # Test manual delete is blocked
            with pytest.raises(sqlite3.IntegrityError) as excinfo:
                cursor.execute("DELETE FROM ledger_entries WHERE seq = 1")
            assert "immutable master ledger" in str(excinfo.value)

    finally:
        await actor.stop()

@pytest.mark.asyncio
async def test_idempotent_retry_collapse():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        event = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.created",
            payload={"value": 42},
            cortex_taint="test_idempotency",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-1"
        )

        res1 = await actor.append(event)
        res2 = await actor.append(event)

        assert res1["seq"] == res2["seq"]
        assert res1["event_id"] == res2["event_id"]
        assert res1["entry_hash"] == res2["entry_hash"]

        import aiosqlite
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT COUNT(*) FROM ledger_entries")
            count = await cur.fetchone()
            assert count[0] == 1

    finally:
        await actor.stop()

@pytest.mark.asyncio
async def test_cortex_taint_check():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        event_invalid = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.created",
            payload={"value": 42},
            cortex_taint="",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-1"
        )
        
        with pytest.raises(ValueError) as excinfo:
            await actor.append(event_invalid)
        assert "cortex_taint" in str(excinfo.value)

    finally:
        await actor.stop()

@pytest.mark.asyncio
async def test_idempotency_masking_on_integrity_error():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        event = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.created",
            payload={"value": 42},
            cortex_taint="test_masking",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-1"
        )
        res1 = await actor.append(event)

        # Mock the event_id check SELECT query to return None only ONCE
        original_process = actor._process
        
        called = False
        async def mock_process(db, ev, fut):
            original_execute = db.execute
            
            async def mock_execute(sql, *args, **kwargs):
                nonlocal called
                if "SELECT seq, entry_hash FROM ledger_entries WHERE event_id =" in sql and not called:
                    called = True
                    class MockCursor:
                        async def fetchone(self):
                            return None
                    return MockCursor()
                return await original_execute(sql, *args, **kwargs)
                
            db.execute = mock_execute
            await original_process(db, ev, fut)

        actor._process = mock_process

        # This append should trigger IntegrityError but return successfully because of masking (INV_BFT_05)
        res2 = await actor.append(event)
        
        assert res1["seq"] == res2["seq"]
        assert res1["entry_hash"] == res2["entry_hash"]

    finally:
        await actor.stop()

@pytest.mark.asyncio
async def test_zombie_actor_prevention():
    actor = BFTLedgerActor(DB_PATH)
    await actor.start()

    try:
        event = LedgerEvent(
            stream="stream-1",
            entity_id="entity-A",
            event_type="test.created",
            payload={"value": 42},
            cortex_taint="test_zombie",
            source_db="test_db",
            source_table="test_table",
            source_pk="pk-1"
        )
        
        original_process = actor._process
        
        async def mock_process_fail(db, ev, fut):
            original_execute = db.execute
            async def mock_execute(sql, *args, **kwargs):
                if sql == "ROLLBACK":
                    raise sqlite3.Error("Mock Rollback Failure")
                if "INSERT INTO ledger_entries" in sql:
                    raise sqlite3.Error("Mock Insert Failure")
                return await original_execute(sql, *args, **kwargs)
            db.execute = mock_execute
            await original_process(db, ev, fut)

        actor._process = mock_process_fail

        # Append and expect the future to fail
        fut = actor.append(event)
        with pytest.raises(Exception):
            await fut

        # Give the worker loop a brief moment to fail and terminate
        await asyncio.sleep(0.1)

        # Subsequent append must raise RuntimeError due to Zombie Actor Prevention (INV_BFT_07)
        with pytest.raises(RuntimeError) as excinfo:
            actor.append(event)
        assert "Zombie Actor Prevention" in str(excinfo.value)

    finally:
        await actor.stop()
