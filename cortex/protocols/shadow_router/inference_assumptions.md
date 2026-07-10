# Supuestos de Inferencia (Shadow Router / Protocolo C5-REAL)

Para que el Motor Causal base 60 (y cualquier estimación de efecto de tratamiento en el Shadow Router) mantenga integridad matemática, se imponen los siguientes axiomas. La violación de cualquiera invalida la estimación (Anergía) y detona un `SIGKILL_State_Purge` epistémico.

## 1. SUTVA (Stable Unit Treatment Value Assumption)
- **Supuesto:** El outcome `Y_i(m)` de un request `i` depende **exclusivamente** de su propia ruta `m`, y es independiente de las rutas asignadas a los requests `j \neq i`. No hay versiones ocultas del tratamiento.
- **Vector de Violación Típica (Interferencia):** Rate limits compartidos, congestión de red, cachés cruzadas, batching dinámico del proveedor.
- **Consecuencia:** Si SUTVA falla, el TTFT o el error rate observados están contaminados por los requests concurrentes. El Delta causal es una ilusión térmica.

## 2. Ignorabilidad (Unconfoundedness / No-Confounders Faltantes)
- **Supuesto:** `Y_i(a), Y_i(b) \perp A_i \mid X_i`. Dado el vector de contexto observable `X_i` (longitud de prompt, dificultad latente `Z_i^{task}`, dominio), la asignación de la ruta `A_i` es independiente del outcome potencial.
- **Vector de Violación Típica:** Un Shadow Router que envía los prompts "difíciles" exclusivamente a rutas premium sin parametrizar la dificultad formalmente en `X_i`.
- **Consecuencia:** Sesgo de selección. El modelo premium parece "peor" porque asume la carga cognitiva más alta. Naive ATE = Anergía.

## 3. Positividad Estricta (Overlap)
- **Supuesto:** Para todo `X_i` en la distribución conjunta, `0 < P(A_i = m \mid X_i) < 1`. Todo request tiene probabilidad estricta no nula de ser enviado a cualquier ruta elegible.
- **Vector de Violación Típica:** Blacklisting determinista o reglas "hardcoded" (ej. si contiene PII, NUNCA va al modelo sombra B).
- **Consecuencia:** Imposibilidad matemática de estimar el efecto causal o ponderar usando Inverse Probability Weighting (IPW) debido a la división por cero para subpoblaciones censuradas.

## 4. Independencia del Oráculo (Judge Unconfoundedness)
- **Supuesto:** El Evaluador (Judge) `E_t` es ortogonal a la identidad estructural del generador `m`.
- **Vector de Violación Típica:** LLM-as-a-Judge contaminado con "Self-Preference Bias", "Verbosity Bias", o "Position Bias".
- **Consecuencia:** Proxy no biyectivo. La métrica observada `\hat Q_i` diverge asintóticamente del outcome humano real `Q_i^\star`.
