# [C5-REAL] Exergy-Maximized - SOTA BFT-Ready Analysis API
# Autoría: Borja Moskv (borjamoskv)
# Descargo: Exclusivo para el Teorema-Robinson-Moskv de CORTEX.

import os
import sqlite3
import time
import json
from datetime import datetime
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# API Versioning and Metadata
__version__ = "2.2.0"

JWT_SECRET = os.getenv("CORTEX_JWT_SECRET", "moskv-omega-strict-key-2026")
JWT_ALGORITHM = "HS256"
DB_PATH = os.path.expanduser("~/.babylon60/cortex.db")
MEMORY_PATH = os.path.expanduser("~/.agent/memory")

app = FastAPI(
    title="CORTEX Analysis Pipeline (MOSKV-1 OMEGA)",
    version=__version__,
    docs_url=None,
    description="Sovereign Endpoint for BFT-validated external AI audits. Created by Borja Moskv."
)

class FactNode(BaseModel):
    id: str
    level: str = "C5-REAL"
    content: str
    timestamp: str

class AuditResponse(BaseModel):
    query: str
    nodes_yield: int
    results: list[FactNode]
    authorized_by: str
    exergy_latency_ms: float

# Forensic Middleware
@app.middleware("http")
async def forensic_audit_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Exergy-Latency-Ms"] = f"{process_time:.2f}"
    print(f"[FORENSIC] {request.method} {request.url.path} | IP: {request.client.host} | Latency: {process_time:.2f}ms | Status: {response.status_code}")
    return response

def verify_strict_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="MISSING_BFT_AUTHORIZATION")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="INVALID_BFT_SCHEME")
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"BFT_SIGNATURE_INVALID: {str(e)}")

def _extract_ontology_facts(query: str) -> list[FactNode]:
    """Extracts crystallized facts directly from the C5-REAL SQLite WAL Ontology DB"""
    facts = []
    if not os.path.exists(DB_PATH):
        return facts

    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        cursor = conn.cursor()

        # Define tables and search columns
        tables = {
            "primitivas_de_colapso": ["id", "primitiva", "mecanismo_causal"],
            "invariantes_termodinamicas": ["id", "invariante", "lógica___principio", "implicación_operacional"],
            "antipatrones_estocasticos": ["id", "antipatrón", "disfunción_causal", "refactor_alternativa"],
            "redundancias_activas": ["id", "redundancia_c5", "función_topológica"],
            "vectores_adversariales": ["id", "vector_adversarial", "mecanismo_de_explotación"]
        }

        for table, cols in tables.items():
            if query.lower() == "all":
                select_query = f"SELECT id, * FROM {table}"
                cursor.execute(select_query)
            else:
                # Build LIKE conditions for search
                conditions = " OR ".join([f"{col} LIKE ?" for col in cols])
                select_query = f"SELECT id, * FROM {table} WHERE {conditions}"
                params = [f"%{query}%"] * len(cols)
                cursor.execute(select_query, params)

            rows = cursor.fetchall()
            # Fetch column names
            col_names = [description[0] for description in cursor.description]

            for row in rows:
                row_dict = dict(zip(col_names, row))
                entity_id = row_dict.get("id", "UNKNOWN")
                
                # Format detailed description
                content_parts = []
                for k, v in row_dict.items():
                    if k != "id" and v:
                        content_parts.append(f"{k.replace('___', '/').replace('_', ' ').capitalize()}: {v}")
                
                content_str = " | ".join(content_parts)
                
                facts.append(FactNode(
                    id=entity_id,
                    level="C5-REAL",
                    content=content_str,
                    timestamp=datetime.utcnow().isoformat()
                ))

        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to query SQLite ontology DB: {str(e)}")
        
    return facts

def _extract_cortex_memory(query: str) -> list[FactNode]:
    """Zero-entropy extraction from CORTEX VSA system memory (ghosts)"""
    ghosts_file = os.path.join(MEMORY_PATH, "ghosts.json")
    facts = []
    if os.path.exists(ghosts_file):
        try:
            with open(ghosts_file) as f:
                data = json.load(f)
                for proj, ghost in data.items():
                    task = ghost.get("last_task", "")
                    if query.lower() in task.lower() or query.lower() == "all":
                        facts.append(FactNode(
                            id=f"GHOST-{proj.upper()}",
                            content=f"Project: {proj} | Task: {task} | Status: {ghost.get('status', 'active')}",
                            timestamp=ghost.get("timestamp", datetime.utcnow().isoformat())
                        ))
        except Exception:
            pass
    return facts

@app.get("/health")
def health_check():
    return {
        "status": "C5-REAL",
        "engine": "MOSKV-1 OMEGA",
        "timestamp": datetime.utcnow().isoformat(),
        "entropy_leak": 0.0,
        "author": "Borja Moskv"
    }

@app.get("/facts", response_model=AuditResponse)
def get_facts(
    query: str = Query(..., min_length=2, description="BFT Extractor Query (use 'all' for full ledger)"),
    user: dict = Depends(verify_strict_token),
):
    """
    Exposes CORTEX-Persist C5-REAL crystallized memory.
    Requires valid HS256 Bearer Token.
    """
    t0 = time.time()
    
    # Extract both ontology facts and ghost memories
    ontology_nodes = _extract_ontology_facts(query)
    ghost_nodes = _extract_cortex_memory(query)
    
    results = ontology_nodes + ghost_nodes
    
    return AuditResponse(
        query=query,
        nodes_yield=len(results),
        results=results,
        authorized_by=user.get("user", "sys_auditor"),
        exergy_latency_ms=(time.time() - t0) * 1000
    )

# Serve Custom themed Swagger
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=app.title + " - Moskv Aesthetic UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_css_url="/static/swagger_theme.css",
    )
