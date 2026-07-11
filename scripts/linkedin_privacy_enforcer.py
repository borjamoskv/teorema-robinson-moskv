#!/usr/bin/env python3
"""
LinkedIn Privacy Enforcer (Zero-Friction C5-REAL)
Matrix-Driven Architecture. Transmutes semantic privacy primitives into physical execution.
"""

import sys
import os
import time
import subprocess
import yaml
from typing import Dict, Any

sys.path.append("$CORTEX_ROOT/.gemini/config/skills/Darwin_CGEvent_Injector/scripts")
try:
    from ui_maestro import UIMaestro
except ImportError:
    print("Error: Darwin_CGEvent_Injector skill not found or incomplete.")
    sys.exit(1)

def navigate_brave_to(url: str) -> None:
    cmd = f'tell application "Brave Browser" to set URL of active tab of front window to "{url}"'
    subprocess.run(["osascript", "-e", cmd], capture_output=True)
    time.sleep(4)

def enforce_matrix_node(node_id: str, data: dict, maestro: UIMaestro) -> Dict[str, Any]:
    print(f"\n[MATRIX-NODE] Executing {node_id}: {data.get('description')}")
    navigate_brave_to(data['url'])
    
    try:
        res = maestro.click_element_by_title_zero_friction(data['target_element'], "Brave Browser")
        print(f"[SUCCESS] {node_id} Enforced -> {res}")
        return res
    except Exception as e:
        print(f"[FAILED] {node_id} Target Element '{data['target_element']}' not found or unreachable. Error: {e}")
        return {"status": "failed", "error": str(e)}

def main():
    print("=== STARTING MATRIX-DRIVEN ZERO-FRICTION ENFORCEMENT ===")
    
    matrix_path = "scripts/privacy_matrix.yaml"
    if not os.path.exists(matrix_path):
        matrix_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "privacy_matrix.yaml")
        
    with open(matrix_path, "r") as f:
        matrix = yaml.safe_load(f)
        
    maestro = UIMaestro()
    nodes = matrix.get("C5_REAL_ENFORCEMENT_MATRIX", {})
    
    for node_id, data in nodes.items():
        enforce_matrix_node(node_id, data, maestro)
        
    print("\n=== PRIVACY ENFORCEMENT RUN COMPLETE ===")

if __name__ == "__main__":
    main()
