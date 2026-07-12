import time
import zlib
from decimal import Decimal
import string
import hashlib
try:
    import strike_rs
except ImportError:
    print('\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m strike_rs no compilado o instalado en el venv.')
    exit(1)

def compute_kolmogorov_python(text_data: str) -> dict:
    if not text_data:
        return {'mdl': Decimal('0.0'), 'compressed_size': 0, 'raw_size': 0}
    raw_bytes = text_data.encode('utf-8')
    raw_size = len(raw_bytes)
    compressed = zlib.compress(raw_bytes, level=9)
    compressed_size = len(compressed)
    mdl = Decimal(compressed_size) / Decimal(raw_size) if raw_size > 0 else Decimal('0.0')
    return {'mdl': mdl, 'compressed_size': compressed_size, 'raw_size': raw_size, 'compression_ratio': Decimal(raw_size) / Decimal(compressed_size) if compressed_size > 0 else Decimal('1.0')}

def main():
    print('█▄ CORTEX RUST-STRIKE (PRUEBA DE CONCEPTO) █▄')
    print('Generando Payload Entrópico Estocástico (5MB)...')
    payload_size = 5 * 1024 * 1024
    base_hash = hashlib.blake2b(b'C5-REAL_STRIKE').digest()
    payload = (base_hash * (payload_size // len(base_hash) + 1))[:payload_size].hex()
    print('\n[1] Ejecutando: Python Nativo (zlib GIL-bound)')
    t0 = time.perf_counter()
    res_py = compute_kolmogorov_python(payload)
    t1 = time.perf_counter()
    py_time = t1 - t0
    print(f'    Tiempo: {py_time:.4f}s')
    print(f"    MDL: {res_py['mdl']}")
    print('\n[2] Ejecutando: Transmutación Rust-Strike (flate2 PyO3)')
    t0 = time.perf_counter()
    res_rs = strike_rs.compute_kolmogorov_approximation_rs(payload)
    t1 = time.perf_counter()
    rs_time = t1 - t0
    print(f'    Tiempo: {rs_time:.4f}s')
    print(f"    MDL: {res_rs['mdl']}")
    speedup = py_time / rs_time if rs_time > 0 else 0
    print(f'\n[!] RESULTADO DE APOPTOSIS TERMODINÁMICA:')
    print(f'    Aceleración empírica: {speedup:.2f}x Speedup')
    if speedup > 1.0:
        print('    STATUS: C5-REAL (Exergía Maximizada. GIL Bypassed).')
    else:
        print('    STATUS: C4-SIM (Anergía detectada).')
if __name__ == '__main__':
    main()
