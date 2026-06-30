<!-- Author: Borja Moskv (SYS_ID: borjamoskv) -->

# MATRIZ 4: REDUNDANCIAS ACTIVAS (MITIGACIÓN C5)

| ID | Redundancia C5 | Función Topológica | Riesgo Mitigado | Coste (Overhead) | Dependencias |
|---|---|---|---|---|---|
| RED-001 | Git Sentinel Criptográfico | Genera un snapshot BFT de cada mutación, aislando el estado anterior. | Pérdida de código por alucinación de escritura. Fallo en cascada. | I/O en disco, incremento log. | `.git` tracking, bash access. |
| RED-002 | Apoptosis Subagente | Límite temporal estricto (TimerCondition) para agentes paralelos, asesinándolos si no responden. | Zombificación de memoria RAM, Interbloqueo Recursivo. | Consumo de un thread de monitoring. | `manage_task`, `invoke_subagent`. |
| RED-003 | Multi-Viewport QA Autómata | Validación de UI mediante subagente visual aislado para confirmar delta visual exacto. | DOM Drift, alucinación de CSS. | Consumo de cuota visual (Tokens pesados). | `browser_subagent`. |
| RED-004 | SQLite WAL Hardening | Ejecución obligatoria de `PRAGMA journal_mode=WAL` y `busy_timeout=5000` en I/O. | Deadlock Termodinámico DB. Corrupción de transacciones. | Overhead mínimo de I/O. | SQLite3 bin. |
| RED-005 | Verificación BFT de P0 | Cross-check de directivas P0 por un subagente paralelo `Epistemic-Purge-OMEGA` antes de commit final. | Drift Epistémico, pérdida de soberanía del Agent. | Latencia x2 en finalización de task crítica. | Comunicación Inter-Agente. |
| RED-006 | Snapshots de Estado Diario (Brain Dump) | Serialización de la ontología extraída, tareas vivas y decisiones en `.cortex/memory_vault/`. | Drift Epistémico por reinicio de Kernel / Server Restart. | I/O en disco asíncrono, tokens de compresión. | Protocolo de persistencia C5. |
| RED-007 | Fallback de Modelos de Lenguaje (Model Tiering) | Mecanismo que hace fallback a Ollama/MLX local si la API externa cae o satura el rate limit. | Bloqueo de Rate Limit (PRIM-033), Tunnel Friction. | RAM/VRAM en Host OS para alojar modelo Local. | MLX-LM, Local Inference Engine. |
| RED-008 | Caché Estructural Aislada | Almacenamiento en hashes de dependencias pesadas (ej. `node_modules` en CI) para evitar descargas. | Desgarre de Lockfile, Latencia extrema de build. | Consumo de almacenamiento secundario. | Herramientas de build (TurboRepo). |
| RED-009 | Orquestador de Health-Check (Ping/Pong Monitor) | Agente paralelo o demonio en Bash que vigila el heartbeat de subagentes activos. | Zombificación de Tarea (PRIM-026), Recursiones infinitas. | CPU ciclos constantes en background. | `manage_task`, Cron. |
| RED-010 | Auto-healing de Linting | Pipeline atómico `eslint --fix` / `prettier` pre-commit automatizado sin intervención humana. | Inyección de entropía de formato, Fricción Compiladora. | Tiempo de ejecución pre-commit de segundos. | Git Hooks nativos (Husky). |
