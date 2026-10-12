"""Execute each delivered CAD script alone, check geometry and related artifacts."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile,time
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
REQUIRED=['model.step','model.brep','model.stl','cad.py','parameters.json','curves.json','curve_samples_256.npz','render_transform.json','surface_boundaries.png','source_vs_cad.png','report.json']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def matching_supports(shape,other,diag,center,original_xyz):
    import numpy as np
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from smooth_visualize import extract
    def key(f):return (f.geomType(),round(f.Area()/diag**2,7),*[round(v/diag,7) for v in f.Center().toTuple()])
    if len(shape.Faces())!=len(other.Faces()):return False
    for fa,fb in zip(sorted(shape.Faces(),key=key),sorted(other.Faces(),key=key)):
        sa,sb=BRepAdaptor_Surface(fa.wrapped,True),BRepAdaptor_Surface(fb.wrapped,True)
        a=[sa.FirstUParameter(),sa.LastUParameter(),sa.FirstVParameter(),sa.LastVParameter()]
        b=[sb.FirstUParameter(),sb.LastUParameter(),sb.FirstVParameter(),sb.LastVParameter()]
        if fa.geomType()!=fb.geomType() or not np.allclose(a,b,rtol=1e-8,atol=1e-8):return False
        for fu in (.07,.29,.5,.71,.93):
            for fv in (.07,.29,.5,.71,.93):
                u,v=a[0]+fu*(a[1]-a[0]),a[2]+fv*(a[3]-a[2])
                if sa.Value(u,v).Distance(sb.Value(u,v))/diag>1e-7:return False
    _,xyz=extract(other)
    return xyz.shape==original_xyz.shape and np.allclose((xyz-center)/diag,(original_xyz-center)/diag,rtol=1e-7,atol=1e-7)
def inspect(od):
    import cadquery as cq,numpy as np
    from PIL import Image
    from regenerate_smooth import tess,evaluate
    from smooth_visualize import extract
    r=json.loads((od/'report.json').read_text());errors=[]
    for name in REQUIRED:
        if not (od/name).is_file():errors.append('missing '+name)
    if errors:return dict(errors=errors,passed=False)
    h={n:digest(od/n) for n in ('model.step','cad.py','report.json')}
    source=Path(r['source_path'])
    if digest(source)!=r['source_sha256']:errors.append('source hash changed')
    shape=cq.importers.importStep(str(od/'model.step')).val()
    if not shape.isValid() or not shape.Solids():errors.append('invalid delivered STEP')
    curves=json.loads((od/'curves.json').read_text())['curves'];sample=np.load(od/'curve_samples_256.npz')
    actual,actualxyz=extract(shape)
    if len(curves)!=len(actual) or len(curves)!=r['total_curve_count']:errors.append('curve count mismatch')
    if sum(not c['is_seam'] for c in actual)!=r['boundary_count']:errors.append('boundary count mismatch')
    if sample['curve_xyz'].shape!=(len(curves),256,3):errors.append('sample array shape')
    elif not np.allclose(actualxyz,sample['curve_xyz'],rtol=1e-7,atol=1e-7):errors.append('curves do not match STEP')
    for name,size in [('surface_boundaries.png',(2000,1630)),('source_vs_cad.png',(2000,860))]:
        with Image.open(od/name) as im:
            im.load()
            if im.size!=size:errors.append('wrong image size '+name)
    with tempfile.TemporaryDirectory(prefix='cad_rebuild_',dir=ROOT/'validation') as td:
        td=Path(td);(td/'cad.py').write_bytes((od/'cad.py').read_bytes())
        rebuilt=subprocess.run([sys.executable,str(td/'cad.py')],cwd=td,capture_output=True,text=True,timeout=90)
        if rebuilt.returncode:return dict(passed=False,errors=errors+['standalone script failed: '+rebuilt.stderr[-1500:]],hashes=h)
        other=cq.importers.importStep(str(td/'model.step')).val()
        if not other.isValid():errors.append('standalone STEP invalid')
        a=shape.BoundingBox();b=other.BoundingBox();diag=(a.xlen*a.xlen+a.ylen*a.ylen+a.zlen*a.zlen)**.5
        bbox_delta=max(abs(getattr(a,k)-getattr(b,k)) for k in ('xmin','xmax','ymin','ymax','zmin','zmax'))/diag
        volume_delta=abs(shape.Volume()-other.Volume())/max(abs(shape.Volume()),1e-12)
        area_delta=abs(shape.Area()-other.Area())/max(shape.Area(),1e-12)
        topology_match=(len(shape.Faces()),len(shape.Edges()),len(shape.Solids()))==(len(other.Faces()),len(other.Edges()),len(other.Solids()))
        if bbox_delta>1e-5 or volume_delta>1e-4 or area_delta>1e-4 or not topology_match:errors.append('standalone geometry or topology mismatch')
        center=((a.xmin+a.xmax)/2,(a.ymin+a.ymax)/2,(a.zmin+a.zmax)/2)
        base_result=dict(hashes=h,bbox_relative_delta=bbox_delta,volume_relative_delta=volume_delta,area_relative_delta=area_delta,topology_match=topology_match,source_unchanged=True)
        if errors:return dict(passed=False,errors=errors,**base_result)
        if matching_supports(shape,other,diag,center,actualxyz):
            if h!={n:digest(od/n) for n in h}:errors.append('output changed during audit; rerun required')
            return dict(passed=not errors,errors=errors,exact_surface_check=dict(method='matching parameterized surface supports and all 256-point trimmed boundary curves',passed=True),**base_result)
        aa=shape.translate(tuple(-v for v in center)).scale(100/diag);bb=other.translate(tuple(-v for v in center)).scale(100/diag)
        ma,mb=tess(aa,.01),tess(bb,.01)
        meshes_identical=ma.vertices.shape==mb.vertices.shape and ma.faces.shape==mb.faces.shape and np.array_equal(ma.faces,mb.faces) and np.allclose(ma.vertices,mb.vertices,rtol=1e-9,atol=1e-7)
        q=evaluate(ma,mb,2048)
        exact_check=None
        if not errors and not meshes_identical and (q['p95_distance_pct_diagonal']>.02 or q['sampled_max_distance_pct_diagonal']>.05):
            from OCP.BRepAdaptor import BRepAdaptor_Surface
            # Equal support surfaces plus equal trimmed boundary curves avoid an
            # ill-conditioned point projection on high-curvature NURBS surfaces.
            support_equal=topology_match and bbox_delta<1e-7 and volume_delta<1e-4 and area_delta<1e-4
            def face_key(f):return (f.geomType(),round(f.Area()/diag**2,7),*[round(v/diag,7) for v in f.Center().toTuple()])
            if support_equal:
                for fa,fb in zip(sorted(shape.Faces(),key=face_key),sorted(other.Faces(),key=face_key)):
                    sa,sb=BRepAdaptor_Surface(fa.wrapped,True),BRepAdaptor_Surface(fb.wrapped,True)
                    ba=[sa.FirstUParameter(),sa.LastUParameter(),sa.FirstVParameter(),sa.LastVParameter()]
                    bbounds=[sb.FirstUParameter(),sb.LastUParameter(),sb.FirstVParameter(),sb.LastVParameter()]
                    if fa.geomType()!=fb.geomType() or not np.allclose(ba,bbounds,rtol=1e-8,atol=1e-8):support_equal=False;break
                    for fu in (.07,.29,.5,.71,.93):
                        for fv in (.07,.29,.5,.71,.93):
                            u,v=ba[0]+fu*(ba[1]-ba[0]),ba[2]+fv*(ba[3]-ba[2])
                            if sa.Value(u,v).Distance(sb.Value(u,v))/diag>1e-7:support_equal=False
            if support_equal:
                other_records,other_xyz=extract(other)
                support_equal=other_xyz.shape==actualxyz.shape and np.allclose((other_xyz-center)/diag,(actualxyz-center)/diag,rtol=1e-7,atol=1e-7)
            if support_equal:
                exact_check=dict(method='matching parameterized surface supports and all 256-point trimmed boundary curves',passed=True)
        if not errors and not meshes_identical and exact_check is None and (q['p95_distance_pct_diagonal']>.02 or q['sampled_max_distance_pct_diagonal']>.05):
            # Independent OCC tessellations can differ even for the same surface.
            # Resolve this using trimmed surface points and exact B-Rep distances.
            from OCP.BRepAdaptor import BRepAdaptor_Surface
            from OCP.BRepClass import BRepClass_FaceClassifier
            from OCP.gp import gp_Pnt2d
            from OCP.TopAbs import TopAbs_IN,TopAbs_ON
            distances=[];self_distances=[];distance_differences=[]
            for src,target in ((shape,other),(other,shape)):
                for face in sorted(src.Faces(),key=lambda f:-f.Area())[:32]:
                    ad=BRepAdaptor_Surface(face.wrapped,True)
                    u0,u1,v0,v1=ad.FirstUParameter(),ad.LastUParameter(),ad.FirstVParameter(),ad.LastVParameter()
                    for fu in (.15,.5,.85):
                        for fv in (.15,.5,.85):
                            u,v=u0+(u1-u0)*fu,v0+(v1-v0)*fv
                            state=BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(u,v),1e-7).State()
                            if state not in (TopAbs_IN,TopAbs_ON):continue
                            p=ad.Value(u,v);vertex=cq.Vertex.makeVertex(p.X(),p.Y(),p.Z())
                            ds=vertex.distance(src)/diag;dt=vertex.distance(target)/diag
                            self_distances.append(ds);distance_differences.append(abs(dt-ds))
                            if ds<1e-7:distances.append(dt)
            exact_check=dict(valid_surface_points=len(distances),excluded_surface_points=sum(d>=1e-7 for d in self_distances),max_relative_distance=max(distances) if distances else None,max_self_relative_distance=max(self_distances) if self_distances else None,max_distance_difference=max(distance_differences) if distance_differences else None)
            if not distances or max(distances)>1e-7 or max(distance_differences)>1e-7:errors.append('standalone surface distance mismatch')
    if h!={n:digest(od/n) for n in h}:errors.append('output changed during audit; rerun required')
    return dict(passed=not errors,errors=errors,hashes=h,bbox_relative_delta=bbox_delta,volume_relative_delta=volume_delta,area_relative_delta=area_delta,topology_match=topology_match,rebuild_tessellations_identical=meshes_identical,rebuild_distance=q,exact_surface_check=exact_check,source_unchanged=True)
def run(od):
    dest=ROOT/'validation'/od.parent.name/(od.name+'.json');dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        old=json.loads(dest.read_text())
        if old.get('hashes')=={n:digest(od/n) for n in ('model.step','cad.py','report.json')} and old.get('passed'):return old
    try:
        p=subprocess.run([sys.executable,__file__,'--one',str(od)],capture_output=True,text=True,timeout=300)
        result=json.loads(p.stdout.split('AUDIT_RESULT ')[-1]) if p.returncode==0 else dict(passed=False,errors=[p.stderr[-2000:]])
    except Exception as e:result=dict(passed=False,errors=[str(e)])
    result.update(case_id=od.parent.name,part_id=od.name);dest.write_text(json.dumps(result,indent=2))
    print('AUDITED',od.parent.name,od.name,result['passed'],result.get('errors'),flush=True)
    return result
if __name__=='__main__':
    (ROOT/'validation').mkdir(exist_ok=True)
    if len(sys.argv)>1 and sys.argv[1]=='--one':print('AUDIT_RESULT '+json.dumps(inspect(Path(sys.argv[2]))));sys.exit()
    paths=[]
    for p in sorted((ROOT/'cases').glob('*/*/report.json')):
        if json.loads(p.read_text()).get('artifacts_complete'):paths.append(p.parent)
    with ThreadPoolExecutor(max_workers=24) as pool:results=list(pool.map(run,paths))
    summary=dict(total=len(results),passed=sum(r['passed'] for r in results),failed=[r for r in results if not r['passed']])
    (ROOT/'validation/summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
