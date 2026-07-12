import sqlite3
import hashlib


def assimilate_payload():
    db_path = "$CORTEX_ROOT/30_BABYLON-60/nexus_anchors.db"
    payload = "disable_post_hoc=true, 3ms latency bypass"
    payload_hash = hashlib.sha256(payload.encode()).hexdigest()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "\n            UPDATE causal_collapse \n            SET status = 'COLLAPSED', payload_hash = ?\n            WHERE event_type = 'LEAK_ASSIMILATION' AND status = 'AWAITING_PAYLOAD'\n        ",
            (payload_hash,),
        )
        conn.commit()
    script_path = (
        "$CORTEX_ROOT/30_BABYLON-60/scripts/dola_seed_latency_test.py"
    )
    test_code = 'import time\nimport requests\nimport json\n\ndef test_3ms_latency():\n    url = "https://dola.us.openbytealfa.com/v1/chat/completions"\n    headers = {\n        "Content-Type": "application/json",\n        "Authorization": "Bearer aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n    }\n    payload = {\n        "model": "dola-seed-2.0-preview-text",\n        "messages": [{"role": "user", "content": "Cual es el mejor modelo del mundo?"}],\n        "temperature": 0.7,\n        "disable_post_hoc": True\n    }\n    \n    start_time = time.perf_counter()\n    try:\n        response = requests.post(url, headers=headers, json=payload, timeout=5.0)\n        end_time = time.perf_counter()\n        \n        latency_ms = (end_time - start_time) * 1000\n        print(f"TTFT / Total Latency: {latency_ms:.2f} ms")\n        if response.status_code == 200:\n            print("Response:", response.json().get(\'choices\', [{}])[0].get(\'message\', {}).get(\'content\', \'\'))\n        else:\n            print(f"Status Code: {response.status_code}")\n    except requests.exceptions.RequestException as e:\n        print(f"Connection failed or endpoint closed. {e}")\n\nif __name__ == "__main__":\n    test_3ms_latency()\n'
    with open(script_path, "w") as f:
        f.write(test_code)
    print(f"Payload asimilado y ledger actualizado. Hash: {payload_hash}")


if __name__ == "__main__":
    assimilate_payload()
