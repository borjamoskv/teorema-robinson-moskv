import os
import sys
import json
import hashlib
import subprocess
import asyncio
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from bft.ledger_actor import BFTLedgerActor, LedgerEvent

def get_git_commits(n=10):
    try:
        result = subprocess.run(
            ["git", "log", f"-n", str(n), "--format=%H"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        hashes = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        return hashes
    except Exception as e:
        print(f"Error fetching git commits: {e}", file=sys.stderr)
        sys.exit(1)

def compute_merkle_root(hashes):
    if not hashes:
        return "0" * 64
    current_level = hashes
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i+1] if i+1 < len(current_level) else left
            combined = (left + right).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        current_level = next_level
    return current_level[0]

async def main():
    print("[CORTEX COMPRESSOR] Starting compression...")
    commits = get_git_commits(10)
    if not commits:
        print("No commits found.", file=sys.stderr)
        sys.exit(1)
    
    merkle_root = compute_merkle_root(commits)
    print(f"[CORTEX COMPRESSOR] Merkle Root computed: {merkle_root}")
    
    # Generate JSON payload in L1_sink
    l1_sink_dir = PROJECT_ROOT / "L1_sink"
    l1_sink_dir.mkdir(parents=True, exist_ok=True)
    payload_file = l1_sink_dir / f"op_return_{merkle_root}.json"
    
    payload = {
        "merkle_root": merkle_root,
        "commit_hashes": commits,
        "timestamp_utc": subprocess.run(["date", "-u"], stdout=subprocess.PIPE, text=True).stdout.strip()
    }
    
    with open(payload_file, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[CORTEX COMPRESSOR] JSON payload saved to {payload_file}")
    
    # Anchor Merkle Root in BFT Ledger
    db_path = PROJECT_ROOT / "bft" / "ultrathink_ledger.db"
    print(f"[CORTEX COMPRESSOR] Anchoring in ledger at {db_path}...")
    actor = BFTLedgerActor(db_path)
    await actor.start()
    try:
        event = LedgerEvent(
            stream="cortex_merkle_compression",
            entity_id="merkle_root",
            event_type="merkle.anchored",
            payload=payload,
            cortex_taint="bft_merkle_compressor_auto",
            source_db="git",
            source_table="commits",
            source_pk="git_rev_parse",
        )
        fut = actor.append(event)
        res = await fut
        print(f"[CORTEX COMPRESSOR] Anchoring successful. Seq: {res['seq']}, Entry Hash: {res['entry_hash']}")
        
        # Write output format for agent
        output_data = {
            "Claim": f"Merkle Root compression successfully anchored to BFT Ledger.",
            "Proof": {
                "Base": f"{res['entry_hash']}",
                "Range": f"{merkle_root}",
                "Confidence": "C5"
            },
            "Payload_File": str(payload_file.relative_to(PROJECT_ROOT))
        }
        print("===RESULT_START===")
        print(json.dumps(output_data))
        print("===RESULT_END===")
        
    finally:
        await actor.stop()

if __name__ == "__main__":
    asyncio.run(main())
