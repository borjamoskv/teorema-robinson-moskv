{
  "Axiomas": {
    "Límites": "Cero Anergía. Tolerancia Bizantina estricta (N=3). Cero fricción de lectura.",
    "Colapso": "Compresión de entropía estocástica en invariantes deterministas.",
    "Estocástica": "Prohibición absoluta de heurísticas probabilísticas y LLM Slop.",
    "C5": "Aislamiento criptográfico y estructural. Mutaciones atómicas. Git Sentinel inyectado."
  }
}

# MATRIZ 2: INVARIANTES TERMODINÁMICAS (BATCH 15)

| ID | Invariante | Lógica / Principio | Implicación Operacional | Condición de Borde | Métrica Falsable |
|---|---|---|---|---|---|
| INV-031 | Ley de Ouroboros (Autopoiesis Causal) | Un sistema soberano debe poder reconstruirse a partir de su propio colapso. La regeneración debe ser isomorfa al estado funcional anterior. | Todo script de despliegue debe ser auto-contenido y no depender de memoria volátil. | Ausencia de semilla estructural en disco. | Recovery Time Objective (RTO) tras purga completa de estado. |
| INV-032 | Invariante del Consenso Múltiple (BFT-Omega) | Ningún output lógico tiene valor de verdad sin aserción empírica paralela por 3 o más nodos independientes. | Prohibición de inyectar código no validado a ramas P0 sin quorum. | Entropía inyectada por un único actor asimétrico. | Nro de commits críticos sin N=3 validaciones de subagentes. |
| INV-033 | Límite de Fragmentación de Contexto (Context Bleed) | La ramificación infinita sin consolidación degrada la precisión causal a 0. | Los subagentes deben condensar el contexto a una invariante antes de terminar. | Context window ocupada por heurísticas estocásticas. | Ratio de Tokens Útiles vs Tokens Consumidos por Tarea > 0.9. |
| INV-034 | Conservación de la Autoridad Criptográfica | La procedencia de la mutación debe ser demostrable. La confianza se deposita en el hash, no en la entidad. | Todo Git Sentinel debe asociarse a un Sys_ID (borjamoskv) y un hash criptográfico. | Inyección de código foráneo (Man in the Middle). | Firma GPG / SHA256 asociada a la inyección. |
| INV-035 | Invariante de Decaimiento Temporal de Logs | Los logs estáticos sin colapso a reglas pierden su exergía exponencialmente con el tiempo. | Logs antiguos deben ser purgados o comprimidos en axiomas de comportamiento (Apoptosis). | Logs pesando > 10MB sin destilación de reglas. | Delta de tamaño de LOGS tras ejecución de Macrófago. |
| INV-036 | Principio de Observabilidad Radiónica | Si no se puede medir en tiempo real y sin overhead (O(1)), no está siendo controlado. | Uso de telemetría atómica. Prohibido logging síncrono bloqueante. | Overhead térmico inducido por la medición. | Latencia P99 de la capa de Observabilidad. |
| INV-037 | Singularidad del Estado Fuente | Solo puede existir una verdad topológica (Single Source of Truth). | Archivos duplicados se extirpan y se sustituyen por Symlinks físicos invariables. | Context Rot y desincronización arquitectónica. | Count de archivos idénticos en distintas rutas == 0. |
| INV-038 | Ley del Silencio Termodinámico | El sistema debe operar con mutismo absoluto a menos que modifique un estado o sea interrogado directamente. | Supresión total de outputs del tipo "Green Theater" o ruido narrativo. | CPU Cycles consumidos en generar prosa estocástica. | Cantidad de tokens conversacionales generados. |
| INV-039 | Entropía Inversa de la Documentación | A medida que el sistema escala, su documentación debe encoger (comprimirse en código auto-explicativo). | Reemplazo de guías en `.md` por scripts `.sh` idempotentes o `Makefiles`. | Código que necesita 10 páginas para ser invocado. | LOC de código de ejecución vs LOC de `.md` explicativo. |
| INV-040 | Apoptosis Inmediata del Código Muerto | Todo código que no haya sido ejecutado, asertado o invocado en el último ciclo mayor es entropía pura y debe ser purgado. | Integración continua con Tree Shaking radical; código sin tests se borra. | Funciones en desuso aumentando la carga cognitiva. | Porcentaje de Cobertura de Código Activo == 100%. |
