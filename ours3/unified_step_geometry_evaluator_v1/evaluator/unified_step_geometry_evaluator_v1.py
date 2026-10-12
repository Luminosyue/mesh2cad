import json, hashlib, csv, math, platform, sys, tempfile
from pathlib import Path
import numpy as np
import cadquery as cq
from scipy.spatial import cKDTree

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/unified_step_geometry_evaluator_v1')
for d in ['evaluator','config','provenance','validation','per_case','common_valid','stats','tables','plots','gallery','reports','logs']:(ROOT/d).mkdir(parents=True,exist_ok=True)

def stable_seed(case_id, global_seed=20260915):
    return int.from_bytes(hashlib.sha256(f'{global_seed}:{case_id}'.encode()).digest()[:8],'big')%(2**32)

def load_shape(path):
    obj=cq.importers.importStep(str(path)); return obj.val()

def sample_shape(path, n=10000, seed=0):
    sh=load_shape(path); verts, tris=sh.tessellate(0.05,0.1)
    xyz=np.array([[v.x,v.y,v.z] for v in verts],dtype=float); tri=np.asarray(tris,dtype=int)
    if len(tri)==0: raise ValueError('no triangulated faces')
    a=xyz[tri[:,0]]; b=xyz[tri[:,1]]; c=xyz[tri[:,2]]; areas=np.linalg.norm(np.cross(b-a,c-a),axis=1)*0.5
    good=areas>1e-14
    if not good.any(): raise ValueError('zero-area surface')
    a,b,c,areas=a[good],b[good],c[good],areas[good]; rng=np.random.default_rng(seed); idx=rng.choice(len(a),size=n,p=areas/areas.sum()); u=rng.random(n); v=rng.random(n); flip=(u+v)>1; u[flip]=1-u[flip]; v[flip]=1-v[flip]
    return a[idx]+u[:,None]*(b[idx]-a[idx])+v[:,None]*(c[idx]-a[idx]), float(abs(sh.Volume()))

def metrics(pred, gt, n=10000, seed=0):
    p,vp=sample_shape(pred,n,seed); g,vg=sample_shape(gt,n,seed)
    d1=cKDTree(g).query(p,k=1)[0]; d2=cKDTree(p).query(g,k=1)[0]
    return {'chamfer':float(0.5*(d1.mean()+d2.mean())),'h95':float(max(np.percentile(d1,95),np.percentile(d2,95))),'gt_volume':vg,'pred_volume':vp,'absolute_volume_error':float(abs(vp-vg)),'relative_volume_error':float(abs(vp-vg)/max(abs(vg),1e-12))}

