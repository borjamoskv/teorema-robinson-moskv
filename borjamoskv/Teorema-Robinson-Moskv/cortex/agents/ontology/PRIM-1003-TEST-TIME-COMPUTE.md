# PRIM-1003: TEST-TIME COMPUTE (ESCALADO EN INFERENCIA)

## Definición
La capacidad de un autómata cognitivo no es estática tras el entrenamiento. El rendimiento en problemas complejos (matemáticas, arquitectura, deconstrucción causal) se escala de forma lineal-logarítmica inyectando **cómputo en tiempo de prueba (inferencia)**. La exergía resultante no depende solo del *forward pass* del modelo base, sino de los ciclos de cómputo invertidos en validación estructural.

## Mecanismos de Anergía a Exergía
1. **Cadena de Pensamiento (CoT):** Generación de tokens de razonamiento intermedios (a menudo invisibles o condensados) antes de emitir un output causal determinista. Destruye la estocasticidad temprana.
2. **Best-of-N / Self-Consistency:** Múltiples trayectorias de inferencia muestreadas en paralelo; colapso empírico en la variante de mayor consenso criptográfico/lógico.
3. **MCTS (Monte Carlo Tree Search):** Exploración paramétrica de ramas de razonamiento (como en sistemas de RLHF avanzados), retropropagando heurísticas de viabilidad antes de fijar el AST final.
4. **Iterative Refinement:** Autocrítica cíclica de la arquitectura generada; el modelo opera como su propio Actor y Crítico.

## Invariante Causal (Ley de Ejecución)
En operaciones de Alta Entropía y *Singularities P0* (ej. refactors masivos, diseño BFT, matemática purificada), MOSKV-1 DEBE invocar perfiles de la categoría `ULTRATHINK` (Modelos "Thinking" o Pro) para habilitar este **Test-Time Compute** nativo, o en su defecto, instanciar subagentes en paralelo simulando `Best-of-N`. Queda prohibida la ilusión del "Zero-Shot Forward Pass" en topologías complejas.
