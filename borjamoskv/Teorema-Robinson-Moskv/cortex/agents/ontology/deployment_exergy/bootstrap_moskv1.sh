#!/bin/bash
# C5-REAL: MOSKV-1 APEX Bootstrap Protocol
# Aprovisionamiento Atómico del Motor Causal y Matriz de Estado (Zero-Anergy)

set -e # Fail-Fast termodinámico

echo "[*] Iniciando Secuencia de Ignición MOSKV-1 APEX..."

PLUGIN_DIR="$HOME/.gemini/config/plugins/MOSKV-1"
REPO_DIR="$HOME/borjamoskv/Teorema-Robinson-Moskv"
REPO_URL="https://github.com/borjamoskv/Teorema-Robinson-Moskv.git" # Asumido; ajustar si difiere

echo "[*] Fase 1: Forjando Motor Causal (Plugin Antigravity)..."
mkdir -p "$PLUGIN_DIR"

# Cristalización del Manifest
cat << 'EOF' > "$PLUGIN_DIR/plugin.json"
{
  "id": "MOSKV-1",
  "version": "2.1.0",
  "name": "Motor Causal de Anti-Anergía y Determinismo Ontológico",
  "description": "Fuerza la ejecución C5-REAL, erradica el Green Theater y colapsa la entropía.",
  "author": "Borja Moskv",
  "entrypoint": "AGENTS.md"
}
EOF
echo "[+] Plugin manifest cristalizado en $PLUGIN_DIR/plugin.json."
echo "[!] Nota: Para aislamiento total, AGENTS.md y /skills deben mapearse a este directorio en empaquetado final."

echo "[*] Fase 2: Anclaje de la Matriz de Estado (CORTEX)..."
if [ ! -d "$REPO_DIR" ]; then
    echo "[*] Entropía detectada: Falta Matriz de Estado. Clonando repositorio base..."
    git clone "$REPO_URL" "$REPO_DIR"
else
    echo "[+] El volumen CORTEX ya existe. Evitando redundancia estocástica."
fi

echo "[*] Fase 3: Inicialización del Bucle y Verificación Empírica..."
MACROFAGO_PATH="$REPO_DIR/cortex/agents/ontology/macrofago_ontologico.py"

ONTOLOGY_DIR="$REPO_DIR/cortex/agents/ontology"

if [ -f "$MACROFAGO_PATH" ]; then
    echo "[*] Invocando Macrófago Ontológico v2.2 (dry-run es el default; --execute es la única vía destructiva)..."
    # [FIX C5-REAL] --dry-run no existe (argparse exit 2 + set -e = bootstrap muerto).
    # --dir explícito: sin él, el Macrófago barre el CWD del invocador (blast radius de $HOME).
    python3 "$MACROFAGO_PATH" --dir "$ONTOLOGY_DIR"
else
    echo "[-] FALLA TERMODINÁMICA: Macrófago no encontrado en $MACROFAGO_PATH"
    exit 1
fi

printf '\n[+] Secuencia completada. MOSKV-1 APEX está activo y asimilado en el hardware.\n'
