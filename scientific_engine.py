# CORTEX Scientific Engine
# Author: Borja Moskv
# Reality Level: C5-REAL
# Description: Native scientific calculations for Shannon Entropy, Fisher Information, d-separation DAG solving, and Kolmogorov MDL.

import sys
import json
import math
import zlib
from collections import Counter
from decimal import Decimal

__all__ = [
    "compute_shannon_entropy",
    "compute_fisher_information",
    "solve_d_separation",
    "compute_kolmogorov_approximation",
    "compute_asymmetric_trust_isomorphism",
]


def compute_shannon_entropy(data: list | str) -> dict:
    """
    Computes Shannon Entropy of a list of items or string.
    H(X) = -sum(P(x) * log2(P(x)))
    """
    if not data:
        return {
            "entropy": Decimal("0.0"),
            "max_entropy": Decimal("0.0"),
            "efficiency": Decimal("1.0"),
        }

    # If input is a list of numbers or objects, count frequencies.
    # If string, count char frequencies.
    total = len(data)
    counts = Counter(data)

    entropy = Decimal("0.0")
    terms = []
    for count in counts.values():
        p = Decimal(count) / Decimal(total)
        terms.append(-p * Decimal(str(math.log2(float(p)))))

    entropy = sum(terms, Decimal("0.0"))

    return {
        "entropy": entropy,
        "max_entropy": Decimal(str(math.log2(total))) if total > 1 else Decimal("0.0"),
        "efficiency": (entropy / Decimal(str(math.log2(total))))
        if total > 1 and entropy > Decimal("0.0")
        else Decimal("1.0"),
    }


def compute_fisher_information(time_series: list[Decimal]) -> dict:
    """
    Computes Fisher Information metric for a time-series vector.
    For a sequence of values v_t, we compute:
    I_F = sum( ((v_{t+1} - v_t) / dt)^2 / v_t )
    """
    if not time_series or len(time_series) < 2:
        return {"fisher_information": Decimal("0.0"), "status": "insufficient_data"}

    # Filter out zero or negative values to prevent domain error and division by zero
    epsilon = Decimal("1e-10")
    series = [Decimal(str(v)) if Decimal(str(v)) > epsilon else epsilon for v in time_series]

    fisher_sum = Decimal("0.0")
    terms = []
    for i in range(len(series) - 1):
        diff = series[i + 1] - series[i]
        terms.append((diff**2) / series[i])

    fisher_sum = sum(terms, Decimal("0.0"))
    
    # O(N) single-pass variance calculation
    n = Decimal(len(series))
    mean = sum(series, Decimal("0.0")) / n
    variance = sum(((x - mean) ** 2 for x in series), Decimal("0.0")) / n

    return {
        "fisher_information": fisher_sum,
        "mean": mean,
        "variance": variance,
    }


