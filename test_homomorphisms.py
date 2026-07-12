import sqlite3
import os
import re

DB_PATH = os.path.expanduser("~/.babylon60/cortex_memory.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "cortex_memory.db")
    )


def parse_td(s) -> "Any":
    m = re.match("T(\\d+)\\.D(\\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def test_assert_cyclic_dimensional_homomorphism_invariant() -> None:
    assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT source, target, type FROM L2_isomorphism_edges WHERE type = 'Dimensional'"
    )
    edges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    assert len(edges) == 36, f"Expected 36 Dimensional edges, found {len(edges)}."
    for e in edges:
        src = e["source"]
        tgt = e["target"]
        src_parsed = parse_td(src)
        tgt_parsed = parse_td(tgt)
        assert src_parsed is not None, f"Failed to parse source: {src}"
        assert tgt_parsed is not None, f"Failed to parse target: {tgt}"
        t_src, d_src = src_parsed
        t_tgt, d_tgt = tgt_parsed
        expected_t = (t_src + 3) % 9
        if expected_t == 0:
            expected_t = 9
        assert t_tgt == expected_t, (
            f"Theory shift mismatch: {src} -> {tgt} (Expected T={expected_t}, got T={t_tgt})"
        )
        expected_d = (d_src + 2) % 8
        if expected_d == 0:
            expected_d = 8
        assert d_tgt == expected_d, (
            f"Dimension shift mismatch: {src} -> {tgt} (Expected D={expected_d}, got D={d_tgt})"
        )


def test_assert_local_primitive_nodes_bijections() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, theory, dimension, name FROM L1_primitive_nodes")
    nodes = [dict(row) for row in cursor.fetchall()]
    cursor.execute(
        "SELECT source, target FROM L2_isomorphism_edges WHERE type = 'Dimensional'"
    )
    dim_edges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    td_nodes = {}
    for n in nodes:
        nid = n["id"]
        if "." in nid:
            parts = nid.split(".")
            if len(parts) >= 2:
                key = f"{parts[0]}.{parts[1]}"
                if key not in td_nodes:
                    td_nodes[key] = []
                td_nodes[key].append(n)
    for edge in dim_edges:
        src = edge["source"]
        tgt = edge["target"]
        src_list = td_nodes.get(src, [])
        tgt_list = td_nodes.get(tgt, [])
        assert len(src_list) == 10, (
            f"Source group {src} has {len(src_list)} nodes instead of 10."
        )
        assert len(tgt_list) == 10, (
            f"Target group {tgt} has {len(tgt_list)} nodes instead of 10."
        )


if __name__ == "__main__":
    print("--- Executing Homomorphism Invariant Tests ---")
    test_assert_cyclic_dimensional_homomorphism_invariant()
    print("  [PASSED] test_assert_cyclic_dimensional_homomorphism_invariant")
    test_assert_local_primitive_nodes_bijections()
    print("  [PASSED] test_assert_local_primitive_nodes_bijections")
    print("ALL HOMOMORPHISM TESTS PASSED SUCCESSFULLY (C5-REAL).")
