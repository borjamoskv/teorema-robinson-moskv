import os
import stat
import pytest
from kernel import stub_kms
from kernel.stub_sha256 import sha256_bytes, sha256_text, sha256_file, assert_match
from kernel import bft_strict
from kernel.bft_strict import (
    ASTLintNode,
    IntegrityNode,
    MutationPayload,
    TestNode,
    ValidatorNode,
    QUORUM,
    validate_mutation,
    _verify_attestation,
)

NIST_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
NIST_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_sha256_nist_vectors():
    assert sha256_bytes(b"") == NIST_EMPTY
    assert sha256_bytes(b"abc") == NIST_ABC
    assert sha256_text("abc") == NIST_ABC


def test_sha256_no_truncation_lowercase():
    d = sha256_bytes(b"payload")
    assert len(d) == 64 and d == d.lower()
    assert set(d) <= set("0123456789abcdef")


def test_sha256_rejects_str():
    with pytest.raises(TypeError):
        sha256_bytes("no strings")


def test_sha256_streaming_matches_oneshot(tmp_path):
    blob = os.urandom(200 * 1024)
    f = tmp_path / "blob.bin"
    f.write_bytes(blob)
    assert sha256_file(f) == sha256_bytes(blob)


def test_assert_match_crash_over_catch():
    assert assert_match(b"abc", NIST_ABC) == NIST_ABC
    with pytest.raises(SystemExit):
        assert_match(b"abc", NIST_EMPTY)


@pytest.fixture
def kms_env(tmp_path, monkeypatch):
    monkeypatch.setattr(stub_kms, "AUDIT_LOG", tmp_path / "kms_audit.log")
    return tmp_path / "keys"


def test_kms_store_key_born_0600(kms_env):
    p = stub_kms.store_key("k1", b"secret", key_dir=kms_env)
    assert stat.S_IMODE(os.stat(p).st_mode) == 384


def test_kms_enforce_corrects_and_logs(kms_env):
    p = stub_kms.store_key("k2", b"secret", key_dir=kms_env)
    os.chmod(p, 420)
    state = stub_kms.enforce(p)
    assert not state.compliant and state.previous == "0o644"
    assert stat.S_IMODE(os.stat(p).st_mode) == 384
    log = stub_kms.AUDIT_LOG.read_text()
    assert "old=0o644" in log and "new=0o600" in log


def test_kms_idempotent(kms_env):
    p = stub_kms.store_key("k3", b"secret", key_dir=kms_env)
    assert stub_kms.enforce(p).compliant
    assert stub_kms.enforce(p).compliant


def test_kms_boot_scan_recursive(kms_env):
    p = stub_kms.store_key("k4", b"secret", key_dir=kms_env)
    os.chmod(p, 493)
    results = stub_kms.boot_scan(kms_env)
    assert any((not r.compliant for r in results))
    assert stat.S_IMODE(os.stat(p).st_mode) == 384


def test_kms_rejects_path_escape(kms_env):
    with pytest.raises(ValueError):
        stub_kms.store_key("../../etc/evil", b"x", key_dir=kms_env)


@pytest.fixture
def bft_env(tmp_path, monkeypatch):
    monkeypatch.setattr(stub_kms, "AUDIT_LOG", tmp_path / "kms_audit.log")
    key = os.urandom(32)
    monkeypatch.setattr(bft_strict, "_attestation_key", lambda: key)
    return {"key": key, "merkle": tmp_path / "merkle.jsonl"}


def _payload(src: bytes, falsification=lambda: True, digest=None, ct="python"):
    return MutationPayload(
        diff=src,
        author="test",
        timestamp="2026-07-12T00:00:00Z",
        declared_digest=digest or sha256_bytes(src),
        content_type=ct,
        falsification=falsification,
    )


def test_bft_quorum_3_of_3_commits(bft_env):
    r = validate_mutation(_payload(b"x = 1\n"), merkle_log=bft_env["merkle"])
    assert r.accepted and r.quorum == QUORUM == 3
    assert len(r.attestations) == 3 and len(r.merkle_root) == 64
    d = sha256_bytes(b"x = 1\n")
    for node, att in zip(bft_strict.VALIDATORS, r.attestations):
        assert _verify_attestation(node.node_id, d, att, bft_env["key"])
        assert not _verify_attestation(node.node_id, d, "0" * 64, bft_env["key"])


def test_bft_rejects_integrity_violation(bft_env):
    r = validate_mutation(
        _payload(b"x = 1\n", digest="f" * 64), merkle_log=bft_env["merkle"]
    )
    assert not r.accepted and r.quorum == 0
    assert not bft_env["merkle"].exists()


def test_bft_rejects_syntax_error(bft_env):
    r = validate_mutation(_payload(b"def broken(:\n"), merkle_log=bft_env["merkle"])
    assert not r.accepted and r.quorum == 2


def test_bft_no_test_no_vote(bft_env):
    r = validate_mutation(
        _payload(b"x = 1\n", falsification=None), merkle_log=bft_env["merkle"]
    )
    assert not r.accepted and r.quorum == 2


def test_bft_crashing_test_is_failing_test(bft_env):

    def boom():
        raise RuntimeError("empirical failure")

    r = validate_mutation(
        _payload(b"x = 1\n", falsification=boom), merkle_log=bft_env["merkle"]
    )
    assert not r.accepted


def test_bft_merkle_chain_linkage(bft_env):
    r1 = validate_mutation(_payload(b"a = 1\n"), merkle_log=bft_env["merkle"])
    r2 = validate_mutation(_payload(b"b = 2\n"), merkle_log=bft_env["merkle"])
    d2 = sha256_bytes(b"b = 2\n")
    assert r2.merkle_root == sha256_bytes(f"{r1.merkle_root}{d2}".encode())


def test_bft_is_mock_structurally_forbidden():
    with pytest.raises(TypeError):

        class MockNode(ValidatorNode):
            is_mock = True


def test_bft_nodes_are_real_not_constant():
    bad_integrity = _payload(b"x = 1\n", digest="a" * 64)
    assert IntegrityNode().verify(bad_integrity) is False
    assert ASTLintNode().verify(_payload(b"def x(:\n")) is False
    assert TestNode().verify(_payload(b"x = 1\n", falsification=lambda: False)) is False
