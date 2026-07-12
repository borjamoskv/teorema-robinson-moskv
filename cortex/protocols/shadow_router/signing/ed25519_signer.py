import json
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

def canonicalize_json(payload: dict) -> bytes:
    return json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False).encode('utf-8')

class Ed25519Signer:

    def __init__(self, private_key_hex: str):
        self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
        self._public_key = self._private_key.public_key()

    @property
    def public_key_hex(self) -> str:
        from cryptography.hazmat.primitives import serialization
        raw = self._public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        return raw.hex()

    def sign_payload(self, payload: dict) -> dict:
        canonical_bytes = canonicalize_json(payload)
        payload_hash = 'sha256:' + hashlib.sha256(canonical_bytes).hexdigest()
        signature_bytes = self._private_key.sign(payload_hash.encode('utf-8'))
        signature_b64 = base64.urlsafe_b64encode(signature_bytes).decode('utf-8').rstrip('=')
        return {'payload_hash': payload_hash, 'signature': {'algorithm': 'Ed25519', 'value': signature_b64}}

def verify_signature(public_key_hex: str, payload: dict, payload_hash: str, signature_b64: str) -> bool:
    canonical_bytes = canonicalize_json(payload)
    computed_hash = 'sha256:' + hashlib.sha256(canonical_bytes).hexdigest()
    if computed_hash != payload_hash:
        return False
    try:
        padding = '=' * (4 - len(signature_b64) % 4)
        signature_bytes = base64.urlsafe_b64decode(signature_b64 + padding)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        public_key.verify(signature_bytes, payload_hash.encode('utf-8'))
        return True
    except (InvalidSignature, ValueError):
        return False
