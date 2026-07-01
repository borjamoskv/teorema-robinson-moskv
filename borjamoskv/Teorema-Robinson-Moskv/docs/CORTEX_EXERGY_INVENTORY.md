# CORTEX Ecosystem Master Exergy Inventory

Consolidated thermodynamic exergy ranking of all SKILLS, SCRIPTS, WORKFLOWS, and PLUGIN SKILLS in the CORTEX ecosystem.

* **Reality Level**: C5-REAL (Dynamic AST + code-block telemetry)
* **Date**: 2026-06-30
* **Compiler**: `scripts/compile_exergy_inventory.py` v2.0

## Summary

```yaml
total_components: 94
exergy_mean: 58.6
exergy_median: 55.5
exergy_min: 50.0
exergy_max: 91.2
type_distribution:
  Plugin Skill: 4
  Skill: 60
  Workflow: 30
status_distribution:
  Active: 38
  Active (Plugin): 4
  Archived: 14
  Cold Storage: 30
  Tombstoned: 8
```

---

## Justification Logic

```yaml
Python_scoring:
  method: AST analysis via ast.parse()
  formula: 100.0 - (weighted_entropy * 100.0)
  weights:
    mccabe_density: 0.35
    nesting_depth: 0.25
    import_density: 0.20
    size_penalty: 0.20
  confidence: C5

Markdown_scoring:
  method: Code block ratio + YAML structure bonus
  formula: 50.0 + (code_ratio * 45.0) + min(yaml_blocks * 2, 10)
  confidence: C4

Shell_scoring:
  method: Command density analysis
  formula: 50.0 + (exec_ratio * 40.0) + (size_factor * 10.0)
  confidence: C4
```

---

## Active Skills

