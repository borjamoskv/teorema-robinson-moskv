import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class CausalEstimate:
    """Resultado de estimación proxy causal con notación estándar."""
    estimand: str  # "mean_paired_proxy_difference"
    estimate: float
    ci_lower: float
    ci_upper: float
    confidence_level: float  # e.g., 0.95
    estimator: str  # "hajek_weighted_paired_difference"
    sample_size: int
    assumptions: List[str]
    
    def to_string(self) -> str:
        return (
            f"Estimand: {self.estimand} = {self.estimate:.4f} "
            f"[{self.ci_lower:.4f}, {self.ci_upper:.4f}] "
            f"({self.confidence_level*100:.0f}% IC, {self.estimator}, n={self.sample_size})"
        )

def estimate_shadow_proxy_difference(
    paired_proxy_differences: np.ndarray,
    inclusion_probabilities: np.ndarray,
    confidence_level: float = 0.95,
    bootstrap_replicates: int = 10000
) -> CausalEstimate:
    """
    Estima la diferencia media ponderada (proxy regret) usando el estimador de Hájek.
    
    Nota: Esto estima observed_proxy_regret (diferencia de proxy), NO un ATE sobre
    el outcome final del usuario. No se puede afirmar causalidad de usuario
    sin un A/B user-facing.
    
    Args:
        paired_proxy_differences: Array de diferencias Delta_i = U(x_i, primary) - U(x_i, shadow)
        inclusion_probabilities: Array de q_i (probabilidad de que shadow fue incluido)
    """
    if len(paired_proxy_differences) != len(inclusion_probabilities):
        raise ValueError("Las matrices de diferencias y probabilidades de inclusión deben tener la misma longitud.")
        
    n = len(paired_proxy_differences)
    if n == 0:
        raise ValueError("No se puede estimar con muestra 0.")

    # Clipping to avoid division by zero
    q = np.clip(inclusion_probabilities, 0.01, 1.0)
    
    # Hájek estimator point estimate
    numerator = np.sum(paired_proxy_differences / q)
    denominator = np.sum(1.0 / q)
    estimate_point = numerator / denominator
    
    # Bootstrap CI
    bootstrap_estimates = []
    rng = np.random.default_rng(42)
    
    for _ in range(bootstrap_replicates):
        idx = rng.choice(n, size=n, replace=True)
        boot_diffs = paired_proxy_differences[idx]
        boot_q = q[idx]
        
        boot_num = np.sum(boot_diffs / boot_q)
        boot_den = np.sum(1.0 / boot_q)
        boot_est = boot_num / boot_den
        bootstrap_estimates.append(boot_est)
    
    ci_lower = float(np.percentile(bootstrap_estimates, (1 - confidence_level) / 2 * 100))
    ci_upper = float(np.percentile(bootstrap_estimates, (1 + confidence_level) / 2 * 100))
    
    return CausalEstimate(
        estimand="mean_paired_proxy_difference",
        estimate=float(estimate_point),
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        confidence_level=confidence_level,
        estimator="hajek_weighted_paired_difference",
        sample_size=n,
        assumptions=["ignorability_given_propensity", "overlap"]
    )
