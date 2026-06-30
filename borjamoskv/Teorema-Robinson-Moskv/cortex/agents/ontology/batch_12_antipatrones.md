# ONTOLOGY-FORGE-OMEGA - BATCH 12

## MATRIZ 3: ANTIPATRONES ESTOCÁSTICOS (ANTI-021 a ANTI-030)

| ID | Antipatrón | Disfunción Causal | Señal de Presencia | Impacto en Robustez | Refactor (Alternativa) |
|---|---|---|---|---|---|
| ANTI-021 | Logging Silencioso | Escribir a stdout/stderr pero no recoger ni persistir el log para auditoría BFT. | `console.log()` sin agregación o persistencia en DB/Archivos C5. | Pérdida de Linaje Causal en fallos de producción. | Envío sincrónico a archivo de log rotativo o Cortex Vault. |
| ANTI-022 | Dependencia de Red en Desarrollo Local | Requerir internet para levantar el entorno BFT o de testing (Cloud DBs sin fallback local). | Tests fallan en modo offline o túnel VPN caído. | Fricción de Túnel (PRIM-019), parálisis. | Instanciación Dockerizada (SQLite Local/Redis) estricta. |
| ANTI-023 | Uso de Magic Numbers | Valores literales de control incrustados en el código sin nombramiento semántico. | `if (status == 4)` o `setTimeout(..., 86400)`. | Entropía léxica; incomprensión de contratos físicos. | Extracción a constantes MECE `const STATUS_ERROR = 4`. |
| ANTI-024 | Validaciones en Frontera Pasivas | Asumir que los datos entrantes (API, Webhooks) tienen el tipo correcto sin validación runtime estricta (Zod). | Usar TypeScript `as MyType` sin parsar. | Schema Drift (PRIM-036), corrupción de datos. | Aserción estricta en frontera (Zod/Valibot). |
| ANTI-025 | Hardcoding de Rutas Absolutas en Código | Escribir `/Users/borja/` dentro del código fuente compilado. | Errores en CI/CD o al compartir repo. | Desgarre de portabilidad C5. | Uso estricto de resolución relativa desde `__dirname` o Env. |
| ANTI-026 | Mutación de Props (State Mutation Leak) | Modificar objetos de estado recibidos por referencia en lugar de clonarlos inmutablemente. | `prop.value = X` en frameworks React/Vue o Python. | Falsos positivos visuales (Ghost DOM), Side-effects. | Estructuras inmutables, `structuredClone`. |
| ANTI-027 | God Object (Objeto Dios) | Un solo archivo o clase maneja DB, red, lógica de negocio y presentación simultáneamente. | Archivo `utils.js` o `App.tsx` de 5000 líneas. | Saturación del AST, colisiones BFT masivas. | Desacoplamiento por Responsabilidad Única (SRP). |
| ANTI-028 | Git Push Force Ciego | Sobreescribir el historial BFT de una rama remota sin verificar la desincronización de reloj vectorial (VEC-006). | `git push -f` sin `--force-with-lease`. | Destrucción de Invariantes y código colaborativo. | Prohibición estricta; uso de merge o force con aserción BFT. |
| ANTI-029 | Ignorar Timestamps Criptográficos | Depender de contadores incrementales (IDs) de DB que pueden ser resecuenciados, en lugar de UUIDs/ULIDs o Timestamps. | IDs como `1, 2, 3` predecibles y colisionables. | Vulnerabilidad de enumeración, colisión tras import/export. | Uso absoluto de identificadores criptográficos (UUIDv4/ULID). |
| ANTI-030 | Tests Acoplados a Implementación | Testear métodos privados o estructuras internas del AST en lugar del contrato público. | Mock de funciones privadas del mismo módulo. | Asimetría de Refactor (INV-016), Tests frágiles. | Testing Behavior-Driven (Contrato I/O puro). |
