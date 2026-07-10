#!/usr/bin/env python3
# [C5-REAL]
import random
import sqlite3
import sys

sys.path.append("$CORTEX_ROOT/30_BABYLON-60")

from cortex_inference import CortexInferenceEngine, DB_PATH

VOCAB = [
    "causar", "provocar", "generar", "hacer", "por qué", "efecto",
    "parte", "sistema", "estructura", "composición", "dividir",
    "cambiar", "evolucionar", "fluir", "transitar", "dinámica", "tiempo",
    "podría", "debería", "sería", "quizás", "posible", "mundo",
    "mejorar", "optimizar", "aprender", "entrenar", "divergencia", "entropía",
    "significar", "interpretar", "leer", "texto", "signo", "código",
    "confianza", "verdad", "verificar", "test", "hash", "isomorfismo",
    "fuego", "ruido", "vórtice", "colapso", "oráculo", "matriz"
]

def main():
    print("Initiating 1000-cycle ULTRATHINK L3 Memoization Protocol...")
    
    # 1. Start Engine (creates DB if not exists, but we assume it exists)
    engine = CortexInferenceEngine()
    
    unique_queries = set()
    
    # We want exactly 1000 unique queries to guarantee 1000 cache entries
    while len(unique_queries) < 1000:
        length = random.randint(3, 8)
        query = " ".join(random.sample(VOCAB, length))
        unique_queries.add(query)
        
    print("Pre-computing and caching 1000 isomorphic traces...")
    for query in unique_queries:
        # Calling this will trigger a cache miss the first time, compute the result, and INSERT to L3 cache
        engine.execute_inference(query)
        
    engine.close()
    
    # 2. Verify Database Cache
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM L3_inference_cache")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count >= 1000:
        print(f"SUCCESS: L3_inference_cache contains {count} entries. Zero-Anergy condition achieved.")
        sys.exit(0)
    else:
        print(f"FAILURE: Expected 1000 entries, but found {count}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
