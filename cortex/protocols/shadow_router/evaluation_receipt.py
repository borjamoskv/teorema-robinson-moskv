import hashlib
import time
from dataclasses import dataclass, field
from typing import List, Optional
from cortex.protocols.shadow_router.canonical_json import canonical_json

@dataclass
class EvaluationReceipt:
    """T2: Unified evaluation and proxy regret measurement per request."""
    quality_proxy_basis_points: int
    utility_basis_points: int
    observed_proxy_regret_basis_points: int
    evaluator_hash: str
    utility_spec_hash: str
    timestamp_unix: int = field(default_factory=lambda: int(time.time()))
    signature: Optional[str] = None

    def sign(self, evaluator_key: str) -> None:
        payload = canonical_json({
            "quality_proxy_basis_points": self.quality_proxy_basis_points,
            "utility_basis_points": self.utility_basis_points,
            "observed_proxy_regret_basis_points": self.observed_proxy_regret_basis_points,
            "evaluator_hash": self.evaluator_hash,
            "utility_spec_hash": self.utility_spec_hash,
            "timestamp_unix": self.timestamp_unix
        })
        self.signature = hashlib.sha256(f"{evaluator_key}:{payload}".encode()).hexdigest()
