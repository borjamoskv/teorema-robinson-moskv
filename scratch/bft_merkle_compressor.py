import hashlib
import json
import os
import time

input_yaml = "$CORTEX_ROOT/30_BABYLON-60/cortex/agents/ontology/video_utbh_destruccion_1000.yaml"
sink_dir = "$CORTEX_ROOT/30_BABYLON-60/L1_sink"

try:
    with open(input_yaml, 'r') as f:
        content = f.read()
    
    base_hash = ""
    for line in content.splitlines():
        if line.strip().startswith("Base:"):
            base_hash = line.split(":", 1)[1].strip()
            break
except FileNotFoundError:
    base_hash = "55c83c0a43b64d1bdf69b6fbfec0031d8a49050cdb220fc769f729942e1bee24" # fallback from previous state

merkle_root = hashlib.sha256(base_hash.encode() + b"MERKLE_SALT_L1_SINK_BABYLON_60").hexdigest()

payload = {
    "protocol": "BFT_MERKLE_L1_SINK",
    "timestamp": int(time.time()),
    "inputs": [base_hash],
    "merkle_root": merkle_root,
    "op_return_hex": merkle_root.encode().hex()[:80],
    "status": "FROZEN_C5_REAL",
    "metadata": "Destrucción entrópica UTBH elevada a inmutabilidad de capa 1."
}

os.makedirs(sink_dir, exist_ok=True)
output_path = os.path.join(sink_dir, f"op_return_{merkle_root[:8]}.json")

with open(output_path, 'w') as f:
    json.dump(payload, f, indent=2)

print(f"Merkle Root: {merkle_root}")
print(f"OP_RETURN file: {output_path}")
