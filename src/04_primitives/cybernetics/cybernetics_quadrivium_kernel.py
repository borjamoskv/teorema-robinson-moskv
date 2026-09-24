# C5-REAL EXERGY CERTIFIED
"""
Cybernetics Quadrivium Kernel (Unified Evaluator)
Integra los 4 pilares cibernéticos:
1. Ashby (Variedad Requerida)
2. Beer (Viabilidad VSM)
3. Bateson (Tipos Lógicos & Doble Vínculo)
4. Bandler & Grinder (Coste de Falsificación Somático)
"""

from dataclasses import dataclass
from typing import Dict, Any, List

from .variety_evaluator import AshbyVarietyEvaluator, VarietyReport
from .vsm_analyzer import BeerVsmAnalyzer, VsmTopology, VsmReport
from .logical_types_filter import BatesonLogicalTypesFilter, Injunction, DoubleBindReport
from .involuntary_cost_verifier import BandlerGrinderCostVerifier, ForgeryAuditReport

@dataclass(frozen=True)
class CyberneticAuditReceipt:
    ashby_variety: VarietyReport
    beer_vsm: VsmReport
    bateson_types: DoubleBindReport
    bandler_grinder_forgery: ForgeryAuditReport
    is_globally_viable: bool
    fail_stop_triggered: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ashby_variety": self.ashby_variety.to_dict(),
            "beer_vsm": self.beer_vsm.to_dict(),
            "bateson_types": self.bateson_types.to_dict(),
            "bandler_grinder_forgery": self.bandler_grinder_forgery.to_dict(),
            "is_globally_viable": self.is_globally_viable,
            "fail_stop_triggered": self.fail_stop_triggered,
            "summary": self.summary
        }

class CyberneticsQuadriviumKernel:
    """
    Núcleo unificado de evaluación cibernética de arquitecturas cognitivas y topologías de enjambre.
    """

    @classmethod
    def audit_system(
        cls,
        disturbances: int,
        regulator_actions: int,
        vsm_topology: VsmTopology,
        injunctions: List[Injunction],
        escape_allowed: bool,
        voluntary_payload_bits: float,
        involuntary_work_metric: float
    ) -> CyberneticAuditReceipt:
        # 1. Ashby
        rep_ashby = AshbyVarietyEvaluator.evaluate(
            disturbances_count=disturbances,
            regulator_actions_count=regulator_actions
        )

        # 2. Beer VSM
        rep_vsm = BeerVsmAnalyzer.audit_topology(vsm_topology)

        # 3. Bateson
        rep_bateson = BatesonLogicalTypesFilter.audit_injunction_matrix(
            injunctions=injunctions,
            escape_allowed=escape_allowed
        )

        # 4. Bandler & Grinder
        rep_bg = BandlerGrinderCostVerifier.verify(
            voluntary_payload_bits=voluntary_payload_bits,
            involuntary_work_metric=involuntary_work_metric
        )

        # Veredicto Global
        fail_stop = (
            rep_ashby.entropy_leak_bits > 0.0 or
            not rep_vsm.is_viable or
            rep_bateson.is_deadlock or
            not rep_bg.is_authentic
        )

        is_globally_viable = not fail_stop

        if is_globally_viable:
            summary = "SISTEMA CIBERNÉTICAMENTE VIABLE: Variedad balanceada, recursión VSM completa, tipos lógicos coherentes y coste de falsificación atestado."
        else:
            reasons = []
            if rep_ashby.entropy_leak_bits > 0:
                reasons.append(f"Déficit de Variedad ({rep_ashby.entropy_leak_bits} bits)")
            if not rep_vsm.is_viable:
                reasons.append(f"Patología VSM ({len(rep_vsm.pathologies)} fallos)")
            if rep_bateson.is_deadlock:
                reasons.append("Deadlock de Doble Vínculo")
            if not rep_bg.is_authentic:
                reasons.append("Anergía por Cheap Talk / Falsificación")
            summary = f"FAIL-STOP CIBERNÉTICO ACTIVADO: {'; '.join(reasons)}."

        return CyberneticAuditReceipt(
            ashby_variety=rep_ashby,
            beer_vsm=rep_vsm,
            bateson_types=rep_bateson,
            bandler_grinder_forgery=rep_bg,
            is_globally_viable=is_globally_viable,
            fail_stop_triggered=fail_stop,
            summary=summary
        )
