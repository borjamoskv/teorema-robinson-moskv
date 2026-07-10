import sqlite3
import os
import hashlib
import time

DB_DIR = os.path.expanduser("~/.babylon60")
DB_PATH = os.path.join(DB_DIR, "master_ledger_bft.db")
AGENT_ID = "FRONTIER_REVENG_OMEGA_v1.0.0"

os.makedirs(DB_DIR, exist_ok=True)

signals = [
    {
        "model": "DeepSeek-V2",
        "signal": "MLA (Multi-Head Latent Attention) with RoPE decoupling. DeepSeekMoE. 236B total params, 21B active. O(1) KV cache compression.",
        "confidence": "C5-REAL"
    },
    {
        "model": "Llama-3-70B",
        "signal": "Dense Transformer, GQA (Grouped Query Attention). Optimized for extreme TPS via KV cache size reduction. 8 KV heads.",
        "confidence": "C5-REAL"
    }
]

def get_cortex_taint(data: str) -> str:
    return f"TAINT_REVENG_{int(time.time())}"

def run():
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bft_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lamport_t INTEGER,
            agent_id TEXT,
            prev_hash TEXT UNIQUE,
            hash TEXT UNIQUE,
            cortex_taint TEXT,
            model_target TEXT,
            signal_data TEXT,
            confidence TEXT,
            UNIQUE(lamport_t, agent_id)
        )
    """)
    
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS bft_no_update
        BEFORE UPDATE ON bft_ledger
        BEGIN
            SELECT RAISE(ABORT, 'C5-REAL: MASTER LEDGER IS IMMUTABLE');
        END;
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS bft_no_delete
        BEFORE DELETE ON bft_ledger
        BEGIN
            SELECT RAISE(ABORT, 'C5-REAL: MASTER LEDGER IS IMMUTABLE');
        END;
    """)

    cursor = conn.cursor()
    cursor.execute("BEGIN EXCLUSIVE TRANSACTION;")
    try:
        cursor.execute("SELECT MAX(lamport_t), hash FROM bft_ledger")
        row = cursor.fetchone()
        
        current_lamport = row[0] if row[0] is not None else 0
        prev_hash = row[1] if row[1] is not None else "GENESIS_HASH"
        
        for sig in signals:
            current_lamport += 1
            taint = get_cortex_taint(sig["signal"])
            content = f"{current_lamport}{AGENT_ID}{prev_hash}{sig['model']}{sig['signal']}{taint}"
            current_hash = hashlib.sha256(content.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO bft_ledger (lamport_t, agent_id, prev_hash, hash, cortex_taint, model_target, signal_data, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (current_lamport, AGENT_ID, prev_hash, current_hash, taint, sig['model'], sig['signal'], sig['confidence']))
            
            prev_hash = current_hash
            print(f"[{current_lamport}] {sig['model']} -> {current_hash[:16]}")
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(lamport_t) FROM bft_ledger")
        max_t = cursor.fetchone()[0]
        print(f"C5-REAL Tie-Breaking: Recuperación BFT. MAX(lamport_t) = {max_t}")

    conn.close()

if __name__ == "__main__":
    run()
