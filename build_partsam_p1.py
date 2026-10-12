"""Build isolated operation-aware P1 pseudo-supervision from audited PartSAM fits.

No training, no source mutation, no fallback from sharp-only to all-edge tokens.
"""
from pathlib import Path
import os,sys,json,csv,hashlib,ast,traceback,argparse,subprocess,concurrent.futures,collections
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'partsam_p1_training_v1'
FIT=ROOT/'partsam_cad_iou_top1000_v1'
SOURCE=ROOT/'partsam/PartObjaverse-Tiny_instance_stl'
VERSION='direct_stl_fit_v2'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
import numpy as np

def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else str(x)),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lit(x):
    if isinstance(x,np.ndarray):x=x.tolist()
    if isinstance(x,(list,tuple)):return '['+', '.join(lit(v) for v in x)+']'
    return repr(round(float(x),8))

def make_dsl(spec,scale,translation):
    kind=spec['kind'];B=np.asarray(spec['basis']);center=np.asarray(spec['center']);axis=B[:,2];xd=B[:,0]
    lines=[]
    def emit(call):
        name=f'body_{len(lines)}';lines.append(f'{name} = {call}');return name
    def extrude(points,origin,height):
        return emit(f'ExtrudePolygon(points={lit(np.asarray(points)*scale)}, height={lit(height*scale)}, axis={lit(axis)}, origin={lit(origin*scale+translation)}, x_axis={lit(xd)})')
    if kind=='extrusion':
        origin=center+spec['zmin']*axis;height=spec['zmax']-spec['zmin'];result=None
        for profile in spec['profiles']:
            body=extrude(profile['outer'],origin,height)
            for hole in profile.get('holes',[]):
                cutter=extrude(hole,origin,height);body=emit(f'Cut({body}, {cutter})')
            result=body if result is None else emit(f'Union({result}, {body})')
    elif kind=='box':
        mn=np.asarray(spec['mins']);mx=np.asarray(spec['maxs']);d=mx-mn
        # Existing fitted box origin is a corner; P1 Box uses a centered rectangle.
        origin=center+B@np.array([(mn[0]+mx[0])/2,(mn[1]+mx[1])/2,mn[2]])
        result=emit(f'Box(width={lit(d[0]*scale)}, depth={lit(d[1]*scale)}, height={lit(d[2]*scale)}, axis={lit(axis)}, origin={lit(origin*scale+translation)}, x_axis={lit(xd)})')
    elif kind=='cylinder':
        origin=center+spec['zmin']*axis
        result=emit(f'Cylinder(radius={lit(spec["radius"]*scale)}, height={lit((spec["zmax"]-spec["zmin"])*scale)}, axis={lit(axis)}, origin={lit(origin*scale+translation)})')
    else:raise ValueError(f'unsupported_existing_p1_operation:{kind}')
    return '\n'.join(lines+[f'result = {result}'])+'\n'

def sample(mesh,n,seed):
    import trimesh
    p,ids=trimesh.sample.sample_surface(mesh,n,seed=seed)
    return np.concatenate([p,mesh.face_normals[ids]],axis=1).astype(np.float32)

def distances(mesh,points):
    import trimesh
    return np.concatenate([trimesh.proximity.closest_point(mesh,part)[1] for part in np.array_split(points,max(1,int(np.ceil(len(points)/256))))])

