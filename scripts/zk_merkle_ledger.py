import os
import sqlite3
import hashlib
import json
import time
import asyncio
DB_PATH = '$CORTEX_ROOT/.babylon60/zk_ledger.db'

class ZKMerkleLedgerDaemon:

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, timeout=5.0)
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.conn.execute('PRAGMA synchronous=NORMAL;')
        self._init_schema()
        self.write_queue = asyncio.Queue()

    def _init_schema(self):
        self.conn.execute('\n            CREATE TABLE IF NOT EXISTS causal_chain (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                payload TEXT NOT NULL,\n                cortex_taint TEXT NOT NULL,\n                prev_hash TEXT NOT NULL,\n                merkle_root TEXT NOT NULL UNIQUE\n            );\n        ')
        self.conn.execute("\n            CREATE TRIGGER IF NOT EXISTS trigger_abort_update\n            BEFORE UPDATE ON causal_chain\n            BEGIN\n                SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Mutación prohibida en Merkle Ledger.');\n            END;\n        ")
        self.conn.execute("\n            CREATE TRIGGER IF NOT EXISTS trigger_abort_delete\n            BEFORE DELETE ON causal_chain\n            BEGIN\n                SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Eliminación prohibida en Merkle Ledger.');\n            END;\n        ")
        self.conn.execute("\n            CREATE TRIGGER IF NOT EXISTS trigger_validate_chain\n            BEFORE INSERT ON causal_chain\n            FOR EACH ROW\n            WHEN NEW.id > 1 AND NEW.prev_hash != (SELECT merkle_root FROM causal_chain WHERE id = NEW.id - 1)\n            BEGIN\n                SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Fractura topológica detectada. prev_hash no coincide con la raíz anterior.');\n            END;\n        ")
        self.conn.commit()

    def _hash_data(self, data: str) -> str:
        h = hashlib.blake2s()
        h.update(data.encode('utf-8'))
        return h.hexdigest()

    def _sync_insert(self, payload_dict: dict, caller_id: str):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, merkle_root FROM causal_chain ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        prev_hash = row[1] if row else 'GENESIS_BLOCK_0000000000000000'
        payload_str = json.dumps(payload_dict, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        cortex_taint = f'PID:{os.getpid()}|TIME:{time.time()}|CALLER:{caller_id}'
        merkle_root = self._hash_data(prev_hash + payload_str + cortex_taint)
        try:
            cursor.execute('INSERT INTO causal_chain (payload, cortex_taint, prev_hash, merkle_root) VALUES (?, ?, ?, ?)', (payload_str, cortex_taint, prev_hash, merkle_root))
            self.conn.commit()
            return merkle_root
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise RuntimeError(f'C5-REAL SIGKILL: Fallo Causal Físico. {e}')

    async def enqueue_mutation(self, payload_dict: dict, caller_id: str):
        future = asyncio.get_running_loop().create_future()
        await self.write_queue.put((payload_dict, caller_id, future))
        return await future

    async def writer_daemon_loop(self):
        while True:
            payload_dict, caller_id, future = await self.write_queue.get()
            try:
                merkle_root = self._sync_insert(payload_dict, caller_id)
                future.set_result(merkle_root)
            except RuntimeError as e:
                future.set_exception(e)
            finally:
                self.write_queue.task_done()

    def close(self):
        self.conn.close()

async def run_stress_test():
    daemon = ZKMerkleLedgerDaemon()
    daemon_task = asyncio.create_task(daemon.writer_daemon_loop())
    print('Iniciando inyección concurrente asíncrona (O(1) Fricción)...')
    tasks = []
    for i in range(1, 6):
        caller_id = f'AGENT_THREAD_{i}'
        tasks.append(daemon.enqueue_mutation({'AST_delta': f'mut_node_{i}'}, caller_id))
    roots = await asyncio.gather(*tasks)
    for i, root in enumerate(roots, 1):
        print(f'Bloque {i} colapsado asíncronamente. Taint Inyectado. Root: {root}')
    daemon_task.cancel()
    daemon.close()
if __name__ == '__main__':
    asyncio.run(run_stress_test())
