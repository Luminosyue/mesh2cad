"""Resumable feature reconstruction. Never changes input geometry."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,time,hashlib,traceback,subprocess,concurrent.futures,shutil,signal
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_historical_route_100_20261011/runs/new_object_079/objects')
CODE=Path(__file__).resolve().parent
RUN=ROOT/'_cadquery_batch_20260922'

def dump(p,d):
    temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(d,indent=2),encoding='utf-8');temp.replace(p)

def candidates(m):
    import numpy as np,trimesh
    from sections import section,coords,resample
    from fit_revolve import fit
    bases=[np.roll(np.eye(3),i,axis=0) for i in range(3)]
    _,_,v=np.linalg.svd(m.vertices[::max(1,len(m.vertices)//5000)]-m.centroid)
    if np.linalg.det(v)<0:v[0]*=-1
    bases += [v[[1,2,0]],v[[2,0,1]],v]
    locals=[]
    for bi,b in enumerate(bases):
        local=trimesh.Trimesh(m.vertices@b.T,m.faces,process=False);lo,hi=local.bounds[:,2];span=hi-lo
        if span<1e-6:continue
        mid=section(local,(lo+hi)/2,.12);locals.append((bi,b,local,lo,hi,mid))
        # Test analytic round sketches before more general profile extrusion.
        for frac in [.5]:
            polys=mid
            if not polys:continue
            loops=[];analytic=False
            for p in polys:
                rings=[]
                for ring in [p.exterior,*p.interiors]:
                    pts=np.asarray(ring.coords)[:-1];A=np.c_[2*pts,np.ones(len(pts))]
                    c=np.linalg.lstsq(A,(pts*pts).sum(1),rcond=None)[0];rad=np.linalg.norm(pts-c[:2],axis=1)
                    if len(pts)>7 and rad.std()/max(rad.mean(),1e-8)<.012:
                        rings.append(dict(center=c[:2].tolist(),radius=float(rad.mean())));analytic=True
                    else:rings.append(coords(ring))
                loops.append(rings)
            if analytic:
                yield dict(operation='extrude',basis=b.tolist(),features=[dict(type='extrude',start=float(lo),length=float(span),loops=q) for q in loops],axis_candidate=bi,analytic_circles=True)
            yield dict(operation='extrude',basis=b.tolist(),features=[dict(type='extrude',start=float(lo),length=float(span),loops=[coords(p.exterior)]+[coords(q) for q in p.interiors]) for p in polys],axis_candidate=bi)
    # Rotation axis selected from near-circular sections, not tank part IDs.
    for bi,b,local,lo,hi,mid in locals:
        if len(mid)!=1:continue
        pts=np.asarray(mid[0].exterior.coords);c=pts.mean(0);r=np.linalg.norm(pts-c,axis=1)
        if r.std()/max(r.mean(),1e-8)>.10:continue
        try:yield dict(fit(local),operation='revolve',basis=b.tolist(),axis_candidate=bi)
        except Exception:pass
    for count in [9,21,41]:
        for bi,b,local,lo,hi,mid in locals:
            zs=np.linspace(lo+(hi-lo)*.001,hi-(hi-lo)*.001,count)
            secs=[section(local,z,.12) for z in zs]
            if not all(len(s)==1 for s in secs):continue
            # Retain through cavities only when section topology stays constant.
            holes=[len(s[0].interiors) for s in secs]
            if len(set(holes))!=1 or holes[0]>4:continue
            def aligned(rings):
                from shapely.geometry import Polygon
                result=[];prev=None
                for ring in rings:
                    q=resample(Polygon(ring),48)
                    if prev is not None:q=min((np.roll(q,k,axis=0) for k in range(len(q))),key=lambda a:np.sum((a-prev)**2))
                    result.append(q);prev=q
                return [[float(z),np.round(q,6).tolist()] for z,q in zip(zs,result)]
            outer=aligned([s[0].exterior for s in secs]);pockets=[]
            for h in range(holes[0]):pockets.append(aligned([sorted(s[0].interiors,key=lambda q:abs(__import__('shapely').geometry.Polygon(q).area),reverse=True)[h] for s in secs]))
            yield dict(operation='loft',basis=b.tolist(),features=[dict(type='loft',smooth=True,ruled=True,sections=outer,pockets=pockets)],axis_candidate=bi,section_count=count)
    # Few thickness regions inferred from cross-section area changes.
    for bi,b,local,lo,hi,mid in locals[:3]:
        n=33;edges=np.linspace(lo,hi,n+1);secs=[section(local,z,.1) for z in (edges[:-1]+edges[1:])/2]
        areas=np.array([sum(p.area for p in s) for s in secs]);bands=[(0,n)]
        def loss(a,c):return np.sum((areas[a:c]-areas[a:c].mean())**2)
        for count in range(2,6):
            options=[(loss(a,c)-loss(a,j)-loss(j,c),ix,j) for ix,(a,c) in enumerate(bands) for j in range(a+2,c-1)]
            if not options:break
            _,ix,j=max(options);a,c=bands.pop(ix);bands.extend([(a,j),(j,c)]);bands.sort()
            if count not in [2,3,5]:continue
            fs=[]
            for a,c in bands:
                ix=min(range(a,c),key=lambda i:abs(areas[i]-areas[a:c].mean()))
                for p in secs[ix]:fs.append(dict(type='extrude',start=float(edges[a]),length=float(edges[c]-edges[a]+(hi-lo)*.00002),loops=[coords(p.exterior)]+[coords(q) for q in p.interiors]))
            if fs and len(fs)<35:yield dict(operation='base_and_profile_pads',basis=b.tolist(),features=fs,axis_candidate=bi,thickness_regions=count,limitation='Inferred few-region profile pads; curved transitions simplified')

def worker(case,pid):
    import numpy as np,trimesh,cadquery as cq
    from feature_runtime import build_model
    from quality import tessellate,evaluate
    src=next((ROOT/case/'xpart_parts'/pid).glob('complete*.obj'))
    out=ROOT/case/'xpart_parts_cadquery_features'/pid;out.mkdir(parents=True,exist_ok=True)
    source=trimesh.load(src,force='mesh');center=source.bounds.mean(0);scale=100/source.extents.max()
    m=source.copy();m.apply_translation(-center);m.apply_scale(scale)
    sha=hashlib.sha256(src.read_bytes()).hexdigest();start=time.time();best=float('inf');attempts=[]
    runtime=(CODE/'feature_runtime.py').read_text()
    try:
        for i,p in enumerate(candidates(m)):
            p.update(center=center.tolist(),construction_scale=float(scale));t=time.time()
            try:
                shape=build_model(p)
                if not shape.isValid() or not shape.Solids():raise ValueError('Invalid or empty solid')
                tri=tessellate(shape.translate(tuple(-center)).scale(scale));q=evaluate(m,tri)
                score=q['p95_distance_pct_diagonal']+.05*q['volume_error_pct']+.1*q['sampled_max_distance_pct_diagonal']+.0003*len(shape.Faces())
                attempts.append(dict(index=i,method=p['operation'],score=score,seconds=time.time()-t))
                if score<best:
                    temp=out/'checkpoint';temp.mkdir(exist_ok=True)
                    shape.exportStep(str(temp/f'{pid}.step'));actual=cq.importers.importStep(str(temp/f'{pid}.step')).val()
                    if not actual.isValid() or len(actual.Solids())!=len(shape.Solids()):raise ValueError('STEP round trip failed')
                    tri=tessellate(actual.translate(tuple(-center)).scale(scale));q=evaluate(m,tri)
                    p['expected_solid_count']=len(actual.Solids());params=json.dumps(p,indent=2)
                    code='"""Inferred standard-feature CAD. Approximate reconstruction, not recovered design history."""\nfrom pathlib import Path\nimport json\n'+runtime+'\nPARAMETERS=json.loads(r\'\'\''+params+'\'\'\')\ndef build():\n    return build_model(PARAMETERS)\nif __name__=="__main__":\n    result=build()\n    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]\n    result.exportStep(str(Path(__file__).with_suffix(".step")))\n'
                    (temp/f'{pid}.py').write_text(code);dump(temp/'parameters.json',p)
                    tri.apply_scale(1/scale);tri.apply_translation(center);tri.export(temp/f'{pid}_preview.stl')
                    ok=q['p95_distance_pct_diagonal']<=1 and q['volume_error_pct']<=10 and q['sampled_max_distance_pct_diagonal']<=4
                    report=dict(case=case,part=pid,status='APPROXIMATION_ACCEPTED' if ok else 'NEEDS_REFINEMENT',method=p['operation'],cad_faces=len(actual.Faces()),cad_solids=len(actual.Solids()),step_valid=True,quality=q,source=str(src),source_sha256=sha,seconds=time.time()-start,search_complete=False)
                    # Checkpoint report is committed last so the runner never mistakes partial exports for a result.
                    for f in temp.iterdir():f.replace(out/f.name)
                    dump(out/'report.json',report);best=score
                    print(case,pid,'BEST',p['operation'],round(q['p95_distance_pct_diagonal'],3),flush=True)
                dump(out/'attempts.json',attempts)
                if q['p95_distance_pct_diagonal']<.3 and q['volume_error_pct']<3 and q['sampled_max_distance_pct_diagonal']<2:break
            except Exception as e:
                attempts.append(dict(index=i,method=p['operation'],error=str(e),seconds=time.time()-t));dump(out/'attempts.json',attempts)
        if (out/'report.json').exists():
            report=json.loads((out/'report.json').read_text());report['search_complete']=True;dump(out/'report.json',report)
    except Exception as e:dump(out/'search_error.json',dict(error=str(e),traceback=traceback.format_exc()))

def job(item,timeout):
    case,pid=item;out=ROOT/case/'xpart_parts_cadquery_features'/pid;out.mkdir(parents=True,exist_ok=True)
    if (out/'job_status.json').exists():return json.loads((out/'job_status.json').read_text())
    if shutil.disk_usage(ROOT).free<5e9:return dict(case=case,part=pid,status='DISK_LOW')
    t=time.time()
    with (out/'run.log').open('w') as log:
        proc=subprocess.Popen([sys.executable,str(__file__),'worker',case,pid],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:rc=proc.wait(timeout=timeout);reason='finished' if rc==0 else f'exit_{rc}'
        except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait();reason='time_limit'
    if (out/'report.json').exists():r=json.loads((out/'report.json').read_text())
    else:r=dict(case=case,part=pid,status='FAILED',error='No valid checkpoint')
    r.update(termination=reason,wall_seconds=time.time()-t)
    dump(out/'job_status.json',r);return r

def run(names,workers=24,timeout=180):
    RUN.mkdir(exist_ok=True);tasks=[]
    for c in sorted(ROOT.iterdir()):
        if c.name=='tank' or not (c/'xpart_parts').is_dir() or (names and c.name not in names):continue
        tasks.extend((c.name,p.parent.name) for p in sorted((c/'xpart_parts').rglob('complete*.obj')))
    dump(RUN/'task_manifest.json',dict(tasks=tasks,workers=workers,timeout=timeout,source_root=str(ROOT)))
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs={pool.submit(job,t,timeout):t for t in tasks}
        for f in concurrent.futures.as_completed(futs):
            try:r=f.result()
            except Exception as e:r=dict(case=futs[f][0],part=futs[f][1],status='FAILED',error=str(e))
            rows.append(r);dump(RUN/'progress.json',dict(total=len(tasks),completed=len(rows),counts={s:sum(r['status']==s for r in rows) for s in set(r['status'] for r in rows)},results=rows))
            print('DONE',len(rows),'/',len(tasks),r['case'],r['part'],r['status'],flush=True)
    dump(RUN/'batch_complete.json',dict(total=len(tasks),completed=len(rows)))

if __name__=='__main__':
    if sys.argv[1]=='worker':worker(*sys.argv[2:4])
    else:run(sys.argv[2:],int(os.environ.get('CAD_WORKERS','24')),int(os.environ.get('CAD_TIMEOUT','180')))
