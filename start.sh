#!/bin/bash
# [C5-REAL] CORTEX Unified Start Script (Refactored: Causal Debt 0)
# Author: borjamoskv
# Reality Level: C5-REAL

set -euo pipefail
IFS=$'\n\t'

export PORT=8080

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --port) PORT="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo -e "\033[1;34m[CORTEX]\033[0m Initializing Sovereign Telemetry Panel..."
echo -e "\033[1;34m[CORTEX]\033[0m Target Port: $PORT"

# Clean up any orphan processes on target ports to prevent EADDRINUSE
echo -e "\033[1;33m[CORTEX]\033[0m Auditing ports to prevent EADDRINUSE..."
for port in "$PORT" 8081; do
    PID=$(lsof -t -i :"$port" || true)
    if [ -n "$PID" ]; then
        echo -e "\033[1;31m[CORTEX]\033[0m Releasing port $port (SIGTERM process $PID)..."
        kill -15 "$PID" 2>/dev/null || true
        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 "$PID" 2>/dev/null; then break; fi
            sleep 1
        done
        # Escalation to SIGKILL if still alive
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "\033[1;31m[CORTEX]\033[0m Process $PID unresponsive. Escalating to SIGKILL."
            kill -9 "$PID" 2>/dev/null || true
        fi
    fi
done

if command -v npm &> /dev/null; then
    echo -e "\033[1;32m[CORTEX]\033[0m Auto-detected Node.js environment. Enforcing C5-REAL direct execution."
    exec node server.js
else
    echo -e "\033[1;31m[ERROR]\033[0m Node.js not found. Anergy level critical. System halt." >&2
    exit 1
fi
