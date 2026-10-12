#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'SpatialLM'),str(ROOT.resolve().parent)]
import curve_ablation_runtime
curve_ablation_runtime.install()
import corrected_m2_runtime_audit
corrected_m2_runtime_audit.install()
from spatiallm_curve_token_v1.train_curve_token_spatiallm import main
raise SystemExit(main())
