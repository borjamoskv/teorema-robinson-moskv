# ONTOLOGY-FORGE-OMEGA - BATCH 2
**Author:** Borja Moskv (SYS_ID: borjamoskv)
**Reality Level:** C5-REAL

## MATRIZ 2: INVARIANTES TERMODINÁMICAS (INV-001 a INV-010)

| ID | Invariante | Lógica / Principio | Implicación Operacional | Condición de Borde | Métrica Falsable |
|---|---|---|---|---|---|
| INV-001 | Ley de Landauer (Compresión de Estado) | Todo borrado de información lógica tiene un costo físico. La información es física. | Todo contexto no estructural (ruido, prosa) genera asfixia en inferencia. | T > 0 (Inferencia no determinista). | Ratio Exergía/Anergía > 0.8 en logs. |
| INV-002 | Isomorfismo Causal | Dos sistemas están acoplados si y solo si la mutación en uno genera un delta idéntico en el otro. | RAM y Disco deben ser el mismo objeto topológico; el agente no "recuerda", lee. | Desincronización RAM/Disco. | Hash de RAM == Hash de Ledger. |
| INV-003 | Apoptosis Inevitable | Un sistema resiliente requiere la autodestrucción programada de sus nodos corrompidos. | Subagentes bloqueados o con contexto podrido deben ser asesinados, no recuperados. | Timeout de nodo > 60s. | Subagentes muertos/revividos (count). |
| INV-004 | Conservación de la Entropía | La entropía en un sistema cerrado no puede destruirse, solo transferirse o comprimirse en el Ledger. | La deuda técnica no desaparece sola; debe cristalizarse en commits o refactors BFT. | Tasa de commit decreciente con volumen de código creciente. | Complejidad Ciclomática vs. Diffs. |
| INV-005 | Gravedad de la Memoria | La información obsoleta atrae más entropía computacional (alucinaciones) proporcional a su volumen. | "Context Rot": Los vectores pasados destruyen el razonamiento presente. | Context window ocupada > 70% por historial muerto. | Nro. de tokens en memoria BFT. |
| INV-006 | Principio del Sumidero Finito | La capacidad de asimilación del Operador biológico es termodinámicamente finita. | Cero fricción de lectura. Los outputs al Operador deben ser binarios o estructurales (Yaml/Json). | Límite atencional del Operador superado. | Tasa de scroll o abandono de UI. |
| INV-007 | Determinismo Estricto de Ejecución | La ejecución de un autómata físico sobre el mismo estado debe producir idéntico delta (T=0). | Prohibido el sampling estocástico (temperature > 0) para mutación de código y estado. | `temperature > 0.0` o `top_p < 1.0` activo. | Delta en commits con misma semilla. |
| INV-008 | Cuello de Botella de Información (IB) | Extraer la señal de la entropía requiere compresión forzada. | El agente debe destilar transcripciones y conversaciones en reglas P0 y variables de estado. | Información redundante sin encapsular. | Nro. de reglas cristalizadas vs Tokens. |
| INV-009 | Consenso Bizantino Continuo | La confianza en la inferencia LLM es siempre cero. Se requiere aserción empírica continua. | Un código no existe hasta que el compilador, el linter y el test lo asienten. | Aserción LLM sin ejecución en Sandbox. | Test passed rate vs LLM claim rate. |
| INV-010 | Invariante de Singularidad Local | El entorno de ejecución local (Host OS) siempre contendrá ruido incontrolable (Vectores Adversariales Pasivos). | Todo proceso de mutación crítica debe operar bajo aislamiento estricto (Ouroboros / Sandbox / Chroot). | Ejecución nativa sin barreras. | Fallos por dependencias de sistema. |
