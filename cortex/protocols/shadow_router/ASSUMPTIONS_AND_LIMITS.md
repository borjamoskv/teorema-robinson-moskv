# ASSUMPTIONS AND LIMITS (Shadow Router v0.2 — Evidence-Calibrated)

Esta especificación asume la calibración basada en la evidencia (Evidence-Calibrated) para mitigar la falsa ortogonalidad y la pseudo-física. A continuación, se definen los supuestos y límites de la evaluación causal.

## Supuestos Causales (Assumptions)

1. **Ignorability given propensity (Unconfoundedness):**
   Asumimos que la asignación al shadow router depende únicamente de las variables observadas en el `DecisionReceipt` y capturadas en el Propensity Score. No existen confusores ocultos que alteren simultáneamente la probabilidad de ser enviado al shadow y el resultado de la evaluación proxy.
2. **Overlap (Positivity):**
   Para estimar el ATE (Average Treatment Effect) mediante Inverse Propensity Scoring, la probabilidad de ser enrutado al shadow debe estar acotada entre $0 < P(X) < 1$. Todo requerimiento debe tener probabilidad no nula de ser evaluado por ambos modelos.
3. **SUTVA (Stable Unit Treatment Value Assumption):**
   La evaluación de un request no interfiere causalmente con el outcome de otro request (No Interference). Además, no existen múltiples versiones ocultas del tratamiento (los alias de modelo son estables durante el periodo de evaluación).

## Limitaciones (Limits)

- **Proxy Regret vs. Causal Regret:** El resultado de `estimate_ate_shadow` cuantifica el **Proxy Regret** (evaluación sistémica) frente al evaluador, no el impacto final sobre el usuario (CSAT, retención, resolución de negocio). Para inferir causalidad sobre el usuario final, se requiere A/B testing directo.
- **Intervalos de Confianza (Bootstrap):** La validez del IC al 95% derivado del cluster bootstrap depende del tamaño muestral $N$. Con muestras reducidas, el IC subestimará el error.
- **Gobernanza Git:** La confianza depositada en la ontología se apoya en firmas criptográficas (GPG/SSH Tags) y auditoría remota. Si la clave de firma es comprometida, la atestación pierde validez (Single Point of Failure).
