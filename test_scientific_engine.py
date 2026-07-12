import math
import pytest

pytest.importorskip("babylon60", reason="módulo nativo babylon60 no compilado")
from scientific_engine import (
    compute_shannon_entropy,
    compute_fisher_information,
    solve_d_separation,
    compute_kolmogorov_approximation,
)


def test_compute_shannon_entropy() -> None:
    data = ["A", "A", "B", "B"]
    res = compute_shannon_entropy(data)
    assert math.isclose(res["entropy"], 1.0)
    assert res["max_entropy"] == 2.0
    assert math.isclose(res["efficiency"], 0.5)


def test_compute_fisher_information() -> None:
    series = [10.0, 10.0, 10.0]
    res = compute_fisher_information(series)
    assert math.isclose(res["fisher_information"], 0.0)


def test_solve_d_separation() -> None:
    nodes = ["A", "B", "C"]
    edges = [["A", "B"], ["B", "C"]]
    res = solve_d_separation(nodes, edges, "A", "C", ["B"])
    assert res["d_separated"] is True
    res2 = solve_d_separation(nodes, edges, "A", "C", [])
    assert res2["d_separated"] is False


def test_compute_kolmogorov_approximation() -> None:
    data = "A" * 1000
    res = compute_kolmogorov_approximation(data)
    assert res["compressed_size"] < res["raw_size"]
    assert res["mdl"] < 1.0
