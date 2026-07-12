import re

wrapper = "\ndef _compute_entry_hash_wrapper(event_id, stream, entity_id, event_type, payload_json, source_db, source_table, source_pk, cortex_taint, lamport_t, prev_hash, created_at):\n    return _compute_entry_hash(event_id, stream, entity_id, event_type, payload_json, source_db, source_table, source_pk, cortex_taint, lamport_t, prev_hash, created_at)\n"
new_process = "cursor = await db.execute(\n                '''INSERT INTO ledger_entries (\n                    event_id, stream, entity_id, event_type, payload_json,\n                    source_db, source_table, source_pk, cortex_taint,\n                    lamport_t, prev_hash, entry_hash, created_at\n                ) VALUES (\n                    ?, ?, ?, ?, ?, ?, ?, ?, ?,\n                    COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1,\n                    COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000'),\n                    c5_compute_hash(?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1, COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000'), ?),\n                    ?\n                )\n                ON CONFLICT(event_id) DO NOTHING\n                RETURNING seq, entry_hash''',\n                (\n                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,\n                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,\n                    event_id, event.stream, event.entity_id, event.event_type, stored_payload,\n                    event.source_db, event.source_table, event.source_pk, event.cortex_taint,\n                    created_at, created_at\n                )\n            )\n            db_row = await cursor.fetchone()\n            if db_row is None:\n                # Idempotencia: el event_id ya existe, colisión pacífica resuelta en DB.\n                cursor = await db.execute(\"SELECT seq, entry_hash FROM ledger_entries WHERE event_id = ?\", (event_id,))\n                db_row = await cursor.fetchone()\n                if db_row is None:\n                    raise RuntimeError(\"Insertion failed: event_id not persisted and not found\")"


def refactor(filename, class_name) -> "Any":
    with open(filename, "r") as f:
        content = f.read()
    if "_compute_entry_hash_wrapper" not in content:
        content = content.replace(
            f"class {class_name}:", wrapper + f"\nclass {class_name}:"
        )
    if "c5_compute_hash" not in content:
        content = content.replace(
            "async with aiosqlite.connect(self._db_path) as db:\n",
            'async with aiosqlite.connect(self._db_path) as db:\n            await db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)\n',
        )
    process_match = re.search(
        'cur = await db\\.execute\\("SELECT lamport_t.*?raise RuntimeError\\("Insertion failed: event_id not persisted and not found"\\)',
        content,
        re.DOTALL,
    )
    if process_match:
        content = content.replace(process_match.group(0), new_process)
    with open(filename, "w") as f:
        f.write(content)


refactor("bft/ledger_actor.py", "BFTLedgerActor")
refactor("core/master_ledger.py", "BFTLedgerActor")
