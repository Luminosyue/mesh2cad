#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/deepcad'),str(ROOT/'SpatialLM')]
from geometry_pack_v1.decode_joint_j0_j2 import _exec_step
ap=argparse.ArgumentParser();ap.add_argument('--dsl',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--result',type=Path,required=True);a=ap.parse_args()
try:r=_exec_step(a.dsl.read_text(),a.out)
except BaseException as e:r={'parsed':False,'step_ok':False,'error':f'worker: {type(e).__name__}: {e}','failure_reason':'EXEC_EXCEPTION'}
a.result.write_text(json.dumps(r)+'\n')
