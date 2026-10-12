#!/usr/bin/env bash
set -u
cd /data/home/cuiyuehan/project/mesh2cad/ours3
mkdir -p batch9_case09_style_fullstack_v6_2/logs
if pgrep -f 'python3 batch9_v6_2_[r]esume.py' >/dev/null; then
  echo "ALREADY_RUNNING"
  pgrep -af 'python3 batch9_v6_2_[r]esume.py'
  exit 0
fi
nohup env TEXT_MODEL=qwen3.7-flash MAC_WORKERS=1 MAC_TEXT_RETRIES=1 MAC_VISUAL_RETRIES=2 MAC_MAX_TOKENS=2048 MAC_TEXT_TIMEOUT=600 MAC_VISUAL_TIMEOUT=180 python3 batch9_v6_2_resume.py >batch9_case09_style_fullstack_v6_2/logs/resume.log 2>&1 &
echo "STARTED_PID=$!"
