import numpy as np
import pytest
from cortex.protocols.shadow_router.causal_estimation import estimate_ate_shadow

def test_causal_estimation_ate():
    """Valida el cálculo del ATE usando Inverse Propensity Scoring (IPS) con Bootstrap CI."""
    primary = np.array([0.8, 0.9, 0.7, 0.85, 0.95])
    shadow = np.array([0.7, 0.8, 0.65, 0.8, 0.9])
    propensities = np.array([0.1, 0.2, 0.1, 0.5, 0.2])
    
    # Run estimation (using few replicates for speed in test)
    estimate = estimate_ate_shadow(primary, shadow, propensities, bootstrap_replicates=100)
    
    assert estimate.estimator == "ips_weighted_difference"
    assert estimate.sample_size == 5
    assert estimate.ci_lower <= estimate.ci_upper
    
    # ATE > 0 indicates primary outperformed shadow in this mock data
    assert estimate.ate > 0
    assert "ignorability_given_propensity" in estimate.assumptions

def test_causal_estimation_requires_equal_length():
    with pytest.raises(ValueError, match="misma longitud"):
        estimate_ate_shadow(np.array([1.0]), np.array([1.0, 0.5]), np.array([0.5]))
