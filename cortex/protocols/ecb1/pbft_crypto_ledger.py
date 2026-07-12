import sys
import collections
import sqlite3
import os
import hashlib
import hmac
import json
N = 4
F = 1
DB_PATH = os.path.expanduser('~/.babylon60/cortex_bft_state.db')
NODE_KEYS = {i: f'SECRET_KEY_NODO_{i}'.encode() for i in range(N)}
L_PRE = '📢'
L_PRP = '🛡️'
L_CMT = '✅'
L_REP = '📤'

def sign_payload(node_id, payload):
    return hmac.new(NODE_KEYS[node_id], payload.encode(), hashlib.sha256).hexdigest()

def verify_signature(node_id, payload, signature):
    expected = sign_payload(node_id, payload)
    return hmac.compare_digest(expected, signature)

class CryptoLedgerFusion:

    def __init__(self):
        self.view = 0
        self.last_hash = '0000000000000000000000000000000000000000000000000000000000000000'
        self.setup_ledger()

    def setup_ledger(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, isolation_level=None)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('\n            CREATE TABLE IF NOT EXISTS pbft_crypto_ledger (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                view INTEGER,\n                phase TEXT,\n                node_id INTEGER,\n                payload TEXT,\n                signature TEXT,\n                prev_hash TEXT UNIQUE,\n                block_hash TEXT UNIQUE,\n                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n            )\n        ')
        cur = self.conn.execute('SELECT block_hash FROM pbft_crypto_ledger ORDER BY id DESC LIMIT 1')
        row = cur.fetchone()
        if row:
            self.last_hash = row[0]

    def write_block(self, phase, node_id, payload, signature):
        if not verify_signature(node_id, payload, signature):
            raise ValueError(f'Firma criptográfica inválida para el Nodo {node_id}')
        block_data = f'{self.view}:{phase}:{node_id}:{payload}:{signature}:{self.last_hash}'
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        try:
            self.conn.execute('\n                INSERT INTO pbft_crypto_ledger (view, phase, node_id, payload, signature, prev_hash, block_hash)\n                VALUES (?, ?, ?, ?, ?, ?, ?)\n            ', (self.view, phase, node_id, payload, signature, self.last_hash, block_hash))
            self.last_hash = block_hash
            return block_hash
        except sqlite3.IntegrityError:
            raise ValueError('Integridad de Merkle comprometida: Prev_Hash duplicado (Fork detectado).')

    def run_crypto_consensus(self):
        primary = 0
        sys.stdout.write(f'❖ [ VISTA: {self.view} | LÍDER: N{primary} | INICIO DE BLOQUE CRIPTOGRÁFICO ] ❖\n\n')
        payload_base = '📦🧠⚡'
        msg = f'{L_PRE}{payload_base}'
        sig = sign_payload(primary, msg)
        self.write_block('PRE-PREPARE', primary, msg, sig)
        sys.stdout.write(f'  [ 1. PRE-PREPARE ] N{primary} firma -> {sig[:16]}...\n')
        sys.stdout.write('  [ 2. PREPARE ]\n')
        for i in range(N):
            if i == primary:
                continue
            msg_prp = f'{L_PRP}{payload_base}'
            sig_prp = sign_payload(i, msg_prp)
            b_hash = self.write_block('PREPARE', i, msg_prp, sig_prp)
            sys.stdout.write(f'    N{i} firma -> {sig_prp[:16]}... | BlockHash: {b_hash[:8]}\n')
        sys.stdout.write('  [ 3. COMMIT ]\n')
        for i in range(N):
            msg_cmt = f'{L_CMT}{payload_base}'
            sig_cmt = sign_payload(i, msg_cmt)
            b_hash = self.write_block('COMMIT', i, msg_cmt, sig_cmt)
            sys.stdout.write(f'    N{i} firma -> {sig_cmt[:16]}... | BlockHash: {b_hash[:8]}\n')
        sys.stdout.write('\n  [ 💀 ATAQUE CRIPTOGRÁFICO ] Nodo 2 forja payload falso y firma con llave incorrecta...\n')
        fake_msg = f'{L_CMT}📦🧠💀'
        fake_sig = hmac.new(b'CLAVE_FALSA', fake_msg.encode(), hashlib.sha256).hexdigest()
        try:
            self.write_block('COMMIT_ATTACK', 2, fake_msg, fake_sig)
        except ValueError as e:
            sys.stdout.write(f'    [ DENEGADO ] :: {e}\n')
        sys.stdout.write('\n  [ 4. EXECUTED ]\n')
        msg_rep = f'{L_REP}{payload_base}'
        sig_rep = sign_payload(primary, msg_rep)
        final_hash = self.write_block('EXECUTED', primary, msg_rep, sig_rep)
        sys.stdout.write(f'    Consenso cerrado en Hash: {final_hash}\n')
        return final_hash

    def audit_chain(self):
        sys.stdout.write('\n❖ [ AUDITORÍA MERKLE CHAIN (HASH CHAIN) ] ❖\n')
        cursor = self.conn.execute('SELECT phase, node_id, block_hash, prev_hash FROM pbft_crypto_ledger ORDER BY id DESC LIMIT 5')
        rows = cursor.fetchall()
        for r in reversed(rows):
            sys.stdout.write(f'  [{r[0].ljust(11)} N{r[1]}] :: Hash: {r[2][:16]}... <- Prev: {r[3][:16]}...\n')
if __name__ == '__main__':
    sys.stdout.write('❖ [ C5-DAEMON-CORE :: CRIPTOGRAFÍA + LEDGER INMUTABLE ] ❖\n\n')
    engine = CryptoLedgerFusion()
    final_hash = engine.run_crypto_consensus()
    engine.audit_chain()
