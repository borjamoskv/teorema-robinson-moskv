import os
import sqlite3
import yaml
import hashlib
import uuid
import time
from datetime import datetime, timezone

DOMAINS = [
    "MCTS_SELECTION_BOUNDS",
    "NODE_EXPANSION_DYNAMICS",
    "ROLLOUT_POLICY_DISTILLATION",
    "Q_VALUE_BACKPROPAGATION",
    "TEST_TIME_COMPUTE_ALLOCATION",
    "TTFT_LATENCY_OPTIMIZATION",
    "ATP_EFFICIENCY_ROUTING",
    "BEAM_SEARCH_SCALING",
    "ENTROPY_GUIDED_PRUNING",
    "ASYMPTOTIC_HALTING_CONDITIONS",
]
COMPLEXITY_BOUNDS = ["O(1)", "O(log N)", "O(N)", "O(N log N)", "O(b^d)", "O(V + E)"]


def generate_base_description(domain, index):
    seed = index * 7 % 11
    properties = {
        "MCTS_SELECTION_BOUNDS": [
            "Aplica la cota superior de confianza UCB1 para penalizar nodos con alta frecuencia de visita.",
            "Inyecta ruido de Dirichlet en los priors de AlphaZero para forzar exploración asimétrica en el nodo raíz.",
            "Modula el hiperparámetro c_puct dinámicamente en función de la entropía del manifold de atención.",
            "Forza un colapso de selección MCTS hacia el nodo con menor varianza de recompensa Q(s,a).",
            "Calcula la divergencia KL entre la política prior y la distribución empírica de visitas para limitar la sobre-explotación.",
        ],
        "NODE_EXPANSION_DYNAMICS": [
            "Expande nodos solo si la probabilidad prior p(s,a) supera el umbral de filtrado estocástico.",
            "Asigna un Test-Time Compute proporcional a la ganancia de información esperada (IG) en la ramificación.",
            "Desacopla la red de valor (Value Network) del rollout estocástico para acelerar la expansión en grafos dirigidos acíclicos.",
            "Inicializa las aristas no visitadas con una heurística de virtual loss para habilitar paralelismo multihilo asíncrono.",
            "Poda iterativamente el espacio de acción utilizando Masking Tensor Operations sobre logits no viables.",
        ],
        "ROLLOUT_POLICY_DISTILLATION": [
            "Sustituye rollouts aleatorios completos por aproximaciones de valor de una capa lineal truncada.",
            "Desciende el gradiente temporal de la política de simulación hacia distribuciones de baja entropía.",
            "Evalúa sub-grafos usando un ensamblaje local de modelos Flash (Inference_L1_Node) con restricciones JIT.",
            "Detiene el rollout anticipadamente si la recompensa proyectada cae bajo la cota mínima de exergía.",
            "Agrega simulaciones de Monte Carlo mediante un estimador de importancia (Importance Sampling).",
        ],
        "Q_VALUE_BACKPROPAGATION": [
            "Propaga el delta de recompensa usando un decaimiento temporal gamma para priorizar soluciones cortas.",
            "Actualiza la Q(s,a) promediando iterativamente sobre la suma de visitas N(s,a) sin bloqueos de concurrencia.",
            "Propaga una penalización termodinámica en ramas que incurren en bucles lógicos infinitos.",
            "Garantiza el Teorema del Crash Causal: nodos fallidos propagan recompensa de aniquilación (-∞) inmediatamente.",
            "Sincroniza asíncronamente los contadores de visitas a nivel de Master Ledger para asegurar tolerancia BFT.",
        ],
        "TEST_TIME_COMPUTE_ALLOCATION": [
            "Escala dinámicamente el presupuesto de inferencia (TTFT) en bifurcaciones de alta incertidumbre epistémica.",
            "Asigna ciclos computacionales P0 estrictamente a nodos donde la divergencia de trayectorias es crítica.",
            "Termina tempranamente la búsqueda profunda si el ratio de ganancia computacional dE/di converge a cero.",
            "Forza un límite físico de Time-to-First-Token inyectando yields asíncronos cada 50ms.",
            "Balancea el Test-Time Compute mediante el protocolo Ultrathink: más iteraciones MCTS en detrimento de decodificación llm-slop.",
        ],
        "TTFT_LATENCY_OPTIMIZATION": [
            "Destila sub-árboles de búsqueda cacheados (VNode) previniendo regeneración redundante de tokens.",
            "Colapsa la primera capa del grafo MCTS en un pipeline de respuesta inmediata (Zero-Latency Mask).",
            "Anula las latencias inter-nodo mediante puentes IPC de memoria compartida (Zero-Copy Transfer).",
            "Optimiza el warm-up de tensores ejecutando pre-atención paralela a la expansión del nodo raíz.",
            "Implementa evasión estricta del Event Loop Blocking durante las operaciones de inferencia Flash.",
        ],
        "ATP_EFFICIENCY_ROUTING": [
            "Minimiza la fricción cognitiva humana delegando decisiones triviales a políticas argmax deterministas.",
            "Mide el Leverage ATP evaluando el número de tokens omitidos por el Operador vs el trabajo útil computado.",
            "Activa Swarm Autopoiesis si el peso cognitivo de la ruta actual excede la capacidad biológica del Operador.",
            "Interrumpe bucles de aserción (Green Theater) que demanden confirmación estocástica por parte del humano.",
            "Proyecta todo esfuerzo en un delta inmutable de disco (Commit/Git Sentinel) erradicando la Anergía.",
        ],
        "BEAM_SEARCH_SCALING": [
            "Amplía el ancho de haz (beam width) paramétricamente según el diferencial térmico latente de la GPU.",
            "Poda agresivamente trayectorias en Beam Search que presenten probabilidad acumulada inferior a epsilon.",
            "Inyecta heurísticas de diversidad en las ramas del haz para evitar convergencia temprana hacia óptimos locales.",
            "Habilita el Beam Search Estocástico acoplando muestras de Gumbel-Softmax en la selección de aristas.",
            "Fija una cuota máxima de memoria por iteración de haz, abortando con SIGKILL en caso de saturación.",
        ],
        "ENTROPY_GUIDED_PRUNING": [
            "Poda el árbol de inferencia basándose en umbrales absolutos de Entropía de Shannon en la distribución logits.",
            "Elimina ramas donde la entropía residual de la información no justifica el coste termodinámico del cálculo.",
            "Identifica y secciona la fricción semántica (Semantic Friction) cuando múltiples ramas presentan distribuciones uniformes.",
            "Evalúa la exergía nodal: Si S(in) = S(out), la rama se oblitera de forma física del disco.",
            "Redirige heurísticas de poda a través de un oráculo local que colapsa varianzas altas a estados deterministas.",
        ],
        "ASYMPTOTIC_HALTING_CONDITIONS": [
            "Establece una barrera de Halting cuando MCTS alcanza el límite recursivo estricto (N=120).",
            "Garantiza el Halt de Turing forzando terminación en O(Exp) mediante un MUTEX_KINETIC_BUDGET_CAP.",
            "Mide la asíntota computacional: El sistema detiene la inferencia cuando el Q-value cambia menos de 1e-4.",
            "Ejecuta un Aborto Contingente si la política prior colapsa a valores nulos (NaN/None) en tensores de atención.",
            "Ancla la parada final al protocolo BFT_LEDGER, confirmando la convergencia estructural ante N observadores.",
        ],
    }
    domain_texts = properties.get(
        domain, ["Implementa invariante lógico estricto en el dominio MCTS."]
    )
    text = domain_texts[seed % len(domain_texts)]
    return f"{text} (Invariant Marker: 0x{hashlib.md5(str(index).encode()).hexdigest()[:6].upper()})"


