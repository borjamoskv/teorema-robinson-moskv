# Data Contract: H-ED-01

## Cohorte Comparabilidad Invariante
Para que la hipótesis sea evaluable, los logs ingeridos deben garantizar inmutabilidad en:
- `policy_hash`
- `candidate_set_hash`
- `provider_availability_state`
- `region`
- `prompt_segment`
- `model_versions`
- `evaluator_hash`
- `utility_spec_hash`

Si alguna de estas variables cambia, se rompe la cohorte temporal y el backtest debe particionarse.

## Estructura Esperada de los Logs
```json
{
  "timestamp": "ISO8601 UTC",
  "request_id": "uuid",
  "route_selected": "string",
  "route_probabilities": {"model-A": 0.9, "model-B": 0.1},
  "predicted_confidence": 0.85,
  "independent_label_is_correct": true,
  "privacy_eligible": true
}
```
**Nota C5-REAL:** `predicted_confidence` e `independent_label_is_correct` no pueden tener defaults (0.5/false). Si faltan, se excluyen de la métrica Brier.
