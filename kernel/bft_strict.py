"""STUB-BFT-STRICT-001 — Validador de Consenso BFT Estricto (C5-REAL).

Materialización física de cortex/ontology/stub_bft_strict.yaml.
Remediación directa de babylon_60_audit: "Tres nodos mock devolviendo
constante hardcodeada is_mock=True".

Los 3 nodos NO son servidores distribuidos sino capas de verificación
ortogonales [PRIM-005]:
  - IntegrityNode: SHA-256 real del payload vs digest declarado (STUB-SHA256-001)
  - ASTLintNode:   validación sintáctica real (ast.parse / UTF-8 estricto)
  - TestNode:      falsación empírica — sin test ejecutable, no hay voto

Parámetros: N=3, f=0, quórum=3/3 estricto. Sin quórum, sin commit.
Attestations: HMAC-SHA256 con clave local del KMS (STUB-KMS-0600-001).
Fail_Mode: reject_and_log. No idempotente: cada commit muta el Merkle Tree.

Dependency_Chain (acíclica): STUB-SHA256-001, STUB-KMS-0600-001.
Prohibido is_mock=True en cualquier nodo validador.
"""

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

# BFT_Parameters del stub
N = 3
F = 0
QUORUM = 3  # modo estricto: 3/3
assert QUORUM >= (2 * F) + 1, "Assertion del stub: quórum >= 2f+1"

ATTESTATION_KEY_NAME = "bft_attestation.key"
DEFAULT_MERKLE_LOG = Path(__file__).resolve().parent / "merkle_chain.jsonl"


@dataclass(frozen=True)
class MutationPayload:
    """Input del stub: mutation_payload {diff, author, timestamp}."""
    diff: bytes
    author: str
    timestamp: str  # iso8601
    declared_digest: str  # SHA-256 declarado por el proponente
    content_type: str = "python"  # 'python' | 'bytes'
    falsification: Optional[Callable[[], bool]] = None  # test ejecutable


@dataclass(frozen=True)
class ConsensusResult:
    """Output del stub: {accepted, quorum, attestations}."""
    accepted: bool
    quorum: int
    attestations: list = field(default_factory=list)  # list[hex_digest]
    reason: str = ""
    merkle_root: str = ""


def _attestation_key() -> bytes:
    """Clave HMAC local vía STUB-KMS-0600-001. Se crea si no existe."""
    try:
        return stub_kms.load_key(ATTESTATION_KEY_NAME)
    except FileNotFoundError:
        import secrets
        material = secrets.token_bytes(32)
        stub_kms.store_key(ATTESTATION_KEY_NAME, material)
        return material


def _sign(node_id: str, payload_digest: str, key: bytes) -> str:
    """Attestation = HMAC-SHA256(node_id || digest). Verificable, no mock."""
    msg = f"{node_id}:{payload_digest}".encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def _verify_attestation(node_id: str, payload_digest: str,
                        attestation: str, key: bytes) -> bool:
    expected = _sign(node_id, payload_digest, key)
    return hmac.compare_digest(expected, attestation)


# ---------------------------------------------------------------- nodos ---

class ValidatorNode:
    """Base. is_mock queda estructuralmente prohibido: no existe el atributo
    y cualquier intento de definirlo revienta en __init_subclass__."""

    node_id: str = "base"

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if "is_mock" in cls.__dict__:
            raise TypeError("Prohibido is_mock en nodos validadores "
                            "[STUB-BFT-STRICT-001]")

    def verify(self, payload: MutationPayload) -> bool:  # pragma: no cover
        raise NotImplementedError("Nodo abstracto: sin verificación real, sin voto")


class IntegrityNode(ValidatorNode):
    """Nodo 1 — Git Sentinel / ancla criptográfica [RED-001, INV-012]."""
    node_id = "integrity-sha256"

    def verify(self, payload: MutationPayload) -> bool:
        return sha256_bytes(payload.diff) == payload.declared_digest.lower()


