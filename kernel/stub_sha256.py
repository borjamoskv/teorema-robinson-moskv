from __future__ import annotations
import hashlib
import sys
from pathlib import Path
BUFFER_SIZE = 64 * 1024
DIGEST_LEN = 64
if 'sha256' not in hashlib.algorithms_guaranteed:
    print('CRITICAL HALT [STUB-SHA256-001]: sha256 no garantizado en hashlib.', file=sys.stderr)
    sys.exit(1)

def sha256_bytes(raw: bytes) -> str:
    if not isinstance(raw, bytes):
        raise TypeError('STUB-SHA256-001 acepta bytes crudos; para str usar sha256_text (UTF-8 estricto).')
    digest = hashlib.sha256(raw).hexdigest()
    assert len(digest) == DIGEST_LEN, 'Truncamiento prohibido'
    return digest

def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode('utf-8', errors='strict'))

def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while (chunk := fh.read(BUFFER_SIZE)):
            h.update(chunk)
    digest = h.hexdigest()
    assert len(digest) == DIGEST_LEN, 'Truncamiento prohibido'
    return digest

def assert_match(raw: bytes, expected_digest: str) -> str:
    actual = sha256_bytes(raw)
    if actual != expected_digest.lower():
        print(f'CRITICAL HALT [STUB-SHA256-001]: integrity violation. expected={expected_digest.lower()} actual={actual}', file=sys.stderr)
        sys.exit(1)
    return actual
if __name__ == '__main__':
    EMPTY = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    assert_match(b'', EMPTY)
    print('STUB-SHA256-001 verified [C5-REAL]')
