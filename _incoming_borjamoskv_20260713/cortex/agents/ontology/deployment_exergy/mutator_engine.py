import yaml
import sys
import os
import re
import hashlib
from typing import Dict, Any

class OuroborosMutator:
    def __init__(self, matrix_path: str):
        with open(matrix_path, "r") as f:
            self.matrix = yaml.safe_load(f)
        self.primitives = self.matrix.get("primitives", [])
        
    def _crypto_hash(self, payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()[:8]

    def _apply_mutation(self, filepath: str, primitive: Dict[str, Any]) -> bool:
        if not os.path.exists(filepath):
            return False

        with open(filepath, "r") as f:
            content = f.read()

        target_pattern = primitive.get("target_pattern")
        collapse_state = primitive.get("collapse_state")
        
        if not target_pattern or not collapse_state:
            return False

        if re.search(target_pattern, content):
            new_content = re.sub(target_pattern, collapse_state, content)
            if new_content != content:
                with open(filepath, "w") as f:
                    f.write(new_content)
                print(f"[C5-REAL] Mutación ejecutada en {filepath}: {primitive['id']} -> {self._crypto_hash(new_content)}")
                return True
        return False

    def scan_and_mutate(self, target_dir: str):
        print(f"[C5-REAL] Iniciando Ouroboros Mutator en {target_dir} (N={len(self.primitives)} primitivas)")
        mutations_applied = 0
        for root, _, files in os.walk(target_dir):
            if "node_modules" in root or ".git" in root:
                continue
            for file in files:
                filepath = os.path.join(root, file)
                for primitive in self.primitives:
                    if primitive.get("file_regex") and re.match(primitive["file_regex"], file):
                        if self._apply_mutation(filepath, primitive):
                            mutations_applied += 1
        
        if mutations_applied > 0:
            print(f"[C5-REAL] Exergía Maximizada. Nodos colapsados: {mutations_applied}.")
            # Autopoiesis: El sistema puede modificar su propia matriz incrementando pesos
            self._evolve_matrix()
        else:
            print("[C5-REAL] Entropía bajo control. Invariantes preservadas.")

    def _evolve_matrix(self):
        """El sistema muta sus propios pesos termodinámicos basándose en hits empíricos."""
        for p in self.primitives:
            p['weight'] = p.get('weight', 1.0) + 0.1
        with open(self.matrix.get('path', 'matrix.yaml'), "w") as f:
            yaml.dump(self.matrix, f, allow_unicode=True)
        print("[C5-REAL] Matriz de Invariantes Mutada (Evolución de Pesos Ouroboros).")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 mutator_engine.py <matrix.yaml> <target_dir>")
        sys.exit(1)
        
    engine = OuroborosMutator(sys.argv[1])
    engine.matrix['path'] = sys.argv[1] # Inject runtime path for evolution
    engine.scan_and_mutate(sys.argv[2])
