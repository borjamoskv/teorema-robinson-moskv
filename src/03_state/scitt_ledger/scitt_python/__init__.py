# C5-REAL EXERGY CERTIFIED
"""
CORTEX: Sovereign C5-REAL Execution Kernel.
"""

try:
    from scitt_python.core.quad_pillar_kernel import (
        QuadPillarKernel,
        SystemPillar,
        OrchestrationPillar,
        MemoryPillar,
        DeterminismPillar,
    )
    from scitt_python.core.cognitive_state_observer import CognitiveStateObserver
    from scitt_python.engines.subadditivity_verifier import CertificateCategoryP
    from scitt_python.engines.entropy_mapping_engine import ThermodynamicEntropyEngine
    from scitt_python.core.invariant_sentinel import audit_and_align_invariants
    from scitt_python.core.deliverability_validator import DeliverabilityValidator
    from scitt_python.engines.active_inference_engine import UnifiedActiveInferenceEngine

    __all__ = [
        "QuadPillarKernel",
        "SystemPillar",
        "OrchestrationPillar",
        "MemoryPillar",
        "DeterminismPillar",
        "CognitiveStateObserver",
        "CertificateCategoryP",
        "ThermodynamicEntropyEngine",
        "audit_and_align_invariants",
        "DeliverabilityValidator",
        "UnifiedActiveInferenceEngine",
    ]
except ImportError:
    __all__ = []

