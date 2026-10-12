#!/bin/bash
set -euo pipefail
cd /data/home/cuiyuehan/project/mesh2cad
export MPLCONFIGDIR=/tmp/matplotlib-v3
mkdir -p ours3/airplane_routeb_point2cad_v3/logs
exec python3 -u scripts/run_airplane_routeb_v3.py --timeout 900 "$@"
