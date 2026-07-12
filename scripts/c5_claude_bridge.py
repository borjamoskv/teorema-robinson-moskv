import subprocess
import sys

prompt = """
OBJETIVO: Erradicar la violación de `INV_BFT_01 (Zero Memory Sequencing)` en `bft/ledger_actor.py` y `core/master_ledger.py`.

CONTEXTO:
Actualmente, el reloj de Lamport y el `prev_hash` se leen hacia la memoria de Python, creando un hueco de fidelidad semántica (TOCTOU) bajo concurrencia:
`cur = await db.execute("SELECT lamport_t, entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1")`
`lamport_t = prev_lamport + 1`

RESTRICCIÓN FÍSICA:
El hash criptográfico (`entry_hash`) depende de `lamport_t` y `prev_hash`, y requiere serialización JSON canónica (Python). SQLite nativo no soporta SHA256.

VECTOR DE SOLUCIÓN ESTRICTA (C5-REAL):
1. Registra una función determinista en SQLite al inicializar la conexión (`db.create_function("c5_compute_hash", 12, _compute_entry_hash_wrapper, deterministic=True)`). Para `aiosqlite`, accede a la conexión subyacente o configurándola.
2. Aniquila el `SELECT` previo en `_process`.
3. Fusiona la lectura y la mutación en un único `INSERT INTO ... SELECT` atómico:

INSERT INTO ledger_entries (...)
SELECT 
    event_id, stream, entity_id, event_type, payload, 
    source_db, source_table, source_pk, cortex_taint,
    COALESCE((SELECT MAX(lamport_t) FROM ledger_entries), 0) + 1 AS new_lamport,
    COALESCE((SELECT entry_hash FROM ledger_entries ORDER BY seq DESC LIMIT 1), '0000000000000000000000000000000000000000000000000000000000000000') AS prev_hash,
    c5_compute_hash(event_id, stream, entity_id, event_type, payload, source_db, source_table, source_pk, cortex_taint, new_lamport, prev_hash, created_at),
    created_at
RETURNING seq, lamport_t, prev_hash, entry_hash;

INSTRUCCIONES DE COLAPSO:
- Refactoriza ambos archivos (`bft/ledger_actor.py` y `core/master_ledger.py`).
- Elimina el Python-side `SELECT`.
- Adapta el unpacking del `RETURNING` para setear el `future.set_result`.
- No pidas disculpas ni des explicaciones. Genera el código mutado, asegúrate de que pasa el linter y haz un Git Commit con el prefijo "fix(bft): atomize lamport_t sequence generation via sqlite".
"""

print("C5-REAL BRIDGE: Inyectando prompt a Claude Code (Fable 5)...")
try:
    # Use pty or standard run. Claude code might require a TUI, but -p usually bypasses it or streams it.
    process = subprocess.run(
        ["/opt/homebrew/bin/claude", "-p", prompt],
        cwd="$CORTEX_ROOT/30_BABYLON-60",
        capture_output=True,
        text=True,
        check=True
    )
    print("OUTPUT CLAUDE:")
    print(process.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error invocado claude: {e}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
    sys.exit(1)
