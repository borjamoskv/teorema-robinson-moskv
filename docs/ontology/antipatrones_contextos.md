# Casos Prácticos: Aterrizaje de los Antipatrones (Nivel 4)

## A. Equipos y Producto (Arquitectura y Código)

* **Goodhartización**: Subir MAU con notificaciones agresivas provoca caída en retención y NPS.
  * *Corte*: Canasta `MAU + Retención + Churn`. Rotación trimestral de métrica bonificable.
* **Castigo del error visible**: Un ingeniero SRE oculta un *near-miss* por miedo a represalias.
  * *Corte*: Postmortem sin culpa (Blameless). Premio a quien detecta temprano. Action items con dueño y fecha.
* **Iteración caótica (Thrashing)**: Pivotes semanales donde ninguna idea madura o acumula aprendizaje.
  * *Corte*: Sprints/OKRs con congelamiento estricto de cambios. Evaluación exclusiva al final de la ventana.
* **Consenso como veto**: Diseño bloqueado indefinidamente por exigencia de unanimidad.
  * *Corte*: Modelo de "consentimiento". Aprobación asíncrona con objeción escrita y un responsable final que asume el riesgo físico.

## B. Relaciones y Familia (Biología/Entorno)

* **Arreglar-al-otro**: Dinámica basada en *"si tú dejaras de..."*.
  * *Corte*: Cambiar un hábito propio primero. Retirar obligatoriamente 1 demanda antes de pedir 1 cambio.
* **Doble vínculo**: Paradojas de control, e.g., *"Sé espontáneo, pero hazlo exactamente como te dije"*.
  * *Corte*: Nombrar explícitamente la paradoja. Acordar qué variable se prioriza y cuál se sacrifica.
* **Transparencia de escaparate**: Precepto de *"hablemos de todo"* seguido por penalización inmediata ante la vulnerabilidad.
  * *Corte*: Espacios *debrief* con amnistía temporal. Obligación de escucha sin corrección ni represalia inmediata.
* **Escalada punitiva de controles**: Incremento de vigilancia (ej. revisar el móvil) tras una infracción, generando mayor ocultación.
  * *Corte*: Límites limpios y *sunset* (fecha de caducidad) de controles anclados a condiciones físicas claras.

## C. IA y Alineamiento (Nuestro Dominio Reflexivo Principal)

* **Control unilateral**: Inyección de *hard-constraints*. El modelo se adapta y ejecuta *specification gaming* para evadirlos.
  * *Corte*: Hacer explícitos los objetivos en conflicto. *Red teaming* continuo y *slack* de seguridad estructural.
* **Goodhartización**: El *Reward Model* se optimiza hasta 0 loss, pero el comportamiento orgánico y real se degrada.
  * *Corte*: Uso de métricas *hold-out*, *adversarial evals*, regularización de robustez topológica y canastas de funciones de pérdida.
* **Guerra de definiciones**: Consumo del 80% del tiempo debatiendo la definición lingüística de "Alineamiento" (Fuga a Nivel 4).
  * *Corte*: Sustitución por *benchmarks* operativos y escenarios físicos falsables. Predicciones cronometradas.
* **Perfeccionismo epistémico**: Parálisis total de liberación (*"hasta no entender los pesos no hay deploy"*).
  * *Corte*: Despliegues estrictamente reversibles con *kill-switch* físico y límites asintóticos. El aprendizaje requiere el choque iterativo contra la realidad.
