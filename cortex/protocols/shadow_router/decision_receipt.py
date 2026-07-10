import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class DecisionReceipt:
    """T0: Proof-of-Route decision persisted before execution."""
    request_id: str
    prompt_commitment: str
    shadow_sampling_policy_id: str
    shadow_sampling_policy_hash: str
    eligible_candidate_set_hash: str
    primary_route_id: str
    selected_shadow_routes: List[str]
    predictions: Dict[str, Any]
    uncertainty_calibrated: float
    propensity_scores: Dict[str, float]
    shadow_allowed: bool
    config_hash: str
    timestamp: float = field(default_factory=time.time)
    receipt_id: str = field(default_factory=lambda: f"dr_{uuid.uuid4().hex}")
    signature: Optional[str] = None

    def sign(self, router_key: str) -> None:
        """Signs the decision receipt immutably."""
        payload = json.dumps({
            "request_id": self.request_id,
            "prompt_commitment": self.prompt_commitment,
            "config_hash": self.config_hash,
            "primary_route_id": self.primary_route_id,
            "shadow_routes": self.selected_shadow_routes,
            "shadow_allowed": self.shadow_allowed,
            "timestamp": self.timestamp
        }, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        self.signature = hashlib.sha256(f"{router_key}:{payload}".encode()).hexdigest()

    def verify(self, router_key: str) -> bool:
        if not self.signature:
            return False
        payload = json.dumps({
            "request_id": self.request_id,
            "prompt_commitment": self.prompt_commitment,
            "config_hash": self.config_hash,
            "primary_route_id": self.primary_route_id,
            "shadow_routes": self.selected_shadow_routes,
            "shadow_allowed": self.shadow_allowed,
            "timestamp": self.timestamp
        }, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        expected = hashlib.sha256(f"{router_key}:{payload}".encode()).hexdigest()
        return self.signature == expected