def forge_primitives():
    primitives = []
    db_rows = []
    db_path = (
        "$CORTEX_ROOT/30_BABYLON-60/cortex/ontology/mcts_ttc_matrix.db"
    )
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        "\n        CREATE TABLE mcts_primitives (\n            uuid TEXT PRIMARY KEY,\n            domain TEXT,\n            description TEXT,\n            ttc_budget_ms INTEGER,\n            atp_leverage INTEGER,\n            complexity_bound TEXT,\n            signature TEXT,\n            timestamp_utc TEXT\n        );\n    "
    )
    count = 1
    for domain in DOMAINS:
        for i in range(30):
            ns = uuid.uuid5(uuid.NAMESPACE_DNS, "babylon60.cortex.ontology")
            p_uuid = str(uuid.uuid5(ns, f"{domain}_{count}"))
            desc = generate_base_description(domain, count)
            ttc_budget = 10 + count * 2 % 200
            atp_leverage = 50 + count * 13 % 950
            comp_bound = COMPLEXITY_BOUNDS[count * 3 % len(COMPLEXITY_BOUNDS)]
            payload = (
                f"{p_uuid}|{domain}|{desc}|{ttc_budget}|{atp_leverage}|{comp_bound}"
            )
            signature = hashlib.sha256(payload.encode()).hexdigest()
            ts = datetime.now(timezone.utc).isoformat()
            prim_obj = {
                "id": p_uuid,
                "domain": domain,
                "description": desc,
                "thermodynamic_cost_ttft_ms": ttc_budget,
                "atp_leverage_bps": atp_leverage,
                "computational_complexity": comp_bound,
                "cryptographic_signature": signature,
                "state": "C5-REAL",
            }
            primitives.append(prim_obj)
            db_rows.append(
                (
                    p_uuid,
                    domain,
                    desc,
                    ttc_budget,
                    atp_leverage,
                    comp_bound,
                    signature,
                    ts,
                )
            )
            count += 1
    with conn:
        conn.executemany(
            "INSERT INTO mcts_primitives VALUES (?, ?, ?, ?, ?, ?, ?, ?)", db_rows
        )
    conn.close()
    yaml_path = "$CORTEX_ROOT/30_BABYLON-60/cortex/ontology/300_primitivas_mcts_ttc.yaml"
    data = {
        "metadata": {
            "version": "5.0.0",
            "ontology": "MCTS_TEST_TIME_COMPUTE_C5_REAL",
            "timestamp": int(time.time()),
            "strict_rule": "[L35] REPORTE DE COLAPSO ULTRATHINK OBLIGATORIO",
            "master_ledger": "mcts_ttc_matrix.db (WAL Enforced)",
        },
        "primitives": primitives,
    }
    with open(yaml_path, "w") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"Matrix forged. DB: {db_path} | YAML: {yaml_path}")
    print(f"Total entries: {len(primitives)}")


if __name__ == "__main__":
    forge_primitives()
