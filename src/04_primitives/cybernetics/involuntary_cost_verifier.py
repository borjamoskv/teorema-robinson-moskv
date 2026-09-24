# C5-REAL EXERGY CERTIFIED
"""
Bandler-Grinder Involuntary Cost-of-Forgery Verifier Primitive (Ring-2 / C5-REAL)
Implementa el modelado cibernético de señales sensoriales involuntarias (Bandler & Grinder, 1979)
y el Aforismo 5 de C5-REAL: "Lo voluntario vale menos que lo involuntario".
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

class SignalTier(Enum):
    CHEAP_TALK_VOLUNTARY = "CHEAP_TALK_VOLUNTARY"  # Texto libre, tokens LLM, prompts sin coste térmico
    ATTESTED_INVOLUNTARY = "ATTESTED_INVOLUNTARY"  # Telemetría de hardware, firma Merkle, latencia física, pulso térmico

@dataclass(frozen=True)
class TelemetricSignal:
    name: str
    tier: SignalTier
    cost_of_forgery_joules_or_work: float
    entropy_bits: float

@dataclass(frozen=True)
class ForgeryAuditReport:
    is_authentic: bool
    cost_of_forgery_ratio: float
    detected_tier: SignalTier
    exergy_density: float
    verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_authentic": self.is_authentic,
            "cost_of_forgery_ratio": self.cost_of_forgery_ratio,
            "detected_tier": self.detected_tier.value,
            "exergy_density": self.exergy_density,
            "verdict": self.verdict
        }

class BandlerGrinderCostVerifier:
    """
    Verificador de Coste de Falsificación (Aforismo 5).
    Rechaza toda aserción que no esté anclada a una señal involuntaria
    con un coste termodinámico o computacional no nulo (PoW, Merkle, telemetría física).
    """

    MIN_COST_THRESHOLD: float = 0.5  # Umbral mínimo de coste de falsificación

    @classmethod
    def verify(
        cls,
        voluntary_payload_bits: float,
        involuntary_work_metric: float
    ) -> ForgeryAuditReport:
        if voluntary_payload_bits < 0 or involuntary_work_metric < 0:
            raise ValueError("Las métricas deben ser valores no negativos.")

        # Ratio de coste de falsificación: trabajo real dividido entre volumen de cheap talk
        ratio = involuntary_work_metric / max(1.0, voluntary_payload_bits)
        is_authentic = ratio >= cls.MIN_COST_THRESHOLD

        if is_authentic:
            tier = SignalTier.ATTESTED_INVOLUNTARY
            verdict = "VALIDADO: La señal está acoplada al sustrato termodinámico real (Costo no falsificable)."
        else:
            tier = SignalTier.CHEAP_TALK_VOLUNTARY
            verdict = "RECHAZADO: Anergía detectada. El payload es pura retórica voluntaria (Cheap Talk) sin anclaje físico."

        return ForgeryAuditReport(
            is_authentic=is_authentic,
            cost_of_forgery_ratio=round(ratio, 4),
            detected_tier=tier,
            exergy_density=round(ratio * 100.0, 2),
            verdict=verdict
        )
