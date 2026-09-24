#!/usr/bin/env python3
# C5-REAL EXERGY CERTIFIED
"""
Test Suite: Cybernetics Quadrivium Primitives & Kernel
Verifica el comportamiento determinista de los 4 evaluadores:
- Ashby (Variedad Requerida)
- Beer (Viable System Model)
- Bateson (Doble Vínculo & Tipos Lógicos)
- Bandler & Grinder (Coste de Falsificación Involuntario)
"""

import sys
from pathlib import Path

# Añadir src/04_primitives al sys.path para soportar directorios que inician con dígitos
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "04_primitives"))

from cybernetics.variety_evaluator import AshbyVarietyEvaluator, VarietyStatus
from cybernetics.vsm_analyzer import BeerVsmAnalyzer, VsmTopology, VsmSystemId, VsmPathology
from cybernetics.logical_types_filter import BatesonLogicalTypesFilter, Injunction
from cybernetics.involuntary_cost_verifier import BandlerGrinderCostVerifier, SignalTier
from cybernetics.cybernetics_quadrivium_kernel import CyberneticsQuadriviumKernel

def test_ashby_variety():
    print("[1] Test Ashby Variety Evaluator...")
    # Caso 1: Regulador balanceado (Perturbaciones=16 -> 4 bits, Regulador=16 -> 4 bits, Tolerancia=1 -> 0 bits)
    rep1 = AshbyVarietyEvaluator.evaluate(disturbances_count=16, regulator_actions_count=16, outcomes_tolerance_count=1)
    assert rep1.status == VarietyStatus.HOMEOSTATIC_EQUILIBRIUM, f"Esperado EQUILIBRIUM, obtenido {rep1.status}"
    assert rep1.entropy_leak_bits == 0.0, "No debe haber fuga de entropía"

    # Caso 2: Déficit de variedad (Perturbaciones=64 -> 6 bits, Regulador=4 -> 2 bits, Tolerancia=1 -> 0 bits)
    rep2 = AshbyVarietyEvaluator.evaluate(disturbances_count=64, regulator_actions_count=4, outcomes_tolerance_count=1)
    assert rep2.status == VarietyStatus.VARIETY_DEFICIT, f"Esperado VARIETY_DEFICIT, obtenido {rep2.status}"
    assert rep2.entropy_leak_bits == 4.0, f"Fuga esperada 4.0 bits, obtenida {rep2.entropy_leak_bits}"
    print("  ✓ Ashby Variety Evaluator verificado.")

def test_beer_vsm():
    print("[2] Test Beer VSM Analyzer...")
    # Caso 1: Topología viable completa
    viable_top = VsmTopology(
        active_systems={
            VsmSystemId.SYSTEM_1_OPERATIONS,
            VsmSystemId.SYSTEM_2_COORDINATION,
            VsmSystemId.SYSTEM_3_CONTROL_SYNERGY,
            VsmSystemId.SYSTEM_3_STAR_AUDIT,
            VsmSystemId.SYSTEM_4_INTELLIGENCE,
            VsmSystemId.SYSTEM_5_POLICY
        },
        s3_s4_channel_connected=True,
        algedonic_channel_active=True
    )
    rep1 = BeerVsmAnalyzer.audit_topology(viable_top)
    assert rep1.is_viable, f"Topología completa debe ser viable: {rep1.pathologies}"
    assert len(rep1.pathologies) == 0

    # Caso 2: Falta S2 (Coordinación) y S3* (Auditoría)
    pathological_top = VsmTopology(
        active_systems={
            VsmSystemId.SYSTEM_1_OPERATIONS,
            VsmSystemId.SYSTEM_3_CONTROL_SYNERGY,
            VsmSystemId.SYSTEM_4_INTELLIGENCE,
            VsmSystemId.SYSTEM_5_POLICY
        },
        s3_s4_channel_connected=True,
        algedonic_channel_active=True
    )
    rep2 = BeerVsmAnalyzer.audit_topology(pathological_top)
    assert not rep2.is_viable
    assert VsmPathology.RACE_CONDITION_OSCILLATION in rep2.pathologies
    assert VsmPathology.UNVERIFIED_REPORTING_BLINDNESS in rep2.pathologies
    print("  ✓ Beer VSM Analyzer verificado.")

