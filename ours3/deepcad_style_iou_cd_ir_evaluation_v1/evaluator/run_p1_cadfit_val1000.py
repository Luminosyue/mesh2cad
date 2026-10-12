from __future__ import annotations
import argparse, csv, json, sys, time, multiprocessing as mp
from pathlib import Path
import numpy as np
import trimesh
import cadquery as cq
from OCP.StlAPI import StlAPI_Reader
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Transform
from OCP.TopoDS import TopoDS, TopoDS_Shape
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.gp import gp_Pnt, gp_Vec, gp_Trsf

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
EVAL=ROOT/'ours3/deepcad_style_iou_cd_ir_evaluation_v1'
sys.path.insert(0,str(EVAL/'evaluator'))
from deepcad_style_cd_v1 import chamfer_squared_symmetric, case_seed
from solid_iou_v1 import solid_iou

MANIFEST=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl'
P1ROOT=ROOT/'ours3/p1_exact9998_val1000_eval_v2'
CFROOT=ROOT/'ours3/cadfit_val1000_baseline_v1'
CFOUT=CFROOT/'native_outputs/recovered_mesh_runs_v1'
REC=ROOT/'ours3/cadfit_recovered_meshes_v1/DeepCAD/train'
OUT=EVAL/'cadfit_comparison_v1'

def shape_sample(shape,n,seed):
    verts,tris=shape.tessellate(0.05,0.1)
    xyz=np.array([[v.x,v.y,v.z] for v in verts],float); tri=np.asarray(tris,int)
    if len(tri)==0: raise ValueError('empty face set')
    a,b,c=xyz[tri[:,0]],xyz[tri[:,1]],xyz[tri[:,2]]
    area=np.linalg.norm(np.cross(b-a,c-a),axis=1)*.5; good=area>1e-14
    if not good.any(): raise ValueError('zero-area surface')
    a,b,c,area=a[good],b[good],c[good],area[good]
    rng=np.random.default_rng(seed); idx=rng.choice(len(a),size=n,p=area/area.sum())
    uv=rng.random((n,2)); flip=uv.sum(1)>1; uv[flip]=1-uv[flip]
    return a[idx]+uv[:,0,None]*(b[idx]-a[idx])+uv[:,1,None]*(c[idx]-a[idx])

def stl_solid(path):
    raw=TopoDS_Shape()
    if not StlAPI_Reader().Read(raw,str(path)): raise ValueError('stl read failed')
    sew=BRepBuilderAPI_Sewing(1e-5); sew.Add(raw); sew.Perform(); s=sew.SewedShape()
    shells=[]
    if s.ShapeType()==TopAbs_SHELL: shells=[TopoDS.Shell_s(s)]
    else:
        ex=TopExp_Explorer(s,TopAbs_SHELL)
        while ex.More(): shells.append(TopoDS.Shell_s(ex.Current())); ex.Next()
    solids=[]
    for shell in shells:
        mk=BRepBuilderAPI_MakeSolid(shell)
        if mk.IsDone(): solids.append(cq.Shape.cast(mk.Solid()))
    if not solids: raise ValueError('no solid from STL')
    return solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)

def inverse_normalize(shape,input_stl):
    m=trimesh.load_mesh(input_stl,process=True); center=m.bounds.mean(axis=0)
    maxdim=float((m.bounds[1]-m.bounds[0]).max()); scale=2.0/maxdim
    t=gp_Trsf(); t.SetScale(gp_Pnt(0,0,0),1.0/scale); t.SetTranslationPart(gp_Vec(*map(float,center)))
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped,t,True).Shape())

def gt_path(row):
    p=Path(row['gt_step_path'])
    if p.exists(): return p
    cid=row['cad_id']
    if cid.startswith('deepcad__'):
        q=REC/cid.split('__',1)[1]/'model.step'
        if q.exists(): return q
    return p

def cadfit_names(cid):
    sid=cid.split('__',1)[1] if cid.startswith('deepcad__') else cid
    d=CFOUT/sid
    for name in ('best_greedy_parallel_iterative.stl','best_greedy_parallel.stl'):
        p=d/name
        if p.exists(): return sid,p
    return sid,d/'best_greedy_parallel_iterative.stl'

