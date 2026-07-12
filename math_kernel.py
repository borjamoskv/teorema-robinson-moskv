import babylon60
import time
from typing import Final, Tuple
from dataclasses import dataclass
from decimal import Decimal
from babylon60.database.core import connect, causal_write

DB_PATH: Final[str] = "nexus_anchors.db"

@dataclass(frozen=True)
class ExergyNode:
    tokens: int
    temperature: Decimal
    exergy: Decimal
    causal_hash: str
    lamport_t: int

def init_ledger() -> None:
    """Ignición determinista del Master Ledger con WAL y busy_timeout de 5000ms."""
    conn = connect(DB_PATH)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exergy_ledger (
                causal_hash TEXT PRIMARY KEY,
                tokens INTEGER,
                temperature REAL,
                exergy REAL,
                lamport_t INTEGER
            )
        ''')
    finally:
        conn.close()

def calculate_exergy(tokens: int, temperature: Decimal) -> ExergyNode:
    """
    Colapso termodinámico de la exergía con anclaje criptográfico.
    La exergía decrece dividiendo la base entrópica por la temperatura.
    """
    if temperature <= Decimal("0.0"):
        raise ValueError("Violación Termodinámica: Temperatura debe ser > 0.")
        
    exergy = (tokens * 100) / temperature
    lamport_t = int(time.time() * 1000)
    
    # Hash causal de procedencia (FFI ring)
    raw_causal = f"{tokens}|{temperature}|{exergy}|{lamport_t}"
    causal_hash = babylon60.blake2b_hash(raw_causal)
    
    node = ExergyNode(
        tokens=tokens,
        temperature=temperature,
        exergy=exergy,
        causal_hash=causal_hash,
        lamport_t=lamport_t
    )
    
    # Persistencia BFT en Master Ledger
    conn = connect(DB_PATH)
    try:
        with causal_write(conn), conn:
            conn.execute('''
                INSERT INTO exergy_ledger (causal_hash, tokens, temperature, exergy, lamport_t)
                VALUES (?, ?, ?, ?, ?)
            ''', (node.causal_hash, node.tokens, float(node.temperature), float(node.exergy), node.lamport_t))
    finally:
        conn.close()
        
    return node

# Inicialización síncrona en carga de módulo
init_ledger()

