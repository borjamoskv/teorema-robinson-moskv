#!/usr/bin/env bash
# [C5-REAL] SOBERANÍA FÍSICA: SBOM & AUDITORÍA DE BINARIOS
# Requiere: syft, grype instalados localmente.

set -euo pipefail

WORKSPACE="${BABYLON_WORKSPACE:-/Users/borjafernandezangulo/30_BABYLON-60}"
OUT_DIR="$WORKSPACE/cortex/artifacts/sbom"

echo -e "\033[1;34m[CORTEX-SBOM]\033[0m Iniciando forja de SBOM local..."
mkdir -p "$OUT_DIR"

# 1. Escaneo Estructural (Syft)
syft scan dir:"$WORKSPACE" -o spdx-json="$OUT_DIR/babylon60_sbom.json" > /dev/null
echo -e "\033[1;32m[+] SBOM cristalizado:\033[0m $OUT_DIR/babylon60_sbom.json"

# 2. Auditoría de Vulnerabilidades (Grype)
grype sbom:"$OUT_DIR/babylon60_sbom.json" -o table > "$OUT_DIR/babylon60_audit_report.txt"
echo -e "\033[1;32m[+] Reporte de vulnerabilidades anclado:\033[0m $OUT_DIR/babylon60_audit_report.txt"

# 3. Hash Ledger
HASH=$(shasum -a 256 "$OUT_DIR/babylon60_sbom.json" | awk '{print $1}')
echo -e "\033[1;33m[LEDGER HASH]\033[0m $HASH"
