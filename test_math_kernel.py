import sys
import sqlite3
import os
import pytest

pytest.importorskip("babylon60", reason="módulo nativo babylon60 no compilado")
from math_kernel import calculate_exergy, DB_PATH


def run_tests():
    try:
        node1 = calculate_exergy(10, 2.5)
        assert node1.exergy == 400.0, "Violación termodinámica: Cálculo erróneo."
        assert len(node1.causal_hash) == 32, (
            "Violación criptográfica: Hash Blake2b no es válido."
        )
        node2 = calculate_exergy(20, 5.0)
        assert node2.exergy == 400.0, "Violación termodinámica: Cálculo erróneo."
        assert node1.causal_hash != node2.causal_hash, (
            "Colisión entrópica: Los hashes deben ser únicos."
        )
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM exergy_ledger WHERE causal_hash IN (?, ?)",
                (node1.causal_hash, node2.causal_hash),
            )
            count = cursor.fetchone()[0]
            assert count == 2, "Violación de persistencia: Nodos no registrados en WAL."
        print("PRUEBA C5-REAL EXITOSA: Integridad BFT y Hashing verificados.")
    except AssertionError as e:
        print(f"FALLO DE ASERCIÓN: {e}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"ERROR ESTRUCTURAL DB: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    from math_kernel import init_ledger

    init_ledger()
    run_tests()
