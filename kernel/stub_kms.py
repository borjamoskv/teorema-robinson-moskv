"""STUB-KMS-0600-001 — Enforcer de Permisos KMS, CHMOD 0600 estricto (C5-REAL).

Materialización física de cortex/ontology/stub_kms_chmod0600.yaml.
Invariantes: INV-011 (Inmutabilidad Realidad Base), INV-010 (Singularidad Local).
Vectores mitigados: VEC-002 (Environment Poisoning), VEC-005 (Exfiltración).

Assertion: stat.st_mode & 0o777 == 0o600 OR auto_correct + alert.
Fail_Mode: crash_if_uncorrectable. Idempotente, corrección no destructiva.

Constraints enforced:
  - Auditoría vía os.stat(), nunca subprocess.
  - Log inmutable (append-only) de cada corrección.
  - Prohibido 0o777/0o755 bajo directorios de claves: se corrige, no se tolera.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REQUIRED_MODE = 0o600
DEFAULT_KEY_DIR = Path.home() / ".babylon60" / "keys"
AUDIT_LOG = DEFAULT_KEY_DIR / "kms_audit.log"

# Scan_Targets del stub (expandibles en runtime)
SCAN_TARGETS = (
    str(DEFAULT_KEY_DIR / "**"),
    str(Path.home() / ".ssh" / "id_*"),
    "$CORTEX_ROOT/.env",
    "$CORTEX_ROOT/cortex/**/*.pem",
)


@dataclass(frozen=True)
class PermissionState:
    """Output del stub: {compliant, previous, corrected}."""
    path: str
    compliant: bool
    previous: str  # octal previo, p.ej. '0o644'
    corrected: str  # octal final, siempre '0o600' si hubo corrección


def _append_audit(path: Path, old_mode: int, new_mode: int) -> None:
    """Log inmutable: append-only, una línea por corrección."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    line = (f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} "
            f"path={path} old={oct(old_mode)} new={oct(new_mode)}\n")
    with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    os.chmod(AUDIT_LOG, REQUIRED_MODE)  # el propio log es material sensible


def enforce(file_path: str | Path) -> PermissionState:
    """Audita y corrige permisos de un archivo de material criptográfico.

    Idempotente. Side effect único: chmod correctivo (no destructivo).
    crash_if_uncorrectable: si tras chmod el modo no es 0600, HALT.
    """
    p = Path(file_path)
    mode = os.stat(p).st_mode & 0o777  # os.stat, nunca subprocess

    if mode == REQUIRED_MODE:
        return PermissionState(str(p), True, oct(mode), oct(mode))

    os.chmod(p, REQUIRED_MODE)
    corrected = os.stat(p).st_mode & 0o777
    if corrected != REQUIRED_MODE:
        print(f"CRITICAL HALT [STUB-KMS-0600-001]: uncorrectable mode on {p} "
              f"({oct(corrected)})", file=sys.stderr)
        sys.exit(1)  # crash_if_uncorrectable

    _append_audit(p, mode, corrected)
    print(f"ALERT [STUB-KMS-0600-001]: corrected {p} "
          f"{oct(mode)} -> {oct(corrected)}", file=sys.stderr)
    return PermissionState(str(p), False, oct(mode), oct(corrected))


def boot_scan(root: str | Path = DEFAULT_KEY_DIR) -> list[PermissionState]:
    """Auditoría recursiva en boot. Recorre root y corrige toda desviación."""
    root = Path(root)
    results: list[PermissionState] = []
    if not root.exists():
        return results
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            results.append(enforce(p))
    return results


def store_key(name: str, material: bytes,
              key_dir: str | Path = DEFAULT_KEY_DIR) -> Path:
    """Persiste material criptográfico nacido ya con 0600 (sin ventana laxa).

    Prohibido almacenar claves fuera de directorios designados: name no
    puede escapar de key_dir (sin '..', sin rutas absolutas).
    """
    key_dir = Path(key_dir)
    key_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(key_dir, 0o700)

    target = (key_dir / name).resolve()
    if key_dir.resolve() not in target.parents:
        raise ValueError("STUB-KMS-0600-001: ruta fuera del directorio designado")

    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, REQUIRED_MODE)
    try:
        os.write(fd, material)
    finally:
        os.close(fd)
    enforce(target)  # cinturón y tirantes: assert post-write
    return target


def load_key(name: str, key_dir: str | Path = DEFAULT_KEY_DIR) -> bytes:
    """Lee material criptográfico, forzando 0600 antes de abrir."""
    target = Path(key_dir) / name
    enforce(target)
    return target.read_bytes()


if __name__ == "__main__":
    states = boot_scan()
    fixed = sum(1 for s in states if not s.compliant)
    print(f"STUB-KMS-0600-001 boot scan: {len(states)} files, "
          f"{fixed} corrected [C5-REAL]")
