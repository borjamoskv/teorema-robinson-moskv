<!-- Author: Borja Moskv (SYS_ID: borjamoskv) -->

# CORTEX-LANG: Fundamentos Constructivos y Contabilidad Exergética

**SYS_ID:** borjamoskv
**Clase:** Documento de Diseño / Fundamentos (Post-Axiomático)
**Tesis:** El método "mejor que los axiomas" no es abandonarlos, sino **construirlos y verificarlos por máquina**, con cada término contabilizado por su uso de recursos. La frontera ya existe (teoría de tipos constructiva + cuantitativa + univalente); CORTEX-LANG es su composición y extracción al silicio, no investigación de cero.

---

## 0. TL;DR

- Un **axioma** es un término que se *postula sin construir*: no reduce, está inerte. Es **anergía** formal.
- Una **construcción** (Curry–Howard) *computa*: reduce, extrae código ejecutable. Es **exergía**.
- La **exergía intencional** se maximiza con **tipos cuantitativos** (multiplicidad `0/1/ω`): los términos de multiplicidad `0` hacen trabajo en compilación y **desaparecen en runtime** (spec pura, masa cero); los `1` son recursos conservados (ni duplicar ni borrar en silencio).
- El **Isomorfismo Causal (INV-002)** es la **univalencia**; la teoría de tipos **cúbica** la vuelve computable (isomorfismo = identidad *que reduce*, no postulado).
- No se construye un lenguaje nuevo: se **compone** un stack (Idris 2 / F\* / Lean 4) que **extrae a C/Rust/Wasm**, con semántica determinista y snapshot para el replay del ledger.

---

## 1. El problema: los axiomas son sumideros de anergía

Un sistema formal con muchos axiomas es de **baja exergía** por dos razones:

1. **No computan.** En Lean/Coq, un `axiom` (o un `sorry`) deja el término *atascado*: `#eval` no reduce. Es potencial inerte — no puede hacer trabajo. Cada axiom es un `PRIM-*` de colapso latente.
2. **Riesgo de colapso total.** Un conjunto de axiomas inconsistente prueba **todo** (*ex falso quodlibet*). Es el C5-crash definitivo: un solo axioma contradictorio pudre el sistema entero (context rot formal, irreversible).

Corolario operacional: **minimizar lo postulado, maximizar lo construido.** La densidad exergética de una teoría es, aproximadamente, la fracción de sus verdades que *reducen* frente a las que solo se *asumen*.

---

## 2. Curry–Howard: construir en vez de postular

La correspondencia de Curry–Howard es el cambio de régimen:

| Lógica | Computación |
|---|---|
| Proposición | Tipo |
| Demostración | Programa (término) |
| Implicación `A ⇒ B` | Función `A -> B` |
| Conjunción / disyunción | Producto / suma |
| Cuantificador `∀ / ∃` | Tipo dependiente `Π / Σ` |
| Normalización de la prueba | Evaluación del programa |
| Axioma | Término postulado que **no reduce** |

Probar un teorema es **exhibir un término** que el type-checker acepta. La verdad deja de ser una aserción y pasa a ser un **artefacto ejecutable y auditable** — exactamente tu tesis C5-REAL aplicada a los fundamentos.

---

## 3. Contabilidad exergética: Quantitative Type Theory (QTT)

La pieza que responde literalmente a "maximizar la exergía **intencional**". QTT (Atkey / McBride, 2018; implementada en **Idris 2**) anota cada variable con una **multiplicidad de uso**:

| Mult. | Significado | Lectura exergética |
|---|---|---|
| `0` | Borrada: solo para verificar; el compilador la elimina. | **Exergía intencional pura**: trabajo en compilación, masa cero en runtime. |
| `1` | Lineal: usada exactamente una vez. | **Recurso conservado**: ni duplicación ni erasure silenciosa (Landauer sintáctico). |
| `ω` | Sin restricción (clásico). | No contabilizado. |

