import asyncio
import aiosqlite
import hashlib
import time
import sys
import random
import os
import math
import collections
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXERGY_DB = os.path.join(script_dir, 'nexus_anchors.db')

class ApoptosisException(Exception):
    pass

class UltraThinkBudgetForcer:

    def __init__(self, max_iterations=120, max_tokens=10000):
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.iterations = 0

    def tick(self, tokens=0):
        self.current_tokens += tokens
        self.iterations += 1
        if self.iterations > self.max_iterations or self.current_tokens > self.max_tokens:
            raise ApoptosisException('Thermodynamic limits exceeded (Anergy Overflow).')

def calculate_shannon_entropy_bytes(data: bytes) -> float:
    if not data:
        return 0.0
    len_data = len(data)
    frequencies = collections.Counter(data)
    entropy = 0.0
    for count in frequencies.values():
        p = count / len_data
        entropy -= p * math.log2(p)
    return entropy

async def legion_mcts_worker(worker_id: str, cycles: int=125):
    print(f'🧬 [LEGION] Worker {worker_id} iniciando {cycles} ciclos de Exergy Físico...')
    t_start = time.perf_counter()
    budget_forcer = UltraThinkBudgetForcer(max_iterations=120, max_tokens=10000)
    async with aiosqlite.connect(EXERGY_DB, timeout=10000) as db:
        await db.execute('PRAGMA journal_mode=WAL;')
        await db.execute('CREATE TABLE IF NOT EXISTS executions (id INTEGER PRIMARY KEY, hash TEXT, entropy REAL, cortex_taint TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
        try:
            db_rows = []
            for cycle in range(1, cycles + 1):
                budget_forcer.tick(tokens=50)
                seed_data = f'legion_mcts_{worker_id}_{cycle}_{time.time_ns()}'.encode()
                state_hash = hashlib.blake2b(seed_data).hexdigest()
                entropy = calculate_shannon_entropy_bytes(seed_data)
                session_id = os.environ.get('GEMINI_SESSION_ID', 'local-session')
                timestamp_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                cortex_taint = f'taint:LEGION_{worker_id}:{session_id}:{timestamp_iso}:{state_hash[:32]}'
                db_rows.append((state_hash, entropy, cortex_taint))
                if cycle % 10 == 0:
                    await asyncio.sleep(0.0001)
            await db.executemany('INSERT INTO executions (hash, entropy, cortex_taint, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)', db_rows)
            await db.commit()
        except ApoptosisException as e:
            print(f'🛑 [SIGKILL_STATE_PURGE] {e}')
            await db.rollback()
    t_end = time.perf_counter()
    print(f'✅ [LEGION] Worker {worker_id} colapsó {min(cycles, 120)} ciclos en {(t_end - t_start) * 1000:.2f}ms.')
if __name__ == '__main__':
    worker_id = sys.argv[1] if len(sys.argv) > 1 else 'ALPHA'
    cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 125
    asyncio.run(legion_mcts_worker(worker_id, cycles))
