import re

with open("bft/ledger_actor.py", "r") as f:
    la = f.read()
wrapper = "\ndef _compute_entry_hash_wrapper(event_id, stream, entity_id, event_type, payload_json, source_db, source_table, source_pk, cortex_taint, lamport_t, prev_hash, created_at):\n    return _compute_entry_hash(event_id, stream, entity_id, event_type, payload_json, source_db, source_table, source_pk, cortex_taint, lamport_t, prev_hash, created_at)\n"
if "_compute_entry_hash_wrapper" not in la:
    la = la.replace("class BFTLedgerActor:", wrapper + "\nclass BFTLedgerActor:")
worker_regex = "(async def _worker\\(self\\) -> None:.*?async with aiosqlite\\.connect\\(self\\._db_path\\) as db:\\n)(.*?)"
worker_inject = '\\1            await db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)\\n\\2'
if "c5_compute_hash" not in la:
    la = la.replace(
        "async with aiosqlite.connect(self._db_path) as db:\n",
        'async with aiosqlite.connect(self._db_path) as db:\n            await db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)\n',
    )
process_match = re.search(
    'cur = await db\\.execute\\("SELECT lamport_t.*?db_row = await cursor\\.fetchone\\(\\)',
    la,
    re.DOTALL,
)
if process_match:
    new_process = "cursor = await db.execute(\n                '''INSERT INTO ledger_entries (\n                    event_id, stream, entity_id, event_type, payload_json,\n                    source_db, source_table, source_pk, cortex_taint,\n                    lamport_t, prev_hash, entry_hash, created_at\n                ) \n                SELECT \n                    ?, ?, ?, ?, ?, ?, ?, ?, ?,\n                    COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1 AS new_lamport,\n                    COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000') AS prev_hash,\n                    c5_compute_hash(?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1, COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000'), ?) AS entry_hash,\n                    ?\n                WHERE NOT EXISTS (SELECT 1 FROM ledger_entries WHERE event_id = ?)\n                RETURNING seq, entry_hash''',\n                (\n                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,\n                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,\n                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,\n                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,\n                    created_at, created_at, event_id\n                )\n            )\n            db_row = await cursor.fetchone()"
    la = la.replace(process_match.group(0), new_process)
with open("bft/ledger_actor.py", "w") as f:
    f.write(la)
print("Refactored ledger_actor.py")
with open("core/master_ledger.py", "r") as f:
    ml = f.read()
if "_compute_entry_hash_wrapper" not in ml:
    ml = ml.replace("class MasterLedger:", wrapper + "\nclass MasterLedger:")
if "c5_compute_hash" not in ml:
    ml = ml.replace(
        "async with aiosqlite.connect(self._db_path) as db:\n",
        'async with aiosqlite.connect(self._db_path) as db:\n            await db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)\n',
    )
process_match_ml = re.search(
    'cur = await db\\.execute\\("SELECT lamport_t.*?db_row = await cursor\\.fetchone\\(\\)',
    ml,
    re.DOTALL,
)
if process_match_ml:
    ml = ml.replace(process_match_ml.group(0), new_process)
with open("core/master_ledger.py", "w") as f:
    f.write(ml)
print("Refactored master_ledger.py")
