# Marco Metodológico: Análisis de Comportamiento Inauténtico Coordinado (CIB) en Ecosistemas Substack

Este documento establece la metodología formal y reproducible para analizar y auditar redes de interacción artificial o *engagement pods* en boletines y notas de Substack (especialmente en la sección "Negocios"). El análisis se fundamenta estrictamente en datos públicos y técnicas OSINT pasivas.

---

## 1. Planteamiento de Hipótesis CIB

Para evaluar de forma científica la presencia de un nodo coordinado se formulan dos hipótesis contrastables:

*   **Hipótesis Nula ($H_0$):** El engagement de la publicación (likes, restacks, respuestas) es de carácter orgánico, con distribución geográfica dispersa, asincronía temporal y baja reciprocidad sistemática.
*   **Hipótesis Alternativa ($H_1$):** Existe un subgrafo densamente conectado (clúster de ~80-90 cuentas) cuyos miembros interactúan recíproca e inminentemente ante cada publicación para forzar señales positivas en el algoritmo de recomendación de Substack.

---

## 2. Métricas y Algoritmos de Detección

### A. Similitud Conductual (Lockstep Behavior)
La similitud entre interactores se mide mediante el **Coeficiente de Jaccard** aplicado al conjunto de notas en las que han interactuado:

$$J(U_1, U_2) = \frac{|N_1 \cap N_2|}{|N_1 \cup N_2|}$$

Donde:
*   $N_1$ es el conjunto de notas interactuadas por el usuario $U_1$.
*   $N_2$ es el conjunto de notas interactuadas por el usuario $U_2$.

Un valor de $J(U_1, U_2) > 0.7$ sostenido en más de 20 notas indica una correlación de comportamiento extremadamente inusual para lectores independientes.

### B. Sincronización Temporal y Entropía ($H$)
La sincronización en las interacciones post-publicación se calcula mediante la entropía de Shannon sobre intervalos de tiempo discretizados:

$$H_t = -\sum_{i=1}^{k} P(t_i) \log_2 P(t_i)$$

*   Una entropía $H_t \to 0$ significa que las interacciones ocurren en un bloque temporal uniforme y altamente predecible (típicamente en los primeros 10 minutos tras la publicación).
*   El comportamiento orgánico exhibe una distribución de Poisson de cola larga con alta entropía.

### C. Topología de Red y Detección de Comunidades
Proyectando el grafo bipartito `[Usuario - Nota]` en un grafo monopartito `[Usuario - Usuario]`, se aplican algoritmos de detección de comunidades como **Louvain** o **Leiden** para segmentar y aislar comunidades anómalas. Un nodo de amplificación inauténtico se caracteriza por tener una modularidad y centralidad de intermediación (*betweenness centrality*) marcadamente elevada en comparación con el resto de la red.

---

## 3. Guía de Reporte Ético y Cumplimiento Legal

1. **Anonimización:** Al divulgar informes públicos, los nombres de usuario (*handles*) deben ser ofuscados mediante hashes criptográficos de un solo sentido (por ejemplo, SHA-256 truncado) para proteger la privacidad individual bajo GDPR/CCPA.
2. **Uso de Datos Públicos:** Toda la información recolectada debe provenir de llamadas de consulta pública (Open APIs de Substack o renderizado DOM estándar de páginas públicas).
3. **Lenguaje Objetivo:** Evitar calificativos subjetivos o acusaciones sin respaldo forense. Utilizar términos técnicos formalizados en ciberseguridad y análisis de redes sociales (por ejemplo: "Comportamiento coordinado", "Astroturfing", "Engagement Farming", "Clúster cerrado").