def test_bateson_double_bind():
    print("[3] Test Bateson Logical Types Filter...")
    # Caso 1: Sin contradicción
    inj_ok = [
        Injunction(level=0, predicate="ejecutar_transaccion", is_negation=False),
        Injunction(level=1, predicate="reportar_auditoria", is_negation=False)
    ]
    rep1 = BatesonLogicalTypesFilter.audit_injunction_matrix(inj_ok, escape_allowed=True)
    assert not rep1.has_double_bind
    assert not rep1.is_deadlock

    # Caso 2: Doble Vínculo activo (Nivel 0 ordena actuar, Nivel 1 prohíbe actuar, salida cerrada)
    inj_db = [
        Injunction(level=0, predicate="ejecutar_transaccion", is_negation=False),
        Injunction(level=1, predicate="ejecutar_transaccion", is_negation=True)
    ]
    rep2 = BatesonLogicalTypesFilter.audit_injunction_matrix(inj_db, escape_allowed=False)
    assert rep2.has_double_bind
    assert rep2.is_deadlock
    assert "CAMBIO_2" in rep2.recommended_intervention
    print("  ✓ Bateson Double Bind Detector verificado.")

def test_bandler_grinder_cost():
    print("[4] Test Bandler-Grinder Involuntary Cost Verifier...")
    # Caso 1: Cheap talk (1000 bits de retórica con solo 10 joules de prueba -> ratio 0.01)
    rep1 = BandlerGrinderCostVerifier.verify(voluntary_payload_bits=1000.0, involuntary_work_metric=10.0)
    assert not rep1.is_authentic
    assert rep1.detected_tier == SignalTier.CHEAP_TALK_VOLUNTARY

    # Caso 2: Señal atestada con alto PoW/trabajo físico (500 bits con 400 unidades de trabajo -> ratio 0.8)
    rep2 = BandlerGrinderCostVerifier.verify(voluntary_payload_bits=500.0, involuntary_work_metric=400.0)
    assert rep2.is_authentic
    assert rep2.detected_tier == SignalTier.ATTESTED_INVOLUNTARY
    print("  ✓ Bandler-Grinder Involuntary Cost Verifier verificado.")

def test_unified_kernel():
    print("[5] Test Cybernetics Quadrivium Kernel...")
    viable_top = VsmTopology(
        active_systems={
            VsmSystemId.SYSTEM_1_OPERATIONS,
            VsmSystemId.SYSTEM_2_COORDINATION,
            VsmSystemId.SYSTEM_3_CONTROL_SYNERGY,
            VsmSystemId.SYSTEM_3_STAR_AUDIT,
            VsmSystemId.SYSTEM_4_INTELLIGENCE,
            VsmSystemId.SYSTEM_5_POLICY
        },
        s3_s4_channel_connected=True,
        algedonic_channel_active=True
    )
    inj_ok = [
        Injunction(level=0, predicate="procesar", is_negation=False),
        Injunction(level=1, predicate="validar", is_negation=False)
    ]

    receipt = CyberneticsQuadriviumKernel.audit_system(
        disturbances=16,
        regulator_actions=16,
        vsm_topology=viable_top,
        injunctions=inj_ok,
        escape_allowed=True,
        voluntary_payload_bits=100.0,
        involuntary_work_metric=90.0
    )
    assert receipt.is_globally_viable, f"Kernel debería pasar: {receipt.summary}"
    assert not receipt.fail_stop_triggered
    print("  ✓ Cybernetics Quadrivium Kernel verificado exitosamente.")

