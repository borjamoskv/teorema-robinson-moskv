import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TTFTMetrics:
    ttft_ms_p50: Optional[float]
    ttft_ms_p95: Optional[float]
    ttft_ms_p99: Optional[float]
    total_time_ms: float
    queue_ms: Optional[float]
    network_ms: Optional[float]
    prefill_ms: Optional[float]
    batching_ms: Optional[float]
    serving_ms: Optional[float]
    is_streaming: bool

@dataclass
class ExecutionReceipt:
    """T1: Result of a single primary or shadow execution."""
    decision_receipt_id: str
    route_id: str
    status: str
    metrics: TTFTMetrics
    tokens_in: int
    tokens_out: int
    cost_usd: float
    errors: int
    retries: int
    fallback_used: bool
    response_commitment: str
    provider_receipt: Optional[Dict]
    timestamp: float = field(default_factory=time.time)
    signature: Optional[str] = None
