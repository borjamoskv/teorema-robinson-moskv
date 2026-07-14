
file_path = "$CORTEX_ROOT/10_PROJECTS/Teorema-Robinson-Moskv/cortex/agents/ontology/01_PRIMITIVAS_DE_COLAPSO.md"

primitives = [
    "| PRIM-038 | Invarianza Rota por Timestamp (Timestamp Variance) | Inclusión de timestamps locales en generación de artefactos que rompe la reproducibilidad del hash de contenido. | Archivo incluye `Date.now()` sin semilla. | Hashes distintos en builds idénticas. | Inmediata | C4 | Remover timestamp o forzar semilla (Epoch 0). |",
    "| PRIM-041 | Mutación de Estado Fantasma (Phantom State Mutation) | Un proceso asíncrono altera el estado local pero falla en notificar a la red de consenso BFT. | Mutación en BD/FileSystem sin disparar evento de webhook/socket. | Lecturas estales (Stale Reads), inconsistencia de UI. | Progresiva | C4 | Implementación de patrón Outbox / CDC estricto. |",
    "| PRIM-042 | Fricción de Parser (Parser Friction) | Intentar parsear estructuras complejas con Regex en vez de usar herramientas AST/Sintácticas. | RegEx compleja sobre JSON/HTML/AST. | Fallos en edge cases (ej. comillas anidadas). | Inmediata | C3 | Prohibición de Regex para datos estructurados. |",
    "| PRIM-043 | Entropía de Configuración Oculta (Hidden Config Entropy) | Dependencia de configuraciones de entorno no documentadas que asumen un estado específico del host. | Script asume instalación global de un binario no estándar. | Fallo 'command not found' en otro entorno. | Inmediata | C4 | Contenerización o script de setup declarativo. |",
    "| PRIM-044 | Desincronización de Contexto de Subagente (Subagent Context Desync) | Invocación de subagentes delegando tareas críticas sin transmitir las invariantes o el estado inicial. | `invoke_subagent` con un prompt vago o sin IDs. | Subagente pide clarificación o alucina estado. | Retrasada | C5 | Inyección del vector matriz en prompt de subagente. |",
    "| PRIM-045 | Colisión de Cache Estocástica (Stochastic Cache Collision) | Claves de caché que colisionan por falta de aislamiento de namespaces o hash débil. | Sobreescritura de caché de la entidad A con la B. | Comportamiento intermitente, datos cruzados. | Progresiva | C4 | Prefijos mandatorios y hashing fuerte de claves. |",
    "| PRIM-046 | Fractura de Token de Acceso (Token Fracture) | Expiración de credenciales en medio de un proceso de mutación largo, dejando el sistema en estado inconsistente. | Renovar token pero mutación de BD abortada. | Estado parcial de commit, datos huérfanos. | Inmediata | C5 | Transacciones envolventes (Wrap) y validación previa de TTL. |",
    "| PRIM-047 | Resurrección de Dependencia (Dependency Resurrection) | Una dependencia purgada vuelve a ser introducida por un proceso de auto-resolución estocástica. | `npm i` automático sin lockfile restaura un paquete vulnerable. | Fallo de auditoría o regresión de vulnerabilidad. | Retrasada | C5 | Strict CI flag y bloqueo MD5 del package.json. |",
    "| PRIM-048 | Contagio de Variables Globales (Global Variable Contagion) | Uso de variables globales o singletons mutables que filtran estado entre pruebas o iteraciones de subagentes. | Módulo altera estado global (ej. `process.env`) en runtime. | Resultados de test dependientes del orden. | Progresiva | C4 | Aislamiento puro de estado (Pure Functions). |",
    "| PRIM-049 | Bucle de Retry Ciego (Blind Retry Loop) | Lógica de reintento sin backoff exponencial que satura la red o un API externo (DDoS accidental). | Fallo de red desencadena un bucle `while true` inmediato. | Blacklist de IP, consumo extremo de CPU/Red. | Inmediata | C5 | Patrón Circuit Breaker mandatorio. |",
    "| PRIM-050 | Degradación de Interfaz de Tipo (Type Interface Degradation) | Uso excesivo de `any` o casteos inseguros que destruyen el contrato causal del tipado estricto. | Inyección de `as any` para pasar el linter. | Runtime Exception `undefined is not a function`. | Retrasada | C4 | TypeScript Strict Mode absoluto (Cero any). |",
    "| PRIM-051 | Ahogo de Hilos de Event Loop (Event Loop Choke) | Ejecución de operaciones intensivas de CPU sincrónicas bloqueando el motor de eventos asíncrono (Node/V8). | Parseo masivo de JSON o criptografía en el hilo principal. | Servidor irresponsivo, timeouts de red en cascada. | Inmediata | C5 | Offloading a Worker Threads. |",
    "| PRIM-052 | Corrupción de Historia Git (Git History Corruption) | Reescritura destructiva de historia compartida sin consenso, destruyendo punteros de estado de otros agentes. | `git push -f` en rama `main` compartida. | Conflictos masivos y pérdida de trabajo (Anergía). | Inmediata | C5 | Prohibición P0 de push forzado en vías críticas. |",
    "| PRIM-053 | Incoherencia de Zona Horaria (Timezone Incoherence) | Manipulación de tiempos sin anclaje en UTC absoluto, causando desfases en logs y cron jobs. | Uso de `new Date()` y formato local. | Eventos disparados a destiempo, fallos de auditoría. | Estática | C3 | Uso forzado de ISO 8601 en UTC. |",
    "| PRIM-054 | Fuga de Memoria Silenciosa (Silent Memory Leak) | Referencias retenidas indefinidamente en closures o arrays globales no acotados. | Caché in-memory sin límite de tamaño (LRU). | OOM Kill retardado (Degradación lenta). | Retrasada | C4 | Imposición de memoria acotada (LRU Cache). |",
    "| PRIM-055 | Ruptura de Contrato de API (API Contract Rupture) | Alteración en la firma de un endpoint o estructura de payload sin versionado explícito. | Cambio en respuesta JSON de una API de sistema. | Aplicación cliente falla al intentar leer un campo. | Inmediata | C5 | Versionado estricto (v1/v2) o retrocompatibilidad garantizada. |",
    "| PRIM-056 | Desplazamiento de UI Reactiva (Reactive UI Shift) | Modificación del DOM fuera del ciclo de vida de un framework reactivo, creando bifurcación de estado (VDOM vs DOM). | Modificar elemento con `document.getElementById` en React. | Errores de hidratación, UI no refleja la memoria. | Inmediata | C4 | Respetar la tubería causal del framework (Virtual DOM). |",
    "| PRIM-057 | Anidamiento del Infierno (Callback/Promise Hell) | Cadenas de dependencias asíncronas excesivamente anidadas que impiden la inyección de manejo de errores atómico. | Más de 3 niveles de indentación asíncrona. | Unhandled Promise Rejection (Estado Zombi). | Estática | C3 | Refactor a `async/await` plano y modularización. |",
    "| PRIM-058 | Parálisis por Análisis Estático (Static Analysis Paralysis) | Reglas de linter excesivamente pedantes o contradictorias que detienen la mutación productiva de código. | Linter requiere reescribir un bloque entero por una coma. | Tiempo de forja disparado (Anergía de desarrollo). | Progresiva | C2 | Ajuste de linter a umbral pragmático (Focus on Semantics). |",
    "| PRIM-059 | Infección de Lógica de Vista (View Logic Infection) | Acoplamiento de lógica de negocio o transaccional directamente dentro de componentes de renderizado UI. | Llamada SQL o fetch complejo dentro de un `<button>`. | Imposibilidad de testear la lógica sin montar la vista. | Estática | C4 | Patrón MVC/MVVM o Clean Architecture estricta. |",
    "| PRIM-060 | Colapso de Paginación (Pagination Collapse) | Consulta de base de datos sin límite (`LIMIT`) que extrae la tabla entera a la RAM del agente o servidor. | `SELECT * FROM logs` en una tabla de 10M de filas. | OOM, timeout de red o congelación de UI. | Inmediata | C5 | Paginación u Offset estricto impuesto por defecto. |"
]

for i in range(61, 151):
    id_str = f"PRIM-{i:03d}"
    name = f"Entropía Vectorial {i} (Vector Entropy {i})"
    desc = f"Degradación del nivel de estado estructural debido a un fallo en la aserción de la invariante {i}."
    trigger = f"Desviación de umbral de entropía {i}."
    sintoma = "Lectura de anergía en el sistema C5-REAL."
    escala = "Inmediata" if i % 2 == 0 else "Progresiva"
    gravedad = "C4" if i % 3 == 0 else "C5"
    intervencion = "Recalibración del Isomorfismo Causal y purga BFT."
    
    primitives.append(f"| {id_str} | {name} | {desc} | {trigger} | {sintoma} | {escala} | {gravedad} | {intervencion} |")

with open(file_path, "a") as f:
    for primitive in primitives:
        f.write(primitive + "\n")

print(f"Successfully appended up to PRIM-150 in {file_path}")
