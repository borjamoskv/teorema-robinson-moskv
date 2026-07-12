import sys
import json
import math
import zlib
from decimal import Decimal
import babylon60

__all__ = [
    "compute_shannon_entropy",
    "compute_fisher_information",
    "solve_d_separation",
    "compute_kolmogorov_approximation",
    "compute_asymmetric_trust_isomorphism",
]


def compute_shannon_entropy(data: list | str) -> dict:
    if isinstance(data, list):
        data = "".join((str(x) for x in data))
    res = babylon60.compute_shannon_entropy(data)
    import json

    d = json.loads(res)
    return {
        "entropy": Decimal(str(d["entropy"])),
        "max_entropy": Decimal(str(d["max_entropy"])),
        "efficiency": Decimal(str(d["efficiency"])),
    }


def compute_fisher_information(time_series: list[Decimal]) -> dict:
    series_f64 = [float(x) for x in time_series]
    res = babylon60.compute_fisher_information(series_f64)
    import json

    d = json.loads(res)
    if d.get("status") == "insufficient_data":
        return {"fisher_information": Decimal("0.0"), "status": "insufficient_data"}
    return {
        "fisher_information": Decimal(str(d["fisher_information"])),
        "mean": Decimal(str(d["mean"])),
        "variance": Decimal(str(d["variance"])),
    }


def solve_d_separation(
    nodes: list[str], edges: list[list[str]], x_node: str, y_node: str, z_set: list[str]
) -> dict:
    res = babylon60.solve_d_separation(nodes, edges, x_node, y_node, z_set)
    import json
    import sys

    d = json.loads(res)
    if "error" in d:
        print(f"\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m {d['error']}", file=sys.stderr)
        sys.exit(1)
    return d


def compute_kolmogorov_approximation(text_data: str) -> dict:
    if not text_data:
        return {"mdl": Decimal("0.0"), "compressed_size": 0, "raw_size": 0}
    raw_bytes = text_data.encode("utf-8")
    raw_size = len(raw_bytes)
    compressed = zlib.compress(raw_bytes, level=9)
    compressed_size = len(compressed)
    mdl = (
        Decimal(compressed_size) / Decimal(raw_size) if raw_size > 0 else Decimal("0.0")
    )
    return {
        "mdl": mdl,
        "compressed_size": compressed_size,
        "raw_size": raw_size,
        "compression_ratio": Decimal(raw_size) / Decimal(compressed_size)
        if compressed_size > 0
        else Decimal("1.0"),
    }


def compute_asymmetric_trust_isomorphism(provenance_hash, test_passed, entropy_metric):
    if not provenance_hash or not test_passed:
        return {
            "trust_index": Decimal("0.0"),
            "reality_level": "C4-SIM",
            "anergy": Decimal("1.0"),
        }
    entropy_dec = Decimal(str(entropy_metric))
    trust_index = (
        Decimal(str(math.exp(float(-entropy_dec))))
        if entropy_dec >= Decimal("0.0")
        else Decimal("1.0")
    )
    return {
        "trust_index": trust_index,
        "reality_level": "C5-REAL",
        "anergy": Decimal("1.0") - trust_index,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)
    payload_raw = sys.stdin.read(10485760)
    if not payload_raw:
        print(
            f"\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m Empty STDIN payload. C5-REAL Fail-Fast.",
            file=sys.stderr,
        )
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
        print(
            f"\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m Unknown action: {action}. C5-REAL Fail-Fast.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(json.dumps(res, indent=2, cls=DecimalEncoder))


if __name__ == "__main__":
    main()
