# BABYLON-60 · Estado final — 2026-07-13

**Rama:** `audit/fixes-2026-07-13` · **19 commits** en español sobre `e0b8ce9` · **release v1.0.3**
Este archivo es la referencia al día. APLICAR.md refleja una versión anterior (11 commits) — ignora su sección de `cargo update` y su número de tag.

## Aplicar

```bash
# desde tu clon local de BABYLON-60:
git checkout main && git pull
git fetch /ruta/a/Teorema-Robinson-Moskv/BABYLON-60-fixes/audit-fixes.bundle \
    audit/fixes-2026-07-13:audit/fixes-2026-07-13
git merge audit/fixes-2026-07-13 && git push origin main
```

Alternativa: `git am -3 patches-es/*.patch` (15 parches). ⚠️ Usa `patches-es/`, NO `patches/` (contiene restos viejos en inglés que no pude borrar desde la sesión).

## Qué cambió desde APLICAR.md (commits 12-18)

12. **fix(deps)** — eliminado `chromadb` 1.5.9: inyección de código pre-auth **sin parche existente** (GHSA-f4j7-r4q5-qw2c) y cero usos en el código. −21 paquetes del lock.
13. **fix(build)** — eliminados 5 symlinks rotos apuntando a rutas absolutas de tu Mac. Rompían `python -m build` (fatal), el caché de ruff (E902) y cualquier CI ajeno.
14. **fix(packaging)** — `py.typed` creado e incluido en el wheel (el classifier "Typing :: Typed" lo prometía sin cumplirlo).
15. **test(security)** — regresión del gate JIT, 4 tests, ambos estados del flag.
16. **chore** — eliminados scripts de render UTBH (`c5_parallel_render*`, `c5_repair_audio`, con rutas `/Users/.../Downloads`) y la ruta absoluta de `generate_ecosystem_map.py` → `CORTEX_ARTIFACTS_DIR`. Cero `/Users/...` en código activo.
17. **release: 1.0.3** — 1.0.2 nunca llegó a PyPI y había cambios sustanciales; se sube a 1.0.3 para que el tag cuadre con pyproject (publish.yml lo valida). CHANGELOG consolidado.
18. **release** — `babylon60.__version__` sincronizado a 1.0.3 (el test de consistencia exige módulo = pyproject = shim cortex = CHANGELOG; se había quedado atrás).
19. **chore(redundancias)** — −259 archivos: `_archived/` completo (4 MB, aislado, 98 ficheros Solidity de terceros vendorizados con forge-std duplicado en dos submódulos), `docs/blog/blog/*.html` (ruta duplicada, copia byte a byte de `public/blog/`) y `LEGION_93_MAPPING.md` duplicado. Nada importado desde código activo.

**Redundancias restantes (24, deliberadamente intactas):** fixtures de ledger duplicados a propósito para tests de mutación, boilerplate estándar de openapi-generator en los 3 SDKs, y un par crate Rust/SQL cuya consolidación no se puede verificar sin `cargo` en el sandbox. Tocarlas sería temerario sin poder ejecutar la build completa.

## Verificación final

- **Wheel construye e instala**: `cortex_persist-1.0.2` (4,1 MB, 1.925 archivos, sin tests/docs/basura), importa OK, 4 entry points, py.typed dentro. Antes de estos fixes `python -m build` **fallaba** — tu publicación en PyPI habría muerto.
- **ruff: All checks passed** en babylon60 completo (el E902 era el symlink roto).
- **Dependencias (OSV.dev)**: Python 0/250 · npm 0/611 · Rust 0/83. Las 17 alertas de Dependabot en GitHub son obsoletas (el Cargo.lock actual ya ni contiene openssl/rustls-webpki) — se cierran al re-escanear tras tu push. **`cargo update` ya no es necesario**; ignora esa sección de APLICAR.md.
- ~3.940 tests en verde en sweep completo; los 7 pre-existentes rotos, arreglados (commits 8, 10, 11).

## Ya aplicado en tu repo local (Teorema-Robinson-Moskv)

`c5_remotion_video`: 2 high de axios (CSRF+SSRF) resueltas con override `"axios": "^1.12.2"` — package.json y lock ya escritos y verificados a 0. Te queda `npm install` ahí y commitear en ese repo.

## Tu checklist final

1. Aplicar rama + push (arriba).
2. GitHub: ci.yml verde · pestaña Security → alertas cerrándose solas.
3. `pip install git-filter-repo && ./scripts/purge_history.sh` (backup automático; revisa antes del force-push).
4. `git tag v1.0.3 && git push --tags` → publish.yml (OIDC, exige tag == versión de pyproject; ya cuadran en 1.0.3). El wheel `cortex_persist-1.0.3` está verificado: construye, instala e importa 1.0.3.
