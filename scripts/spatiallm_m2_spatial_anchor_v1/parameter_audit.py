#!/usr/bin/env python3
"""Read-only numeric/coordinate error audit over frozen 150 pilot predictions."""
from __future__ import annotations
import json, re
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
IN=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/pilot_eval_150_frozen_v1'
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/reports/PARAMETER_SPATIAL_AUDIT_V1.json'
SPLIT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_pilot_eval_150.json'
NUM=re.compile(r'(?<![A-Za-z_])[-+]?(?:\d+\.\d+|\d+)(?:[eE][-+]?\d+)?')
def nums(s): return np.array([float(x) for x in NUM.findall(s)],np.float64)
def main():
 if OUT.exists(): raise FileExistsError(f'refusing overwrite {OUT}')
 targets={r['cad_id']:Path(r['target_dsl']).read_text() for r in json.loads(SPLIT.read_text())['records']}
 report={'pilot_outputs_read_only':True,'official_test_read':False,'training_started':False,'arms':{}}
 for arm,folder in {'B0':'b0_epoch09','B1_V3':'b1_epoch09','M2_V3':'m2_epoch10'}.items():
  rows=[json.loads(x) for x in (IN/folder/'per_cad.jsonl').read_text().splitlines()]
  diffs=[]; count_ratios=[]
  for r in rows:
   gt,pred=nums(targets[r['cad_id']]),nums(r['generated_dsl']); n=min(len(gt),len(pred))
   if n: diffs.extend(np.abs(gt[:n]-pred[:n]).tolist())
   count_ratios.append(float(len(pred)/max(1,len(gt))))
  report['arms'][arm]={'n':len(rows),'numeric_token_count_ratio_mean':float(np.mean(count_ratios)),'sequential_numeric_abs_error_median':float(np.median(diffs)) if diffs else None,'sequential_numeric_abs_error_p90':float(np.quantile(diffs,.9)) if diffs else None,'note':'Provisional lexical numeric alignment only; semantic parameter matching requires operation-aligned AST audit.'}
 OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(report,indent=2)+'\n'); print(OUT)
if __name__=='__main__': main()
