import hashlib
import json
import logging
import os
import secrets
import sqlite3
import threading
import time
import uuid
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

# ❖ C5-REAL :: MCON API + ECDSA (ULTRATHINK) ❖
# API REST con Cadena Hash y Firmas Digitales Verificables.

# -----------------------------
# Configuración Criptográfica
# -----------------------------
NODE_ID = os.getenv("NODE_ID", "N0")
DB_PATH = os.getenv("MCON_DB", "mcon_audit_crypto.db")
API_KEY = os.getenv("MCON_API_KEY", "dev-secret")
KEY_PATH = f"{NODE_ID}_private.pem"

logging.basicConfig(level="INFO", format="%(message)s")
logger = logging.getLogger("cortex_mcon")

# Generar o Cargar Clave Privada ECDSA
if os.path.exists(KEY_PATH):
    with open(KEY_PATH, "rb") as f:
        private_key = SigningKey.from_pem(f.read())
else:
    private_key = SigningKey.generate(curve=SECP256k1)
    with open(KEY_PATH, "wb") as f:
        f.write(private_key.to_pem())

public_key = private_key.get_verifying_key()
public_key_hex = public_key.to_string().hex()

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
class StateUpdate(BaseModel):
    state: Optional[str] = Field(default=None)
    emoji: Optional[str] = Field(default=None)
    reason: str = Field(default="", max_length=500)

class AuditEventInput(BaseModel):
    phase: str = Field(min_length=1, max_length=32)
    state: Optional[str] = None
    emoji: Optional[str] = None
    payload: dict = Field(default_factory=dict)

# -----------------------------
# Base de Datos con Firmas
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
                node_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                state TEXT,
                payload_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                previous_hash TEXT,
                event_hash TEXT NOT NULL,
                public_key_hex TEXT NOT NULL,
                signature_hex TEXT NOT NULL
            )
        """)
        conn.execute("CREATE TABLE IF NOT EXISTS runtime_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("INSERT OR IGNORE INTO runtime_state(key, value) VALUES ('state', 'IDLE')")
        conn.commit()

init_db()

def canonical_json(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def get_current_state() -> str:
    with connect_db() as conn:
        row = conn.execute("SELECT value FROM runtime_state WHERE key = 'state'").fetchone()
    return row["value"] if row else "IDLE"

def append_event(phase: str, state: Optional[str], payload: dict, update_runtime_state: Optional[str] = None) -> dict:
    event_id = str(uuid.uuid4())
    timestamp = time.time()
    payload_json = canonical_json(payload)

    with DB_LOCK:
        conn = connect_db()
        try:
            conn.execute("BEGIN IMMEDIATE")
            prev = conn.execute("SELECT event_hash FROM audit_events ORDER BY seq DESC LIMIT 1").fetchone()
            previous_hash = prev["event_hash"] if prev else None

            # Contenido a Firmar y Hashear
            unsigned_event = {
                "event_id": event_id,
                "node_id": NODE_ID,
                "phase": phase,
                "state": state,
                "payload": payload,
                "timestamp": timestamp,
                "previous_hash": previous_hash
            }
            
            event_hash = hashlib.sha256(canonical_json(unsigned_event).encode("utf-8")).hexdigest()
            signature_hex = private_key.sign(event_hash.encode()).hex()

            conn.execute("""
                INSERT INTO audit_events 
                (event_id, node_id, phase, state, payload_json, timestamp, previous_hash, event_hash, public_key_hex, signature_hex)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_id, NODE_ID, phase, state, payload_json, timestamp, previous_hash, event_hash, public_key_hex, signature_hex))

            if update_runtime_state:
                conn.execute("UPDATE runtime_state SET value = ? WHERE key = 'state'", (update_runtime_state,))
            
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    return {**unsigned_event, "hash": event_hash, "signature": signature_hex, "emoji": EMOJI_BY_STATE.get(state)}

# -----------------------------
# API
# -----------------------------
app = FastAPI(title="MCON C5-REAL (ECDSA)", version="2.0.0")

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if API_KEY and (not x_api_key or not secrets.compare_digest(x_api_key, API_KEY)):
        raise HTTPException(status_code=401, detail="API key inválida")

@app.get("/healthz")
def healthz():
    state = get_current_state()
    return {"status": "ok", "node_id": NODE_ID, "state": state, "emoji": EMOJI_BY_STATE.get(state, "📦")}

@app.get("/public-key")
def get_public_key():
    return {"node_id": NODE_ID, "public_key_hex": public_key_hex}

@app.post("/events", dependencies=[Depends(require_api_key)])
def create_event(event: AuditEventInput):
    state = STATE_BY_EMOJI.get(event.emoji) if event.emoji else event.state
    return {"accepted": True, "event": append_event(phase=event.phase, state=state, payload=event.payload)}

@app.get("/verify-chain")
def verify_chain():
    with connect_db() as conn:
        rows = conn.execute("SELECT * FROM audit_events ORDER BY seq ASC").fetchall()
    
    previous_hash = None
    for row in rows:
        unsigned_event = {
            "event_id": row["event_id"],
            "node_id": row["node_id"],
            "phase": row["phase"],
            "state": row["state"],
            "payload": json.loads(row["payload_json"]),
            "timestamp": row["timestamp"],
            "previous_hash": previous_hash
        }
        
        expected_hash = hashlib.sha256(canonical_json(unsigned_event).encode("utf-8")).hexdigest()
        if row["previous_hash"] != previous_hash:
            return {"valid": False, "seq": row["seq"], "error": "previous_hash roto (Fork detectado)"}
        if row["event_hash"] != expected_hash:
            return {"valid": False, "seq": row["seq"], "error": "event_hash inconsistente (Mutación de datos)"}
        
        vk = VerifyingKey.from_string(bytes.fromhex(row["public_key_hex"]), curve=SECP256k1)
        try:
            vk.verify(bytes.fromhex(row["signature_hex"]), expected_hash.encode())
        except BadSignatureError:
            return {"valid": False, "seq": row["seq"], "error": "Firma ECDSA rechazada (Spoofing detectado)"}
            
        previous_hash = row["event_hash"]

    return {"valid": True, "events_checked": len(rows), "status": "Cadena criptográficamente inmutable"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    with connect_db() as conn:
        rows = conn.execute("SELECT phase, COUNT(*) AS total FROM audit_events GROUP BY phase").fetchall()
    
    lines = ["# HELP mcon_events_total Eventos registrados por fase.", "# TYPE mcon_events_total counter"]
    for row in rows:
        lines.append(f'mcon_events_total{{phase="{row["phase"]}"}} {row["total"]}')
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
