#!/bin/bash
# C5-REAL SOTA Engine Daemon
# Orquestador Ouroboros para ingestar, cristalizar y publicar señales SOTA.

DIR="$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage"
SCRIPTS="$DIR/scripts/sota"
VENV="$DIR/.venv/bin/activate"

source $VENV

echo "[C5-REAL] Iniciando Adquisición de Señales..."
python3 $SCRIPTS/ingestor_arxiv.py
python3 $SCRIPTS/ingestor_github.py
python3 $SCRIPTS/ingestor_cybersec.py

echo "[C5-REAL] Iniciando Cristalización Isomórfica..."
python3 $SCRIPTS/cristalizador_nodos.py

echo "[C5-REAL] Generando output para Substack Premium..."
python3 $SCRIPTS/substack_publisher.py

echo "[C5-REAL] Flujo completado. Nodos disponibles para API FastAPI."
