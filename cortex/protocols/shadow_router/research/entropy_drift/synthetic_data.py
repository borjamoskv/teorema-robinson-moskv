import uuid
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta


def generate_synthetic_cohort(size: int = 1000) -> List[Dict[str, Any]]:
    records = []
    base_time = datetime.utcnow()
    for i in range(size):
        record_time = base_time + timedelta(minutes=i * 10)
        has_label = random.random() > 0.1
        is_correct = random.random() > 0.2 if has_label else None
        conf = random.uniform(0.6, 0.99)
        record = {
            "timestamp": record_time.isoformat() + "Z",
            "request_id": str(uuid.uuid4()),
            "route_selected": "model-A" if random.random() > 0.3 else "model-B",
            "route_probabilities": {"model-A": 0.8, "model-B": 0.2},
            "predicted_confidence": conf,
            "independent_label_is_correct": is_correct,
            "privacy_eligible": True,
        }
        records.append(record)
    return records
