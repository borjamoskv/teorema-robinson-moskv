import asyncio
from typing import Dict, Any, AsyncGenerator
from cortex.protocols.shadow_router.protocol.schemas import (
    ReceiptEnvelope,
    SignatureBlock,
    DecisionReceipt,
    RoutingPolicy,
    ShadowPolicy,
    ShadowRouteSelection,
    UtilityPredictions,
    PrivacyEligibilityResult,
)
from cortex.protocols.shadow_router.routing.egress_gate import EgressGate
from cortex.protocols.shadow_router.signing.jcs_rfc8785 import canonical_hash
from datetime import datetime


class MockProviderClient:
    def __init__(self, egress_gate: EgressGate) -> "Any":
        self.egress_gate = egress_gate

    async def invoke_streaming(
        self, permit: Any, delay_ms: int = 10
    ) -> AsyncGenerator[str, None]:
        self.egress_gate.consume_permit(permit)
        yield "Chunk 1"
        await asyncio.sleep(delay_ms / 1000.0)
        yield " Chunk 2"


class ShadowRouter:
    def __init__(
        self,
        egress_gate: EgressGate,
        provider_client: MockProviderClient,
        router_key_hex: str,
        key_id: str,
    ):
        self.egress_gate = egress_gate
        self.provider_client = provider_client
        self.router_key_hex = router_key_hex
        self.key_id = key_id

    async def route_request(
        self, request_payload: str, metadata: Dict[str, Any]
    ) -> ReceiptEnvelope:
        routing_policy = RoutingPolicy(
            selected_route="gemini-2.0-flash",
            selection_propensity_basis_points=9500,
            candidate_set_hash="sha256:candidates",
            policy_version="v0.2.2-policy",
            features_hash="sha256:features",
        )
        shadow_selection = ShadowRouteSelection(
            route_id="claude-3.7-sonnet",
            conditional_inclusion_probability_basis_points=500,
        )
        shadow_policy = ShadowPolicy(
            eligible=metadata.get("shadow_eligible", True),
            inclusion_probability_basis_points=500,
            selection_strategy="stratified-random",
            selected_shadow_routes=[shadow_selection]
            if metadata.get("shadow_eligible", True)
            else [],
        )
        utility_preds = UtilityPredictions(
            selected_model_utility_basis_points=8500,
            shadow_candidates_utility_basis_points={"claude-3.7-sonnet": 8200},
            utility_spec_hash="sha256:utility_spec",
        )
        privacy_result = PrivacyEligibilityResult(
            shadow_allowed=metadata.get("privacy_allowed", True),
            reasons=["Legal base check passed"],
            blocked_reasons=[],
            data_classification="public",
            region="us-east-1",
            privacy_decisions={
                "claude-3.7-sonnet": {
                    "provider_approved": True,
                    "processing_region_allowed": True,
                    "data_classification_allowed": True,
                    "legal_basis_present": True,
                }
            },
        )
        decision = DecisionReceipt(
            request_id=metadata.get("request_id", "req-001"),
            routing_policy=routing_policy,
            shadow_policy=shadow_policy,
            utility_predictions=utility_preds,
            privacy_eligibility=privacy_result,
            prompt_commitment="sha256:prompt_commitment",
            config_hash="sha256:config",
        )
        payload_dict = decision.model_dump()
        p_hash = canonical_hash(payload_dict)
        from cortex.protocols.shadow_router.signing.ed25519 import sign_payload

        sig_val = sign_payload(payload_dict, self.router_key_hex)
        sig_block = SignatureBlock(
            algorithm="Ed25519",
            key_id=self.key_id,
            value=sig_val,
            signed_at=datetime.now(),
        )
        envelope = ReceiptEnvelope(
            schema_version="proof-of-route/envelope/v0.2.2",
            parent_signed_receipt_hash=None,
            payload_hash=p_hash,
            signature=sig_block,
            payload=payload_dict,
        )
        return envelope
