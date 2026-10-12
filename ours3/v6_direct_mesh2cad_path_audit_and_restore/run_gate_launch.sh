#!/usr/bin/env bash
set -euo pipefail
cd /data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore
mkdir -p logs
if pgrep -f 'python3 [r]un_gate.py' >/dev/null; then
  echo ALREADY_RUNNING
  pgrep -af 'python3 [r]un_gate.py'
  exit 0
fi
nohup python3 run_gate.py >logs/run_gate.log 2>&1 </dev/null &
echo STARTED_PID=$!
