import sys
import multiprocessing
import time
import queue
import sqlite3
import os
import hashlib
N = 4
F = 1
DB_PATH = os.path.expanduser('~/.babylon60/cortex_ipc_ledger.db')
L_PRE = '📢'
L_PRP = '🛡️'
L_CMT = '✅'

def setup_ledger():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('\n        CREATE TABLE IF NOT EXISTS ipc_ledger (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            node_id INTEGER,\n            phase TEXT,\n            payload TEXT,\n            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n        )\n    ')
    conn.close()

def log_to_ledger(node_id, phase, payload):
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=5.0)
    conn.execute('INSERT INTO ipc_ledger (node_id, phase, payload) VALUES (?, ?, ?)', (node_id, phase, payload))
    conn.close()

def run_node(node_id, queues, is_byzantine=False):
    sys.stdout.write(f' [ PID {os.getpid()} ] Nodo {node_id} Inicializado. Bizantino: {is_byzantine}\n')
    sys.stdout.flush()
    my_queue = queues[node_id]
    pre_prepares = []
    prepares = []
    commits = []
    if node_id == 0:
        payload = '📦🧠⚡'
        msg = f'{L_PRE}{payload}'
        log_to_ledger(node_id, 'PRE-PREPARE', msg)
        for target in range(N):
            if target == node_id:
                continue
            queues[target].put((node_id, msg))
            sys.stdout.write(f'  [IPC] N{node_id} -> N{target} :: {msg}\n')
            sys.stdout.flush()
    while True:
        try:
            sender, msg = my_queue.get(timeout=1.5)
        except queue.Empty:
            break
        payload = msg[1:]
        phase = msg[0]
        if phase == L_PRE:
            if is_byzantine:
                msg_prp = f'{L_PRP}📦🧠💀'
            else:
                msg_prp = f'{L_PRP}{payload}'
            log_to_ledger(node_id, 'PREPARE', msg_prp)
            for target in range(N):
                queues[target].put((node_id, msg_prp))
        elif phase == L_PRP:
            prepares.append(payload)
            if prepares.count(payload) == 2 * F:
                msg_cmt = f'{L_CMT}{payload}'
                log_to_ledger(node_id, 'COMMIT', msg_cmt)
                for target in range(N):
                    queues[target].put((node_id, msg_cmt))
        elif phase == L_CMT:
            commits.append(payload)
            if commits.count(payload) == 2 * F + 1:
                log_to_ledger(node_id, 'EXECUTED', payload)
                sys.stdout.write(f'  [EXEC] N{node_id} alcanzó Consenso BFT en: {payload}\n')
                sys.stdout.flush()
                break
    sys.stdout.write(f' [ PID {os.getpid()} ] Nodo {node_id} Terminado.\n')
    sys.stdout.flush()
if __name__ == '__main__':
    sys.stdout.write('❖ [ C5-DAEMON-CORE :: MULTIPROCESSING PBFT CLUSTER ] ❖\n\n')
    setup_ledger()
    queues = {i: multiprocessing.Queue() for i in range(N)}
    processes = []
    for i in range(N):
        is_byz = i == 2
        p = multiprocessing.Process(target=run_node, args=(i, queues, is_byz))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    sys.stdout.write('\n❖ [ AUDITORÍA DEL LEDGER MAESTRO (Últimas transacciones WAL) ] ❖\n')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT node_id, phase, payload FROM ipc_ledger ORDER BY id DESC LIMIT 6')
    for row in cursor.fetchall():
        sys.stdout.write(f'   Nodo {row[0]} | {row[1].ljust(12)} | {row[2]}\n')
    conn.close()
