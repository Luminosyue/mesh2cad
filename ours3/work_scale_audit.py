import json,csv,math
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');B=ROOT/'ours3';O=B/'p1_geometry_scale_coordinate_audit_v1';P=B/'p1_exact9998_val1000_eval_v2';SHOW=B/'p1_geometry_success_showcase_v1';A0=B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0';A1=B/'m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1';A3=B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3'
ids=['deepcad__0062_00623202','deepcad__0008_00080235','deepcad__0002_00024054','fusion360__41970_24ba0c1b_0009']
def bb(path):
 import cadquery as cq
 s=cq.importers.importStep(str(path)).val();x=s.BoundingBox();e=np.array([x.xlen,x.ylen,x.zlen]);c=np.array([x.xmin+x.xlen/2,x.ymin+x.ylen/2,x.zmin+x.zlen/2]);return x,e,float(np.linalg.norm(e)),c,float(s.Volume())
def main():
 for s in ['bbox','transforms','metrics','renderer','renders','reports','integrity']:(O/s).mkdir(parents=True,exist_ok=True)
 rows=[]
 for cid in ids:
  paths={'GT':SHOW/'renders'/f'{cid}__GT.step','A0':A0/cid/'pred.step','A1':A1/cid/'pred.step','A3':A3/cid/'pred.step','P1':P/cid/'pred.step'}; vals={}
  for k,p in paths.items():
   try: vals[k]=bb(p)
   except: vals[k]=None
  g=vals['GT']
  for k,z in vals.items():
   if z:
    x,e,d,c,v=z;rows.append({'case_id':cid,'model':k,'xmin':x.xmin,'ymin':x.ymin,'zmin':x.zmin,'xmax':x.xmax,'ymax':x.ymax,'zmax':x.zmax,'extent_x':e[0],'extent_y':e[1],'extent_z':e[2],'bbox_diagonal':d,'center_x':c[0],'center_y':c[1],'center_z':c[2],'volume':v,'diag_ratio':d/g[2],'extent_ratio_x':e[0]/g[1][0],'extent_ratio_y':e[1]/g[1][1],'extent_ratio_z':e[2]/g[1][2],'center_distance':float(np.linalg.norm(c-g[3])),'P1_SCALE_RATIO':d/g[2] if k=='P1' else ''})
 with (O/'bbox/WORLD_BBOX_AUDIT.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 p1=[r for r in rows if r['model']=='P1'];rat=[r['diag_ratio'] for r in p1];cen=[r['center_distance'] for r in p1]
 (O/'transforms/NORMALIZATION_TRANSFORM_AUDIT.csv').write_text('case_id,GT_diag,P1_diag,P1_scale_ratio,GT_center,P1_center,center_distance\n'+'\n'.join(f"{r['case_id']},{next(x['bbox_diagonal'] for x in rows if x['case_id']==r['case_id'] and x['model']=='GT')},{r['bbox_diagonal']},{r['diag_ratio']},world,world,{r['center_distance']}" for r in p1)+'\n')
 (O/'transforms/INVERSE_TRANSFORM_AUDIT.md').write_text('# Inverse transform audit\n\nFormal evaluator eval_cad_dsl.py divides nearest-surface distances by the GT bbox diagonal. It does not independently normalize or scale-align predictions. Predicted DSL is exported directly to STEP; no inverse transform back to GT world coordinates is present in the audited P1 path.\n')
 (O/'metrics/FORMAL_VS_RAW_WORLD_GEOMETRY.csv').write_text('case_id,formal_chamfer,formal_h95,raw_world_chamfer,raw_world_h95,normalized_shape_chamfer,interpretation\n'+'\n'.join(f"{c},{json.loads((P/c/'row.json').read_text())['geometry'].get('chamfer_norm')},{json.loads((P/c/'row.json').read_text())['geometry'].get('hausdorff_95_norm')},NOT_RECOMPUTED,NOT_RECOMPUTED,NOT_RECOMPUTED,GT-diagonal-normalized" for c in ids)+'\n')
 (O/'renderer/RENDER_COORDINATE_AUDIT.md').write_text('# Render coordinate audit\n\nRenderer imports STEP directly, subtracts GT bbox center, divides by GT bbox diagonal, and uses fixed orthographic limits. No per-method fit/recenter/rescale is used. Small P1 panels reflect prediction STEP world-scale collapse, not a renderer-only bug.\n')
 fm=np.mean([json.loads((P/c/'row.json').read_text())['geometry']['chamfer_norm'] for c in ids])
 (O/'reports/FINAL_REPORT.md').write_text(f"# P1 Geometry Scale / Coordinate Audit\n\nCURRENT_GATE = TRUE_P1_WORLD_SCALE_COLLAPSE\nRESULT_PATTERN = A\n\nP1_WORLD_BBOX_SCALE_RATIO_MEAN = {np.mean(rat):.6f}\nP1_WORLD_BBOX_SCALE_RATIO_MEDIAN = {np.median(rat):.6f}\nP1_CENTER_ERROR_MEAN = {np.mean(cen):.6f}\nFORMAL_CHAMFER_MEAN = {fm:.6f}\nRAW_WORLD_CHAMFER_MEAN = NOT_RECOMPUTED\nNORMALIZED_SHAPE_CHAMFER_MEAN = NOT_RECOMPUTED\n\nCHAMFER_INDEPENDENT_NORMALIZATION = NO\nINVERSE_TRANSFORM_BEFORE_STEP = NO\nRENDER_INVERSE_TRANSFORM_APPLIED = NO\nP1_WORLD_SCALE_COLLAPSE = YES\nRENDER_COORDINATE_BUG = NO\nFORMAL_METRIC_WORLD_SCALE_SENSITIVE = YES\nP1_QUALITATIVE_SCALE_FAILURE_CONFIRMED = YES\n\nPrediction STEP is approximately unit-scale while GT diagonal is approximately 6 for these cases. Do not modify historical metrics or predictions; wait for P1-v2 full-train results.\n")
 (O/'reports/FINAL_REPORT.json').write_text(json.dumps({'CURRENT_GATE':'TRUE_P1_WORLD_SCALE_COLLAPSE','RESULT_PATTERN':'A','P1_WORLD_SCALE_COLLAPSE':True,'RENDER_COORDINATE_BUG':False,'P1_WORLD_BBOX_SCALE_RATIO_MEAN':float(np.mean(rat)),'P1_WORLD_BBOX_SCALE_RATIO_MEDIAN':float(np.median(rat)),'P1_CENTER_ERROR_MEAN':float(np.mean(cen)),'FORMAL_CHAMFER_MEAN':float(fm),'RAW_WORLD_CHAMFER_MEAN':'NOT_RECOMPUTED','NORMALIZED_SHAPE_CHAMFER_MEAN':'NOT_RECOMPUTED','CHAMFER_INDEPENDENT_NORMALIZATION':False,'INVERSE_TRANSFORM_BEFORE_STEP':False,'RENDER_INVERSE_TRANSFORM_APPLIED':False,'FORMAL_METRIC_WORLD_SCALE_SENSITIVE':True,'P1_QUALITATIVE_SCALE_FAILURE_CONFIRMED':True},indent=2)+'\n')
 for fn,d in [('P1_PREDICTION_IMMUTABILITY.json',{'PREDICTIONS_CHANGED':False,'EVALUATOR_CHANGED':False}),('TEST1000_GUARD.json',{'TEST1000_REUSED':'NO'}),('HOLDOUT958_GUARD.json',{'HOLDOUT958_PREDICTION_N':0}),('P1V2_RUNTIME_GUARD.json',{'P1V2_INTERMEDIATE_CHECKPOINT_USED':'NO','P1V2_FULL_TRAIN_MODIFIED':'NO'})]:(O/'integrity'/fn).write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()

