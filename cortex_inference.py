import sqlite3
import yaml
import re
import os
import sys
import json
import hashlib
import math
from collections import Counter
from scientific_engine import compute_asymmetric_trust_isomorphism, compute_shannon_entropy

# CONFIGURACIÓN
_BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE, "cortex_memory.db")
ENGINE_YAML_PATH = os.path.join(_BASE, "cortex_inference_engine.yaml")

def load_engine_config():
    with open(ENGINE_YAML_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class CortexInferenceEngine:
    TRIGGERS = {
        "causal": re.compile(r"(causar|provocar|generar|hacer|por qué|efecto)", re.IGNORECASE),
        "mereo": re.compile(r"(parte|sistema|estructura|composición|dividir)", re.IGNORECASE),
        "process": re.compile(r"(cambiar|evolucionar|fluir|transitar|dinámica|tiempo)", re.IGNORECASE),
        "modal": re.compile(r"(podría|debería|sería|quizás|posible|mundo)", re.IGNORECASE),
        "info": re.compile(r"(mejorar|optimizar|aprender|entrenar|divergencia|entropía)", re.IGNORECASE),
        "semiotic": re.compile(r"(significar|interpretar|leer|texto|signo|código)", re.IGNORECASE),
        "epistemic": re.compile(r"(confianza|verdad|verificar|test|hash|isomorfismo)", re.IGNORECASE)
    }

    def __init__(self, db_path=None):
        self.config = load_engine_config()
        self.db = sqlite3.connect(db_path or DB_PATH, timeout=5.0)
        self.db.execute("PRAGMA journal_mode = WAL;")
        self.db.execute("PRAGMA busy_timeout = 5000;")
        self.db.row_factory = sqlite3.Row
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        if hasattr(self, "db") and self.db:
            self.db.close()
        
    def parse_query(self, query):
        # STAGE 1: Query Parsing -> Activation Vector 6D
        # Verbos causales, modales, de proceso, etc.
        scores = {k: 0.0 for k in self.TRIGGERS.keys()}
        for key, pattern in self.TRIGGERS.items():
            matches = pattern.findall(query)
            scores[key] = len(matches) * 0.5
            
        return scores

    def retrieve_primitives(self, mode, scores, query=""):
        # STAGE 2: Primitive Retrieval
        cursor = self.db.cursor()
        
        # Mapeo de modos a pools de teoría
        theory_map = {
            "MODE-01-CAUSAL-DEDUCTION": ["CAUSAL-ONTOLOGY", "GRAPH-MORPHISMS"],
            "MODE-02-MEREOTOPOLOGICAL-COMPOSITION": ["MEREOTOPOLOGY", "SYSTEMIC-BOUNDARIES", "GRAPH-MORPHISMS"],
            "MODE-03-PROCESS-DYNAMICS": ["PROCESS-DYNAMICS", "INFORMATION-GEOMETRY", "SYSTEMIC-BOUNDARIES"],
            "MODE-04-MODAL-EXPLORATION": ["MODAL-SPACES", "COMPUTATIONAL-STATES", "INTENTIONAL-STRUCTURES"],
            "MODE-05-INFORMATION-GEOMETRY": ["INFORMATION-GEOMETRY", "COMPUTATIONAL-STATES", "GRAPH-MORPHISMS"],
            "MODE-06-SEMIOTIC-DECODING": ["SEMIOTIC-ENCODING", "INTENTIONAL-STRUCTURES", "MODAL-SPACES"],
            "MODE-07-EPISTEMIC-TRUST": ["EPISTEMIC-BOUNDARY", "ASYMMETRIC-TRUST", "GRAPH-MORPHISMS"]
        }
        
        theories = theory_map.get(mode, ["CAUSAL-ONTOLOGY"])
        
        # Obtener primitivas
        placeholders = ', '.join('?' for _ in theories)
        query_seed = int(hashlib.md5(query.encode('utf-8')).hexdigest()[:8], 16) if query else 1
        cursor.execute(f"""
            SELECT id, theory, name FROM L1_primitive_nodes 
            WHERE theory IN ({placeholders})
        """, theories)
        all_primitives = [dict(row) for row in cursor.fetchall()]
        
        # Ordenamiento determinista en base a query_seed en Python
        # para evitar fallos de coerción TEXT a NUMERIC en SQLite (id * ?)
        all_primitives.sort(key=lambda p: hashlib.md5(f"{p['id']}-{query_seed}".encode('utf-8')).hexdigest())
        primitives = all_primitives[:5]
        
        # Obtener isomorfismos
        cursor.execute("""
            SELECT id, type, source, target, weight, justification 
            FROM L2_isomorphism_edges
        """)
        all_isomorphisms = [dict(row) for row in cursor.fetchall()]
        all_isomorphisms.sort(key=lambda i: hashlib.md5(f"{i['id']}-{query_seed}".encode('utf-8')).hexdigest())
        isomorphisms = all_isomorphisms[:3]
        
        return primitives, isomorphisms

    def execute_inference(self, query):
        scores = self.parse_query(query)
        
        # Determinar modo principal
        sorted_modes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        max_category = sorted_modes[0][0]
        
        mode_mapping = {
            "causal": "MODE-01-CAUSAL-DEDUCTION",
            "mereo": "MODE-02-MEREOTOPOLOGICAL-COMPOSITION",
            "process": "MODE-03-PROCESS-DYNAMICS",
            "modal": "MODE-04-MODAL-EXPLORATION",
            "info": "MODE-05-INFORMATION-GEOMETRY",
            "semiotic": "MODE-06-SEMIOTIC-DECODING",
            "epistemic": "MODE-07-EPISTEMIC-TRUST"
        }
        
        active_mode = mode_mapping.get(max_category, "MODE-01-CAUSAL-DEDUCTION")
        if scores[max_category] == 0.0:
            active_mode = "MODE-01-CAUSAL-DEDUCTION" # Default
            
        primitives, isomorphisms = self.retrieve_primitives(active_mode, scores, query)
        
        # Simular pipeline de inferencia
        steps = self.config["inference_modes"][active_mode]["inference_steps"]
        
        # Calculate entropy of primitive nodes to feed isomorphism
        node_names = [p["name"] for p in primitives]
        entropy = compute_shannon_entropy(node_names)["entropy"]
                
        if active_mode == "MODE-07-EPISTEMIC-TRUST":
            has_hash = "hash" in query.lower() or "isomorfismo" in query.lower()
            has_test = "test" in query.lower() or "verificar" in query.lower()
            query_hash = hashlib.sha256(query.encode('utf-8')).hexdigest()
            trust_metric = compute_asymmetric_trust_isomorphism(query_hash if has_hash else None, has_test, entropy)
            confidence = trust_metric["reality_level"]
        else:
            confidence = "C5-REAL" if len(primitives) > 3 else "C4-SIM"
        
        # Sintetizar traza
        trace = {
            "claim": f"Resolución de inferencia en modo {active_mode}",
            "proof": {
                "Base": "Teorema-Robinson-Moskv / CORTEX-db",
                "Confidence": confidence
            },
            "query": query,
            "mode_activated": active_mode,
            "activation_vector": scores,
            "retrieved_nodes": [p["id"] for p in primitives],
            "applied_isomorphisms": [i["id"] for i in isomorphisms],
            "reasoning_steps": steps
        }
        
        if active_mode == "MODE-07-EPISTEMIC-TRUST":
            trace["epistemic_trust_metric"] = trust_metric

        
        return trace

if __name__ == "__main__":
    is_json = False
    args = sys.argv[1:]
    if args and args[0] == "--json":
        is_json = True
        args = args[1:]
        
    if not args:
        query = "Por qué falló el sistema al cambiar el estado del proceso en el tiempo"
    else:
        query = " ".join(args)
        
    engine = CortexInferenceEngine()
    result = engine.execute_inference(query)
    
    if is_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(yaml.dump(result, allow_unicode=True, sort_keys=False))
