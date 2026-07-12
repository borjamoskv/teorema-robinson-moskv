import pytest
import secrets
from cortex.protocols.shadow_router.signing.ed25519_signer import (
    Ed25519Signer,
    verify_signature,
    canonicalize_json,
)
from cortex.protocols.shadow_router.signing.trust_store import TrustStore


def test_strict_canonicalization():
    payload1 = {"z": 1, "a": "hello"}
    payload2 = {"a": "hello", "z": 1}
    bytes1 = canonicalize_json(payload1)
    bytes2 = canonicalize_json(payload2)
    assert bytes1 == bytes2
    assert b" " not in bytes1


def test_ed25519_signing_and_verification():
    private_key_hex = secrets.token_bytes(32).hex()
    signer = Ed25519Signer(private_key_hex)
    public_key_hex = signer.public_key_hex
    payload = {"decision": "route_A", "confidence": 0.99, "timestamp": 1234567890}
    sig_data = signer.sign_payload(payload)
    is_valid = verify_signature(
        public_key_hex,
        payload,
        sig_data["payload_hash"],
        sig_data["signature"]["value"],
    )
    assert is_valid is True


def test_ed25519_tampered_payload_fails():
    private_key_hex = secrets.token_bytes(32).hex()
    signer = Ed25519Signer(private_key_hex)
    public_key_hex = signer.public_key_hex
    payload = {"decision": "route_A"}
    sig_data = signer.sign_payload(payload)
    tampered_payload = {"decision": "route_B"}
    is_valid = verify_signature(
        public_key_hex,
        tampered_payload,
        sig_data["payload_hash"],
        sig_data["signature"]["value"],
    )
    assert is_valid is False


def test_trust_store_fail_fast():
    store = TrustStore()
    store.register_issuer("did:cortex:router1", "aabbccdd")
    assert store.get_public_key("did:cortex:router1") == "aabbccdd"
    store.revoke_issuer("did:cortex:router1")
    with pytest.raises(PermissionError):
        store.get_public_key("did:cortex:router1")
    with pytest.raises(KeyError):
        store.get_public_key("did:cortex:router2")
