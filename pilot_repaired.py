"""Executable feature CAD pilot. Source inputs are read-only; no mesh-to-BRep path."""
from pathlib import Path
import os, sys, json, csv, hashlib, subprocess, tempfile, shutil, ast, copy, time, traceback
from collections import Counter
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.optimize import least_squares
from shapely.geometry import Polygon, LineString
from shapely.geometry.polygon import orient
# Compatibility aliases for the server's pyparsing/ezdxf combination.
try:
    import pyparsing, builtins
    for _old, _new in [('add_parse_action','addParseAction'), ('set_results_name','setResultsName'), ('add_condition','addCondition'), ('parse_string','parseString')]:
        if hasattr(pyparsing.ParserElement, _new) and not hasattr(pyparsing.ParserElement, _old): setattr(pyparsing.ParserElement, _old, getattr(pyparsing.ParserElement, _new))
    for _old, _new in [('one_of','oneOf'), ('infix_notation','infixNotation'), ('delimited_list','delimitedList')]:
        if hasattr(pyparsing, _new): setattr(builtins, _old, getattr(pyparsing, _new))
except Exception:
    pass
import cadquery as cq

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_executable_cad_v1')
VERSION = 'pilot_repaired_20260921_v1'
ENV = os.environ.copy()
ENV.pop('PYTHONPATH', None)
ENV.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf-8')

def csvwrite(path, rows, fields=None):
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def load(p):
    m = trimesh.load(p, force='mesh', process=False)
    if isinstance(m, trimesh.Scene): m = m.to_mesh()
    m.merge_vertices(); m.remove_unreferenced_vertices()
    return m

def frame(axis):
    z = np.asarray(axis, float); z /= np.linalg.norm(z)
    h = np.eye(3)[np.argmin(abs(z))]
    x = np.cross(h, z); x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])

def circle_fit(x):
    x = np.asarray(x)
    A = np.column_stack([2*x, np.ones(len(x))])
    v = np.linalg.lstsq(A, (x*x).sum(1), rcond=None)[0]
    c = v[:2]; r = np.sqrt(max(v[2]+c@c, 1e-20))
    fit = least_squares(lambda a: np.linalg.norm(x-a[:2], axis=1)-a[2], [*c, r], max_nfev=40)
    c, r = fit.x[:2], abs(fit.x[2])
    err = np.sqrt(np.mean((np.linalg.norm(x-c, axis=1)-r)**2))/max(r, 1e-10)
    return c, r, float(err)

def fit_profile(poly, diag, cap=20):
    """A section is reduced to an analytic or bounded sketch, never source triangles."""
    poly = orient(poly, sign=1)
    ring = LineString(poly.exterior.coords)
    x = np.array([ring.interpolate(t, normalized=True).coords[0] for t in np.linspace(0,1,96,endpoint=False)])
    c, r, err = circle_fit(x)
    if err < .015:
        e = dict(type='SKETCH_CIRCLE', center=c.tolist(), radius=float(r))
        area, count = np.pi*r*r, 1
    else:
        lo, hi = np.array(poly.bounds[:2]), np.array(poly.bounds[2:])
        dims = hi-lo; mid=(hi+lo)/2
        if abs(poly.area/np.prod(dims)-1) < .008:
            e=dict(type='SKETCH_RECTANGLE', center=mid.tolist(), width=float(dims[0]), height=float(dims[1]))
            area, count = np.prod(dims), 4
        else:
            a,b=dims/2
            er=np.sqrt(np.mean((np.sqrt(((x-mid)**2/[a*a,b*b]).sum(1))-1)**2))
            if er < .015:
                e=dict(type='SKETCH_ELLIPSE',center=mid.tolist(), x_radius=float(a), y_radius=float(b))
                area,count=np.pi*a*b,1
            else:
                tol=diag*.001
                s=poly.simplify(tol,preserve_topology=True)
                while len(s.exterior.coords)-1>cap:
                    tol*=1.35; s=poly.simplify(tol,preserve_topology=True)
                pts=np.asarray(s.exterior.coords[:-1])
                if len(pts)<3 or not s.is_valid: raise ValueError('SKETCH_CLOSURE_ERROR')
                e=dict(type='SKETCH_POLYGON', points=pts.tolist())
                area,count=s.area,len(pts)
    e['profile_validation']=dict(closed=True, closure_error=0., self_intersection=False,
        orientation='CCW', profile_area=float(area), profile_entity_count=int(count),
        source_section_area=float(poly.area), circle_fit_relative_rms=err)
    return e

def section_data(m, R, center, fractions):
    y=(m.vertices-center)@R
    zlo,zhi=y[:,2].min(),y[:,2].max()
    result=[]
    for f in fractions:
        z=float(zlo+(zhi-zlo)*f)
        cut=m.section(plane_origin=center+R[:,2]*z,plane_normal=R[:,2])
        loops=[]
        if cut is not None:
            for line in cut.discrete:
                xy=((line-center)@R)[:,:2]
                if np.linalg.norm(xy[0]-xy[-1]) > np.linalg.norm(m.extents)*1e-5: continue
                p=Polygon(xy)
                if p.is_valid and p.area > np.linalg.norm(m.extents)**2*1e-8: loops.append(p)
        loops.sort(key=lambda p:-p.area)
        components=[]
        for p in loops:
            containing=[q for q in loops if q.area>p.area and q.contains(p.representative_point())]
            if len(containing)%2==0:
                holes=[q for q in loops if q.area<p.area and p.contains(q.representative_point())
                    and len([v for v in loops if v.area>q.area and v.contains(q.representative_point())])==len(containing)+1]
                components.append((p,holes))
        result.append(dict(z=z,components=components,area=float(sum(p.area-sum(h.area for h in hs) for p,hs in components))))
    return result,float(zlo),float(zhi)

