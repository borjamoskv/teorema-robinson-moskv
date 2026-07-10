from dataclasses import dataclass
from typing import Tuple

@dataclass
class RiskSensitivePolicy:
    domain: str
    impact_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    reversibility: bool
    privacy_risk: bool
    cost_sensitivity: str
    slo_ms: int

    def evaluate_action(self, confidence_calibrated: float) -> Tuple[str, str]:
        """
        Determines the routing action based on calibrated uncertainty and risk context.
        Does NOT use a fixed 80% threshold.
        """
        if self.impact_level == "CRITICAL" or self.privacy_risk:
            # High risk requires high confidence, else human review / safe fallback
            if confidence_calibrated < 95.0:
                return "ESCALATE", "Confianza insuficiente para contexto crítico."
            return "ROUTE_PRIMARY", "Confianza adecuada."
            
        if self.impact_level == "LOW" and self.reversibility:
            # Low risk can tolerate lower confidence
            if confidence_calibrated < 60.0:
                return "ROUTE_BALANCED", "Confianza baja, usando ruta robusta genérica."
            return "ROUTE_PRIMARY", "Confianza adecuada para bajo riesgo."
            
        # Default medium risk
        if confidence_calibrated < 85.0:
            return "DELEGATE_DEEP_RESEARCH", "Incertidumbre alta, delegar a investigación."
            
        return "ROUTE_PRIMARY", "Confianza adecuada."
