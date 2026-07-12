import pytest
from typing import Dict


class CausalViolationError(Exception):
    pass


class SUTVAViolationError(CausalViolationError):
    pass


class PositivityViolationError(CausalViolationError):
    pass


class ShadowRouterSimulator:
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self.concurrent_load = 0

    def route_request(
        self, prompt_difficulty: float, target_model: str, is_shadow: bool = False
    ) -> Dict:
        self.concurrent_load += 1
        base_latency = 100
        interference_penalty = (
            self.concurrent_load**2 if self.concurrent_load > self.capacity else 0
        )
        actual_latency = base_latency + interference_penalty
        if actual_latency > base_latency * 10:
            raise SUTVAViolationError(
                f"SIGKILL: SUTVA Violated. Interference penalty {interference_penalty:.2f} exceeded threshold."
            )
        if target_model == "blacklisted_model" and prompt_difficulty > 0.9:
            if is_shadow:
                raise PositivityViolationError(
                    "SIGKILL: Positivity violated. Attempted shadow IPW calculation with 0.0 propensity."
                )
        return {"latency": actual_latency, "status": "success"}


def test_sutva_violation_fail_fast():
    router = ShadowRouterSimulator(capacity=10)
    with pytest.raises(SUTVAViolationError):
        for i in range(50):
            router.route_request(prompt_difficulty=0.5, target_model="model_a")


def test_positivity_violation_fail_fast():
    router = ShadowRouterSimulator()
    with pytest.raises(PositivityViolationError):
        router.route_request(
            prompt_difficulty=0.95, target_model="blacklisted_model", is_shadow=True
        )


def test_ignorability_confounder_detection():
    outcomes = [
        {"model": "A", "difficulty": 0.9, "success": 1},
        {"model": "A", "difficulty": 0.8, "success": 1},
        {"model": "B", "difficulty": 0.1, "success": 1},
        {"model": "B", "difficulty": 0.2, "success": 1},
    ]
    success_a = (
        sum((1 for o in outcomes if o["model"] == "A" and o["success"] == 1)) / 2
    )
    success_b = (
        sum((1 for o in outcomes if o["model"] == "B" and o["success"] == 1)) / 2
    )
    naive_ate = success_a - success_b
    assert naive_ate == 0.0, (
        "Naive ATE must expose the confounded artifact without IPW adjustment."
    )