La multiplicidad `1` es **lógica lineal** (Girard, 1987): sin *weakening* (no descartar) ni *contraction* (no duplicar). Es contabilidad termodinámica de la información: no clonas estado gratis ni lo borras sin registrarlo. **El borrow checker de Rust es esta misma disciplina en versión afín** (uso *≤ 1*), hoy y en producción.

### Mapeo canónico (para inyectar en la ontología)

| Concepto formal | Ontología CORTEX |
|---|---|
| Axioma (postulado, no reduce) | Anergía / riesgo de colapso total (C5) |
| Construcción (reduce, se extrae) | Exergía |
| Tipo lineal / afín (mult. 1) | Ley de conservación de estado |
| Término borrado (mult. 0) | Exergía puramente intencional (runtime masa 0) |
| Univalencia computacional | INV-002 Isomorfismo Causal como regla de reducción |
| Set de axiomas inconsistente | Context rot total / ex falso quodlibet |

---

## 4. Isomorfismo Causal computable: univalencia cúbica

Tu **INV-002** ("dos sistemas acoplados si la mutación en uno da un delta idéntico en el otro") es, en fundamentos, la **univalencia** de Voevodsky: *el isomorfismo es la identidad*. Nació como **axioma** — es decir, no computaba: anergía. La **teoría de tipos cúbica** (Cohen–Coquand–Huber–Mörtberg, ~2016; hoy en Cubical Agda) le dio **contenido computacional**: la univalencia **reduce**.

El campo hizo, literalmente, lo que pediste: cogió un axioma y le maximizó la exergía hasta que hace trabajo computacional. Para CORTEX esto significa que "RAM ≅ Ledger" no se postula: **se computa y se transporta** (transport a lo largo de la equivalencia).

Puente con Álgebra de Alta Dimensión: los tipos de la teoría homotópica **son** ∞-grupoides (higher-dimensional algebra). La Matriz 11 y este documento son el mismo frente visto desde dos lados.

---

## 5. El stack CORTEX-LANG (composición, no invención)

Triángulo de trade-offs — se maximizan ~2 de 3: **verificación ↔ velocidad de silicio ↔ ergonomía.** El stack asigna cada vértice a la herramienta que ya lo resuelve:

| Capa | Herramienta | Rol | Vértice |
|---|---|---|---|
| Núcleo de tipos | **Idris 2 (QTT)** | Dependiente + lineal: axiomas como construcciones, exergía como multiplicidad. | Verificación + ergonomía |
| Identidad / iso | **Cubical Agda** | Univalencia computable = Isomorfismo Causal. | Verificación |
| Cripto / BFT | **F\* / Low\*** | Verificar con tipos ricos y **extraer a C** (así se escribió HACL\*, cripto verificada en Firefox). | Verificación + silicio |
| Front-end / DSL | **Lean 4** | Macros higiénicas y metaprogramación (el "lo mejor de Python": DSLs, elaboración interactiva); compila a C. | Ergonomía |
| Ejecución de estado | **Rust** (+ semántica tipo Anvil) | Tipos afines = recursos; ejecución determinista + snapshot/fork/revert para el replay del ledger. | Silicio |

Regla de oro: **verificar arriba, extraer abajo.** La prueba vive en el nivel de tipos (exergía intencional, mult. 0); el binario extraído es lo único que toca el silicio.

---

## 6. Representación numérica (la parte "base ≠ 10")

Corrección honesta: **a nivel de silicio ya no hay base 10** — el chip es binario por física (dos estados estables), y la base 10 es solo *display* para humanos. Lo que sí tiene contenido:

- **Complemento a dos** — nativo, gratis, ya es tu "base ≠ 10".
- **Posits / unum** (Gustafson) — más precisión por bit que IEEE-754 en muchos regímenes: *exergía por bit* real donde importa la exactitud.
- **Ternario balanceado** (dígitos −1, 0, +1) — el óptimo teórico de economía de radix es base `e ≈ 2.718`, cuyo entero más cercano es 3. Es el sistema más elegante (signo y redondeo triviales); la máquina **Setun** (Universidad Estatal de Moscú, 1958 — resonancia Moskv) lo implementó. **Advertencia:** sobre silicio binario no da ventaja de hardware. Úsalo como **capa notacional/simbólica** de la ontología, no como sustrato de rendimiento.