def iou_worker(pred,gt,conn):
    try: conn.send(('ok',solid_iou(pred,gt)))
    except Exception as e: conn.send(('err',type(e).__name__+':'+str(e)))
    finally: conn.close()

def timed_solid_iou(pred,gt,timeout=30):
    parent,child=mp.Pipe(False)
    proc=mp.Process(target=iou_worker,args=(pred,gt,child)); proc.start(); child.close()
    if parent.poll(timeout):
        status,payload=parent.recv(); proc.join(2)
        if status=='err': raise ValueError(payload)
        return payload
    proc.terminate(); proc.join(5)
    raise TimeoutError('solid_iou_timeout_30s')

def evaluate(cid,gtp,pred_builder):
    row={'case_id':cid,'deepcad_invalid':True,'invalid_reason':'','iou_valid':False,'iou':'','cd_valid':False,'cd_deepcad':''}
    try: gt=cq.importers.importStep(str(gtp)).val()
    except Exception as e: row['invalid_reason']='gt:'+type(e).__name__; return row
    try: pred=pred_builder()
    except Exception as e: row['invalid_reason']='pred:'+type(e).__name__+':'+str(e); return row
    try:
        if not pred.isValid() or pred.Volume()<=0: raise ValueError('invalid_or_empty')
        shape_sample(pred,10,case_seed(cid)+99)
        row['deepcad_invalid']=False
    except Exception as e: row['invalid_reason']='validity:'+type(e).__name__+':'+str(e); return row
    try:
        z=timed_solid_iou(pred,gt)
        row['iou_valid']=True; row['iou']=z['iou']
    except Exception as e: row['iou_failure_reason']=type(e).__name__+':'+str(e)
    try:
        seed=case_seed(cid); g=shape_sample(gt,2000,seed); p=shape_sample(pred,2000,seed+1)
        row['cd_valid']=True; row['cd_deepcad']=chamfer_squared_symmetric(g,p)
    except Exception as e: row['cd_failure_reason']=type(e).__name__+':'+str(e)
    return row

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int); ap.add_argument('--start',type=int,default=0); args=ap.parse_args()
    rows=[json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    rows=rows[args.start:]
    if args.limit: rows=rows[:args.limit]
    results={'P1':[],'CADFit':[]}; started=time.time()
    for i,r in enumerate(rows):
        cid=r['cad_id']; gt=gt_path(r); sid,cfp=cadfit_names(cid); inp=CFROOT/'input_recovered_v2'/(sid+'.stl')
        p1p=P1ROOT/cid/'pred.step'
        results['P1'].append(evaluate(cid,gt,lambda p=p1p: cq.importers.importStep(str(p)).val()))
        results['CADFit'].append(evaluate(cid,gt,lambda p=cfp,q=inp: inverse_normalize(stl_solid(p),q)))
        if (i+1)%10==0: print('processed',i+1,'elapsed',round(time.time()-started,1),flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    tag='pilot'+str(args.limit) if args.limit else 'val1000'
    for method,rs in results.items():
        keys=sorted({k for x in rs for k in x}); p=OUT/f'{method.upper()}_{tag}.csv'
        with p.open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rs)
    common=[(a,b) for a,b in zip(results['P1'],results['CADFit']) if not a['deepcad_invalid'] and not b['deepcad_invalid'] and a['iou_valid'] and b['iou_valid'] and a['cd_valid'] and b['cd_valid']]
    def mean(xs,k): return float(np.mean([float(x[k]) for x in xs])) if xs else None
    s={'N':len(rows),'P1_IR':sum(x['deepcad_invalid'] for x in results['P1'])/len(rows),'CADFit_IR':sum(x['deepcad_invalid'] for x in results['CADFit'])/len(rows),'COMMON_VALID_N':len(common),'P1_IOU':mean([a for a,b in common],'iou'),'CADFit_IOU':mean([b for a,b in common],'iou'),'P1_CD':mean([a for a,b in common],'cd_deepcad'),'CADFit_CD':mean([b for a,b in common],'cd_deepcad'),'elapsed_sec':time.time()-started}
    (OUT/f'SUMMARY_{tag}.json').write_text(json.dumps(s,indent=2)+'\n'); print(json.dumps(s,indent=2))
if __name__=='__main__': main()
