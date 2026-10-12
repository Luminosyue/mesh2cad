import os,sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'SpatialLM')]
os.environ.setdefault('CAD_USE_EDGE_SCORE','0')
from spatiallm.tuner.trainer import run_exp
sys.argv=['run_p3',str(EXP/'p3_train.yaml')]
raise SystemExit(run_exp())
