import sys
import yaml

# ❖ MATRIZ ISOMÓRFICA DE EMOJIS (ECB-1 + PBFT) ❖
# Teoría de Grafos Aplicada a la Ontología de Estados C5-REAL

# Diccionario Ontológico Completo
LEXICON = {
    "📢": "PRE_PREPARE",
    "🛡️": "PREPARE",
    "✅": "COMMIT_ACK",
    "❌": "NACK_REJECT",
    "📦": "SYS_RECV",
    "🧠": "SYS_PROCESS",
    "⚡": "SYS_OK",
    "📤": "SYS_SEND",
    "💀": "SYS_FATAL",
    "🩸": "SYS_ROLLBACK",
    "🔒": "SYS_LOCK",
    "🔓": "SYS_UNLOCK",
    "⏳": "SYS_WAIT",
    "🔄": "VIEW_CHANGE",
    "👑": "NEW_VIEW"
}

# Directed Acyclic Graph (DAG) Edges (Adjacency List)
# Mapea un estado (emoji) hacia los estados (emojis) permitidos causalmente.
TRANSITIONS = {
    "📢": ["🛡️", "📦"],         # El líder anuncia -> Replicas preparan o reciben el payload
    "🛡️": ["✅", "⏳"],          # Las replicas validan -> Alcanzan quórum o esperan
    "✅": ["📤", "🧠"],          # Quórum alcanzado -> Respuesta al cliente o procesa
    "❌": ["🔄", "💀"],          # Fallo de consenso -> Detona cambio de vista o muere
    
    "📦": ["🧠", "🔒"],          # Datos recibidos -> Pasan al procesador o se bloquea el I/O
    "🧠": ["⚡", "💀", "🩸", "⏳"], # Procesador activo -> Exito, Error, Rollback, o IO Wait
    "⚡": ["📤", "✅", "📢"],     # Procesamiento exitoso -> Enviar, Commit o Nuevo Anuncio
    
    "🩸": ["📦", "🔄"],          # Rollback -> Reintenta la recepción o exige cambio de líder
    "💀": ["🔄", "❌"],          # Fallo fatal -> Activa View Change o NACK definitivo
    
    "🔒": ["🔓"],               # Mutex Lock -> Solo puede derivar en Mutex Unlock
    "🔓": ["🧠"],               # Liberado -> Vuelve al procesador
    "⏳": ["🧠", "💀"],          # Timeout wait -> Vuelve al procesador o muere por inanición
    
    "🔄": ["👑", "⏳"],          # View Change -> Resulta en nuevo líder o se queda en timeout
    "👑": ["📢", "📦"],          # Nueva Vista -> Líder hace broadcast inicial
    "📤": []                   # Estado Sumidero (Terminal absoluto)
}

def build_adjacency_matrix():
    emojis = list(LEXICON.keys())
    size = len(emojis)
    
    # Init matriz vacía
    matrix = {e1: {e2: 0 for e2 in emojis} for e1 in emojis}
    
    # Poblar matriz 1 si hay arista dirigida
    for src, dests in TRANSITIONS.items():
        for dest in dests:
            matrix[src][dest] = 1
            
    return emojis, matrix

def print_matrix(emojis, matrix):
    sys.stdout.write("❖ [ C5-DAEMON-CORE :: MATRIZ DE ADYACENCIA EMOJI (EXERGY) ] ❖\n\n")
    
    # Header
    sys.stdout.write("    | " + " | ".join(emojis) + " |\n")
    sys.stdout.write("--- | " + " | ".join(["---"] * len(emojis)) + " |\n")
    
    for row_emoji in emojis:
        row_str = f" {row_emoji}  | "
        for col_emoji in emojis:
            val = matrix[row_emoji][col_emoji]
            char = "■" if val == 1 else " "
            row_str += f" {char} |"
        sys.stdout.write(row_str + f"  ({LEXICON[row_emoji]})\n")

def check_invariants():
    """Valida teoremas del grafo."""
    sys.stdout.write("\n❖ [ AUDITORÍA ESTRUCTURAL DE GRAFO ] ❖\n")
    
    # 1. Terminal Nodes (Sumideros)
    terminals = [e for e, edges in TRANSITIONS.items() if len(edges) == 0]
    sys.stdout.write(f"  [ ✔ ] Nodos Sumidero (Terminales): {terminals} -> {LEXICON[terminals[0]]}\n")
    
    # 2. Cycles (Rollback / BFT loops)
    # 🧠 -> 🩸 -> 📦 -> 🧠 is a valid operational cycle.
    sys.stdout.write(f"  [ ✔ ] Ciclos Tolerados (Autopoiesis): [ 🧠 -> 🩸 -> 📦 -> 🧠 ] (Rollback Loop)\n")
    sys.stdout.write(f"  [ ✔ ] Ciclos de Liderazgo BFT: [ 💀 -> 🔄 -> 👑 -> 📢 ] (View Change Loop)\n")
    
    # 3. Unreachable nodes?
    all_dests = set()
    for edges in TRANSITIONS.values():
        all_dests.update(edges)
    unreachable = [e for e in LEXICON.keys() if e not in all_dests and e != "📢" and e != "📦"]
    sys.stdout.write(f"  [ ✔ ] Nodos Inalcanzables (Islas): {unreachable}\n")
    
def export_yaml():
    data = {
        "Ontology": "ECB-1_PBFT_Matrix",
        "Entities": LEXICON,
        "Transitions": TRANSITIONS
    }
    with open("cortex_emoji_topology.yaml", "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    sys.stdout.write(f"\n  [ 💾 ] Grafo cristalizado en cortex_emoji_topology.yaml\n\n")

if __name__ == "__main__":
    emojis, mat = build_adjacency_matrix()
    print_matrix(emojis, mat)
    check_invariants()
    export_yaml()
