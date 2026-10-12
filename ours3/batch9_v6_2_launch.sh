#!/usr/bin/env bash
set -u
cd /data/home/cuiyuehan/project/mesh2cad/ours3
mkdir -p batch9_case09_style_fullstack_v6_2/logs
if pgrep -f 'python3 batch9_fullstack_mesh2cad_mac_v6/scripts/[b]atch9_mac.py' >/dev/null; then
  echo "ALREADY_RUNNING"
  pgrep -af 'python3 batch9_fullstack_mesh2cad_mac_v6/scripts/[b]atch9_mac.py'
  exit 0
fi
nohup env TEXT_MODEL=qwen3.7-plus python3 batch9_fullstack_mesh2cad_mac_v6/scripts/batch9_mac.py >batch9_case09_style_fullstack_v6_2/logs/mac_batch.log 2>&1 &
echo "STARTED_PID=$!"
