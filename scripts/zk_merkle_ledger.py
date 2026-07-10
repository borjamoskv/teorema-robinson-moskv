import os
import sqlite3
import hashlib
import json

DB_PATH = "/Users/borjafernandezangulo/.babylon60/zk_ledger.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    # Tabla inmutable
    conn.execute('''
        CREATE TABLE IF NOT EXISTS causal_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            merkle_root TEXT NOT NULL UNIQUE
        );
    ''')

    # Trigger de Fallo Causal (Inmutabilidad absoluta post-inserción)
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS trigger_abort_update
        BEFORE UPDATE ON causal_chain
        BEGIN
            SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Mutación prohibida en Merkle Ledger.');
        END;
    ''')
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS trigger_abort_delete
        BEFORE DELETE ON causal_chain
        BEGIN
            SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Eliminación prohibida en Merkle Ledger.');
        END;
    ''')

    # Trigger de Validación Causal (Aserción de prev_hash)
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS trigger_validate_chain
        BEFORE INSERT ON causal_chain
        FOR EACH ROW
        WHEN NEW.id > 1 AND NEW.prev_hash != (SELECT merkle_root FROM causal_chain WHERE id = NEW.id - 1)
        BEGIN
            SELECT RAISE(ABORT, 'C5-REAL SIGKILL: Fractura topológica detectada. prev_hash no coincide con la raíz anterior.');
        END;
    ''')
    
    conn.commit()
    return conn

def hash_data(data: str) -> str:
    """Implementa BLAKE2s para emular el hashing determinista"""
    h = hashlib.blake2s()
    h.update(data.encode('utf-8'))
    return h.hexdigest()

def insert_zk_trace(conn, payload_dict: dict):
    cursor = conn.cursor()
    cursor.execute("SELECT id, merkle_root FROM causal_chain ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    
    prev_hash = row[1] if row else "GENESIS_BLOCK_0000000000000000"
    payload_str = json.dumps(payload_dict, sort_keys=True)
    
    # El zk_proof físico local (simulado) es el hash computado de [prev_hash + payload]
    merkle_root = hash_data(prev_hash + payload_str)
    
    try:
        cursor.execute(
            "INSERT INTO causal_chain (payload, prev_hash, merkle_root) VALUES (?, ?, ?)",
            (payload_str, prev_hash, merkle_root)
        )
        conn.commit()
        return merkle_root
    except sqlite3.IntegrityError as e:
        print(f"FAILED: {e}")
        conn.rollback()
        raise

if __name__ == "__main__":
    conn = init_db()
    # Insert 5 test blocks
    print("Iniciando inyección de entropía en ZK Merkle Ledger...")
    for i in range(1, 6):
        root = insert_zk_trace(conn, {"AST_delta": f"mut_node_{i}", "entropy_score": 0.0})
        print(f"Block {i} collapsado. Merkle Root: {root}")

    # Demostrar el fallo causal manual
    print("\n--- INYECTANDO CORRUPCIÓN (TEST DE FALLO CAUSAL) ---")
    try:
        conn.execute("UPDATE causal_chain SET payload = 'corrupted' WHERE id = 2")
    except sqlite3.IntegrityError as e:
        print(f"Éxito: Fallo Causal detonado en UPDATE. ({e})")
        
    try:
        conn.execute("DELETE FROM causal_chain WHERE id = 3")
    except sqlite3.IntegrityError as e:
        print(f"Éxito: Fallo Causal detonado en DELETE. ({e})")
        
    # Demostrar rotura de cadena en inserción
    print("\n--- TEST DE FRACTURA DE CADENA ---")
    try:
        conn.execute("INSERT INTO causal_chain (id, payload, prev_hash, merkle_root) VALUES (6, '{}', 'FAKE_HASH', 'FAKE_ROOT')")
    except sqlite3.IntegrityError as e:
        print(f"Éxito: Fallo Causal detonado en INSERT (Cadena rota). ({e})")
        
    conn.close()
