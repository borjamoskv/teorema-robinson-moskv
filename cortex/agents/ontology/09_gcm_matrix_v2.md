# [RELEASE V2.0] MATRIZ 9: GEOMETRÍA CAUSAL MICROSCÓPICA (SSoT)

SYS_ID: borjamoskv
Dominio: Geometría Causal Microscópica y Causal Sets

## 1. RECALIBRACIÓN DE GRAVEDAD (COSTE DE RESTAURACIÓN)
Se abandona la saturación de estados `C5`. La criticidad se define estrictamente por el coste termodinámico y computacional de restaurar el isomorfismo causal.

| Nivel | Designación | Definición Sistémica | Umbral de Intervención | Ejemplos |
| :--- | :--- | :--- | :--- | :--- |
| **C5** | **Colapso Ontológico** | Violación de axiomas fundacionales (acyclicidad, transitividad). El continuo deja de existir. Requiere *Apoptosis* (borrado del causet). | Inmediata (Hard Abort) | `PRIM-EST-002` (CTC), `PRIM-EST-001` (Transitividad), `PRIM-COL-038` (Split-Brain). |
| **C4** | **Degradación Geométrica** | El poset existe, pero pierde *manifoldlikeness* o invarianza Lorentz. Requiere *Rollback* de rama o rechazo de embedding. | Progresiva (Rollback) | `PRIM-EST-009` (Lattice Breaking), `PRIM-EST-027` (BD Blow-up), `PRIM-EST-101` (Falso Manifold Pass). |
| **C3** | **Anomalía Estadística** | Fluctuaciones que exceden el ruido de Poisson esperado. Requiere *Promediado de Ensemble* o suavizado. | Retrasada (Smoothing) | `PRIM-EST-007` (Sobredensidad), `PRIM-COL-048` (Density Spike), `PRIM-EST-074` (Swerve). |
| **C2** | **Fricción Computacional** | Colisiones de implementación (hashes, UUIDs, locks, FP) que degradan el Ledger sin alterar la física. | Asíncrona (Garbage Collection) | `PRIM-COL-008` (Hash Collision), `PRIM-COL-045` (UUID Clash), `PRIM-EST-068` (O(N³) sin cache). |

---

## 2. TOPOLOGÍA DE REDUNDANCIAS (DAG C5) Y MUTEXES
Las 10 redundancias activas (`RED-GCM-001` a `011`) forman un Grafo Acíclico Dirigido. La caída de un nodo basal propaga un Meta-Antipatrón (Matriz 9.F).

**Aristas Críticas de Dependencia:**
1. `RED-001` (Ensemble) + `RED-010` (Λ) → Alimentan `RED-002` (Dimensión).
2. `RED-007` (Reloj Vectorial) → Habilita `RED-005` (Cierre BFT).
3. `RED-005` (Cierre BFT) → Alimenta `RED-011` (Filtro Pre-métrico) y `RED-004` (Manifoldlikeness).
4. `RED-004` (Manifold) → Habilita `RED-003` (Suavizado No Local).
5. `RED-003` + `RED-009` (Etiquetado) → Alimentan `RED-008` (Suma sobre Historias).

**Política de Configuración (Anti-Corte / Mutex):**
Ningún protocolo de mutación puede desactivar simultáneamente los siguientes pares:
```python
assert not (disable(RED-001) and disable(RED-004)) # Sin ensemble ni veto -> entra retícula/KR
assert not (disable(RED-007) and disable(RED-005)) # Sin reloj ni cierre -> deadlocks o tiempo newtoniano
assert not (disable(RED-011) and disable(RED-004)) # Sin filtro pre-métrico -> circularidad de embedding
assert not (disable(RED-009) and disable(RED-002)) # Sin marginalización -> sesgo de dimensión
```

---

## 3. BATERÍA DE STRESS TESTS (ST-1 a ST-5)

