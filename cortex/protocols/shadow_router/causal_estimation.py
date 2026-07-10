import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class CausalEstimate:
    """Resultado de estimación causal con notación estándar."""
    ate: float  # E[Y(1)] - E[Y(0)]
    ci_lower: float
    ci_upper: float
    confidence_level: float  # e.g., 0.95
    estimator: str  # "ips_weighted_difference"
    sample_size: int
    assumptions: List[str]
    
    def to_string(self) -> str:
        return (
            f"ATE = {self.ate:.4f} "
            f"[{self.ci_lower:.4f}, {self.ci_upper:.4f}] "
            f"({self.confidence_level*100:.0f}% IC, {self.estimator}, n={self.sample_size})"
        )

def estimate_ate_shadow(
    primary_outcomes: np.ndarray,
    shadow_outcomes: np.ndarray,
    propensity_scores: np.ndarray,
    confidence_level: float = 0.95,
    bootstrap_replicates: int = 10000
) -> CausalEstimate:
    """
    Estima ATE mediante Inverse Propensity Scoring con IC bootstrap.
    
    ATE = E[Y | do(selected)] - E[Y | do(shadow)]
    
    Nota: Esto estima observed_proxy_regret, NO "regret causal absoluto".
    """
    if len(primary_outcomes) != len(shadow_outcomes) or len(primary_outcomes) != len(propensity_scores):
        raise ValueError("Las matrices de resultados y propensiones deben tener la misma longitud.")
        
    n = len(primary_outcomes)
    if n == 0:
        raise ValueError("No se puede estimar ATE con muestra 0.")

    # IPS weights (clip to avoid division by zero or extreme weights)
    clipped_propensities = np.clip(propensity_scores, 0.01, 0.99)
    weights_primary = 1.0 / clipped_propensities
    weights_shadow = 1.0 / (1.0 - clipped_propensities)
    
    # Weighted means
    ate_point = np.average(primary_outcomes, weights=weights_primary) - \
                np.average(shadow_outcomes, weights=weights_shadow)
    
    # Bootstrap CI
    bootstrap_ates = []
    rng = np.random.default_rng(42)
    
    for _ in range(bootstrap_replicates):
        idx = rng.choice(n, size=n, replace=True)
        boot_primary = primary_outcomes[idx]
        boot_shadow = shadow_outcomes[idx]
        boot_weights_primary = weights_primary[idx]
        boot_weights_shadow = weights_shadow[idx]
        
        boot_ate = np.average(boot_primary, weights=boot_weights_primary) - \
                   np.average(boot_shadow, weights=boot_weights_shadow)
        bootstrap_ates.append(boot_ate)
    
    ci_lower = float(np.percentile(bootstrap_ates, (1 - confidence_level) / 2 * 100))
    ci_upper = float(np.percentile(bootstrap_ates, (1 + confidence_level) / 2 * 100))
    
    return CausalEstimate(
        ate=float(ate_point),
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        confidence_level=confidence_level,
        estimator="ips_weighted_difference",
        sample_size=n,
        assumptions=["ignorability_given_propensity", "overlap", "SUTVA"]
    )
