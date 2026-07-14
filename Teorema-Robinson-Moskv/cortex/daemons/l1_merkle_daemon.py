import hashlib
import json
import os
import subprocess
import time

def get_recent_hashes(repo_path, limit=10):
    try:
        result = subprocess.run(["git", "log", f"-n{limit}", "--format=%H"], cwd=repo_path, capture_output=True, text=True, check=True)
        return [h for h in result.stdout.strip().split("\n") if h]
    except subprocess.CalledProcessError:
        return []

def compute_merkle_root(hashes):
    if not hashes:
        return hashlib.sha3_256(b"genesis").hexdigest()
    if len(hashes) == 1:
        return hashes[0]
    next_level = []
    for i in range(0, len(hashes), 2):
        left = hashes[i]
        right = hashes[i+1] if i+1 < len(hashes) else left
        combined = f"{left}{right}".encode('utf-8')
        next_level.append(hashlib.sha3_256(combined).hexdigest())
    return compute_merkle_root(next_level)

repo_path = os.path.expanduser("~/30_BABYLON-60/Teorema-Robinson-Moskv")
hashes = get_recent_hashes(repo_path)
merkle_root = compute_merkle_root(hashes)

l1_sink_dir = os.path.join(repo_path, "cortex", "L1_sink")
os.makedirs(l1_sink_dir, exist_ok=True)

payload_data = {
    "protocol": "CORTEX_C5_REAL",
    "daemon": "L1_MERKLE_CRON",
    "timestamp": int(time.time()),
    "merkle_root": merkle_root,
    "leaf_count": len(hashes)
}

payload_path = os.path.join(l1_sink_dir, f"cron_op_return_{merkle_root[:8]}.json")
with open(payload_path, "w") as f:
    json.dump(payload_data, f, indent=2)

try:
    subprocess.run(["git", "add", "cortex/L1_sink/"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", f"chore(daemon): L1_MERKLE_CRON execution - Root {merkle_root[:8]}"], cwd=repo_path, check=True)
except subprocess.CalledProcessError:
    pass

print(f"L1_MERKLE_CRON executed successfully. Root: {merkle_root}")
