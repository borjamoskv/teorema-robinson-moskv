# CORTEX Scientific Engine
# Author: Borja Moskv
# Reality Level: C5-REAL
# Description: Native scientific calculations for Shannon Entropy, Fisher Information, d-separation DAG solving, and Kolmogorov MDL.

import sys
import json
import math
import zlib
from collections import Counter

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
            "entropy": 0.0,
            "max_entropy": 0.0,
            "efficiency": 1.0,
        }

    # If input is a list of numbers or objects, count frequencies.
    # If string, count char frequencies.
    total = len(data)
    counts = Counter(data)

    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)

    return {
        "entropy": entropy,
        "max_entropy": math.log2(total) if total > 1 else 0.0,
        "efficiency": (entropy / math.log2(total))
        if total > 1 and entropy > 0
        else 1.0,
    }


def compute_fisher_information(time_series: list[float]) -> dict:
    """
    Computes Fisher Information metric for a time-series vector.
    For a sequence of values v_t, we compute:
    I_F = sum( ((v_{t+1} - v_t) / dt)^2 / v_t )
    """
    if not time_series or len(time_series) < 2:
        return {"fisher_information": 0.0, "status": "insufficient_data"}

    # Filter out zeros or very small values to prevent division by zero
    epsilon = 1e-5
    series = [float(v) if abs(v) > epsilon else epsilon for v in time_series]

    fisher_sum = 0.0
    for i in range(len(series) - 1):
        diff = series[i + 1] - series[i]
        fisher_sum += (diff**2) / series[i]

    return {
        "fisher_information": fisher_sum,
        "mean": sum(series) / len(series),
        "variance": sum((x - (sum(series) / len(series))) ** 2 for x in series)
        / len(series),
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

    # Helper to get all descendants of a node in the DAG
    def get_descendants(node):
        desc = set()
        queue = [node]
        while queue:
            c = queue.pop(0)
            for child in adj_out[c]:
                if child not in desc:
                    desc.add(child)
                    queue.append(child)
        return desc

    # 3. BFS/DFS traversal over the "moral" undirected paths with active-path tracking.
    # An active path from X to Y given Z is a path where:
    # - If we have a collider (A -> B <- C), B or a descendant of B must be in Z.
    # - If we have a non-collider (A -> B -> C or A <- B -> C or A <- B <- C), B must NOT be in Z.

    # To implement this cleanly, we do a search over the configuration space.
    # State: (node, direction_of_entry)
    # direction_of_entry: 'UP' (coming from child, going up to parent) or 'DOWN' (coming from parent, going down to child)

    d_separated = True
    paths_found = []

    # We will run a standard reachability search
    # Let's keep it simple: find all simple paths in the undirected version of the graph
    # and check if any path is active.
    # Since n is usually small in this UI, we can find all simple paths from X to Y.
    undirected_adj = {n: set() for n in nodes}
    for u, v in edges:
        undirected_adj[u].add(v)
        undirected_adj[v].add(u)

    def find_all_paths(start, end, path=None):
        if path is None:
            path = [start]
        if start == end:
            return [path]
        paths = []
        for node in undirected_adj[start]:
            if node not in path:
                paths.extend(find_all_paths(node, end, path + [node]))
        return paths

    all_paths = find_all_paths(x_node, y_node)

    for path in all_paths:
        # Check if the path is active given Z
        is_active = True
        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            nxt = path[i + 1]

            # Determine if 'curr' is a collider on this path
            # Collider means: prev -> curr <- nxt
            is_collider = (curr in adj_out[prev]) and (curr in adj_out[nxt])

            if is_collider:
                # Collider: 'curr' or any descendant of 'curr' must be in Z
                has_descendant_in_z = (curr in z_set) or any(
                    d in z_set for d in get_descendants(curr)
                )
                if not has_descendant_in_z:
                    is_active = False
                    break
            else:
                # Non-collider: 'curr' must NOT be in Z
                if curr in z_set:
                    is_active = False
                    break

        if is_active:
            d_separated = False
            paths_found.append(path)

    return {
        "d_separated": d_separated,
        "active_paths": paths_found,
        "total_paths": len(all_paths),
        "conditioning_set": list(z_set),
    }


def compute_kolmogorov_approximation(text_data: str) -> dict:
    """
    Approximates Kolmogorov Complexity using zlib compression ratio.
    K(s) = len(compress(s)) / len(s)
    """
    if not text_data:
        return {"mdl": 0.0, "compressed_size": 0, "raw_size": 0}

    raw_bytes = text_data.encode("utf-8")
    raw_size = len(raw_bytes)

    compressed = zlib.compress(raw_bytes, level=9)
    compressed_size = len(compressed)

    mdl = compressed_size / raw_size if raw_size > 0 else 0.0

    return {
        "mdl": mdl,
        "compressed_size": compressed_size,
        "raw_size": raw_size,
        "compression_ratio": (raw_size / compressed_size)
        if compressed_size > 0
        else 1.0,
    }


def compute_asymmetric_trust_isomorphism(provenance_hash, test_passed, entropy_metric):
    """
    [L39] TEOREMA DE LA CONFIANZA ASIMÉTRICA.
    Trust is NOT derived from manual AST review, but from physical execution and cryptographic provenance.
    If test_passed is False, Trust = 0.0 (C4-SIM Anergia).
    If True, Trust approaches 1.0 (C5-REAL) based on execution and lack of stochastic noise (entropy).
    """
    if not provenance_hash or not test_passed:
        return {"trust_index": 0.0, "reality_level": "C4-SIM", "anergy": 1.0}

    # Isomorphism: Trust scales inversely with entropy (noise).
    # If entropy is 0, trust is max.
    trust_index = math.exp(-entropy_metric) if entropy_metric >= 0 else 1.0

    return {
        "trust_index": trust_index,
        "reality_level": "C5-REAL",
        "anergy": 1.0 - trust_index,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)

    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}))
        sys.exit(1)

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
        res = {"error": f"Unknown action: {action}"}

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
