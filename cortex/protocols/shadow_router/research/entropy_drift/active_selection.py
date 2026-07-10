import hashlib

def calculate_priority(uncertainty: float, drift: float, impact: float, label_reliability: float, privacy_eligibility: float) -> float:
    """
    Priority(x) = Uncertainty(x) * Drift(x) * Impact(x) * LabelReliability(x) * PrivacyEligibility(x)
    """
    return uncertainty * drift * impact * label_reliability * privacy_eligibility

def active_selection_top_k(samples: list, k: int) -> list:
    """
    Muestreo activo de anomalías para labeling.
    Desempate determinista por hash.
    samples: List[Dict] con 'request_id' y valores para priority.
    """
    scored = []
    for s in samples:
        p = calculate_priority(
            s.get('uncertainty', 0.0),
            s.get('drift', 0.0),
            s.get('impact', 0.0),
            s.get('label_reliability', 0.0),
            s.get('privacy_eligibility', 0.0)
        )
        
        # C5-REAL Deterministic Tie-Breaker
        tie_breaker_hash = int(hashlib.sha256(s['request_id'].encode()).hexdigest()[:8], 16)
        scored.append((p, tie_breaker_hash, s))
        
    # Sort descending by priority, then ascending by hash
    scored.sort(key=lambda x: (-x[0], x[1]))
    
    return [s for _, _, s in scored[:k]]
