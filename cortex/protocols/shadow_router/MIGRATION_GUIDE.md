# MIGRATION GUIDE: Shadow Router v0.1 to v0.2-C5

La migración a `v0.2-C5` introduce bloqueos termodinámicos estrictos y erradica el modelo estocástico de routing.

## 1. Abandono de `asyncio.create_task()`
**Motivo:** No es durable.
**Acción:** Inyectar una implementación de `ShadowDispatcher` (RabbitMQ, SQS, Celery) compatible con el `Protocol` de Python.

## 2. Inyección de Causalidad (Do-Calculus)
El Shadow Router ya no evalúa "modelos paralelos" como observador, sino que inyecta una variable instrumental. 
- Todo routing primario es una intervención `do(primary)`.
- El shadow asíncrono es `do(shadow)`.

## 3. Límites Asintóticos (Teorema Λ8)
El `UtilityEstimator` ahora exige validación asintótica. Revisa tu `algorithm_complexity` en la política; si excede `O(N log N)`, la ejecución fallará bajo Fail-Fast.

## 4. Duda Algorítmica (PRM-06)
Si tu estimador de regret y utilidad reporta `confidence_percent < 80%`, el router levantará una excepción obligando a ceder el control al enjambre de investigación.

## 5. Métrica TTFT (Adiós Pseudofísica)
Eliminar referencias a `attention_fatigue`. Sustituir por `mcts_depth` y `branching_factor` dentro de `LatencyMetrics`.
