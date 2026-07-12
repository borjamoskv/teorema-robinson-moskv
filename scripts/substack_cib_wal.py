import sqlite3
import hashlib
import time
import json
from pathlib import Path


class SubstackCIBWALDetector:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path, timeout=5.0) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute(
                "\n                CREATE TABLE IF NOT EXISTS master_ledger (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    action TEXT NOT NULL,\n                    prev_hash TEXT UNIQUE,\n                    current_hash TEXT UNIQUE NOT NULL,\n                    cortex_taint TEXT NOT NULL,\n                    timestamp REAL NOT NULL\n                );\n            "
            )
            conn.execute(
                "\n                CREATE TABLE IF NOT EXISTS cib_nodes (\n                    node_id TEXT PRIMARY KEY,\n                    cortex_taint TEXT NOT NULL\n                );\n            "
            )
            conn.execute(
                "\n                CREATE TABLE IF NOT EXISTS cib_edges (\n                    source TEXT,\n                    target TEXT,\n                    type TEXT,\n                    timestamp REAL,\n                    cortex_taint TEXT NOT NULL,\n                    PRIMARY KEY(source, target, type, timestamp)\n                );\n            "
            )
            conn.execute(
                "\n                CREATE TRIGGER IF NOT EXISTS prevent_ledger_update\n                BEFORE UPDATE ON master_ledger\n                BEGIN SELECT RAISE(ABORT, 'C5-REAL: Master Ledger updates are physically forbidden'); END;\n            "
            )
            conn.execute(
                "\n                CREATE TRIGGER IF NOT EXISTS prevent_ledger_delete\n                BEFORE DELETE ON master_ledger\n                BEGIN SELECT RAISE(ABORT, 'C5-REAL: Master Ledger deletes are physically forbidden'); END;\n            "
            )

    def _append_ledger(self, conn: sqlite3.Connection, action: str) -> str:
        cur = conn.cursor()
        cur.execute("SELECT current_hash FROM master_ledger ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        prev_hash = row[0] if row else "GENESIS"
        timestamp = time.time()
        cortex_taint = f"OSINT-CIB|{timestamp}|borjamoskv"
        current_hash = hashlib.sha256(
            f"{prev_hash}{action}{cortex_taint}".encode()
        ).hexdigest()
        cur.execute(
            "INSERT INTO master_ledger (action, prev_hash, current_hash, cortex_taint, timestamp) VALUES (?, ?, ?, ?, ?)",
            (action, prev_hash, current_hash, cortex_taint, timestamp),
        )
        return current_hash

    def ingest_interaction(
        self, source_node: str, target_node: str, interaction_type: str
    ):
        timestamp = time.time()
        cortex_taint = f"INGEST|{timestamp}|borjamoskv"
        action_log = f"INGEST: {source_node} -> {target_node} [{interaction_type}]"
        with sqlite3.connect(self.db_path, timeout=5.0) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO cib_nodes (node_id, cortex_taint) VALUES (?, ?)",
                (source_node, cortex_taint),
            )
            conn.execute(
                "INSERT OR IGNORE INTO cib_nodes (node_id, cortex_taint) VALUES (?, ?)",
                (target_node, cortex_taint),
            )
            conn.execute(
                "INSERT INTO cib_edges (source, target, type, timestamp, cortex_taint) VALUES (?, ?, ?, ?, ?)",
                (source_node, target_node, interaction_type, timestamp, cortex_taint),
            )
            self._append_ledger(conn, action_log)

    def calculate_roi_dissonance(
        self, node_id: str, estimated_hours_spent: float
    ) -> str:
        with sqlite3.connect(self.db_path, timeout=5.0) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM cib_nodes")
            total_nodes = cur.fetchone()[0]
            avg_value_per_hour = 25.0
            opportunity_cost = estimated_hours_spent * avg_value_per_hour
            subs_gained_from_pod = 0.01 * total_nodes
            verdict = (
                "NEGATIVE_ROI_SERVITUDE"
                if opportunity_cost > subs_gained_from_pod * 50
                else "MARGINAL_VALUE"
            )
            action_log = f"ROI_CALC_DISSONANCE: {node_id} -> {verdict} | COST: ${opportunity_cost} | GAIN: {subs_gained_from_pod} subs"
            hash_val = self._append_ledger(conn, action_log)
            return json.dumps(
                {
                    "node_id": node_id,
                    "opportunity_cost_usd": opportunity_cost,
                    "organic_subs_gained": subs_gained_from_pod,
                    "verdict": verdict,
                    "ledger_hash": hash_val,
                },
                indent=2,
            )


if __name__ == "__main__":
    db_file = str(Path(__file__).parent / "cib_master_ledger.db")
    print(f"[*] Ignición C5-REAL SQLite WAL: {db_file}")
    detector = SubstackCIBWALDetector(db_file)
    detector.ingest_interaction("follower_89", "daviddominguez", "instant_like")
    detector.ingest_interaction("follower_12", "daviddominguez", "generic_comment")
    print("[+] Mutaciones CIB inyectadas en Master Ledger.")
    print("[+] Inyección de disonancia ROI:")
    print(detector.calculate_roi_dissonance("follower_89", 15.0))
