import babylon60
import time
from typing import Final
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
    conn = connect(DB_PATH)
    try:
        conn.execute(
            "\n            CREATE TABLE IF NOT EXISTS exergy_ledger (\n                causal_hash TEXT PRIMARY KEY,\n                tokens INTEGER,\n                temperature REAL,\n                exergy REAL,\n                lamport_t INTEGER\n            )\n        "
        )
    finally:
        conn.close()


def calculate_exergy(tokens: int, temperature: Decimal) -> ExergyNode:
    if temperature <= Decimal("0.0"):
        raise ValueError("Violación Termodinámica: Temperatura debe ser > 0.")
    exergy = tokens * 100 / temperature
    lamport_t = int(time.time() * 1000)
    raw_causal = f"{tokens}|{temperature}|{exergy}|{lamport_t}"
    causal_hash = babylon60.blake2b_hash(raw_causal)
    node = ExergyNode(
        tokens=tokens,
        temperature=temperature,
        exergy=exergy,
        causal_hash=causal_hash,
        lamport_t=lamport_t,
    )
    conn = connect(DB_PATH)
    try:
        with causal_write(conn), conn:
            conn.execute(
                "\n                INSERT INTO exergy_ledger (causal_hash, tokens, temperature, exergy, lamport_t)\n                VALUES (?, ?, ?, ?, ?)\n            ",
                (
                    node.causal_hash,
                    node.tokens,
                    float(node.temperature),
                    float(node.exergy),
                    node.lamport_t,
                ),
            )
    finally:
        conn.close()
    return node


init_ledger()
