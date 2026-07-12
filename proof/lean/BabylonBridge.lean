-- C5-REAL: Puente semántico Causal ↔ lamport_t del BFTLedgerActor.
-- Estrechamiento del agujero declarado en lean4_semantic_gap_fracture.yaml.
-- Babylon.lean afirma en comentario que `Causal` es "isomorfo al lamport_t
-- monótono del BFTLedgerActor", pero ninguna prueba ataba esa flecha. Aquí las
-- DOS reglas reales del actor (bft/ledger_actor.py) se transcriben a Lean y se
-- demuestra que inducen exactamente el orden `Causal`/`CausalStrict`:
--
--   1. Verificador `_verify_chain` (L99/L119/L140): `last_lamport = 0`; por
--      cada fila en orden seq: `if lamport_t <= last_lamport: return False`,
--      después `last_lamport = lamport_t`.
--   2. Asignación en INSERT (L248): `COALESCE((SELECT MAX(lamport_t) ...),0)+1`.
--
-- Queda ATADO: aceptación del verificador ⟹ CausalStrict (y Causal) entre todo
-- par en orden seq — la comprobación Python es solo entre adyacentes y es
-- `Nat.lt_trans` quien la eleva a orden global; la positividad (CHECK
-- lamport_t > 0, L195) y la unicidad (UNIQUE, L195) dejan de ser constraints
-- SQL y pasan a teoremas; la regla MAX+1 produce siempre cadenas aceptadas con
-- lamport_t = idx+1 (espejo del assert de test_ledger_actor.py L118).
--
-- Queda FUERA (el agujero se estrecha, no desaparece): la cadena de hashes
-- prev_hash/entry_hash (SHA-256) y la consecutividad de seq.
-- Cero axiomas, cero `sorry`, cero `trivial : True`.

import Babylon

namespace Babylon

/-- Transliteración del bucle verificador real (`_verify_chain`): `true` sii
    cada `lamport_t` supera estrictamente al acumulador. Línea a línea con
    L119 (`lamport_t <= last` ⟹ rechazo) y L140 (avance del acumulador). -/
def verifyFrom : Timestamp → List Timestamp → Bool
  | _, [] => true
  | last, t :: ts => if t ≤ last then false else verifyFrom t ts

/-- Verificador completo: el actor arranca con `last_lamport = 0` (L99). -/
def chainAccepted (ts : List Timestamp) : Bool :=
  verifyFrom 0 ts

/-- Descomposición de una aceptación: la cabeza supera estrictamente al
    acumulador y la cola se acepta desde la cabeza. Es L119+L140 como
    proposición. -/
theorem verify_head {last t : Timestamp} {ts : List Timestamp}
    (h : verifyFrom last (t :: ts) = true) :
    CausalStrict last t ∧ verifyFrom t ts = true := by
  have h' : (if t ≤ last then false else verifyFrom t ts) = true := h
  cases Nat.lt_or_ge last t with
  | inl hlt =>
    have hne : ¬ t ≤ last := fun hle => Nat.lt_irrefl last (Nat.lt_of_lt_of_le hlt hle)
    rw [if_neg hne] at h'
    exact ⟨hlt, h'⟩
  | inr hge =>
    rw [if_pos hge] at h'
    exact Bool.noConfusion h'

/-- Todo elemento de una cadena aceptada desde `last` está estrictamente por
    encima de `last`. El check Python solo compara adyacentes: es la
    transitividad (`Nat.lt_trans`) quien hace global la garantía. -/
theorem verify_all_gt {last : Timestamp} {ts : List Timestamp}
    (h : verifyFrom last ts = true) : ∀ t ∈ ts, CausalStrict last t := by
  induction ts generalizing last with
  | nil => intro t ht; cases ht
  | cons x xs ih =>
    intro t ht
    have hx := verify_head h
    cases ht with
    | head _ => exact hx.1
    | tail _ hmem => exact Nat.lt_trans hx.1 (ih hx.2 t hmem)

/-- Autopertenencia tras un prefijo: `b ∈ l₂ ++ b :: l₃`. Auxiliar sin
    dependencias de librería. -/
theorem mem_append_cons_self (l₂ l₃ : List Timestamp) (b : Timestamp) :
    b ∈ l₂ ++ b :: l₃ := by
  induction l₂ with
  | nil => exact List.Mem.head _
  | cons x xs ih => exact List.Mem.tail x ih

/-- Si se acepta `l₁ ++ ts` desde `last`, algún acumulador acepta `ts`. -/
theorem verify_suffix {ts : List Timestamp} :
    ∀ (l₁ : List Timestamp) (last : Timestamp),
      verifyFrom last (l₁ ++ ts) = true →
      ∃ last', verifyFrom last' ts = true := by
  intro l₁
  induction l₁ with
  | nil => intro last h; exact ⟨last, h⟩
  | cons x xs ih => intro last h; exact ih x (verify_head h).2

/-- PUENTE (orden estricto): si el verificador real acepta la cadena, todo par
    `(a, b)` con `a` anterior a `b` en orden seq cumple `CausalStrict a b`. -/
