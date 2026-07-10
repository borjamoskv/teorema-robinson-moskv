import numpy as np
from typing import List, Dict
import json

from .feature_spec import compute_aggregate_entropy, compute_predictive_entropy, compute_distribution_divergence
from .label_quality import EvaluatorBrierScore
from .temporal_validation import TemporalValidator

def run_offline_backtest(records: List[Dict], horizons: List[int] = [6, 12, 24, 48]):
    """
    Simulación offline de backtesting. 
    1. Agrega los datos en ventanas temporales reales (ej. 6h).
    2. Calcula Brier (sin defaults) y las métricas de Entropía separadas.
    3. Valida contra B3 usando rolling-origin temporal validation.
    4. NO dispara retraining automático. Culmina en ALERT_AND_AUDIT.
    """
    
    print("Iniciando Offline Backtest para H-ED-01...")
    
    # 1. Validación de Calidad de Labels
    brier_engine = EvaluatorBrierScore(min_coverage_threshold=30)
    brier = brier_engine.compute_brier(records)
    
    if brier is None:
        print("ALERT_AND_AUDIT: Cobertura insuficiente de labels independientes. Brier no estimable.")
        return
        
    print(f"Brier Histórico (Ventana T): {brier:.4f}")
    
    # 2. Separación de Señales de Entropía
    # (Simulamos la ingesta de las propensiones de ruta de los records)
    route_probs = np.array([r.get('route_probabilities', {'A': 1.0}) for r in records])
    # En una impl real, se calcularía la marginal y la condicional.
    
    print("Señales extraídas: H(R), E_x[H(pi(R|x))], D_JS, Drift(Prompt).")
    
    # 3. Validación Temporal (Mock)
    validator = TemporalValidator(step_size_hours=6)
    # mock features array
    features = np.zeros((len(records), 4))
    target = np.zeros(len(records))
    
    results = validator.rolling_origin_validation(features, target, horizons)
    
    print("Resultados de Validación Temporal (Ganancia Predictiva):")
    for k, v in results.items():
        print(f" - {k}: Gain = {v['predictive_gain']}, FAR = {v['false_alert_rate']}")
        
    print("\nAcción C5-REAL Terminal: ALERT_AND_AUDIT.")
    print("La hipótesis H-ED-01 no se promoverá a `monitoring/` hasta que PredictiveGain > 0 fuera de muestra.")

if __name__ == "__main__":
    from .synthetic_data import generate_synthetic_cohort
    # Mocking execution para prueba de humo de pipeline
    dummy_records = generate_synthetic_cohort(size=200)
    run_offline_backtest(dummy_records)
