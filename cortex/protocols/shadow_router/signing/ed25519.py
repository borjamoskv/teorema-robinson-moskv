import nacl.signing
import nacl.encoding
import nacl.exceptions
from cortex.protocols.shadow_router.signing.jcs_rfc8785 import canonicalize

def sign_payload(payload: dict, private_key_hex: str) -> str:
    """Signs JCS payload and returns base64url encoded signature."""
    try:
        private_bytes = bytes.fromhex(private_key_hex)
        signing_key = nacl.signing.SigningKey(private_bytes)
        canonical = canonicalize(payload)
        signed = signing_key.sign(canonical.encode('utf-8'))
        # Return base64url-like representation or hex. Let's use hex for ease, or true base64url.
        # RFC 8785 signature vectors often use base64url. We'll use urlsafe base64.
        import base64
        return base64.urlsafe_b64encode(signed.signature).decode('utf-8').rstrip('=')
    except RuntimeError as e:
        raise ValueError(f"Firma fallida: {e}")

def verify_envelope(payload: dict, signature_b64url: str, public_key_hex: str) -> bool:
    """Verifies JCS payload signature."""
    try:
        public_bytes = bytes.fromhex(public_key_hex)
        verify_key = nacl.signing.VerifyKey(public_bytes)
        import base64
        # Add padding back if missing
        rem = len(signature_b64url) % 4
        if rem > 0:
            signature_b64url += '=' * (4 - rem)
        signature_bytes = base64.urlsafe_b64decode(signature_b64url)
        canonical = canonicalize(payload)
        verify_key.verify(canonical.encode('utf-8'), signature_bytes)
        return True
    except nacl.exceptions.BadSignatureError:
        return False
    except RuntimeError:
        return False
