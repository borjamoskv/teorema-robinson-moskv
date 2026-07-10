import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class CalibratedUncertainty:
    confidence_calibrated: float
    confidence_type: str  # e.g., "frequentist_coverage_95"
    margin: float
    sample_size: int
    period: str
    calibration_method: str
    dataset_hash: str
    policy_hash: str
    evaluator_hash: str
    ontology_commit: str

@dataclass
class CausalClaim:
    intervention: str
    outcome: str
    confounders: List[str]
    identification_strategy: str
    estimator: str
    sample_size: int
    confidence_interval: List[float]
    assumptions: List[str]

@dataclass
class EvaluationReceipt:
    """T2: Unified evaluation and proxy regret measurement."""
    evaluated_execution_hashes: List[str]
    observed_proxy_regret: float
    causal_claim: CausalClaim
    uncertainty: CalibratedUncertainty
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None

    def sign(self, evaluator_key: str) -> None:
        payload = json.dumps({
            "evaluated_execution_hashes": sorted(self.evaluated_execution_hashes),
            "observed_proxy_regret": self.observed_proxy_regret,
            "ontology_commit": self.uncertainty.ontology_commit
        }, sort_keys=True)
        self.signature = hashlib.sha256(f"{evaluator_key}:{payload}".encode()).hexdigest()
