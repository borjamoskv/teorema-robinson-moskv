import sqlite3
import re
import hashlib
import os

DB_PATH = "/Users/borjafernandezangulo/30_BABYLON-60/cortex/ontology/isomorfismos_500.sqlite"
MD_PATH = "/Users/borjafernandezangulo/30_BABYLON-60/cortex/ontology/isomorfismos_estructurales_500.md"

def extract_entropy():
    conn = sqlite3.connect(DB_PATH, timeout=5000)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    conn.execute("DROP TABLE IF EXISTS structural_primitives")
    conn.execute("""
        CREATE TABLE structural_primitives (
            id INTEGER PRIMARY KEY,
            domain TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            lamport_t INTEGER DEFAULT 0,
            causal_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    
    with open(MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Split to ignore the Protocolo section at the end
    content = content.split("## Protocolo para evitar")[0]

    # Regex to match:
    # 1. **Name:** description
    # 251. **Name.**
    pattern = re.compile(r"^(\d+)\.\s+\*\*([^\*]+)\*\*(?:[ \t]+(.*))?$", re.MULTILINE)
    matches = pattern.findall(content)

    if not matches:
        print("SIGKILL_STATE_PURGE: No matches found. Regex failure.")
        return

    cursor = conn.cursor()
    cursor.execute("DELETE FROM structural_primitives") 

    count = 0
    for match in matches:
        uid = int(match[0])
        name = match[1].strip()
        # Clean up name if it ends with colon or period
        if name.endswith(':') or name.endswith('.'):
            name = name[:-1].strip()

        desc = match[2].strip() if match[2] else "N/A"
        
        node_type = "PRIMITIVE" if uid <= 250 else "INVARIANT"
        
        domain = "UNKNOWN"
        if 1 <= uid <= 25: domain = "Sustrato_Tipado"
        elif 26 <= uid <= 50: domain = "Relaciones_Incidencia"
        elif 51 <= uid <= 75: domain = "Operaciones_Algebraicas"
        elif 76 <= uid <= 100: domain = "Orden_Geometria_Topologia"
        elif 101 <= uid <= 125: domain = "Descomposicion_Interfaces"
        elif 126 <= uid <= 150: domain = "Dinamica_Concurrencia"
        elif 151 <= uid <= 175: domain = "Logica_Restricciones"
        elif 176 <= uid <= 200: domain = "Correspondencia_Sintesis"
        elif 201 <= uid <= 225: domain = "Magnitudes_Pesos"
        elif 226 <= uid <= 250: domain = "Canonizacion_Verificacion"
        elif 251 <= uid <= 275: domain = "Signatura_Cardinalidad"
        elif 276 <= uid <= 300: domain = "Incidencia_Matrices_Refinamiento"
        elif 301 <= uid <= 325: domain = "Conectividad_Caminos_Ciclos"
        elif 326 <= uid <= 350: domain = "Invariantes_Algebraicos"
        elif 351 <= uid <= 375: domain = "Ordenes_Reticulos"
        elif 376 <= uid <= 400: domain = "Simetria_Descomposicion"
        elif 401 <= uid <= 425: domain = "Dinamica_Lenguajes_Concurrencia"
        elif 426 <= uid <= 450: domain = "Topologia_Homologia"
        elif 451 <= uid <= 475: domain = "Pesos_Medidas_Espectros"
        elif 476 <= uid <= 500: domain = "Logica_Conteos_Completitud"

        sig = f"{uid}|{node_type}|{domain}|{name}|{desc}"
        causal_hash = hashlib.blake2s(sig.encode()).hexdigest()

        try:
            cursor.execute(
                "INSERT INTO structural_primitives (id, domain, name, description, type, causal_hash) VALUES (?, ?, ?, ?, ?, ?)",
                (uid, domain, name, desc, node_type, causal_hash)
            )
            count += 1
        except sqlite3.IntegrityError as e:
            print(f"Error on {uid} ({name}): {e}")

    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM structural_primitives")
    final_count = cursor.fetchone()[0]
    
    print(f"C5-REAL_COLLAPSE_SUCCESS: {final_count}/500 entidades transducidas a SQLite WAL.")
    conn.close()

if __name__ == "__main__":
    extract_entropy()
