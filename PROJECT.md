# Project: BABYLON-60

## Architecture
- **Ecosystem**: CORTEX Ecosystem by Borja Moskv, a C5-REAL execution kernel.
- **Components**:
  - `cortex/`: Core agents and ontology configuration.
  - `bft/`: Byzantine Fault Tolerance ledger files and synchronization.
  - `strike_rs/`: Rust core library for GIL bypass and exergy extraction.
  - `cortex_memory.db`: Master ledger database storing transactional and causal state.
  - `cortex_surface_map.db`: Key-value map database for spatial/agent representation.
  - `telemetry.db`: Performance and state telemetry logger database.
  - `README.md`: Entrypoint document summarizing architecture, setup, and usage.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Git Log Audit | Audit git history since Feb 2026, compile undocumented items into YAML. | None | IN_PROGRESS (2c051482-de1a-4006-8a53-1426294a3415) |
| 2 | M2: GitHub SOTA Eval | Inspect local GitHub setup, verify CI/CD gaps, compile markdown report. | None | IN_PROGRESS (2c051482-de1a-4006-8a53-1426294a3415) |
| 3 | M3: README Refactoring | Rewrite README.md in Industrial Noir 2026 aesthetic with ASCII dividers `█▄`. | None | PLANNED |
| 4 | M4: Git Sentinel Anchoring | Commit all changes under Git Sentinel to seal the ledger state. | M1, M2, M3 | PLANNED |

## Interface Contracts
- **Git Log format** ↔ **YAML parser**: Extract commit hashes, authors, dates, and message bodies. Output to `cortex/audits/hitos_no_remarcados.yaml` in YAML format.
- **GitHub directory** ↔ **SOTA standards**: Evaluate presence of workflows, branching rules, PR templates, and issue templates. Output to `cortex/audits/github_sota_eval.md`.
- **README.md** ↔ **Industrial Noir 2026**: Replaced entirely with C5-REAL styling, ASCII dividers, and no conversational prose.
