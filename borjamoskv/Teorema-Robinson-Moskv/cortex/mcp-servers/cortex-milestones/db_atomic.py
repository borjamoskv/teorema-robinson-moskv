import sqlite3
import os
import contextlib

DB_PATH = os.path.join(os.path.dirname(__file__), "cortex_milestones.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

@contextlib.contextmanager
def get_db_connection():
    # Force timeout to 5000ms for concurrent access (TOCTOU mitigation)
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        # Atomic Pragma execution
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA foreign_keys=ON;")
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_db_connection() as conn:
        with open(SCHEMA_PATH, 'r') as f:
            schema = f.read()
        conn.executescript(schema)

if __name__ == "__main__":
    init_db()
