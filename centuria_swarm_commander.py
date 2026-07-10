#!/usr/bin/env python3
# [C5-REAL]
import ast
import json
import os
import glob
from pathlib import Path

WORKSPACE = "$CORTEX_ROOT/30_BABYLON-60"
SHARDS_FILE = os.path.join(WORKSPACE, "shards.json")

def generate_100_vectors():
    print("[CENTURIA] Initiating Surface Mapping...")
    vectors = []
    
    # 1. AST Scanning for Python Files
    py_files = glob.glob(f"{WORKSPACE}/*.py")
    for fpath in py_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    vectors.append({
                        "type": "AST_Function",
                        "target": f"{os.path.basename(fpath)}::{node.name}",
                        "directive": "Audit cyclomatic complexity and deterministic closure."
                    })
                elif isinstance(node, ast.ClassDef):
                    vectors.append({
                        "type": "AST_Class",
                        "target": f"{os.path.basename(fpath)}::{node.name}",
                        "directive": "Audit memory footprint and state mutability."
                    })
        except Exception as e:
            print(f"Error parsing {fpath}: {e}")
            
    # 2. Add structural boundaries (Database, Networking, State)
    vectors.extend([
        {"type": "DB_Schema", "target": "L1_primitive_nodes", "directive": "Verify indexing and constraint rigor."},
        {"type": "DB_Schema", "target": "L2_isomorphism_edges", "directive": "Verify foreign key simulation and cascade."},
        {"type": "DB_Schema", "target": "L3_inference_cache", "directive": "Verify hit/miss distribution and entropy."},
        {"type": "Network", "target": "server.js", "directive": "Audit async event loop blocking and IPC overhead."},
        {"type": "YAML_Config", "target": "cortex_inference_engine.yaml", "directive": "Audit structural integrity of trigger definitions."}
    ])
    
    # Ensure we don't pad with synthetic load (Anergy purge)
    # The true complexity vectors are strictly the physical AST nodes and structural boundaries.
    
    print(f"[CENTURIA] Generated {len(vectors)} Deep Research Vectors (Pure Exergy).")
    
    # Shard into 3 blocks for our 3 Titans
    shards = {
        "Titan-1": vectors[:33],
        "Titan-2": vectors[33:66],
        "Titan-3": vectors[66:]
    }
    
    with open(SHARDS_FILE, "w", encoding="utf-8") as f:
        json.dump(shards, f, indent=2)
        
    print(f"[CENTURIA] Shards crystallized to {SHARDS_FILE}")

if __name__ == "__main__":
    generate_100_vectors()
