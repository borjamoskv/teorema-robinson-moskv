#!/usr/bin/env python3
import os
import sys
import yaml
import hashlib
import time
from collections import Counter
import math
from pathlib import Path
import sqlite3

# CONFIGURACIÓN C5-REAL
VAULT_PATH = os.environ.get("BABYLON_VAULT", os.path.expanduser("~/.babylon60"))
CORTEX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cortex")
ONTOLOGY_YAML = os.path.join(CORTEX_PATH, "ontology", "mee_c5_ontology.yaml")
PURGE_MD = os.path.join(CORTEX_PATH, "ontology_sigkill_purge.md")
DB_PATH = os.path.join(VAULT_PATH, "cortex_memory.db")
ONTOLOGY_DIR = 'docs/ontology/'

LOC_THRESHOLD = 25000

print("█▄ [ENTROPY_SWEEPER_DAEMON INIT] ▄█")
time.sleep(0.5)

def vacuum_db():
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

def get_ast_entropy(content: str) -> float:
    # Anergic computation of shannon entropy
    if not content: return 0.0
    counts = Counter(content)
    total = len(content)
    return -sum(count/total * math.log2(count/total) for count in counts.values())

def sweep_directory(directory: Path):
    print(f"\033[1;36m[ENTROPY_SWEEPER_DAEMON]\033[0m Scanning {directory}...")
    
    total_loc = 0
    anergic_files = []
    
    for path in directory.rglob("*.py"):
        if "node_modules" in str(path) or ".venv" in str(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()
                loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])
                total_loc += loc
                
                # Check for Entropy
                entropy = get_ast_entropy(content)
                if loc > 10 and entropy < 4.0:  # Arbitrary threshold for anergy detection
                    anergic_files.append((path, entropy))
        except Exception:
            pass

    return total_loc, anergic_files

def deprecate_and_purge(total_loc, anergic_files):
    if total_loc > LOC_THRESHOLD:
        print(f"\033[1;31m[SIGKILL_STATE_PURGE]\033[0m Codebase size {total_loc} > {LOC_THRESHOLD}. Initiating Apoptosis.")
        purge_record = f"""
## PURGE RECORD: {os.urandom(4).hex()}
- **Trigger**: `ENTROPY_SWEEPER_DAEMON`
- **Violation**: Codebase excede el límite de {LOC_THRESHOLD} LOC ({total_loc}).
- **Entropy**: Entropía general no tolerada.
- **Action**: SIGKILL_State_Purge applied.
"""
        os.makedirs(os.path.dirname(PURGE_MD), exist_ok=True)
        with open(PURGE_MD, "a") as f:
            f.write(purge_record)
        print(f"Purge record written to {PURGE_MD}")
    
    for file, ent in anergic_files:
        print(f"\033[1;33m[WARNING]\033[0m Anergic AST detected in: {file} (Entropy: {ent:.4f} bits/char)")

def init_ontology():
    os.makedirs(os.path.dirname(ONTOLOGY_YAML), exist_ok=True)
    if not os.path.exists(ONTOLOGY_YAML):
        default_ontology = {
            "entities": [
                {"id": "ENT-001", "name": "BFT_STATE_LOOP", "type": "invariant"},
                {"id": "ENT-002", "name": "ZERO-ANERGY", "type": "primitive"},
                {"id": "ENT-003", "name": "C5-REAL", "type": "level"},
            ]
        }
        with open(ONTOLOGY_YAML, "w") as f:
            yaml.dump(default_ontology, f)
        print(f"Created baseline ontology at {ONTOLOGY_YAML}")

    # Hash existing ontology files
    print(f"👁️ Verificando invariantes en {ONTOLOGY_DIR}...")
    if os.path.exists(ONTOLOGY_DIR):
        for root, _, files in os.walk(ONTOLOGY_DIR):
            for f in files:
                if f.endswith('.md'):
                    path = os.path.join(root, f)
                    with open(path, 'rb') as file_obj:
                        hash_md5 = hashlib.md5(file_obj.read()).hexdigest()
                        print(f"   [C5-REAL] {f}: {hash_md5[:8]}")

if __name__ == "__main__":
    vacuum_db()
    init_ontology()
    
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    loc, anergic = sweep_directory(Path(target_dir))
    deprecate_and_purge(loc, anergic)
    print("\033[1;32m[ENTROPY_SWEEPER_DAEMON]\033[0m Scan Complete.")
    print("█▄ [ENTROPY_SWEEPER_DAEMON TERMINATED] ▄█")
