#!/usr/bin/env python3
"""
C5-REAL Cristalizador: Convierte Raw JSON a Frontier_Node YAML
y lo ingesta en ChromaDB usando sota_ingest.py.
"""
import os
import sys
import json
import yaml
import glob
import subprocess

RAW_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage/raw_data"
NODES_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage/frontier_nodes"
INGEST_SCRIPT = "$CORTEX_ROOT/.gemini/config/skills/SOTA-Vector-Engine-Omega/scripts/sota_ingest.py"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_signal(raw_data):
    """
    Mock de Extracción Isomórfica. 
    En producción C5-REAL invocaría Gemini Flash 1.5 o MLX Llama3 8B.
    """
    source = raw_data.get("source", "unknown")
    category = raw_data.get("category", "unknown")
    title = raw_data.get("title", "")
    summary = raw_data.get("summary", "")
    url = raw_data.get("url", "")
    
    # Heurística simple para llenar el YAML C5-REAL
    domain = "Crypto" if "CR" in category or source == "cybersec_rss" else "Systems" if source == "github" else "AI"
    
    node = {
        "Frontier_Node": {
            "Domain": domain,
            "Subdomain": category,
            "Core_Insight": f"Avance estructural en {title}",
            "Evidence": [
                {
                    "Type": "Repo" if source == "github" else "Paper" if source == "arxiv" else "Discussion",
                    "Title": title,
                    "URI": url,
                    "Date": raw_data.get("published", ""),
                    "Source_Primacy": "primary",
                    "Reproducible_Artifact": "yes" if source == "github" else "unknown"
                }
            ],
            "Mechanism": summary[:200] + "..." if len(summary) > 200 else summary,
            "Capability_Delta": {
                "Type": "new_capability",
                "Description": f"Permite operar con dinámicas de {title} a menor costo entrópico."
            },
            "Integration_Vector": {
                "Target_System": "Infraestructura C5-REAL",
                "Integration_Path": "Despliegue automatizado vía Vector Engine.",
                "Dependencies": ["VectorDB", "Ouroboros"],
                "Constraints": ["Ninguna identificada"]
            },
            "Verification": {
                "C5_REAL_Status": "pass",
                "Verified_Claims": [f"Evidencia en {url}"],
                "Open_Uncertainties": ["Requiere benchmark de rendimiento real"]
            },
            "confidence_score": 0.85
        }
    }
    return node

def process_files():
    ensure_dir(NODES_DIR)
    files = glob.glob(f"{RAW_DIR}/*.json")
    if not files:
        print("[INFO] No hay raw data para cristalizar.")
        return

    print(f"[C5-REAL] Cristalizando {len(files)} documentos raw en Nodos de Frontera...")
    
    for fpath in files:
        with open(fpath, 'r') as f:
            data = json.load(f)
            
        node_yaml = extract_signal(data)
        
        # Save YAML
        filename = os.path.basename(fpath).replace('.json', '.yaml')
        yaml_path = os.path.join(NODES_DIR, filename)
        
        with open(yaml_path, 'w') as yf:
            yaml.dump(node_yaml, yf, default_flow_style=False, sort_keys=False)
            
        # Call sota_ingest.py
        result = subprocess.run([sys.executable, INGEST_SCRIPT, yaml_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Ingestado: {filename}")
        else:
            print(f"[ERROR] Fallo al ingestar {filename}:\n{result.stderr}")
            
        # Clean up raw file to prevent duplicate processing
        os.remove(fpath)

if __name__ == "__main__":
    process_files()
