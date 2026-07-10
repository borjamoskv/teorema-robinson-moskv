import uuid
from datetime import datetime, timedelta
from typing import Set
from cortex.protocols.shadow_router.protocol.schemas import ReceiptEnvelope, EgressPermit
from cortex.protocols.shadow_router.signing.trust_store import TrustStore

class EgressGate:
    def __init__(self, trust_store: TrustStore):
        self.trust_store = trust_store
        self.used_permits: Set[str] = set()

    def authorize_egress(
        self,
        decision_envelope: ReceiptEnvelope,
        route_id: str,
        purpose: str,  # "primary" or "shadow"
        validity_seconds: int = 30
    ) -> EgressPermit:
        """
        Validates the signed DecisionReceipt and issues a one-time EgressPermit.
        """
        # 1. Verify Trust
        if not self.trust_store.verify_envelope_trust(decision_envelope, required_role="router"):
            raise PermissionError("Fallo de confianza en el DecisionReceipt firmado.")
            
        decision = decision_envelope.payload
        # Convert dict payload back to semantic fields or read them directly
        # Since payload is dict due to JCS serialization:
        routing_policy = decision["routing_policy"]
        shadow_policy = decision["shadow_policy"]
        privacy = decision["privacy_eligibility"]
        
        # 2. Check route authorization
        authorized = False
        if purpose == "primary":
            authorized = (routing_policy["selected_route"] == route_id)
        elif purpose == "shadow":
            authorized = any(sr["route_id"] == route_id for sr in shadow_policy["selected_shadow_routes"])
            
        if not authorized:
            raise PermissionError(f"Route_id {route_id} no autorizado para propósito {purpose}.")
            
        # 3. Privacy egress check
        if purpose == "shadow":
            route_decision = privacy["privacy_decisions"].get(route_id)
            if not route_decision or not route_decision["provider_approved"] or not route_decision["processing_region_allowed"]:
                raise PermissionError(f" shadow route {route_id} bloqueada por compliance/privacidad.")
                
        # 4. Issue Permit
        now = datetime.now()
        permit = EgressPermit(
            issuer="did:web:router.cortex.internal",
            decision_signed_receipt_hash=decision_envelope.payload_hash,
            route_id=route_id,
            purpose=purpose,
            permit_id=str(uuid.uuid4()),
            issued_at=now,
            expires_at=now + timedelta(seconds=validity_seconds),
            single_use=True
        )
        return permit

    def consume_permit(self, permit: EgressPermit) -> None:
        """Consumes a permit, ensuring single-use and expiration checks."""
        now = datetime.now()
        if now > permit.expires_at:
            raise ValueError("El EgressPermit ha expirado.")
            
        if permit.permit_id in self.used_permits:
            raise ValueError("El EgressPermit ya ha sido consumido.")
            
        if permit.single_use:
            self.used_permits.add(permit.permit_id)