def geometry(m):
    diag=float(np.linalg.norm(m.extents)); center=m.bounds.mean(0)
    _,R=np.linalg.eigh(np.cov((m.vertices-center).T)); R=R[:,::-1]
    if np.linalg.det(R)<0:R[:,-1]*=-1
    axes=[*np.eye(3), *R.T]
    # Add the dominant area-weighted planar normal when it differs from these axes.
    normals=m.face_normals.copy(); signs=np.sign(normals[np.arange(len(normals)),np.argmax(abs(normals),axis=1)])
    normals*=signs[:,None]
    bins=np.round(normals/.06).astype(int)
    uniq,inv=np.unique(bins,axis=0,return_inverse=True)
    weights=np.bincount(inv,weights=m.area_faces)
    for idx in np.argsort(weights)[-3:]:
        a=np.average(normals[inv==idx],axis=0,weights=m.area_faces[inv==idx]); a/=np.linalg.norm(a)
        if all(abs(a@v)<.985 for v in axes):axes.append(a)
    analyses=[]
    for axis in axes:
        basis=frame(axis)
        try:
            sections,lo,hi=section_data(m,basis,center,[.08,.25,.5,.75,.92])
            areas=np.array([s['area'] for s in sections]); available=[s for s in sections if s['components']]
            if len(available)<3:continue
            mid=min(available,key=lambda s:abs(s['z']-(lo+hi)/2))
            outer=mid['components'][0][0]
            ring=LineString(outer.exterior.coords)
            pts=np.array([ring.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,96,endpoint=False)])
            c,rad,cerr=circle_fit(pts)
            variation=float(areas.std()/max(areas.mean(),1e-12))
            volumefit=abs(mid['area']*(hi-lo)-abs(m.volume))/max(abs(m.volume),1e-12)
            profiles=[s['components'][0][0] for s in available]
            overlap=float(np.mean([outer.intersection(q).area/max(outer.union(q).area,1e-12) for q in profiles]))
            analyses.append(dict(R=basis,center=center,sections=sections,lo=lo,hi=hi,
                variation=variation,profile_overlap=overlap,circle_error=cerr,rad=rad,circle_center=c,
                extrude_cost=variation+.4*volumefit+(1-overlap),revolve_cost=cerr))
        except Exception as ex:
            print('section_warning',str(ex)[:100],flush=True)
    if not analyses:raise ValueError('NO_SIMPLE_CAD_EXPLANATION')
    bestex=min(analyses,key=lambda d:d['extrude_cost']); bestrv=min(analyses,key=lambda d:d['revolve_cost'])
    holes=max(sum(len(h) for _,h in s['components']) for a in analyses for s in a['sections'])
    sharp=m.face_adjacency_angles>np.deg2rad(30)
    planar=float(weights[weights/m.area>.025].sum()/m.area)
    axis=bestrv['R'][:,2]; radial=(m.triangles_center-center)-np.outer((m.triangles_center-center)@axis,axis)
    radial/=np.maximum(np.linalg.norm(radial,axis=1,keepdims=True),1e-12)
    cylindrical=float(m.area_faces[(abs(m.face_normals@axis)<.08)&(abs((radial*m.face_normals).sum(1))>.98)].sum()/m.area)
    if bestex['extrude_cost']<.15: family='EXTRUDE_HOLE' if holes else 'PROFILE_EXTRUSION'
    elif bestrv['circle_error']<.035: family='REVOLUTION'
    else:family='FREEFORM_DIFFICULT'
    analysis=dict(watertight=bool(m.is_watertight),is_volume=bool(m.is_volume),vertices=len(m.vertices),faces=len(m.faces),
        connected_components=len(m.split(only_watertight=False)),bbox_x=float(m.extents[0]),bbox_y=float(m.extents[1]),
        bbox_z=float(m.extents[2]),bbox_diagonal=diag,centroid=m.centroid.tolist(),volume=float(m.volume),surface_area=float(m.area),
        principal_axes=R.tolist(),planar_region_ratio=planar,cylindrical_region_ratio=cylindrical,
        region_ratio_method='area weighted normal clusters >2.5%; radial normals within 0.98 cosine, axis-normal <0.08',
        candidate_extrusion_axes=[dict(direction=a['R'][:,2].tolist(),section_area_cv=a['variation'],profile_overlap=a['profile_overlap'],
            cost=a['extrude_cost'],section_count=len(a['sections'])) for a in analyses],
        candidate_revolve_axes=[dict(direction=a['R'][:,2].tolist(),circle_relative_rms=a['circle_error']) for a in analyses],
        symmetry=dict(rotational_relative_rms=bestrv['circle_error'],axis=bestrv['R'][:,2].tolist()),
        holes=dict(max_section_holes=holes,method='nested closed cross-sections',blind_pocket_detection='limited to sampled sections'),
        sharp_edges=dict(count=int(sharp.sum()),angle_threshold_degrees=30),geometry_family=family,
        confidence=float(max(0.,1-min(bestex['extrude_cost'],bestrv['circle_error']*4))),
        candidate_operations=['EXTRUDE','REVOLVE','CUT','UNION'],
        limitations=['Five sections per candidate axis; narrow unseen cavities can remain unrecovered.',
            'Freeform surfaces, arbitrary blind pockets and detailed edge blends are not guaranteed recoverable.'])
    return analysis,bestex,bestrv

def entity_clean(e):return {k:v for k,v in e.items() if k!='profile_validation'}

def make_program(family,R,center,ops):
    return dict(version='XPART_CAD_DSL_V1',geometry_family=family,
        workplane=dict(origin=np.asarray(center).tolist(),x_direction=R[:,0].tolist(),normal=R[:,2].tolist()),operations=ops)

def extrusion_ops(components,z0,z1,diag,prefix='b',cap=20):
    ops=[]; outputs=[]
    for j,(outer,holes) in enumerate(components[:3]):
        k=f'{prefix}{j}'; e=fit_profile(outer,diag,cap=cap)
        ops.extend([dict(**e,id=k,z=z0),dict(type='EXTRUDE',id=k,distance=z1-z0)])
        for h,q in enumerate(holes[:3]):
            hk=f'{k}h{h}'; he=fit_profile(q,diag,cap=cap)
            ops.extend([dict(**he,id=hk,z=z0),dict(type='EXTRUDE',id=hk,distance=z1-z0),dict(type='CUT',id=k,tool=hk)])
        outputs.append(k)
    for other in outputs[1:]:ops.append(dict(type='UNION',id=outputs[0],tool=other))
    return ops,outputs[0]

