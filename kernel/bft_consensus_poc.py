import sys
import time
from kernel.bft_strict import MutationPayload, validate_mutation, QUORUM
from kernel.stub_sha256 import sha256_bytes


def validate_bft_quorum(diff: bytes, falsification=None, author: str = "operator"):
    payload = MutationPayload(
        diff=diff,
        author=author,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        declared_digest=sha256_bytes(diff),
        falsification=falsification,
    )
    result = validate_mutation(payload)
    if not result.accepted:
        print("CRITICAL HALT: BFT Quorum failure. No mock allowed.", file=sys.stderr)
        sys.exit(1)
    return result


if __name__ == "__main__":
    r = validate_bft_quorum(b"x = 1\n", falsification=lambda: True)
    print(f"BFT Validator Initialized [C5-REAL] quorum={r.quorum}/{QUORUM}")
