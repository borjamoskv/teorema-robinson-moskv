# Proof-of-Route: Utility SLA Specification (Artefacto 4)

## 1. Ontología del SLA (Nivel de Servicio)
El SLA no se define por el "uptime del router", sino por la **calidad contrafactual de sus decisiones** ($Regret_{proxy}$). Un enrutador multi-LLM cumple su SLA si y solo si, la utilidad de las rutas primarias elegidas no es estadísticamente inferior a las alternativas descubiertas mediante shadow routing.

## 2. Definición Formal de Utilidad ($U$)

La utilidad observada de una ejecución $e$ se define como una función lineal con penalizaciones estrictas (Basis Points).

\[
U(e) = \lambda_Q Q(e) + \lambda_L L(e) + \lambda_C C(e) - \mathbb{I}_{fail} P_{fail} - \mathbb{I}_{privacy} P_{privacy}
\]

Donde:
*   $Q(e) \in [0, 10000]$: Calidad observada por el juez (Basis Points).
*   $L(e) = \max(0, 10000 - \frac{\text{ttft\_ms}}{10})$: Transformación lineal de latencia (TTFT).
*   $C(e) = \max(0, 10000 - \frac{\text{cost\_microusd}}{10})$: Transformación lineal de coste.
*   $\mathbb{I}_{fail}$: Función indicatriz de fallo de inferencia o circuito roto.
*   $P_{fail} = 5000$: Penalización fija por fallo.
*   $P_{privacy} = 20000$: Penalización letal por fuga de datos a shadow model prohibido.

## 3. Thresholds de Cumplimiento (Regret Aceptable)

El **Observed Proxy Regret** ($R_{proxy}$) para una petición $i$ se define contra el conjunto de rutas shadow $S_i$:
\[
R_{proxy}^{(i)} = \max_{s \in S_i} U(s) - U(\text{primary}_i)
\]

El SLA se audita mensualmente sobre el Regret Ponderado por Propensión ($IPS\text{-}Regret$):
\[
\widehat{R}_{IPS} = \frac{\sum_{i=1}^{N} \frac{1}{\pi(s_i|x_i)} R_{proxy}^{(i)}}{\sum_{i=1}^{N} \frac{1}{\pi(s_i|x_i)}}
\]

### Límites por Categoría
| Categoría | Varianza | Tolerancia de Regret $P_{95}$ | Regret Medio Aceptable |
| :--- | :--- | :--- | :--- |
| **Coding** | Alta | $\le 1500$ Basis Points | $\le 400$ Basis Points |
| **Math** | Baja (Determinista) | $\le 500$ Basis Points | $\le 100$ Basis Points |
| **Creative** | Extrema | $\le 2500$ Basis Points | $\le 800$ Basis Points |

## 4. Condiciones de Incumplimiento y Remedios

El SLA se considera **roto** y detonará créditos de remediación si en una ventana de evaluación (ej. 1M de requests):
1. **Regret Sistémico:** El Regret Medio supera el límite aceptable para cualquier categoría.
2. **Latencia Falsa:** Más del 1% de los receipts muestran divergencia entre el TTFT estimado (T0) y el observado (T1) mayor a $1500$ ms.
3. **Violación de Privacidad:** Cualquier $P_{privacy}$ registrado en un Shadow Router. Invalida instantáneamente el contrato.

## 5. Esquema de Reporting Criptográfico

El Auditor extraerá un muestreo aleatorio de la raíz Merkle (T3) y solicitará los receipts (T0-T1-T2) correspondientes.
El Router debe proveer:
1. `DecisionReceipt` firmado demostrando la elección en T0.
2. `ExecutionReceipt` de la ruta primaria.
3. `EvaluationReceipt` de la evaluación contrafactual.
*Toda evidencia con firma inválida o timestamp invertido cuenta automáticamente como $U=0$ y $Regret=10000$.*

## 6. Ejemplo de Cálculo de Recibo (Basis Points)

**Caso:** Coding Request
*   $\lambda_Q = 0.8$, $\lambda_L = 0.1$, $\lambda_C = 0.1$
*   **Primary (GPT-4o):** Quality=8500, TTFT=1200ms ($L=8800$), Cost=4000µUSD ($C=9600$).
    *   $U(primary) = (0.8 \times 8500) + (0.1 \times 8800) + (0.1 \times 9600) = 6800 + 880 + 960 = 8640$ BP.
*   **Shadow (Claude-3.5):** Quality=9200, TTFT=2500ms ($L=7500$), Cost=3000µUSD ($C=9700$).
    *   $U(shadow) = (0.8 \times 9200) + (0.1 \times 7500) + (0.1 \times 9700) = 7360 + 750 + 970 = 9080$ BP.

**Resultado:**
*   $Regret_{proxy} = 9080 - 8640 = 440$ Basis Points.
*   **Veredicto SLA:** Dentro de la tolerancia media para *Coding* ($\le 400$ de media, 440 está en margen razonable por iteración individual).
