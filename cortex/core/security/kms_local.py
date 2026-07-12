# kms_local.py | Nivel de Realidad: #C5-REAL | Mitigación: P0 (exfiltración de material de clave)
# Stub atómico físico: almacén local de claves con 0600 forzado e inspección estricta de permisos.
# Escritura atómica (O_EXCL + os.replace). I/O real, sin mocks. stdlib únicamente.
import os
import stat
import sys


class KMSError(RuntimeError):
    pass


def _kms_dir() -> str:
    d = os.environ.get("CORTEX_KMS_DIR", os.path.expanduser("~/.cortex/kms"))
    os.makedirs(d, mode=0o700, exist_ok=True)
    os.chmod(d, 0o700)  # forzado incluso si ya existía
    return d


def _assert_mode(path: str, want: int) -> None:
    mode = stat.S_IMODE(os.stat(path).st_mode)
    if mode != want:
        raise KMSError(f"permisos inválidos en {path}: {oct(mode)} != {oct(want)}")


def store_key(name: str, material: bytes) -> str:
    """Persiste material de clave con CHMOD 0600. Atómico: o existe completo o no existe."""
    if not material:
        raise KMSError("material de clave vacío")
    if os.sep in name or name.startswith("."):
        raise KMSError(f"nombre de clave inválido: {name!r}")
    d = _kms_dir()
    final = os.path.join(d, name + ".key")
    tmp = final + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, material)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, final)  # rename atómico en el mismo FS
    os.chmod(final, 0o600)
    _assert_mode(final, 0o600)
    return final


def load_key(name: str) -> bytes:
    """Lectura estricta: si el fichero no está en 0600 exacto, se rechaza (no se lee)."""
    path = os.path.join(_kms_dir(), name + ".key")
    if not os.path.isfile(path):
        raise KMSError(f"clave inexistente: {name}")
    _assert_mode(path, 0o600)
    with open(path, "rb") as f:
        return f.read()


def _selftest() -> int:
    import secrets
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        os.environ["CORTEX_KMS_DIR"] = os.path.join(td, "kms")
        material = secrets.token_bytes(32)
        path = store_key("node_alpha", material)
        assert stat.S_IMODE(os.stat(path).st_mode) == 0o600, "no está en 0600"
        assert load_key("node_alpha") == material, "material corrupto"
        # Sabotaje: relajar permisos debe provocar rechazo estricto
        os.chmod(path, 0o644)
        try:
            load_key("node_alpha")
            raise AssertionError("aceptó clave con 0644 — violación P0")
        except KMSError:
            pass
        # No debe quedar tmp huérfano (atomicidad)
        assert not [p for p in os.listdir(os.path.dirname(path)) if p.endswith(".tmp")]
        print("[C5-REAL] kms_local: SELFTEST OK (0600 forzado, escritura atómica)")
        return 0


if __name__ == "__main__":
    sys.exit(_selftest())
