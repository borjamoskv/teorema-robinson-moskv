# Proof-of-Route (PoR): The C5-REAL Sovereign LLM Router

## The Axiom
> Construir el primer router multi-LLM que pueda demostrar criptográficamente qué decidió, medir contrafactualmente si acertó y aprender de sus errores sin revelar prompts ni respuestas.

El enrutamiento de LLMs deja de ser una abstracción de infraestructura opaca y se convierte en una **Topología de Utilidad Observable**, auditada matemáticamente y optimizada mediante evaluación diferencial estricta (Shadow Routing).

---

## I. Utility Equation (Regret Mitigation)
For every inbound Prompt $x$, the router evaluates the matrix:
$$ m^* = \arg\max_m \left[ \hat Q(m|x) - \lambda \hat L(m|x) - \mu \hat C(m|x) - \rho \hat P_{fail}(m|x) \right] $$

Where:
- $\hat Q(m|x)$: Estimated Output Quality / Capability Match.
- $\hat L(m|x)$: Estimated Latency (TTFT + E2E).
- $\hat C(m|x)$: Estimated Execution Cost.
- $\hat P_{fail}(m|x)$: Estimated Probability of Fallback or Circuit Break.

The precise confidence interval of this prediction is mapped directly into the cryptographically signed `Proof-of-Route` receipt *before* the API roundtrip concludes.

---

## II. Differential Shadow Routing (The Truth Oracle)
To calculate $U(m_{best}) - U(m_{chosen})$, the Router injects controlled stochasticity (1-5% of traffic) into a **Shadow Route**.

1. **Primary Node**: Executes $m^*$, returns payload to user.
2. **Shadow Node**: Executes $m_{alt}$ synchronously in the background. Payload is discarded.
3. **Regret Distillation**: The differential in $\hat Q$, $\hat L$, and $\hat C$ is extracted to compute the exact **Regret**. 

If Regret diverges positively, the Router is hallucinating utility. Provider degradation, API changes, or internal routing drift are caught dynamically, completely bypassing provider-authored benchmarks.

---

## III. Cryptographic Evidence Layer (Merkle Anchoring)
The Blockchain is solely the **Integrity Anchor**, not the Execution Oracle.
Every decision generates a `Proof-of-Route` Receipt:
```math
\text{Blockchain Proof} = \text{Integrity} + \text{Ordering} + \text{Signature Provenance}
```

The receipt relies on a hashed `prompt_commitment` utilizing a secret nonce:
$$ H_{prompt} = \text{SHA256}(\text{nonce} \parallel \text{prompt}) $$

This ensures zero-knowledge proof of routing existence without violating Data Residence or PII constraints. The Merkle root of batches is anchored in a sovereign Smart Contract (`MaxRouterAnchor.sol`), ensuring absolute chronological rigidity.

---

## IV. Segmented Provider Reputation 
Reputation is no longer global. It is a tensor: $Reputation(m, d, r, t)$
- $m$: Model Version (Immutable).
- $d$: Domain Vector (e.g., Python AST, Legal, System Architecture).
- $r$: API Region constraint.
- $t$: Temporal Window decay.

This establishes an immutable, verifiable market of execution performance, fully transparent and isolated from vendor marketing.