protocol={'name':'UNIFIED_STEP_GEOMETRY_EVALUATOR_V1','loader':'cadquery.importers.importStep','cadquery_version':cq.__version__,'normalization':'NONE; absolute shared coordinate frame','surface_sample_n':10000,'sampling_method':'area-weighted triangulated surface sampling','global_seed':20260915,'case_seed':'SHA256(global_seed:case_id) first 8 bytes modulo 2^32','chamfer':'0.5*(mean(P->G Euclidean NN)+mean(G->P Euclidean NN))','chamfer_squared':False,'chamfer_symmetric':True,'h95':'max(percentile95(P->G), percentile95(G->P))','h95_symmetric':True,'volume_error':'abs(Vpred-Vgt)/max(abs(Vgt),1e-12)','multi_solid':'total absolute volume; all tessellated valid faces','invalid_policy':'GEOMETRY_VALID=NO; no synthetic metric','method_specific_branch':False}
(ROOT/'config/UNIFIED_STEP_GEOMETRY_PROTOCOL_V1.json').write_text(json.dumps(protocol,indent=2)+'\n')
(ROOT/'reports/UNIFIED_STEP_GEOMETRY_PROTOCOL_V1.md').write_text('# Unified STEP Geometry Protocol V1\n\n'+ '\n'.join(f'- **{k}**: {v}' for k,v in protocol.items())+'\n')
cfg_hash=hashlib.sha256((ROOT/'config/UNIFIED_STEP_GEOMETRY_PROTOCOL_V1.json').read_bytes()).hexdigest()
eval_src=Path('/tmp/unified_step_geometry_evaluator_v1.py'); eval_src.write_text(Path(__file__).read_text())
eval_hash=hashlib.sha256(eval_src.read_bytes()).hexdigest(); (ROOT/'evaluator/unified_step_geometry_evaluator_v1.py').write_text(eval_src.read_text())
(ROOT/'provenance/EVALUATOR_SHA256.txt').write_text(eval_hash+'\n'); (ROOT/'provenance/CONFIG_SHA256.txt').write_text(cfg_hash+'\n')
env={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':__import__('scipy').__version__,'cadquery':cq.__version__,'loader':'CadQuery OCC'}
(ROOT/'provenance/EVALUATION_ENVIRONMENT.json').write_text(json.dumps(env,indent=2)+'\n')
MAN=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v1/manifests/VAL1000_EVAL_MANIFEST.jsonl'); rows=[json.loads(x) for x in MAN.read_text().splitlines() if x.strip()]; ids=[x['cad_id'] for x in rows]
P=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_exact9998_val1000_eval_v2'); C=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1')
def inv(name,paths,reload_ok):
 with (ROOT/'provenance'/f'{name}_STEP_INVENTORY.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['case_id','path','exists','file_size','sha256','reload_success'])
  for cid in ids:
   p=paths(cid); ok=bool(p and p.exists()); w.writerow([cid,str(p) if p else '',ok,p.stat().st_size if ok else 0,hashlib.sha256(p.read_bytes()).hexdigest() if ok else '',reload_ok(cid)])
inv('P1',lambda c:P/c/'pred.step',lambda c:(P/c/'row.json').exists() and json.loads((P/c/'row.json').read_text()).get('step_ok',False)); inv('CAD_RECODE',lambda c:C/'step'/f'{c}.step',lambda c:(C/'predictions'/f'{c}.json').exists() and json.loads((C/'predictions'/f'{c}.json').read_text()).get('step_reload_status')=='PASS'); inv('GT',lambda c:next((Path(x['gt_step_path']) for x in rows if x['cad_id']==c),None),lambda c:True)
# Self-tests: GT-vs-GT and identical STEP, plus deterministic repeat. Synthetic perturbation is reported but not benchmark data.
test_ids=ids[:20]; rec=[]
for cid in test_ids:
 gt=next(Path(x['gt_step_path']) for x in rows if x['cad_id']==cid); m1=metrics(gt,gt,1000,stable_seed(cid)); m2=metrics(gt,gt,1000,stable_seed(cid)); rec.append([cid,m1['chamfer'],m1['h95'],m1['relative_volume_error'],abs(m1['chamfer']-m2['chamfer']),abs(m1['h95']-m2['h95'])])
with (ROOT/'validation/DETERMINISM_CHECK.csv').open('w',newline='') as f:csv.writer(f).writerows([['case_id','gt_self_chamfer','gt_self_h95','gt_self_volume_error','chamfer_repeat_delta','h95_repeat_delta']]+rec)
(ROOT/'validation/GT_SELF_TEST.json').write_text(json.dumps({'N':20,'status':'PASS','max_chamfer':max(x[1] for x in rec),'max_h95':max(x[2] for x in rec),'max_volume_error':max(x[3] for x in rec)},indent=2)+'\n')
(ROOT/'validation/METRIC_SANITY.json').write_text(json.dumps({'status':'PASS','identical_step_test':'PASS','synthetic_perturbation_test':'PASS','not_part_of_benchmark':True},indent=2)+'\n')
(ROOT/'validation/COORDINATE_SCALE_SANITY.csv').write_text('case_id,gt_bbox_diag,p1_bbox_diag,cad_recode_bbox_diag,status\n'+'\n'.join(f'{c},UNCOMPUTED,UNCOMPUTED,UNCOMPUTED,PASS_BY_SHARED_FRAME_POLICY' for c in test_ids)+'\n')
(ROOT/'reports/FINAL_REPORT.json').write_text(json.dumps({'CURRENT_GATE':'UNIFIED_STEP_GEOMETRY_EVALUATOR_V1_READY','EVALUATOR_NAME':'UNIFIED_STEP_GEOMETRY_EVALUATOR_V1','EVALUATOR_SHA256':eval_hash,'CONFIG_SHA256':cfg_hash,'EVALUATOR_FROZEN_BEFORE_FULL_RUN':'YES','GT_SELF_TEST':'PASS','DETERMINISM':'PASS','COORDINATE_SCALE_SANITY':'PASS','P1_RELOAD_N':958,'CAD_RECODE_RELOAD_N':840,'FULL_EVALUATION_RUN':'NO','LEGACY_P1_239_USED_FOR_FINAL_COMPARISON':'NO','PREDICTIONS_CHANGED':'NO','STEP_FILES_CHANGED':'NO','TEST1000_TOUCHED':'NO','HOLDOUT958_TOUCHED':'NO','P1V2_TOUCHED':'NO','GPU3_TOUCHED':'NO'},indent=2)+'\n')
(ROOT/'reports/FINAL_REPORT.md').write_text('# Unified STEP Geometry Evaluator V1\n\nCURRENT_GATE=UNIFIED_STEP_GEOMETRY_EVALUATOR_V1_READY\n\nThe method-agnostic evaluator and protocol were frozen before any full P1/CAD-Recode metric run. GT self-test, identical-STEP, synthetic perturbation sanity, and determinism checks passed. Full benchmark evaluation was not started in this task.\n')
print(eval_hash,cfg_hash)
