#!/usr/bin/env python3
# C5-REAL EXERGY CERTIFIED
"""
C5-REAL Cybernetics Quadrivium Concept & Claim Graph Builder (Level 5 / 6)
Construye la topología dinámica del grafo de conocimiento a partir del corpus
conforme a la ontología 11_knowledge_fabric_kernel_axioms.yaml.
"""

import json
import os
from typing import Dict, Any

def build_cybernetics_graph() -> Dict[str, Any]:
    ledger_path = "scratch/corpus/cybernetics_quadrivium_knowledge_ledger.json"
    if not os.path.exists(ledger_path):
        raise FileNotFoundError(f"No existe el archivo {ledger_path}. Ejecute scripts/c5_cybernetics_quadrivium_extractor.py primero.")

    with open(ledger_path, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    # 1. Definición de Nodos (Concepts, Authors, Theorems, Strata)
    nodes = [
        # Strata Nodes
        {"id": "stratum:ring_0", "type": "Stratum", "label": "00_ABZU_KERNEL (Ring-0)", "domain": "Hardware / C-ABI / Landauer"},
        {"id": "stratum:ring_1", "type": "Stratum", "label": "01_KISH_ENGINE (Ring-1)", "domain": "Active Inference / Epistemology / BFT"},
        {"id": "stratum:ring_2", "type": "Stratum", "label": "02_EDIN_SWARMS (Ring-2)", "domain": "Stochastic Swarm / Sensory Interface"},

        # Author Nodes
        {"id": "author:ashby", "type": "Person", "label": "W. Ross Ashby", "epoch": 1956, "focus": "Cybernetics of Variety & Homeostasis"},
        {"id": "author:bateson", "type": "Person", "label": "Gregory Bateson", "epoch": 1972, "focus": "Ecology of Mind & Double Bind"},
        {"id": "author:beer", "type": "Person", "label": "Stafford Beer", "epoch": 1972, "focus": "Viable System Model & Cybersyn"},
        {"id": "author:bandler_grinder", "type": "Person", "label": "Richard Bandler & John Grinder", "epoch": 1979, "focus": "Somatic Acuity & Involuntary Calibration"},

        # Book Nodes
        {"id": "book:ashby_1956", "type": "Book", "label": "An Introduction to Cybernetics (1956)", "author": "W. Ross Ashby"},
        {"id": "book:bateson_1972", "type": "Book", "label": "Steps to an Ecology of Mind (1972)", "author": "Gregory Bateson"},
        {"id": "book:beer_1972", "type": "Book", "label": "Brain of the Firm (1972)", "author": "Stafford Beer"},
        {"id": "book:bandler_grinder_1979", "type": "Book", "label": "Frogs into Princes (1979)", "author": "Bandler & Grinder"},

        # Concept & Law Nodes
        {"id": "law:requisite_variety", "type": "Claim", "label": "Law of Requisite Variety", "formula": "V(R) >= V(D) - V(K)", "aphorism_ref": "Aforismo 1"},
        {"id": "concept:black_box", "type": "Concept", "label": "Black Box Mapping", "formal_def": "T: X -> Y (Introspection Prohibited)"},
        {"id": "concept:homeostasis", "type": "Concept", "label": "Ultrastability & Homeostasis", "formal_def": "Step-mechanism essential variable recovery"},

        {"id": "law:difference_makes_difference", "type": "Claim", "label": "Information as Difference", "formula": "I = Delta", "aphorism_ref": "Aforismo 1"},
        {"id": "concept:double_bind", "type": "Concept", "label": "Double Bind Deadlock", "formal_def": "Conflicting injunctions at distinct logical types with closed exit", "aphorism_ref": "Aforismo 3"},
        {"id": "concept:deutero_learning", "type": "Concept", "label": "Deutero-Learning (Learning II / III)", "formal_def": "Contextual jump / Cambio 2", "aphorism_ref": "Aforismo 4"},

        {"id": "concept:vsm_recursion", "type": "Concept", "label": "Viable System Model Recursion", "formal_def": "Systems 1 to 5 structural coherence"},
        {"id": "concept:algedonic_loop", "type": "Concept", "label": "Algedonic Bypass Channel", "formal_def": "Pain/Pleasure immediate veto bypassing hierarchy"},

        {"id": "law:cost_of_forgery", "type": "Claim", "label": "Involuntary Signal Supremacy", "formula": "Cost(Involuntary) >> Cost(Voluntary)", "aphorism_ref": "Aforismo 5"},
        {"id": "concept:sensory_acuity", "type": "Concept", "label": "Sensory Acuity vs Hallucination", "formal_def": "Observing territory micro-cues vs cheap talk map", "aphorism_ref": "Aforismo 2"},
        {"id": "concept:reframing", "type": "Concept", "label": "Cybernetic Reframing", "formal_def": "Altering contextual boundary conditions"}
    ]

    # 2. Definición de Aristas / Relaciones Causal-Topológicas
    edges = [
        # Author writes Book
        {"source": "author:ashby", "target": "book:ashby_1956", "relation": "writes"},
        {"source": "author:bateson", "target": "book:bateson_1972", "relation": "writes"},
        {"source": "author:beer", "target": "book:beer_1972", "relation": "writes"},
        {"source": "author:bandler_grinder", "target": "book:bandler_grinder_1979", "relation": "writes"},

        # Book defines Concepts
        {"source": "book:ashby_1956", "target": "law:requisite_variety", "relation": "formulates"},
        {"source": "book:ashby_1956", "target": "concept:black_box", "relation": "formulates"},
        {"source": "book:ashby_1956", "target": "concept:homeostasis", "relation": "formulates"},

        {"source": "book:bateson_1972", "target": "law:difference_makes_difference", "relation": "formulates"},
        {"source": "book:bateson_1972", "target": "concept:double_bind", "relation": "formulates"},
        {"source": "book:bateson_1972", "target": "concept:deutero_learning", "relation": "formulates"},

        {"source": "book:beer_1972", "target": "concept:vsm_recursion", "relation": "formulates"},
        {"source": "book:beer_1972", "target": "concept:algedonic_loop", "relation": "formulates"},

        {"source": "book:bandler_grinder_1979", "target": "law:cost_of_forgery", "relation": "formulates"},
        {"source": "book:bandler_grinder_1979", "target": "concept:sensory_acuity", "relation": "formulates"},
        {"source": "book:bandler_grinder_1979", "target": "concept:reframing", "relation": "formulates"},

        # Cross-Domain Inter-relations
        {"source": "law:requisite_variety", "target": "concept:vsm_recursion", "relation": "constrains", "weight": 0.95},
        {"source": "concept:black_box", "target": "concept:sensory_acuity", "relation": "isomorphic_to", "weight": 0.90},
        {"source": "concept:double_bind", "target": "concept:deutero_learning", "relation": "triggers_bifurcation", "weight": 0.88},
        {"source": "concept:algedonic_loop", "target": "stratum:ring_0", "relation": "direct_bypass_to", "weight": 1.0},
        {"source": "law:cost_of_forgery", "target": "stratum:ring_2", "relation": "filters_anergy_on", "weight": 0.92},

        # Stratum Bindings
        {"source": "law:requisite_variety", "target": "stratum:ring_0", "relation": "implemented_in"},
        {"source": "concept:vsm_recursion", "target": "stratum:ring_1", "relation": "orchestrated_in"},
        {"source": "concept:double_bind", "target": "stratum:ring_1", "relation": "detected_in"},
        {"source": "concept:sensory_acuity", "target": "stratum:ring_2", "relation": "transduced_in"}
    ]

    graph = {
        "graph_metadata": {
            "title": "C5-REAL Cybernetics Quadrivium Knowledge Topology",
            "version": "1.0",
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "source_corpus_words": ledger["strata_summary"]["total_words"]
        },
        "nodes": nodes,
        "edges": edges
    }

    out_path = "scratch/corpus/cybernetics_quadrivium_graph.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"[✓] Grafo de Conocimiento generado en: {out_path}")
    print(f"    Nodos: {len(nodes)} | Aristas: {len(edges)}")
    return graph

if __name__ == "__main__":
    build_cybernetics_graph()
