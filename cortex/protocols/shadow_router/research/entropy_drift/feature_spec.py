import numpy as np
from typing import List


def compute_aggregate_entropy(route_probabilities: np.ndarray) -> float:
    route_probabilities = route_probabilities[route_probabilities > 0]
    return -np.sum(route_probabilities * np.log2(route_probabilities))


def compute_predictive_entropy(prompt_propensities: List[np.ndarray]) -> float:
    entropies = []
    for props in prompt_propensities:
        props = props[props > 0]
        h = -np.sum(props * np.log2(props))
        entropies.append(h)
    return float(np.mean(entropies)) if entropies else 0.0


def compute_distribution_divergence(p_t: np.ndarray, p_ref: np.ndarray) -> float:
    m = 0.5 * (p_t + p_ref)

    def kl_divergence(p, q) -> "Any":
        mask = (p > 0) & (q > 0)
        return np.sum(p[mask] * np.log2(p[mask] / q[mask]))

    return 0.5 * kl_divergence(p_t, m) + 0.5 * kl_divergence(p_ref, m)
