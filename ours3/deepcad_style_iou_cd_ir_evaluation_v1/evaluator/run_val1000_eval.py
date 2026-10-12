from __future__ import annotations
import csv, json, sys, time
from pathlib import Path
import numpy as np
import cadquery as cq
from scipy.spatial import cKDTree
from scipy.stats import binomtest
sys.path.insert(0, str(Path(__file__).parent))
from deepcad_style_cd_v1 import sample_mesh_surface, chamfer_squared_symmetric, case_seed
from solid_iou_v1 import solid_iou
from deepcad_style_invalid_classifier_v1 import classify_prediction
from OCP.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/deepcad_style_iou_cd_ir_evaluation_v1'
MANIFEST = ROOT / 'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl'
P1ROOT = ROOT / 'ours3/p1_exact9998_val1000_eval_v2'
CRROOT = ROOT / 'ours3/cad_recode_val1000_inference_v1'

def adapt_cr(shape):
    t = gp_Trsf(); t.SetScale(gp_Pnt(0,0,0), 1.0/200.0); t.SetTranslationPart(gp_Vec(0.5,0.5,0.5))
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, t, True).Shape())

def shape_sample(shape, n, seed):
    verts, tris = shape.tessellate(0.05, 0.1)
    xyz = np.array([[v.x, v.y, v.z] for v in verts], dtype=float); tri=np.asarray(tris,dtype=int)
    if len(tri)==0: raise ValueError('empty face set')
    a,b,c=xyz[tri[:,0]],xyz[tri[:,1]],xyz[tri[:,2]]; areas=np.linalg.norm(np.cross(b-a,c-a),axis=1)*.5
    good=areas>1e-14
    if not good.any(): raise ValueError('zero-area surface')
    rng=np.random.default_rng(seed); a,b,c,areas=a[good],b[good],c[good],areas[good]
    idx=rng.choice(len(a),size=n,p=areas/areas.sum()); uv=rng.random((n,2)); flip=uv.sum(1)>1; uv[flip]=1-uv[flip]
    return a[idx]+uv[:,0,None]*(b[idx]-a[idx])+uv[:,1,None]*(c[idx]-a[idx])

def eval_method(case_id, gt_path, pred_path, method):
    row={'case_id':case_id,'native_exec_success':bool(pred_path and pred_path.exists()),'shape_exists':False,'brep_valid':False,'surface_sampling_success':False,'deepcad_invalid':True,'invalid_reason':'native_program_invalid' if not pred_path or not pred_path.exists() else '', 'iou_valid':False,'iou':'','iou_failure_reason':'','cd_valid':False,'cd_deepcad':'','cd_failure_reason':'','gt_valid':False,'gt_failure_reason':'','step_reload_success':False}
    gt = None
    try:
        gt=cq.importers.importStep(str(gt_path)).val(); row['gt_valid']=bool(gt.isValid() and gt.Volume()>0)
        if not row['gt_valid']: row['gt_failure_reason']='invalid_gt_brep'
    except Exception as e:
        row['gt_failure_reason']='gt_step_load:'+type(e).__name__
    try:
        if not row['native_exec_success']: return row
        pred=cq.importers.importStep(str(pred_path)).val(); row['step_reload_success']=True; row['shape_exists']=pred is not None; pred=adapt_cr(pred) if method=='CAD-Recode' else pred
        row['brep_valid']=bool(pred is not None and pred.isValid() and pred.Volume()>0)
        if not row['brep_valid']: row['invalid_reason']='invalid_or_empty_brep'; return row
        row['surface_sampling_success']=True; row['deepcad_invalid']=False; row['invalid_reason']=''
        if not row['gt_valid']:
            return row
        try:
            io=solid_iou(pred,gt); row.update({'iou_valid':True,'iou':io['iou'],'intersection_volume':io['intersection_volume'],'union_volume':io['union_volume']})
        except Exception as e: row['iou_failure_reason']=type(e).__name__+':'+str(e)
        try:
            seed=case_seed(case_id); g=shape_sample(gt,2000,seed); p=shape_sample(pred,2000,seed+1); row['cd_valid']=True; row['cd_deepcad']=chamfer_squared_symmetric(g,p)
        except Exception as e: row['cd_failure_reason']=type(e).__name__+':'+str(e)
    except Exception as e:
        row['invalid_reason']='step_reload_or_shape:'+type(e).__name__
    return row

