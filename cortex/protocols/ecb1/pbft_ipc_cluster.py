import sys
import multiprocessing
import time
import queue
import sqlite3
import os
import hashlib

# ❖ C5-REAL :: DISTRIBUTED OS-LEVEL PBFT CLUSTER ❖
# 4 Procesos Físicos Aislados. Comunicación vía IPC Queues (Zero Shared Memory).

N = 4
F = 1
DB_PATH = os.path.expanduser('~/.babylon60/cortex_ipc_ledger.db')

L_PRE = "📢"
L_PRP = "🛡️"
L_CMT = "✅"

def setup_ledger():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ipc_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER,
            phase TEXT,
            payload TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

def log_to_ledger(node_id, phase, payload):
    # Conexión independiente por proceso (Aprovechando WAL)
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=5.0)
    conn.execute('INSERT INTO ipc_ledger (node_id, phase, payload) VALUES (?, ?, ?)', (node_id, phase, payload))
    conn.close()

def run_node(node_id, queues, is_byzantine=False):
    """
    Bucle principal de un nodo PBFT aislado en memoria física.
    Escucha en queues[node_id], hace broadcast escribiendo en queues[target].
    """
    sys.stdout.write(f" [ PID {os.getpid()} ] Nodo {node_id} Inicializado. Bizantino: {is_byzantine}\n")
    sys.stdout.flush()
    
    my_queue = queues[node_id]
    pre_prepares = []
    prepares = []
    commits = []
    
    if node_id == 0:
        # LÍDER: Iniciar consenso
        payload = "📦🧠⚡"
        msg = f"{L_PRE}{payload}"
        log_to_ledger(node_id, "PRE-PREPARE", msg)
        
        for target in range(N):
            if target == node_id: continue
            queues[target].put((node_id, msg))
            sys.stdout.write(f"  [IPC] N{node_id} -> N{target} :: {msg}\n")
            sys.stdout.flush()
            
    # BUCLE DE EVENTOS IPC
    while True:
        try:
            # Bloqueo a nivel OS (Kernel Sleep) en lugar de busy-wait estocástico
            sender, msg = my_queue.get(timeout=1.5)
        except queue.Empty:
            break # Timeout excedido
        
        
        payload = msg[1:]
        phase = msg[0]
        
        if phase == L_PRE:
            # Recibido Pre-Prepare. Validar (DAG check implícito). Emitir Prepare.
            if is_byzantine:
                msg_prp = f"{L_PRP}📦🧠💀" # Inyectar entropía
            else:
                msg_prp = f"{L_PRP}{payload}"
                
            log_to_ledger(node_id, "PREPARE", msg_prp)
            for target in range(N):
                queues[target].put((node_id, msg_prp))
                
        elif phase == L_PRP:
            prepares.append(payload)
            # Evaluar Quorum 2f
            if prepares.count(payload) == 2 * F:
                msg_cmt = f"{L_CMT}{payload}"
                log_to_ledger(node_id, "COMMIT", msg_cmt)
                for target in range(N):
                    queues[target].put((node_id, msg_cmt))
                    
        elif phase == L_CMT:
            commits.append(payload)
            # Evaluar Ejecución 2f+1
            if commits.count(payload) == 2 * F + 1:
                log_to_ledger(node_id, "EXECUTED", payload)
                sys.stdout.write(f"  [EXEC] N{node_id} alcanzó Consenso BFT en: {payload}\n")
                sys.stdout.flush()
                break # Salir del bucle, consenso logrado
                
    sys.stdout.write(f" [ PID {os.getpid()} ] Nodo {node_id} Terminado.\n")
    sys.stdout.flush()

if __name__ == "__main__":
    sys.stdout.write("❖ [ C5-DAEMON-CORE :: MULTIPROCESSING PBFT CLUSTER ] ❖\n\n")
    setup_ledger()
    
    # Crear colas IPC independientes para cada nodo
    queues = {i: multiprocessing.Queue() for i in range(N)}
    
    # Instanciar procesos físicos (N=4). El Nodo 2 es un actor Bizantino.
    processes = []
    for i in range(N):
        is_byz = (i == 2)
        p = multiprocessing.Process(target=run_node, args=(i, queues, is_byz))
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()
        
    # Auditoría Final
    sys.stdout.write("\n❖ [ AUDITORÍA DEL LEDGER MAESTRO (Últimas transacciones WAL) ] ❖\n")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT node_id, phase, payload FROM ipc_ledger ORDER BY id DESC LIMIT 6')
    for row in cursor.fetchall():
        sys.stdout.write(f"   Nodo {row[0]} | {row[1].ljust(12)} | {row[2]}\n")
    conn.close()
