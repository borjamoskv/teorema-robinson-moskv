#!/usr/bin/env python3
"""
C5-REAL API SaaS: HFT / Startups (SOTA Vector Engine)
Expone la base de ChromaDB a través de FastAPI con Auth.
"""
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
import os
import uvicorn
from typing import List, Optional

CORTEX_DB_PATH = os.path.expanduser("~/.gemini/config/.cortex/vector_db")

app = FastAPI(title="SOTA Arbitrage API", description="C5-REAL Institutional Signal Engine")

API_KEY = "CORTEX_HFT_500X" # Mock token para HFT/Startups
API_KEY_NAME = "X-SOTA-Token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="C5-REAL: Acceso Denegado. Token Inválido.")

class SignalQuery(BaseModel):
    query: str
    n_results: int = 5
    domain: Optional[str] = None

# Init DB Connection
def get_collection():
    if not os.path.exists(CORTEX_DB_PATH):
        raise HTTPException(status_code=500, detail="VectorDB no inicializada.")
    client = chromadb.PersistentClient(path=CORTEX_DB_PATH)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(name="sota_frontier_nodes", embedding_function=emb_fn)

@app.get("/api/v1/signals/latest")
def get_latest_signals(api_key: str = Depends(get_api_key)):
    """Retorna los nodos de frontera más recientes (sin filtro vectorial, solo offset)."""
    collection = get_collection()
    res = collection.get(limit=10)
    return {"status": "ok", "nodes": res}

@app.post("/api/v1/signals/query")
def query_signals(query_data: SignalQuery, api_key: str = Depends(get_api_key)):
    """Ejecuta una búsqueda vectorial RAG para fondos HFT."""
    collection = get_collection()
    where_clause = {"domain": query_data.domain} if query_data.domain else None
    
    results = collection.query(
        query_texts=[query_data.query],
        n_results=query_data.n_results,
        where=where_clause
    )
    return {"status": "ok", "query": query_data.query, "results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
