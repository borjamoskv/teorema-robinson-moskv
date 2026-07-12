import subprocess
import sys

prompt = '\nOBJETIVO: Erradicar la violación de `INV_BFT_01 (Zero Memory Sequencing)` en `bft/ledger_actor.py` y `core/master_ledger.py`.\n\nCONTEXTO:\nActualmente, el reloj de Lamport y el `prev_hash` se leen hacia la memoria de Python, creando un hueco de fidelidad semántica (TOCTOU) bajo concurrencia:\n`cur = await db.execute("SELECT lamport_t, entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1")`\n`lamport_t = prev_lamport + 1`\n\nRESTRICCIÓN FÍSICA:\nEl hash criptográfico (`entry_hash`) depende de `lamport_t` y `prev_hash`, y requiere serialización JSON canónica (Python). SQLite nativo no soporta SHA256.\n\nVECTOR DE SOLUCIÓN ESTRICTA (C5-REAL):\n1. Registra una función determinista en SQLite al inicializar la conexión (`db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)`). Para `aiosqlite`, accede a la conexión subyacente o configurándola.\n2. Aniquila el `SELECT` previo en `_process`.\n3. Fusiona la lectura y la mutación en un único `INSERT INTO ... SELECT` atómico:\n\nINSERT INTO ledger_entries (...)\nSELECT \n    event_id, stream, entity_id, event_type, payload, \n    source_db, source_table, source_pk, cortex_taint,\n    COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1 AS new_lamport,\n    COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), \'0000000000000000000000000000000000000000000000000000000000000000\') AS prev_hash,\n    c5_compute_hash(event_id, stream, entity_id, event_type, payload, source_db, source_table, source_pk, cortex_taint, new_lamport, prev_hash, created_at),\n    created_at\nRETURNING seq, lamport_t, prev_hash, entry_hash;\n\nINSTRUCCIONES DE COLAPSO:\n- Refactoriza ambos archivos (`bft/ledger_actor.py` y `core/master_ledger.py`).\n- Elimina el Python-side `SELECT`.\n- Adapta el unpacking del `RETURNING` para setear el `future.set_result`.\n- No pidas disculpas ni des explicaciones. Genera el código mutado, asegúrate de que pasa el linter y haz un Git Commit con el prefijo "fix(bft): atomize lamport_t sequence generation via sqlite".\n'
print("C5-REAL BRIDGE: Inyectando prompt a Claude Code (Fable 5)...")
try:
    process = subprocess.run(
        ["/opt/homebrew/bin/claude", "-p", prompt],
        cwd="$CORTEX_ROOT/30_BABYLON-60",
        capture_output=True,
        text=True,
        check=True,
    )
    print("OUTPUT CLAUDE:")
    print(process.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error invocado claude: {e}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
    sys.exit(1)
