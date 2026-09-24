#!/usr/bin/env python3
# C5-REAL EXERGY CERTIFIED
"""
C5-REAL Cybernetics Knowledge Kernel Runner (Omega 5 - Omega 10)
Carga la topología dinámica del Quadrivium Cibernético en el KnowledgeKernelEngine.
Ejecuta:
- Omega 3: SCITT Event Sourcing Ledger con firmas SHA3-256
- Omega 5: Memoria Fractal de 7 Niveles (Raw a Prediction Graph)
- Omega 6: Motor de Hipótesis Abductivas (Convergencia latente)
- Omega 7: Detección de Desplazamiento e Innovación Paradigmática
- Omega 8: Pirámide de Compresión de Kolmogorov
- Omega 9: Simulación Contrafactual sobre la Red de Dependencias
- Omega 10: Grafo Causal con Atestación Criptográfica
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

# Resolución dinámica de estratos numerados
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "03_state" / "scitt_ledger" / "scitt_python" / "engines"))
sys.path.insert(0, str(REPO_ROOT / "src" / "04_primitives"))

from knowledge_kernel_engine import KnowledgeKernelEngine, CompressionPyramid  # noqa: E402

# Vector canónico de 8 dimensiones para los invariantes cibernéticos:
# [0: variedad, 1: homeostasis, 2: caja_negra, 3: doble_vinculo, 4: tipos_logicos, 5: vsm_recursivo, 6: algedonico, 7: coste_falsificacion]
SEMANTIC_PROFILES: Dict[str, List[float]] = {
    "author:ashby": [0.95, 0.90, 0.85, 0.10, 0.20, 0.30, 0.15, 0.25],
    "author:bateson": [0.30, 0.40, 0.35, 0.95, 0.90, 0.25, 0.30, 0.80],
    "author:beer": [0.85, 0.70, 0.50, 0.20, 0.30, 0.98, 0.92, 0.40],
    "author:bandler_grinder": [0.25, 0.35, 0.60, 0.70, 0.75, 0.30, 0.45, 0.98],
    "book:ashby_1956": [0.92, 0.88, 0.82, 0.10, 0.20, 0.30, 0.15, 0.20],
    "book:bateson_1972": [0.30, 0.40, 0.35, 0.92, 0.88, 0.25, 0.30, 0.75],
    "book:beer_1972": [0.82, 0.68, 0.48, 0.20, 0.30, 0.95, 0.90, 0.35],
    "book:bandler_grinder_1979": [0.25, 0.35, 0.58, 0.68, 0.72, 0.30, 0.42, 0.95],
    "law:requisite_variety": [1.00, 0.75, 0.50, 0.10, 0.20, 0.70, 0.40, 0.30],
    "concept:black_box": [0.60, 0.50, 1.00, 0.20, 0.40, 0.30, 0.20, 0.70],
    "concept:homeostasis": [0.80, 1.00, 0.60, 0.15, 0.25, 0.65, 0.50, 0.30],
    "law:difference_makes_difference": [0.40, 0.30, 0.40, 0.80, 0.95, 0.30, 0.35, 0.70],
    "concept:double_bind": [0.20, 0.30, 0.30, 1.00, 0.85, 0.20, 0.30, 0.60],
    "concept:deutero_learning": [0.35, 0.45, 0.40, 0.80, 0.90, 0.40, 0.35, 0.75],
    "concept:vsm_recursion": [0.85, 0.70, 0.40, 0.20, 0.35, 1.00, 0.75, 0.30],
    "concept:algedonic_loop": [0.50, 0.60, 0.30, 0.30, 0.30, 0.75, 1.00, 0.85],
    "law:cost_of_forgery": [0.30, 0.40, 0.65, 0.60, 0.70, 0.35, 0.80, 1.00],
    "concept:sensory_acuity": [0.25, 0.30, 0.70, 0.50, 0.60, 0.30, 0.50, 0.95],
    "concept:reframing": [0.30, 0.40, 0.45, 0.75, 0.85, 0.35, 0.40, 0.70],
    "stratum:ring_0": [0.90, 0.85, 0.70, 0.10, 0.10, 0.80, 0.95, 0.90],
    "stratum:ring_1": [0.80, 0.75, 0.60, 0.70, 0.90, 0.90, 0.70, 0.75],
    "stratum:ring_2": [0.40, 0.50, 0.60, 0.60, 0.65, 0.40, 0.50, 0.95],
}

def normalize_vector(vec: List[float]) -> List[float]:
    mag = math.sqrt(sum(v * v for v in vec))
    if mag == 0.0:
        return [0.0] * len(vec)
    return [round(v / mag, 4) for v in vec]

def populate_kernel_engine(graph_data: Dict[str, Any]) -> KnowledgeKernelEngine:
    engine = KnowledgeKernelEngine()

    # 1. Registrar Nodos y Eventos SCITT
    for node in graph_data.get("nodes", []):
        node_id = node["id"]
        raw_vec = SEMANTIC_PROFILES.get(node_id, [0.125] * 8)
        norm_vec = normalize_vector(raw_vec)
        engine.register_node(
            node_id=node_id,
            node_type=node.get("type", "Concept"),
            embedding=norm_vec,
            metadata=node,
        )
        engine.append_event(
            actor="C5_ORCHESTRATOR",
            action="registers_node",
            object_id=node_id,
            confidence=1.0,
            source="urn:c5:cybernetics_quadrivium_graph",
        )

    # 2. Registrar Aristas y Eventos SCITT
    for edge in graph_data.get("edges", []):
        weight = float(edge.get("weight", 1.0))
        engine.add_edge(
            source=edge["source"],
            target=edge["target"],
            relation=edge["relation"],
            confidence=weight,
        )
        engine.append_event(
            actor="C5_ORCHESTRATOR",
            action="binds_relation",
            object_id=f"{edge['source']}->{edge['target']}",
            confidence=weight,
            source="urn:c5:cybernetics_quadrivium_graph",
        )

    # 3. Registrar Causal Claims Formals (Omega 10)
    engine.register_claim(
        proposition="A regulator achieves homeostasis if and only if its variety matches or exceeds disturbance variety: V(R) >= V(D) - V(K).",
        source="urn:c5:ashby_1956:chapter_11",
        evidence=["author:ashby", "book:ashby_1956", "law:requisite_variety", "concept:homeostasis"],
        counter_evidence=[],
    )
    engine.register_claim(
        proposition="Pathology is produced when mutually contradictory injunctions span discrete logical types with closed exit; resolvable only through Change 2.",
        source="urn:c5:bateson_1972:part_3",
        evidence=["author:bateson", "book:bateson_1972", "concept:double_bind", "concept:deutero_learning"],
        counter_evidence=[],
    )
    engine.register_claim(
        proposition="Viable systems maintain homeostatic autopoiesis through 5-tier recursive organization with independent algedonic bypass channels.",
        source="urn:c5:beer_1972:part_2",
        evidence=["author:beer", "book:beer_1972", "concept:vsm_recursion", "concept:algedonic_loop"],
        counter_evidence=[],
    )
    engine.register_claim(
        proposition="Veracity is bounded by involuntary physiological signals with high cost of forgery, purging cheap talk voluntary rhetoric.",
        source="urn:c5:bandler_grinder_1979:chapter_2",
        evidence=["author:bandler_grinder", "book:bandler_grinder_1979", "law:cost_of_forgery", "concept:sensory_acuity"],
        counter_evidence=[],
    )

    return engine

def run_synthesis() -> Dict[str, Any]:
    graph_path = REPO_ROOT / "scratch" / "corpus" / "cybernetics_quadrivium_graph.json"
    if not graph_path.exists():
        raise FileNotFoundError(f"Grafo no encontrado en {graph_path}")

    with open(graph_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    engine = populate_kernel_engine(graph_data)

    # 1. Topological Centrality (PageRank)
    pagerank_scores = engine.compute_pagerank()
    sorted_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)

    # 2. Omega 6 Abductive Hypotheses
    hypotheses = engine.generate_hypotheses()

    # 3. Omega 7 Innovation Shift Detection (1956 Ashby vs 1979 Bandler-Grinder)
    ashby_emb = engine._nodes["book:ashby_1956"].embedding
    bg_emb = engine._nodes["book:bandler_grinder_1979"].embedding
    shift_audit = engine.detect_innovation_shift(ashby_emb, bg_emb, threshold=0.30)

    # 4. Omega 9 Counterfactual Simulations
    sim_vsm_severed = engine.simulate_counterfactual(
        target_node_id="concept:vsm_recursion",
        perturbation={"operation": "sever_system_5_policy", "algedonic_active": False},
    )
    sim_variety_collapse = engine.simulate_counterfactual(
        target_node_id="law:requisite_variety",
        perturbation={"operation": "variety_deficit", "entropy_leak": 8.0},
    )

    # 5. Omega 5 Fractal Memory Hierarchy (Tiers 1 to 7)
    core_nodes = ["law:requisite_variety", "concept:double_bind", "concept:vsm_recursion", "law:cost_of_forgery"]
    fractal_hierarchies = {nid: engine.get_fractal_memory_hierarchy(nid) for nid in core_nodes}

    # 6. Omega 8 Kolmogorov Compression Pyramid
    total_words = 550009
    compression_pyramid = CompressionPyramid.compute_exergy_density(total_words)

    # Compilar Reporte de Síntesis
    synthesis_report = {
        "reality_level": "C5-REAL",
        "quadrivium_metadata": graph_data.get("graph_metadata", {}),
        "kernel_telemetry": engine.export_telemetry(),
        "topological_centrality_top5": sorted_pagerank[:5],
        "abductive_hypotheses_count": len(hypotheses),
        "abductive_hypotheses": hypotheses,
        "innovation_shift_audit": shift_audit,
        "counterfactual_simulations": {
            "vsm_recursion_severance": sim_vsm_severed,
            "variety_collapse": sim_variety_collapse,
        },
        "compression_pyramid": compression_pyramid,
        "fractal_memory_hierarchies": fractal_hierarchies,
    }

    out_path = REPO_ROOT / "scratch" / "corpus" / "cybernetics_quadrivium_fractal_memory.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(synthesis_report, f, indent=2, ensure_ascii=False)

    return synthesis_report

def main() -> None:
    print("============================================================")
    print(" 🧠 C5-REAL KNOWLEDGE KERNEL RUNNER: CYBERNETICS QUADRIVIUM")
    print("============================================================")
    report = run_synthesis()
    print(f"[+] Nodos Cargados: {report['kernel_telemetry']['nodes_count']}")
    print(f"[+] Aristas Cargadas: {report['kernel_telemetry']['edges_count']}")
    print(f"[+] Eventos SCITT Atómicos: {report['kernel_telemetry']['events_count']}")
    print(f"[+] Causal Claims Registrados: {report['kernel_telemetry']['claims_count']}")
    print(f"[+] Hipótesis Abductivas Descubiertas: {report['abductive_hypotheses_count']}")
    print(f"[+] Desplazamiento de Innovación (1956 -> 1979): {report['innovation_shift_audit']['displacement']:.4f} ({report['innovation_shift_audit']['signal']})")
    print("\n[+] Topología Central (Top 3 PageRank):")
    for nid, score in report["topological_centrality_top5"][:3]:
        print(f"    - {nid}: {score:.4f}")
    print("\n[✓] SÍNTESIS DE MEMORIA FRACTAL EXPORTADA EXITOSAMENTE.")

if __name__ == "__main__":
    main()