def fit_direct(mesh,dest):
    import importlib.util,trimesh,cadquery as cq
    from canonical_cad_data_v4.converters.cad_dsl import parse_dsl,_build_shape
    sp=importlib.util.spec_from_file_location('readonly_fit_helpers',FIT/'scripts/pipeline.py')
    helper=importlib.util.module_from_spec(sp);sys.modules[sp.name]=helper;sp.loader.exec_module(helper)
    axes=helper.candidate_axes(mesh);specs=[];errors=[]
    for axis in axes[:3]:
        try:
            spec=helper.projected_profile(mesh,axis,max_entities=80)
            if spec['sketch_entity_count']<=100:specs.append(spec)
        except Exception as e:errors.append(str(e))
    for kind in ('box','cylinder'):
        for axis in axes[:3]:
            try:specs.append(helper.primitive_profile(mesh,axis,kind))
            except Exception as e:errors.append(str(e))
    a=sample(mesh,512,1728);best=None
    for spec in specs:
        try:
            dsl=make_dsl(spec,1.,np.zeros(3));program=parse_dsl(dsl)
            # Parser resolves named references into operation trees; build result exactly once.
            obj=_build_shape(program.assignments['result'],{});shape=obj.val() if hasattr(obj,'val') else obj
            if not shape.isValid() or not shape.Solids():continue
            vs,fs=shape.tessellate(.002,.08);cad=trimesh.Trimesh(np.array([v.toTuple() for v in vs]),np.array(fs),process=True)
            da=distances(cad,a[:,:3])/6;db=distances(mesh,sample(cad,512,1727)[:,:3])/6
            score=max(da.mean(),db.mean())+max(np.quantile(da,.95),np.quantile(db,.95))
            if best is None or score<best[0]:best=(score,spec,dsl,shape,cad)
        except Exception as e:errors.append(type(e).__name__+':'+str(e)[:120])
    dump(dest/'fit_search.json',{'attempted':len(specs),'errors':errors,'best_score':best[0] if best else None})
    if best is None:raise ValueError('no_supported_valid_operation_fit')
    _,spec,dsl,shape,cad=best
    if best[0]>.03:raise ValueError('coarse_geometry_gate')
    cq.exporters.export(shape,str(dest/'model.step'));shape.exportBrep(str(dest/'model.brep'));cad.export(dest/'model.stl')
    # Reload STEP before curves and final metrics.
    reloaded=cq.importers.importStep(str(dest/'model.step')).val()
    if not reloaded.isValid() or len(reloaded.Faces())!=len(shape.Faces()):raise ValueError('step_roundtrip')
    return spec,dsl,reloaded,cad

def process(row):
    import trimesh,cadquery as cq
    from scipy.spatial import cKDTree
    from canonical_cad_data_v4.converters.cad_dsl import execute_dsl
    case=row['case_id'];cad_id='partsam__'+case;dest=OUT/'PartSAM/geometry_pack_v1'/case;dest.mkdir(parents=True,exist_ok=True)
    src=SOURCE/row['object_id']/f"part_{int(row['part_id']):03d}.stl"
    rec={'cad_id':cad_id,'sample_id':case,'dataset':'partsam','object_id':row['object_id'],
         'source_path':str(src),'fit_directory':str(FIT/'candidates'/case),'pseudo_supervision':True,
         'original_design_history_recovered':False,'geometry_class':'pending','status':'processing','build_version':VERSION}
    try:
        src_hash=sha(src);rec['source_sha256']=src_hash
        mesh=trimesh.load(src,force='mesh',process=True);mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
        diag=float(np.linalg.norm(mesh.extents));s=6/diag;t=-s*mesh.bounds[0]
        nz={'source_bbox_min':mesh.bounds[0].tolist(),'source_bbox_max':mesh.bounds[1].tolist(),'source_diagonal':diag,
            'target_diagonal':6.,'scale':s,'translation':t.tolist(),'source':'original_mesh_bbox; identical transform for DSL, surface and curves'}
        dump(dest/'coordinate_transform.json',nz)
        original_normalized=mesh.copy();original_normalized.vertices=original_normalized.vertices*s+t
        spec,dsl,shape,cad=fit_direct(original_normalized,dest)
        rec['geometry_class']=spec['kind'];rec['fit_directory']=str(dest)
        dump(dest/'fitted_parameters_canonical.json',spec);(dest/'program_canonical.dsl').write_text(dsl)
        # Exact point-to-triangle distances, not point-to-point sample spacing.
        a=sample(original_normalized,4096,1729);b=sample(cad,4096,1730)
        da=distances(cad,a[:,:3])/6;db=distances(original_normalized,b[:,:3])/6
        metrics={'mesh_to_cad_mean':float(da.mean()),'cad_to_mesh_mean':float(db.mean()),
                 'mesh_to_cad_p95':float(np.quantile(da,.95)),'cad_to_mesh_p95':float(np.quantile(db,.95)),
                 'sampled_max':float(max(da.max(),db.max())),
                 'metric':'4096 deterministic area-weighted samples per direction; exact point-to-triangle distance / source bbox diagonal',
                 'thresholds':{'mean_each':.003,'p95_each':.01,'sampled_max':.03},
                 'source_watertight':bool(mesh.is_watertight),'cad_watertight':bool(cad.is_watertight)}
        rec['geometry_metrics']=metrics;dump(dest/'geometry_validation.json',metrics)
        if max(da.mean(),db.mean())>.003 or max(np.quantile(da,.95),np.quantile(db,.95))>.01 or max(da.max(),db.max())>.03:
            raise ValueError('mesh_cad_surface_distance_gate')
        surface=sample(original_normalized,8192,20260919)
        if not np.isfinite(surface).all() or not np.allclose(np.linalg.norm(surface[:,3:],axis=1),1,atol=1e-5):raise ValueError('invalid_surface')
        np.save(dest/'surface_points.npy',surface);np.save(dest/'features_canonical.npy',surface)
        export_curves(shape,dest,rec)
        rec.update(status='geometry_ready',target_path=str(dest/'program_canonical.dsl'),step_path=str(dest/'model.step'),
                   surface_path=str(dest/'surface_points.npy'),curve_path=str(dest/'curve_samples.npz'),
                   source_unchanged=sha(src)==src_hash,normalization=nz,surface_input_provenance='original STL mesh; reconstructed CAD supplies pseudo target and curves')
        assert rec['source_unchanged']
    except Exception as exc:
        rec.update(status='excluded',reason=str(exc),traceback=traceback.format_exc()[-2000:])
    dump(dest/'record.json',rec)
    return rec