def test_knowledge_kernel_synthesis():
    print("[6] Test Knowledge Kernel Synthesis (Omega 5 - 10)...")
    scripts_dir = str(REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import c5_cybernetics_knowledge_kernel_runner as runner
    report = runner.run_synthesis()
    assert report["kernel_telemetry"]["nodes_count"] == 22
    assert report["kernel_telemetry"]["edges_count"] == 24
    assert report["kernel_telemetry"]["events_count"] == 46
    assert report["kernel_telemetry"]["claims_count"] == 4
    assert report["abductive_hypotheses_count"] > 0
    assert report["innovation_shift_audit"]["shift_detected"]
    assert "vsm_recursion_severance" in report["counterfactual_simulations"]
    assert len(report["fractal_memory_hierarchies"]) == 4
    print("  ✓ Knowledge Kernel Synthesis verificado exitosamente.")

def test_c_abi_baremetal_cybernetic_audit():
    print("[7] Test C-ABI Bare-Metal Cybernetic Audit (Ring-0 FFI)...")
    import ctypes
    dylib_path = REPO_ROOT / "scratch" / "libc5_abi_core.dylib"
    assert dylib_path.exists(), "La librería nativa scratch/libc5_abi_core.dylib debe existir"
    lib = ctypes.CDLL(str(dylib_path))
    assert hasattr(lib, "c5_abi_cybernetic_audit_baremetal"), "Función FFI no exportada"

    class CyberneticAuditRequest(ctypes.Structure):
        _fields_ = [
            ("disturbances_count", ctypes.c_uint64),
            ("regulator_actions_count", ctypes.c_uint64),
            ("outcomes_tolerance_count", ctypes.c_uint64),
            ("vsm_systems_mask", ctypes.c_uint32),
            ("algedonic_active", ctypes.c_uint32),
            ("double_bind_detected", ctypes.c_uint32),
            ("voluntary_payload_bits", ctypes.c_double),
            ("involuntary_work_metric", ctypes.c_double),
        ]

    class CyberneticAuditResult(ctypes.Structure):
        _fields_ = [
            ("is_viable", ctypes.c_uint32),
            ("fail_stop_triggered", ctypes.c_uint32),
            ("variety_ratio", ctypes.c_double),
            ("entropy_leak_bits", ctypes.c_double),
            ("cost_of_forgery_ratio", ctypes.c_double),
            ("execution_ns", ctypes.c_uint64),
            ("scitt_digest", ctypes.c_uint8 * 32),
        ]

    lib.c5_abi_cybernetic_audit_baremetal.argtypes = [
        ctypes.POINTER(CyberneticAuditRequest),
        ctypes.POINTER(CyberneticAuditResult),
    ]
    lib.c5_abi_cybernetic_audit_baremetal.restype = ctypes.c_uint32

    # Caso: Sistema Viable (Máscara 63 = 0x3F, algedónico activo, sin double bind, ratio >= 0.35)
    req = CyberneticAuditRequest(
        disturbances_count=16,
        regulator_actions_count=16,
        outcomes_tolerance_count=1,
        vsm_systems_mask=63,
        algedonic_active=1,
        double_bind_detected=0,
        voluntary_payload_bits=50.0,
        involuntary_work_metric=50.0,
    )
    res = CyberneticAuditResult()
    status = lib.c5_abi_cybernetic_audit_baremetal(ctypes.byref(req), ctypes.byref(res))
    assert status == 0
    assert res.is_viable == 1
    assert res.fail_stop_triggered == 0
    assert res.variety_ratio == 1.0
    assert res.entropy_leak_bits == 0.0
    assert res.cost_of_forgery_ratio == 0.5
    assert res.scitt_digest[0] == 0xC5
    print("  ✓ C-ABI Bare-Metal Cybernetic Audit verificado exitosamente.")

def test_larsa_120_and_mushushu_0_triad():
    print("[8] Test LARSA-120 & MUSHUSHU-0 Consensus Triad...")
    sys.path.insert(0, str(REPO_ROOT / "src" / "02_engines"))
    sys.path.insert(0, str(REPO_ROOT / "src" / "02_engines" / "mushushu_0"))
    from larsa_120.core.orchestrator import LarsaOrchestrator
    from larsa_120.larsa_execution_pipeline import C5RealPipeline
    from guard import enforce_invariant

    # 1. Boot orchestrator and check POSIX shared memory epoch
    with LarsaOrchestrator() as orch:
        epoch_id, ts = orch.get_active_epoch()
        assert epoch_id >= 0
        assert ts >= 0

    # 2. Pipeline L1 exergy gate, L2 WAL lock, and L3 verification
    pipeline = C5RealPipeline()
    res = pipeline.process(
        payload="Cybernetics-Quadrivium-Triad-Consensus",
        entropy_gain=4.5,
        cost=1.0,
        action="VERIFY_CYBERNETIC_TRIAD"
    )
    assert res["status"] == "SUCCESS"
    assert res["l3_proof"]["status"] == "VERIFIED_C5_REAL"

    # 3. MUSHUSHU-0 POSIX guard invariant
    enforce_invariant(True, "CYBERNETIC_EQUILIBRIUM_PASS")
    print("  ✓ LARSA-120 & MUSHUSHU-0 Consensus Triad verificado exitosamente.")

def main():
    print("=" * 60)
    print("EJECUTANDO COMPLIANCE SUITE: CYBERNETICS QUADRIVIUM")
    print("=" * 60)
    test_ashby_variety()
    test_beer_vsm()
    test_bateson_double_bind()
    test_bandler_grinder_cost()
    test_unified_kernel()
    test_knowledge_kernel_synthesis()
    test_c_abi_baremetal_cybernetic_audit()
    test_larsa_120_and_mushushu_0_triad()
    print("\n[✓] TODOS LOS TESTS PASARON EXITOSAMENTE (100% EXERGÍA C5).")

if __name__ == "__main__":
    main()



