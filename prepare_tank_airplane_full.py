from pathlib import Path
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import sys,json,copy,concurrent.futures,subprocess,time
import numpy as np,trimesh,cadquery as cq
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_cadquery_tank_airplane54_full_v1'
sys.path.insert(0,str(ROOT/'p3_xpart_open_cases/_cadquery_batch_code_20260922'))
from quality import tessellate,evaluate
def dump(p,d):p.write_text(json.dumps(d,indent=2))
def compact(p,sections,points,precision):
    p=copy.deepcopy(p)
    def thin(seq):
        ids=np.unique(np.round(np.linspace(0,len(seq)-1,min(sections,len(seq)))).astype(int));result=[]
        for i in ids:
            z,q=seq[i];q=np.asarray(q)
            ix=np.unique(np.floor(np.arange(min(points,len(q)))*len(q)/min(points,len(q))).astype(int));result.append([z,q[ix].tolist()])
        return result
    for f in p.get('features',[]):
        if f['type']=='loft':
            f['sections']=thin(f['sections']);f['pockets']=[thin(q) for q in f.get('pockets',[])]
    def rounding(x):
        if isinstance(x,float):return round(x,precision)
        if isinstance(x,list):return [rounding(v) for v in x]
        if isinstance(x,dict):return {k:rounding(v) for k,v in x.items()}
        return x
    return rounding(p)
def emit(p,s,t):
    lines=['import cadquery as cq'];wi=0;bi=0
    def lit(x):return repr(x)
    def wire(q,z,smooth=False):
        nonlocal wi
        name=f'w{wi}';wi+=1;expr=f'cq.Workplane("XY",origin=(0,0,{z}))'
        if isinstance(q,dict):expr+=f'.center({q["center"][0]},{q["center"][1]}).circle({q["radius"]})'
        elif smooth:expr+=f'.spline({lit(q)},periodic=True).wire()'
        else:expr+=f'.polyline({lit(q)}).close()'
        lines.append(name+'='+expr+'.val()');return name
    def loft(seq,smooth,ruled):
        nonlocal bi
        ws=[wire(q,z,smooth) for z,q in seq];name=f'b{bi}';bi+=1
        lines.append(name+'=cq.Workplane("XY").newObject(['+','.join(ws)+f']).toPending().loft(ruled={ruled},combine=False).val()');return name
    if p['operation']=='revolve':
        pts=p['profile'];n=len(pts);bounds=sorted(set(int(i*(n-1)/p['segments']) for i in range(p['segments']+1)))
        lines.append(f'result=cq.Workplane("XZ").moveTo(0,{pts[0][1]}).lineTo({pts[0][0]},{pts[0][1]})')
        def tangent(k):
            d=np.array(pts[min(n-1,k+1)])-pts[max(0,k-1)];return (d/np.linalg.norm(d)).tolist()
        for a,b in zip(bounds[:-1],bounds[1:]):lines.append(f'result=result.spline({pts[a+1:b+1]},includeCurrent=True,tangents={np.round([tangent(a),tangent(b)],8).tolist()},scale=False)')
        lines.append(f'result=result.lineTo(0,{pts[-1][1]}).close().revolve(360,(0,0),(0,1)).val().translate({[*p["center_xy"],0]})')
    else:
        bodies=[]
        for f in p['features']:
            if f['type']=='extrude':
                ws=[wire(q,f['start']) for q in f['loops']];name=f'b{bi}';bi+=1;lines.append(name+'=cq.Workplane("XY").newObject(['+','.join(ws)+f']).toPending().extrude({f["length"]},combine=False).val()')
            else:
                name=loft(f['sections'],f.get('smooth',False),f.get('ruled',True))
                for pocket in f.get('pockets',[]):tool=loft(pocket,True,True);lines.append(f'{name}={name}.cut({tool})')
            bodies.append((name,f.get('cut',False)))
        lines.append('result='+bodies[0][0])
        for name,cut in bodies[1:]:lines.append(f'result=result.{"cut" if cut else "fuse"}({name})')
        lines.append('result=result.clean()')
    if 'basis' in p:
        b=p['basis'];lines.append(f'result=result.located(cq.Location(cq.Plane(origin=(0,0,0),xDir={b[0]},normal={b[2]})))')
    lines.append(f'result=result.scale({round(s/p["construction_scale"],10)}).translate({np.round(np.array(p["center"])*s+t,8).tolist()})')
    return '\n'.join(lines)+'\n'
