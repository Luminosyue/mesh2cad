#!/usr/bin/env python3
import os, runpy, sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM'),str(ROOT.resolve().parent)]
import curve_ablation_runtime
curve_ablation_runtime.install()
entry=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/launch/unified_v2_entrypoint.py'
runpy.run_path(str(entry), run_name='__main__')
