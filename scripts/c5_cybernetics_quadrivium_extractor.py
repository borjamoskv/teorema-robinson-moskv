#!/usr/bin/env python3
# C5-REAL EXERGY CERTIFIED
"""
C5-REAL Cybernetics Quadrivium Extractor & Topological Synthesizer
Procesa el corpus de los 4 pilares cibernéticos (Ashby, Bateson, Bandler & Grinder, Beer),
extrae las primitivas ontológicas (Sustantivos S, Verbos f), calcula métricas discretas
de entropía de Shannon H(X) y compila el Knowledge Ledger en JSON.
"""

import os
import re
import math
import json
import glob
from collections import Counter
from typing import Dict, List, Any

CORPUS_PATHS = {
    "ashby_1956": {
        "title": "Una introducción a la cibernética / An Introduction to Cybernetics",
        "author": "W. Ross Ashby",
        "year": 1956,
        "publisher": "Chapman & Hall",
        "path": "scratch/corpus/ashby_1956_introduction_to_cybernetics/ashby_1956_introduction_to_cybernetics.txt",
        "domain": "Ring-0 (Physical Limits & Requisite Variety)"
    },
    "bateson_1972": {
        "title": "Pasos hacia una ecología de la mente / Steps to an Ecology of Mind",
        "author": "Gregory Bateson",
        "year": 1972,
        "publisher": "University of Chicago Press",
        "path": "scratch/corpus/bateson_1972_steps_to_an_ecology_of_mind/bateson_1972_steps_to_an_ecology_of_mind.txt",
        "domain": "Ring-1 (Epistemology, Double Bind & Logical Types)"
    },
    "bandler_grinder_1979": {
        "title": "Ranas en príncipes / Frogs into Princes",
        "author": "Richard Bandler & John Grinder",
        "year": 1979,
        "publisher": "Real People Press",
        "path": "scratch/corpus/bandler_grinder_1979_frogs_into_princes/bandler_grinder_1979_frogs_into_princes.txt",
        "domain": "Ring-2 (Somatic Acuity, Reframing & Involuntary Substrate)"
    },
    "beer_1972": {
        "title": "Cerebro de la empresa / Brain of the Firm",
        "author": "Stafford Beer",
        "year": 1972,
        "publisher": "Allen Lane",
        "path": "scratch/corpus/beer_1972_brain_of_the_firm/beer_1972_brain_of_the_firm.txt",
        "domain": "Ring-1 / Ring-0 (Viable System Model & Structural Recursion)"
    }
}

KEYWORD_VECTORS = {
    "ashby_1956": [
        "variety", "requisite variety", "constraint", "transformation", "equilibrium",
        "homeostat", "black box", "stability", "feedback", "determinism",
        "operator", "closed", "entropy", "channel", "capacity"
    ],
    "bateson_1972": [
        "difference", "mind", "context", "double bind", "deutero-learning",
        "schismogenesis", "logical type", "entropy", "information", "cybernetic",
        "ecology", "analogic", "digital", "metalog", "redundancy"
    ],
    "bandler_grinder_1979": [
        "reframing", "sensory", "acuity", "involuntary", "subconscious",
        "anchor", "calibration", "eye movement", "predicate", "reframe",
        "hallucination", "hypnosis", "linguistic", "representation", "feedback"
    ],
    "beer_1972": [
        "viable system", "system 1", "system 2", "system 3", "system 4", "system 5",
        "algedonic", "cybersyn", "variety", "recursion", "attenuation",
        "amplification", "homeostasis", "autonomic", "parasympathetic"
    ]
}

def compute_entropy(text: str) -> float:
    """Calcula la entropía de Shannon sobre la distribución de caracteres (bits/char)."""
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    ent = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return round(ent, 4)

def extract_key_contexts(text: str, keywords: List[str], max_snippets: int = 5) -> List[Dict[str, Any]]:
    """Extrae pasajes paradigmáticos donde confluyen términos clave."""
    snippets = []
    # Dividir en párrafos
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 100]
    
    scored_paragraphs = []
    for p in paragraphs:
        p_clean = " ".join(p.split())
        p_lower = p_clean.lower()
        score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', p_lower))
        if score >= 2:
            scored_paragraphs.append((score, p_clean))
            
    scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
    
    seen = set()
    for score, para in scored_paragraphs[:max_snippets]:
        if para[:80] not in seen:
            seen.add(para[:80])
            snippets.append({
                "keyword_density": score,
                "text_snippet": para[:400] + ("..." if len(para) > 400 else "")
            })
    return snippets

def analyze_corpus():
    results = {
        "metadata": {
            "engine": "C5-REAL Cybernetics Quadrivium Extractor v1.0",
            "standard": "BABYLON-60 Epistemic Synthesis",
            "timestamp": "2026-09-23T01:40:00Z"
        },
        "strata_summary": {
            "total_words": 0,
            "total_bytes": 0,
            "works_analyzed": 4
        },
        "works": {}
    }

    for key, info in CORPUS_PATHS.items():
        path = info["path"]
        if not os.path.exists(path):
            print(f"[!] No existe: {path}")
            continue

        size = os.path.getsize(path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        words = content.split()
        word_count = len(words)
        unique_words = len(set(w.lower() for w in words if w.isalnum()))
        char_entropy = compute_entropy(content)

        # Conteo de términos clave
        keywords = KEYWORD_VECTORS.get(key, [])
        kw_counts = {}
        content_lower = content.lower()
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            kw_counts[kw] = len(re.findall(pattern, content_lower))

        # Pasajes representativos
        key_passages = extract_key_contexts(content, keywords, max_snippets=4)

        results["strata_summary"]["total_words"] += word_count
        results["strata_summary"]["total_bytes"] += size

        results["works"][key] = {
            "title": info["title"],
            "author": info["author"],
            "year": info["year"],
            "publisher": info["publisher"],
            "domain": info["domain"],
            "metrics": {
                "file_size_bytes": size,
                "word_count": word_count,
                "unique_words": unique_words,
                "type_token_ratio": round(unique_words / max(1, word_count), 4),
                "shannon_entropy_bits_per_char": char_entropy
            },
            "top_cybernetic_invariants": kw_counts,
            "paradigmatic_passages": key_passages
        }

    out_ledger = "scratch/corpus/cybernetics_quadrivium_knowledge_ledger.json"
    os.makedirs(os.path.dirname(out_ledger), exist_ok=True)
    with open(out_ledger, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[✓] Knowledge Ledger generado exitosamente en: {out_ledger}")
    print(f"    Total Palabras: {results['strata_summary']['total_words']:,}")
    print(f"    Total Bytes:    {results['strata_summary']['total_bytes']:,}")
    return results

if __name__ == "__main__":
    analyze_corpus()
