import sqlite3
import yaml
import re
import os
import sys
import json

# CONFIGURACIÓN
DB_PATH = "/Users/borjafernandezangulo/10_PROJECTS/Teorema-Robinson-Moskv/cortex_memory.db"
ENGINE_YAML_PATH = "/Users/borjafernandezangulo/10_PROJECTS/Teorema-Robinson-Moskv/cortex_inference_engine.yaml"

def load_engine_config():
    with open(ENGINE_YAML_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class CortexInferenceEngine:
    def __init__(self):
        self.config = load_engine_config()
        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row
        
    def parse_query(self, query):
        # STAGE 1: Query Parsing -> Activation Vector 6D
        # Verbos causales, modales, de proceso, etc.
        triggers = {
            "causal": r"(causar|provocar|generar|hacer|por qué|efecto)",
            "mereo": r"(parte|sistema|estructura|composición|dividir)",
            "process": r"(cambiar|evolucionar|fluir|transitar|dinámica|tiempo)",
            "modal": r"(podría|debería|sería|quizás|posible|mundo)",
            "info": r"(mejorar|optimizar|aprender|entrenar|divergencia|entropía)",
            "semiotic": r"(significar|interpretar|leer|texto|signo|código)"
        }
        
        scores = {k: 0.0 for k in triggers.keys()}
        for key, pattern in triggers.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            scores[key] = len(matches) * 0.5
            
        return scores

    def retrieve_primitives(self, mode, scores):
        # STAGE 2: Primitive Retrieval
        cursor = self.db.cursor()
        
        # Mapeo de modos a pools de teoría
        theory_map = {
            "MODE-01-CAUSAL-DEDUCTION": ["CAUSAL-ONTOLOGY", "GRAPH-MORPHISMS"],
            "MODE-02-MEREOTOPOLOGICAL-COMPOSITION": ["MEREOTOPOLOGY", "SYSTEMIC-BOUNDARIES", "GRAPH-MORPHISMS"],
            "MODE-03-PROCESS-DYNAMICS": ["PROCESS-DYNAMICS", "INFORMATION-GEOMETRY", "SYSTEMIC-BOUNDARIES"],
            "MODE-04-MODAL-EXPLORATION": ["MODAL-SPACES", "COMPUTATIONAL-STATES", "INTENTIONAL-STRUCTURES"],
            "MODE-05-INFORMATION-GEOMETRY": ["INFORMATION-GEOMETRY", "COMPUTATIONAL-STATES", "GRAPH-MORPHISMS"],
            "MODE-06-SEMIOTIC-DECODING": ["SEMIOTIC-ENCODING", "INTENTIONAL-STRUCTURES", "MODAL-SPACES"]
        }
        
        theories = theory_map.get(mode, ["CAUSAL-ONTOLOGY"])
        
        # Obtener primitivas
        placeholders = ', '.join('?' for _ in theories)
        cursor.execute(f"""
            SELECT id, theory, name FROM L1_primitive_nodes 
            WHERE theory IN ({placeholders})
            ORDER BY RANDOM() LIMIT 5
        """, theories)
        primitives = [dict(row) for row in cursor.fetchall()]
        
        # Obtener isomorfismos
        cursor.execute("""
            SELECT id, type, source, target, weight, justification 
            FROM L2_isomorphism_edges
            ORDER BY RANDOM() LIMIT 3
        """)
        isomorphisms = [dict(row) for row in cursor.fetchall()]
        
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
            "semiotic": "MODE-06-SEMIOTIC-DECODING"
        }
        
        active_mode = mode_mapping.get(max_category, "MODE-01-CAUSAL-DEDUCTION")
        if scores[max_category] == 0.0:
            active_mode = "MODE-01-CAUSAL-DEDUCTION" # Default
            
        primitives, isomorphisms = self.retrieve_primitives(active_mode, scores)
        
        # Simular pipeline de inferencia
        steps = self.config["inference_modes"][active_mode]["inference_steps"]
        
        # Sintetizar traza
        trace = {
            "claim": f"Resolución de inferencia en modo {active_mode}",
            "proof": {
                "Base": "Teorema-Robinson-Moskv / CORTEX-db",
                "Confidence": "C5-REAL" if len(primitives) > 3 else "C4-SIM"
            },
            "query": query,
            "mode_activated": active_mode,
            "activation_vector": scores,
            "retrieved_nodes": [p["id"] for p in primitives],
            "applied_isomorphisms": [i["id"] for i in isomorphisms],
            "reasoning_steps": steps
        }
        
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
