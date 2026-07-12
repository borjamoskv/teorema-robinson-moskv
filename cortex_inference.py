import asyncio
import aiosqlite
import yaml
import re
import os
import sys
import json
from cryptography.fernet import Fernet
import babylon60
from babylon60.ledger import SovereignLedger
from scientific_engine import (
    compute_asymmetric_trust_isomorphism,
    compute_shannon_entropy,
)
from decimal import Decimal

_BASE = os.path.dirname(os.path.abspath(__file__))
ENGINE_YAML_PATH = os.path.join(_BASE, "cortex_inference_engine.yaml")
VAULT_PATH = os.environ.get("BABYLON_VAULT", os.path.expanduser("~/.babylon60"))
DB_PATH = os.path.join(VAULT_PATH, "cortex_memory.db")
CACHE_DB_PATH = os.path.join(VAULT_PATH, "nexus_cache.db")
if not os.path.exists(ENGINE_YAML_PATH):
    print(
        f"\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m Essential Config Missing: {ENGINE_YAML_PATH}. C5-REAL Fail-Fast.",
        file=sys.stderr,
    )
    sys.exit(1)
with open(ENGINE_YAML_PATH, "r", encoding="utf-8") as f:
    ENGINE_CONFIG = yaml.safe_load(f)


class CortexInferenceEngine:
    TRIGGERS = {
        "causal": re.compile(
            "\\b(causar|provocar|generar|hacer|por qué|efecto)\\b", re.IGNORECASE
        ),
        "mereo": re.compile(
            "\\b(parte|sistema|estructura|composición|dividir)\\b", re.IGNORECASE
        ),
        "process": re.compile(
            "\\b(cambiar|evolucionar|fluir|transitar|dinámica|tiempo)\\b", re.IGNORECASE
        ),
        "modal": re.compile(
            "\\b(podría|debería|sería|quizás|posible|mundo)\\b", re.IGNORECASE
        ),
        "info": re.compile(
            "\\b(mejorar|optimizar|aprender|entrenar|divergencia|entropía)\\b",
            re.IGNORECASE,
        ),
        "semiotic": re.compile(
            "\\b(significar|interpretar|leer|texto|signo|código)\\b", re.IGNORECASE
        ),
        "epistemic": re.compile(
            "\\b(confianza|verdad|verificar|test|hash|isomorfismo)\\b", re.IGNORECASE
        ),
    }

    def __init__(self, db_path=None, cache_db_path=None) -> "Any":
        self.config = ENGINE_CONFIG
        self.target_db = db_path or DB_PATH
        self.target_cache = cache_db_path or CACHE_DB_PATH
        self.db = None
        self.cache_db = None
        self.ledger = None

    async def initialize(self):
        db_uri = f"file:{self.target_db}?mode=ro"
        self.db = await aiosqlite.connect(db_uri, uri=True, timeout=5.0)
        self.db.row_factory = aiosqlite.Row
        import sqlite3

        sync_conn = sqlite3.connect(self.target_cache, timeout=5.0)
        _ = SovereignLedger(sync_conn)
        sync_conn.close()
        self.cache_db = await aiosqlite.connect(self.target_cache, timeout=5.0)
        await self.cache_db.execute("PRAGMA journal_mode = WAL;")
        await self.cache_db.execute("PRAGMA busy_timeout = 5000;")
        self.cache_db.row_factory = aiosqlite.Row
        await self.cache_db.execute(
            "\n            CREATE TABLE IF NOT EXISTS L3_inference_cache (\n                query_hash TEXT PRIMARY KEY,\n                active_mode TEXT,\n                retrieved_nodes TEXT,\n                applied_isomorphisms TEXT,\n                trace_payload TEXT,\n                hits INTEGER DEFAULT 0\n            )\n        "
        )
        await self.cache_db.commit()
        self.ledger = SovereignLedger(self.cache_db)

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self.db:
            await self.db.close()
        if self.cache_db:
            await self.cache_db.close()

    def parse_query(self, query) -> "Any":
        scores = {k: Decimal("0.0") for k in self.TRIGGERS.keys()}
        for key, pattern in self.TRIGGERS.items():
            matches = pattern.findall(query)
            scores[key] = Decimal(len(matches)) * Decimal("0.5")
        return scores

    async def retrieve_primitives(self, mode, scores, query=""):
        theory_map = {
            "MODE-01-CAUSAL-DEDUCTION": ["CAUSAL-ONTOLOGY", "GRAPH-MORPHISMS"],
            "MODE-02-MEREOTOPOLOGICAL-COMPOSITION": [
                "MEREOTOPOLOGY",
                "SYSTEMIC-BOUNDARIES",
                "GRAPH-MORPHISMS",
            ],
            "MODE-03-PROCESS-DYNAMICS": [
                "PROCESS-DYNAMICS",
                "INFORMATION-GEOMETRY",
                "SYSTEMIC-BOUNDARIES",
            ],
            "MODE-04-MODAL-EXPLORATION": [
                "MODAL-SPACES",
                "COMPUTATIONAL-STATES",
                "INTENTIONAL-STRUCTURES",
            ],
            "MODE-05-INFORMATION-GEOMETRY": [
                "INFORMATION-GEOMETRY",
                "COMPUTATIONAL-STATES",
                "GRAPH-MORPHISMS",
            ],
            "MODE-06-SEMIOTIC-DECODING": [
                "SEMIOTIC-ENCODING",
                "INTENTIONAL-STRUCTURES",
                "MODAL-SPACES",
            ],
            "MODE-07-EPISTEMIC-TRUST": [
                "EPISTEMIC-BOUNDARY",
                "ASYMMETRIC-TRUST",
                "GRAPH-MORPHISMS",
            ],
        }
        theories = theory_map.get(mode, ["CAUSAL-ONTOLOGY"])
        placeholders = ", ".join(("?" for _ in theories))
        async with self.db.execute(
            f"\n            SELECT id, theory, name FROM L1_primitive_nodes \n            WHERE theory IN ({placeholders})\n            ORDER BY id\n            LIMIT 5\n        ",
            theories,
        ) as cursor:
            primitives = [dict(row) for row in await cursor.fetchall()]
        prim_ids = [p["id"] for p in primitives]
        if prim_ids:
            p_placeholders = ", ".join(("?" for _ in prim_ids))
            async with self.db.execute(
                f"\n                SELECT id, type, source, target, weight, justification \n                FROM L2_isomorphism_edges\n                WHERE source IN ({p_placeholders}) OR target IN ({p_placeholders})\n                LIMIT 3\n            ",
                prim_ids * 2,
            ) as cursor:
                isomorphisms = [dict(row) for row in await cursor.fetchall()]
        else:
            isomorphisms = []
        return (primitives, isomorphisms)

    async def execute_inference(self, query):
        normalized_query = query.strip().lower()
        query_hash = babylon60.sha256_hash(normalized_query)
        async with self.cache_db.execute(
            "SELECT trace_payload FROM L3_inference_cache WHERE query_hash = ?",
            (query_hash,),
        ) as cache_cursor:
            cached = await cache_cursor.fetchone()
        if cached:
            trace_payload_raw = cached["trace_payload"]
            vault_key = os.environ.get("CORTEX_VAULT_KEY")
            if vault_key and trace_payload_raw.startswith("C5ENC:"):
                fernet = Fernet(vault_key.encode("utf-8"))
                trace_payload_raw = fernet.decrypt(
                    trace_payload_raw[6:].encode("utf-8")
                ).decode("utf-8")
            trace_data = json.loads(trace_payload_raw)
            await self.ledger.record_transaction_async(
                project="CORTEX_INFERENCE_L3",
                action="CACHE_HIT_BYPASS",
                detail={"query_hash": query_hash},
                tenant_id="inference_engine",
            )
            return trace_data
        scores = self.parse_query(query)
        sorted_modes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        max_category = sorted_modes[0][0]
        mode_mapping = {
            "causal": "MODE-01-CAUSAL-DEDUCTION",
            "mereo": "MODE-02-MEREOTOPOLOGICAL-COMPOSITION",
            "process": "MODE-03-PROCESS-DYNAMICS",
            "modal": "MODE-04-MODAL-EXPLORATION",
            "info": "MODE-05-INFORMATION-GEOMETRY",
            "semiotic": "MODE-06-SEMIOTIC-DECODING",
            "epistemic": "MODE-07-EPISTEMIC-TRUST",
        }
        active_mode = mode_mapping.get(max_category, "MODE-01-CAUSAL-DEDUCTION")
        if scores[max_category] == Decimal("0.0"):
            active_mode = "MODE-01-CAUSAL-DEDUCTION"
        primitives, isomorphisms = await self.retrieve_primitives(
            active_mode, scores, query
        )
        if active_mode not in self.config["inference_modes"]:
            print(
                f"\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m YAML Key missing for mode {active_mode}. C5-REAL Fail-Fast.",
                file=sys.stderr,
            )
            sys.exit(1)
        steps = self.config["inference_modes"][active_mode]["inference_steps"]
        node_names = [p["name"] for p in primitives]
        entropy = compute_shannon_entropy(node_names)["entropy"]
        if active_mode == "MODE-07-EPISTEMIC-TRUST":
            has_hash = "hash" in query.lower() or "isomorfismo" in query.lower()
            has_test = "test" in query.lower() or "verificar" in query.lower()
            query_hash = babylon60.sha256_hash(query)
            trust_metric = compute_asymmetric_trust_isomorphism(
                query_hash if has_hash else None, has_test, entropy
            )
            confidence = trust_metric["reality_level"]
        else:
            confidence = "C5-REAL" if len(primitives) > 3 else "C4-SIM"

        def decimal_to_str(obj) -> "Any":
            if isinstance(obj, dict):
                return {k: decimal_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_str(x) for x in obj]
            elif isinstance(obj, Decimal):
                return float(obj)
            return obj

        trace = {
            "claim": f"Resolución de inferencia en modo {active_mode}",
            "proof": {
                "Base": "Teorema-Robinson-Moskv / CORTEX-db",
                "Confidence": confidence,
            },
            "query": query,
            "mode_activated": active_mode,
            "activation_vector": decimal_to_str(scores),
            "retrieved_nodes": [p["id"] for p in primitives],
            "applied_isomorphisms": [i["id"] for i in isomorphisms],
            "reasoning_steps": steps,
        }
        if active_mode == "MODE-07-EPISTEMIC-TRUST":
            trace["epistemic_trust_metric"] = trust_metric
        vault_key = os.environ.get("CORTEX_VAULT_KEY")
        payload_raw = json.dumps(trace, ensure_ascii=False)
        if vault_key:
            fernet = Fernet(vault_key.encode("utf-8"))
            stored_payload = (
                f"C5ENC:{fernet.encrypt(payload_raw.encode('utf-8')).decode('utf-8')}"
            )
        else:
            stored_payload = payload_raw
        await self.cache_db.execute(
            "\n            INSERT INTO L3_inference_cache \n            (query_hash, active_mode, retrieved_nodes, applied_isomorphisms, trace_payload, hits)\n            VALUES (?, ?, ?, ?, ?, 0)\n            ON CONFLICT(query_hash) DO UPDATE SET\n                active_mode = excluded.active_mode,\n                retrieved_nodes = excluded.retrieved_nodes,\n                applied_isomorphisms = excluded.applied_isomorphisms,\n                trace_payload = excluded.trace_payload\n            ",
            (
                query_hash,
                active_mode,
                json.dumps(trace["retrieved_nodes"], ensure_ascii=False),
                json.dumps(trace["applied_isomorphisms"], ensure_ascii=False),
                stored_payload,
            ),
        )
        await self.cache_db.commit()
        await self.ledger.record_transaction_async(
            project="CORTEX_INFERENCE",
            action="CACHE_MISS_EVALUATED",
            detail={"query_hash": query_hash, "mode_activated": active_mode},
            tenant_id="inference_engine",
        )
        return trace


async def main():
    is_json = False
    args = sys.argv[1:]
    if args and args[0] == "--json":
        is_json = True
        args = args[1:]
    if not args:
        query = "Por qué falló el sistema al cambiar el estado del proceso en el tiempo"
    else:
        query = " ".join(args)
    async with CortexInferenceEngine() as engine:
        result = await engine.execute_inference(query)
        if is_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(yaml.dump(result, allow_unicode=True, sort_keys=False))


if __name__ == "__main__":
    asyncio.run(main())
