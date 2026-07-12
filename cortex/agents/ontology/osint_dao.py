"""
C5-REAL OSINT Ontology Data Access Object
Enforces [INV_BFT_02] Asynchronous I/O Lock via aiosqlite.
Fail-fast: Crash over catch [L12: Κ1].
"""

import asyncio
import aiosqlite
from pathlib import Path
from typing import List, Dict, Any

# Repo-relative: el .db vive junto a este módulo. Antes hardcodeado a
# /30_BABYLON-60/... → en otro checkout aiosqlite abría un DB vacío y las
# queries fallaban con "no such table". Path portable derivado de __file__.
DB_PATH: str = str(Path(__file__).resolve().parent / "osint_primitives.db")

class OSINTOntologyAccessor:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path

    async def get_primitives_by_domain(self, domain_name: str) -> List[Dict[str, Any]]:
        """
        Extracción asíncrona de primitivas limitadas por vector termodinámico.
        [MUTEX_HALTING_BOUND] N=120 limit applied at DB layer.
        """
        query: str = '''
            SELECT p.id, p.name, p.description 
            FROM primitive p
            JOIN domain d ON p.domain_id = d.id
            WHERE d.name LIKE ?
            LIMIT 120
        '''
        async with aiosqlite.connect(self.db_path) as db:
            db.text_factory = str
            # Enforce L2 thermodynamic bounds on connection
            await db.execute("PRAGMA busy_timeout=5000")
            await db.execute("PRAGMA journal_mode=WAL")
            
            async with db.execute(query, (f"%{domain_name}%",)) as cursor:
                rows = await cursor.fetchall()
                if not rows:
                    raise RuntimeError(f"Dominio OSINT no encontrado o vacío: {domain_name}")
                return [{"id": r[0], "name": r[1], "description": r[2]} for r in rows]

    async def get_all_invariants(self) -> List[Dict[str, str]]:
        """Recupera invariantes estructurales para inyección en System Prompt."""
        query: str = 'SELECT code, description FROM invariant'
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA busy_timeout=5000")
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [{"code": r[0], "description": r[1]} for r in rows]

if __name__ == "__main__":
    async def run_audit() -> None:
        accessor = OSINTOntologyAccessor()
        invariants = await accessor.get_all_invariants()
        print(f"Loaded {len(invariants)} invariants.")
        primitives = await accessor.get_primitives_by_domain("SOCINT")
        print(f"Loaded {len(primitives)} SOCINT primitives. First: {primitives[0]['name']}")
    
    asyncio.run(run_audit())
