"""
C5-REAL Hardware Bijective Footprint Validator
Enforces structural rigor and mapping consistency for the Bio-Silicon Isomorphisms.
Fail-fast: Crash over catch [L12: K1].
"""

import os
import yaml
import pytest
from pathlib import Path

# Repo-relative: portable entre máquinas y CI (antes hardcodeado a 30_BABYLON-60).
YAML_PATH = str(Path(__file__).resolve().parents[1]
                / "cortex" / "ontology" / "huella_biyectiva_hardware.yaml")

def test_yaml_exists():
    """Valida la existencia física del archivo de ontología."""
    assert os.path.exists(YAML_PATH), f"El archivo YAML no existe en {YAML_PATH}"

def test_yaml_structure():
    """Valida la integridad de los campos obligatorios del estándar C5-REAL."""
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    assert data is not None, "El YAML está vacío o corrupto."
    
    # Nodos obligatorios según SKILL.md
    required_keys = [
        "Claim",
        "Auditoria_Epistemica",
        "Topologia_Isomorfica_Borja_Moskv",
        "Estructura_Resolucion_Atomica",
        "Firma_Ejecucion"
    ]
    
    for key in required_keys:
        assert key in data, f"Falta el nodo obligatorio: {key}"

def test_isomorphisms_density():
    """Valida la densidad termodinámica de los mapeos isomórficos (mínimo 18)."""
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    mappings = data.get("Topologia_Isomorfica_Borja_Moskv", [])
    assert isinstance(mappings, list), "Topologia_Isomorfica_Borja_Moskv debe ser una lista."
    assert len(mappings) >= 18, f"Se esperaban al menos 18 mapeos de huella hardware, se encontraron {len(mappings)}"
    
    for i, mapping in enumerate(mappings):
        assert "Vector_Origen" in mapping, f"Falta Vector_Origen en el mapeo índice {i}"
        assert "Vector_Destino" in mapping, f"Falta Vector_Destino en el mapeo índice {i}"
        assert "Invariante" in mapping, f"Falta Invariante en el mapeo índice {i}"
        assert "Resolucion_C5" in mapping, f"Falta Resolucion_C5 en el mapeo índice {i}"

def test_cryptographic_signature():
    """Valida la firma de ejecución C5 y la atribución causal."""
    with open(YAML_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    signature = data.get("Firma_Ejecucion", {})
    assert signature.get("Autor") == "borjamoskv", "Autor incorrecto o corrupto."
    assert signature.get("Kernel") == "MOSKV-1 APEX", "Kernel incorrecto o corrupto."
    assert "[CORTEX-TAINT:" in signature.get("Atribucion", ""), "Falta la firma CORTEX-TAINT en atribución."
    assert signature.get("ZKP_Assertion") is not None, "Falta la declaración zkProof/BLAKE3."
