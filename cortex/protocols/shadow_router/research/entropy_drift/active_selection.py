import hashlib

def calculate_priority(uncertainty: float, drift: float, impact: float, label_reliability: float, privacy_eligibility: float) -> float:
    return uncertainty * drift * impact * label_reliability * privacy_eligibility

def active_selection_top_k(samples: list, k: int) -> list:
    scored = []
    for s in samples:
        p = calculate_priority(s.get('uncertainty', 0.0), s.get('drift', 0.0), s.get('impact', 0.0), s.get('label_reliability', 0.0), s.get('privacy_eligibility', 0.0))
        tie_breaker_hash = int(hashlib.sha256(s['request_id'].encode()).hexdigest()[:8], 16)
        scored.append((p, tie_breaker_hash, s))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [s for _, _, s in scored[:k]]
