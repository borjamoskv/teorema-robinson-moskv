import numpy as np
from cortex.protocols.shadow_router.proxy_evaluation.paired_difference import (
    estimate_shadow_proxy_difference,
)
from cortex.protocols.shadow_router.proxy_evaluation.sampled_set_regret import (
    calculate_observed_proxy_regret,
)


def test_paired_proxy_difference_estimation() -> None:
    diffs = np.array([120, -50, 200, 10, 80])
    indicators = np.array([1, 1, 1, 1, 1])
    propensities = np.array([200, 500, 200, 1000, 500])
    estimate = estimate_shadow_proxy_difference(
        paired_differences_basis_points=diffs,
        shadow_inclusion_indicators=indicators,
        shadow_inclusion_propensities_basis_points=propensities,
        bootstrap_replicates=100,
    )
    assert estimate.estimand == "mean_paired_proxy_difference"
    assert estimate.sample_size == 5
    assert (
        estimate.confidence_interval.lower_basis_points
        <= estimate.confidence_interval.upper_basis_points
    )


def test_observed_proxy_regret_nonnegative() -> None:
    regret = calculate_observed_proxy_regret(
        primary_route_id="gemini-flash",
        primary_utility_basis_points=8000,
        shadow_utilities_basis_points={"claude-sonnet": 8500},
        utility_spec_hash="sha256:util",
        evaluator_hash="sha256:eval",
    )
    assert regret.observed_proxy_regret_basis_points == 500
    regret_best = calculate_observed_proxy_regret(
        primary_route_id="gemini-flash",
        primary_utility_basis_points=9000,
        shadow_utilities_basis_points={"claude-sonnet": 8500},
        utility_spec_hash="sha256:util",
        evaluator_hash="sha256:eval",
    )
    assert regret_best.observed_proxy_regret_basis_points == 0