def programs(m, analysis, ex, rv):
    diag=float(np.linalg.norm(m.extents)); origin=m.bounds.mean(0)
    # Score primitive proposals by surface residual, not by their labels.
    pts,_=trimesh.sample.sample_surface(m,4096,seed=73)
    primitive=[]
    for R in [np.eye(3),ex['R']]:
        y=(m.vertices-origin)@R; lo=y.min(0); hi=y.max(0); dims=hi-lo; c=(lo+hi)/2
        q=abs((pts-origin)@R-c)-dims/2
        dist=np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(q.max(1),0)
        p=make_program('EXTRUSION',R,origin,[dict(type='SKETCH_RECTANGLE',id='body',center=c[:2].tolist(),width=float(dims[0]),height=float(dims[1]),z=float(lo[2])),dict(type='EXTRUDE',id='body',distance=float(dims[2]))])
        primitive.append((np.mean(abs(dist))/diag,p))
    R=rv['R']; y=(pts-origin)@R; c=rv['circle_center']; rad=rv['rad']; h=rv['hi']-rv['lo']
    q=np.column_stack([np.linalg.norm(y[:,:2]-c,axis=1)-rad,abs(y[:,2]-(rv['hi']+rv['lo'])/2)-h/2])
    d=np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(q.max(1),0)
    primitive.append((np.mean(abs(d))/diag,make_program('PRIMITIVE',R,origin,[dict(type='SKETCH_CIRCLE',id='body',center=c.tolist(),radius=float(rad),z=rv['lo']),dict(type='EXTRUDE',id='body',distance=h)])))
    fit=least_squares(lambda a:np.linalg.norm(pts-a[:3],axis=1)-a[3],[*origin,diag/3],max_nfev=50)
    primitive.append((np.mean(abs(fit.fun))/diag,make_program('PRIMITIVE',np.eye(3),fit.x[:3],[dict(type='SPHERE',id='body',radius=float(abs(fit.x[3])))])))
    proposed=[('primitive',min(primitive,key=lambda t:t[0])[1])]
    sec=min(ex['sections'],key=lambda s:abs(s['z']-(ex['lo']+ex['hi'])/2))
    ops,res=extrusion_ops(sec['components'],ex['lo'],ex['hi'],diag)
    ops.append(dict(type='RESULT',id=res))
    proposed.append(('profile',make_program('EXTRUDE_HOLE' if any(h for _,h in sec['components']) else 'PROFILE_EXTRUSION',ex['R'],origin,ops)))
    # A bounded radial profile from cross-sections; maximum 14 profile points.
    R=rv['R']; secs,lo,hi=section_data(m,R,origin,[.002,.05,.15,.25,.35,.5,.65,.75,.85,.95,.998])
    circles=[]
    for s in secs:
        if not s['components']:continue
        po,hs=s['components'][0]
        ring=LineString(po.exterior.coords)
        xy=np.array([ring.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,64,endpoint=False)])
        cc,rr,err=circle_fit(xy); inner=0.
        if hs:
            hh=max(hs,key=lambda q:q.area)
            inner=np.sqrt(hh.area/np.pi)
        circles.append([s['z'],rr,inner,*cc])
    if len(circles)>=3:
        a=np.array(circles); axisxy=np.median(a[:,3:5],axis=0)
        outer=np.column_stack([a[:,1],a[:,0]]);outer[0,1]=lo;outer[-1,1]=hi
        if np.max(a[:,2])>diag*.003:
            inner=np.column_stack([a[::-1,2],a[::-1,0]]);inner[0,1]=hi;inner[-1,1]=lo
        else:inner=np.array([[0.,hi],[0.,lo]])
        poly=Polygon(np.vstack([outer,inner]));tol=diag*.001
        simplified=poly.simplify(tol,preserve_topology=True)
        while len(simplified.exterior.coords)>15:
            tol*=1.4;simplified=poly.simplify(tol,preserve_topology=True)
        rcenter=origin+R[:,:2]@axisxy
        points=list(map(list,simplified.exterior.coords[:-1]))
        rvplane=np.column_stack([R[:,0],R[:,2],-R[:,1]])
        ops=[dict(type='SKETCH_POLYGON',id='body',points=points,z=0.,profile_validation=dict(closed=True,closure_error=0.,self_intersection=not simplified.is_valid,orientation='CCW' if simplified.exterior.is_ccw else 'CW',profile_area=float(simplified.area),profile_entity_count=len(points))),dict(type='REVOLVE',id='body',angle=360.,axis_start=[0.,0.],axis_end=[0.,1.])]
        proposed.append(('revolve',make_program('REVOLUTION',rvplane,rcenter,ops)))
    # Three bounded feature slabs: union of sketches; holes are CAD cuts.
    ops=[];ids=[]
    for j,f in enumerate([1/6,.5,5/6]):
        s=min(ex['sections'],key=lambda s:abs(s['z']-(ex['lo']+(ex['hi']-ex['lo'])*f)))
        if not s['components']:continue
        z0=ex['lo']+(ex['hi']-ex['lo'])*j/3;z1=ex['lo']+(ex['hi']-ex['lo'])*(j+1)/3
        partops,res=extrusion_ops(s['components'][:1],z0,z1,diag,prefix=f's{j}',cap=10)
        ops.extend(partops);ids.append(res)
    for other in ids[1:]:ops.append(dict(type='UNION',id=ids[0],tool=other))
    ops.append(dict(type='RESULT',id=ids[0]))
    proposed.append(('composite',make_program('BOOLEAN_COMPOSITE',ex['R'],origin,ops)))
    return proposed[:4]

