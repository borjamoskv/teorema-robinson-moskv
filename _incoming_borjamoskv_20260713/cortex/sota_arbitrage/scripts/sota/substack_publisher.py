#!/usr/bin/env python3
"""
C5-REAL Publisher: Substack Premium (SOTA Vector Engine)
Consolida los Nodos de Frontera de las últimas 24h en Markdown Brutalista.
Cumple con R12 (Substack Exergy) y L6 (Zero Fluff).
"""
import chromadb
from chromadb.utils import embedding_functions
import os
import time

CORTEX_DB_PATH = os.path.expanduser("~/.gemini/config/.cortex/vector_db")
OUTPUT_MD = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage/substack_daily.md"

def get_collection():
    if not os.path.exists(CORTEX_DB_PATH):
        print("[ERROR] VectorDB no inicializada.")
        return None
    client = chromadb.PersistentClient(path=CORTEX_DB_PATH)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(name="sota_frontier_nodes", embedding_function=emb_fn)

def generate_markdown():
    collection = get_collection()
    if not collection: return
    
    # Extraer los nodos recientes (mock limit=20 para demostración)
    res = collection.get(limit=20)
    
    if not res or not res.get("documents"):
        print("[INFO] Sin señales para publicar.")
        return
        
    md = []
    md.append("# █ SOTA ARBITRAGE: SIGNAL INTELLIGENCE")
    md.append("**DATE**: " + time.strftime("%Y-%m-%d"))
    md.append("**STATE**: C5-REAL | **ENTROPY**: PURGED")
    md.append("\n---\n")
    
    docs = res["documents"]
    metas = res["metadatas"]
    ids = res["ids"]
    
    for i in range(len(docs)):
        meta = metas[i] if metas and i < len(metas) else {}
        domain = meta.get("domain", "Unknown")
        conf = meta.get("confidence", 0.0)
        source = meta.get("source", "Unknown")
        
        md.append(f"### [NODE-{ids[i][:8]}] {domain}")
        md.append(f"> **CONFIDENCE**: {conf} | **SOURCE**: {source}")
        md.append(f"\n```yaml\n{docs[i]}\n```\n")
        md.append("---\n")
        
    with open(OUTPUT_MD, 'w') as f:
        f.write("\n".join(md))
        
    print(f"[C5-REAL] Substack Exergy generado en: {OUTPUT_MD}")

if __name__ == "__main__":
    generate_markdown()
