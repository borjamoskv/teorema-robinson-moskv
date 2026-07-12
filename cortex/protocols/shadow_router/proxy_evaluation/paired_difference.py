import numpy as np
from typing import List
from cortex.protocols.shadow_router.protocol.schemas import ProxyDifferenceEstimate, ConfidenceInterval

def estimate_shadow_proxy_difference(paired_differences_basis_points: np.ndarray, shadow_inclusion_indicators: np.ndarray, shadow_inclusion_propensities_basis_points: np.ndarray, confidence_level_basis_points: int=9500, bootstrap_replicates: int=10000, weight_trim_threshold: float=50.0, random_seed: int=42) -> ProxyDifferenceEstimate:
    n = len(paired_differences_basis_points)
    if n == 0:
        raise ValueError('Muestra vacía.')
    rng = np.random.default_rng(random_seed)
    q = shadow_inclusion_propensities_basis_points / 10000.0
    assert np.all(q > 0)
    raw_weights = shadow_inclusion_indicators / q
    trimmed_weights = np.minimum(raw_weights, weight_trim_threshold)
    weight_trimming_applied = np.any(raw_weights > weight_trim_threshold)
    max_weight = np.max(raw_weights)
    numerator = np.sum(trimmed_weights * paired_differences_basis_points)
    denominator = np.sum(trimmed_weights)
    if denominator == 0:
        raise ValueError('No shadow evaluations included (denominator = 0)')
    estimate = numerator / denominator
    effective_n = np.sum(trimmed_weights) ** 2 / np.sum(trimmed_weights ** 2)
    boot_estimates = []
    for _ in range(bootstrap_replicates):
        idx = rng.choice(n, size=n, replace=True)
        boot_diffs = paired_differences_basis_points[idx]
        boot_ind = shadow_inclusion_indicators[idx]
        boot_q = q[idx]
        boot_raw_w = boot_ind / boot_q
        boot_trimmed_w = np.minimum(boot_raw_w, weight_trim_threshold)
        boot_num = np.sum(boot_trimmed_w * boot_diffs)
        boot_den = np.sum(boot_trimmed_w)
        if boot_den > 0:
            boot_estimates.append(boot_num / boot_den)
    ci_lower = np.percentile(boot_estimates, (10000 - confidence_level_basis_points) / 200.0)
    ci_upper = np.percentile(boot_estimates, (10000 + confidence_level_basis_points) / 200.0)
    ci = ConfidenceInterval(level_basis_points=confidence_level_basis_points, lower_basis_points=int(ci_lower), upper_basis_points=int(ci_upper), method='hajek_weighted_bootstrap')
    return ProxyDifferenceEstimate(estimand='mean_paired_proxy_difference', estimate_basis_points=int(estimate), confidence_interval=ci, estimator='hajek_weighted_paired_difference', assumptions=['shadow_inclusion_independent_of_outcome_given_features', 'overlap', 'no_interference_between_primary_and_shadow'], sample_size=n, effective_sample_size=int(effective_n), max_weight_basis_points=int(max_weight * 10000), weight_trimming_applied=weight_trimming_applied)