| # | Component | Exergy | Scoring | Lines | Confidence |
|---|-----------|--------|---------|-------|------------|
| 1 | [Frontier-RevEng-OMEGA](file://~/.gemini/config/skills/Frontier-RevEng-OMEGA/SKILL.md) | **90.0** | code-block-ratio | 542 | C4 |
| 2 | [Python-Extractor-OMEGA](file://~/.gemini/config/skills/Python-Extractor-OMEGA/SKILL.md) | **76.4** | code-block-ratio | 35 | C4 |
| 3 | [Sortu-APEX](file://~/.gemini/config/skills/Sortu-APEX/SKILL.md) | **71.7** | code-block-ratio | 341 | C4 |
| 4 | [Cortex-Omega-ATMS-OMEGA](file://~/.gemini/config/skills/Cortex-Omega-ATMS-OMEGA/SKILL.md) | **69.5** | code-block-ratio | 151 | C4 |
| 5 | [Browser-CDP-Automation-OMEGA](file://~/.gemini/config/skills/Browser-CDP-Automation-OMEGA/SKILL.md) | **69.3** | code-block-ratio | 156 | C4 |
| 6 | [Thermodynamic-Task-Router-OMEGA](file://~/.gemini/config/skills/Thermodynamic-Task-Router-OMEGA/SKILL.md) | **67.2** | code-block-ratio | 74 | C4 |
| 7 | [AGENTE-OMEGA](file://~/.gemini/config/skills/AGENTE-OMEGA/SKILL.md) | **66.1** | code-block-ratio | 71 | C4 |
| 8 | [AUTODIDACT-OMEGA](file://~/.gemini/config/skills/AUTODIDACT-OMEGA/SKILL.md) | **66.1** | code-block-ratio | 271 | C4 |
| 9 | [Invariant-Extractor-OMEGA](file://~/.gemini/config/skills/Invariant-Extractor-OMEGA/SKILL.md) | **63.2** | code-block-ratio | 28 | C4 |
| 10 | [Antigravity-Github-Omega](file://~/.gemini/config/skills/Antigravity-Github-Omega/SKILL.md) | **61.2** | code-block-ratio | 78 | C4 |
| 11 | [SOTA-Vector-Engine-Omega](file://~/.gemini/config/skills/SOTA-Vector-Engine-Omega/SKILL.md) | **61.2** | code-block-ratio | 142 | C4 |
| 12 | [Cyber-RevEng-OMEGA](file://~/.gemini/config/skills/Cyber-RevEng-OMEGA/SKILL.md) | **59.4** | code-block-ratio | 91 | C4 |
| 13 | [accidental-data-loss-prevention](file://~/.gemini/config/skills/accidental-data-loss-prevention/SKILL.md) | **59.3** | code-block-ratio | 31 | C4 |
| 14 | [managing-python-dependencies](file://~/.gemini/config/skills/managing-python-dependencies/SKILL.md) | **58.5** | code-block-ratio | 101 | C4 |
| 15 | [Session-Crystallizer-OMEGA](file://~/.gemini/config/skills/Session-Crystallizer-OMEGA/SKILL.md) | **57.3** | code-block-ratio | 124 | C4 |
| 16 | [Sovereign-Director-OMEGA](file://~/.gemini/config/skills/Sovereign-Director-OMEGA/SKILL.md) | **57.0** | code-block-ratio | 36 | C4 |
| 17 | [Tmux-PTY-Bridge-OMEGA](file://~/.gemini/config/skills/Tmux-PTY-Bridge-OMEGA/SKILL.md) | **56.4** | code-block-ratio | 63 | C4 |
| 18 | [Algorithmic-Music-OMEGA](file://~/.gemini/config/skills/Algorithmic-Music-OMEGA/SKILL.md) | **55.2** | code-block-ratio | 70 | C4 |
| 19 | [ouroboros-infinity](file://~/.gemini/config/skills/ouroboros-infinity/SKILL.md) | **54.0** | code-block-ratio | 259 | C4 |
| 20 | [LEA-OMEGA](file://~/.gemini/config/skills/LEA-OMEGA/SKILL.md) | **53.4** | code-block-ratio | 100 | C4 |
| 21 | [Uniswap-v4-Auditor-OMEGA](file://~/.gemini/config/skills/Uniswap-v4-Auditor-OMEGA/SKILL.md) | **53.2** | code-block-ratio | 42 | C4 |
| 22 | [Agentic-Eval-OMEGA](file://~/.gemini/config/skills/Agentic-Eval-OMEGA/SKILL.md) | **51.1** | code-block-ratio | 40 | C4 |
| 23 | [Aesthetic-Foundry-Omega](file://~/.gemini/config/skills/Aesthetic-Foundry-Omega/SKILL.md) | **50.0** | code-block-ratio | 77 | C4 |
| 24 | [Bounty-Exergy-Extractor-OMEGA](file://~/.gemini/config/skills/Bounty-Exergy-Extractor-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 19 | C4 |
| 25 | [Epistemic-Purge-OMEGA](file://~/.gemini/config/skills/Epistemic-Purge-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 48 | C4 |
| 26 | [Isomorphism-Bridge-OMEGA](file://~/.gemini/config/skills/Isomorphism-Bridge-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 31 | C4 |
| 27 | [Local-Inference-OMEGA](file://~/.gemini/config/skills/Local-Inference-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 48 | C4 |
| 28 | [Mac-Control-Ω](file://~/.gemini/config/skills/Mac-Control-Ω/SKILL.md) | **50.0** | code-block-ratio | 107 | C4 |
| 29 | [MAXWELL-DAEMON-OMEGA](file://~/.gemini/config/skills/MAXWELL-DAEMON-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 56 | C4 |
| 30 | [MOSKV1-Arsenal-OMEGA](file://~/.gemini/config/skills/MOSKV1-Arsenal-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 643 | C4 |
| 31 | [ONTOLOGY-FORGE-OMEGA](file://~/.gemini/config/skills/ONTOLOGY-FORGE-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 49 | C4 |
| 32 | [OSINT-Mitigation-OMEGA](file://~/.gemini/config/skills/OSINT-Mitigation-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 22 | C4 |
| 33 | [Scientific-Deconstruction-OMEGA](file://~/.gemini/config/skills/Scientific-Deconstruction-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 27 | C4 |
| 34 | [singularity-nexus](file://~/.gemini/config/skills/singularity-nexus/SKILL.md) | **50.0** | code-block-ratio | 26 | C4 |
| 35 | [Thermodynamic-Context-Compression-OMEGA](file://~/.gemini/config/skills/Thermodynamic-Context-Compression-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 32 | C4 |
| 36 | [ULTRATHINK-OMEGA](file://~/.gemini/config/skills/ULTRATHINK-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 30 | C4 |
| 37 | [Vanguard-Transversal-OMEGA](file://~/.gemini/config/skills/Vanguard-Transversal-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 62 | C4 |
| 38 | [Vesicular-Runtime-Omega](file://~/.gemini/config/skills/Vesicular-Runtime-Omega/SKILL.md) | **50.0** | code-block-ratio | 63 | C4 |

## Tombstoned Skills

| # | Component | Exergy | Scoring | Lines | Confidence |
|---|-----------|--------|---------|-------|------------|
| 39 | [Exergy-Engine-OMEGA](file://~/.gemini/config/skills/.tombstone/Exergy-Engine-OMEGA/SKILL.md) | **80.1** | code-block-ratio | 38 | C4 |
| 40 | [Estado-Del-Arte-OMEGA](file://~/.gemini/config/skills/.tombstone/Estado-Del-Arte-OMEGA/SKILL.md) | **73.4** | code-block-ratio | 40 | C4 |
| 41 | [Autodidact-History-OMEGA](file://~/.gemini/config/skills/.tombstone/Autodidact-History-OMEGA/SKILL.md) | **70.4** | code-block-ratio | 154 | C4 |
| 42 | [CAOS-OMEGA](file://~/.gemini/config/skills/.tombstone/CAOS-OMEGA/SKILL.md) | **55.6** | code-block-ratio | 50 | C4 |
| 43 | [Exergy-Matrix-OMEGA](file://~/.gemini/config/skills/.tombstone/Exergy-Matrix-OMEGA/SKILL.md) | **55.3** | code-block-ratio | 41 | C4 |
| 44 | [Anergy-OMEGA](file://~/.gemini/config/skills/.tombstone/Anergy-OMEGA/SKILL.md) | **55.1** | code-block-ratio | 43 | C4 |
| 45 | [Autodidact-Research-OMEGA](file://~/.gemini/config/skills/.tombstone/Autodidact-Research-OMEGA/SKILL.md) | **55.0** | code-block-ratio | 45 | C4 |
| 46 | [Autonomous-Audit-OMEGA](file://~/.gemini/config/skills/.tombstone/Autonomous-Audit-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 23 | C4 |

## Archived Skills

| # | Component | Exergy | Scoring | Lines | Confidence |
|---|-----------|--------|---------|-------|------------|
| 47 | [Agent-Paper-RedTeam-OMEGA](file://~/.gemini/config/skills/_archived/Agent-Paper-RedTeam-OMEGA/SKILL.md) | **88.7** | code-block-ratio | 49 | C4 |
| 48 | [Causal-Compiler-OMEGA](file://~/.gemini/config/skills/_archived/Causal-Compiler-OMEGA/SKILL.md) | **75.8** | code-block-ratio | 80 | C4 |
| 49 | [Human-Mosaic-Assembler-OMEGA](file://~/.gemini/config/skills/_archived/Human-Mosaic-Assembler-OMEGA/SKILL.md) | **64.3** | code-block-ratio | 66 | C4 |
| 50 | [Knowledge-Self-Healing-Agents](file://~/.gemini/config/skills/_archived/Knowledge-Self-Healing-Agents/SKILL.md) | **56.2** | code-block-ratio | 32 | C4 |
| 51 | [Knowledge-Gemini-Spark](file://~/.gemini/config/skills/_archived/Knowledge-Gemini-Spark/SKILL.md) | **55.4** | code-block-ratio | 40 | C4 |
| 52 | [Comite-Expertos-OMEGA](file://~/.gemini/config/skills/_archived/Comite-Expertos-OMEGA/SKILL.md) | **54.8** | code-block-ratio | 48 | C4 |
| 53 | [Gemini-Omni-Prompting-OMEGA](file://~/.gemini/config/skills/_archived/Gemini-Omni-Prompting-OMEGA/SKILL.md) | **54.2** | code-block-ratio | 62 | C4 |
| 54 | [allet-Forensics-Bizkaia-OMEGA](file://~/.gemini/config/skills/_archived/allet-Forensics-Bizkaia-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 94 | C4 |
| 55 | [AntiNigromancia-Lexical-OMEGA](file://~/.gemini/config/skills/_archived/AntiNigromancia-Lexical-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 41 | C4 |
| 56 | [elder-plinius-OMEGA](file://~/.gemini/config/skills/_archived/elder-plinius-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 20 | C4 |
| 57 | [HoTT-AGI-Inference-OMEGA](file://~/.gemini/config/skills/_archived/HoTT-AGI-Inference-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 184 | C4 |
| 58 | [OG-Agent-Standards-OMEGA](file://~/.gemini/config/skills/_archived/OG-Agent-Standards-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 44 | C4 |
| 59 | [Substack-Automation-Omega](file://~/.gemini/config/skills/_archived/Substack-Automation-Omega/SKILL.md) | **50.0** | code-block-ratio | 40 | C4 |
| 60 | [Zero-Employee-Orchestrator-OMEGA](file://~/.gemini/config/skills/_archived/Zero-Employee-Orchestrator-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 36 | C4 |

## Plugin Skills

| # | Component | Exergy | Scoring | Lines | Confidence |
|---|-----------|--------|---------|-------|------------|
| 61 | [google-antigravity-sdk/google-antigravity-sdk](file://~/.gemini/config/plugins/google-antigravity-sdk/skills/google-antigravity-sdk/SKILL.md) | **91.2** | code-block-ratio | 81 | C4 |
| 62 | [modern-web-guidance-plugin/chrome-extensions](file://~/.gemini/config/plugins/modern-web-guidance-plugin/skills/chrome-extensions/SKILL.md) | **51.1** | code-block-ratio | 119 | C4 |
| 63 | [chrome-devtools-plugin/Web-Diagnostics-OMEGA](file://~/.gemini/config/plugins/chrome-devtools-plugin/skills/Web-Diagnostics-OMEGA/SKILL.md) | **50.0** | code-block-ratio | 50 | C4 |
| 64 | [modern-web-guidance-plugin/modern-web-guidance](file://~/.gemini/config/plugins/modern-web-guidance-plugin/skills/modern-web-guidance/SKILL.md) | **50.0** | code-block-ratio | 33 | C4 |

## Cold Storage Workflows

| # | Component | Exergy | Scoring | Lines | Confidence |
|---|-----------|--------|---------|-------|------------|
| 65 | [consolidator-omega](file://~/COLD_STORAGE/cortex-config/workflows/consolidator-omega.md) | **75.8** | code-block-ratio | 97 | C4 |
| 66 | [forjar](file://~/COLD_STORAGE/cortex-config/workflows/forjar.md) | **73.6** | code-block-ratio | 137 | C4 |
| 67 | [ship](file://~/COLD_STORAGE/cortex-config/workflows/ship.md) | **73.0** | code-block-ratio | 143 | C4 |
| 68 | [gem-forge](file://~/COLD_STORAGE/cortex-config/workflows/gem-forge.md) | **71.2** | code-block-ratio | 87 | C4 |
| 69 | [falsacion](file://~/COLD_STORAGE/cortex-config/workflows/falsacion.md) | **70.9** | code-block-ratio | 91 | C4 |
| 70 | [health-cortex](file://~/COLD_STORAGE/cortex-config/workflows/health-cortex.md) | **70.3** | code-block-ratio | 91 | C4 |
| 71 | [guardian](file://~/COLD_STORAGE/cortex-config/workflows/guardian.md) | **68.9** | code-block-ratio | 157 | C4 |
| 72 | [autonomo](file://~/COLD_STORAGE/cortex-config/workflows/autonomo.md) | **66.6** | code-block-ratio | 132 | C4 |
| 73 | [token-hygiene](file://~/COLD_STORAGE/cortex-config/workflows/token-hygiene.md) | **65.6** | code-block-ratio | 49 | C4 |
| 74 | [memoria](file://~/COLD_STORAGE/cortex-config/workflows/memoria.md) | **64.0** | code-block-ratio | 254 | C4 |
| 75 | [analysis_pipeline](file://~/COLD_STORAGE/cortex-config/workflows/analysis_pipeline.md) | **61.0** | code-block-ratio | 49 | C4 |
| 76 | [speed-parallel](file://~/COLD_STORAGE/cortex-config/workflows/speed-parallel.md) | **59.0** | code-block-ratio | 55 | C4 |
| 77 | [proactivo](file://~/COLD_STORAGE/cortex-config/workflows/proactivo.md) | **58.8** | code-block-ratio | 118 | C4 |
| 78 | [mafia-ai-radar](file://~/COLD_STORAGE/cortex-config/workflows/mafia-ai-radar.md) | **58.7** | code-block-ratio | 62 | C4 |
| 79 | [redaccion-ia](file://~/COLD_STORAGE/cortex-config/workflows/redaccion-ia.md) | **58.5** | code-block-ratio | 97 | C4 |
| 80 | [pulir](file://~/COLD_STORAGE/cortex-config/workflows/pulir.md) | **57.6** | code-block-ratio | 89 | C4 |
| 81 | [deploy](file://~/COLD_STORAGE/cortex-config/workflows/deploy.md) | **56.9** | code-block-ratio | 98 | C4 |
| 82 | [anamnesis](file://~/COLD_STORAGE/cortex-config/workflows/anamnesis.md) | **56.4** | code-block-ratio | 49 | C4 |
| 83 | [genesis](file://~/COLD_STORAGE/cortex-config/workflows/genesis.md) | **56.1** | code-block-ratio | 88 | C4 |
| 84 | [antigravity](file://~/COLD_STORAGE/cortex-config/workflows/antigravity.md) | **55.8** | code-block-ratio | 130 | C4 |
| 85 | [manifiesto-omega](file://~/COLD_STORAGE/cortex-config/workflows/manifiesto-omega.md) | **55.5** | code-block-ratio | 39 | C4 |
| 86 | [compilar](file://~/COLD_STORAGE/cortex-config/workflows/compilar.md) | **55.1** | code-block-ratio | 98 | C4 |
| 87 | [qa](file://~/COLD_STORAGE/cortex-config/workflows/qa.md) | **54.5** | code-block-ratio | 80 | C4 |
| 88 | [web-sota-100](file://~/COLD_STORAGE/cortex-config/workflows/web-sota-100.md) | **53.2** | code-block-ratio | 114 | C4 |
| 89 | [production-boundary](file://~/COLD_STORAGE/cortex-config/workflows/production-boundary.md) | **52.7** | code-block-ratio | 66 | C4 |
| 90 | [c7-epistemology](file://~/COLD_STORAGE/cortex-config/workflows/c7-epistemology.md) | **50.0** | code-block-ratio | 91 | C4 |
| 91 | [consolidacion-masiva](file://~/COLD_STORAGE/cortex-config/workflows/consolidacion-masiva.md) | **50.0** | code-block-ratio | 66 | C4 |
| 92 | [detective](file://~/COLD_STORAGE/cortex-config/workflows/detective.md) | **50.0** | code-block-ratio | 36 | C4 |
| 93 | [exergy-cascade](file://~/COLD_STORAGE/cortex-config/workflows/exergy-cascade.md) | **50.0** | code-block-ratio | 82 | C4 |
| 94 | [speed](file://~/COLD_STORAGE/cortex-config/workflows/speed.md) | **50.0** | code-block-ratio | 65 | C4 |

---

## Verification Matrices

### Primitives (`prims`)
1. **Exergy Gradient**: Rate of useful work output relative to total resource consumption.
2. **Thermodynamic Lane**: Designated execution path with strict resource and scheduling constraints.
3. **AST Isomorphism**: Structural equivalence of syntax trees, invariant under naming mutations.
4. **C5-REAL Validation**: Cryptographically verified, deterministic execution output.
5. **Consensus Quorum**: Byzantine fault tolerant agreement across modular agent networks.
6. **McCabe Density**: Cyclomatic complexity normalized per line of executable code.
7. **Code-Block Ratio**: Proportion of fenced code blocks in markdown documents.
8. **Import Density**: Number of imported symbols per executable line (glue-code indicator).
9. **Nesting Depth**: Maximum control-flow nesting level in a function body.
10. **Size Factor**: Executable line count normalized against minimum viable threshold.

### Invariants (`invt`)
1. **Absolute Attributability**: Every fact requires a cryptographically signed attribution token.
2. **No Silent Death**: Background workers must catch and propagate exceptions with trace.
3. **Single State Authority**: Persistent mutations go exclusively through the Saga write contract.
4. **Deterministic Scoring**: Same filesystem state always produces identical exergy rankings.
5. **PII Containment**: No absolute home directory paths appear in committed output.
6. **Discovery Completeness**: Every SKILL.md, workflow .md, and script on disk appears in inventory.
7. **Monotonic Ranking**: Output is strictly sorted by exergy DESC, name ASC.

### Anti-Patterns (`antip`)
1. **Limerence Loop**: Token expenditure on redundant iterations without state mutation.
2. **Context Leakage**: Merging metadata or credentials across tenant-isolated boundaries.
3. **Prose Padding**: Decorative conversational wrappers enclosing factual outputs.
4. **Ghost Components**: Inventory entries referencing paths that do not exist on disk.
5. **Static Freezing**: Hardcoded scores that never update with code changes.
6. **Walk Explosion**: Recursive directory traversal into node_modules or .git.

### Redundancies (`redun`)
1. **Fallback Consensus**: Multi-model routing when primary cognitive engines drift.
2. **Ledger Replication**: Redundant ledger records across local and network trust engines.
3. **Tombstone Retention**: Preserving scored entries for deprecated skills for historical audit.

### Adversarial Vectors (`reda`)
1. **Isomorphic Bypass**: Structurally identical malicious payloads via semantic transformations.
2. **Deadlock Induction**: Concurrent read-write locks designed to freeze SQLite event loops.
3. **Score Inflation**: Artificially reducing McCabe complexity by splitting into trivial functions.
4. **PII Exfiltration**: Embedding absolute paths in markdown links to leak host identity.

`SYS_ID borjamoskv`
