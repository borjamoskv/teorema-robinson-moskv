from typing import Dict, Any

class BaselineModels:

    @staticmethod
    def get_b0(historical_brier: float) -> float:
        return historical_brier

    @staticmethod
    def get_b1(historical_brier: float, label_volume: int) -> float:
        return historical_brier * (1.0 + 1.0 / max(1, label_volume))

    @staticmethod
    def get_b3(historical_brier: float, label_volume: int, traffic_mix_shift: float, policy_changes: int) -> float:
        base = BaselineModels.get_b1(historical_brier, label_volume)
        return base + traffic_mix_shift * 0.1 + policy_changes * 0.05
