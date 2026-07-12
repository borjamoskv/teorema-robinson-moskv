"""
C5-REAL OSINT DAO Verification Matrix
Enforces [L16: Τ5] - Compilación y ejecución bajo presión (pytest).
Fail-fast: Crash over catch [L12: Κ1].
"""
import pytest
import os

from cortex.agents.ontology.osint_dao import OSINTOntologyAccessor, DB_PATH








@pytest.mark.asyncio
async def test_dao_initialization():
    """Valida la inyección de la ruta física."""
    assert os.path.exists(DB_PATH), "La base de datos física no existe, fallo en [INV_STATE_02]."
    accessor = OSINTOntologyAccessor()
    assert accessor.db_path == DB_PATH

@pytest.mark.asyncio
async def test_get_all_invariants():
    """Valida la consistencia estructural BFT de Invariantes."""
    accessor = OSINTOntologyAccessor()
    invariants = await accessor.get_all_invariants()
    assert len(invariants) >= 3, "El ledger debe contener al menos 3 Invariantes OSINT BFT."
    assert any("INV_OSINT_01" in inv["code"] for inv in invariants), "Falta invariante core INV_OSINT_01."

@pytest.mark.asyncio
async def test_get_primitives_by_domain_socint():
    """Valida la extracción de SOCINT aplicando [MUTEX_HALTING_BOUND]."""
    accessor = OSINTOntologyAccessor()
    primitives = await accessor.get_primitives_by_domain("SOCINT")
    assert len(primitives) > 0, "No se encontraron primitivas SOCINT."
    assert len(primitives) <= 120, "El Halting Bound N=120 ha sido vulnerado."

@pytest.mark.asyncio
async def test_fail_fast_unknown_domain():
    """Valida la cláusula [L12: Κ1] (Crash over catch) para dominios entrópicos."""
    accessor = OSINTOntologyAccessor()
    with pytest.raises(RuntimeError) as exc_info:
        await accessor.get_primitives_by_domain("DOMINIO_INEXISTENTE_C4_SIM")
    assert "Dominio OSINT no encontrado o vacío" in str(exc_info.value)
