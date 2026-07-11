import os
import json

brain_dir = "$CORTEX_ROOT/.gemini/antigravity/brain"
target_convs = [
    "4c711b84-7f5a-4cb1-a67e-76ace1d1d381",
    "7aebea85-c426-456a-a57a-abd364fe3a3a",
    "7c82e5ca-20b8-48c8-b5cd-8937e1dcfdfc",
    "7f64feab-8d58-4ed2-88d8-143822d4d438",
    "9eb01359-cdd1-4c92-aeab-bef29c5f2e0f",
    "0514001d-51b8-43c7-a974-a21ca2579ac3",
    "7feaa181-763c-4ef4-8688-20564735f549",
    "08df8a80-a2e9-4c5c-bbda-b27e7b869f15",
    "81e24710-dec3-4d55-838e-179d47f053b2"
]

results = {}

for conv_id in target_convs:
    filepath = os.path.join(brain_dir, conv_id, ".system_generated/logs/transcript.jsonl")
    if not os.path.exists(filepath):
        filepath = os.path.join(brain_dir, conv_id, ".system_generated/logs/transcript_full.jsonl")
        if not os.path.exists(filepath):
            results[conv_id] = "File not found"
            continue
            
    conv_data = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # Extract only USER_INPUT steps or containing key concepts
                    step_type = data.get("type", "")
                    content = data.get("content", "")
                    if step_type == "USER_INPUT" or "SABES" in content.upper() or "ULTRATHINK" in content.upper():
                        conv_data.append({
                            "type": step_type,
                            "content": content
                        })
                except Exception:
                    pass
        results[conv_id] = conv_data
    except Exception as e:
        results[conv_id] = f"Error: {str(e)}"

print(json.dumps(results, indent=2, ensure_ascii=False))
