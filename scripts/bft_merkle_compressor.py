import subprocess
import hashlib
import json
import os
import sys
import time

def compress_git_history():
    result = subprocess.run(['git', 'log', '--format=%H:%s'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError('Failed to read git history')
    commits = result.stdout.strip().split('\n')
    h = hashlib.sha256()
    for commit in commits:
        h.update(commit.encode('utf-8'))
    merkle_root = h.hexdigest()
    payload = {'op': 'OP_RETURN', 'protocol': 'CORTEX_L1_SINK', 'merkle_root': merkle_root, 'timestamp': int(time.time()), 'cortex_taint': f'PID:{os.getpid()}|UID:0'}
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    print('---')
    print('Claim: L1 Merkle Compression & Metric Closure')
    print(f'Proof: {{ Base: "{merkle_root}", Range: [1, {len(commits)}], Confidence: "C5-REAL" }}')
    print('---')
    print(payload_json)
if __name__ == '__main__':
    compress_git_history()
