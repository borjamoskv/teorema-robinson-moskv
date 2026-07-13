# ctre_engine.py | Nivel de Realidad: #C5-REAL
import numpy as np
from typing import List, Tuple

class CommitTimeReconciliationEngine:
    """Freno Termodinámico para Agentes Asíncronos."""
    def __init__(self, alpha: float = 0.05, variance_threshold: float = 0.015):
        assert 0.0 < alpha < 1.0, "Alpha debe ser probabilístico."
        self.alpha = alpha
        self.threshold = variance_threshold

    def _calculate_cvar(self, drift_samples: np.ndarray) -> float:
        if len(drift_samples) == 0: return 0.0
        var_limit = np.percentile(drift_samples, 100 * (1 - self.alpha))
        tail_risks = drift_samples[drift_samples >= var_limit]
        return float(np.mean(tail_risks)) if len(tail_risks) > 0 else float(var_limit)

    def enforce_thermodynamic_brake(self, drift_observations: List[float]) -> Tuple[str, float]:
        """El Enrutador Negentrópico: Colapsa la acción o purga el estado."""
        assert len(drift_observations) > 0, "Fricción estática: Faltan observaciones."
        
        cvar_risk = self._calculate_cvar(np.array(drift_observations))
        if cvar_risk > self.threshold:
            return "ACTION_ABORT", round(cvar_risk, 5) # Vector browniano letal detectado
            
        return "ACTION_COMMIT", round(cvar_risk, 5) # Cambio determinista aprobado
