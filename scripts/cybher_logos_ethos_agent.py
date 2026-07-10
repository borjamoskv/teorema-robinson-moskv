#!/usr/bin/env python3
"""
C5-REAL: Autonomous Hypervigilant LOGOS ETHOS Cybher Agent
Author: Borja Moskv (borjamoskv)
[P0 ULTRATHINK] EXERGY-MAXIMIZER MUTATION: 100x CYCLE COMPRESSION
"""

import os
import hashlib
import sqlite3
import asyncio

EXCLUDE_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.ruff_cache', '.pytest_cache'}

class CybherHypervigilantAgent:
    def __init__(self, target_dir: str, db_path: str):
        self.target_dir = os.path.abspath(os.path.expanduser(target_dir))
        self.db_path = os.path.abspath(os.path.expanduser(db_path))
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, timeout=5000)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA temp_store=MEMORY")
        self._init_db()
        
        self.state_cache = {}
        self.write_queue = asyncio.Queue()
        self.lamport_t = self._get_max_lamport()
        self.prev_hash = f"GENESIS_{self.lamport_t}"

    def _init_db(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS ethos_ledger (
                lamport_t INTEGER PRIMARY KEY,
                agent_id TEXT,
                file_path TEXT,
                prev_hash TEXT UNIQUE,
                payload_hash TEXT,
                cortex_taint TEXT
            )
        ''')
        self.conn.commit()

    def _get_max_lamport(self):
        cursor = self.conn.execute("SELECT MAX(lamport_t) FROM ethos_ledger")
        row = cursor.fetchone()
        return row[0] or 0

    def _hash_payload(self, path: str) -> str:
        h = hashlib.blake2b()
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    async def _sqlite_writer_daemon(self):
        batch = []
        while True:
            task = await self.write_queue.get()
            if task is None:
                if batch:
                    self._flush_batch(batch)
                break
            
            batch.append(task)
            self.write_queue.task_done()
            
            if len(batch) >= 2000 or self.write_queue.empty():
                self._flush_batch(batch)
                batch.clear()

    def _flush_batch(self, batch):
        try:
            self.conn.executemany('''
                INSERT INTO ethos_ledger (lamport_t, agent_id, file_path, prev_hash, payload_hash, cortex_taint)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', batch)
            self.conn.commit()
        except sqlite3.IntegrityError:
            print("[!] SIGKILL_State_Purge: IntegrityError BFT_STATE_LOOP.")
            os._exit(1)

    def _fast_scandir(self, path):
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name not in EXCLUDE_DIRS and not entry.name.startswith('.'):
                            yield from self._fast_scandir(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        if not entry.name.startswith('.') and not entry.name.endswith('.db'):
                            yield entry.path, entry.stat().st_mtime
        except PermissionError:
            pass

    async def bft_state_loop(self):
        agent_id = "CYBHER_UID1"
        writer_task = asyncio.create_task(self._sqlite_writer_daemon())
        
        try:
            while True:
                if not os.path.exists(self.target_dir):
                    os._exit(1)

                for filepath, current_mtime in self._fast_scandir(self.target_dir):
                    if self.state_cache.get(filepath) != current_mtime:
                        try:
                            payload_hash = self._hash_payload(filepath)
                            self.lamport_t += 1
                            cortex_taint = f"LOGOS-C5::ETHOS::{payload_hash[:8]}"
                            
                            await self.write_queue.put((
                                self.lamport_t, 
                                agent_id, 
                                filepath, 
                                self.prev_hash, 
                                payload_hash, 
                                cortex_taint
                            ))
                            
                            self.state_cache[filepath] = current_mtime
                            self.prev_hash = payload_hash
                            # Silent execution -> Zero Green Theater
                        except OSError:
                            pass

                await asyncio.sleep(2.0)
        finally:
            await self.write_queue.put(None)
            await writer_task

async def main():
    agent = CybherHypervigilantAgent("~/30_BABYLON-60", "~/.babylon60/cybher_nexus.db")
    await agent.bft_state_loop()

if __name__ == "__main__":
    asyncio.run(main())
