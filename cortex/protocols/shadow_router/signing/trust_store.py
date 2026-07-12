from typing import Any
from cortex.protocols.shadow_router.signing.ed25519 import verify_envelope

class TrustStore:

    def __init__(self, trust_info: dict=None):
        self._authorized_keys = {}
        self._revoked_keys = set()
        if trust_info:
            for issuer_id, info in trust_info.items():
                if info.get('revoked', False):
                    self._revoked_keys.add(issuer_id)
                else:
                    self._authorized_keys[issuer_id] = info['public_key_hex']

    def verify_envelope_trust(self, envelope: Any, required_role: str) -> bool:
        issuer_id = envelope.signature.key_id
        if not self.is_authorized(issuer_id):
            return False
        public_key_hex = self.get_public_key(issuer_id)
        return verify_envelope(envelope.payload, envelope.signature.value, public_key_hex)

    def register_issuer(self, issuer_id: str, public_key_hex: str):
        if issuer_id in self._revoked_keys:
            raise ValueError(f'CRITICAL: Issuer {issuer_id} is revoked.')
        self._authorized_keys[issuer_id] = public_key_hex

    def revoke_issuer(self, issuer_id: str):
        self._revoked_keys.add(issuer_id)
        if issuer_id in self._authorized_keys:
            del self._authorized_keys[issuer_id]

    def get_public_key(self, issuer_id: str) -> str:
        if issuer_id in self._revoked_keys:
            raise PermissionError(f'Issuer {issuer_id} is revoked.')
        if issuer_id not in self._authorized_keys:
            raise KeyError(f'Issuer {issuer_id} not found in Trust Store.')
        return self._authorized_keys[issuer_id]

    def is_authorized(self, issuer_id: str) -> bool:
        return issuer_id in self._authorized_keys and issuer_id not in self._revoked_keys
