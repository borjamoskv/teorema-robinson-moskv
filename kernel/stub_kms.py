from __future__ import annotations
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REQUIRED_MODE = 384
DEFAULT_KEY_DIR = Path.home() / ".babylon60" / "keys"
AUDIT_LOG = DEFAULT_KEY_DIR / "kms_audit.log"
SCAN_TARGETS = (
    str(DEFAULT_KEY_DIR / "**"),
    str(Path.home() / ".ssh" / "id_*"),
    "$CORTEX_ROOT/.env",
    "$CORTEX_ROOT/cortex/**/*.pem",
)


@dataclass(frozen=True)
class PermissionState:
    path: str
    compliant: bool
    previous: str
    corrected: str


def _append_audit(path: Path, old_mode: int, new_mode: int) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} path={path} old={oct(old_mode)} new={oct(new_mode)}\n"
    with open(AUDIT_LOG, "a", encoding="utf-8") as fh:
        fh.write(line)
    os.chmod(AUDIT_LOG, REQUIRED_MODE)


def enforce(file_path: str | Path) -> PermissionState:
    p = Path(file_path)
    mode = os.stat(p).st_mode & 511
    if mode == REQUIRED_MODE:
        return PermissionState(str(p), True, oct(mode), oct(mode))
    os.chmod(p, REQUIRED_MODE)
    corrected = os.stat(p).st_mode & 511
    if corrected != REQUIRED_MODE:
        print(
            f"CRITICAL HALT [STUB-KMS-0600-001]: uncorrectable mode on {p} ({oct(corrected)})",
            file=sys.stderr,
        )
        sys.exit(1)
    _append_audit(p, mode, corrected)
    print(
        f"ALERT [STUB-KMS-0600-001]: corrected {p} {oct(mode)} -> {oct(corrected)}",
        file=sys.stderr,
    )
    return PermissionState(str(p), False, oct(mode), oct(corrected))


def boot_scan(root: str | Path = DEFAULT_KEY_DIR) -> list[PermissionState]:
    root = Path(root)
    results: list[PermissionState] = []
    if not root.exists():
        return results
    for p in sorted(root.rglob("*")):
        if p.is_file() and (not p.is_symlink()):
            results.append(enforce(p))
    return results


def store_key(
    name: str, material: bytes, key_dir: str | Path = DEFAULT_KEY_DIR
) -> Path:
    key_dir = Path(key_dir)
    key_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(key_dir, 448)
    target = (key_dir / name).resolve()
    if key_dir.resolve() not in target.parents:
        raise ValueError("STUB-KMS-0600-001: ruta fuera del directorio designado")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, REQUIRED_MODE)
    try:
        os.write(fd, material)
    finally:
        os.close(fd)
    enforce(target)
    return target


def load_key(name: str, key_dir: str | Path = DEFAULT_KEY_DIR) -> bytes:
    target = Path(key_dir) / name
    enforce(target)
    return target.read_bytes()


if __name__ == "__main__":
    states = boot_scan()
    fixed = sum((1 for s in states if not s.compliant))
    print(
        f"STUB-KMS-0600-001 boot scan: {len(states)} files, {fixed} corrected [C5-REAL]"
    )
