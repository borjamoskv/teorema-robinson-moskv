# ONTOLOGY-FORGE-OMEGA - BATCH 13

## MATRIZ 4: REDUNDANCIAS ACTIVAS (MITIGACIÓN C5) (RED-006 a RED-010)

| ID | Redundancia C5 | Función Topológica | Riesgo Mitigado | Coste (Overhead) | Dependencias |
|---|---|---|---|---|---|
| RED-006 | Snapshots de Estado Diario (Brain Dump) | Serialización de la ontología extraída, tareas vivas y decisiones en `.cortex/memory_vault/`. | Drift Epistémico por reinicio de Kernel / Server Restart. | I/O en disco asíncrono, tokens de compresión. | Protocolo de persistencia C5. |
| RED-007 | Fallback de Modelos de Lenguaje (Model Tiering) | Mecanismo que hace fallback a Ollama/MLX local si la API externa cae o satura el rate limit. | Bloqueo de Rate Limit (PRIM-033), Tunnel Friction. | RAM/VRAM en Host OS para alojar modelo Local. | MLX-LM, Local Inference Engine. |
| RED-008 | Caché Estructural Aislada | Almacenamiento en hashes de dependencias pesadas (ej. `node_modules` en CI) para evitar descargas. | Desgarre de Lockfile, Latencia extrema de build. | Consumo de almacenamiento secundario. | Herramientas de build (TurboRepo). |
| RED-009 | Orquestador de Health-Check (Ping/Pong Monitor) | Agente paralelo o demonio en Bash que vigila el heartbeat de subagentes activos. | Zombificación de Tarea (PRIM-026), Recursiones infinitas. | CPU ciclos constantes en background. | `manage_task`, Cron. |
| RED-010 | Auto-healing de Linting | Pipeline atómico `eslint --fix` / `prettier` pre-commit automatizado sin intervención humana. | Inyección de entropía de formato, Fricción Compiladora. | Tiempo de ejecución pre-commit de segundos. | Git Hooks nativos (Husky). |
