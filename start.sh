#!/bin/bash

# CORTEX Unified Start Script
# Author: borjamoskv
# Reality Level: C5-REAL

export PORT=8080
FORCE_NODE=0
FORCE_PYTHON=0

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --node) FORCE_NODE=1 ;;
        --python) FORCE_PYTHON=1 ;;
        --port) PORT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "[CORTEX] Initializing Sovereign Telemetry Panel..."
echo "[CORTEX] Target Port: $PORT"

if [ $FORCE_NODE -eq 1 ]; then
    echo "[CORTEX] Forcing Node.js Server..."
    npm run start:node
    exit 0
elif [ $FORCE_PYTHON -eq 1 ]; then
    echo "[CORTEX] Forcing Python Server..."
    npm run start:python
    exit 0
fi

# Auto-detect
if command -v npm &> /dev/null; then
    echo "[CORTEX] Auto-detected Node.js environment."
    npm run start:node
elif command -v python3 &> /dev/null; then
    echo "[CORTEX] Auto-detected Python 3 environment."
    npm run start:python
else
    echo "[ERROR] Neither Node.js nor Python 3 found. Anergy level critical. System halt."
    exit 1
fi
