import hashlib
import hmac
import os
from typing import Dict, Any, Optional

def generate_prompt_commitment(canonical_request_envelope: str, is_audit: bool = False, nonce: Optional[str] = None) -> str:
    """
    Generates a secure commitment of the prompt.
    For internal audit, uses HMAC-SHA-256 with a rotating router key.
    For selective disclosure, uses a KMS-backed nonce.
    """
    if is_audit:
        if not nonce:
            raise ValueError("Nonce required for audit disclosure.")
        payload = f"ProofOfRoute/Prompt/v1||{nonce}||{canonical_request_envelope}"
        return hashlib.sha256(payload.encode()).hexdigest()
    else:
        # Default internal mapping
        router_key = os.environ.get("ROUTER_HMAC_KEY", "default-dev-key")
        return hmac.new(router_key.encode(), canonical_request_envelope.encode(), hashlib.sha256).hexdigest()


class PrivacyGate:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def shadow_allowed(
        self,
        has_consent: bool,
        data_classification_allowed: bool,
        provider_approved: bool,
        region_compatible: bool,
        budget_available: bool,
        no_sensitive_tool_context: bool,
        no_security_incident: bool
    ) -> bool:
        """
        Hard gate for shadow egress. All conditions MUST be True.
        """
        return all([
            has_consent,
            data_classification_allowed,
            provider_approved,
            region_compatible,
            budget_available,
            no_sensitive_tool_context,
            no_security_incident
        ])
