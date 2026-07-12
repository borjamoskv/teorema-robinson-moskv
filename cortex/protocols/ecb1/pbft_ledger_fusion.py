import sys
import collections
import sqlite3
import os
N = 4
F = 1
DB_PATH = os.path.expanduser('~/.babylon60/cortex_bft_state.db')
L_PRE = '📢'
L_PRP = '🛡️'
L_CMT = '✅'
L_REP = '📤'
L_VWC = '🔄'
L_NWV = '👑'

class PBFTLedgerFusion:

    def __init__(self):
        self.view = 0
        self.logs = {i: [] for i in range(N)}
        self.setup_ledger()

    def setup_ledger(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, isolation_level=None)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('\n            CREATE TABLE IF NOT EXISTS pbft_ledger (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                view INTEGER,\n                phase TEXT,\n                node_id INTEGER,\n                payload TEXT,\n                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n            )\n        ')

    def write_ledger(self, phase, node_id, payload):
        self.conn.execute('\n            INSERT INTO pbft_ledger (view, phase, node_id, payload)\n            VALUES (?, ?, ?, ?)\n        ', (self.view, phase, node_id, payload))

    def get_primary(self):
        return self.view % N

    def run_consensus(self):
        primary = self.get_primary()
        sys.stdout.write(f'\n❖ [ VISTA ACTUAL: {self.view} | LÍDER: N{primary} ] ❖\n')
        payloads = ['📦🧠⚡', '📦🧠💀', '📦🧠🩸']
        target_idx = 0
        for target in range(N):
            if target == primary:
                continue
            payload = payloads[target_idx]
            target_idx += 1
            msg = f'{L_PRE}{payload}'
            self.logs[target].append((primary, msg))
            self.write_ledger('PRE-PREPARE', primary, msg)
        prepares = {i: [] for i in range(N)}
        for i in range(N):
            if i == primary:
                continue
            recv_pre = [m[1][1:] for m in self.logs[i] if m[1].startswith(L_PRE)]
            if not recv_pre:
                continue
            msg = f'{L_PRP}{recv_pre[0]}'
            for target in range(N):
                prepares[target].append((i, msg))
            self.write_ledger('PREPARE', i, msg)
        quorum_reached = False
        for i in range(N):
            if i == primary:
                continue
            counts = collections.Counter([m[1][1:] for m in prepares[i]])
            max_count = max(counts.values()) if counts else 0
            if max_count >= 2 * F:
                quorum_reached = True
        if not quorum_reached:
            new_view = self.view + 1
            new_primary = new_view % N
            view_changes = {i: [] for i in range(N)}
            for i in range(N):
                if i == primary:
                    continue
                msg = f'{L_VWC}v{new_view}'
                for target in range(N):
                    view_changes[target].append((i, msg))
                self.write_ledger('VIEW-CHANGE', i, msg)
            if len(view_changes[new_primary]) >= 2 * F:
                msg = f'{L_NWV}v{new_view}'
                self.write_ledger('NEW-VIEW', new_primary, msg)
                self.view = new_view
                return self.run_honest_consensus()
        return '❌ CONSENSUS_STALLED'

    def run_honest_consensus(self):
        primary = self.get_primary()
        sys.stdout.write(f'\n❖ [ NUEVA VISTA HONESTA: {self.view} | LÍDER: N{primary} ] ❖\n')
        msg = f'{L_PRE}📦🧠⚡'
        self.write_ledger('PRE-PREPARE', primary, msg)
        for i in range(N):
            if i == primary:
                continue
            self.write_ledger('PREPARE', i, f'{L_PRP}📦🧠⚡')
        for i in range(N):
            self.write_ledger('COMMIT', i, f'{L_CMT}📦🧠⚡')
        self.write_ledger('EXECUTED', primary, f'{L_REP}📦🧠⚡')
        return '✅ CONSENSUS_REACHED_AND_COMMITTED'

    def audit_ledger(self):
        sys.stdout.write('\n❖ [ AUDITORÍA DEL MASTER LEDGER (Últimos 10 registros) ] ❖\n')
        cursor = self.conn.execute('SELECT view, phase, node_id, payload FROM pbft_ledger ORDER BY id DESC LIMIT 10')
        rows = cursor.fetchall()
        for r in reversed(rows):
            sys.stdout.write(f'  [ View {r[0]} ] :: {r[1].ljust(12)} | Nodo {r[2]} | {r[3]}\n')
if __name__ == '__main__':
    sys.stdout.write('❖ [ C5-DAEMON-CORE :: PBFT VIEW CHANGE + CORTEX LEDGER ] ❖\n')
    engine = PBFTLedgerFusion()
    result = engine.run_consensus()
    sys.stdout.write(f'\n[ GLOBAL STATE ] -> {result}\n')
    engine.audit_ledger()
