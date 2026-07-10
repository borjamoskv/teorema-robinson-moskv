from typing import Dict, Any, Optional
from datetime import datetime
from cortex.protocols.shadow_router.protocol.schemas import ReceiptEnvelope
from cortex.protocols.shadow_router.signing.ed25519 import verify_envelope

class TrustStore:
    def __init__(self, trusted_keys: Dict[str, Dict[str, Any]]):
        """
        trusted_keys maps did_key -> {
            "public_key_hex": str,
            "roles": List[str],
            "valid_from": datetime,
            "valid_until": datetime,
            "revoked": bool
        }
        """
        self.trusted_keys = trusted_keys

    def verify_envelope_trust(self, envelope: ReceiptEnvelope, required_role: str) -> bool:
        key_id = envelope.signature.key_id
        if key_id not in self.trusted_keys:
            return False
            
        key_info = self.trusted_keys[key_id]
        if key_info.get("revoked", False):
            return False
            
        now = datetime.now()
        if not (key_info["valid_from"] <= now <= key_info["valid_until"]):
            return False
            
        if required_role not in key_info.get("roles", []):
            return False
            
        # Verify signature
        return verify_envelope(
            payload=envelope.payload,
            signature_b64url=envelope.signature.value,
            public_key_hex=key_info["public_key_hex"]
        )
