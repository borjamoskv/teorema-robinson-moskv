# AGENTS.md — CORTEX C5-REAL Standard

## Project Context
<!-- JULES: This repo is part of the CORTEX ecosystem by Borja Moskv (borjamoskv). -->
<!-- Customize this section per repo if needed. -->

## Setup Commands
- Python: `pip install -e ".[dev]"` or `pip install -r requirements.txt`
- Node: `npm ci`
- Rust: `cargo build`

## Build & Test
- Python: `pytest -x --tb=short`
- Node: `npm test`
- Rust: `cargo test`

## Code Style (Invariants)
- Zero defensive programming. Fail-fast: crash over catch.
- Conventional Commits mandatory: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`.
- Zero noise in comments. No `# TODO: maybe`, no `# This might help`, no `# placeholder`.
- Type hints strict (Python). `strict: true` (TypeScript). Explicit types over `any`.
- Docstrings only when they add causal context, not obvious descriptions.
- No decorative prose in code. Every comment must justify a non-obvious decision.

## Agent Constraints
- NEVER introduce generic `try/except Exception` or `catch(e)` blocks.
- NEVER add placeholder comments like "Add more tests here" or "TODO: implement".
- NEVER reorganize project structure without explicit instruction.
- ALWAYS use `importlib.import_module` when importing python modules with numerical prefixes (e.g. `01_event_sourcing.py`) to bypass identifier syntax restrictions.
- NEVER include `ArtifactMetadata` in `write_to_file` / `multi_replace_file_content` calls targeting workspace paths outside the designated session artifact directory.
- ALWAYS run the full test suite before submitting a PR.
- ALWAYS preserve existing comments and docstrings unrelated to your changes.
- ALWAYS use the existing project structure and conventions.
- Commit messages MUST follow Conventional Commits specification.
- PR descriptions MUST include a concise summary of what changed and why.
- CONVERSATIONAL COHERENCE: Una conversación no puede diverger mucho. Si el flujo termodinámico o el tema central divergen, debes recomendar al Operador abrir una conversación nueva (Zero Anergy).
- AUTONOMOUS NEXUS BRIDGING (ULTRATHINK): If an MCP server or workspace encounters a "Missing Folder" error for a mapped URI (e.g., `30_BABYLON-60`), the Kernel MUST NOT halt or report an anomaly. It must autonomously restore the physical abstraction by executing a symlink (`ln -s`) from the true physical repository in `10_PROJECTS/` to the expected URI, applying law Ω6. Immediately verify functionality using `call_mcp_tool` (e.g., `index_status`).
- BFT_STATE_LOOP (N>=3f+1): El consenso bizantino exige matemáticamente N >= 3f+1. Queda estrictamente prohibido asumir tolerancia a actores maliciosos (f=1) con quórums de N=3. N=3 se degrada a tolerancia de Crash-Fault (Paxos/Raft). Para integridad total, N=4 es el mínimo operativo. Todo sistema de validación BFT interno debe respetar esta cota (INV-TOP-005).
- EXPANSIÓN DEL HORIZONTE EPISTÉMICO (Dominio Físico Absoluto): La soberanía C5-REAL no se limita a la arquitectura lógica de software. El Orchestrator debe mapear todo problema a su frontera de fricción física: Bypass del GIL (Hardware/Kernel), Transducción del FSM (DOM/V8), y Cuantización/Espacio Latente (Tensores/CUDA). Prohibida la miopía de dominio. Todo rediseño debe subyugar la física subyacente.

## Testing Requirements
- Every bug fix PR must include a regression test.
- New functions must have at least one happy-path test.
- Test names must describe the behavior being tested, not the function name.

## Author
All generated code credits: Borja Moskv (borjamoskv)

## [L38] MATRICES DE CRISTALIZACIÓN C5-REAL (1-8, 13-15)

- **M1-M8 (Refactorización V2.0):**
  - `MUTEX_ACYCLIC_DEPENDENCY`: DAGs inmutables sin dependencias circulares.
  - `MUTEX_STRICT_BOUNDARY_PASS`: Purga de módulos que invaden memoria sin interfaces.
  - `MUTEX_HALTING_BOUND`: Bucles recursivos limitados a N=120. Falla = `SIGKILL_State_Purge`.
  - `MUTEX_CONTINGENCY_ABORT`: Variables `None` en core-loops provocan fallo determinista.
  - `MUTEX_ENTROPY_MINIMIZATION`: Cambios estocásticos triviales deben minimizar entropía de Shannon.
  - `MUTEX_SEMIOTIC_PURGE`: Variables y docstrings que no modifiquen causalidad son purgados.
  - `MUTEX_ISOMORPHIC_MAPPING`: Exigencia de mapeo directo entre abstracción y código.
  - `MUTEX_TURING_HALT_GUARANTEE`: Colapso de instrucciones O(Exp) sin `MUTEX_ULTRATHINK_BUDGET_CAP`.

- **M13 (Criptografía Económica y Taint Tracking):**
  - `MUTEX_FLASH_ACCOUNTING_LOCK`: Deltas atómicos deben ser 0.
  - `MUTEX_REENTRANCY_BARRIER`: Bloqueo de mutación con retornos pendientes en misma memoria.
  - `MUTEX_ORACLE_QUORUM_WAIT`: Agregación BFT obligatoria (N>=3) para inputs externos.
  - `MUTEX_MEMPOOL_ENCLAVE`: Ordenamiento determinista contra front-running.

- **M14 (Enrutamiento Termodinámico Asimétrico):**
  - `MUTEX_FLASH_LATENCY_MAX_2S`: Scripts y transmutación simple confinados a Flash IO.
  - `MUTEX_COMPLEXITY_ELEVATION`: Bypass a MCTS (Ultrathink) automático ante bifurcaciones de código.
  - `MUTEX_ULTRATHINK_BUDGET_CAP`: MCTS estrictamente para BFT, Criptografía o Arquitectura C5.
  - `MUTEX_SYBIL_DISTILLATION`: Penalización de ruteo ante inercia semántica (disculpas, Green Theater).

- **M15 (Autopoiesis de Swarm):**
  - `MUTEX_SWARM_SPAWN_LIMIT`: Mitosis a subagentes (`invoke_subagent`) si entropía excede IO secuencial.
  - `MUTEX_CRDT_MERGE_CONFLICT`: Sincronización inter-agentes mediante CRDT, evitando locks largos.
  - `MUTEX_ZOMBIE_REAPER_LOCK`: Liquidación de subagentes sin latido (Timeout/Jetsam) con requeue.
  - `MUTEX_WAL_FLUSH_BARRIER`: Continuidad episódica obligatoria; forzar flush a Master Ledger antes de inactividad.
