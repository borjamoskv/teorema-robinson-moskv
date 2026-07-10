from typing import List, Dict

class PropensitySampler:
    """
    Inverse Propensity Scoring (IPS) requires known inclusion probabilities
    and positive sampling.
    """
    def __init__(self, policy_id: str, policy_hash: str):
        self.policy_id = policy_id
        self.policy_hash = policy_hash

    def get_inclusion_probabilities(self, eligible_candidates: List[str]) -> Dict[str, float]:
        """
        Returns basis points probability (0.0 to 1.0) for each eligible candidate.
        Ensures positivity (all > 0).
        """
        if not eligible_candidates:
            return {}
        
        # In a real stratified random sampler, these would be derived deterministically
        base_prob = 1.0 / len(eligible_candidates)
        probs = {c: base_prob for c in eligible_candidates}
        return probs
