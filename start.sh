#!/bin/bash

# CORTEX Unified Start Script (Refactored: Causal Debt 0)
# Author: borjamoskv
# Reality Level: C5-REAL

export PORT=8080

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "[CORTEX] Initializing Sovereign Telemetry Panel..."
echo "[CORTEX] Target Port: $PORT"

# Clean up any orphan processes on target ports to prevent EADDRINUSE
echo "[CORTEX] Auditing ports to prevent EADDRINUSE..."
for port in "$PORT" 8081; do
    PID=$(lsof -t -i :"$port")
    if [ -n "$PID" ]; then
        echo "[CORTEX] Releasing port $port (killing process $PID)..."
        kill -9 "$PID" 2>/dev/null || true
    fi
done

if command -v npm &> /dev/null; then
    echo "[CORTEX] Auto-detected Node.js environment."
    npm run start:node
else
    echo "[ERROR] Node.js not found. Anergy level critical. System halt."
    exit 1
fi
