<!-- C5-REAL EXERGY CERTIFIED -->
# LARSA-120 ENGINE

**Motor de Ejecución de IA, Memoria Determinista (cortex-persist) y Orquestación**

El núcleo de infraestructura de agentes de Inteligencia Artificial del ecosistema Teorema-Robinson-Moskv.

## Módulos del Sistema
- **`src/babylon-60/`**: Frontend IDE Visual Cortex con renderizado reactivo y telemetría de memoria compartida.
- **`src/03_state/scitt_ledger/`**: Persistencia de estado, event ledger y base de datos vectorial para IA.
- **`src/02_engines/mushushu_0/`**: Middleware de protección de costes, límites de API y failover.
- **`src/moskv-daemon/`**: Kernel determinista Ring-0 en Rust puro con IPC Lock-Free EBR.

## Modos de Uso
- Iniciar frontend Babylon-60: `cd src/babylon-60 && npm run dev`
- Verificación preflight: `bash scripts/preflight.sh`

