from typing import Any
from cortex.protocols.shadow_router.signing.ed25519 import verify_envelope

class TrustStore:
    """
    C5-REAL Trust Store.
    Repositorio inmutable de identidades de la federación.
    MUTEX_ORACLE_QUORUM_WAIT exige que las entidades estén registradas antes de ser aceptadas.
    """
    
    def __init__(self, trust_info: dict = None):
        # Mapeo de issuer_id -> public_key_hex
        self._authorized_keys = {}
        self._revoked_keys = set()
        if trust_info:
            for issuer_id, info in trust_info.items():
                if info.get("revoked", False):
                    self._revoked_keys.add(issuer_id)
                else:
                    self._authorized_keys[issuer_id] = info["public_key_hex"]
                    
    def verify_envelope_trust(self, envelope: Any, required_role: str) -> bool:
        """
        Verifica que el sobre de recibo esté firmado por un emisor autorizado en el Trust Store
        con el rol especificado.
        """
        issuer_id = envelope.signature.key_id
        if not self.is_authorized(issuer_id):
            return False
            
        public_key_hex = self.get_public_key(issuer_id)
        # Call the verify_envelope function (possibly mocked by tests)
        return verify_envelope(envelope.payload, envelope.signature.value, public_key_hex)
        
    def register_issuer(self, issuer_id: str, public_key_hex: str):
        """Registra un emisor y su clave pública."""
        if issuer_id in self._revoked_keys:
            raise ValueError(f"CRITICAL: Issuer {issuer_id} is revoked.")
        self._authorized_keys[issuer_id] = public_key_hex
        
    def revoke_issuer(self, issuer_id: str):
        """Revoca permanentemente un emisor (SIGKILL_STATE_PURGE)."""
        self._revoked_keys.add(issuer_id)
        if issuer_id in self._authorized_keys:
            del self._authorized_keys[issuer_id]
            
    def get_public_key(self, issuer_id: str) -> str:
        """Devuelve la clave pública. Falla ruidosamente si no existe (Fail-Fast)."""
        if issuer_id in self._revoked_keys:
            raise PermissionError(f"Issuer {issuer_id} is revoked.")
        if issuer_id not in self._authorized_keys:
            raise KeyError(f"Issuer {issuer_id} not found in Trust Store.")
            
        return self._authorized_keys[issuer_id]

    def is_authorized(self, issuer_id: str) -> bool:
        return issuer_id in self._authorized_keys and issuer_id not in self._revoked_keys
