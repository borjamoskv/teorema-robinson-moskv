import sqlite3
import hashlib
import time

def log_leak():
    db_path = "/Users/borjafernandezangulo/30_BABYLON-60/nexus_anchors.db"
    
    # Asegurar que la tabla exista (modo WAL se asume configurado)
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS causal_collapse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                event_type TEXT,
                payload_hash TEXT,
                status TEXT,
                cortex_taint TEXT
            )
        ''')
        
        payload = "LEAK_RULE_300_BYTEDANCE_TTFT_2.9MS"
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        cortex_taint = "EXERGY_POSTHOC_INVARIANT_L71"
        
        conn.execute('''
            INSERT INTO causal_collapse (timestamp, event_type, payload_hash, status, cortex_taint)
            VALUES (?, ?, ?, ?, ?)
        ''', (int(time.time()), 'LEAK_ASSIMILATION', payload_hash, 'AWAITING_PAYLOAD', cortex_taint))
        
        conn.commit()
        
    print(f"Leak registrado en Master Ledger (WAL). Hash: {payload_hash}")

if __name__ == "__main__":
    log_leak()
