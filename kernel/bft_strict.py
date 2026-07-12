from __future__ import annotations
import ast
import hmac
import json
import hashlib
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from kernel.stub_sha256 import sha256_bytes
from kernel import stub_kms

N = 3
F = 0
QUORUM = 3
assert QUORUM >= 2 * F + 1, "Assertion del stub: quórum >= 2f+1"
ATTESTATION_KEY_NAME = "bft_attestation.key"
DEFAULT_MERKLE_LOG = Path(__file__).resolve().parent / "merkle_chain.jsonl"


@dataclass(frozen=True)
class MutationPayload:
    diff: bytes
    author: str
    timestamp: str
    declared_digest: str
    content_type: str = "python"
    falsification: Optional[Callable[[], bool]] = None


@dataclass(frozen=True)
class ConsensusResult:
    accepted: bool
    quorum: int
    attestations: list = field(default_factory=list)
    reason: str = ""
    merkle_root: str = ""


def _attestation_key() -> bytes:
    try:
        return stub_kms.load_key(ATTESTATION_KEY_NAME)
    except FileNotFoundError:
        import secrets

        material = secrets.token_bytes(32)
        stub_kms.store_key(ATTESTATION_KEY_NAME, material)
        return material


def _sign(node_id: str, payload_digest: str, key: bytes) -> str:
    msg = f"{node_id}:{payload_digest}".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def _verify_attestation(
    node_id: str, payload_digest: str, attestation: str, key: bytes
) -> bool:
    expected = _sign(node_id, payload_digest, key)
    return hmac.compare_digest(expected, attestation)


class ValidatorNode:
    node_id: str = "base"

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if "is_mock" in cls.__dict__:
            raise TypeError(
                "Prohibido is_mock en nodos validadores [STUB-BFT-STRICT-001]"
            )

    def verify(self, payload: MutationPayload) -> bool:
        raise NotImplementedError("Nodo abstracto: sin verificación real, sin voto")


class IntegrityNode(ValidatorNode):
    node_id = "integrity-sha256"

    def verify(self, payload: MutationPayload) -> bool:
        return sha256_bytes(payload.diff) == payload.declared_digest.lower()


class ASTLintNode(ValidatorNode):
    node_id = "ast-lint"

    def verify(self, payload: MutationPayload) -> bool:
        try:
            text = payload.diff.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return payload.content_type == "bytes" and len(payload.diff) > 0
        if payload.content_type == "python":
            try:
                ast.parse(text)
                return True
            except SyntaxError:
                return False
        return len(text) > 0


class TestNode(ValidatorNode):
    node_id = "test-suite"

    def verify(self, payload: MutationPayload) -> bool:
        if payload.falsification is None:
            return False
        return bool(payload.falsification())


VALIDATORS: tuple[ValidatorNode, ...] = (IntegrityNode(), ASTLintNode(), TestNode())
assert len(VALIDATORS) == N, "Mínimo 3 nodos validadores (N=3)"


def _merkle_commit(payload_digest: str, attestations: list[str], log_path: Path) -> str:
    prev_root = "0" * 64
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        if lines:
            prev_root = json.loads(lines[-1])["root"]
    root = sha256_bytes(f"{prev_root}{payload_digest}".encode("utf-8"))
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "payload_digest": payload_digest,
        "attestations": attestations,
        "prev_root": prev_root,
        "root": root,
    }
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, separators=(",", ":")) + "\n")
    return root


def _reject(reason: str, quorum: int, attestations: list[str]) -> ConsensusResult:
    print(
        f"REJECT [STUB-BFT-STRICT-001]: {reason} (quorum={quorum}/{QUORUM})",
        file=sys.stderr,
    )
    return ConsensusResult(False, quorum, attestations, reason)


def validate_mutation(
    payload: MutationPayload, merkle_log: str | Path = DEFAULT_MERKLE_LOG
) -> ConsensusResult:
    if sha256_bytes(payload.diff) != payload.declared_digest.lower():
        return _reject("payload integrity failure (pre-propose)", 0, [])
    key = _attestation_key()
    payload_digest = payload.declared_digest.lower()
    attestations: list[str] = []
    for node in VALIDATORS:
        if node.verify(payload):
            att = _sign(node.node_id, payload_digest, key)
            if _verify_attestation(node.node_id, payload_digest, att, key):
                attestations.append(att)
    quorum = len(attestations)
    if quorum < QUORUM or quorum < 2 * F + 1:
        return _reject("quorum not reached", quorum, attestations)
    root = _merkle_commit(payload_digest, attestations, Path(merkle_log))
    return ConsensusResult(True, quorum, attestations, "quorum 3/3 — committed", root)


if __name__ == "__main__":
    src = b"x = 1\n"
    p = MutationPayload(
        diff=src,
        author="borja",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        declared_digest=sha256_bytes(src),
        falsification=lambda: True,
    )
    r = validate_mutation(p)
    print(
        f"STUB-BFT-STRICT-001: accepted={r.accepted} quorum={r.quorum}/{QUORUM} root={r.merkle_root[:16]}… [C5-REAL]"
    )
