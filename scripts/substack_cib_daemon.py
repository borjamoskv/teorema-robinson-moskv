import sqlite3
import hashlib
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, Any

class CIBMasterLedgerDaemon:

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.write_queue: asyncio.Queue = asyncio.Queue()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path, timeout=5.0) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('PRAGMA synchronous=NORMAL;')
            conn.execute('\n                CREATE TABLE IF NOT EXISTS master_ledger (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    action TEXT NOT NULL,\n                    prev_hash TEXT UNIQUE,\n                    current_hash TEXT UNIQUE NOT NULL,\n                    cortex_taint TEXT NOT NULL,\n                    timestamp REAL NOT NULL\n                );\n            ')
            conn.execute('\n                CREATE TABLE IF NOT EXISTS cib_nodes (\n                    node_id TEXT PRIMARY KEY,\n                    cortex_taint TEXT NOT NULL\n                );\n            ')
            conn.execute('\n                CREATE TABLE IF NOT EXISTS cib_edges (\n                    source TEXT,\n                    target TEXT,\n                    type TEXT,\n                    timestamp REAL,\n                    cortex_taint TEXT NOT NULL,\n                    PRIMARY KEY(source, target, type, timestamp)\n                );\n            ')
            conn.execute('DROP TRIGGER IF EXISTS prevent_ledger_update;')
            conn.execute("\n                CREATE TRIGGER prevent_ledger_update\n                BEFORE UPDATE ON master_ledger\n                BEGIN SELECT RAISE(ABORT, 'C5-REAL: Master Ledger updates forbidden'); END;\n            ")
            conn.execute('DROP TRIGGER IF EXISTS prevent_ledger_delete;')
            conn.execute("\n                CREATE TRIGGER prevent_ledger_delete\n                BEFORE DELETE ON master_ledger\n                BEGIN SELECT RAISE(ABORT, 'C5-REAL: Master Ledger deletes forbidden'); END;\n            ")

    async def _physical_writer_loop(self):
        print('[*] Daemon C5-REAL Writer Loop: ACTIVO')
        try:
            with sqlite3.connect(self.db_path, timeout=5.0, isolation_level='IMMEDIATE') as conn:
                while True:
                    task = await self.write_queue.get()
                    if task is None:
                        break
                    action_type = task.get('action_type')
                    payload = task.get('payload')
                    timestamp = time.time()
                    cortex_taint = f'OSINT-ASYNC|{timestamp}|borjamoskv'
                    cur = conn.cursor()
                    if action_type == 'INGEST':
                        src, tgt, itype = (payload['source'], payload['target'], payload['type'])
                        cur.execute('INSERT OR IGNORE INTO cib_nodes (node_id, cortex_taint) VALUES (?, ?)', (src, cortex_taint))
                        cur.execute('INSERT OR IGNORE INTO cib_nodes (node_id, cortex_taint) VALUES (?, ?)', (tgt, cortex_taint))
                        cur.execute('INSERT INTO cib_edges (source, target, type, timestamp, cortex_taint) VALUES (?, ?, ?, ?, ?)', (src, tgt, itype, timestamp, cortex_taint))
                        log_action = f'INGEST: {src} -> {tgt} [{itype}]'
                    elif action_type == 'ROI_CALC':
                        log_action = payload['log']
                    else:
                        self.write_queue.task_done()
                        continue
                    cur.execute('SELECT current_hash FROM master_ledger ORDER BY id DESC LIMIT 1')
                    row = cur.fetchone()
                    prev_hash = row[0] if row else 'GENESIS'
                    current_hash = hashlib.sha256(f'{prev_hash}{log_action}{cortex_taint}'.encode()).hexdigest()
                    cur.execute('INSERT INTO master_ledger (action, prev_hash, current_hash, cortex_taint, timestamp) VALUES (?, ?, ?, ?, ?)', (log_action, prev_hash, current_hash, cortex_taint, timestamp))
                    conn.commit()
                    self.write_queue.task_done()
        except asyncio.CancelledError:
            print('[!] Daemon Writer Cancelled')

    async def ingest_interaction(self, source_node: str, target_node: str, interaction_type: str):
        await self.write_queue.put({'action_type': 'INGEST', 'payload': {'source': source_node, 'target': target_node, 'type': interaction_type}})

    async def calculate_roi_dissonance(self, node_id: str, estimated_hours_spent: float) -> str:
        with sqlite3.connect(self.db_path, timeout=5.0) as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM cib_nodes')
            total_nodes = cur.fetchone()[0]
        avg_value_per_hour = 25.0
        opportunity_cost = estimated_hours_spent * avg_value_per_hour
        subs_gained_from_pod = 0.01 * total_nodes
        verdict = 'NEGATIVE_ROI_SERVITUDE' if opportunity_cost > subs_gained_from_pod * 50 else 'MARGINAL_VALUE'
        log_msg = f'ROI_CALC_DISSONANCE: {node_id} -> {verdict} | COST: ${opportunity_cost} | GAIN: {subs_gained_from_pod} subs'
        await self.write_queue.put({'action_type': 'ROI_CALC', 'payload': {'log': log_msg}})
        return json.dumps({'node_id': node_id, 'opportunity_cost_usd': opportunity_cost, 'organic_subs_gained': subs_gained_from_pod, 'verdict': verdict, 'daemon_queued': True}, indent=2)

async def main():
    db_file = str(Path(__file__).parent / 'cib_async_ledger.db')
    daemon = CIBMasterLedgerDaemon(db_file)
    writer_task = asyncio.create_task(daemon._physical_writer_loop())
    print('[*] Inyectando interacciones CIB concurrentes (Ouroboros Phase 3)...')
    res = await daemon.calculate_roi_dissonance('follower_01', 30.0)
    print('\n[+] Disonancia ROI (Queue Asíncrona):')
    print(res)
    await asyncio.gather(daemon.ingest_interaction('follower_01', 'daviddominguez', 'instant_like'), daemon.ingest_interaction('follower_02', 'daviddominguez', 'generic_comment'), daemon.ingest_interaction('daviddominguez', 'follower_01', 'cross_restack'), daemon.ingest_interaction('follower_03', 'daviddominguez', 'bot_like'))
    await daemon.write_queue.join()
    await daemon.write_queue.put(None)
    await writer_task
    print('\n[+] Colapso de Grafo Asíncrono completado. Zero Deadlocks Termodinámicos.')
if __name__ == '__main__':
    asyncio.run(main())
