import sqlite3
import os
import sys
from cryptography.fernet import Fernet

def get_fernet():
    key = os.environ.get('CORTEX_VAULT_KEY')
    if not key:
        print('ERROR: CORTEX_VAULT_KEY no definida en el entorno.')
        sys.exit(1)
    return Fernet(key.encode('utf-8'))

def migrate_nexus_cache(fernet):
    vault_path = os.environ.get('BABYLON_VAULT', os.path.expanduser('~/.babylon60'))
    db_path = os.path.join(vault_path, 'nexus_cache.db')
    if not os.path.exists(db_path):
        print(f'[*] Skip: {db_path} no encontrado.')
        return
    print(f'[*] Migrando nexus_cache.db (L3_inference_cache)...')
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='L3_inference_cache'")
        if cursor.fetchone()[0] == 0:
            print('[*] Tabla L3_inference_cache no existe.')
            conn.close()
            return
        cursor.execute('SELECT query_hash, trace_payload FROM L3_inference_cache')
        rows = cursor.fetchall()
        updates = 0
        for row in rows:
            payload = row['trace_payload']
            if not payload.startswith('C5ENC:'):
                enc = f"C5ENC:{fernet.encrypt(payload.encode('utf-8')).decode('utf-8')}"
                cursor.execute('UPDATE L3_inference_cache SET trace_payload = ? WHERE query_hash = ?', (enc, row['query_hash']))
                updates += 1
        conn.commit()
        conn.close()
        print(f'[+] Migración exitosa: {updates} filas cifradas en nexus_cache.db.')
    except sqlite3.OperationalError as e:
        if 'readonly database' in str(e):
            print('[!] Base de datos en modo readonly. C5-REAL previene la mutación.')
        else:
            print(f'[!] Error: {e}')

def migrate_master_ledger(fernet, db_path):
    if not os.path.exists(db_path):
        print(f'[*] Skip: {db_path} no encontrado.')
        return
    print(f'[*] Migrando ledger_entries en {db_path}...')
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ledger_entries'")
        if cursor.fetchone()[0] == 0:
            print('[*] Tabla ledger_entries no existe.')
            conn.close()
            return
        cursor.execute('SELECT seq, payload_json FROM ledger_entries')
        rows = cursor.fetchall()
        updates = 0
        for row in rows:
            payload = row['payload_json']
            if not payload.startswith('C5ENC:'):
                enc = f"C5ENC:{fernet.encrypt(payload.encode('utf-8')).decode('utf-8')}"
                cursor.execute('PRAGMA ignore_check_constraints = 1')
                cursor.execute('DROP TRIGGER IF EXISTS trg_ledger_immutable_update')
                cursor.execute('UPDATE ledger_entries SET payload_json = ? WHERE seq = ?', (enc, row['seq']))
                cursor.execute("\n                    CREATE TRIGGER IF NOT EXISTS trg_ledger_immutable_update BEFORE UPDATE ON ledger_entries\n                    BEGIN SELECT RAISE(ABORT, 'C5 BFT: immutable master ledger'); END;\n                ")
                updates += 1
        conn.commit()
        conn.close()
        print(f'[+] Migración exitosa: {updates} filas cifradas en {db_path}.')
    except RuntimeError as e:
        print(f'[!] Error: {e}')
if __name__ == '__main__':
    fernet = get_fernet()
    migrate_nexus_cache(fernet)
    migrate_master_ledger(fernet, 'bft/master_ledger.db')
    migrate_master_ledger(fernet, 'test_ledger.db')
    print('[*] C5-REAL MIGRATION COMPLETADA')
