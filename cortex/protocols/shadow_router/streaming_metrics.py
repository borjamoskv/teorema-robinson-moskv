from dataclasses import dataclass
from typing import Optional

@dataclass
class LatencyMetrics:
    """
    TTFT is an operational metric. It represents MCTS algorithmic volume
    in applicable models, not "attention fatigue".
    """
    ttft_ms: Optional[float]
    total_time_ms: float
    is_streaming: bool
    
    # Métricas algorítmicas puras
    mcts_depth: Optional[int] = None
    branching_factor: Optional[float] = None
    algorithmic_volume: Optional[str] = None  # e.g., "O(d * b^d)"
    attention_fatigue_score: Optional[float] = None  # MUST BE NULL
    
    def __post_init__(self):
        if self.attention_fatigue_score is not None:
            raise ValueError("attention_fatigue_score es pseudofísica. Usar mcts_depth + branching_factor.")
        
        if not self.is_streaming and self.ttft_ms is not None:
            # TTFT requires a streaming response to be measurable distinctly from total_time
            self.ttft_ms = None
