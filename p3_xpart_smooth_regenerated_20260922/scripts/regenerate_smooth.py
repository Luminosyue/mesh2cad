"""Fresh section fitting for all non-tank X-Part meshes; resumable, isolated outputs."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['LP_NUM_THREADS']='2';os.environ['VTK_SMP_MAX_THREADS']='2'
from pathlib import Path
import sys,json,time,hashlib,traceback,subprocess,csv,argparse,shutil
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
import trimesh
from shapely.geometry import Polygon,LineString
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
import cadquery as cq
from smooth_runtime import build_normalized,build_model

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
SCRIPTS=Path(__file__).resolve().parent
GATES={'mean_distance_pct_diagonal':.3,'p95_distance_pct_diagonal':1.,'sampled_max_distance_pct_diagonal':4.,'volume_error_pct':10.}
def dump(p,o):
    p.parent.mkdir(parents=True,exist_ok=True); temp=p.with_suffix(p.suffix+'.tmp');temp.write_text(json.dumps(o,indent=2,allow_nan=False),encoding='utf-8');temp.replace(p)
def load(p):
    m=trimesh.load(p,force='mesh',process=False);m.process(validate=True);m.remove_unreferenced_vertices();return m
def frame(z):
    z=np.array(z,float);z/=np.linalg.norm(z);x=np.cross(np.eye(3)[np.argmin(abs(z))],z);x/=np.linalg.norm(x)
    return np.array([x,np.cross(z,x),z])
def section(m,z):
    cut=m.section(plane_origin=(0,0,z),plane_normal=(0,0,1));polys=[]
    if cut is None:return []
    for pts in cut.discrete:
        if len(pts)<4 or np.linalg.norm(pts[0]-pts[-1])>.02:continue
        p=Polygon(pts[:,:2])
        if not p.is_valid:p=p.buffer(0)
        for q in (p.geoms if hasattr(p,'geoms') else [p]):
            if q.geom_type=='Polygon' and q.area>1e-5:polys.append(q)
    polys.sort(key=lambda p:-p.area);parents=[]
    for i,p in enumerate(polys):parents.append([j for j,q in enumerate(polys[:i]) if q.contains(p.representative_point())])
    components=[]
    for i,p in enumerate(polys):
        if len(parents[i])%2==0:
            holes=[q for j,q in enumerate(polys) if i in parents[j] and len(parents[j])==len(parents[i])+1]
            components.append((p,sorted(holes,key=lambda x:-x.area)))
    return components
def circle(p):
    line=LineString(p.exterior.coords);q=np.array([line.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,80,endpoint=False)])
    v=np.linalg.lstsq(np.c_[2*q,np.ones(len(q))],(q*q).sum(1),rcond=None)[0];c=v[:2];r=np.sqrt(max(v[2]+c@c,1e-10));err=float(np.sqrt(np.mean((np.linalg.norm(q-c,axis=1)-r)**2))/r)
    # A nearly straight, thin outline also fits a circle of enormous radius.
    # Such an ill-conditioned fit must not be classified as a circular profile.
    bounds=np.asarray(p.bounds);span=max(bounds[2]-bounds[0],bounds[3]-bounds[1])
    if r>span or np.any(c<bounds[:2]) or np.any(c>bounds[2:]):err=max(err,1.)
    return c,float(r),err
def sketch(poly,smooth=False,count=40):
    c,r,err=circle(poly)
    if err<.004:return dict(kind='circle',center=c.tolist(),radius=r)
    p=poly.simplify(.08,preserve_topology=True)
    coords=np.array(p.exterior.coords[:-1]);vec=np.roll(coords,-1,axis=0)-coords;vec/=np.maximum(np.linalg.norm(vec,axis=1,keepdims=True),1e-9)
    corners=np.arccos(np.clip((np.roll(vec,1,axis=0)*vec).sum(1),-1,1))
    if not smooth and len(coords)<=64:
        # Preserve straight features and true corners; sample smooth rings as periodic splines.
        if len(coords)<=10 or np.count_nonzero(corners>.35)>=3:return dict(kind='polygon',points=coords.tolist())
    ring=LineString(poly.exterior.coords);q=np.array([ring.interpolate(i/count,normalized=True).coords[0] for i in range(count)])
    if not poly.exterior.is_ccw:q=q[::-1]
    q=np.roll(q,-int(np.argmax(q[:,0])),axis=0)
    return dict(kind='spline',points=q.tolist())
def scene(m):
    import open3d as o3d
    s=o3d.t.geometry.RaycastingScene(nthreads=1);s.add_triangles(o3d.t.geometry.TriangleMesh(o3d.core.Tensor(m.vertices.astype('float32')),o3d.core.Tensor(m.faces.astype('uint32'))));return s
def evaluate(source,cad,n=2048,ss=None):
    import open3d as o3d
    a,_=trimesh.sample.sample_surface(source,n,seed=720);b,_=trimesh.sample.sample_surface(cad,n,seed=721)
    cs=scene(cad);ss=ss if ss is not None else scene(source)
    d1=cs.compute_distance(o3d.core.Tensor(a.astype('float32')),nthreads=1).numpy();d2=ss.compute_distance(o3d.core.Tensor(b.astype('float32')),nthreads=1).numpy()
    diag=float(np.linalg.norm(source.extents));d=np.r_[d1,d2]/diag*100
    volume=abs(abs(cad.volume)-abs(source.volume))/abs(source.volume)*100 if source.is_volume and abs(source.volume)>1e-9 else None
    return dict(mean_distance_pct_diagonal=float(d.mean()),p95_distance_pct_diagonal=float(np.percentile(d,95)),sampled_max_distance_pct_diagonal=float(d.max()),volume_error_pct=volume,samples_each=n,source_to_cad_p95_pct=float(np.percentile(d1,95)/diag*100),cad_to_source_p95_pct=float(np.percentile(d2,95)/diag*100))
def passed(q):return all(q[k] is None or q[k]<=v for k,v in GATES.items())
def score(q):return q['p95_distance_pct_diagonal']+q['mean_distance_pct_diagonal']+.1*q['sampled_max_distance_pct_diagonal']+.008*(q['volume_error_pct'] or 0)
def tess(shape,tol=.06):
    v,f=shape.tessellate(tol,.15);return trimesh.Trimesh([p.toTuple() for p in v],f,process=True)

def candidates(m,attempts):
    pts,_=trimesh.sample.sample_surface(m,4096,seed=401)
    origin=m.bounds.mean(0);diag=np.linalg.norm(m.extents)
    sphere=least_squares(lambda a:np.linalg.norm(pts-a[:3],axis=1)-a[3],[*origin,diag/3],max_nfev=35)
    if np.mean(abs(sphere.fun))/diag<.008:
        yield dict(method='sphere',sphere_center=sphere.x[:3].tolist(),radius=float(abs(sphere.x[3])))
    _,_,v=np.linalg.svd(pts-pts.mean(0),full_matrices=False)
    axes=[*v,*np.eye(3)];seen=[];analyses=[]
    normals=m.face_normals.copy();sign=np.sign(normals[np.arange(len(normals)),np.argmax(abs(normals),axis=1)]);normals*=sign[:,None]
    bins=np.round(normals/.06).astype(int);_,inv=np.unique(bins,axis=0,return_inverse=True);weights=np.bincount(inv,weights=m.area_faces)
    for idx in np.argsort(weights)[-3:]:
        a=np.average(normals[inv==idx],axis=0,weights=m.area_faces[inv==idx]);a/=max(np.linalg.norm(a),1e-10)
        if all(abs(a@b)<.99 for b in axes):axes.append(a)
    for axis in axes:
        if any(abs(axis@other)>.995 for other in seen):continue
        seen.append(axis);basis=frame(axis);local=trimesh.Trimesh(m.vertices@basis.T,m.faces,process=False);lo,hi=local.bounds[:,2];h=hi-lo
        secs=[section(local,lo+h*f) for f in [.1,.3,.5,.7,.9]]
        if not secs[2]:continue
        areas=np.array([sum(p.area-sum(q.area for q in holes) for p,holes in s) for s in secs]);cv=float(areas.std()/max(areas.mean(),1e-9))
        circ=circle(secs[2][0][0])[2]
        analyses.append((cv,basis,local,lo,hi,secs,circ))
    analyses.sort(key=lambda x:x[0])
    for ai,(cv,basis,local,lo,hi,secs,circ) in enumerate(analyses):
        if cv<.3 or ai==0:
            components=secs[2]
            if len(components)<=12:
                yield dict(method='profile_extrude',basis=basis.tolist(),axis_rank=ai,features=[dict(z0=float(lo),z1=float(hi),outer=sketch(p),holes=[sketch(q) for q in hs]) for p,hs in components])
    # Shape-specific revolution fits use fresh meridian sections of this part.
    for cv,basis,local,lo,hi,secs,circ in sorted(analyses,key=lambda x:x[-1])[:2]:
        if circ>.04:continue
        if all(len(s)==1 and len(s[0][1])==0 for s in secs):
            try:
                from fit_revolve import fit
                spec=fit(local);q=np.array(spec['profile']);n=len(q)
                yield dict(method='spline_revolve',basis=basis.tolist(),axis_xy=spec['center_xy'],profile=q.tolist(),breaks=np.unique(np.linspace(0,n-1,9).astype(int)).tolist())
            except Exception as e:attempts.append(dict(stage='meridian_fit',error=str(e)))
        circles=[];holecounts=[]
        for f in np.r_[.002,np.linspace(.05,.95,15),.998]:
            s=section(local,lo+(hi-lo)*f)
            if len(s)!=1:break
            p,hs=s[0];c,r,err=circle(p)
            if err>.06 or len(hs)>1:break
            circles.append([r,float(lo+(hi-lo)*f),*c,circle(hs[0])[1] if hs else 0]);holecounts.append(len(hs))
        if len(circles)==17 and len(set(holecounts))==1:
            a=np.array(circles);a[0,1]=lo;a[-1,1]=hi
            yield dict(method='radial_revolve',basis=basis.tolist(),axis_xy=np.median(a[:,2:4],axis=0).tolist(),outer=a[:,:2].tolist(),inner=np.c_[a[::-1,4],a[::-1,1]].tolist() if holecounts[0] else [])
    # Smooth loft only when every section has consistent components and hole topology.
    # Branches are never silently discarded.
    for cv,basis,local,lo,hi,secs,circ in analyses[:4]:
        for n in [9,17]:
            zs=lo+(hi-lo)*np.r_[.003,np.linspace(.06,.94,n-2),.997]
            slices=[section(local,z) for z in zs];signature=[tuple(len(hs) for _,hs in s) for s in slices]
            if not slices[0] or len(slices[0])>8 or len(set(signature))!=1:continue
            features=[]
            for ci in range(len(slices[0])):
                track=[];previous=None
                for z,s in zip(zs,slices):
                    p,holes=s[ci];data=sketch(p,True,count=40)
                    if data['kind']=='spline' and previous is not None:
                        q=np.array(data['points']);q=min([np.roll(q,k,axis=0) for k in range(len(q))],key=lambda x:np.sum((x-previous)**2));data['points']=q.tolist()
                    previous=np.array(data['points']) if data['kind']=='spline' else None
                    track.append(dict(z=float(z),outer=data,holes=[sketch(h,True,40) for h in holes]))
                # Keep sampled end sections in their observed planes; report approximation via distance gate.
                features.append(dict(sections=track))
            yield dict(method='smooth_loft',basis=basis.tolist(),features=features,section_count=n)

def process(src,refine=False):
    started=time.time();rel=src.relative_to(ROOT);case,part=rel.parts[0],src.parent.name;base_od=OUT/'cases'/case/part;od=(OUT/'refinements'/case/part) if refine else base_od;od.mkdir(parents=True,exist_ok=True)
    report=dict(case_id=case,part_id=part,source_path=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),status='FAILED',gates=GATES,source_units='unknown; original numeric coordinates retained',new_fit=True,faceted_brep=False)
    attempts=[];best=None;best_runtime=None
    if refine and (base_od/'report.json').exists() and (base_od/'parameters.json').exists() and (base_od/'model.step').exists():
        old=json.loads((base_od/'report.json').read_text())
        if old.get('source_sha256')==report['source_sha256'] and old.get('quality'):
            best=(score(old['quality']),json.loads((base_od/'parameters.json').read_text()),cq.importers.importStep(str(base_od/'model.step')).val())
            best_runtime=(base_od/'cad.py').read_text().split('\nPARAMETERS = ')[0]
            attempts=json.loads((base_od/'attempts.json').read_text()) if (base_od/'attempts.json').exists() else []
            report['refinement_of_current_run']=True
    try:
        source=load(src);center=source.bounds.mean(0);scale=100/source.extents.max();m=source.copy();m.apply_translation(-center);m.apply_scale(scale)
        if not np.isfinite(m.vertices).all():raise ValueError('Nonfinite source')
        report.update(source_faces=len(source.faces),source_watertight=bool(source.is_watertight),source_volume_defined=bool(source.is_volume))
        ss=scene(m)
        np.savez_compressed(od/'evaluation_mesh.npz',vertices=m.vertices,faces=m.faces)
        fitmesh=m
        if len(m.faces)>45000:
            import open3d as o3d
            om=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(m.vertices),o3d.utility.Vector3iVector(m.faces)).simplify_quadric_decimation(45000)
            fitmesh=trimesh.Trimesh(np.asarray(om.vertices),np.asarray(om.triangles),process=True)
        report['fitting_mesh_faces']=len(fitmesh.faces)
        if refine:
            from refine_sections import candidates as refined_candidates
            proposals=refined_candidates(fitmesh)
        else:proposals=candidates(fitmesh,attempts)
        for spec in proposals:
            spec.update(center=center.tolist(),construction_scale=float(scale))
            try:
                print('TRY',spec['method'],round(time.time()-started,1),flush=True)
                dump(od/'candidate_parameters.json',spec)
                run=subprocess.run([sys.executable,str(SCRIPTS/'build_native_candidate.py'),str(od/'candidate_parameters.json'),str(od/'native_candidate.brep'),str(od/'evaluation_mesh.npz'),str(od/'candidate_quality.json')],capture_output=True,text=True,timeout=25)
                if run.returncode:raise ValueError(run.stderr[-1200:])
                shape=cq.Shape.importBrep(str(od/'native_candidate.brep'))
                q=json.loads((od/'candidate_quality.json').read_text())
                attempts.append(dict(method=spec['method'],quality=q,cad_faces=len(shape.Faces())))
                if best is None or score(q)<best[0]:
                    world=shape.scale(1/scale).translate(tuple(center));world.exportStep(str(od/'candidate.step'))
                    check=cq.importers.importStep(str(od/'candidate.step')).val()
                    if not check.isValid() or len(check.Solids())!=len(shape.Solids()):raise ValueError('STEP roundtrip invalid')
                    best=(score(q),spec,check)
                    best_runtime=(od/'candidate_runtime.txt').read_text()
                    dump(od/'best_parameters.json',spec)
                if passed(q):break
            except Exception as e:attempts.append(dict(method=spec['method'],error=str(e)))
            dump(od/'attempts.json',attempts)
            if time.time()-started>150 and best is not None:break
        if best is None:raise RuntimeError('No valid native smooth feature reconstruction')
        _,spec,world=best
        runtime_ns={};exec(compile(best_runtime,'chosen_runtime.py','exec'),runtime_ns)
        world=runtime_ns['partition_periodic_faces'](world.translate(tuple(-center)).scale(scale)).scale(1/scale).translate(tuple(center));spec['partition_final']=True
        world.exportStep(str(od/'model.step'));world.exportBrep(str(od/'model.brep'))
        # Final distances are evaluated against tessellation of the reimported STEP.
        actual=cq.importers.importStep(str(od/'model.step')).val();norm=actual.translate(tuple(-center)).scale(scale);cm=tess(norm,.025)
        q=evaluate(m,cm,10000,ss);cm.apply_scale(1/scale);cm.apply_translation(center);cm.export(od/'model.stl')
        dump(od/'parameters.json',spec)
        runtime=best_runtime
        code=runtime+'\nPARAMETERS = '+repr(spec)+'\n\nif __name__ == "__main__":\n    from pathlib import Path\n    p=Path(__file__).parent\n    shape=build_model(PARAMETERS)\n    assert shape.isValid() and shape.Solids()\n    shape.exportStep(str(p/"model.step"))\n    shape.exportBrep(str(p/"model.brep"))\n    shape.exportStl(str(p/"model.stl"),tolerance=0.025,angularTolerance=0.15)\n'
        (od/'cad.py').write_text(code)
        report.update(status='ACCEPTED' if passed(q) else 'NEEDS_REFINEMENT',method=spec['method'],quality=q,step_valid=bool(actual.isValid()),cad_faces=len(actual.Faces()),cad_solids=len(actual.Solids()),artifacts_complete=False)
        dump(od/'report.json',report)
        from smooth_visualize import extract_and_render
        counts=extract_and_render(actual,cm,od,report,source)
        report.update(**counts,artifacts_complete=True)
    except Exception as e:
        report.update(error=str(e),traceback=traceback.format_exc())
        if best is not None:report['status']='INCOMPLETE'
    report['seconds']=time.time()-started
    report['source_unchanged']=hashlib.sha256(src.read_bytes()).hexdigest()==report['source_sha256']
    dump(od/'attempts.json',attempts);dump(od/'report.json',report)
    if refine and report.get('artifacts_complete') and report.get('source_unchanged'):
        for name in ['model.step','model.brep','model.stl','cad.py','parameters.json','curves.json','curve_samples_256.npz','render_transform.json','surface_boundaries.png','source_vs_cad.png','attempts.json']:
            shutil.copy2(od/name,base_od/name)
        dump(base_od/'report.json',report)
    print(json.dumps({k:report.get(k) for k in ('case_id','part_id','status','method','seconds','error')},ensure_ascii=False),flush=True)
    return report

def summary(files):
    rows=[]
    for src in files:
        p=OUT/'cases'/src.relative_to(ROOT).parts[0]/src.parent.name/'report.json'
        rows.append(json.loads(p.read_text()) if p.exists() else dict(case_id=src.relative_to(ROOT).parts[0],part_id=src.parent.name,status='PENDING'))
    from collections import Counter
    s=dict(total_parts=len(rows),cases=len(set(r['case_id'] for r in rows)),status_counts=dict(Counter(r['status'] for r in rows)),new_fit_count=sum(r.get('new_fit',False) for r in rows),complete_artifact_count=sum(r.get('artifacts_complete',False) for r in rows),tank_skipped=True,gates=GATES,outputs=str(OUT))
    dump(OUT/'summary.json',s);dump(OUT/'manifest.json',rows)
    fields=['case_id','part_id','status','method','step_valid','cad_faces','cad_solids','boundary_count','seam_count','artifacts_complete','seconds','error']
    with (OUT/'manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    for case in sorted(set(r['case_id'] for r in rows)):
        dump(OUT/'cases'/case/'summary.json',[r for r in rows if r['case_id']==case])
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--part');ap.add_argument('--pilot',action='store_true');ap.add_argument('--force',action='store_true');ap.add_argument('--refine',action='store_true');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--summary',action='store_true');args=ap.parse_args()
    files=sorted(p for p in ROOT.glob('*/xpart_parts/PART_*/complete_part_*.obj') if p.relative_to(ROOT).parts[0]!='tank')
    OUT.mkdir(parents=True,exist_ok=True)
    if args.part:return process(ROOT/args.part,args.refine)
    if args.summary:print(json.dumps(summary(files)));return
    if args.pilot:
        cases=['2_of_jenga_classic_game','airplane','canister','vase','winerack','11pro_sl_trx_fg']
        files=[next(p for p in files if p.relative_to(ROOT).parts[0]==c) for c in cases]
    dump(OUT/'input_inventory.json',[str(p) for p in files])
    def run(src):
        rp=OUT/'cases'/src.relative_to(ROOT).parts[0]/src.parent.name/'report.json'
        if rp.exists():
            old=json.loads(rp.read_text())
            if old.get('artifacts_complete') and old.get('source_unchanged') and not args.force and (not args.refine or old.get('status')=='ACCEPTED'):return old
        od=rp.parent;od.mkdir(parents=True,exist_ok=True)
        with (od/'run.log').open('w') as f:
            try:
                rr=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--part',str(src.relative_to(ROOT))]+(['--refine'] if args.refine else []),stdout=f,stderr=subprocess.STDOUT,timeout=300)
                if rr.returncode:raise RuntimeError('worker exited '+str(rr.returncode))
            except Exception as e:
                old=json.loads(rp.read_text()) if rp.exists() else dict(case_id=src.relative_to(ROOT).parts[0],part_id=src.parent.name)
                old.update(status='TIMEOUT' if isinstance(e,subprocess.TimeoutExpired) else 'FAILED',error=str(e));dump(rp,old)
        return json.loads(rp.read_text()) if rp.exists() else dict(status='FAILED')
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        fs=[pool.submit(run,p) for p in files]
        for i,f in enumerate(as_completed(fs),1):
            r=f.result();print('DONE',i,len(files),r.get('case_id'),r.get('part_id'),r['status'],flush=True)
            if i%10==0:summary(files)
    print(json.dumps(summary(files)),flush=True)
if __name__=='__main__':main()
