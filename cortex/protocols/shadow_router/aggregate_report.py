from dataclasses import dataclass, field
from typing import List, Optional
import time
import hashlib
from cortex.protocols.shadow_router.canonical_json import canonical_json

@dataclass
class AggregateEvaluationReport:
    """T3: Aggregate statistical inference."""
    cohort_id: str
    metric: str
    estimate_basis_points: float
    confidence_interval_95_basis_points: List[float]
    sample_size: int
    estimator: str
    period_start: str
    period_end: str
    dataset_hash: str
    policy_hash: str
    evaluator_hash: str
    timestamp_unix: int = field(default_factory=lambda: int(time.time()))
    signature: Optional[str] = None

    def sign(self, evaluator_key: str) -> None:
        payload = canonical_json({
            "cohort_id": self.cohort_id,
            "metric": self.metric,
            "estimate_basis_points": self.estimate_basis_points,
            "confidence_interval_95_basis_points": self.confidence_interval_95_basis_points,
            "sample_size": self.sample_size,
            "estimator": self.estimator,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "dataset_hash": self.dataset_hash,
            "policy_hash": self.policy_hash,
            "evaluator_hash": self.evaluator_hash
        })
        self.signature = hashlib.sha256(f"{evaluator_key}:{payload}".encode()).hexdigest()
