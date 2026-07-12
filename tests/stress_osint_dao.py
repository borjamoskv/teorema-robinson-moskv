import asyncio
import time
import sys
sys.path.append('$CORTEX_ROOT/30_BABYLON-60')
from cortex.agents.ontology.osint_dao import OSINTOntologyAccessor

async def worker(accessor: OSINTOntologyAccessor, worker_id: int) -> int:
    try:
        res = await accessor.get_primitives_by_domain('SOCINT')
        return len(res)
    except RuntimeError as e:
        return 0

async def stress_test() -> None:
    accessor = OSINTOntologyAccessor()
    start_time = time.time()
    total_successes = 0
    batch_size = 500
    for _ in range(20):
        tasks = [worker(accessor, i) for i in range(batch_size)]
        results = await asyncio.gather(*tasks)
        total_successes += sum((1 for r in results if r > 0))
    end_time = time.time()
    elapsed = end_time - start_time
    failures = 10000 - total_successes
    print('STRESS_TEST_COLLAPSE')
    print('Total_Requests: 10000')
    print(f'Success: {total_successes}')
    print(f'Failures: {failures}')
    print(f'Elapsed_Time: {elapsed:.3f}s')
    print(f'Throughput: {10000 / elapsed:.2f}_req/s')
    assert total_successes == 10000, 'Fallo termodinámico en stress test (Anergía).'
if __name__ == '__main__':
    asyncio.run(stress_test())