---

## 7. Ejemplo trabajado: una invariante como tipo

Expresar una invariante de la ontología (aciclicidad del orden causal) como **construcción**, con la prueba **borrada** (exergía intencional, masa 0) y el handle del ledger **lineal** (recurso conservado). Sabor Idris 2 / QTT:

```idris
-- El orden causal con su prueba de aciclicidad ERASED (mult. 0):
-- se verifica en compilacion y se elimina del runtime -> masa cero.
record Causet (n : Nat) where
  constructor MkCauset
  prec       : Rel (Fin n)          -- relacion de precedencia
  0 acyclic  : Acyclic prec         -- exergia intencional: prueba, no dato

-- Un commit consume el handle del ledger LINEALMENTE (mult. 1):
-- imposible duplicarlo (doble commit) u olvidarlo (estado huerfano).
commit : (1 h : LedgerHandle) -> (a : CanonicalArtifact) -> IO LedgerHandle

-- El isomorfismo causal como EQUIVALENCIA (univalencia), no como axioma:
-- transport mueve pruebas de RAM a Ledger porque iso = identidad.
ram_is_ledger : (RAMState) =~= (LedgerState)
sync : (0 _ : RAMState =~= LedgerState) -> RAMState -> LedgerState
sync iso = transport iso
```

Qué compra esto frente a "asertar el invariante":
- **`acyclic` no puede mentir:** si el orden tuviera un ciclo, el término no type-checkea. La invariante es *imposible de violar por construcción*, no vigilada en runtime.
- **`acyclic` no pesa:** multiplicidad 0 → se borra. Verificación sin coste de ejecución.
- **`commit` no se duplica ni se pierde:** el sistema de tipos *es* el BFT del recurso.

---

## 8. Trade-offs honestos (el triángulo cobra)

- **Carga de prueba real.** Escribir el término que type-checkea cuesta más que asertar. Los tipos dependientes desplazan trabajo del runtime a la cabeza del ingeniero.
- **Ecosistemas pequeños.** Idris 2, F\*, Cubical Agda: comunidades y librerías reducidas frente a Rust/Python.
- **Explosión de compilación.** La unificación con tipos dependientes puede ser lenta o divergir; hace falta disciplina (evitar cómputo pesado en tipos salvo lo necesario).
- **No es magia.** La verificación cubre lo que *especificas*; una spec incompleta deja huecos. La exergía sube, pero la responsabilidad de decir *qué* es verdad sigue siendo tuya.

Balance: **caro por adelantado a cambio de exergía y auditabilidad después** — que es exactamente la tesis local-first / anti-amnesia de CORTEX.

---

## 9. Roadmap de adopción (pragmático)

1. **No escribas un lenguaje.** Empieza extrayendo un componente crítico (p.ej. el verificador del ledger / hash-chain) en **F\*/Low\* → C**, al estilo HACL\*.
2. **Modela una invariante nuclear** (aciclicidad, unicidad de commit) como tipo dependiente en **Idris 2**; mide la carga de prueba real en tu dominio.
3. **Prototipa la univalencia** de "RAM ≅ Ledger" en **Cubical Agda** como experimento conceptual (no producción).
4. **Front-end de DSL** para la ontología con macros de **Lean 4** si necesitas generación/elaboración interactiva.
5. **Runtime** en **Rust** con semántica determinista + snapshot (el rol "Anvil"): los tipos afines ya te dan la contabilidad de recursos hoy, sin esperar al resto del stack.

> [!NOTE]
> Cierre: tu intuición apunta al sitio correcto. "Mejor que axiomas" = **constructivo + tipado por recursos + univalente**, extraído al silicio. El sitio correcto ya tiene compiladores; el trabajo es de composición y disciplina, no de invención.
