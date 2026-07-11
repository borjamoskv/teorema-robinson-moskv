"""
C5-REAL OSINT DAO Stress Matrix
Enforces [L10: R10] - Concurrencia Confiable de DB
Ejecuta 10,000 aserciones concurrentes contra el Ledger OSINT.
"""
import asyncio
import time
import sys

# Ensure module path is accessible
sys.path.append("/Users/borjafernandezangulo/30_BABYLON-60")

from cortex.agents.ontology.osint_dao import OSINTOntologyAccessor

async def worker(accessor: OSINTOntologyAccessor, worker_id: int) -> int:
    # Simulates high concurrent IO read
    try:
        res = await accessor.get_primitives_by_domain("SOCINT")
        return len(res)
    except Exception as e:
        return 0

async def stress_test() -> None:
    accessor = OSINTOntologyAccessor()
    start_time = time.time()
    
    # Batching to prevent max file descriptor limits in macOS (ulimit -n is often 256 or 1024)
    # We will do 100 batches of 100 requests (10,000 total)
    total_successes = 0
    batch_size = 500
    
    for _ in range(20):
        tasks = [worker(accessor, i) for i in range(batch_size)]
        results = await asyncio.gather(*tasks)
        total_successes += sum(1 for r in results if r > 0)
        
    end_time = time.time()
    elapsed = end_time - start_time
    failures = 10000 - total_successes
    
    print("STRESS_TEST_COLLAPSE")
    print("Total_Requests: 10000")
    print(f"Success: {total_successes}")
    print(f"Failures: {failures}")
    print(f"Elapsed_Time: {elapsed:.3f}s")
    print(f"Throughput: {10000 / elapsed:.2f}_req/s")
    
    assert total_successes == 10000, "Fallo termodinámico en stress test (Anergía)."

if __name__ == "__main__":
    asyncio.run(stress_test())
