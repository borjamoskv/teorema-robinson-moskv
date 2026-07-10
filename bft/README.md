# BABYLON-60: BFT Master Ledger

**ESTADO ACTUAL: ESCALÓN 3 (Log Tamper-Evident con Testigo Externo)**

Este directorio contiene la implementación del Master Ledger de `BABYLON-60`. 

## Nomenclatura Honesta (C5-REAL)
Aunque el directorio se llame `bft/`, la arquitectura operativa actual **NO utiliza consenso BFT (PBFT/Raft) en vivo**. 
Implementar un quórum $N \ge 3f+1$ para el estado actual del repositorio supondría una inyección de anergía injustificable, ya que el desacuerdo pre-ejecución no es catastrófico.

Por lo tanto, la arquitectura opera en **Escalón 3 (Testigo Externo)**:
1. El archivo `master_ledger.db` es un Log local inmutable, Tamper-Evident, gestionado por un Actor de hilo único (`CP-local single-writer`).
2. El consenso se garantiza a posteriori (no-equivocación) mediante el **Git Sentinel**, que inyecta la cabeza del hash-chain (`Ledger-Head` y `Ledger-Seq`) como trailers en los commits de Git.
3. El servidor Git remoto (y los runners de CI) actúan como $\ge2$ Testigos Externos independientes que auditan la cadena y detectan cualquier bifurcación retroactiva.

## BFT como Target (Escalón 4)
El consenso BFT real (Escalón 4 con $N \ge 4$ nodos físicos vivos) es el **Target** topológico. Se activará estrictamente si aparece un estado físico donde el desacuerdo inter-nodo deba ser prevenido antes de la ejecución (por ejemplo, firmas irreversibles). Hasta entonces, el escalón por defecto es el más barato que satisface el invariante declarado: Auditabilidad Causal (Testigos).