class ASTLintNode(ValidatorNode):
    """Nodo 2 — validación sintáctica real, sin subprocess."""
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
    """Nodo 3 — falsación empírica. Sin test ejecutable no hay voto:
    la ausencia de test es rechazo, no aprobación tácita [ANTI-008]."""
    node_id = "test-suite"

    def verify(self, payload: MutationPayload) -> bool:
        if payload.falsification is None:
            return False
        # K1 FAIL-FAST: Un test que crashea por error de sintaxis/runtime
        # NO ES un test que falla pacíficamente, es un colapso del AST.
        return bool(payload.falsification())


VALIDATORS: tuple[ValidatorNode, ...] = (IntegrityNode(), ASTLintNode(), TestNode())
assert len(VALIDATORS) == N, "Mínimo 3 nodos validadores (N=3)"


# --------------------------------------------------------- merkle commit ---

def _merkle_commit(payload_digest: str, attestations: list[str],
                   log_path: Path) -> str:
    """Side effect único y condicionado a quórum: append al Merkle chain.
    root_n = SHA256(root_{n-1} || payload_digest). Append-only."""
    prev_root = "0" * 64
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        if lines:
            prev_root = json.loads(lines[-1])["root"]
    root = sha256_bytes(f"{prev_root}{payload_digest}".encode("utf-8"))
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
             "payload_digest": payload_digest,
             "attestations": attestations,
             "prev_root": prev_root, "root": root}
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, separators=(",", ":")) + "\n")
    return root


def _reject(reason: str, quorum: int, attestations: list[str]) -> ConsensusResult:
    """Fail_Mode: reject_and_log."""
    print(f"REJECT [STUB-BFT-STRICT-001]: {reason} "
          f"(quorum={quorum}/{QUORUM})", file=sys.stderr)
    return ConsensusResult(False, quorum, attestations, reason)


# ------------------------------------------------------------- consenso ---

def validate_mutation(payload: MutationPayload,
                      merkle_log: str | Path = DEFAULT_MERKLE_LOG) -> ConsensusResult:
    """Punto de entrada del stub. Toda mutación de estado pasa por aquí.

    1. Integridad del payload vía STUB-SHA256-001 antes de proponer.
    2. Cada nodo ejecuta verificación REAL y, solo si pasa, firma attestation.
    3. len(valid_attestations) >= 2f+1 (estricto: == 3) OR REJECT.
    4. Commit al Merkle Tree solo si quórum alcanzado.
    """
    # Paso 1: pre-verificación de integridad (dependencia STUB-SHA256-001)
    if sha256_bytes(payload.diff) != payload.declared_digest.lower():
        return _reject("payload integrity failure (pre-propose)", 0, [])

    key = _attestation_key()
    payload_digest = payload.declared_digest.lower()

    # Paso 2: votación con verificación real por nodo
    attestations: list[str] = []
    for node in VALIDATORS:
        if node.verify(payload):
            att = _sign(node.node_id, payload_digest, key)
            if _verify_attestation(node.node_id, payload_digest, att, key):
                attestations.append(att)

    # Paso 3: assertion de quórum
    quorum = len(attestations)
    if quorum < QUORUM or quorum < (2 * F) + 1:
        return _reject("quorum not reached", quorum, attestations)

    # Paso 4: commit condicionado
    root = _merkle_commit(payload_digest, attestations, Path(merkle_log))
    return ConsensusResult(True, quorum, attestations,
                           "quorum 3/3 — committed", root)


if __name__ == "__main__":
    src = b"x = 1\n"
    p = MutationPayload(diff=src, author="borja",
                        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        declared_digest=sha256_bytes(src),
                        falsification=lambda: True)
    r = validate_mutation(p)
    print(f"STUB-BFT-STRICT-001: accepted={r.accepted} "
          f"quorum={r.quorum}/{QUORUM} root={r.merkle_root[:16]}… [C5-REAL]")
