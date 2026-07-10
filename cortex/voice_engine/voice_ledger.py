import sqlite3
import time
import hashlib
import logging

class VoiceLedger:
    """
    C5-REAL SQLite WAL Mutex Anchor.
    Enforces R10 (Concurrencia Confiable de DB) with busy_timeout=5000.
    """
    def __init__(self, db_path: str = "cortex/voice_engine/voice_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self):
        schema_path = "cortex/voice_engine/voice_ledger.sql"
        try:
            with open(schema_path, "r") as f:
                schema = f.read()
            with self._get_conn() as conn:
                conn.executescript(schema)
                conn.commit()


    def start_session(self) -> str:
        session_id = f"sess_{hashlib.blake2b(str(time.time()).encode()).hexdigest()[:12]}"
        with self._get_conn() as conn:
            conn.execute("INSERT INTO voice_sessions (session_id, termination_reason) VALUES (?, 'NORMAL')", (session_id,))
            conn.commit()
        return session_id

    def log_acoustic_event(self, session_id: str, input_hash: str, tensor_hash: str, pcm_hash: str, ttft_ms: float, ttfaf_ms: float):
        event_id = f"evt_{hashlib.blake2b(str(time.time()).encode()).hexdigest()[:12]}"
        try:
            with self._get_conn() as conn:
                conn.execute('''
                    INSERT INTO acoustic_events 
                    (event_id, session_id, input_hash, tensor_state_hash, output_pcm_hash, ttft_ms, ttfaf_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (event_id, session_id, input_hash, tensor_hash, pcm_hash, ttft_ms, ttfaf_ms))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Apoptosis: Ledger Insertion Failed -> {str(e)}")
            raise
