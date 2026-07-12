import pytest
from datetime import datetime, timedelta
from cortex.protocols.shadow_router.protocol.schemas import ReceiptEnvelope, SignatureBlock
from cortex.protocols.shadow_router.signing.trust_store import TrustStore
from cortex.protocols.shadow_router.routing.egress_gate import EgressGate

def test_egress_gate_single_use():
    trust_info = {'did:key:z6MkpTHR8VNsBxRcmStjecrxVCoVdPk2yFw6J22tCSZazn1x': {'public_key_hex': '2b3be5d4a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c', 'roles': ['router'], 'valid_from': datetime.now() - timedelta(days=1), 'valid_until': datetime.now() + timedelta(days=1), 'revoked': False}}
    ts = TrustStore(trust_info)
    gate = EgressGate(ts)
    decision_payload = {'receipt_type': 'decision_receipt', 'request_id': 'req-123', 'routing_policy': {'selected_route': 'gemini-2.0-flash', 'selection_propensity_basis_points': 9500, 'candidate_set_hash': 'sha256:candidates', 'policy_version': 'v1', 'features_hash': 'sha256:feat'}, 'shadow_policy': {'eligible': True, 'inclusion_probability_basis_points': 500, 'selection_strategy': 'stratified', 'selected_shadow_routes': [{'route_id': 'claude-3.7-sonnet', 'conditional_inclusion_probability_basis_points': 10000}]}, 'utility_predictions': {'selected_model_utility_basis_points': 8000, 'shadow_candidates_utility_basis_points': {'claude-3.7-sonnet': 8500}, 'utility_spec_hash': 'sha256:util'}, 'privacy_eligibility': {'shadow_allowed': True, 'reasons': [], 'blocked_reasons': [], 'data_classification': 'public', 'region': 'us-east-1', 'privacy_decisions': {'claude-3.7-sonnet': {'provider_approved': True, 'processing_region_allowed': True, 'data_classification_allowed': True, 'legal_basis_present': True}}}, 'prompt_commitment': 'sha256:prompt', 'config_hash': 'sha256:config'}
    import cortex.protocols.shadow_router.signing.trust_store as trust_store_module
    original_verify = trust_store_module.verify_envelope
    trust_store_module.verify_envelope = lambda payload, signature_b64url, public_key_hex: True
    sig_block = SignatureBlock(algorithm='Ed25519', key_id='did:key:z6MkpTHR8VNsBxRcmStjecrxVCoVdPk2yFw6J22tCSZazn1x', value='signature_val', signed_at=datetime.now())
    envelope = ReceiptEnvelope(schema_version='proof-of-route/envelope/v0.2.2', payload_hash='sha256:payload', signature=sig_block, payload=decision_payload)
    permit = gate.authorize_egress(envelope, 'gemini-2.0-flash', purpose='primary')
    assert permit.route_id == 'gemini-2.0-flash'
    gate.consume_permit(permit)
    with pytest.raises(ValueError, match='ya ha sido consumido'):
        gate.consume_permit(permit)
    trust_store_module.verify_envelope = original_verify
