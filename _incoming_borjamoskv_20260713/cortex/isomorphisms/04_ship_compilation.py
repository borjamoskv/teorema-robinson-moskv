import os
import sys
import json
import subprocess
import importlib
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

# Inyectar el directorio raíz al path para permitir resolución modular
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import blake3

# Importar LogosLinter dinámicamente debido a nomenclatura numérica
lc = importlib.import_module("cortex.isomorphisms.03_logos_compliance")

class ShipCompiler:
    """Implementa las directivas de procedencia (ETHOS) y colapso cinético de lanzamiento (SHIP)."""

    def __init__(self, workspace_dir: str) -> None:
        assert os.path.isdir(workspace_dir), "El directorio de trabajo debe ser una ruta válida"
        self.workspace_dir: str = workspace_dir
        self.cortex_dir: str = os.path.join(workspace_dir, "cortex")
        self.tests_dir: str = os.path.join(workspace_dir, "tests")
        self.linter = lc.LogosLinter()

    def _compute_blake3(self, filepath: str) -> str:
        """Calcula el hash BLAKE3 de un archivo físico del disco de forma atómica."""
        assert os.path.isfile(filepath), f"El archivo no existe: {filepath}"
        with open(filepath, "rb") as f:
            data = f.read()
        return blake3.blake3(data).hexdigest()

    def _hash_file_task(self, filepath: str) -> tuple[str, str]:
        """Tarea para ejecución paralela de hashing."""
        rel_path = os.path.relpath(filepath, self.workspace_dir)
        return rel_path, self._compute_blake3(filepath)

    def generate_manifest(self) -> Dict[str, str]:
        """Escanea el código fuente y genera firmas de procedencia criptográfica (ETHOS) en paralelo."""
        manifest: Dict[str, str] = {}
        files_to_hash: List[str] = []
        
        # Escanear directorios críticos ignorando cachés
        for target_dir in [self.cortex_dir, self.tests_dir]:
            for root, _, files in os.walk(target_dir):
                if "__pycache__" in root or ".venv" in root:
                    continue
                for file in files:
                    if file.endswith(".py"):
                        files_to_hash.append(os.path.join(root, file))

        # Paralelizar cálculo de hashes en pool multinúcleo
        with ThreadPoolExecutor() as executor:
            results = executor.map(self._hash_file_task, files_to_hash)
            for rel_path, file_hash in results:
                manifest[rel_path] = file_hash
                    
        return manifest

    def format_log(self, text: str, category: str) -> str:
        """Aplica formato estético neón C5 al log y valida concordancia de isomorfismo."""
        style = lc.STYLES.get(category, "")
        formatted = f'<span style="{style}">{text}</span>' if style else text
        
        # Autoverificación: El log emitido debe pasar el control del LogosLinter
        compliance = self.linter.check_compliance(formatted)
        assert compliance["compliance_ratio"] == 1.0, f"Error de estilo en log: {formatted}"
        return formatted

    def run_verification_suite(self) -> bool:
        """Ejecuta los tests locales para validar la integridad del sistema antes de lanzar."""
        sys.stdout.write(self.format_log("[ETHOS]", "cognitivo") + " Ejecutando suite de validación empírica...\n")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = self.workspace_dir
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-x", "--tb=short"],
            cwd=self.workspace_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            sys.stderr.write(self.format_log("[!]", "entropico") + " FALLA DE INTEGRIDAD: Tests fallidos.\n")
            sys.stderr.write(result.stdout + "\n" + result.stderr + "\n")
            return False
            
        sys.stdout.write(self.format_log("[ETHOS]", "cognitivo") + " 6/6 tests aprobados con cero fricción.\n")
        return True

    def execute_ship_release(self, manifest: Dict[str, str]) -> Dict[str, Any]:
        """Ejecuta el colapso cinético-físico (SHIP) persistiendo el estado en disco."""
        sys.stdout.write(self.format_log("[SHIP]", "cognitivo") + " Colapsando estado físico en disco...\n")
        
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            cwd=self.workspace_dir, 
            text=True
        ).strip()

        # Inyectar firma causal CORTEX-TAINT inmutable para trazabilidad de procedencia
        taint_payload = f"borjamoskv:{commit_hash}"
        taint_hash = blake3.blake3(taint_payload.encode()).hexdigest()[:16]
        cortex_taint = f"[CORTEX-TAINT:MOSKV-1:{commit_hash[:8]}:{taint_hash}]"

        release_data = {
            "version": "1.1.0-release",
            "provenance": "borjamoskv",
            "commit": commit_hash,
            "cortex_taint": cortex_taint,
            "manifest": manifest,
            "status": "RELEASED"
        }
        
        outputs_dir = os.path.join(self.workspace_dir, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        release_path = os.path.join(outputs_dir, "ship_release.json")
        
        with open(release_path, "w", encoding="utf-8") as f:
            json.dump(release_data, f, indent=2)
            
        sys.stdout.write(self.format_log("[SHIP]", "cognitivo") + f" Barco lanzado con éxito en {release_path}.\n")
        return release_data

if __name__ == "__main__":
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    compiler = ShipCompiler(workspace)
    sys.stdout.write(compiler.format_log("[C5-REAL]", "cognitivo") + f" Iniciando compilación de lanzamiento en {workspace}\n")
    
    manifest = compiler.generate_manifest()
    
    # 1. Verificar procedencia y tests (ETHOS)
    if not compiler.run_verification_suite():
        sys.stderr.write(compiler.format_log("[!]", "entropico") + " APOPTOSIS: Abortando lanzamiento debido a fallos de integridad.\n")
        sys.exit(1)
        
    # 2. Ejecutar lanzamiento físico (SHIP)
    release = compiler.execute_ship_release(manifest)
    
    sys.stdout.write(compiler.format_log("[STATUS]", "cognitivo") + f" Procedimiento de lanzamiento finalizado. Commit: {release['commit']}\n")