def one(case,pid):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000',use_fast=True)
    folder=ROOT/'p3_xpart_open_cases'/case/'xpart_parts_cadquery_features'/pid;p=json.loads((folder/'parameters.json').read_text())
    # Tank runtime rotates only non-revolve operations.
    if case=='tank' and p['operation']=='revolve':p.pop('basis',None)
    sr=ROOT/'p3_xpart_open_cases'/case/'xpart_parts'
    src=next((sr/pid).glob('complete*.obj'),None)
    if src is None:src=sr/(pid+'.stl')
    if not src.exists():
        candidates=list(sr.rglob(pid+'*.stl'));src=candidates[0] if candidates else src
    source=trimesh.load(src,force='mesh');s=6/np.linalg.norm(source.extents);t=-source.bounds[0]*s
    ref=cq.importers.importStep(str(folder/(pid+'.step'))).val().scale(s).translate(tuple(t));refmesh=tessellate(ref)
    dest=EXP/'assets/XPart/geometry_pack_v1'/(case+'__'+pid);dest.mkdir(parents=True,exist_ok=True);attempts=[];best=None
    levels=[(10000,10000,9)]
    for sections,points,precision in levels:
        cp=compact(p,sections,points,precision);code=emit(cp,s,t);n=len(tok.encode(code,add_special_tokens=False))
        if n>250000:attempts.append({'tokens':n,'skip':'exceeds_14500'});continue
        try:
            ns={};exec(compile(code,'target.py','exec'),ns);shape=ns['result'];assert shape.isValid() and len(shape.Solids())==len(ref.Solids())
            q=evaluate(refmesh,tessellate(shape));ok=q['p95_distance_pct_diagonal']<=.5 and q['sampled_max_distance_pct_diagonal']<=2 and q['volume_error_pct']<=5
            attempts.append({'tokens':n,'sections':sections,'points':points,'quality_vs_original_cad':q,'pass':ok})
            if ok:
                shape.exportStep(str(dest/'target.step'));(dest/'target.py').write_text(code);dump(dest/'compact_parameters.json',cp)
                best={'case':case,'part':pid,'source':str(src),'scale':s,'translation':t.tolist(),'target_tokens':n,'solids':len(shape.Solids()),'quality_vs_original_cad':q,'original_quality_status':json.loads((folder/'report.json').read_text())['status'],'status':'READY'};break
        except Exception as e:attempts.append({'tokens':n,'error':str(e)})
    dump(dest/'compression_attempts.json',attempts)
    record=best or {'case':case,'part':pid,'status':'NEEDS_COMPRESSION'};dump(dest/'record.json',record);print(case,pid,record['status'],record.get('target_tokens'),flush=True)
def main():
    for d in ['assets','logs','data','audits','configs','launch']:(EXP/d).mkdir(parents=True,exist_ok=True)
    tasks=[(case,p.name) for case in ['tank','airplane'] for p in sorted((ROOT/'p3_xpart_open_cases'/case/'xpart_parts_cadquery_features').glob('PART_*'))]
    def job(x):
        with (EXP/'logs'/('_'.join(x)+'.log')).open('w') as f:
            try:r=subprocess.run([sys.executable,__file__,*x],stdout=f,stderr=subprocess.STDOUT,timeout=240);return [*x,r.returncode]
            except subprocess.TimeoutExpired:return [*x,'TIMEOUT']
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(job,tasks))
    dump(EXP/'audits/preparation_jobs.json',results);print('COMPRESSION_ATTEMPTED',len(results),flush=True)
if __name__=='__main__':
    if len(sys.argv)==3:one(*sys.argv[1:])
    else:main()

