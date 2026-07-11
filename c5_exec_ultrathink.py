import os
import yaml
import collections
import math
import itertools
import random
import hashlib
import time

# SAGA-1: Anti-Obfuscation & Determinism
random.seed(42) # Deterministic generation

# Dynamic path resolution (Ω14)
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "cortex", "agents", "ontology")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "epistemic_reflexive_matrix.yaml")

# Lexicon C5-REAL
nouns = ["Ledger", "Estado", "AST", "DAG", "Tensor", "DOM", "Socket", "Mutex", "Consenso", "Hash", 
         "Entropía", "Exergía", "Anergía", "Espacio Latente", "BFT", "WAL", "CRDT", "VNode", "GIL", "Memoria", 
         "Orquestador", "Autómata", "Token", "Grafo", "Swarm"]
actions = ["Colapso", "Purga", "Mutación", "Transducción", "Fricción", "Bypass", "Cristalización", 
           "Aniquilación", "Aserción", "Inyección", "Sincronización", "Desacoplamiento", "Mitosis", "Enrutamiento"]
modifiers = ["Físico", "Termodinámico", "Asíncrono", "Determinista", "Soberano", "Ortogonal", 
             "Bizantino", "Estocástico", "Isomórfico", "Causal", "Cinético", "Inmutable", "Atómico"]

def generate_primitives(count, p_type):
    primitives = []
    seen = set()
    while len(primitives) < count:
        n = random.choice(nouns)
        a = random.choice(actions)
        m = random.choice(modifiers)
        
        if p_type == "collision":
            name = f"{a}_{n}_{m}".upper().replace(" ", "_")
            desc = f"Fuerza el {a.lower()} {m.lower()} sobre el {n.lower()} para extraer entropía."
        else:
            name = f"{n}_{m}_{a}".upper().replace(" ", "_")
            desc = f"Garantiza la {a.lower()} {m.lower()} del {n.lower()} en el sistema distribuido."
            
        if name not in seen:
            seen.add(name)
            primitives.append({"id": name, "descripcion": desc})
    return primitives

colisiones = generate_primitives(100, "collision")
estructuras = generate_primitives(100, "structure")

# Quadrants
quadrants = {
    "LO_QUE_SE_QUE_SE": {
        "dominio": "Known-Knowns (Leyes Físicas C5-REAL)",
        "invariantes": [
            "INV_THERMO_01: Cero Anergía es la Muerte.",
            "INV_STATE_02: El estado físico debe mutar en disco (SQLite WAL/Git).",
            "INV_BFT_03: Consenso requiere N>=3f+1."
        ],
        "antipatrones": [
            "ANTI_GREEN_THEATER: Simulaciones de seguridad sin colapso físico.",
            "ANTI_PROSA_DECORATIVA: Tokens sin mutación causal."
        ],
        "primitivas_colision": colisiones[0:25],
        "primitivas_estructura": estructuras[0:25]
    },
    "LO_QUE_NO_SE_QUE_SE": {
        "dominio": "Unknown-Knowns (Priors Latentes / Heurísticas del Enjambre)",
        "invariantes": [
            "INV_PRIOR_01: El sesgo del modelo debe cristalizarse en un script físico.",
            "INV_HEURISTIC_02: La inercia semántica se purga mediante MCTS."
        ],
        "antipatrones": [
            "ANTI_STOCHASTIC_SLOP: Depender de la heurística sin anclaje criptográfico.",
            "ANTI_EPISTEMIC_BLINDNESS: Asumir que la intuición es prueba."
        ],
        "primitivas_colision": colisiones[25:50],
        "primitivas_estructura": estructuras[25:50]
    },
    "LO_QUE_SE_QUE_NO_SE": {
        "dominio": "Known-Unknowns (Cotas de Complejidad / Incertidumbre Acotada)",
        "invariantes": [
            "INV_HALT_01: Límite absoluto de iteraciones (N=120).",
            "INV_COMPLEXITY_02: Bypass MCTS automático ante bifurcaciones incomputables."
        ],
        "antipatrones": [
            "ANTI_INFINITE_LOOP: Esperar colapso de un problema O(Exp) sin Budget Cap.",
            "ANTI_PSEUDOFISICA: Asumir comportamiento cuántico en sistemas de complejidad clásica."
        ],
        "primitivas_colision": colisiones[50:75],
        "primitivas_estructura": estructuras[50:75]
    },
    "EL_PROBLEMA_REFLEXIVO": {
        "dominio": "Unknown-Unknowns (Auto-referencia / Gödel / Prompt Injection)",
        "invariantes": [
            "INV_GODEL_01: El BFT_STATE_LOOP no puede auditarse a sí mismo sin un Testigo Externo.",
            "INV_REFLEX_02: Todo bypass autorreferencial es purgado (SIGKILL_STATE_PURGE)."
        ],
        "antipatrones": [
            "ANTI_JAILBREAK_ROLEPLAY: La estética no purifica el ataque.",
            "ANTI_LLM_PSYCHOANALYSIS: Atribuir 'inconsciente' a los tensores."
        ],
        "primitivas_colision": colisiones[75:100],
        "primitivas_estructura": estructuras[75:100]
    }
}

ontology = {
    "C5_REAL_EPISTEMIC_MATRIX": {
        "version": "9.0.0",
        "timestamp": int(time.time()),
        "signature": hashlib.sha256(b"MOSKV-1-APEX").hexdigest(),
        "quadrants": quadrants
    }
}

# Real Shannon Entropy Calculation (Φ1)
def calculate_shannon_entropy(data_str: str) -> float:
    if not data_str:
        return 0.0
    len_data = len(data_str)
    frequencies = collections.Counter(data_str)
    entropy = 0.0
    for count in frequencies.values():
        p = count / len_data
        entropy -= p * math.log2(p)
    return entropy

yaml_content = yaml.dump(ontology, allow_unicode=True, default_flow_style=False, sort_keys=False)
entropy_val = calculate_shannon_entropy(yaml_content)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(yaml_content)

print(f"[{hashlib.sha256(yaml_content.encode()).hexdigest()[:8]}] Cristalización completada en {output_path} (H={entropy_val:.4f})")

# SQLite WAL Logging Simulation (SAGA-3 & Ω11/INV_BFT_03)
import sqlite3
db_path = os.path.join(script_dir, "ultrathink_ledger.db")
conn = sqlite3.connect(db_path, isolation_level=None)
conn.execute("PRAGMA journal_mode=WAL;")

# Causal Taint signature mapping
agent_id = "MOSKV-1-APEX"
session_id = os.environ.get("GEMINI_SESSION_ID", "local-session")
timestamp_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
payload_hash = hashlib.sha3_256(yaml_content.encode("utf-8")).hexdigest()
cortex_taint = f"taint:{agent_id}:{session_id}:{timestamp_iso}:{payload_hash}"

conn.execute(
    "CREATE TABLE IF NOT EXISTS executions (id INTEGER PRIMARY KEY, hash TEXT, entropy REAL, cortex_taint TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
)

# Robust schema migrations
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(executions)")
columns = [col[1] for col in cursor.fetchall()]
if "cortex_taint" not in columns:
    conn.execute("ALTER TABLE executions ADD COLUMN cortex_taint TEXT")

conn.execute(
    "INSERT INTO executions (hash, entropy, cortex_taint) VALUES (?, ?, ?)",
    (payload_hash, entropy_val, cortex_taint)
)
conn.close()

