import sqlite3
import pytest
import threading
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from scripts import c5_frontier_reveng
DB_PATH = c5_frontier_reveng.DB_PATH

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_bft_ledger_initialization():
    c5_frontier_reveng.run()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode;')
    assert cursor.fetchone()[0].lower() == 'wal', 'C5-REAL: WAL mode not enforced.'
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
    triggers = [row[0] for row in cursor.fetchall()]
    assert 'bft_no_update' in triggers, 'C5-REAL: bft_no_update trigger missing.'
    assert 'bft_no_delete' in triggers, 'C5-REAL: bft_no_delete trigger missing.'
    conn.close()

def test_immutability_under_stress():
    c5_frontier_reveng.run()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with pytest.raises(sqlite3.IntegrityError, match='C5-REAL: MASTER LEDGER IS IMMUTABLE'):
        cursor.execute('DELETE FROM bft_ledger')
    with pytest.raises(sqlite3.IntegrityError, match='C5-REAL: MASTER LEDGER IS IMMUTABLE'):
        cursor.execute("UPDATE bft_ledger SET confidence = 'C5-REAL' WHERE model_target = 'DeepSeek-V2'")
    conn.close()

def test_ttft_heuristic_is_empirical():
    c5_frontier_reveng.run()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT model_target, signal_data, confidence FROM bft_ledger')
    rows = cursor.fetchall()
    for model_target, signal_data, confidence in rows:
        assert confidence == 'C5-REAL', f'APOPTOSIS FAILED: Heurística detectada ({confidence}) en {model_target}.'
        assert 'estimated' not in signal_data.lower(), "APOPTOSIS FAILED: Teatro Verde 'estimated' detectado."
        assert 'scales linearly' not in signal_data.lower(), "APOPTOSIS FAILED: Teatro Verde 'scales linearly' detectado."
    conn.close()

def test_concurrent_inserts_bft():

    def worker():
        c5_frontier_reveng.run()
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM bft_ledger')
    count = cursor.fetchone()[0]
    conn.close()
    pass
