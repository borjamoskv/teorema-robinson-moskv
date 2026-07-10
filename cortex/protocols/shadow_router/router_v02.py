import asyncio
from typing import AsyncGenerator, Dict, Any, List

from cortex.protocols.shadow_router.decision_receipt import DecisionReceipt
from cortex.protocols.shadow_router.privacy_gate import PrivacyGate, generate_prompt_commitment
from cortex.protocols.shadow_router.shadow_dispatcher import ShadowDispatcher, ShadowJob
from cortex.protocols.shadow_router.risk_policy import RiskSensitivePolicy


class EventStore:
    def __init__(self):
        self.receipts = {}
        
    async def append(self, receipt: DecisionReceipt) -> None:
        self.receipts[receipt.receipt_id] = receipt


class StreamingResponse:
    def __init__(self, stream: AsyncGenerator[str, None], headers: Dict[str, str]):
        self.stream = stream
        self.headers = headers


class UserRequest:
    def __init__(self, payload: str, metadata: Dict[str, Any]):
        self.payload = payload
        self.metadata = metadata


class CortexShadowRouter:
    def __init__(self, event_store: EventStore, dispatcher: ShadowDispatcher, privacy_gate: PrivacyGate, router_key: str):
        self.event_store = event_store
        self.dispatcher = dispatcher
        self.privacy_gate = privacy_gate
        self.router_key = router_key

    async def decide_and_persist(self, request: UserRequest) -> DecisionReceipt:
        # 1. Gate check
        allowed = self.privacy_gate.shadow_allowed(
            has_consent=request.metadata.get("has_consent", False),
            data_classification_allowed=request.metadata.get("data_classification_allowed", False),
            provider_approved=request.metadata.get("provider_approved", False),
            region_compatible=request.metadata.get("region_compatible", False),
            budget_available=request.metadata.get("budget_available", False),
            no_sensitive_tool_context=request.metadata.get("no_sensitive_tool_context", False),
            no_security_incident=request.metadata.get("no_security_incident", False)
        )
        
        # 2. Risk-Sensitive Policy Evaluation
        policy = RiskSensitivePolicy(
            domain=request.metadata.get("domain", "general"),
            impact_level=request.metadata.get("impact_level", "MEDIUM"),
            reversibility=request.metadata.get("reversibility", True),
            privacy_risk=request.metadata.get("privacy_risk", False),
            cost_sensitivity="MEDIUM",
            slo_ms=2000
        )
        
        confidence = request.metadata.get("estimated_confidence", 90.0)
        action, reason = policy.evaluate_action(confidence)
        
        if action == "ESCALATE":
            raise RuntimeError(f"Escalation required: {reason}")
        elif action == "DELEGATE_DEEP_RESEARCH":
            raise RuntimeError(f"Delegating to Deep_Research_DAG: {reason}")
            
        primary_route = "gemini-2.0-flash" if action == "ROUTE_PRIMARY" else "claude-3.5-haiku"
        shadow_routes = ["claude-3.7-sonnet"] if allowed else []
        
        # 3. Create Receipt
        commitment = generate_prompt_commitment(request.payload, is_audit=False)
        receipt = DecisionReceipt(
            request_id=request.metadata.get("request_id", "req_000"),
            prompt_commitment=commitment,
            shadow_sampling_policy_id="stratified-random-v1",
            shadow_sampling_policy_hash="sha256:abcd",
            eligible_candidate_set_hash="sha256:efgh",
            primary_route_id=primary_route,
            selected_shadow_routes=shadow_routes,
            predictions={"utility_selected": 0.856, "utility_shadow": 0.841},
            uncertainty_calibrated=confidence,
            propensity_scores={r: 0.02 for r in shadow_routes},
            shadow_allowed=allowed,
            config_hash="sha256:config"
        )
        
        receipt.sign(self.router_key)
        await self.event_store.append(receipt)
        return receipt

    async def _mock_primary_stream(self) -> AsyncGenerator[str, None]:
        yield "Chunk 1 "
        await asyncio.sleep(0.01)
        yield "Chunk 2"

    async def submit(self, request: UserRequest) -> StreamingResponse:
        """
        Main execution flow.
        T0: Decide and Persist.
        T1: Enqueue shadow jobs.
        T2: Return primary stream (never waits for shadow).
        """
        # Causal Note: This intervention is a do(primary_route).
        decision = await self.decide_and_persist(request)
        
        if decision.shadow_allowed:
            for sr in decision.selected_shadow_routes:
                try:
                    await self.dispatcher.enqueue(ShadowJob(sr, {"payload": request.payload}, decision.receipt_id))
                except Exception:
                    pass

        headers = {
            "X-Proof-of-Route-Decision": decision.receipt_id,
            "X-Proof-of-Route-Policy": decision.shadow_sampling_policy_id
        }
        
        return StreamingResponse(self._mock_primary_stream(), headers)
