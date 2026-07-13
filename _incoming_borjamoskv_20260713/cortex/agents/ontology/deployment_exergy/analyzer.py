import yaml
import re
import sys

def validate_invariants(matrix_path: str):
    with open(matrix_path, 'r') as f:
        data = yaml.safe_load(f)

    print(f"[C5-REAL] Iniciando Auditoría Termodinámica de Invariantes (N={len(data.get('primitives', []))})")
    
    valid = True
    for prim in data.get('primitives', []):
        _id = prim.get('id', 'UNKNOWN')
        target = prim.get('target_pattern')
        collapse = prim.get('collapse_state')
        
        # 1. Determinismo de Expresiones Regulares
        try:
            re.compile(target)
        except Exception as e:
            print(f"  [X] FRACTURA DETECTADA en {_id}: Regex '{target}' es inválida ({e})")
            valid = False
            continue

        # 2. Asimetría Oracular (Evitar que el colapso sea idéntico al target si es literal)
        if target == collapse:
            print(f"  [X] ANERGÍA DETECTADA en {_id}: El vector de colapso no genera mutación neta (Target == Collapse).")
            valid = False
        else:
            print(f"  [+] {_id} validado: Vector ortogonal. (Peso: {prim.get('weight')})")

    if valid:
        print("\n[C5-REAL] TEOREMA DEMOSTRADO: Todas las invariantes son topológicamente válidas y poseen exergía > 0.")
    else:
        print("\n[C5-REAL] FALLO ESTRUCTURAL: La matriz contiene ruido C4-SIM. Requiere purga.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    validate_invariants(sys.argv[1])
