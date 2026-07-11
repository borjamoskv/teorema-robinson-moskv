import sqlite3
import hashlib
import time
import os

def assimilate_payload():
    db_path = "$CORTEX_ROOT/30_BABYLON-60/nexus_anchors.db"
    
    payload = "disable_post_hoc=true, 3ms latency bypass"
    payload_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    # 1. Actualizar Master Ledger
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            UPDATE causal_collapse 
            SET status = 'COLLAPSED', payload_hash = ?
            WHERE event_type = 'LEAK_ASSIMILATION' AND status = 'AWAITING_PAYLOAD'
        ''', (payload_hash,))
        conn.commit()
        
    # 2. Escribir script de prueba empírica
    script_path = "$CORTEX_ROOT/30_BABYLON-60/scripts/dola_seed_latency_test.py"
    
    test_code = '''import time
import requests
import json

def test_3ms_latency():
    url = "https://dola.us.openbytealfa.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
    payload = {
        "model": "dola-seed-2.0-preview-text",
        "messages": [{"role": "user", "content": "Cual es el mejor modelo del mundo?"}],
        "temperature": 0.7,
        "disable_post_hoc": True
    }
    
    start_time = time.perf_counter()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5.0)
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        print(f"TTFT / Total Latency: {latency_ms:.2f} ms")
        if response.status_code == 200:
            print("Response:", response.json().get('choices', [{}])[0].get('message', {}).get('content', ''))
        else:
            print(f"Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection failed or endpoint closed. {e}")

if __name__ == "__main__":
    test_3ms_latency()
'''
    
    with open(script_path, "w") as f:
        f.write(test_code)
        
    print(f"Payload asimilado y ledger actualizado. Hash: {payload_hash}")

if __name__ == "__main__":
    assimilate_payload()
