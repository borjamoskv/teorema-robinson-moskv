## Catálogo de 500 primitivas e invariantes estructurales

Modelo base: una estructura multiclase  
\[
\mathcal A=(S_i,R_j,F_k,c_\ell)
\]
con clases \(S_i\), relaciones \(R_j\), operaciones \(F_k\) y constantes \(c_\ell\). Un isomorfismo es una familia de biyecciones tipadas \(\varphi_i:S_i\to S'_i\) que preserva exactamente constantes, relaciones y operaciones.

Los nombres, metáforas y similitudes visuales se ignoran. Un color, peso o etiqueta solo cuenta si forma parte explícita de la signatura.

---

# I. Primitivas estructurales

## A. Sustrato tipado: 1–25
1. **Clase:** categoría básica de objetos.
2. **Portador:** conjunto de elementos de una clase.
3. **Elemento:** unidad perteneciente a un portador.
4. **Variable tipada:** posición reemplazable restringida a una clase.
5. **Constante:** símbolo que designa un elemento fijo.
6. **Punto distinguido:** elemento con función estructural explícita.
7. **Tupla:** colección ordenada de elementos tipados.
8. **Secuencia:** tupla de longitud variable.
9. **Multiconjunto:** colección con multiplicidades.
10. **Subconjunto:** selección no ordenada de un portador.
11. **Índice:** identificador interno de una familia estructural.
12. **Aridad:** número y tipos de argumentos.
13. **Signatura:** inventario de clases, relaciones, funciones y constantes.
14. **Dominio:** clases admitidas como entradas.
15. **Codominio:** clase declarada de salida.
16. **Producto de clases:** combinación conjuntiva de tipos.
17. **Coproducto de clases:** combinación disjunta de tipos.
18. **Clase unidad:** portador con un único elemento.
19. **Clase vacía:** portador sin elementos.
20. **Subtipo:** clase incluida mediante una condición estructural.
21. **Familia dependiente:** tipo parametrizado por otro elemento.
22. **Clase de equivalencia:** bloque inducido por una equivalencia.
23. **Portador cociente:** conjunto de clases de equivalencia.
24. **Contexto:** asignación tipada de variables.
25. **Interpretación:** realización concreta de una signatura.

## B. Relaciones e incidencia: 26–50
26. **Predicado unario:** propiedad estructural de un elemento.
27. **Relación binaria:** vínculo entre dos elementos.
28. **Relación n-aria:** vínculo entre una tupla tipada.
29. **Función total:** salida única para cada entrada admisible.
30. **Función parcial:** función no definida en todas las entradas.
31. **Correspondencia multivaluada:** asociación con varias salidas posibles.
32. **Nodo:** entidad incidente en una red.
33. **Arista dirigida:** relación con fuente y destino.
34. **Arista no dirigida:** incidencia simétrica entre extremos.
35. **Hiperarista:** incidencia con cualquier número de nodos.
36. **Relación de incidencia:** indica qué objetos participan en otros.
37. **Fuente:** extremo inicial de una relación dirigida.
38. **Destino:** extremo final de una relación dirigida.
39. **Extremo:** participante de una arista no dirigida.
40. **Puerto:** punto local de conexión.
41. **Tipo de puerto:** restricción estructural de conexión.
42. **Bucle:** arista cuyos extremos coinciden.
43. **Identidad de arista paralela:** distingue incidencias repetidas.
44. **Orientación:** elección coherente de sentido.
45. **Polaridad:** signo o rol positivo/negativo preservable.
46. **Multiplicidad:** número de copias de una incidencia.
47. **Color estructural de nodo:** clase interna, no nombre superficial.
48. **Tipo de arista:** clase estructural de una conexión.
49. **Incidencia de frontera:** conexión entre interior e interfaz.
50. **Incidencia prohibida:** combinación excluida por la signatura.

## C. Operaciones algebraicas: 51–75
51. **Identidad composicional:** operación neutra respecto de composición.
52. **Composición:** encadenamiento tipado de transformaciones.
53. **Operación nularia:** operación sin argumentos.
54. **Operación unaria:** transformación de un elemento.
55. **Operación binaria:** combinación de dos elementos.
56. **Operación n-aria:** combinación de una tupla.
57. **Operación inversa:** revierte una operación cuando existe.
58. **Acción:** operación de una estructura sobre otra.
59. **Coacción:** versión dual de una acción.
60. **Multiplicación escalar:** acción de escalares sobre elementos.
61. **Suma:** operación aditiva declarada.
62. **Producto:** operación multiplicativa declarada.
63. **Negación:** operación unaria aditiva inversa.
64. **Unidad:** elemento neutro multiplicativo.
65. **Cero:** elemento neutro aditivo.
66. **Selector:** operación que elige una entrada según una regla.
67. **Emparejamiento:** construcción de un elemento producto.
68. **Proyección:** extracción de una coordenada.
69. **Inyección:** inserción en una suma o superestructura.
70. **Evaluación:** aplicación explícita de una función.
71. **Currificación:** conversión entre argumentos conjuntos y sucesivos.
72. **Plegado:** reducción de una estructura recursiva.
73. **Desplegado:** expansión de una estructura recursiva.
74. **Sustitución:** reemplazo tipado de variables o términos.
75. **Constructor de términos:** regla generadora de expresiones estructurales.

## D. Orden, geometría y topología: 76–100
76. **Igualdad:** coincidencia estructural interna.
77. **Orden estricto:** relación irreflexiva y transitiva.
78. **Orden no estricto:** relación reflexiva, antisimétrica y transitiva.
79. **Preorden:** relación reflexiva y transitiva.
80. **Equivalencia:** relación reflexiva, simétrica y transitiva.
81. **Relación de cobertura:** precedencia sin elemento intermedio.
82. **Ínfimo:** mayor cota inferior.
83. **Supremo:** menor cota superior.
84. **Mínimo global:** elemento inferior distinguido.
85. **Máximo global:** elemento superior distinguido.
86. **Complemento:** operación de oposición respecto de cotas.
87. **Clausura:** operador extensivo, monótono e idempotente.
88. **Interior:** operador contractivo, monótono e idempotente.
89. **Vecindad:** relación de proximidad estructural.
90. **Predicado de abierto:** pertenencia a la topología declarada.
91. **Elemento de base:** abierto generador de una topología.
92. **Métrica:** distancia simétrica con desigualdad triangular.
93. **Pseudométrica:** métrica que permite distancia cero entre distintos.
94. **Betweenness:** relación ternaria de intermediación.
95. **Orientación geométrica:** elección estructural de orientación.
96. **Etiqueta dimensional:** dimensión declarada de una celda.
97. **Símplex:** celda determinada por sus vértices.
98. **Mapa de cara:** eliminación tipada de una coordenada simplicial.
99. **Mapa de degeneración:** repetición tipada de una coordenada.
100. **Operador de borde:** combinación formal de caras.

## E. Descomposición e interfaces: 101–125
101. **Componente:** subestructura separable según una relación.
102. **Subobjeto:** estructura contenida y cerrada bajo operaciones.
103. **Inclusión:** morfismo de un subobjeto al objeto total.
104. **Encaje:** morfismo inyectivo que preserva estructura.
105. **Proyección estructural:** morfismo hacia un factor.
106. **Retracción:** morfismo que revierte una inclusión.
107. **Sección:** inversa derecha de una proyección.
108. **Mapa cociente:** identificación controlada de elementos.
109. **Partición:** división en bloques disjuntos.
110. **Bloque:** parte indivisible respecto de una descomposición.
111. **Fibra:** preimagen de un valor.
112. **Módulo:** subestructura con interfaz definida.
113. **Interfaz:** conjunto de puntos visibles de composición.
114. **Puerto de entrada:** interfaz receptora.
115. **Puerto de salida:** interfaz emisora.
116. **Puerto oculto:** conexión interna no expuesta.
117. **Conector:** objeto que acopla puertos.
118. **Separador:** subestructura cuya retirada desacopla partes.
119. **Interfaz de corte:** frontera producida por una separación.
120. **Frontera de composición:** zona identificada al ensamblar.
121. **Mapa de refinamiento:** reemplaza una unidad por una estructura más fina.
122. **Mapa de abstracción:** colapsa detalles preservando relaciones declaradas.
123. **Agregación:** combinación de elementos en una unidad.
124. **Desagregación:** expansión de una unidad en componentes.
125. **Relación jerárquica padre-hijo:** dependencia de contención estructural.

## F. Dinámica y concurrencia: 126–150
126. **Estado:** configuración estructural instantánea.
127. **Estado inicial:** configuración de partida distinguida.
128. **Estado terminal o aceptante:** configuración final distinguida.
129. **Transición:** cambio permitido entre estados.
130. **Acción estructural:** clase de transición.
131. **Evento:** ocurrencia individual de una transición.
132. **Guarda:** condición de habilitación.
133. **Actualización:** modificación producida por una transición.
134. **Entrada:** dato externo consumido.
135. **Salida:** dato externo producido.
136. **Observación:** proyección visible de un estado.
137. **Reloj:** variable temporal estructurada.
138. **Marca temporal:** posición de un evento en el tiempo.
139. **Duración:** extensión temporal de una transición.
140. **Trayectoria:** sucesión temporal de estados.
141. **Ejecución:** secuencia válida de transiciones.
142. **Traza:** proyección observable de una ejecución.
143. **Planificador:** regla de selección de transiciones.
144. **Relación de habilitación:** indica qué eventos pueden ocurrir.
145. **Relación de conflicto:** eventos mutuamente excluyentes.
146. **Relación de independencia:** eventos intercambiables.
147. **Sincronización:** ocurrencia conjunta obligatoria.
148. **Recurso:** entidad requerida o producida.
149. **Token:** unidad móvil de disponibilidad.
150. **Tasa de transición:** intensidad cuantitativa de cambio.

## G. Lógica y restricciones: 151–175
151. **Fórmula atómica:** afirmación relacional elemental.
152. **Valor de verdad:** resultado semántico de una fórmula.
153. **Negación lógica:** inversión de verdad.
154. **Conjunción:** satisfacción simultánea.
155. **Disyunción:** satisfacción alternativa.
156. **Implicación:** dependencia lógica.
157. **Cuantificador universal:** condición sobre todos los elementos.
158. **Cuantificador existencial:** condición sobre algún elemento.
159. **Existencia única:** existencia de exactamente un testigo.
160. **Modalidad de posibilidad:** verdad en alguna transición o extensión.
161. **Modalidad de necesidad:** verdad en todas las transiciones o extensiones.
162. **Operador temporal siguiente:** verdad en el estado posterior.
163. **Operador temporal hasta:** persistencia hasta otra condición.
164. **Operador temporal pasado:** referencia a estados previos.
165. **Relación de satisfacción:** vincula estructura y fórmula verdadera.
166. **Restricción:** condición que limita modelos válidos.
167. **Restricción dura:** condición obligatoria.
168. **Restricción blanda:** condición optimizable o penalizable.
169. **Ecuación:** igualdad obligatoria entre términos.
170. **Inecuación:** relación de orden entre términos.
171. **Regla de reescritura:** sustitución dirigida de patrones.
172. **Regla de inferencia:** producción de conclusiones desde premisas.
173. **Premisa:** condición de entrada de una inferencia.
174. **Conclusión:** resultado de una inferencia.
175. **Testigo de prueba:** objeto que certifica una afirmación.

## H. Correspondencia y síntesis: 176–200
176. **Relación de correspondencia:** conjunto de pares candidatos.
177. **Mapa candidato:** asignación aún no verificada.
178. **Mapa inyectivo:** no identifica elementos distintos.
179. **Mapa sobreyectivo:** cubre todo el codominio.
180. **Biyección:** mapa inyectivo y sobreyectivo.
181. **Isomorfismo parcial:** biyección preservante sobre subestructuras.
182. **Homomorfismo:** mapa que preserva operaciones y relaciones positivas.
183. **Monomorfismo:** morfismo cancelable por la izquierda.
184. **Epimorfismo:** morfismo cancelable por la derecha.
185. **Automorfismo:** isomorfismo de una estructura consigo misma.
186. **Antiisomorfismo:** isomorfismo que invierte una orientación declarada.
187. **Permutación de clases:** renombrado permitido de clases equivalentes.
188. **Transporte de relaciones:** traslado de tuplas mediante un mapa.
189. **Transporte de operaciones:** conjugación de operaciones mediante biyecciones.
190. **Transporte de constantes:** envío de puntos distinguidos.
191. **Imagen inversa:** traslado contravariante de subconjuntos o relaciones.
192. **Imagen directa:** traslado covariante de elementos o relaciones.
193. **Producto fibrado:** sincronización sobre una interfaz común.
194. **Pushout:** ensamblaje por identificación de interfaces.
195. **Igualador:** subobjeto donde dos mapas coinciden.
196. **Coigualador:** cociente que fuerza la coincidencia de dos mapas.
197. **Restricción de emparejamiento:** condición local sobre correspondencias.
198. **Testigo de consistencia:** evidencia de que un emparejamiento preserva estructura.
199. **Obstrucción:** evidencia finita contra una correspondencia.
200. **Cuadrado conmutativo:** condición de compatibilidad entre mapas.

## I. Magnitudes y pesos: 201–225
201. **Peso natural:** multiplicidad o magnitud discreta no negativa.
202. **Peso entero:** magnitud discreta con signo.
203. **Peso real:** magnitud escalar continua.
204. **Peso vectorial:** magnitud con varias componentes.
205. **Peso matricial o tensorial:** magnitud multilineal.
206. **Coste:** valor que debe minimizarse.
207. **Capacidad:** límite cuantitativo de uso.
208. **Flujo:** cantidad transportada por incidencias.
209. **Medida de probabilidad:** medida normalizada.
210. **Distribución:** asignación probabilística a resultados.
211. **Núcleo estocástico:** distribución condicionada por un estado.
212. **Medida general:** asignación aditiva de tamaño.
213. **Densidad:** representación local de una medida.
214. **Funcional de esperanza:** promedio ponderado de observables.
215. **Valoración:** asignación compatible con un semianillo.
216. **Norma:** magnitud compatible con escala y suma.
217. **Seminorma:** norma que puede anular elementos no nulos.
218. **Producto interno:** forma bilineal o sesquilineal.
219. **Coste de distancia:** penalización entre elementos.
220. **Energía:** funcional cuantitativo global.
221. **Potencial:** magnitud local generadora de diferencias.
222. **Función de rango:** nivel ordinal o dimensional.
223. **Graduación:** partición por grados.
224. **Nivel de filtración:** momento de aparición en una estructura anidada.
225. **Umbral estructural:** valor explícito que activa una relación.

## J. Canonización y verificación: 226–250
226. **Código canónico:** representación independiente del etiquetado.
227. **Orden canónico:** orden determinado por la estructura.
228. **Celda de partición:** conjunto de elementos aún indistinguibles.
229. **Operador de refinamiento:** divide celdas mediante relaciones.
230. **Individualización:** fija temporalmente un elemento candidato.
231. **Marcador de órbita:** identifica elementos intercambiables por automorfismos.
232. **Restricción de estabilizador:** obliga a fijar determinados elementos.
233. **Generador de simetría:** permutación que genera automorfismos.
234. **Certificado de isomorfismo:** biyección completa verificable.
235. **Contraejemplo local:** incidencia concreta no preservada.
236. **Vector de invariantes:** colección de filtros estructurales.
237. **Patrón:** subestructura parametrizada.
238. **Plantilla de motivo:** patrón destinado al conteo.
239. **Subestructura prohibida:** patrón cuya aparición invalida un modelo.
240. **Indicador de inducción:** exige preservar relaciones presentes y ausentes.
241. **Constructor de caminos:** composición sucesiva de incidencias.
242. **Constructor de paseos:** secuencia que admite repeticiones.
243. **Constructor de ciclos:** paseo cerrado con condiciones declaradas.
244. **Predicado de conexión:** detecta componentes relacionadas.
245. **Predicado de alcanzabilidad:** existencia de un camino dirigido.
246. **Clausura transitiva:** añade todas las relaciones alcanzables.
247. **Clausura de congruencia:** propaga igualdades a través de operaciones.
248. **Normalizador:** lleva expresiones a una forma estándar.
249. **Selector de representante canónico:** elige un miembro de cada órbita.
250. **Predicado de decisión:** acepta o rechaza un candidato estructural.

---

# II. Invariantes estructurales

## K. Signatura y cardinalidad: 251–275
251. **Número de clases.**
252. **Perfil de símbolos por clase y aridad.**
253. **Cardinalidad de cada portador.**
254. **Patrón de clases vacías y no vacías.**
255. **Patrón de coincidencia entre constantes.**
256. **Número de puntos distinguidos por clase.**
257. **Perfil de productos, coproductos y subtipos declarados.**
258. **Multiconjunto de aridades.**
259. **Matriz clase-dominio-codominio de los símbolos.**
260. **Cardinalidad del dominio efectivo de cada función parcial.**
261. **Cardinalidad de la imagen de cada función.**
262. **Multiconjunto de tamaños de fibras.**
263. **Tipo de partición inducido por el núcleo de cada función.**
264. **Número de puntos fijos de cada endofunción.**
265. **Tipo del grafo funcional de cada endofunción.**
266. **Cardinalidad de cada relación.**
267. **Cardinalidad del complemento de cada relación.**
268. **Número de tuplas diagonales en cada relación.**
269. **Distribución de patrones de igualdad dentro de las tuplas.**
270. **Cardinalidades de las proyecciones coordenadas de cada relación.**
271. **Cardinalidades de joins relacionales especificados.**
272. **Multiconjunto de participaciones por elemento y símbolo.**
273. **Patrón de verdad de los predicados nularios.**
274. **Tipo y tamaño de la subestructura generada por las constantes.**
275. **Diagrama atómico canónico de una estructura finita.**

## L. Incidencia, matrices y refinamiento: 276–300
276. **Multiconjunto de grados.**
277. **Multiconjunto de grados de entrada.**
278. **Multiconjunto de grados de salida.**
279. **Multiconjunto de grados con signo.**
280. **Multiconjunto de vectores de grado por tipo.**
281. **Multiconjunto de grados ponderados.**
282. **Número de bucles.**
283. **Multiconjunto de multiplicidades de aristas paralelas.**
284. **Multiconjunto de tamaños de hiperaristas.**
285. **Multiconjunto de codegrados entre vértices.**
286. **Rango de la matriz de incidencia sobre un cuerpo fijado.**
287. **Forma normal de Smith de la matriz de incidencia entera.**
288. **Polinomio característico de la matriz de adyacencia.**
289. **Perfil de bloques de Jordan de la adyacencia.**
290. **Valores singulares de la matriz de adyacencia.**
291. **Espectro del laplaciano.**
292. **Espectro del laplaciano normalizado.**
293. **Espectro del laplaciano sin signo.**
294. **Espectro de la matriz de distancias.**
295. **Permanente de la matriz de adyacencia.**
296. **Sucesión de trazas de potencias de la adyacencia.**
297. **Número de paseos cerrados de cada longitud.**
298. **Perfil de vecindades enraizadas por radio.**
299. **Cociente de la partición equitativa estable.**
300. **Histograma estable de Weisfeiler–Leman para dimensión fijada.**

## M. Conectividad, caminos y ciclos: 301–325
301. **Número de componentes débilmente conexas.**
302. **Número de componentes fuertemente conexas.**
303. **Multiconjunto de tamaños de componentes.**
304. **Tipo isomorfo del DAG de condensación.**
305. **Conectividad por vértices.**
306. **Conectividad por aristas.**
307. **Número de puntos de articulación.**
308. **Número de puentes.**
309. **Tipo isomorfo del árbol bloque-corte.**
310. **Diámetro.**
311. **Radio.**
312. **Multiconjunto de excentricidades.**
313. **Longitud del ciclo mínimo o cintura.**
314. **Longitud del ciclo máximo o circunferencia.**
315. **Longitud del ciclo dirigido mínimo.**
316. **Distribución del número de pares por distancia.**
317. **Multiconjunto de todas las distancias entre pares.**
318. **Órbita de la matriz de alcanzabilidad bajo permutaciones.**
319. **Tipo isomorfo de la clausura transitiva.**
320. **Tipo isomorfo de la reducción transitiva de un DAG.**
321. **Número de árboles generadores.**
322. **Rango cíclico o número ciclomático.**
323. **Distribución de ciclos por longitud.**
324. **Número de caminos simples por longitud.**
325. **Perfil de separadores por tamaño y tipo.**

## N. Invariantes algebraicos: 326–350
326. **Clase isomorfa de las tablas de operaciones.**
327. **Presencia y número de elementos identidad.**
328. **Número de ceros o elementos absorbentes.**
329. **Número de elementos idempotentes.**
330. **Número de unidades invertibles.**
331. **Número de divisores de cero.**
332. **Número de elementos nilpotentes.**
333. **Distribución de índices de nilpotencia.**
334. **Multiconjunto de órdenes de elementos.**
335. **Cardinalidad y tipo isomorfo del centro.**
336. **Tipo isomorfo del subobjeto de conmutadores.**
337. **Perfil de factores de la serie derivada.**
338. **Perfil de factores de la serie central inferior.**
339. **Multiconjunto de tamaños de clases de conjugación.**
340. **Tipo isomorfo del retículo de subgrupos o subálgebras.**
341. **Tipo isomorfo del retículo de ideales o congruencias.**
342. **Número mínimo de generadores.**
343. **Exponente algebraico.**
344. **Validez de la conmutatividad.**
345. **Validez de la asociatividad.**
346. **Perfil de identidades distributivas satisfechas.**
347. **Teoría ecuacional completa.**
348. **Tipo isomorfo del clon de operaciones término.**
349. **Perfil de clases de Green de un semigrupo.**
350. **Perfil de factores indecomponibles cuando existe unicidad.**

## O. Órdenes y retículos: 351–375
351. **Cardinalidad del conjunto ordenado.**
352. **Altura del orden.**
353. **Anchura del orden.**
354. **Distribución de elementos por rango.**
355. **Número de elementos mínimos.**
356. **Número de elementos máximos.**
357. **Número de cadenas por longitud.**
358. **Número de anticadenas por tamaño.**
359. **Tipo isomorfo del grafo de cobertura.**
360. **Tipo isomorfo del grafo de comparabilidad.**
361. **Tipo isomorfo del grafo de incomparabilidad.**
362. **Función de Möbius hasta permutación estructural.**
363. **Polinomio característico del poset graduado.**
364. **Dimensión de orden.**
365. **Número de extensiones lineales.**
366. **Número de ideales de orden.**
367. **Número de filtros de orden.**
368. **Número de átomos del retículo.**
369. **Número de coátomos.**
370. **Tipo del poset de elementos join-irreducibles.**
371. **Tipo del poset de elementos meet-irreducibles.**
372. **Número de elementos complementados.**
373. **Perfil distributivo, modular y semimodular.**
374. **Clase isomorfa de las tablas de ínfimo y supremo.**
375. **Multiconjunto de tipos isomorfos de intervalos.**

## P. Simetría y descomposición: 376–400
376. **Orden del grupo de automorfismos.**
377. **Tipo isomorfo del grupo de automorfismos.**
378. **Multiconjunto de tamaños de órbitas.**
379. **Multiconjunto de tamaños de estabilizadores.**
380. **Tamaño mínimo de una base de la acción.**
381. **Número distinguidor.**
382. **Número de presentaciones etiquetadas en la órbita.**
383. **Tipo del árbol de descomposición modular.**
384. **Tipo del árbol SPQR.**
385. **Anchura arbórea.**
386. **Anchura de camino.**
387. **Anchura de ramas.**
388. **Clique-width.**
389. **Rank-width.**
390. **Multiconjunto de separadores mínimos.**
391. **Perfil de tamaños de los \(k\)-cores.**
392. **Degeneración del grafo.**
393. **Distribución de tamaños de cliques maximales.**
394. **Distribución de tamaños de conjuntos independientes maximales.**
395. **Número cromático.**
396. **Polinomio cromático.**
397. **Polinomio de independencia.**
398. **Polinomio de emparejamientos.**
399. **Polinomio de Tutte.**
400. **Perfil de factores primos respecto de una composición fijada.**

## Q. Dinámica, lenguajes y concurrencia: 401–425
401. **Número de estados.**
402. **Número de estados iniciales.**
403. **Número de estados aceptantes.**
404. **Número de transiciones por tipo de acción.**
405. **Multiconjunto de grados de ramificación.**
406. **Número de estados alcanzables.**
407. **Número de estados coalcanzables.**
408. **Número de bloqueos o deadlocks.**
409. **Perfil de componentes de livelock.**
410. **Tipo isomorfo del grafo de transiciones.**
411. **Lenguaje aceptado, salvo renombrados de alfabeto permitidos.**
412. **Lenguaje de trazas.**
413. **Tipo del cociente por bisimulación.**
414. **Tipo del cociente inducido por simulación mutua.**
415. **Tamaño del autómata determinista mínimo.**
416. **Estructura de clases de Myhill–Nerode.**
417. **Espectro de longitudes de palabras sincronizadoras.**
418. **Perfil de clases recurrentes de una cadena de Markov.**
419. **Periodos de las clases recurrentes.**
420. **Conjunto de distribuciones estacionarias hasta renombrado.**
421. **Espectro de la matriz de transición.**
422. **Tasa de entropía para la distribución inicial especificada.**
423. **Teoría temporal satisfecha por el sistema.**
424. **Conjunto de órdenes parciales causales de las ejecuciones.**
425. **Tipo del grafo de independencia y conflicto de eventos.**

## R. Topología y homología: 426–450
426. **Número de componentes conexas topológicas.**
427. **Número de componentes conexas por caminos.**
428. **Característica de Euler.**
429. **Números de Betti.**
430. **Grupos de homología.**
431. **Grupos de cohomología.**
432. **Grupos de homotopía.**
433. **Tipo isomorfo del grupo fundamental.**
434. **Tipo de homotopía.**
435. **Tipo de homeomorfismo.**
436. **Orientabilidad.**
437. **Dimensión topológica o combinatoria.**
438. **Número de componentes de frontera.**
439. **Género.**
440. **Vector \(f\) de un complejo celular o simplicial.**
441. **Vector \(h\).**
442. **Tipo isomorfo del poset de caras.**
443. **Formas normales de Smith de los operadores de borde.**
444. **Perfil de coeficientes de torsión.**
445. **Código de barras de homología persistente.**
446. **Tipo isomorfo del nervio de una cobertura distinguida.**
447. **Compacidad.**
448. **Perfil de conexión local y conexión por caminos local.**
449. **Perfil de axiomas de separación \(T_0,T_1,T_2,\ldots\).**
450. **Tipo isomorfo del retículo de abiertos o de clausuras.**

## S. Pesos, medidas y espectros cuantitativos: 451–475
451. **Peso total.**
452. **Multiconjunto de pesos.**
453. **Multiconjunto de grados ponderados.**
454. **Multiconjunto de capacidades.**
455. **Vector de valores mínimo y máximo.**
456. **Sucesión de momentos de los pesos.**
457. **Perfil de normas del tensor de pesos.**
458. **Rangos de las matricizaciones de un tensor.**
459. **Determinante de la adyacencia ponderada.**
460. **Espectro de la adyacencia ponderada.**
461. **Espectro del laplaciano ponderado.**
462. **Órbita de la matriz de caminos mínimos ponderados.**
463. **Órbita de la matriz de flujos máximos entre pares.**
464. **Perfil de cortes mínimos.**
465. **Valores óptimos de problemas estructuralmente definidos.**
466. **Función de partición.**
467. **Distribución de degeneraciones por nivel de energía.**
468. **Multiconjunto de masas de átomos de una medida.**
469. **Entropía de una distribución distinguida.**
470. **Cardinalidad o dimensión del soporte.**
471. **Espectro de la matriz de covarianza.**
472. **Órbita canónica de un núcleo estocástico.**
473. **Multiconjunto de tiempos esperados de retorno.**
474. **Multiconjunto de distancias de resistencia efectiva.**
475. **Función zeta o serie generadora de paseos ponderados.**

## T. Lógica, conteos y completitud: 476–500
476. **Teoría completa de primer orden.**
477. **Teoría existencial-positiva.**
478. **Teoría universal de Horn.**
479. **Teoría modal.**
480. **Teoría del fragmento guardado.**
481. **Multiconjunto de tipos lógicos de rango cuantificador \(k\).**
482. **Clase de equivalencia de Ehrenfeucht–Fraïssé a rango \(k\).**
483. **Número de homomorfismos desde cada estructura de prueba finita.**
484. **Número de homomorfismos hacia cada estructura de prueba finita.**
485. **Censo de subestructuras inducidas por tipo y tamaño.**
486. **Perfil de subestructuras prohibidas presentes o ausentes.**
487. **Vector de conteos de motivos.**
488. **Perfil de densidades de banderas estructurales.**
489. **Codificación canónica de relaciones y operaciones.**
490. **Presentación lexicográficamente mínima bajo reetiquetado.**
491. **Resumen inyectivo no truncado del código canónico.**
492. **Longitud descriptiva del código canónico bajo una codificación fija.**
493. **Complejidad de Kolmogórov de la forma canónica, salvo constante de máquina.**
494. **Tipo isomorfo del clon de polimorfismos de restricciones.**
495. **Espectro de números de soluciones de problemas CSP definibles.**
496. **Vector de verdad sobre una base lógica estructural fijada.**
497. **Mazo de subestructuras obtenidas eliminando un elemento.**
498. **Mazo de subestructuras obtenidas eliminando una incidencia.**
499. **Sentencia de Scott para estructuras contables.**
500. **Órbita completa bajo el grupo de reetiquetados tipados.**

---

## Protocolo para evitar la analogía superficial
1. **Fijar la signatura:** declarar qué clases, relaciones, operaciones y datos cuantitativos cuentan.
2. **Eliminar nombres externos:** sustituir identificadores por variables tipadas.
3. **Comparar invariantes:** cualquier discrepancia descarta el isomorfismo.
4. **Refinar correspondencias:** usar incidencia, vecindades, operaciones y órbitas.
5. **Construir biyecciones por clase:** sin mezclar tipos salvo que se permita explícitamente.
6. **Verificar conmutación exacta:** \(\varphi(F(a_1,\ldots,a_n)) = F'(\varphi(a_1),\ldots,\varphi(a_n)).\)
7. **Verificar relaciones en ambos sentidos:** \(R(\vec a)\iff R'(\varphi(\vec a)).\)
8. **Entregar certificado u obstrucción:** una biyección completa, o una diferencia estructural concreta.
