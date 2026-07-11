import hashlib
import json
import logging
import os
import secrets
import sqlite3
import threading
import time
import uuid
from typing import Optional, Dict

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

# ❖ C5-REAL :: MCON API + ZERO-TRUST ECDSA BFT (EXERGY) ❖
# API REST con Cadena Hash, Firmas Digitales Locales y Validación Multi-Nodo (Spoofing Prevention).

# -----------------------------
# Configuración Criptográfica
# -----------------------------
NODE_ID = os.getenv("NODE_ID", "N0")
DB_PATH = os.getenv("MCON_DB", f"mcon_audit_{NODE_ID}.db")
API_KEY = os.getenv("MCON_API_KEY", "dev-secret")
KEY_PATH = f"{NODE_ID}_private.pem"

logging.basicConfig(level="INFO", format="%(message)s")
logger = logging.getLogger(f"cortex_mcon_{NODE_ID}")

# 1. Generar o Cargar Clave Privada ECDSA
if os.path.exists(KEY_PATH):
    with open(KEY_PATH, "rb") as f:
        private_key = SigningKey.from_pem(f.read())
else:
    private_key = SigningKey.generate(curve=SECP256k1)
    with open(KEY_PATH, "wb") as f:
        f.write(private_key.to_pem())

public_key = private_key.get_verifying_key()
public_key_hex = public_key.to_string().hex()

# 2. Directorio de Claves Públicas (Cluster BFT)
CLUSTER_KEYS: Dict[str, VerifyingKey] = {
    NODE_ID: public_key
}

# -----------------------------
# Léxico Causal ECB-1
# -----------------------------
EMOJI_BY_STATE = {
    "IDLE": "📦",
    "PROCESSING": "🧠",
    "SUCCESS": "⚡",
    "ERROR": "💀",
    "RECOVERY": "🩸",
    "TERMINAL": "📤"
}

STATE_BY_EMOJI = {v: k for k, v in EMOJI_BY_STATE.items()}
VALID_PHASES = {"PRE_PREPARE", "PREPARE", "COMMIT", "VIEW_CHANGE", "STATE_CHANGE"}
DB_LOCK = threading.Lock()

# -----------------------------
# Modelos
# -----------------------------
class AuditEventInput(BaseModel):
    phase: str = Field(min_length=1, max_length=32)
    state: Optional[str] = None
    emoji: Optional[str] = None
    payload: dict = Field(default_factory=dict)

# -----------------------------
# Base de Datos con Doble Firma
# -----------------------------
def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                origin_node_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                state TEXT,
                payload_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                previous_hash TEXT,
                event_hash TEXT NOT NULL,
                origin_signature_hex TEXT NOT NULL,
                validator_signature_hex TEXT NOT NULL
            )
        """)
        conn.execute("CREATE TABLE IF NOT EXISTS cluster_keys (node_id TEXT PRIMARY KEY, public_key_hex TEXT NOT NULL)")
        # Registrar clave propia
        conn.execute("INSERT OR IGNORE INTO cluster_keys (node_id, public_key_hex) VALUES (?, ?)", (NODE_ID, public_key_hex))
        conn.commit()

init_db()

def load_cluster_keys():
    with connect_db() as conn:
        rows = conn.execute("SELECT node_id, public_key_hex FROM cluster_keys").fetchall()
        for r in rows:
            CLUSTER_KEYS[r["node_id"]] = VerifyingKey.from_string(bytes.fromhex(r["public_key_hex"]), curve=SECP256k1)
load_cluster_keys()

def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def append_event(origin_node: str, origin_sig: str, phase: str, state: Optional[str], payload: dict) -> dict:
    event_id = str(uuid.uuid4())
    timestamp = time.time()
    payload_json = canonical_json(payload)

    with DB_LOCK:
        conn = connect_db()
        try:
            conn.execute("BEGIN IMMEDIATE")
            prev = conn.execute("SELECT event_hash FROM audit_events ORDER BY seq DESC LIMIT 1").fetchone()
            previous_hash = prev["event_hash"] if prev else None

            unsigned_event = {
                "event_id": event_id,
                "origin_node_id": origin_node,
                "phase": phase,
                "state": state,
                "payload": payload,
                "timestamp": timestamp,
                "previous_hash": previous_hash
            }
            
            event_hash = hashlib.sha256(canonical_json(unsigned_event).encode("utf-8")).hexdigest()
            
            # Doble Firma (El Validador firma el hash final que incluye el contexto de la cadena)
            validator_signature_hex = private_key.sign(event_hash.encode()).hex()

            conn.execute("""
                INSERT INTO audit_events 
                (event_id, origin_node_id, phase, state, payload_json, timestamp, previous_hash, event_hash, origin_signature_hex, validator_signature_hex)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_id, origin_node, phase, state, payload_json, timestamp, previous_hash, event_hash, origin_sig, validator_signature_hex))
            
            conn.commit()
        except RuntimeError:
            conn.rollback()
            raise
        finally:
            conn.close()

    return {**unsigned_event, "hash": event_hash, "validator_signature": validator_signature_hex}

# -----------------------------
# API
# -----------------------------
app = FastAPI(title="MCON C5-REAL (Zero-Trust BFT)", version="3.0.0")

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and (not x_api_key or not secrets.compare_digest(x_api_key, API_KEY)):
        raise HTTPException(status_code=401, detail="API key inválida")

@app.post("/register-node", dependencies=[Depends(require_api_key)])
def register_node(node_id: str = Query(...), pub_key_hex: str = Query(...)):
    """Registra dinámicamente un nodo del clúster BFT."""
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(pub_key_hex), curve=SECP256k1)
        CLUSTER_KEYS[node_id] = vk
        with connect_db() as conn:
            conn.execute("INSERT OR REPLACE INTO cluster_keys (node_id, public_key_hex) VALUES (?, ?)", (node_id, pub_key_hex))
            conn.commit()
        return {"accepted": True, "msg": f"Node {node_id} registrado."}
    except RuntimeError as e:
        raise HTTPException(400, f"Clave pública inválida: {e}")

@app.post("/events", dependencies=[Depends(require_api_key)])
async def create_event(
    request: Request,
    event: AuditEventInput,
    x_node_id: str = Header(...),
    x_node_signature: str = Header(...)
):
    """
    Zero-Trust Endpoint: Requiere que el payload esté firmado por la clave criptográfica del origin_node.
    """
    if x_node_id not in CLUSTER_KEYS:
        raise HTTPException(403, f"Nodo {x_node_id} desconocido. Requiere registro previo en BFT Cluster.")
    
    # Reconstruir raw body para validación de firma
    raw_body = await request.body()
    payload_hash = hashlib.sha256(raw_body).hexdigest()
    
    vk = CLUSTER_KEYS[x_node_id]
    try:
        vk.verify(bytes.fromhex(x_node_signature), payload_hash.encode())
    except BadSignatureError:
        raise HTTPException(403, f"💀 Firma ECDSA rechazada (Spoofing detectado desde {x_node_id})")

    state = STATE_BY_EMOJI.get(event.emoji) if event.emoji else event.state
    return {"accepted": True, "event": append_event(origin_node=x_node_id, origin_sig=x_node_signature, phase=event.phase, state=state, payload=event.payload)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
