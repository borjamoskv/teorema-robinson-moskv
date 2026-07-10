import numpy as np
from typing import List, Optional, Dict, Any

class EvaluatorBrierScore:
    """
    Cálculo de Brier Score con Cero Defaults.
    Sin probabilidad calibrable -> excluido.
    Sin label independiente -> outcome missing (no es 0.0 por defecto).
    """
    
    def __init__(self, min_coverage_threshold: int = 30):
        self.min_coverage = min_coverage_threshold

    def compute_brier(self, records: List[Dict[str, Any]]) -> Optional[float]:
        valid_predictions = []
        valid_labels = []

        for record in records:
            # Validación estricta de existencia y tipo
            if 'predicted_confidence' not in record or record['predicted_confidence'] is None:
                continue
            if 'independent_label_is_correct' not in record or record['independent_label_is_correct'] is None:
                continue

            p = float(record['predicted_confidence'])
            y = 1.0 if record['independent_label_is_correct'] else 0.0
            
            valid_predictions.append(p)
            valid_labels.append(y)

        if len(valid_predictions) < self.min_coverage:
            return None # Brier no estimable por falta de cobertura
            
        preds = np.array(valid_predictions)
        labels = np.array(valid_labels)
        
        brier_score = np.mean((preds - labels) ** 2)
        return float(brier_score)
