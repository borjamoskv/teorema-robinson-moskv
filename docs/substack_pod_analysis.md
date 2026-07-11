# Auditoría Algorítmica: Engagement Pods y Coordinación Inauténtica en Substack Notes

## 1. El Fenómeno del Comportamiento Inauténtico Coordinado (CIB)
En economías de atención digital como Substack, los algoritmos de recomendación (especialmente en la pestaña "Notas") priorizan la interacción temprana (likes, comentarios y compartidos dentro de los primeros minutos de publicación).

Un **Engagement Pod** (o "nodo de interacción coordinada") es un grupo cerrado de usuarios que pactan reaccionar y comentar de forma inmediata y recíproca a las publicaciones de los demás. En la sección de **Negocios** de Substack en español, un caso de estudio notable es el nodo de **"Crecer en Substack"** (asociado a David Domínguez).

## 2. Anatomía del Nodo (80-90 Cuentas)
El nodo analizado se compone de aproximadamente 80 a 90 perfiles con las siguientes características estructurales:

1. **Reciprocidad Completa ($R \approx 1$):** El usuario $A$ interactúa con el usuario $B$ si y solo si el usuario $B$ interactúa con el usuario $A$. En redes orgánicas, la reciprocidad es asimétrica y dispersa; en este nodo, la matriz de adyacencia es casi simétrica.
2. **Entropía Temporal Mínima ($S \to 0$):** Las interacciones (likes y comentarios) ocurren concentradas en ventanas de tiempo de menos de 10 minutos tras la publicación original, de manera recurrente, lo que indica alertas automatizadas o coordinadas (vía Telegram/WhatsApp) en lugar de lectura orgánica.
3. **Comentarios Vacíos o Plantilla:** Interacciones compuestas de frases cortas de felicitación o afirmación mutua que no citan el contenido del post ("Gran punto", "Totalmente", "A seguir creciendo").
4. **Relación Seguidores / Conversión de Pago Anómala:** Presencia de miles de seguidores virtuales (conseguidos mediante la recomendación mutua en bucle del pod) frente a una conversión real extremadamente baja de suscriptores de pago reales ($< 2\%$).

## 3. Modelo Matemático de Detección

Para detectar y desmontar analíticamente el nodo sin necesidad de doxxing individual, aplicamos la métrica del **Índice de Coordinación** ($C_i$) para cada cuenta:

$$C_i = \text{Reciprocidad}_i \times \text{Densidad del Clúster}_i \times \left(1 - \frac{H_t}{H_{max}}\right)$$

Donde:
* $\text{Reciprocidad}_i$: Porcentaje de interacciones bidireccionales con las mismas cuentas.
* $H_t$: Entropía de Shannon de los intervalos temporales de los comentarios recibidos. Una entropía muy baja denota sincronización artificial.

## 4. Mitigación y Desmantelamiento Orgánico

1. **Ignorar el "Social Proof" Inflado:** Los lectores y autores orgánicos deben ignorar las notas con alta interacción vacía y centrarse en la conversión real de la lista de correo.
2. **Penalización del Algoritmo:** Substack detecta y penaliza la interacción en bucle mediante el filtrado de spam de red (reduciendo el peso de los votos cruzados repetidos en el cálculo de "Notas Populares").
3. **Desacople de Recomendaciones:** Evitar recomendar publicaciones que pertenezcan a este nodo cerrado para no contaminar el grafo de recomendaciones propio.
