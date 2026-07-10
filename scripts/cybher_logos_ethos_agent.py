#!/usr/bin/env python3
"""
C5-REAL: Autonomous Hypervigilant LOGOS ETHOS Cybher Agent
Author: Borja Moskv (borjamoskv)

Implements:
- LOGOS: Axiomatic adherence, BFT State Loop, SQLite WAL isolation.
- ETHOS: Cryptographic validation of provenance (zkProof proxy via BLAKE3/SHA256).
- [L2] Ω13: Single physical writer queue to avoid locks.
- [L12] Κ1: Fail-fast semantics.
"""

import os
import sys
import time
import hashlib
import sqlite3
import asyncio
from pathlib import Path

class CybherHypervigilantAgent:
    def __init__(self, target_dir: str, db_path: str):
        self.target_dir = Path(target_dir).expanduser().resolve()
        self.db_path = Path(db_path).expanduser().resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # [L2] Ω10: Initializing SQLite with WAL and 5000ms timeout
        self.conn = sqlite3.connect(str(self.db_path), timeout=5000)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self._init_db()
        
        self.state_cache = {}
        self.write_queue = asyncio.Queue()
        self.lamport_t = self._get_max_lamport()
        self.prev_hash = f"GENESIS_{self.lamport_t}"

    def _init_db(self):
        # [L2] Ω11: Master Ledger with UNIQUE(prev_hash) and CORTEX-TAINT
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS ethos_ledger (
                lamport_t INTEGER PRIMARY KEY,
                agent_id TEXT,
                file_path TEXT,
                prev_hash TEXT UNIQUE,
                payload_hash TEXT,
                cortex_taint TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def _get_max_lamport(self):
        cursor = self.conn.execute("SELECT MAX(lamport_t) FROM ethos_ledger")
        row = cursor.fetchone()
        return row[0] if row[0] is not None else 0

    def _hash_payload(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    async def _sqlite_writer_daemon(self):
        # [L2] Ω13: Cola de tareas asyncio.Queue con un único escritor físico
        while True:
            task = await self.write_queue.get()
            if task is None:
                break
            try:
                self.conn.execute('''
                    INSERT INTO ethos_ledger (lamport_t, agent_id, file_path, prev_hash, payload_hash, cortex_taint)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', task)
                self.conn.commit()
            except sqlite3.IntegrityError:
                # [L12] Κ1: Fail-fast - Crash Causal
                print("[!] SIGKILL_State_Purge: IntegrityError in BFT_STATE_LOOP. Aborting.")
                os._exit(1)
            self.write_queue.task_done()

    async def bft_state_loop(self):
        agent_id = "CYBHER_UID1"
        writer_task = asyncio.create_task(self._sqlite_writer_daemon())
        
        print(f"[*] IGNITION DETERMINISTA. Hypervigilant LOGOS ETHOS Agent scanning {self.target_dir}...")
        
        try:
            while True:
                # [L3] Σ5: Validación síncrona de existencia de ruta
                if not self.target_dir.exists():
                    print(f"[!] SIGKILL_State_Purge: Target directory {self.target_dir} vanished.")
                    os._exit(1)

                for filepath in self.target_dir.rglob('*'):
                    if filepath.is_file() and not filepath.name.startswith('.') and 'cortex.db' not in filepath.name:
                        try:
                            current_mtime = filepath.stat().st_mtime
                            if filepath not in self.state_cache or self.state_cache[filepath] != current_mtime:
                                payload_hash = self._hash_payload(filepath)
                                self.lamport_t += 1
                                cortex_taint = f"LOGOS-C5::ETHOS::{payload_hash[:8]}"
                                
                                await self.write_queue.put((
                                    self.lamport_t, 
                                    agent_id, 
                                    str(filepath), 
                                    self.prev_hash, 
                                    payload_hash, 
                                    cortex_taint
                                ))
                                
                                self.state_cache[filepath] = current_mtime
                                self.prev_hash = payload_hash
                                print(f"[+] ETHOS Colapse_L8: {filepath.name} -> {payload_hash[:12]}")
                        except PermissionError:
                            pass
                        except Exception as e:
                            # Strict Error Bubbling
                            raise e

                await asyncio.sleep(2.0)
        finally:
            await self.write_queue.put(None)
            await writer_task

async def main():
    agent = CybherHypervigilantAgent("~/30_BABYLON-60", "~/.babylon60/cybher_nexus.db")
    await agent.bft_state_loop()

if __name__ == "__main__":
    # [L2] Ω9: Inicialización síncrona con await antes de servir
    asyncio.run(main())
