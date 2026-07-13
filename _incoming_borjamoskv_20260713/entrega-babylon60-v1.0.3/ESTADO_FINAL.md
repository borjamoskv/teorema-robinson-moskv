# ESTADO FINAL — auditoría babylon60 · v1.0.3 (2026-07-13)

**Rama:** `audit/fixes-2026-07-13` · 20 commits sobre base `e0b8ce9` · tip `552a58a`
**Bundle:** `fixes.bundle` (sha256 `7f9f2add75d0e95b…`) · **Parches:** `patches-es/` (20)
**Verificado tras el corte:** babylon60 compila, versión 1.0.3 consistente en los 4 consumidores (`pyproject`, `__init__`, CHANGELOG, shim cortex), bundle íntegro, 44 tests dirigidos en verde.

## Los 20 commits

```
03f4b93 docs: README/QUICKSTART reales con rutas verificadas; identidad del repo corregida
588ec43 security: motores JIT con exec() tras el flag BABYLON60_ENABLE_JIT (off por defecto)
c2be19d fix(router): fail-fast si faltan claves de proveedor; fuera sk-ant-fallback
72c535e refactor(guards): fuente única de verdad para los patrones de secretos
302b382 chore: fuera media ajena, web de artista y salida de escáneres commiteada
bb59186 ci: workflows 27 -> 6; fuera los crons de telemetría/lore
61c63af chore(docs): auditorías y lore fuera de la raíz; script de purga de historial
9923087 fix(tests): compatibilidad con Python 3.10
b262071 docs(security): flag JIT y modelo de amenaza documentados; changelog del lote
47e38f5 fix(storage): portabilidad SQLite <3.38 — sustituir unixepoch()
a91311d fix(tests): fixtures de lineage al contrato meta['lineage']; skip de SMT sin z3
87fd139 fix(deps): eliminar chromadb — vulnerabilidad crítica sin parche y cero usos
fa7e8a9 fix(build): eliminar 5 symlinks rotos a rutas absolutas locales
1a132f8 fix(packaging): incluir py.typed en el wheel
aa15a29 test(security): regresión del gate JIT (off por defecto, opt-in con flag)
bee253c chore: eliminar scripts de render UTBH y ruta absoluta hardcodeada
352c94b release: 1.0.3
e15d00f release: sincronizar babylon60.__version__ a 1.0.3
3bc8b39 chore: eliminar redundancias — _archived/ y duplicados de docs (−259 archivos)
552a58a refactor(paths): centralizar rutas ~/.gemini en core/paths.py
```

## Commit 20 — purga de rutas `~/.gemini` hardcodeadas

28 call sites en 27 módulos (`vsa_engine`, `singularity_tools`, `cost_scheduler`, `duress_guard`, `adapter`, observability al completo, etc.) apuntaban a `~/.gemini/...` en literal. Ahora todo deriva de constantes canónicas en `babylon60/core/paths.py`, cada una env-overridable con el patrón existente `MOSKV_*`/`CORTEX_*`: `GEMINI_HOME`, `ANTIGRAVITY_DIR`, `KNOWLEDGE_DIR`, `BRAIN_DIR`, `SCRATCH_DIR`, `GEM_CONFIG_DIR`, `GEM_SKILLS_DIR`, `METRICS_DIR`, `SNAPSHOTS_DIR`, `MEMORY_VAULT_DIR`, `APOPTOSIS_SEED_FILE`.

Los **defaults quedan intactos** (siguen resolviendo a `~/.gemini/...`): en tu Mac nada cambia de sitio; fuera de tu Mac basta exportar `MOSKV_GEMINI_HOME` (o cualquier nodo concreto) para relocalizar el árbol entero. `CORTEX_KNOWLEDGE_DIR`, el único override que ya existía, se sigue respetando. Quedan sin tocar, a propósito: `gemini_cache.py`/`provider.py` (API de Gemini, no rutas) y las entradas `".gemini"` en listas de exclusión de escáneres.

Verificación del commit: grep-gate a cero fuera de `paths.py`, compileall limpio, ruff limpio en los 29 archivos tocados, 44 tests dirigidos en verde (`version_consistency`, `contract_adapter`, `duress_guard`, `cost_scheduler`), smoke-import de los 27 módulos (2 saltados por deps externas ausentes en sandbox: watchdog, sklearn). Hallazgo preexistente anotado sin tocar: `observability/mock_data.py` escribe en el log de métricas en tiempo de import y revienta si el directorio no existe — igual antes y después del cambio.

## Decisiones que NO son omisiones

- **Pepper de auth:** se queda como está. Fail duro en cloud, warn en local — el diseño es correcto; el "fallback inseguro" de los logs era el modo local.
- **ci.yml:** verificado real (change-scope, rust-check, lint, pip-audit+bandit, pytest con junitxml, build, docker). Sin cambios.
- **24 redundancias restantes:** intencionadas o de bajo valor — fixtures de ledger duplicados a propósito (tests de mutación), boilerplate de openapi-generator en los 3 SDKs, y crates Rust/SQL que no se pueden consolidar sin `cargo` para verificar la build. Ahí la mejora se vuelve riesgo.
- **1.0.2 → 1.0.3:** el CHANGELOG tenía un 1.0.2 histórico (28-jun) que nunca llegó a PyPI; con cambios sustanciales nuevos, el tag correcto es v1.0.3.

## Cómo aplicar

```bash
# En tu clon local de babylon60 (debe contener e0b8ce9):
git fetch /ruta/a/fixes.bundle audit/fixes-2026-07-13:audit/fixes-2026-07-13
# — o, si prefieres parches:
git checkout -b audit/fixes-2026-07-13 e0b8ce9 && git am patches-es/*.patch
```

## Checklist restante (tuyo)

1. Aplicar la rama y **push**.
2. Revisar alertas de **Security** en GitHub tras el push.
3. **Purga de historial** (secretos ya commiteados) con el script incluido en `61c63af` — antes del tag.
4. `git tag v1.0.3` y publicar.
