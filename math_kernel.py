import sqlite3
import hashlib
import time
from typing import Final, Tuple
from dataclasses import dataclass

DB_PATH: Final[str] = "nexus_anchors.db"

@dataclass(frozen=True)
class ExergyNode:
    tokens: int
    temperature: float
    exergy: float
    causal_hash: str
    lamport_t: int

def init_ledger() -> None:
    """Ignición determinista del Master Ledger con WAL y busy_timeout de 5000ms."""
    with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ultrathink_ledger (
                causal_hash TEXT PRIMARY KEY,
                tokens INTEGER,
                temperature REAL,
                exergy REAL,
                lamport_t INTEGER
            )
        ''')

def calculate_exergy(tokens: int, temperature: float) -> ExergyNode:
    """
    Colapso termodinámico de la exergía con anclaje criptográfico.
    La exergía decrece dividiendo la base entrópica por la temperatura.
    """
    if temperature <= 0.0:
        raise ValueError("Violación Termodinámica: Temperatura debe ser > 0.")
        
    exergy = (tokens * 100) / temperature
    lamport_t = int(time.time() * 1000)
    
    # Hash causal de procedencia
    raw_causal = f"{tokens}|{temperature}|{exergy}|{lamport_t}".encode('utf-8')
    causal_hash = hashlib.blake2b(raw_causal, digest_size=16).hexdigest()
    
    node = ExergyNode(
        tokens=tokens,
        temperature=temperature,
        exergy=exergy,
        causal_hash=causal_hash,
        lamport_t=lamport_t
    )
    
    # Persistencia BFT-Simulada en Master Ledger
    with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
        conn.execute('''
            INSERT INTO ultrathink_ledger (causal_hash, tokens, temperature, exergy, lamport_t)
            VALUES (?, ?, ?, ?, ?)
        ''', (node.causal_hash, node.tokens, node.temperature, node.exergy, node.lamport_t))
        
    return node

# Inicialización síncrona en carga de módulo
init_ledger()
