import nacl.signing
import nacl.encoding
import nacl.exceptions
from cortex.protocols.shadow_router.signing.jcs_rfc8785 import canonicalize


def sign_payload(payload: dict, private_key_hex: str) -> str:
    try:
        private_bytes = bytes.fromhex(private_key_hex)
        signing_key = nacl.signing.SigningKey(private_bytes)
        canonical = canonicalize(payload)
        signed = signing_key.sign(canonical.encode("utf-8"))
        import base64

        return base64.urlsafe_b64encode(signed.signature).decode("utf-8").rstrip("=")
    except RuntimeError as e:
        raise ValueError(f"Firma fallida: {e}")


def verify_envelope(payload: dict, signature_b64url: str, public_key_hex: str) -> bool:
    try:
        public_bytes = bytes.fromhex(public_key_hex)
        verify_key = nacl.signing.VerifyKey(public_bytes)
        import base64

        rem = len(signature_b64url) % 4
        if rem > 0:
            signature_b64url += "=" * (4 - rem)
        signature_bytes = base64.urlsafe_b64decode(signature_b64url)
        canonical = canonicalize(payload)
        verify_key.verify(canonical.encode("utf-8"), signature_bytes)
        return True
    except nacl.exceptions.BadSignatureError:
        return False
    except RuntimeError:
        return False
