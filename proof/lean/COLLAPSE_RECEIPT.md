# Recibo de Colapso Termodinámico — Babylon.lean

**Fecha:** 2026-07-12 · **Vector:** Formal_Verification · **Veredicto: C5-REAL ✓**

## Entorno físico
- elan 4.2.3 (b6cec7e10 2026-06-08) — coincide con la Base del Claim
- Lean 4.31.0, commit 68218e876d2a38b1985b8590fff244a83c321783, aarch64-linux (Release)
- `lean-toolchain` del repo: `leanprover/lean4:stable` → resuelto hoy a v4.31.0
- Build: `lake build` fail-fast, cold build desde `.lake` vacío

## Objeto colapsado
- Archivo: `proof/lean/Babylon.lean`
- SHA-256: `1925b2d5262c90fec4203dea868765655d288033b4cc441f64f882a8328667b8`
- Resultado: **Build completed successfully** (287 ms de kernel-time)

## Auditoría de axiomas (`#print axioms`)
Los 6 teoremas (`causal_refl`, `causal_trans`, `causal_antisymm`, `causal_EV2_EV3`,
`causal_of_strict`, `ledger_seq_monotone`): **cero axiomas**. Ni `sorryAx`, ni
`propext`, ni `Classical.choice` — términos constructivos puros del core.

## Historial de Anergía detectada (estados previos rechazados por el kernel)
1. `eb644be1…` (`def Causal` + `by decide`): rechazado — `failed to synthesize
   Decidable (Causal 2 3)`. Un `def` es opaco para la síntesis de instancias.
2. `27437907…` (`abbrev Causal` + `by omega`): rechazado — `omega` no despliega
   `Causal`/`CausalStrict`; su frontend busca `≤`/`<` sintácticos en la meta.
   Dos teoremas no cerraban (líneas 39 y 47) aunque el comentario del archivo
   afirmaba lo contrario.

## Fix aplicado (estado actual, verificado)
- L39: `by omega` → `by decide` (el `abbrev` reducible sí permite sintetizar
  `Decidable`, exactamente como documenta el comentario de L16-17)
- L46-47: `by omega` → término puro `Nat.le_of_lt h` (cero tácticas)

## Deuda de reproducibilidad
`leanprover/lean4:stable` es un objetivo móvil: el mismo AST puede colapsar hoy
y no mañana. Para C5 estricto, fijar `lean-toolchain` a `leanprover/lean4:v4.31.0`.
