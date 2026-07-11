import sqlite3
import hashlib
import time

db_path = "/Users/borjafernandezangulo/30_BABYLON-60/ultrathink_ledger.db"
conn = sqlite3.connect(db_path, isolation_level=None)
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("CREATE TABLE IF NOT EXISTS executions (id INTEGER PRIMARY KEY, hash TEXT, entropy REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")

payload = b"ULTRATHINK_ENTROPY_PURGE_BBKLIVE"
h = hashlib.sha256(payload).hexdigest()

# Entropy value representation of the conversational noise purged
conn.execute("INSERT INTO executions (hash, entropy) VALUES (?, ?)", (h, 4.2))
conn.close()