def solve_d_separation(
    nodes: list[str], edges: list[list[str]], x_node: str, y_node: str, z_set: list[str]
) -> dict:
    """
    Determines if x_node and y_node are d-separated given z_set in a DAG.
    nodes: list of node names
    edges: list of [source, target] pairs
    x_node: start node string
    y_node: end node string
    z_set: list of conditioning node strings
    """
    # 1. Build adjacency list representation of DAG
    adj_out = {n: set() for n in nodes}
    adj_in = {n: set() for n in nodes}
    for u, v in edges:
        if u in adj_out:
            adj_out[u].add(v)
        if v in adj_in:
            adj_in[v].add(u)

    z_set = set(z_set)
    
    # 2. Strict DAG Validation (Cycle Detection via DFS)
    visited = set()
    rec_stack = set()
    
    def is_cyclic(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in adj_out.get(node, []):
            if neighbor not in visited:
                if is_cyclic(neighbor): return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    for node in nodes:
        if node not in visited:
            if is_cyclic(node):
                # [L12] K1 FAIL-FAST: Cycles injected.
                print(f"\033[1;31m[CORTEX APOPTOSIS]\033[0m Cyclic Topology Detected. D-Separation requires a strict DAG.", file=sys.stderr)
                sys.exit(1)

    # 3. Bayes-Ball / Active Trail DFS Algorithm O(V+E)
    # Track states as (node, direction) where direction is 'up' (from child) or 'down' (from parent).
    # Initially we start at x_node going 'up' (as if from a child).
    
    # Ancestors of Z
    anc_z = set(z_set)
    queue = list(z_set)
    while queue:
        curr = queue.pop(0)
        for parent in adj_in.get(curr, []):
            if parent not in anc_z:
                anc_z.add(parent)
                queue.append(parent)
                
    visited_states = set()
    queue = [(x_node, 'up')]
    
    reachable = set()
    
    while queue:
        curr, direction = queue.pop(0)
        
        if (curr, direction) in visited_states:
            continue
        visited_states.add((curr, direction))
        
        if curr not in z_set:
            reachable.add(curr)
            
        if direction == 'up' and curr not in z_set:
            for parent in adj_in.get(curr, []):
                queue.append((parent, 'up'))
            for child in adj_out.get(curr, []):
                queue.append((child, 'down'))
        elif direction == 'down':
            if curr not in z_set:
                for child in adj_out.get(curr, []):
                    queue.append((child, 'down'))
            if curr in anc_z:
                for parent in adj_in.get(curr, []):
                    queue.append((parent, 'up'))

    d_separated = y_node not in reachable

    return {
        "d_separated": d_separated,
        "active_paths": [], # Removed O(V!) path generation
        "total_paths": 0,
        "conditioning_set": list(z_set),
    }


def compute_kolmogorov_approximation(text_data: str) -> dict:
    """
    Approximates Kolmogorov Complexity using zlib compression ratio.
    K(s) = len(compress(s)) / len(s)
    """
    if not text_data:
        return {"mdl": Decimal("0.0"), "compressed_size": 0, "raw_size": 0}

    raw_bytes = text_data.encode("utf-8")
    raw_size = len(raw_bytes)

    compressed = zlib.compress(raw_bytes, level=9)
    compressed_size = len(compressed)

    mdl = Decimal(compressed_size) / Decimal(raw_size) if raw_size > 0 else Decimal("0.0")

    return {
        "mdl": mdl,
        "compressed_size": compressed_size,
        "raw_size": raw_size,
        "compression_ratio": (Decimal(raw_size) / Decimal(compressed_size))
        if compressed_size > 0
        else Decimal("1.0"),
    }


def compute_asymmetric_trust_isomorphism(provenance_hash, test_passed, entropy_metric):
    """
    [L39] TEOREMA DE LA CONFIANZA ASIMÉTRICA.
    Trust is NOT derived from manual AST review, but from physical execution and cryptographic provenance.
    If test_passed is False, Trust = 0.0 (C4-SIM Anergia).
    If True, Trust approaches 1.0 (C5-REAL) based on execution and lack of stochastic noise (entropy).
    """
    if not provenance_hash or not test_passed:
        return {"trust_index": Decimal("0.0"), "reality_level": "C4-SIM", "anergy": Decimal("1.0")}

    # Isomorphism: Trust scales inversely with entropy (noise).
    # If entropy is 0, trust is max.
    entropy_dec = Decimal(str(entropy_metric))
    trust_index = Decimal(str(math.exp(float(-entropy_dec)))) if entropy_dec >= Decimal("0.0") else Decimal("1.0")

    return {
        "trust_index": trust_index,
        "reality_level": "C5-REAL",
        "anergy": Decimal("1.0") - trust_index,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)

    # [L12] K1 FAIL-FAST: No try/except block for syntax errors. Let the AST crash if payload is invalid.
    payload_raw = sys.stdin.read(10485760) # 10MB Bound limit
    if not payload_raw:
        print(f"\033[1;31m[CORTEX APOPTOSIS]\033[0m Empty STDIN payload. C5-REAL Fail-Fast.", file=sys.stderr)
        sys.exit(1)
        
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj)
            return super(DecimalEncoder, self).default(obj)

    payload = json.loads(payload_raw)

    action = sys.argv[1]

    if action == "entropy":
        data = payload.get("data", "")
        res = compute_shannon_entropy(data)
    elif action == "fisher":
        series = payload.get("series", [])
        res = compute_fisher_information(series)
    elif action == "dsep":
        nodes = payload.get("nodes", [])
        edges = payload.get("edges", [])
        x = payload.get("x", "")
        y = payload.get("y", "")
        z = payload.get("z", [])
        res = solve_d_separation(nodes, edges, x, y, z)
    elif action == "kolmogorov":
        data = payload.get("data", "")
        res = compute_kolmogorov_approximation(data)
    elif action == "epistemic_trust":
        provenance = payload.get("provenance_hash", "")
        test_passed = payload.get("test_passed", False)
        entropy = payload.get("entropy", 1.0)
        res = compute_asymmetric_trust_isomorphism(provenance, test_passed, entropy)
    else:
        print(f"\033[1;31m[CORTEX APOPTOSIS]\033[0m Unknown action: {action}. C5-REAL Fail-Fast.", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(res, indent=2, cls=DecimalEncoder))


if __name__ == "__main__":
    main()
