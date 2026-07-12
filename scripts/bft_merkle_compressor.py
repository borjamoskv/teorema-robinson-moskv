import subprocess
import hashlib
import json
import os

def get_git_commits():
    result = subprocess.run(['git', 'log', '-n', '10', '--format=%H'], capture_output=True, text=True, cwd='$CORTEX_ROOT/30_BABYLON-60')
    return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

def compute_merkle_root(hashes):
    combined = "".join(hashes).encode('utf-8')
    return hashlib.sha256(combined).hexdigest()

def main():
    commits = get_git_commits()
    if not commits:
        print("No commits found.")
        return
        
    merkle_root = compute_merkle_root(commits)
    
    sink_dir = "$CORTEX_ROOT/30_BABYLON-60/L1_sink"
    os.makedirs(sink_dir, exist_ok=True)
    
    payload = {
        "protocol": "BFT_MERKLE_L1_SINK",
        "merkle_root": merkle_root,
        "tx_type": "OP_RETURN",
        "payload_size_bytes": 32,
        "leaves": commits
    }
    
    filename = os.path.join(sink_dir, f"op_return_{merkle_root}.json")
    with open(filename, 'w') as f:
        json.dump(payload, f, indent=2)
        
    print(f"MERKLE_ROOT:{merkle_root}")

if __name__ == '__main__':
    main()
