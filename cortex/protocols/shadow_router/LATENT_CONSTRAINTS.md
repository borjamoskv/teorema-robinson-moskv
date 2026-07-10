# Shadow Router / Proof-of-Route: Parámetros Latentes

En un **Shadow Router / Proof-of-Route**, los parámetros latentes más restrictivos no son necesariamente pesos internos del LLM: son variables no observadas que pueden cambiar la decisión, la latencia, la evaluación o el outcome.

- **Parámetro latente global**: cambia lentamente o define un sistema, por ejemplo el sesgo del evaluator.
- **Estado latente por request o tiempo**: cambia por prompt, proveedor o instante, por ejemplo cola del proveedor o intención real del usuario.

Formalmente, puedes observar:
`O_i = { X_i, A_i, TTFT_i, C_i, \hat Q_i, \text{logs} }`

Pero hay estados no observados:
`\Lambda_i = { Z_i, S_t, E_t, Y_i(m), M_i, H_i }`

---

## Matriz de Restricciones Latentes (Ontología C5-REAL)

```yaml
- id: LC-01
  symbol: Z_i^{task}
  class: causal_latent_variable
  description: Intención real, dificultad, ambigüedad y requisitos implícitos del prompt.
  observed_proxy: [ prompt_length, syntax_complexity, extracted_domain ]
  prohibited_claims:
    - "No puedes inferir que un modelo causó mejor calidad si el router asignó prompts difíciles a modelos fuertes."
  mitigation:
    - estratificar por dominio y dificultad
    - registrar embeddings, features y segmento
    - usar shadows
    - aleatorizar una fracción de tráfico elegible

- id: LC-02
  symbol: Y_i(m)
  class: counterfactual_outcome
  description: Outcome potencial del request i si hubiera usado la ruta m.
  observed_proxy: [ shadow_evaluator_score, unit_test_result ]
  prohibited_claims:
    - "Shadow routing estima automáticamente ATE (Average Treatment Effect) de usuario."
  mitigation:
    - shadows para utilidad proxy
    - A/B user-facing aleatorizado para outcomes humanos
    - propensiones para evaluación off-policy

- id: LC-03
  symbol: Q_i^\star
  class: ultimate_quality
  description: Calidad o corrección real de una respuesta.
  observed_proxy: [ llm_judge_score, heuristics_match ]
  prohibited_claims:
    - "El score del evaluator equivale a verdad, utilidad o satisfacción humana."
  mitigation:
    - ground truth verification
    - labels humanos ciegos

- id: LC-04
  symbol: E_t
  class: evaluator_state
  description: Estado de calibración, sesgo y drift del evaluator en el tiempo.
  observed_proxy: [ ECE, Brier_Score, drift_metrics ]
  prohibited_claims:
    - "El evaluator conserva su validez sin labels independientes y auditoría temporal."
  mitigation:
    - auditoría temporal
    - labels independientes
    - medir ECE y acuerdo humano

- id: LC-05
  symbol: S_{p,t}
  class: provider_internal_state
  description: Estado interno del proveedor (cola, batching, caché, scheduler, placement, rate limits).
  observed_proxy: [ client_observed_ttft_ms, e2e_latency_ms ]
  prohibited_claims:
    - "TTFT identifica energía."
    - "TTFT identifica FLOPs o MCTS."
    - "TTFT identifica profundidad de razonamiento."
  mitigation:
    - provider_attested_telemetry
    - temporal_controls

- id: LC-06
  symbol: V_{p,t}
  class: model_version_state
  description: Versión real de modelo, deployment, endpoint y configuración oculta del proveedor.
  observed_proxy: [ model_alias_string ]
  prohibited_claims:
    - "Un alias comercial prueba qué modelo exacto respondió."
  mitigation:
    - versión resuelta
    - receipt atestado firmado

- id: LC-07
  symbol: \pi_t
  class: routing_policy
  description: Política de routing efectiva, exploración, fallbacks y reglas de elegibilidad.
  observed_proxy: [ logged_policy_id, fallback_triggers ]
  prohibited_claims:
    - "Evaluación off-policy es defendible sin registrar la política completa."
  mitigation:
    - registrar la política completa en logs inmutables

- id: LC-08
  symbol: q_{i,b}
  class: inclusion_propensity
  description: Probabilidad de incluir la ruta sombra b para el request i.
  observed_proxy: [ logged_inclusion_probability ]
  prohibited_claims:
    - "Ponderar datos de shadow es posible asumiendo inclusión uniforme sin propensión."
  mitigation:
    - registrar propensiones completas y métodos de selección

- id: LC-09
  symbol: M_i
  class: missingness_mechanism
  description: Mecanismo de missingness (timeout, error, judge failure, falta de label).
  observed_proxy: [ timeout_flags, error_codes, judge_failures ]
  prohibited_claims:
    - "Eliminar fallos de la muestra no sesga la evaluación."
    - "Missingness equivale a calidad cero o perfecta sin declararlo."
  mitigation:
    - modelar P(M_i=1 | X_i, Q_i^\star)
    - registrar reason of missingness

- id: LC-10
  symbol: D_t
  class: distribution_drift
  description: Drift de distribución de prompts, regiones, dominios y carga.
  observed_proxy: [ prompt_entropy, traffic_mix_ratios ]
  prohibited_claims:
    - "Un cambio en entropía de routing es puramente degradación del evaluator."
  mitigation:
    - aislar traffic mix de degradación del modelo

- id: LC-11
  symbol: H_i
  class: user_heterogeneity
  description: Preferencias y heterogeneidad real de usuarios.
  observed_proxy: [ CSAT_proxy, implicit_feedback ]
  prohibited_claims:
    - "La calidad proxy identifica conversión, churn o resolución de tarea real."
  mitigation:
    - A/B test a nivel de usuario

- id: LC-12
  symbol: I_i
  class: request_interference
  description: Interferencia entre requests, conversaciones, caché, cuotas y estado compartido (SUTVA violations).
  observed_proxy: [ concurrent_requests_count, cache_hit_rates ]
  prohibited_claims:
    - "Los resultados de las request son estrictamente independientes (SUTVA) bajo alta carga."
  mitigation:
    - aislamiento de tenants
    - control de concurrencia

- id: LC-13
  symbol: \omega_i
  class: decoding_randomness
  description: Aleatoriedad de decoding, seed, temperatura y razonamiento interno.
  observed_proxy: [ generated_tokens, temperature_setting ]
  prohibited_claims:
    - "Una sola ejecución caracteriza la calidad media de una ruta estocástica."
  mitigation:
    - pass@k
    - multi-sample evaluation

- id: LC-14
  symbol: C_i^{privacy}
  class: privacy_sensitivity
  description: Sensibilidad real del contenido y error del clasificador de privacidad.
  observed_proxy: [ privacy_classifier_score, PII_flags ]
  prohibited_claims:
    - "La cohorte elegible para shadows representa a toda la población (sesgo por exclusión sensible)."
  mitigation:
    - auditoría de falsos positivos en clasificadores PII

- id: LC-15
  symbol: P_{p,t}
  class: hardware_power
  description: Potencia, hardware físico y eficiencia energética del proveedor.
  observed_proxy: [ cost_usd, ttft_ms ]
  prohibited_claims:
    - "Puedes deducir consumo energético o carbono a partir del TTFT o coste monetario."
  mitigation:
    - telemetría de hw bare-metal o atestación energética
```

