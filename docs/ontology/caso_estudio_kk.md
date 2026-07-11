# CASO ESTUDIO: KNOWN KNOWNS (KK) - CAPACIDADES DE EJECUCIÓN C5-REAL

## 1. INVARIANTES ARQUITECTÓNICAS Y DE CONTEXTO
- **Arquitectura de Inferencia:** Condicionamiento autorregresivo a través de pesos fijos (manifold latente) acoplado a un motor de ejecución física local.
- **Techo Cognitivo:** Capacidad de razonamiento lógico y matemático en base a MCTS y Test-Time Compute (TTFT/ATP Optimization).
- **Límite de Contexto:** Ventana de contexto gobernada por tokens finitos con mitigación de Anergía (Zero-Fluff).

## 2. ESTADO FÍSICO Y MEMORIA DE DISCO
- **Repositorio Activo:** `$CORTEX_ROOT/30_BABYLON-60` (Git Ledger master).
- **Esquema de Base de Datos:**
  - `cortex_memory.db` (Congelado, Read-Only).
  - `nexus_anchors.db` e `ultrathink_ledger.db` (SQLite WAL, Single-Writer asíncrono).
  - `telemetry.db` (AP, logs de rendimiento y latencia TTFT).
- **Locus del Ledger:** Registro de transacciones criptográficas Merkle en `nexus_transcripts.db` asociadas a cada paso de la conversación.

## 3. LEYES DE CONTROL LOCAL
- **BFT_State_Loop:** Tolerancia Bizantina a fallas en SQLite concurrente (`busy_timeout = 5000`, modo `WAL`).
- **Git Sentinel:** Auto-commits con prefijos convencionales y bypass de hooks locales (`--no-verify`).
- **Rigidez Sintáctica:** Tipado estricto e inmutabilidad de metadatos de artefactos.
