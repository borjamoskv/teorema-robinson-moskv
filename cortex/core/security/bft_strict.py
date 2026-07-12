# bft_strict.py | Nivel de Realidad: #C5-REAL | Mitigación: P1 (BFT Denial / firmas validadas fraudulentamente)
# Stub atómico físico: quórum BFT estricto sobre deltas de estado deterministas.
# Regla estricta: UNA firma inválida o nodo duplicado/desconocido → rechazo de la ronda completa.
# Quórum: 2f+1 con f = (n-1)//3. HMAC-SHA256 con claves de kms_local. Sin mocks.
import hashlib
import hmac
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Vote:
    node_id: str
    digest: str  # sha256 hex del delta de estado propuesto
    sig: str     # HMAC-SHA256(key[node_id], digest) hex


def sign(key: bytes, digest: str) -> str:
    return hmac.new(key, digest.encode("ascii"), hashlib.sha256).hexdigest()


def verify_quorum(votes: list, keys: dict) -> dict:
    """Veredicto determinista. keys: {node_id: bytes}. Devuelve dict falsable."""
    n = len(keys)
    if n < 4:
        return {"ok": False, "reason": f"n={n} < 4: BFT imposible (f=0 sin redundancia)"}
    f = (n - 1) // 3
    quorum = 2 * f + 1

    seen = set()
    for v in votes:
        if v.node_id in seen:
            return {"ok": False, "reason": f"voto duplicado: {v.node_id}"}
        seen.add(v.node_id)
        key = keys.get(v.node_id)
        if key is None:
            return {"ok": False, "reason": f"nodo desconocido: {v.node_id}"}
        if not hmac.compare_digest(sign(key, v.digest), v.sig):
            # Estricto: no se descarta el voto — se aborta la ronda (firma forjada = ataque)
            return {"ok": False, "reason": f"firma inválida: {v.node_id} — ronda abortada"}

    tally: dict = {}
    for v in votes:
        tally[v.digest] = tally.get(v.digest, 0) + 1
    if not tally:
        return {"ok": False, "reason": "sin votos"}
    digest, count = max(tally.items(), key=lambda kv: kv[1])
    if count >= quorum:
        return {"ok": True, "digest": digest, "votes": count, "quorum": quorum, "f": f}
    return {"ok": False, "reason": f"sin quórum: {count}/{quorum}", "f": f}


def _selftest() -> int:
    import secrets
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        os.environ["CORTEX_KMS_DIR"] = os.path.join(td, "kms")
        import kms_local

        nodes = ["n0", "n1", "n2", "n3"]  # n=4, f=1, quórum=3
        keys = {}
        for nid in nodes:
            kms_local.store_key(nid, secrets.token_bytes(32))
            keys[nid] = kms_local.load_key(nid)

        delta = hashlib.sha256(b"delta-de-estado-determinista").hexdigest()

        # 1) Consenso legítimo: 3/4 firman el mismo delta
        votes = [Vote(nid, delta, sign(keys[nid], delta)) for nid in nodes[:3]]
        r = verify_quorum(votes, keys)
        assert r["ok"] and r["votes"] == 3 and r["quorum"] == 3, r

        # 2) Firma forjada → rechazo total de la ronda (aunque haya quórum aparente)
        forged = [Vote("n0", delta, sign(keys["n0"], delta)),
                  Vote("n1", delta, sign(keys["n1"], delta)),
                  Vote("n2", delta, "f" * 64)]
        r = verify_quorum(forged, keys)
        assert not r["ok"] and "firma inválida" in r["reason"], r

        # 3) Split 2/2 → sin quórum
        other = hashlib.sha256(b"delta-divergente").hexdigest()
        split = [Vote("n0", delta, sign(keys["n0"], delta)),
                 Vote("n1", delta, sign(keys["n1"], delta)),
                 Vote("n2", other, sign(keys["n2"], other)),
                 Vote("n3", other, sign(keys["n3"], other))]
        r = verify_quorum(split, keys)
        assert not r["ok"] and "sin quórum" in r["reason"], r

        # 4) Voto duplicado → rechazo
        dup = [Vote("n0", delta, sign(keys["n0"], delta))] * 2
        assert not verify_quorum(dup, keys)["ok"]

        print("[C5-REAL] bft_strict: SELFTEST OK (quórum 2f+1, rechazo estricto)")
        return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(_selftest())