---

## Restricciones de Inferencia Fundamentales

| Afirmación Fuerte | Condición Obligatoria de Aserción |
|---|---|
| “El modelo A es mejor que B” | Se define el outcome, se controla selección y se evalúa por segmento. |
| “El router redujo latencia” | Se mide TTFT/latencia bajo contexto comparable y con percentiles agregados. |
| “El router ahorró energía” | Existe telemetría energética o un proxy validado externamente. |
| “La ruta A causó más satisfacción” | Hay experimento user-facing o identificación causal defendible. |
| “El evaluator está calibrado” | Produce probabilidades y se valida contra labels independientes. |
| “La entropía predice drift” | Demuestra mejora predictiva fuera de muestra frente a baselines. |
| “El proveedor ejecutó modelo X” | Hay versión resuelta o receipt firmado del proveedor. |
| “No hubo fuga de datos” | Egress gate, logs, clasificación, allowlists y auditoría verificable lo respaldan. |

**Invariantes Epistémicos (C5-REAL):**
`[INV_EPISTEMIC_01]` Latente no observado => claim limitado.
`[INV_EPISTEMIC_02]` Proxy observado != variable latente identificada.
`[INV_EPISTEMIC_03]` Afirmación fuerte => instrumentación, supuestos y evidencia proporcionalmente fuertes.
