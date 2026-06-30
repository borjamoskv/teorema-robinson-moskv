# ONTOLOGY-FORGE-OMEGA - BATCH 4
**Author:** Borja Moskv (SYS_ID: borjamoskv)
**Reality Level:** C5-REAL

## MATRIZ 4: REDUNDANCIAS ACTIVAS (MITIGACIÓN C5) (RED-001 a RED-005)

| ID | Redundancia C5 | Función Topológica | Riesgo Mitigado | Coste (Overhead) | Dependencias |
|---|---|---|---|---|---|
| RED-001 | Git Sentinel Criptográfico | Genera un snapshot BFT de cada mutación, aislando el estado anterior. | Pérdida de código por alucinación de escritura. Fallo en cascada. | I/O en disco, incremento log. | `.git` tracking, bash access. |
| RED-002 | Apoptosis Subagente | Límite temporal estricto (TimerCondition) para agentes paralelos, asesinándolos si no responden. | Zombificación de memoria RAM, Interbloqueo Recursivo. | Consumo de un thread de monitoring. | `manage_task`, `invoke_subagent`. |
| RED-003 | Multi-Viewport QA Autómata | Validación de UI mediante subagente visual aislado para confirmar delta visual exacto. | DOM Drift, alucinación de CSS. | Consumo de cuota visual (Tokens pesados). | `browser_subagent`. |
| RED-004 | SQLite WAL Hardening | Ejecución obligatoria de `PRAGMA journal_mode=WAL` y `busy_timeout` en I/O. | Deadlock Termodinámico DB. Corrupción de transacciones. | Overhead mínimo de I/O. | SQLite3 bin. |
| RED-005 | Verificación BFT de P0 | Cross-check de directivas P0 por un subagente paralelo `Epistemic-Purge-OMEGA` antes de commit final. | Drift Epistémico, pérdida de soberanía del Agent. | Latencia x2 en finalización de task crítica. | Comunicación Inter-Agente. |
