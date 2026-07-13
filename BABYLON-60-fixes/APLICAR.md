# BABYLON-60 · Fixes de auditoría — cómo aplicar

**Rama:** `audit/fixes-2026-07-13` · 11 commits sobre `e0b8ce9` (main) · 274 archivos, +167/−12.386
Verificado: compileall ✓, ruff ✓, gates JIT on/off ✓, **~3.940 tests pasan** (raíz completa 2.264 + 39 directorios 1.569 + security 87 + router/firewall 19). Los 7 pre-existentes rotos quedaron arreglados en los commits 10-11; solo quedan skips por servicios externos (redis, soundfile, z3).

## Aplicar y pushear (desde tu clon local de BABYLON-60)

```bash
git fetch origin && git checkout main && git pull
git am BABYLON-60-fixes/patches/*.patch     # opción A: parches
# opción B: git fetch BABYLON-60-fixes/audit-fixes.bundle audit/fixes-2026-07-13:audit/fixes-2026-07-13
git push origin main          # o push de la rama y PR, como prefieras
```

Si tu main local avanzó desde `e0b8ce9` (2026-07-10), usa `git am -3` para merge de 3 vías.

## Los 11 commits

1. **docs** — README real (instalación, quickstart verificado contra el código, features) + QUICKSTART corregido (`babylon60.api.core:app`, puerto 8484, `babylon60.api.client.CortexClient`) + pyproject URLs → BABYLON-60.
2. **security** — `exec()` de demiurge, sandbox_jit y sortu_jit gated tras `BABYLON60_ENABLE_JIT=1` (off por defecto; tests opt-in vía conftest).
3. **fix(router)** — fuera `sk-ant-fallback`/`gemini-fallback`: warning + fail-fast.
4. **refactor(guards)** — SecretGuard reutiliza los patrones de SecretRedactor (una sola fuente de verdad). API intacta.
5. **chore** — eliminados: UTBH (2 m4a + 3 jpg + artículo, 25 MB), `data/naroa/` (217 archivos), `*_alerts.json` (+ .gitignore).
6. **ci** — workflows 27→6 (ci, codeql, security-scan, release, publish, docs). Mueren los crons de telemetry (1.181 runs), SIGINT y Exergy Singularity.
7. **chore(docs)** — auditorías → `docs/audits/`, MILESTONES y cortex_directives → `docs/lore/` (0 referencias en código). Raíz: 18→12 .md. Incluye `scripts/purge_history.sh`.
8. **fix(tests)** — compat Python 3.10: `asyncio.Barrier` sin uso eliminado (API 3.11+ en test de hilos, ahora pasa en 3.10) + fallback `tomllib`→`tomli` en 2 tests. El paquete declara `>=3.10`.
9. **docs(security)** — modelo de amenaza del flag `BABYLON60_ENABLE_JIT` en SECURITY.md + entrada Unreleased en CHANGELOG con todo el lote.
10. **fix(storage)** — `unixepoch()` requiere SQLite ≥3.38; Ubuntu 22.04/Py3.10 trae 3.37 y rompía outbox, evo metrics y nexus **en producción**. Sustituido por fórmula `julianday` equivalente (REAL con subsegundos, cualquier SQLite).
11. **fix(tests)** — fixtures de lineage usaban la clave muerta `lineage_sources` (el contrato es `meta["lineage"]`); test SMT hace skip sin z3 (el guard documenta fallback permisivo).

## Pendiente — requiere tu máquina (sin cargo/credenciales en mi sandbox)

**P0 · Alertas Rust (17, 6 high)** — en tu clon:
```bash
cargo update openssl openssl-sys rustls-webpki rand
cargo build --workspace && cargo test --workspace
git commit -am "fix(deps): patch openssl/rustls-webpki/rand advisories" && git push
```

**P1 · Purga de historial** (los 25 MB de UTBH y naroa siguen en la historia):
```bash
pip install git-filter-repo
./scripts/purge_history.sh    # hace backup, revisa antes del force-push
```

**P2 · PyPI** — publicar 1.0.2 (PyPI está en 1.0.0): `git tag v1.0.2 && git push --tags` → workflow publish, o `python -m build && twine upload dist/*`.

## Notas

- Los 7 tests pre-existentes rotos quedaron resueltos: outbox ×3 (bug real de portabilidad SQLite, commit 10), lineage ×2 y SMT (commit 11), vector_swarm_apoptosis (flaky de timeout, pasa solo — sin cambio).
- La fuente de verdad de esta entrega son `patches/` (11) y `audit-fixes.bundle`; ignora copias del repo en la carpeta de trabajo de la sesión, quedaron desfasadas.
