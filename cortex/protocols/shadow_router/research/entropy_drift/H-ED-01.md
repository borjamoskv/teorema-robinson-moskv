# H-ED-01 — Entropy/Drift Early Warning

## Hipótesis
Bajo cohortes comparables —misma versión de policy, candidate set, región, modalidad y restricciones de disponibilidad—, la entropía predictiva del router y la divergencia residual de routing, combinadas con drift de distribución de prompts, pueden mejorar la predicción fuera de muestra de degradación futura de calibración del evaluator frente a baselines basados solo en Brier histórico, mezcla de tráfico y disponibilidad de proveedores.

## Criterios de Invarianza
- **NO causalidad directa:** $H_{\text{routing}} \not\Rightarrow \text{drift del evaluator}$. 
- **Validación Estricta:** $\text{PredictiveGain}(H_{\text{policy}}, D_{JS}, D_{\text{prompt}}) > 0$ sobre baseline controlado.
- **Sin automatización de Producción:** Las acciones terminales de este protocolo colapsan en `ALERT_AND_AUDIT`, nunca en un re-entrenamiento automático sin supervisión.
