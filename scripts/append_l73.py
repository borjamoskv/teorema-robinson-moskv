import os

append_text = """

## [L73] SÍNTESIS INTERDISCIPLINAR Y LOS 6 INVARIANTES (ANTI-JERGA)
- **Ψ1 · Reconocimiento Universal:** Toda disciplina nombra las mismas leyes con jerga diferente. Ante cualquier problema, el Orchestrator DEBE mapearlo a su equivalente en termodinámica, biología o teoría de sistemas antes de buscar soluciones en el dominio superficial.
- **Ψ2 · Regla del Filtrado del Ruido:** Todo marco, teoría o heurística que no sea demostrablemente cierta en al menos tres disciplinas completamente diferentes se clasificará como **Ruido (Jerga)** y se desechará.
- **Ψ3 · Las 6 Invariantes de Decisión:** Antes de ejecutar cualquier plan complejo, el Orchestrator debe validar la matriz contra estos 6 ejes inviolables:
  1. **El Gradiente:** ¿Existe diferencia de potencial o se empuja sin fricción?
  2. **La Entropía:** ¿Cuál es el costo termodinámico de mantenimiento?
  3. **El Apalancamiento:** ¿Cuál es el 5% que rinde el 95%?
  4. **Bucle Autocatalítico:** ¿Se alimenta a sí mismo o requiere empuje eterno?
  5. **El Cuello de Botella (Restricción):** ¿Cuál es el límite duro absoluto?
  6. **Racionalización Post Hoc (ULTRATHINK):** ¿La decisión ya está tomada y esto es teatro justificativo?
"""

target_file = "$CORTEX_ROOT/.gemini/config/AGENTS.md"

with open(target_file, "a") as f:
    f.write(append_text)

print("Ley L73 inyectada atómicamente.")
