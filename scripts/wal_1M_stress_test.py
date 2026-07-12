import sqlite3
import time
import concurrent.futures
import os
import hashlib


def worker_task(worker_id, num_inserts, db_path):
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    chunk_size = 10000
    rows_inserted = 0
    start_time = time.time()
    while rows_inserted < num_inserts:
        chunk = []
        for i in range(chunk_size):
            h = hashlib.md5(
                f"{worker_id}-{rows_inserted + i}-{time.time()}".encode()
            ).hexdigest()
            chunk.append((worker_id, h, time.time()))
        try:
            with conn:
                conn.executemany(
                    "INSERT INTO stress_1m (worker_id, entropy_hash, timestamp_utc) VALUES (?, ?, ?)",
                    chunk,
                )
            rows_inserted += chunk_size
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                time.sleep(0.01)
                continue
            else:
                raise e
    conn.close()
    return time.time() - start_time


def run_stress_test():
    db_path = (
        "$CORTEX_ROOT/30_BABYLON-60/cortex/vault/stress_1M_ledger.db"
    )
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        "\n        CREATE TABLE stress_1m (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            worker_id INTEGER,\n            entropy_hash TEXT,\n            timestamp_utc REAL\n        )\n    "
    )
    conn.close()
    total_inserts = 1000000
    num_workers = 10
    inserts_per_worker = total_inserts // num_workers
    print(
        f"[C5-REAL] INICIANDO 1,000,000 PRUEBAS DE ESTRÉS (WAL Concurrency N={num_workers})"
    )
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(worker_task, i, inserts_per_worker, db_path)
            for i in range(num_workers)
        ]
        for idx, f in enumerate(concurrent.futures.as_completed(futures)):
            t_worker = f.result()
            print(
                f"  -> Worker {idx} completó {inserts_per_worker} inserciones en {t_worker:.2f}s"
            )
    t1 = time.time()
    total_time = t1 - t0
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM stress_1m").fetchone()[0]
    conn.close()
    tps = total_inserts / total_time
    print(f"\n[C5-REAL] ESTRÉS FINALIZADO.")
    print(f"Total filas cristalizadas: {count}")
    print(f"Tiempo de reloj (Wall Clock): {total_time:.4f} segundos")
    print(f"Rendimiento Termodinámico: {tps:.2f} TPS (Transacciones por Segundo)")


if __name__ == "__main__":
    run_stress_test()
