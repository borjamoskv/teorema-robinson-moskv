# sha256_attestor.py | Nivel de Realidad: #C5-REAL | Mitigación: P0 (aserción forjada)
# Stub atómico físico: toda aserción de trabajo debe referenciar digests de disco, no prosa.
# I/O real, sin mocks. stdlib únicamente.
import hashlib
import json
import os
import sys
import time

_CHUNK = 1 << 20  # 1 MiB


def sha256_file(path: str) -> str:
    """Digest SHA-256 de un fichero físico, en streaming (O(1) memoria)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def attest(path: str) -> dict:
    """Atestación falsable de un artefacto: ruta, digest, tamaño, timestamp."""
    ap = os.path.abspath(path)
    st = os.stat(ap)
    return {
        "path": ap,
        "sha256": sha256_file(ap),
        "bytes": st.st_size,
        "mtime": int(st.st_mtime),
        "ts": int(time.time()),
    }


def verify(path: str, expected_sha256: str) -> bool:
    """Verificación estricta: comparación de digest completa, sin prefijos."""
    return sha256_file(path) == expected_sha256.lower()


def _selftest() -> int:
    import tempfile

    payload = b"C5-REAL: los artefactos no se argumentan, se hashean.\n"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(payload)
        tmp = f.name
    try:
        expected = hashlib.sha256(payload).hexdigest()
        a = attest(tmp)
        assert a["sha256"] == expected, "digest de streaming != digest directo"
        assert a["bytes"] == len(payload)
        assert verify(tmp, expected)
        assert not verify(tmp, "0" * 64)
        print("[C5-REAL] sha256_attestor: SELFTEST OK")
        return 0
    finally:
        os.unlink(tmp)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            print(json.dumps(attest(p), separators=(",", ":")))
    else:
        sys.exit(_selftest())
