import sys

def refactor(filename, class_name):
    with open(filename, "r") as f:
        content = f.read()

    wrapper = """
def _compute_entry_hash_wrapper(event_id, stream, entity_id, event_type, payload_json, source_db, source_table, source_pk, cortex_taint, lamport_t, prev_hash, created_at):
    return _compute_entry_hash(event_id, stream, entity_id, event_type, payload_json, source_db, source_table, source_pk, cortex_taint, lamport_t, prev_hash, created_at)
"""

    if "_compute_entry_hash_wrapper" not in content:
        content = content.replace(f"class {class_name}:", wrapper + f"\nclass {class_name}:")

    # Add create_function
    if "c5_compute_hash" not in content:
        content = content.replace(
            'async with aiosqlite.connect(self._db_path) as db:\n',
            'async with aiosqlite.connect(self._db_path) as db:\n            await db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)\n'
        )

    # 1. Remove the SELECT block
    select_str_actor = """            cur = await db.execute("SELECT lamport_t, entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1")
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

"""
    if select_str_actor in content:
        content = content.replace(select_str_actor, "")
    else:
        print(f"Could not find select_str in {filename}")

    # 2. Replace the INSERT block
    insert_str_actor = """            cursor = await db.execute(
                \"\"\"INSERT INTO ledger_entries (
                    event_id, stream, entity_id, event_type, payload_json,
                    source_db, source_table, source_pk, cortex_taint,
                    lamport_t, prev_hash, entry_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO NOTHING
                RETURNING seq, entry_hash\"\"\",
                (
                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,
                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,
                    lamport_t, prev_hash, entry_hash, created_at
                )
            )"""

    new_insert = """            cursor = await db.execute(
                \"\"\"INSERT INTO ledger_entries (
                    event_id, stream, entity_id, event_type, payload_json,
                    source_db, source_table, source_pk, cortex_taint,
                    lamport_t, prev_hash, entry_hash, created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1,
                    COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000'),
                    c5_compute_hash(?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1, COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000'), ?),
                    ?
                )
                ON CONFLICT(event_id) DO NOTHING
                RETURNING seq, entry_hash\"\"\",
                (
                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,
                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,
                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,
                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,
                    created_at, created_at
                )
            )"""

    if insert_str_actor in content:
        content = content.replace(insert_str_actor, new_insert)
    else:
        print(f"Could not find insert_str in {filename}")
        
    with open(filename, "w") as f:
        f.write(content)

refactor("bft/ledger_actor.py", "BFTLedgerActor")
refactor("core/master_ledger.py", "BFTLedgerActor")