theorem accepted_causal_strict {l₁ l₂ l₃ : List Timestamp} {a b : Timestamp}
    (h : chainAccepted (l₁ ++ (a :: (l₂ ++ (b :: l₃)))) = true) :
    CausalStrict a b := by
  obtain ⟨last', h'⟩ := verify_suffix l₁ 0 h
  exact verify_all_gt (verify_head h').2 b (mem_append_cons_self l₂ l₃ b)

/-- PUENTE (orden débil): la aceptación induce `Causal` — el orden que
    Babylon.lean modela — entre todo par en orden seq. Esta es la flecha
    que el comentario de `Causal` afirmaba sin prueba. -/
theorem accepted_causal {l₁ l₂ l₃ : List Timestamp} {a b : Timestamp}
    (h : chainAccepted (l₁ ++ (a :: (l₂ ++ (b :: l₃)))) = true) :
    Causal a b :=
  causal_of_strict (accepted_causal_strict h)

/-- El `CHECK (lamport_t > 0)` del schema (L195) es teorema, no constraint:
    toda cadena aceptada tiene lamports estrictamente positivos. -/
theorem accepted_pos {ts : List Timestamp}
    (h : chainAccepted ts = true) : ∀ t ∈ ts, 0 < t :=
  verify_all_gt h

/-- El `UNIQUE` de lamport_t (L195) es teorema: dos posiciones distintas de
    una cadena aceptada nunca comparten lamport. -/
theorem accepted_unique {l₁ l₂ l₃ : List Timestamp} {a b : Timestamp}
    (h : chainAccepted (l₁ ++ (a :: (l₂ ++ (b :: l₃)))) = true) : a ≠ b :=
  Nat.ne_of_lt (accepted_causal_strict h)

/-- Regla de asignación real del INSERT (L248): nuevo lamport = MAX + 1.
    Sobre una cadena aceptada el máximo es el último lamport, así que el
    estado del actor se modela por ese acumulador. -/
def assign (lastMax : Timestamp) : Timestamp :=
  lastMax + 1

/-- La asignación MAX+1 siempre produce un evento estrictamente posterior. -/
theorem assign_strict (m : Timestamp) : CausalStrict m (assign m) :=
  Nat.lt_succ_self m

/-- `n` inserciones consecutivas del actor partiendo del acumulador `last`. -/
def genChain : Timestamp → Nat → List Timestamp
  | _, 0 => []
  | last, n + 1 => assign last :: genChain (assign last) n

/-- SOUNDNESS del generador: toda cadena producida por la regla MAX+1 es
    aceptada por el verificador. Las dos mitades del actor son coherentes. -/
theorem gen_accepted : (n : Nat) → (last : Timestamp) →
    verifyFrom last (genChain last n) = true
  | 0, _ => rfl
  | n + 1, last => by
    have h : verifyFrom last (genChain last (n + 1))
        = if assign last ≤ last then false
          else verifyFrom (assign last) (genChain (assign last) n) := rfl
    have hne : ¬ assign last ≤ last := Nat.not_succ_le_self last
    rw [h, if_neg hne]
    exact gen_accepted n (assign last)

/-- Desde tabla vacía (acumulador 0), el actor genera lamports `1,2,3,4,5`:
    espejo exacto del `assert row.lamport_t == idx + 1` de
    test_ledger_actor.py (L118). -/
theorem gen_five : genChain 0 5 = [1, 2, 3, 4, 5] :=
  rfl

-- Vectores de conformidad: la spec Lean responde igual que el verificador
-- Python ante los mismos casos (kernel-reduced, sin tácticas).

/-- Caso feliz del test suite: lamports consecutivos desde 1. -/
theorem conf_happy : chainAccepted [1, 2, 3] = true := rfl

/-- El verificador admite huecos (solo exige monotonía estricta). -/
theorem conf_gaps : chainAccepted [1, 5, 9] = true := rfl

/-- Rechazo de lamport 0: refleja el arranque `last_lamport = 0` (L99)
    y el CHECK del schema. -/
theorem conf_zero_rejected : chainAccepted [0, 1, 2] = false := rfl

/-- Rechazo de duplicado: refleja el UNIQUE (L195) vía `<=` de L119. -/
theorem conf_dup_rejected : chainAccepted [1, 2, 2] = false := rfl

/-- Rechazo de retroceso: una bifurcación temporal nunca verifica. -/
theorem conf_regress_rejected : chainAccepted [1, 3, 2] = false := rfl

/-- El isomorfismo del comentario de `Causal`, hecho preciso: `Causal` es
    exactamente la clausura reflexiva del orden estricto que el verificador
    impone. Eventos distintos del ledger están SIEMPRE estrictamente
    ordenados; la igualdad solo relaciona un evento consigo mismo. -/
theorem causal_iff_strict_or_eq {a b : Timestamp} :
    Causal a b ↔ (CausalStrict a b ∨ a = b) :=
  ⟨fun h => match Nat.eq_or_lt_of_le h with
    | .inl he => .inr he
    | .inr hlt => .inl hlt,
   fun h => match h with
    | .inl hlt => Nat.le_of_lt hlt
    | .inr he => he ▸ Nat.le_refl a⟩

/-- `causal_EV2_EV3` re-derivado del verificador real: 2 y 3 son los lamports
    de EV_2 y EV_3 dentro de la cadena aceptada `[1, 2, 3]`. El teorema
    original deja de ser un hecho aritmético suelto: es instancia del puente. -/
theorem causal_EV2_EV3_bridged : Causal 2 3 :=
  accepted_causal (l₁ := [1]) (l₂ := []) (l₃ := []) rfl

end Babylon
