#!/usr/bin/env bash
# Kylin runtime replay wrapper. Fill variables before execution on the VM.
set -euo pipefail
GOLD_DIR="/home/kylin/eval/gold"
LOG_DIR="/home/kylin/eval/logs"
mkdir -p "$GOLD_DIR" "$LOG_DIR"
echo "[$(date -Is)] runtime replay start" | tee -a "$LOG_DIR/runtime.log"
# Insert real replay commands here: tool hooks, SDK retrieval, forget, restart, degrade.
echo "[$(date -Is)] runtime replay end" | tee -a "$LOG_DIR/runtime.log"
