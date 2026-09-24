# C5-REAL EXERGY CERTIFIED
"""
Ashby Variety Evaluator Primitive (Ring-0 / C5-REAL)
Implementa la Ley de Variedad Requerida de W. Ross Ashby (1956).
H(O) >= H(D) - H(R)
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

class VarietyStatus(Enum):
    HOMEOSTATIC_EQUILIBRIUM = "HOMEOSTATIC_EQUILIBRIUM"
    VARIETY_DEFICIT = "VARIETY_DEFICIT"
    OVER_REGULATED = "OVER_REGULATED"

@dataclass(frozen=True)
class VarietyReport:
    h_disturbances_bits: float
    h_regulator_bits: float
    h_outcomes_allowed_bits: float
    variety_ratio: float
    status: VarietyStatus
    entropy_leak_bits: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "h_disturbances_bits": self.h_disturbances_bits,
            "h_regulator_bits": self.h_regulator_bits,
            "h_outcomes_allowed_bits": self.h_outcomes_allowed_bits,
            "variety_ratio": self.variety_ratio,
            "status": self.status.value,
            "entropy_leak_bits": self.entropy_leak_bits
        }

class AshbyVarietyEvaluator:
    """
    Evaluador formal de variedad requerida.
    Garantiza que la variedad del regulador R sea al menos igual
    a la variedad de perturbaciones D menos la variedad admisible en el objetivo O.
    """

    @staticmethod
    def evaluate(
        disturbances_count: int,
        regulator_actions_count: int,
        outcomes_tolerance_count: int = 1
    ) -> VarietyReport:
        if disturbances_count <= 0 or regulator_actions_count <= 0 or outcomes_tolerance_count <= 0:
            raise ValueError("Las cardinalidades de estados deben ser enteros positivos (>0).")

        # Entropías logarítmicas de estados discretos (bits)
        h_d = math.log2(disturbances_count)
        h_r = math.log2(regulator_actions_count)
        h_o = math.log2(outcomes_tolerance_count)

        # Requisito de Ashby: h_r >= h_d - h_o
        required_h_r = max(0.0, h_d - h_o)
        entropy_leak = max(0.0, required_h_r - h_r)
        variety_ratio = h_r / max(1e-9, required_h_r)

        if entropy_leak > 0.0:
            status = VarietyStatus.VARIETY_DEFICIT
        elif variety_ratio > 1.5 and h_r > 5.0:
            status = VarietyStatus.OVER_REGULATED
        else:
            status = VarietyStatus.HOMEOSTATIC_EQUILIBRIUM

        return VarietyReport(
            h_disturbances_bits=round(h_d, 4),
            h_regulator_bits=round(h_r, 4),
            h_outcomes_allowed_bits=round(h_o, 4),
            variety_ratio=round(variety_ratio, 4),
            status=status,
            entropy_leak_bits=round(entropy_leak, 4)
        )
