import sqlite3
import yaml

import sys
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("CORTEX_DB_PATH", os.path.join(_BASE, "cortex_memory.db"))
MATRIZ_PATH = os.environ.get(
    "CORTEX_MATRIZ_PATH", os.path.join(_BASE, "matriz_1000_primitivas.yaml")
)
ISOMORFISMOS_PATH = os.environ.get(
    "CORTEX_ISOMORFISMOS_PATH",
    os.path.join(_BASE, "isomorfismos_cruzados_1000_primitivas.yaml"),
)


def bootstrap_cortex() -> None:
    print("[CORTEX] Iniciando bootstrap de persistencia de base de datos...")

    # [L12] K1 FAIL-FAST: Verify Physical Assets
    for path in [MATRIZ_PATH, ISOMORFISMOS_PATH]:
        if not os.path.exists(path):
            print(f"\033[1;31m[CORTEX APOPTOSIS]\033[0m Essential Config Missing: {path}. C5-REAL Fail-Fast.", file=sys.stderr)
            sys.exit(1)

    # Cargar YAMLs
    with open(MATRIZ_PATH, "r", encoding="utf-8") as f:
        matriz = yaml.safe_load(f)

    with open(ISOMORFISMOS_PATH, "r", encoding="utf-8") as f:
        isomorfismos = yaml.safe_load(f)

    # Conexión SQLite con WAL y busy_timeout según reglas de la sesión
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    cursor = conn.cursor()

    # Crear tablas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS L1_primitive_nodes (
            id TEXT PRIMARY KEY,
            theory TEXT,
            dimension TEXT,
            name TEXT,
            access_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS L2_isomorphism_edges (
            id TEXT PRIMARY KEY,
            type TEXT,
            source TEXT,
            target TEXT,
            weight REAL,
            justification TEXT,
            hits INTEGER DEFAULT 0,
            last_used TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS L3_inference_cache (
            query_hash TEXT PRIMARY KEY,
            active_mode TEXT,
            retrieved_nodes TEXT,
            applied_isomorphisms TEXT,
            trace_payload TEXT,
            hits INTEGER DEFAULT 0
        )
    """)

    # Crear índices para optimizar búsquedas de O(N) a O(log N)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_l1_theory ON L1_primitive_nodes (theory);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_l2_source ON L2_isomorphism_edges (source);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_l2_target ON L2_isomorphism_edges (target);"
    )

    # Insertar primitivas
    primitives_inserted = 0
    for t_id, t_info in matriz["theories"].items():
        theory_name = t_info["name"]
        for d_name, prims in t_info["dimensions"].items():
            for p_name in prims:
                p_id = f"{t_id}.{d_name.split('_')[0]}.{p_name}"
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO L1_primitive_nodes (id, theory, dimension, name)
                    VALUES (?, ?, ?, ?)
                """,
                    (p_id, theory_name, d_name, p_name),
                )
                primitives_inserted += 1

    # Insertar isomorfismos
    isomorphisms_inserted = 0
    for iso in isomorfismos["isomorphisms"]:
        if iso["type"] == "Fusion-Operator":
            # Guardamos los operadores de fusión de manera adaptada o como relaciones múltiples
            p_id = f"FUSION.{iso['name']}"
            cursor.execute(
                """
                INSERT OR REPLACE INTO L1_primitive_nodes (id, theory, dimension, name)
                VALUES (?, 'FUSION', 'OPERATOR', ?)
            """,
                (p_id, iso["name"]),
            )
            primitives_inserted += 1

            # Conectamos las entradas al operador
            for idx, inp in enumerate(iso["inputs"]):
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO L2_isomorphism_edges (id, type, source, target, weight, justification)
                    VALUES (?, 'FUSION-INPUT', ?, ?, 1.0, ?)
                """,
                    (f"FUSE-{iso['name']}-{idx}", inp, p_id, iso["output_description"]),
                )
                isomorphisms_inserted += 1
        else:
            cursor.execute(
                """
                INSERT OR REPLACE INTO L2_isomorphism_edges (id, type, source, target, weight, justification)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    iso["id"],
                    iso["type"],
                    iso["source"],
                    iso["target"],
                    iso.get("weight", 1.0),
                    iso.get("justification", ""),
                ),
            )
            isomorphisms_inserted += 1

    conn.commit()
    conn.close()

    print("[CORTEX] SQLite persistida exitosamente.")
    print(f"[CORTEX] Nodos Primitivos (L1) instanciados: {primitives_inserted}")
    print(f"[CORTEX] Enlaces Isomorfos (L2) instanciados: {isomorphisms_inserted}")


if __name__ == "__main__":
    bootstrap_cortex()