def stats(vals):
    a=np.asarray(vals,float); return {'n':int(len(a)),'mean':float(a.mean()) if len(a) else None,'median':float(np.median(a)) if len(a) else None,'p25':float(np.percentile(a,25)) if len(a) else None,'p75':float(np.percentile(a,75)) if len(a) else None,'p95':float(np.percentile(a,95)) if len(a) else None}

def main():
    rows=[json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    results={m:[] for m in ('P1','CAD-Recode')}; started=time.time()
    for i,r in enumerate(rows):
        cid=r['cad_id']; short=cid.split('__',1)[1]; ds=cid.split('__',1)[0];
        gt=Path(r['gt_step_path']);
        p1=P1ROOT/cid/'pred.step'; cr=CRROOT/'step'/(cid+'.step')
        results['P1'].append(eval_method(cid,gt,p1,'P1'))
        results['CAD-Recode'].append(eval_method(cid,gt,cr,'CAD-Recode'))
        if (i+1)%25==0: print('processed',i+1,'elapsed',round(time.time()-started,1),flush=True)
    for method,rs in results.items():
        name='P1' if method=='P1' else 'CAD_RECODE'; path=OUT/'per_case'/(name+'_DEEPCAD_STYLE_METRICS.csv'); path.parent.mkdir(parents=True,exist_ok=True)
        keys=sorted({k for x in rs for k in x})
        with path.open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rs)
    p,c=results['P1'],results['CAD-Recode']; common=[(a,b) for a,b in zip(p,c) if not a['deepcad_invalid'] and not b['deepcad_invalid'] and a['gt_valid'] and b['gt_valid'] and a['iou_valid'] and b['iou_valid'] and a['cd_valid'] and b['cd_valid']]
    cv=OUT/'common_valid'; cv.mkdir(exist_ok=True)
    with (cv/'P1_CAD_RECODE_DEEPCAD_COMMON_VALID_CASE_IDS.txt').open('w') as f: f.write('\n'.join(a['case_id'] for a,b in common)+'\n')
    fields=['case_id','P1_iou','CAD_Recode_iou','P1_cd','CAD_Recode_cd'];
    with (cv/'P1_CAD_RECODE_DEEPCAD_COMMON_VALID_PER_CASE.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow({'case_id':a['case_id'],'P1_iou':a['iou'],'CAD_Recode_iou':b['iou'],'P1_cd':a['cd_deepcad'],'CAD_Recode_cd':b['cd_deepcad']}) for a,b in common]
    summary={'VAL1000_N':len(rows),'P1_INVALID_N':sum(x['deepcad_invalid'] for x in p),'CAD_RECODE_INVALID_N':sum(x['deepcad_invalid'] for x in c),'P1_IR':sum(x['deepcad_invalid'] for x in p)/len(rows),'CAD_RECODE_IR':sum(x['deepcad_invalid'] for x in c)/len(rows),'P1_IOU_VALID_N':sum(x['iou_valid'] for x in p),'CAD_RECODE_IOU_VALID_N':sum(x['iou_valid'] for x in c),'P1_CD_VALID_N':sum(x['cd_valid'] for x in p),'CAD_RECODE_CD_VALID_N':sum(x['cd_valid'] for x in c),'COMMON_VALID_N':len(common),'P1_COMMON_IOU':stats([a['iou'] for a,b in common]),'CAD_RECODE_COMMON_IOU':stats([b['iou'] for a,b in common]),'P1_COMMON_CD':stats([a['cd_deepcad'] for a,b in common]),'CAD_RECODE_COMMON_CD':stats([b['cd_deepcad'] for a,b in common]),'elapsed_sec':time.time()-started}
    (OUT/'tables').mkdir(exist_ok=True); (OUT/'tables'/'P1_VS_CAD_RECODE_DEEPCAD_STYLE_CORE.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
