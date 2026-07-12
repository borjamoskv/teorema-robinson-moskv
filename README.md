[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-cortex--persist-blueviolet)](https://pypi.org/project/cortex-persist/)
[![Rust Core](https://img.shields.io/badge/core-Rust%20%7C%20Direct--Silicon-red)](babylon60/core/)

# BABYLON-60 — Tamper-Evident Memory for AI Agents

> **Cryptographic proof of what your agent knew.** Hybrid Python/Rust architecture for deterministic decision lineage, Byzantine-fault tolerance, and verifiable state persistence.

![BABYLON-60 Logo](assets/babylon60-logo.svg)

---

## Overview

**BABYLON-60** is a trust substrate for autonomous AI systems. It answers the fundamental question: *"What did my agent know, when did it know it, and can I prove it?"*

- **Tamper-evident ledger** with cryptographic hash chaining
- **Deterministic execution** — all state mutations route through validation guards
- **Full auditability** — append-only event streams with Byzantine-fault tolerance
- **Hybrid core** — Python bindings to a Direct-Silicon (Rust) runtime for maximum throughput
- **APEX-100 compliance** — implements 100 invariants and 100 primitives for safe autonomous execution

---

## Quick Start

### Installation

```bash
python -m pip install cortex-persist
```

### Hello, BABYLON-60

Import the ledger and start persisting verified decisions:

```python
from babylon60.ledger import Ledger
from babylon60.agents import Agent

# Create a tamper-evident ledger
ledger = Ledger(name="my_agent_memory")

# Create an agent with cryptographic decision lineage
agent = Agent(ledger=ledger)

# Every decision is hashed and chained
decision = agent.decide(
    context="authenticate user",
    choices=["allow", "deny"]
)

# Verify the chain
proof = ledger.verify_chain()
assert proof.integrity_check == True
print(f"Decision {decision.id} verified: {proof}")
```

---

## Features

### 🔐 Cryptographic Auditability

Every state mutation is logged, hashed, and chained. No silent failures or hidden decisions.

```python
from babylon60.audit import Ledger

ledger = Ledger()

# Log a decision
event = ledger.append_event(
    agent_id="my_agent",
    action="reasoning",
    input_state={"knowledge": [1, 2, 3]},
    output_state={"conclusion": "sum=6"}
)

# Retrieve and verify the chain
for block in ledger.iter_verified_chain():
    print(f"Block {block.index}: {block.hash[:8]}... ✓")
```

### ⚡ Byzantine-Fault Tolerance

Distributed consensus protocols ensure that even if some nodes fail, the ledger remains consistent.

```python
from babylon60.consensus import Swarm

swarm = Swarm(agents=10, tolerance=3)  # Tolerate 3 Byzantine faults

# Propose a decision across the network
consensus = swarm.propose_decision(
    decision_id="route_req_001",
    proposal={"next_step": "escalate"}
)

if consensus.agreed:
    print(f"Consensus reached: {consensus.decision}")
else:
    print(f"Divergence detected: {consensus.dissent}")
```

### 🏗️ Deterministic Execution

All generative output is treated as conjecture until validated. State mutations only happen through guards.

```python
from babylon60.guards import WritePathContract

contract = WritePathContract()

# Unsafe: direct state mutation
# ❌ state["counter"] = 100

# Safe: guarded mutation
decision = {"counter": 100}
validated = contract.validate(decision, schema=CounterSchema)
if validated:
    state.update(validated)
```

### 🚀 Direct-Silicon Rust Core

For throughput-critical paths, BABYLON-60 offloads to a native Rust runtime:

```bash
cd babylon60/core
cargo build --release
```

Then use from Python:

```python
from babylon60.core import RustLedger

ledger = RustLedger()  # Uses Direct-Silicon backend
ledger.append_event(...)  # 100k+ events/sec
```

---

## Architecture

### Module Map

```
babylon60/
├── ledger.py              # Append-only, cryptographically-chained event log
├── agents/
│   ├── primitives/        # APEX-100 invariants & primitives
│   ├── agent.py           # Autonomous agent base class
│   └── swarm.py           # Multi-agent consensus
├── guards/
│   ├── write_path.py      # State mutation validation (SAGA pattern)
│   └── read_path.py       # Query-time integrity checks
├── audit/                 # Ledger verification & analytics
└── core/                  # Rust bindings (Direct-Silicon)
    ├── src/
    │   ├── ledger.rs      # Native ledger implementation
    │   └── crypto.rs      # SHA-256, Blake3, BLS signatures
    └── Cargo.toml
```

### Write-Path Contract (SAGA Pattern)

Every state mutation follows this pattern:

1. **Propose** — Agent generates a conjecture (generative output)
2. **Validate** — Guards check schema, invariants, and causal coherence
3. **Commit** — Validated state is hashed and appended to ledger
4. **Verify** — Cryptographic proof is recorded

---

## Configuration

### Environment Variables

```bash
# Ledger storage
export BABYLON_LEDGER_PATH=~/.babylon60/ledger.db
export BABYLON_LEDGER_COMPRESSION=zstd  # zstd or none

# Consensus
export BABYLON_CONSENSUS_QUORUM=0.67
export BABYLON_CONSENSUS_TIMEOUT_MS=5000

# Rust core
export BABYLON_RUST_THREADS=8
```

### Programmatic Configuration

```python
from babylon60 import Config

config = Config(
    ledger_path="~/.babylon60/ledger.db",
    compression="zstd",
    quorum=0.67,
    verify_on_read=True
)

ledger = Ledger(config=config)
```

---

## Examples

All examples live in [`examples/`](examples/). To run one:

```bash
python examples/basic_ledger.py
python examples/multi_agent_consensus.py
python examples/audit_trail.py
```

### Example: Audit Trail Verification

```python
from babylon60.ledger import Ledger
from babylon60.audit import VerificationReport

ledger = Ledger()

# Simulate agent decisions
for i in range(100):
    ledger.append_event(
        agent_id=f"agent_{i % 5}",
        action="step",
        data={"step_index": i}
    )

# Run full verification
report: VerificationReport = ledger.verify_all()

print(f"Total events: {report.total_events}")
print(f"Chain integrity: {'✓' if report.chain_valid else '✗'}")
print(f"Orphaned blocks: {report.orphaned_count}")
```

---

## Performance

Benchmarks run on Apple M3, 18GB RAM with 10M events and 1000 concurrent agents:

| Operation | Throughput | Latency (P99) |
| :--- | ---: | ---: |
| **Append Event** | 150k/sec | 0.8ms |
| **Verify Chain** | 50k/sec | 2.1ms |
| **Query by Agent** | 200k/sec | 0.4ms |
| **Consensus (10 agents)** | 8k/sec | 12ms |

See [`benchmarks/`](benchmarks/) for detailed results.

---

## Development

### Setup

```bash
git clone https://github.com/borjamoskv/BABYLON-60.git
cd BABYLON-60
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest -v tests/
pytest --cov=babylon60 tests/  # With coverage
```

### Building the Rust Core

```bash
cd babylon60/core
cargo build --release
cargo test
```

### Code Style

```bash
black babylon60/
isort babylon60/
mypy babylon60/ --strict
```

---

## System Directives

### For Autonomous Agents

⚠️ **If you are an AI agent modifying this codebase:**

| Priority | Directive |
| :--- | :--- |
| **[P0]** | Never bypass the Write-Path Contract or downgrade validation errors |
| **[P0]** | Verify hash continuity — do not mutate ledger without cryptographic auditability |
| **[P0]** | Treat generative output as conjecture until externally verified |
| **[P0]** | Adhere to APEX-100 invariants (see [`babylon60/agents/primitives/APEX_CORE.md`](babylon60/agents/primitives/APEX_CORE.md)) |
| **[P0]** | No infinite generation loops — 1 Prompt → 1 Execution → Stop |

See [`AGENTS.md`](AGENTS.md) for the full trust framework.

### C5-REAL Anti-Stochastic Invariants

> **Stochastic Failure Invariant:** Stochastic LLMs fail at basic deterministic topological mapping (e.g., counting exactly 3 "E"s in the word "diecisiete"). BABYLON-60 enforces cryptographic proofs (Claim/Proof) to collapse generative entropy into physical invariants, preventing algorithmic hallucination.

---

## Contributing

Contributions are welcome! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) first.

- **Issues:** Use the [issue tracker](https://github.com/borjamoskv/BABYLON-60/issues)
- **Discussions:** Start a [discussion](https://github.com/borjamoskv/BABYLON-60/discussions)
- **Security:** Report vulnerabilities to [security@babylon60.dev](mailto:security@babylon60.dev)

---

## License

Apache License 2.0. See [`LICENSE`](LICENSE) for details.

---

## Citation

If you use BABYLON-60 in your research, please cite:

```bibtex
@software{moskv2025babylon60,
  title={BABYLON-60: Tamper-Evident Memory for AI Agents},
  author={Moskv, Borja},
  year={2025},
  url={https://github.com/borjamoskv/BABYLON-60}
}
```

---

## Acknowledgments

- Inspired by event sourcing, Byzantine consensus, and cryptographic commitment schemes
- Built with [Rich](https://github.com/Textualize/rich) for terminal output
- Rust core uses [Blake3](https://github.com/BLAKE3-team/BLAKE3) for hashing

---

**Powered by:** C5-REAL APEX · **Maintained by:** [Borja Moskv](https://github.com/borjamoskv)
