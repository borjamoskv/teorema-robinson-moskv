import sqlite3
import os
import hashlib
import time

DB_PATH = 'cortex_memory.db'
ONTOLOGY_DIR = 'docs/ontology/'

print("█▄ [ENTROPY_SWEEPER_DAEMON INIT] ▄█")
time.sleep(0.5)

# 1. Vacuum DB
if os.path.exists(DB_PATH):
    print(f"👁️ Vaciando entropía de {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("VACUUM;")
        conn.execute("PRAGMA optimize;")
        conn.commit()
        conn.close()
        print("⚡ DB Optimizada. Anergía purgada.")
    except Exception as e:
        print(f"💀 Fallo en optimización: {e}")
else:
    print(f"👁️ Base de datos {DB_PATH} no encontrada. Saltando VACUUM.")

# 2. Hashing Ontology
print(f"👁️ Verificando invariantes en {ONTOLOGY_DIR}...")
for root, _, files in os.walk(ONTOLOGY_DIR):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            with open(path, 'rb') as file_obj:
                hash_md5 = hashlib.md5(file_obj.read()).hexdigest()
                print(f"   [C5-REAL] {f}: {hash_md5[:8]}")
                
print("█▄ [ENTROPY_SWEEPER_DAEMON TERMINATED] ▄█")