def cad_code(p,diag):
    """The generated file embeds numeric CAD parameters and reads no input files."""
    w=p['workplane']
    lines=['import pyparsing, builtins',
        "for _old, _new in [('add_parse_action','addParseAction'), ('set_results_name','setResultsName'), ('add_condition','addCondition'), ('parse_string','parseString')]:",
        "    if hasattr(pyparsing.ParserElement, _new) and not hasattr(pyparsing.ParserElement, _old): setattr(pyparsing.ParserElement, _old, getattr(pyparsing.ParserElement, _new))",
        "for _old, _new in [('one_of','oneOf'), ('infix_notation','infixNotation'), ('delimited_list','delimitedList')]:",
        "    if hasattr(pyparsing, _new): setattr(builtins, _old, getattr(pyparsing, _new))",
        'import cadquery as cq','from pathlib import Path','','def build_model():',
        f"    plane = cq.Plane(origin={w['origin']!r}, xDir={w['x_direction']!r}, normal={w['normal']!r})"]
    result=None
    for op in p['operations']:
        k=op['id'];t=op['type'];result=k
        if t.startswith('SKETCH_'):
            lines.append(f"    {k} = cq.Workplane(plane).workplane(offset={op.get('z',0.)!r})")
            if t=='SKETCH_POLYGON':lines.append(f"    {k} = {k}.polyline({op['points']!r}).close()")
            else:
                lines.append(f"    {k} = {k}.center({op['center'][0]!r}, {op['center'][1]!r})")
                if t=='SKETCH_CIRCLE':lines.append(f"    {k} = {k}.circle({op['radius']!r})")
                elif t=='SKETCH_RECTANGLE':lines.append(f"    {k} = {k}.rect({op['width']!r}, {op['height']!r})")
                elif t=='SKETCH_ELLIPSE':lines.append(f"    {k} = {k}.ellipse({op['x_radius']!r}, {op['y_radius']!r})")
        elif t=='EXTRUDE':lines.append(f"    {k} = {k}.extrude({op['distance']!r})")
        elif t=='REVOLVE':lines.append(f"    {k} = {k}.revolve({op['angle']!r}, {op['axis_start']!r}, {op['axis_end']!r})")
        elif t=='SPHERE':lines.append(f"    {k} = cq.Workplane(plane).sphere({op['radius']!r})")
        elif t=='CUT':lines.append(f"    {k} = {k}.cut({op['tool']})")
        elif t=='UNION':lines.append(f"    {k} = {k}.union({op['tool']})")
        elif t=='FILLET':lines.append(f"    {k} = {k}.edges().fillet({op['radius']!r})")
        elif t!='RESULT':raise ValueError(t)
    lines.extend([f'    return {result}', '', "if __name__ == '__main__':",'    body = build_model()',
        "    output = Path(__file__).resolve().parent",
        "    cq.exporters.export(body, str(output / 'reconstructed.step'))",
        f"    cq.exporters.export(body, str(output / 'reconstructed.stl'), tolerance={diag*0.00015!r}, angularTolerance=0.08)",
        "    print({'valid': body.val().isValid(), 'solids': body.solids().size(), 'faces': body.faces().size()})"])
    return '\n'.join(lines)+'\n'

def validate_program(p):
    allowed={'SKETCH_POLYGON','SKETCH_CIRCLE','SKETCH_ELLIPSE','SKETCH_RECTANGLE','SPHERE','EXTRUDE','REVOLVE','CUT','UNION','FILLET','RESULT'}
    assert p['version']=='XPART_CAD_DSL_V1'
    assert all(o['type'] in allowed for o in p['operations'])
    assert len(p['operations'])<=48
    assert all(len(o.get('points',[]))<=20 for o in p['operations'])
    assert sum(len(o.get('points',[])) for o in p['operations'])<=72
    assert all(o.get('profile_validation',{}).get('self_intersection',False) is False for o in p['operations'])
    json.dumps(p,allow_nan=False)
    return True

def complexity(p):
    def numeric(x):
        if isinstance(x,dict):return sum(numeric(v) for k,v in x.items() if k!='profile_validation')
        if isinstance(x,list):return sum(numeric(v) for v in x)
        return int(isinstance(x,(int,float)) and not isinstance(x,bool))
    ops=[o for o in p['operations'] if o['type']!='RESULT']
    entities=sum(len(o['points']) if 'points' in o else 4 if o['type']=='SKETCH_RECTANGLE' else 1 if o['type'].startswith('SKETCH') else 0 for o in ops)
    return dict(feature_count=len(ops),parameter_count=numeric(p),sketch_entity_count=entities,
        boolean_count=sum(o['type'] in ['CUT','UNION'] for o in ops))

def mesh_used(code):
    tree=ast.parse(code)
    modules=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):modules.extend(n.name for n in node.names)
        if isinstance(node,ast.ImportFrom):modules.append(node.module)
    bad=any(x.split('.')[0] in ['trimesh','meshio','numpy-stl','stl','open3d','vtk'] for x in modules)
    banned=['trimesh.load','meshio','read_stl','importStl','Mesh','STL','OBJ','PLY','source.stl','source.obj','source.ply','open(','read_text','read_bytes','importers']
    return bad or any(x in code for x in banned)

def execute(p,folder,diag):
    folder.mkdir(parents=True,exist_ok=True)
    validate_program(p);code=cad_code(p,diag);ast.parse(code)
    if mesh_used(code):raise ValueError('REJECTED_MESH_CONVERSION')
    (folder/'cad.py').write_text(code,encoding='utf-8');dump(folder/'program.json',p)
    for name in ['reconstructed.step','reconstructed.stl']:
        (folder/name).unlink(missing_ok=True)
    run=subprocess.run([sys.executable,'cad.py'],cwd=folder,env=ENV,capture_output=True,text=True,timeout=180)
    (folder/'execution.log').write_text(run.stdout+'\n'+run.stderr)
    if run.returncode:raise RuntimeError('CAD_EXECUTION_ERROR: '+run.stderr[-1200:])
    model=cq.importers.importStep(str(folder/'reconstructed.step')).val()
    if not model.isValid() or not model.Solids():raise ValueError('BREP_INVALID')
    cad=load(folder/'reconstructed.stl')
    checks=dict(CAD_PARSE='PASS',CAD_EXECUTION='PASS',BREP_VALID='YES',SOLID_COUNT=len(model.Solids()),
        STEP_EXPORT='PASS',STEP_RELOAD='PASS',MESH_EXPORT='PASS',PROGRAM_JSON_VALID='YES',NO_SOURCE_MESH_IMPORT='YES',
        cad_brep_face_count=len(model.Faces()),face_types=dict(Counter(f.geomType() for f in model.Faces())),
        reconstructed_watertight=bool(cad.is_watertight),reconstructed_is_volume=bool(cad.is_volume))
    return cad,checks

