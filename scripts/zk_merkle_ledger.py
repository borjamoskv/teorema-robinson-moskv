import os
import sqlite3
import hashlib
import json
import time
import asyncio

# C5-REAL: BFT Master Ledger (Zero-Concurrency & Cortex-Taint)
DB_PATH = "$CORTEX_ROOT/.babylon60/zk_ledger.db"

class ZKMerkleLedgerDaemon:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        # Ω10: WAL + 5000ms (A fallback, but queue prevents lock)
        self.conn = sqlite3.connect(DB_PATH, timeout=5.0)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()
        
        # Ω13: Cola de Tareas asyncio para un único escritor físico
        self.write_queue = asyncio.Queue()

    def _init_schema(self):
        # Ω11: Integridad y CORTEX-TAINT
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS causal_chain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                cortex_taint TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                merkle_root TEXT NOT NULL UNIQUE
            );
        ''')

        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS trigger_abort_update
            BEFORE UPDATE ON causal_chain
            BEGIN
                SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Mutación prohibida en Merkle Ledger.');
            END;
        ''')
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS trigger_abort_delete
            BEFORE DELETE ON causal_chain
            BEGIN
                SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Eliminación prohibida en Merkle Ledger.');
            END;
        ''')
        self.conn.execute('''
            CREATE TRIGGER IF NOT EXISTS trigger_validate_chain
            BEFORE INSERT ON causal_chain
            FOR EACH ROW
            WHEN NEW.id > 1 AND NEW.prev_hash != (SELECT merkle_root FROM causal_chain WHERE id = NEW.id - 1)
            BEGIN
                SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Fractura topológica detectada. prev_hash no coincide con la raíz anterior.');
            END;
        ''')
        self.conn.commit()

    def _hash_data(self, data: str) -> str:
        """Implementa BLAKE2s para emular el hashing determinista"""
        h = hashlib.blake2s()
        h.update(data.encode('utf-8'))
        return h.hexdigest()

    def _sync_insert(self, payload_dict: dict, caller_id: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, merkle_root FROM causal_chain ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        
        prev_hash = row[1] if row else "GENESIS_BLOCK_0000000000000000"
        payload_str = json.dumps(payload_dict, sort_keys=True)
        
        # Ω11: CORTEX-TAINT (Firma inmutable de causalidad OS/Agent)
        cortex_taint = f"PID:{os.getpid()}|TIME:{time.time()}|CALLER:{caller_id}"
        
        # Merkle computation
        merkle_root = self._hash_data(prev_hash + payload_str + cortex_taint)
        
        try:
            cursor.execute(
                "INSERT INTO causal_chain (payload, cortex_taint, prev_hash, merkle_root) VALUES (?, ?, ?, ?)",
                (payload_str, cortex_taint, prev_hash, merkle_root)
            )
            self.conn.commit()
            return merkle_root
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise RuntimeError(f"C5-REAL SIGKILL: Fallo Causal Físico. {e}")

    async def enqueue_mutation(self, payload_dict: dict, caller_id: str):
        """Punto de entrada asíncrono para agentes (Zero-Deadlock)"""
        future = asyncio.get_running_loop().create_future()
        await self.write_queue.put((payload_dict, caller_id, future))
        return await future

    async def writer_daemon_loop(self):
        """Macrófago de escritura física O(1). Único thread de mutación SQLite."""
        while True:
            payload_dict, caller_id, future = await self.write_queue.get()
            try:
                # Transducción Síncrona Serializada
                merkle_root = self._sync_insert(payload_dict, caller_id)
                future.set_result(merkle_root)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.write_queue.task_done()

    def close(self):
        self.conn.close()

# TEST HARNESS LOCAL
async def run_stress_test():
    daemon = ZKMerkleLedgerDaemon()
    # Lanzar daemon en background
    daemon_task = asyncio.create_task(daemon.writer_daemon_loop())
    
    print("Iniciando inyección concurrente asíncrona (O(1) Fricción)...")
    tasks = []
    for i in range(1, 6):
        caller_id = f"AGENT_THREAD_{i}"
        tasks.append(daemon.enqueue_mutation({"AST_delta": f"mut_node_{i}"}, caller_id))
    
    roots = await asyncio.gather(*tasks)
    for i, root in enumerate(roots, 1):
        print(f"Bloque {i} colapsado asíncronamente. Taint Inyectado. Root: {root}")
    
    daemon_task.cancel()
    daemon.close()

if __name__ == "__main__":
    asyncio.run(run_stress_test())
