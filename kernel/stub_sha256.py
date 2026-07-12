"""STUB-SHA256-001 — Verificador de Integridad SHA-256 (C5-REAL).

Materialización física de cortex/ontology/stub_sha256_integrity.yaml.
Invariantes: INV-012 (Hash Estructural), RED-016 (Triple-Hash).

Propiedades: determinista, pura, idempotente, sin efectos laterales.
Fail_Mode: crash_over_catch — la corrupción no se captura, se aborta.

Constraints enforced:
  - Sin fallback a MD5 (solo hashlib.sha256, verificado en boot).
  - Sin truncamiento: digest siempre 64 hex chars lowercase.
  - UTF-8 estricto para str, raw para bytes.
  - Streaming con buffer fijo de 64KB para archivos.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BUFFER_SIZE = 64 * 1024  # 64KB fijo — constraint del stub
DIGEST_LEN = 64          # SHA-256 hex: sin truncamiento

# Boot assertion: sha256 disponible, sin degradación posible a MD5.
if "sha256" not in hashlib.algorithms_guaranteed:  # pragma: no cover
    print("CRITICAL HALT [STUB-SHA256-001]: sha256 no garantizado en hashlib.",
          file=sys.stderr)
    sys.exit(1)


def sha256_bytes(raw: bytes) -> str:
    """bytes_in → digest_out. Función pura, cero estado mutable."""
    if not isinstance(raw, bytes):
        raise TypeError("STUB-SHA256-001 acepta bytes crudos; "
                        "para str usar sha256_text (UTF-8 estricto).")
    digest = hashlib.sha256(raw).hexdigest()
    assert len(digest) == DIGEST_LEN, "Truncamiento prohibido"
    return digest


def sha256_text(text: str) -> str:
    """Encoding UTF-8 estricto — errors='strict', nunca 'replace'."""
    return sha256_bytes(text.encode("utf-8", errors="strict"))


def sha256_file(path: str | Path) -> str:
    """Streaming hash con buffer fijo de 64KB."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(BUFFER_SIZE):
            h.update(chunk)
    digest = h.hexdigest()
    assert len(digest) == DIGEST_LEN, "Truncamiento prohibido"
    return digest


def assert_match(raw: bytes, expected_digest: str) -> str:
    """Verificación atómica: hash + assert en operación indivisible.

    Assertion del stub: digest == expected_digest OR SIGKILL.
    No hay estado intermedio observable entre hash y assert.
    """
    actual = sha256_bytes(raw)
    if actual != expected_digest.lower():
        print(f"CRITICAL HALT [STUB-SHA256-001]: integrity violation. "
              f"expected={expected_digest.lower()} actual={actual}",
              file=sys.stderr)
        sys.exit(1)  # crash_over_catch
    return actual


if __name__ == "__main__":
    # Vector de auto-verificación (NIST FIPS 180-4, mensaje vacío)
    EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert_match(b"", EMPTY)
    print("STUB-SHA256-001 verified [C5-REAL]")