def occupancy(m,lo,pitch,dims):
    """VTK triangle stencil at shared voxel centers. Used only for evaluation."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.ascontiguousarray(m.vertices),deep=True))
    cells=np.column_stack([np.full(len(m.faces),3,dtype=np.int64),m.faces]).ravel()
    ca=vtk.vtkCellArray();ca.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(cells,deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(ca)
    ext=(0,int(dims[0]-1),0,int(dims[1]-1),0,int(dims[2]-1))
    stencil=vtk.vtkPolyDataToImageStencil();stencil.SetInputData(poly)
    stencil.SetOutputOrigin(*(lo+pitch/2));stencil.SetOutputSpacing(pitch,pitch,pitch);stencil.SetOutputWholeExtent(*ext)
    stencil.SetTolerance(0.0);stencil.Update()
    convert=vtk.vtkImageStencilToImage();convert.SetInputConnection(stencil.GetOutputPort())
    convert.SetInsideValue(1);convert.SetOutsideValue(0);convert.SetOutputScalarTypeToUnsignedChar();convert.Update()
    return vtk_to_numpy(convert.GetOutput().GetPointData().GetScalars()).astype(bool)

def iou(a,b,res):
    lo=np.minimum(a.bounds[0],b.bounds[0]);hi=np.maximum(a.bounds[1],b.bounds[1])
    pitch=float(max(hi-lo)/res);dims=np.maximum(1,np.ceil((hi-lo)/pitch).astype(int))
    x=occupancy(a,lo,pitch,dims);y=occupancy(b,lo,pitch,dims)
    union=int(np.count_nonzero(x|y));inter=int(np.count_nonzero(x&y))
    if not union:raise ValueError('IOU_EMPTY_GRID')
    return float(inter/union),dict(origin=(lo+pitch/2).tolist(),pitch=pitch,dimensions=dims.tolist(),intersection=inter,union=union,
        source_occupied=int(x.sum()),cad_occupied=int(y.sum()))

def metrics(a,b,high=False):
    sp,si=trimesh.sample.sample_surface(a,32768,seed=2026)
    cp,ci=trimesh.sample.sample_surface(b,32768,seed=2027)
    d1,j1=cKDTree(cp).query(sp);d2,j2=cKDTree(sp).query(cp)
    diag=float(np.linalg.norm(a.extents));cd=float((d1.mean()+d2.mean())/2);hd=float(max(d1.max(),d2.max()))
    normal=float((np.abs((a.face_normals[si]*b.face_normals[ci[j1]]).sum(1)).mean()+np.abs((b.face_normals[ci]*a.face_normals[si[j2]]).sum(1)).mean())/2)
    i64,g64=iou(a,b,64);i128,g128=iou(a,b,128)
    i256,g256=iou(a,b,256) if high or i128>=.9 else (None,None)
    return dict(iou64=i64,iou128=i128,iou256=i256,cd=cd,ncd=cd/diag,hausdorff=hd,nhd=hd/diag,normal_consistency=normal,
        bbox_error=float(np.max(np.linalg.norm(a.bounds-b.bounds,axis=1))/diag),
        centroid_error=float(np.linalg.norm(a.centroid-b.centroid)/diag),
        surface_area_error=float(abs(a.area-b.area)/a.area),volume_error=float(abs(a.volume-b.volume)/abs(a.volume)),
        IOU_VALID=bool(a.is_watertight and a.is_volume and b.is_watertight and b.is_volume),
        grid64=g64,grid128=g128,grid256=g256,surface_sample_count=32768,
        distance_protocol='bidirectional area-uniform sampled NN, mean of directed means; Hausdorff is a sampled estimate; normalized by source bbox diagonal',
        coordinate_protocol='original coordinates; shared union bbox; cubic voxels at centers; no post-hoc alignment')

def scaled(p,factor):
    q=copy.deepcopy(p)
    keys=['radius','x_radius','y_radius','width','height','distance','z']
    for o in q['operations']:
        for k in keys:
            if k in o:o[k]*=factor
        for k in ['center','points']:
            if k in o:o[k]=(np.asarray(o[k])*factor).tolist()
        if 'profile_validation' in o:
            o['profile_validation']['profile_area']*=factor**2
    return q

def overlay(src,cad,out,label):
    from PIL import Image, ImageDraw
    lo=np.minimum(src.bounds[0],cad.bounds[0]);hi=np.maximum(src.bounds[1],cad.bounds[1]);c=(lo+hi)/2;r=max(hi-lo)*.58
    image=Image.new('RGB',(1200,430),'white');draw=ImageDraw.Draw(image)
    # Orthographic x/z projection with a fixed y slant; all panels share bounds/camera.
    def project(v,x0):
        v=np.asarray(v);u=(v[:,0]-c[0])*.86+(v[:,1]-c[1])*.34;w=(v[:,2]-c[2])*.96-(v[:,1]-c[1])*.18
        return [(int(x0+190+145*q/r),int(220-145*t/r)) for q,t in zip(u,w)]
    def panel(mesh,x0,color,alpha):
        tri=mesh.triangles;stride=max(1,len(tri)//1800)
        fill=color if alpha==255 else color+(alpha,)
        for t in tri[::stride]:
            pts=project(t,x0)
            if alpha==255:draw.polygon(pts,fill=color)
            else:
                layer=Image.new('RGBA',(1200,430),(0,0,0,0));ld=ImageDraw.Draw(layer);ld.polygon(pts,fill=fill);image.paste(layer,(0,0),layer)
    for idx,title in enumerate(['SOURCE','CAD','OVERLAY']):
        x0=idx*400
        if idx==0:panel(src,x0,(224,152,54),255)
        elif idx==1:panel(cad,x0,(51,137,186),255)
        else:panel(src,x0,(224,152,54),75);panel(cad,x0,(51,137,186),105)
        draw.text((x0+165,22),title,fill='black')
    draw.text((20,395),label,fill='black');image.save(out)

def process(row):
    relative=Path(row['path']);case=relative.parts[0];part=relative.parent.name+'__'+relative.stem
    od=OUT/'cases'/case/part;od.mkdir(parents=True,exist_ok=True)
    if (od/'metrics.json').exists() and json.loads((od/'metrics.json').read_text()).get('pipeline_version')==VERSION:
        return json.loads((od/'metrics.json').read_text())
    src=load(ROOT/relative);diag=float(np.linalg.norm(src.extents))
    if relative.suffix.lower()=='.stl':shutil.copy2(ROOT/relative,od/'source.stl')
    else:src.export(od/'source.stl')
    source_sha=sha(ROOT/relative)
    analysis,ex,rv=geometry(src);dump(od/'geometry_analysis.json',analysis)
    opts=programs(src,analysis,ex,rv);cr=[];success=[]
    for i,(name,p) in enumerate(opts):
        folder=od/f'candidate_{i}';r=dict(candidate=i,name=name)
        try:
            cad,check=execute(p,folder,diag);mm=metrics(src,cad);co=complexity(p)
            faceted=check['cad_brep_face_count']>=200 or (len(src.faces)>100 and check['cad_brep_face_count']>=.35*len(src.faces))
            score=1-mm['iou128']+.005*co['feature_count']/48+.005*co['parameter_count']/200
            r.update(execute='PASS',score=score,iou128=mm['iou128'],ncd=mm['ncd'],faceted=faceted,**co)
            dump(folder/'metrics.json',mm);dump(folder/'validation.json',check)
            if not faceted and mm['IOU_VALID']:success.append((r,p,cad,check,mm))
        except Exception as e:
            r.update(execute='FAIL',error=str(e));dump(folder/'failure.json',dict(error=str(e),traceback=traceback.format_exc()))
        cr.append(r);print(case,part,name,r.get('iou128'),r.get('error',''),flush=True)
    csvwrite(od/'candidates.csv',cr)
    if not success:raise RuntimeError('CAD_EXECUTION_ERROR: all candidates invalid')
    maximum=max(t[0]['iou128'] for t in success)
    tied=[t for t in success if maximum-t[0]['iou128']<=.002]
    best=min(tied,key=lambda t:(t[0]['feature_count'],t[0]['parameter_count'],t[0]['score']))
    r,p,cad,check,mm=best
    # Two bounded numerical size refinements within the chosen feature family.
    history=[dict(factor=1.,iou128=mm['iou128'])]
    base=copy.deepcopy(p)
    for factor in [.99,1.01]:
        refined=scaled(base,factor)
        try:
            cm,ch=execute(refined,od/'refinement'/str(factor),diag);mt=metrics(src,cm)
            history.append(dict(factor=factor,iou128=mt['iou128']))
            if mt['IOU_VALID'] and mt['iou128']>mm['iou128']+.0001:p,cad,check,mm=refined,cm,ch,mt
        except Exception as e:history.append(dict(factor=factor,error=str(e)))
    dump(od/'refinement.json',dict(method='local coordinate search, uniform dimensional parameter scale about fixed fitted frame; no evaluation-time alignment',evaluations=history))
    cad,check=execute(p,od,diag);mm=metrics(src,cad)
    # Rebuild in an empty folder containing cad.py only (no source or JSON).
    with tempfile.TemporaryDirectory(prefix='source_free_',dir=OUT/'audit') as tmp:
        td=Path(tmp);shutil.copy2(od/'cad.py',td/'cad.py')
        rr=subprocess.run([sys.executable,'cad.py'],cwd=td,env=ENV,capture_output=True,text=True,timeout=180)
        regenerated=rr.returncode==0 and (td/'reconstructed.step').exists() and (td/'reconstructed.stl').exists()
        if regenerated:
            repeat=load(td/'reconstructed.stl')
            regenerated=bool(np.allclose(repeat.bounds,cad.bounds,rtol=1e-8,atol=diag*1e-8) and abs(repeat.volume-cad.volume)<diag**3*1e-8)
        check['SOURCE_FREE_REEXECUTION']='PASS' if regenerated else 'FAIL'
        check['source_free_log']=rr.stdout+'\n'+rr.stderr
    used=mesh_used((od/'cad.py').read_text());faceted=check['cad_brep_face_count']>=200 or (len(src.faces)>100 and check['cad_brep_face_count']>=.35*len(src.faces))
    structural=regenerated and not used and not faceted and mm['IOU_VALID'] and check['BREP_VALID']=='YES' and check['SOLID_COUNT']>=1
    quality='A_HIGH_CONFIDENCE' if mm['iou128']>=.95 else 'B_USABLE' if mm['iou128']>=.9 else 'C_NEAR_MISS' if mm['iou128']>=.8 else 'D_REJECT'
    if not structural:quality='D_REJECT'
    valid=structural and mm['iou128']>=.9 and mm['ncd']<=.01 and mm['bbox_error']<=.03 and mm['centroid_error']<=.02
    failures=[]
    if used:failures.append('REJECTED_MESH_CONVERSION')
    if faceted:failures.append('FACETED_BREP_DETECTED')
    if not regenerated:failures.append('CAD_EXECUTION_ERROR')
    if mm['iou128']<.9:
        failures.append('PRIMITIVE_UNDERFIT' if r['name']=='primitive' else 'PROFILE_ERROR' if r['name']=='profile' else 'REVOLVE_ERROR' if r['name']=='revolve' else 'NO_SIMPLE_CAD_EXPLANATION')
        failures.append('IOU_TOO_LOW')
    if mm['ncd']>.01:failures.append('SURFACE_DISTANCE_EXCEEDED')
    if mm['bbox_error']>.03:failures.append('SCALE_ERROR')
    if mm['centroid_error']>.02:failures.append('PLACEMENT_ERROR')
    if not mm['IOU_VALID']:failures.append('IOU_INVALID')
    check.update(MESH_IMPORT_USED='YES' if used else 'NO',FACETED_BREP='YES' if faceted else 'NO',
        IOU_VALID='YES' if mm['IOU_VALID'] else 'NO',VALID_TRAINING_PAIR='YES' if valid else 'NO')
    result=dict(pipeline_version=VERSION,case_id=case,part_id=part,source_path=str(relative),source_sha256=source_sha,
        geometry_family=p['geometry_family'],feature_sequence=' -> '.join(o['type'] for o in p['operations'] if o['type']!='RESULT'),
        cad_program_path=str((od/'cad.py').relative_to(OUT)),program_json_path=str((od/'program.json').relative_to(OUT)),
        step_path=str((od/'reconstructed.step').relative_to(OUT)),reconstructed_mesh_path=str((od/'reconstructed.stl').relative_to(OUT)),
        cad_program_exec='PASS',brep_valid=True,step_reload=True,mesh_import_used=used,faceted_brep=faceted,
        source_free_reexecution=regenerated,source_triangle_count=len(src.faces),cad_brep_face_count=check['cad_brep_face_count'],
        quality_level=quality,valid_training_pair=bool(valid),failure_reason=';'.join(failures),selected_candidate=r['name'],**complexity(p),**mm)
    dump(od/'parameters.json',dict(workplane=p['workplane'],operations=p['operations']))
    dump(od/'transform.json',dict(normalization_used=False,fitting_frame=p['workplane'],evaluation_alignment='NONE'))
    dump(od/'validation.json',check);dump(od/'metrics.json',result)
    (od/'report.md').write_text(f"# {case}/{part}\n\nFamily: {p['geometry_family']}\n\n{result['feature_sequence']}\n\nIoU128={mm['iou128']:.6f}; NCD={mm['ncd']:.6f}; {quality}\n\nVALID_TRAINING_PAIR={valid}\n\nFailures: {result['failure_reason'] or 'NONE'}\n\nRebuild with `python cad.py` (CadQuery 2.6.1). Source-free rebuild: {regenerated}.\n\nSOURCE is a part mesh, not ground-truth CAD.\n",encoding='utf-8')
    overlay(src,cad,od/'overlay.png',f"{case}/{part} | IoU128 {mm['iou128']:.4f} | NCD {mm['ncd']:.4f} | {quality}")
    return result

def selfcheck():
    a=trimesh.creation.box(extents=[1.,1.,1.]);b=a.copy();b.apply_translation([.5,0,0])
    exact,g=iou(a,a,64);partial,_=iou(a,b,128)
    assert exact==1. and abs(partial-1/3)<.015,(exact,partial)
    ring=cq.Workplane('XY').circle(1).circle(.4).extrude(.7)
    v,f=ring.val().tessellate(.0002);m=trimesh.Trimesh(vertices=[x.toTuple() for x in v],faces=f,process=True)
    solid=cq.Workplane('XY').circle(1).extrude(.7)
    v,f=solid.val().tessellate(.0002);s=trimesh.Trimesh(vertices=[x.toTuple() for x in v],faces=f,process=True)
    ii,_=iou(m,s,128);assert abs(ii-.84)<.015,ii
    dump(OUT/'audit/protocol_selfcheck.json',dict(identity_iou=exact,half_shift_cube_iou=partial,expected_half_shift=1/3,annulus_vs_disk=ii,expected_annulus=.84,status='PASS'))

def audit():
    cache=OUT/'audit/all_parts_scan.json'
    if not cache.exists():
        rows0=[]
        for p in sorted(ROOT.rglob('*')):
            if not p.is_file() or p.suffix.lower() not in ('.obj','.stl') or p.parent.name not in ('p3_parts','xpart_parts'): continue
            try:
                m=load(p);rows0.append(dict(path=str(p.relative_to(ROOT)),watertight=bool(m.is_watertight),volume=bool(m.is_volume),
                    vertices=len(m.vertices),faces=len(m.faces),extents=m.extents.tolist(),centroid=m.centroid.tolist(),
                    bbox_diagonal=float(np.linalg.norm(m.extents)),surface_area=float(m.area),volume_value=float(m.volume) if m.is_volume else None))
            except Exception as ex: rows0.append(dict(path=str(p.relative_to(ROOT)),watertight=False,volume=False,error=str(ex)))
        dump(cache,rows0)
        good=[r for r in rows0 if r.get('watertight') and r.get('volume')]; buckets={'rod':[],'round':[],'compact':[],'complex':[]}
        for r in good:
            e=np.array(r['extents']);ratio=e.max()/max(e.min(),1e-9);s=np.sort(e)
            key='rod' if ratio>5 else 'round' if abs(s[-1]-s[-2])/max(s[-1],1e-9)<.3 else 'compact' if ratio<2.4 else 'complex';buckets[key].append(r)
        sel=[]
        for key,n in [('rod',4),('round',7),('compact',5),('complex',4)]:sel.extend(sorted(buckets[key],key=lambda x:x['path'])[:n])
        dump(OUT/'audit/pilot_selection.json',sel[:20])
    rows=json.loads(cache.read_text())
    sourcefiles=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in ['.stl','.obj','.ply']]
    included={r['path'] for r in rows}
    directory_inventory=Counter('/'.join(p.relative_to(ROOT).parts[1:-1]) for p in sourcefiles)
    dump(OUT/'audit/mesh_directory_inventory.json',dict(counts=dict(directory_inventory),excluded_files=[str(p.relative_to(ROOT)) for p in sourcefiles if str(p.relative_to(ROOT)) not in included],
        scope='component meshes in observed p3_parts and xpart_parts directories; assembly/context meshes excluded'))
    for r in rows:
        p=ROOT/r['path'];r['sha256']=sha(p);r['bytes']=p.stat().st_size;r['case_id']=Path(r['path']).parts[0]
        r['source_group']=Path(r['path']).parent.name
    csvwrite(OUT/'audit/all_parts.csv',rows)
    cases=[]
    for case in sorted({r['case_id'] for r in rows}):
        rr=[r for r in rows if r['case_id']==case]
        cases.append(dict(case_id=case,part_n=len(rr),watertight_n=sum(r['watertight'] for r in rr),volume_n=sum(r['volume'] for r in rr)))
    csvwrite(OUT/'audit/all_cases.csv',cases)
    selection=json.loads((OUT/'audit/pilot_selection.json').read_text())
    assert len(selection)==min(20,len(rows))
    dump(OUT/'audit/selection_policy.json',dict(method='locked original pre-evaluation selection by aspect ratio buckets, path order within buckets',
        selection_changed=False,limitation='Proxy shape buckets; semantic coverage is reported after geometry analysis, not guaranteed by labels.',
        source_groups=dict(Counter(Path(r['path']).parent.name for r in selection))))
    return rows,selection,cases

def summarize(rows,selection,cases,results):
    fields=['case_id','part_id','source_path','geometry_family','feature_sequence','cad_program_path','program_json_path','step_path',
        'reconstructed_mesh_path','cad_program_exec','brep_valid','step_reload','mesh_import_used','faceted_brep','feature_count','parameter_count',
        'sketch_entity_count','boolean_count','source_triangle_count','cad_brep_face_count','iou64','iou128','iou256','cd','ncd','hausdorff','nhd',
        'normal_consistency','bbox_error','centroid_error','surface_area_error','volume_error','quality_level','valid_training_pair','failure_reason','source_free_reexecution']
    csvwrite(OUT/'manifests/all_results.csv',results,fields)
    for name,prefix in [('high_confidence','A_'),('usable','B_'),('near_miss','C_'),('rejected','D_')]:
        csvwrite(OUT/f'manifests/{name}.csv',[r for r in results if r['quality_level'].startswith(prefix)],fields)
    csvwrite(OUT/'manifests/valid_training_pairs.csv',[r for r in results if r.get('valid_training_pair')],fields)
    q=Counter(r['quality_level'] for r in results)
    scores=[r['iou128'] for r in results if r.get('iou128') is not None]
    ncd=[r['ncd'] for r in results if r.get('ncd') is not None]
    failures=Counter(r['failure_reason'].split(';')[0] for r in results if r['failure_reason'])
    report=dict(INPUT_ROOT=str(ROOT),OUTPUT_ROOT=str(OUT),CASE_N=len(cases),TOTAL_PART_N=len(rows),WATERTIGHT_PART_N=sum(r['watertight'] for r in rows),
        PILOT_N=len(selection),CAD_PROGRAM_EXEC_PASS_N=sum(r['cad_program_exec']=='PASS' for r in results),
        BREP_VALID_N=sum(r['brep_valid'] for r in results),STEP_RELOAD_PASS_N=sum(r['step_reload'] for r in results),
        A_HIGH_CONFIDENCE_N=q['A_HIGH_CONFIDENCE'],B_USABLE_N=q['B_USABLE'],C_NEAR_MISS_N=q['C_NEAR_MISS'],D_REJECT_N=q['D_REJECT'],
        IOU128_MEAN=float(np.mean(scores)) if scores else None,IOU128_MEDIAN=float(np.median(scores)) if scores else None,
        IOU128_MIN=min(scores) if scores else None,IOU128_MAX=max(scores) if scores else None,
        NCD_MEAN=float(np.mean(ncd)) if ncd else None,NCD_MEDIAN=float(np.median(ncd)) if ncd else None,
        MESH_IMPORT_N=sum(r['mesh_import_used'] for r in results),FACETED_BREP_N=sum(r['faceted_brep'] for r in results),
        PRIMARY_FAILURE_CAUSE=failures.most_common(1)[0][0] if failures else 'NONE',
        VALID_TRAINING_PAIR_N=sum(r.get('valid_training_pair',False) for r in results))
    passed=q['A_HIGH_CONFIDENCE']+q['B_USABLE']>=12 and report['MESH_IMPORT_N']==0 and report['FACETED_BREP_N']==0 and len(results)==20
    report['CURRENT_GATE']='P3_XPART_EXECUTABLE_CAD_PILOT_PASS' if passed else 'P3_XPART_CAD_PIPELINE_REPAIR_REQUIRED'
    report['NEXT_ALLOWED_STAGE']='FULL_XPART_CONVERSION' if passed else 'PIPELINE_REPAIR'
    dump(OUT/'audit/pilot_summary.json',report)
    dump(OUT/'audit/coverage.json',dict(families=dict(Counter(r.get('geometry_family','UNKNOWN') for r in results)),
        limitations=['Pilot shape diversity was chosen before evaluation; semantic categories may remain uncovered.',
        'Edge fillet/chamfer recovery is not implemented as a general recognizer; uncovered categories require pipeline repair.']))
    ordered=sorted([r for r in results if r.get('iou128') is not None],key=lambda r:-r['iou128'])
    groups={'best5':ordered[:5],'near_miss5':[r for r in ordered if r['quality_level']=='C_NEAR_MISS'][:5],
        'failures5':list(reversed([r for r in ordered if r['quality_level']=='D_REJECT']))[:5]}
    from PIL import Image,ImageDraw
    for name,rr in groups.items():
        ims=[Image.open(OUT/Path(r['cad_program_path']).parent/'overlay.png').convert('RGB') for r in rr]
        width=1260;height=max(90,sum(im.height for im in ims)+65)
        canvas=Image.new('RGB',(width,height),'white');dr=ImageDraw.Draw(canvas)
        dr.text((20,15),f'{name}: {len(rr)} available / 5 requested. Orange: source; blue: CAD.',fill='black')
        y=65
        for im in ims:canvas.paste(im,(0,y));y+=im.height
        canvas.save(OUT/f'visualizations/{name}.png')
    text='```text\n'+'\n'.join(f'{k}={v}' for k,v in report.items())+'\n```\n\n'
    text+='| case_id | part_id | family | feature sequence | feature_count | IoU128 | NCD | quality |\n|---|---|---|---|---:|---:|---:|---|\n'
    for r in results:
        text+='| '+' | '.join(str(r.get(k,'')) for k in ['case_id','part_id','geometry_family','feature_sequence','feature_count','iou128','ncd','quality_level'])+' |\n'
    text+='\nInput audit: 1008 P3 OBJ components and 45 X-Part STL components. 64 are watertight positive volumes. Counts refer to parts, not all assembly/context meshes.\n\n'
    text+='IoU: VTK solid stencil at identical union-bbox voxel centers; source and CAD remain in original coordinates. IoU256 is computed for IoU128 >= 0.90. Chamfer/Hausdorff use 32768 surface samples each; Hausdorff is an estimate.\n\n'
    text+='The pilot supports bounded analytic sketches, extrusion, revolve and CAD booleans. General freeform, blind-pocket and fillet/chamfer recognition remain limited; source meshes are not GT CAD. The gate is a pilot result, not proof of full task coverage.\n\n'
    text+='No full conversion was launched. Rebuild: Python 3.10 with CadQuery 2.6.1, `python cad.py`; no source file is required.\n\n'
    for name,rr in groups.items():text+=f'{name}: {len(rr)}/5 available.\n\n![{name}](visualizations/{name}.png)\n\n'
    (OUT/'FINAL_REPORT.md').write_text(text,encoding='utf-8')
    return report

def main():
    for d in ['audit','cases','manifests','visualizations']:(OUT/d).mkdir(parents=True,exist_ok=True)
    selfcheck();rows,selection,cases=audit();results=[]
    print('AUDIT',len(cases),len(rows),sum(r['watertight'] for r in rows),'PILOT',len(selection),flush=True)
    for n,r in enumerate(selection):
        print('START',n+1,r['path'],flush=True)
        try:result=process(r)
        except Exception as e:
            path=Path(r['path']);part=path.parent.name+'__'+path.stem
            result=dict(case_id=path.parts[0],part_id=part,source_path=r['path'],cad_program_exec='FAIL',brep_valid=False,
                step_reload=False,mesh_import_used=False,faceted_brep=False,quality_level='D_REJECT',valid_training_pair=False,
                failure_reason='CAD_EXECUTION_ERROR',error=str(e))
            dump(OUT/'cases'/path.parts[0]/part/'failure.json',dict(error=str(e),traceback=traceback.format_exc()))
            print(traceback.format_exc(),flush=True)
        results.append(result);dump(OUT/'audit/progress.json',dict(done=len(results),total=len(selection),latest=result))
        print('DONE',n+1,result['quality_level'],result.get('iou128'),flush=True)
    changed=[r['path'] for r in rows if sha(ROOT/r['path'])!=r['sha256']]
    dump(OUT/'audit/source_integrity.json',dict(checked=len(rows),changed=changed,status='PASS' if not changed else 'FAIL'))
    if changed:raise RuntimeError('Source integrity mismatch')
    report=summarize(rows,selection,cases,results);print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
