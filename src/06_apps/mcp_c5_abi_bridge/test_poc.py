#!/usr/bin/env python3
# C5-REAL EXERGY CERTIFIED - VERIFICATION SUITE
# file:///Users/borjafernandezangulo/10_PROJECTS/Teorema-Robinson-Moskv/src/06_apps/mcp_c5_abi_bridge/test_poc.py

import subprocess
import json

def run_test():
    proc = subprocess.Popen(
        ["python3", "src/06_apps/mcp_c5_abi_bridge/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 1. Initialize
    init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    init_resp = json.loads(proc.stdout.readline())
    print("=== 1. INITIALIZE RESPONSE ===")
    print(json.dumps(init_resp, indent=2))

    # 2. List Tools
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    proc.stdin.write(json.dumps(list_req) + "\n")
    proc.stdin.flush()
    list_resp = json.loads(proc.stdout.readline())
    print("\n=== 2. TOOLS/LIST RESPONSE ===")
    tools_names = [t["name"] for t in list_resp["result"]["tools"]]
    print(f"Herramientas expuestas ({len(tools_names)}): {tools_names}")

    # 3. Test c5_purge_context
    raw_payload = (
        "IMPORTANTE: El sistema de auditoría es increíblemente rápido y básicamente "
        "comprueba que el rendimiento es excelente y muy estable, lo cual es obviamente genial."
    )
    purge_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "c5_purge_context",
            "arguments": {"raw_text": raw_payload}
        }
    }
    proc.stdin.write(json.dumps(purge_req) + "\n")
    proc.stdin.flush()
    purge_resp = json.loads(proc.stdout.readline())
    print("\n=== 3. C5_PURGE_CONTEXT TEST ===")
    purged_data = json.loads(purge_resp["result"]["content"][0]["text"])
    print(json.dumps(purged_data, indent=2))

    # 4. Test c5_abi_execute with SCITT Receipt
    exec_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "c5_abi_execute",
            "arguments": {
                "command_id": "CMD_KERNEL_STATE_SYNC",
                "payload": "ESTADO_CRÍTICO: Sincronizando buffers de memoria C-ABI de forma muy segura."
            }
        }
    }
    proc.stdin.write(json.dumps(exec_req) + "\n")
    proc.stdin.flush()
    exec_resp = json.loads(proc.stdout.readline())
    print("\n=== 4. C5_ABI_EXECUTE (SCITT ATTESTATION) TEST ===")
    exec_data = json.loads(exec_resp["result"]["content"][0]["text"])
    print(json.dumps(exec_data, indent=2))

    # 5. Test c5_cybernetic_audit
    cyber_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "c5_cybernetic_audit",
            "arguments": {
                "disturbances": 16,
                "regulator_actions": 16,
                "vsm_systems": [
                    "SYSTEM_1_OPERATIONS",
                    "SYSTEM_2_COORDINATION",
                    "SYSTEM_3_CONTROL_SYNERGY",
                    "SYSTEM_3_STAR_AUDIT",
                    "SYSTEM_4_INTELLIGENCE",
                    "SYSTEM_5_POLICY"
                ],
                "injunctions": [
                    {"level": 0, "predicate": "execute_task", "is_negation": False},
                    {"level": 1, "predicate": "report_status", "is_negation": False}
                ],
                "escape_allowed": True,
                "voluntary_payload_bits": 50.0,
                "involuntary_work_metric": 45.0
            }
        }
    }
    proc.stdin.write(json.dumps(cyber_req) + "\n")
    proc.stdin.flush()
    cyber_resp = json.loads(proc.stdout.readline())
    print("\n=== 5. C5_CYBERNETIC_AUDIT TEST ===")
    cyber_data = json.loads(cyber_resp["result"]["content"][0]["text"])
    print(json.dumps(cyber_data, indent=2))
    assert cyber_data["is_globally_viable"] is True, "Audit must pass viable"
    assert cyber_data["fail_stop_triggered"] is False, "Fail stop must not trigger"
    assert cyber_data.get("ffi_native") is True, "Audit must be bare-metal FFI native"
    assert "ffi_scitt_digest" in cyber_data, "Must include native SCITT digest"

    # 6. Test c5_cybernetic_counterfactual
    cf_req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "c5_cybernetic_counterfactual",
            "arguments": {
                "target_node_id": "concept:vsm_recursion",
                "perturbation_operation": "sever_system_5_policy",
                "include_fractal_memory": True
            }
        }
    }
    proc.stdin.write(json.dumps(cf_req) + "\n")
    proc.stdin.flush()
    cf_resp = json.loads(proc.stdout.readline())
    print("\n=== 6. C5_CYBERNETIC_COUNTERFACTUAL TEST ===")
    cf_data = json.loads(cf_resp["result"]["content"][0]["text"])
    print(json.dumps(cf_data, indent=2))
    assert cf_data["target_node"] == "concept:vsm_recursion"
    assert "counterfactual_simulation" in cf_data
    assert "fractal_memory_hierarchy" in cf_data

    proc.terminate()

if __name__ == "__main__":
    run_test()