def export_curves(shape,dest,rec):
    from curve_token_v1.extract_brep_curves import extract_curves_from_shape
    from curve_token_v1.canonicalize_curves import Normalization,canonicalize_curves
    from curve_token_v1.occ_curve_v1 import make_adaptor
    from curve_token_v1.extract_topology import extract_topology,topology_arrays
    from curve_token_v1.sample_curves import build_sample_arrays
    from geometry_pack_v1.occ import extract_brep_edges
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopoDS import TopoDS
    raw=extract_curves_from_shape(shape.wrapped,cad_id=rec['cad_id'])
    # STEP is already canonical. Never apply source normalization twice.
    nz=Normalization(raw['source_bbox_min'],raw['source_bbox_max'],raw['source_diagonal'],6.,1.,[0.,0.,0.],'identity:STEP already canonical')
    data=canonicalize_curves(raw,nz);curves=data['curves']
    emap=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape.wrapped,TopAbs_EDGE,emap)
    adaptors=[make_adaptor(TopoDS.Edge_s(emap.FindKey(r['edge_id']+1))) for r in curves]
    topo=extract_topology(shape.wrapped,curves);arrays=build_sample_arrays(adaptors,curves,32,nz);arrays.update(topology_arrays(topo,curves))
    brep=extract_brep_edges(shape.wrapped,raw['source_diagonal'])
    for e in brep['edges']:e['is_sharp']=bool(e['dihedral_deg']>30.)
    dump(dest/'brep_edges.json',brep)
    sharp={int(e['edge_index']):bool(e.get('is_sharp',False)) for e in brep['edges']}
    kept=[i for i,r in enumerate(curves) if sharp.get(r['edge_id'],False) and r['curve_type'] in ('LINE','CIRCLE','ELLIPSE','BSPLINE')]
    if not kept:raise ValueError('zero_sharp_curves')
    lengths=np.linalg.norm(np.diff(arrays['curve_xyz_normalized'].astype(np.float64),axis=1),axis=2).sum(axis=1)
    kept=sorted(kept,key=lambda i:-lengths[i])[:128]
    if not arrays['curve_mask'][kept].all():raise ValueError('invalid_curve_samples')
    if not all(r['extraction']['parameter_extraction_ok'] and r['extraction']['geometry_reconstruction_ok'] for r in curves):raise ValueError('curve_parameter_validation')
    np.savez_compressed(dest/'curve_samples.npz',**arrays)
    np.save(dest/'selected_curve_indices.npy',np.array(kept,dtype=np.int64))
    np.save(dest/'curve_points_sharp_xyztangent.npy',np.concatenate([np.concatenate([arrays['curve_xyz_normalized'][i],arrays['curve_tangent'][i]],axis=1) for i in kept]).astype(np.float32))
    dump(dest/'curves.json',data);dump(dest/'topology.json',topo)
    rec.update(curve_count=len(curves),selected_sharp_curve_count=len(kept),curve_type_counts=dict(collections.Counter(r['curve_type'] for r in curves)),
               c2_selection='sharp-only; descending polyline length; cap128; no fallback')

