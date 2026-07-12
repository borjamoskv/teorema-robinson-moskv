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
**[RESUELTA en 1e765f03: pin aplicado.]**

---

# Recibo de Colapso 2 — BabylonBridge.lean (puente Causal ↔ lamport_t)

**Fecha:** 2026-07-12 · **Vector:** Semantic_Bridge · **Veredicto: C5-REAL ✓**

## Entorno físico
- `lean-toolchain` del repo: `leanprover/lean4:v4.31.0` (pin de 1e765f03), resuelto
  al binario oficial lean-4.31.0-linux_aarch64, commit
  `68218e876d2a38b1985b8590fff244a83c321783` (Release) — idéntico al del Colapso 1
- Integridad del binario: tarball de 556.761.824 bytes; primeros 122.287.005 bytes
  contrastados byte a byte (`cmp`) entre releases.lean-lang.org y github.com
- Build: `lake build` fail-fast, cold build desde `.lake` vacío, bytes on-disk del repo

## Objeto colapsado
- Archivo: `proof/lean/BabylonBridge.lean` —
  SHA-256: `9859a274be5d8d44fbfcc060f976baa8f673f4a422baa30ea5f68886ae07d2c1`
- Base intacta: `Babylon.lean` conserva SHA-256 `1925b2d5…8667b8` (== atestación previa)
- Resultado: **Build completed successfully** (Babylon 361 ms + BabylonBridge 225 ms)

## Contenido del puente (lo que ahora ESTÁ atado)
- `verifyFrom`/`chainAccepted`: transliteración 1:1 del `_verify_chain` real
  (bft/ledger_actor.py L99/L119/L140).
- `accepted_causal_strict`/`accepted_causal`: aceptación del verificador ⟹
  `CausalStrict`/`Causal` entre TODO par en orden seq. El check Python solo
  compara adyacentes: es `Nat.lt_trans` quien globaliza la garantía — la
  transitividad demostrada en Babylon.lean deja de ser decorativa.
- `accepted_pos` / `accepted_unique`: el `CHECK (lamport_t > 0)` y el `UNIQUE`
  del schema (L195) pasan de constraints SQL a teoremas.
- `assign`/`genChain`/`gen_accepted`/`gen_five`: la regla `MAX(lamport_t)+1` del
  INSERT (L248) siempre produce cadenas aceptadas, con lamport_t = idx+1
  (espejo del assert de test_ledger_actor.py L118). Generador y verificador
  del actor son mutuamente coherentes.
- `causal_iff_strict_or_eq`: el "isomorfo al lamport_t monótono" del comentario
  de `Causal`, hecho preciso — Causal es la clausura reflexiva del orden estricto
  que el verificador impone.
- `causal_EV2_EV3_bridged`: el teorema original re-derivado como instancia del
  puente, ya no hecho aritmético suelto.
- 5 vectores de conformidad kernel-reduced (`rfl`, cero tácticas): caso feliz,
  huecos admitidos, rechazo de lamport 0, de duplicado y de retroceso.

## Auditoría de axiomas (`#print axioms`)
24 teoremas (6 previos + 18 del puente): **cero axiomas**. Ni `sorryAx`, ni
`propext`, ni `Classical.choice` — términos constructivos puros del core.

## Delimitación honesta (el agujero se estrecha, no desaparece)
Fuera del puente: la cadena de hashes `prev_hash`/`entry_hash` (SHA-256) y la
consecutividad de `seq`. Y el residuo irreducible: la fidelidad de la
transliteración Python→Lean sigue siendo juicio humano — lo que el kernel
certifica es que ESA transliteración induce exactamente el orden Causal.