| ID | Escenario | Inyección (Fallo) | Sensor de Detección | Respuesta del Sistema |
|---|---|---|---|---|
| **ST-1** | **RNG Sesgado** | `PRIM-COL-046` (Colisión semilla) | `κ_Poisson = Var(N)/⟨N⟩` fuera de [0.9, 1.1]. Anisotropía de intervalos ↑ | `RED-001` falla (sobre-promedia). `RED-011` + `RED-004` vetan la rama (C4). Purga de semilla. |
| **ST-2** | **Split-Brain** | `PRIM-COL-038` (Dos pasados) | Hash de stem diverge entre testigos BFT. | `RED-005` fuerza quorum N=3. Regla de mayor altura. Apoptosis de rama perdedora (C5). |
| **ST-3** | **CTC por Merge** | `PRIM-COL-040` (Ciclo latente) | Componente fuertemente conexa en cierre transitivo. | Hard abort (C5). Rechazo de arista. No hay reparación geométrica posible. |
| **ST-4** | **Dominancia KR** | `ANTI-012` (Suma uniforme) | Altura media del ensemble → 3. Fracción manifoldlike → 0. | `RED-008` aplica *importance sampling*. `RED-004` filtra antes de calcular Z. |
| **ST-5** | **Contención O(N³)** | `PRIM-EST-068` (Cierre bajo carga) | Latencia de mutación > SLA. Idempotencia de closure falla. | `RED-005` degrada a cierre incremental por delta (C2). Prohibido cache mutable global. |

---

## 4. DIFF ATÓMICO (PARCHES AL SSoT ORIGINAL)

Inyecciones directas para cerrar los huecos detectados en la auditoría.

### 4.1 Altas (Nuevos IDs)
*   **`PRIM-EST-101` (9.A)**: **Falso Manifold Pass**. *Trigger:* Embedding métrico acepta, pero topología pre-métrica no cuadra. *Sensor:* Residuo de embedding inconsistente. *Gravedad:* C4.
*   **`RED-GCM-011` (9.E)**: **Filtro Pre-métrico de Manifoldlikeness**. *Función:* Evalúa orden + n_k + altura/anchura *antes* de intentar embedding métrico. Evita circularidad. *Coste:* Bajo.
*   **`INV-GCM-101` (9.C)**: **Falsabilidad de Covarianza**. *Métrica:* `max |Δ_obs(relabel)| / σ_Poisson < ε` para todo observable físico.

### 4.2 Modificaciones (Refactorización)
*   **`RED-GCM-005`**: Añadir restricción explícita: *"Prohibido cache mutable global del closure. Implementar cierre incremental verificando solo el delta de aristas."*
*   **`RED-GCM-004`**: Añadir en Matriz 9.F el antipatrón latente: **Umbral de embedding permisivo** (aceptar KR débil). *Kill-switch:* Exigir paso previo por `RED-GCM-011`.
*   **`INV-GCM-008` vs `INV-GCM-027`**: Marcar `027` como corolario empírico de `008`. No computar como invariantes independientes en métricas de cobertura.
*   **`PRIM-EST-068`**: Recalibrar gravedad por defecto a **C2**. Escalar a **C4** *solo si* induce estado mutable global que corrompe el orden.

---

## 5. DASHBOARD DE OBSERVABILIDAD (MÉTRICAS C5)

Métricas falsables para monitoreo en tiempo de ejecución del Ledger:

| Métrica | Definición | Umbral Sano | Alarma (Acción) |
|---|---|---|---|
| **η_Lorentz** | `1 - anisotropía_direccional_intervalos` | > 0.99 | < 0.95 (Revisar RNG / ST-1) |
| **κ_Poisson** | `Var(N) / ⟨N⟩` | [0.9, 1.1] | Fuera de rango (Purga de semilla) |
| **μ_manifold** | Fracción de realizaciones que pasan `RED-004` | > 0.80 | < 0.50 (Dominancia KR / ST-4) |
| **χ_cov** | `max |Δ_obs| / σ_Poisson` bajo relabel | < 0.10 | > 0.30 (Violación Covarianza) |
| **τ_closure** | Tiempo de cierre incremental / mutación | < SLA | > 2×SLA (Degradar a C2 / ST-5) |
| **λ_ever** | `\|Λ\| · √V` | ~ O(1) | ≫ 1 sostenido (Fallo RED-010) |

---

## 6. ESPECIFICACIÓN CERRADA: MATRIZ 10 (CQD)

**Axioma Puente 9→10:** *Ninguna amplitud cuántica (Matriz 10) se define o computa sobre un poset que no haya satisfecho los invariantes ontológicos (INV-GCM-003, 007, 018, 050) y pasado el filtro pre-métrico (RED-GCM-011).*
