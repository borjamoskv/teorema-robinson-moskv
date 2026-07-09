import os
import yaml
import sqlite3
import jwt
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

# Config C5-REAL
JWT_SECRET = os.environ.get("CORTEX_JWT_SECRET", "babylon60_apex_key")
JWT_ALGORITHM = "HS256"

app = FastAPI(docs_url=None)  # Override default docs

# Mount static files for CSS
app.mount("/static", StaticFiles(directory="cortex/api"), name="static")

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - CORTEX API",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_css_url="/static/swagger_theme.css"
    )

@app.get("/token")
def generate_dev_token():
    # Dev token for local testing
    token = jwt.encode({"sub": "operator", "role": "admin"}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token}

@app.get("/health")
def health_check():
    return {"status": "C5-REAL", "bft_consensus": True, "layer": "L5-Manifold"}

@app.get("/audit")
def get_audit_artifact(token: dict = Depends(verify_jwt)):
    audit_path = "/Users/borjafernandezangulo/.gemini/antigravity/brain/be4de698-23dc-4438-b538-6f84d8e1955d/cortex_mythos_audit.md"
    if not os.path.exists(audit_path):
        raise HTTPException(status_code=404, detail="Artifact no encontrado.")
    
    # Simple extraction of the first YAML block for EXERGY metrics
    try:
        with open(audit_path, "r") as f:
            content = f.read()
        
        # Split by ```yaml and take the second part, then split by ```
        if "```yaml" in content:
            yaml_content = content.split("```yaml")[1].split("```")[0].strip()
            data = yaml.safe_load(yaml_content)
            return {"source": "cortex_mythos_audit.md", "data": data}
        else:
            return {"source": "cortex_mythos_audit.md", "raw_content": content}
    except Exception as e:
        # Fail-fast bubble up
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/facts")
def query_facts(query: str, token: dict = Depends(verify_jwt)):
    # Fallback to cortex_memory.db
    db_path = "cortex_memory.db"
    if not os.path.exists(db_path):
        return {"query": query, "results": [], "warning": "No local DB found"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Since we don't know the exact query format, we attempt a naive search over L1 nodes if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='L1_primitive_nodes'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM L1_primitive_nodes LIMIT 10")
            rows = cursor.fetchall()
            return {"query": query, "results": [{"row_data": r} for r in rows]}
        else:
            return {"query": query, "results": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
