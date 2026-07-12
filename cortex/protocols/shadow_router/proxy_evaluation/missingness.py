from typing import Optional


def resolve_outcome_with_missingness(
    raw_outcome: Optional[int], failure_status: str, penalty_basis_points: int = 0
) -> Optional[int]:
    if raw_outcome is not None:
        return raw_outcome
    if failure_status == "shadow_timeout":
        return None if penalty_basis_points == 0 else penalty_basis_points
    if failure_status in ["shadow_failure", "evaluation_unavailable"]:
        return None
    return None
