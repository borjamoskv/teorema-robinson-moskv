from typing import List, Dict
from cortex.protocols.shadow_router.protocol.schemas import ObservedProxyRegret

def calculate_observed_proxy_regret(primary_route_id: str, primary_utility_basis_points: int, shadow_utilities_basis_points: Dict[str, int], utility_spec_hash: str, evaluator_hash: str) -> ObservedProxyRegret:
    best_route_id = primary_route_id
    best_utility = primary_utility_basis_points
    for route_id, utility in shadow_utilities_basis_points.items():
        if utility > best_utility:
            best_utility = utility
            best_route_id = route_id
    regret = best_utility - primary_utility_basis_points
    assert regret >= 0, 'Regret no puede ser negativo.'
    return ObservedProxyRegret(selected_route_id=primary_route_id, best_observed_route_id=best_route_id, selected_utility_basis_points=primary_utility_basis_points, best_observed_utility_basis_points=best_utility, observed_proxy_regret_basis_points=regret, utility_spec_hash=utility_spec_hash, evaluator_hash=evaluator_hash)