def worker_launch(row):
    case=row['case_id'];log=OUT/'logs'/f'{case}.log';log.parent.mkdir(exist_ok=True)
    with log.open('w') as f:
        try:
            p=subprocess.run([sys.executable,__file__,'--case',case],stdout=f,stderr=subprocess.STDOUT,timeout=180)
            path=OUT/'PartSAM/geometry_pack_v1'/case/'record.json'
            if path.exists():return json.loads(path.read_text())
            return {'sample_id':case,'status':'excluded','reason':f'worker_exit:{p.returncode}'}
        except subprocess.TimeoutExpired:return {'sample_id':case,'status':'excluded','reason':'worker_timeout_180s'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case');ap.add_argument('--limit',type=int);ap.add_argument('--workers',type=int,default=6);args=ap.parse_args()
    rows=[{'case_id':p.parent.name+'_'+p.stem,'object_id':p.parent.name,'part_id':int(p.stem.split('_')[-1]),'source_path':str(p)} for p in sorted(SOURCE.glob('*/part_*.stl'))]
    inventory=json.loads((ROOT/'partsam/PartObjaverse-Tiny_instance_cad/input_inventory.json').read_text())
    complexity={r['relative']:r['faces'] for r in inventory}
    rows.sort(key=lambda r:(complexity.get(r['object_id']+'/'+Path(r['source_path']).name,1000000),r['case_id']))
    OUT.mkdir(exist_ok=True)
    if args.case:
        result=process(next(r for r in rows if r['case_id']==args.case));print(json.dumps(result),flush=True);return
    dump(OUT/'build_policy.json',{'input_count':len(rows),'build_version':VERSION,'source_directory':str(SOURCE),
        'rejected_reuse':'upstream same-ID CAD did not match original STL; fitted directly instead','provenance':'reconstructed CAD pseudo supervision',
        'mean_distance_max':.003,'p95_distance_max':.01,'sample_max_distance_max':.03,'unit':'source mesh bbox diagonal',
        'surface_points':8192,'curve_samples':32,'curve_token_cap':128,'split_unit':'object plus duplicate groups',
        'training_started':False})
    selected=rows[:args.limit] if args.limit else rows
    results=[];pending=[]
    for row in selected:
        path=OUT/'PartSAM/geometry_pack_v1'/row['case_id']/'record.json'
        old=json.loads(path.read_text()) if path.exists() else {}
        if old.get('build_version')==VERSION:results.append(old)
        else:pending.append(row)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(worker_launch,pending):
            results.append(result);counts=collections.Counter(r['status'] for r in results)
            dump(OUT/'geometry_progress.json',{'completed':len(results),'total':len(selected),'counts':dict(counts)})
            print(len(results),result['sample_id'],result['status'],result.get('reason',''),flush=True)
    dump(OUT/'geometry_results.json',results)
    print('DONE',dict(collections.Counter(r['status'] for r in results)),flush=True)

if __name__=='__main__':main()
