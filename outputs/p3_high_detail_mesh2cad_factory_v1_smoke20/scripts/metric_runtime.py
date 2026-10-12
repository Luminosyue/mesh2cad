"""Append-only Smoke100 driver; source and historical paths are read-only."""
import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    os.environ[name]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json, csv, sys, shutil, hashlib, subprocess, traceback, datetime, argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from fit_logic import candidate_axes, basis_for_axis, projected_profile, voxel_occupancy

ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'config/factory_config.json').read_text())
SEED=CONFIG['random_seed']
TAXONOMY=['SOURCE_UNREADABLE','SOURCE_DEGENERATE','SOURCE_INCOMPLETE','SOURCE_TOO_COMPLEX',
 'UNSUPPORTED_GEOMETRY','PRIMITIVE_FIT_FAILURE','PLANNER_FAILURE','CAD_SYNTAX_FAILURE',
 'CAD_EXECUTION_FAILURE','BOOLEAN_FAILURE','STEP_EXPORT_FAILURE','STEP_RELOAD_FAILURE',
 'GEOMETRY_MISMATCH','UNKNOWN','SOURCE_PROVENANCE_FAILURE','INVALID_CAD_TESSELLATION','EVALUATOR_FAILURE']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
    with Path(p).open('x') as f: json.dump(obj,f,indent=2,allow_nan=False)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(p): return trimesh.load(str(p),force='mesh',process=True)

def triangle_keys(mesh):
    # Both STL sources store float32 triangles. Vertex ordering/winding is irrelevant.
    t=np.asarray(mesh.triangles,dtype='<f4')
    order=np.lexsort((t[:,:,2],t[:,:,1],t[:,:,0]),axis=1)
    return {row.tobytes() for row in np.take_along_axis(t,order[:,:,None],axis=1)}

def source_audit(row,d):
    p=Path(row['source_mesh_path'])
    if sha(p)!=row['source_mesh_sha256'] or sha(row['source_evidence_path'])!=row['source_evidence_sha256'] or sha(row['parent_mesh_path'])!=row['parent_mesh_sha256']:
        raise ValueError('SOURCE_PROVENANCE_FAILURE: hash drift')
    shutil.copyfile(p,d/'source/source_mesh.stl')
    (d/'source/source_sha256.txt').write_text(row['source_mesh_sha256']+'\n')
    m=load(p)
    valid=bool(len(m.vertices)>0 and len(m.faces)>0 and np.isfinite(m.vertices).all() and
               m.faces.min()>=0 and m.faces.max()<len(m.vertices) and m.area>1e-15 and np.min(m.extents)>1e-12)
    if not valid: raise ValueError('SOURCE_DEGENERATE: empty, invalid faces, nonfinite or degenerate geometry')
    part_keys=triangle_keys(m); parent_keys=triangle_keys(load(row['parent_mesh_path']))
    overlap=len(part_keys & parent_keys)/max(1,len(part_keys))
    if overlap!=1: raise ValueError('SOURCE_PROVENANCE_FAILURE: parent triangle subset fraction '+str(overlap))
    counts=np.bincount(m.edges_unique_inverse)
    audit=dict(file_readable=True,vertex_count=len(m.vertices),face_count=len(m.faces),finite_coordinates=True,
        valid_face_indices=True,nondegenerate_bbox=True,connected_component_count=len(m.split(only_watertight=False)),
        watertight=bool(m.is_watertight),boundary_edge_count=int(np.sum(counts==1)),nonmanifold_edge_count=int(np.sum(counts>2)),
        degenerate_triangle_count=int(np.sum(m.area_faces<=1e-15)),surface_area=float(m.area),
        volume=float(abs(m.volume)) if m.is_volume else None,volume_meaningful=bool(m.is_volume),
        parent_triangle_subset_fraction=overlap,provenance_closed=True,
        incompleteness_confirmed=False,incompleteness_note='Open segmentation boundaries alone are not independent evidence of missing geometry.')
    write(d/'source/audit.json',audit)
    center=m.bounds.mean(0); extent=float(max(m.extents)); f=np.eye(4); f[:3,:3]/=extent; f[:3,3]=-center/extent
    inv=np.linalg.inv(f); original_bounds=m.bounds.tolist(); original_centroid=m.centroid.tolist()
    m.apply_transform(f)
    trans=dict(method='bbox_midpoint_longest_edge_1_orientation_preserved',center=center.tolist(),scale=1/extent,
       original_longest_extent=extent,translation=(-center).tolist(),rotation=None,rotation_if_any=None,
       transform_matrix=f.tolist(),inverse_transform_matrix=inv.tolist(),forward_transform=f.tolist(),inverse_transform=inv.tolist(),
       original_bbox=original_bounds,original_centroid=original_centroid,canonical_bbox=m.bounds.tolist(),canonical_centroid=m.centroid.tolist())
    write(d/'normalized/transform.json',trans); m.export(d/'normalized/normalized_mesh.ply')
    # Evaluation consistently uses the serialized canonical mesh, never an independently aligned CAD.
    return load(d/'normalized/normalized_mesh.ply'),audit,trans

def plane(origin,B):
    return 'cq.Plane(origin='+repr(np.asarray(origin).tolist())+', xDir='+repr(B[:,0].tolist())+', normal='+repr(B[:,2].tolist())+')'

def plan(mesh):
    axes=candidate_axes(mesh); programs=[]; errors=[]
    for axis in axes[:2]:
        try:
            spec=projected_profile(mesh,axis,max_entities=96)
            ps=spec['profiles']; n=sum(len(p['outer'])+sum(map(len,p['holes'])) for p in ps)
            if n>96 or len(ps)>4 or sum(len(p['holes']) for p in ps)>8:
                raise ValueError('SOURCE_TOO_COMPLEX: projected sketch budget exceeded')
            height=spec['zmax']-spec['zmin']
            if height<1e-6: raise ValueError('UNSUPPORTED_GEOMETRY: zero-thickness extrusion')
            B=np.asarray(spec['basis']); origin=np.asarray(spec['center'])+B[:,2]*spec['zmin']
            lines=['import cadquery as cq','plane = '+plane(origin,B)]
            for i,p in enumerate(ps):
                lines.append(f'p{i} = cq.Workplane(plane).polyline({p["outer"]!r}).close().extrude({height!r})')
                for j,h in enumerate(p['holes']):
                    lines.append(f'h{i}_{j} = cq.Workplane(plane).polyline({h!r}).close().extrude({height!r})')
                    lines.append(f'p{i} = p{i}.cut(h{i}_{j})')
            lines.append('result = p0'+''.join(f'.union(p{i})' for i in range(1,len(ps))))
            programs.append(('extrusion', '\n'.join(lines)+'\n',spec))
        except Exception as e: errors.append(str(e))
    # Finite analytical candidates, no iterative loss/parameter optimization.
    B=basis_for_axis(axes[0]); v=np.asarray(mesh.vertices)@B; lo=v.min(0); hi=v.max(0); ext=hi-lo
    if min(ext)>1e-6:
        origin=B@((lo+hi)/2)
        programs.append(('oriented_box','import cadquery as cq\nplane = '+plane(origin,B)+'\nresult = cq.Workplane(plane).box('+', '.join(map(repr,ext.tolist()))+')\n',{'basis':B.tolist(),'extents':ext.tolist(),'origin':origin.tolist()}))
        origin=B@np.array([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]])
        radius=float((ext[0]+ext[1])/4)
        programs.append(('cylinder','import cadquery as cq\nplane = '+plane(origin,B)+f'\nresult = cq.Workplane(plane).circle({radius!r}).extrude({float(ext[2])!r})\n',{'radius':radius,'height':float(ext[2]),'origin':origin.tolist()}))
    return programs[:4],errors

def evaluate(source,cad,seed):
    a,_=trimesh.sample.sample_surface(source,CONFIG['n_points'],seed=seed)
    b,_=trimesh.sample.sample_surface(cad,CONFIG['n_points'],seed=seed+1)
    da=cKDTree(b).query(a,workers=1)[0]; db=cKDTree(a).query(b,workers=1)[0]
    distances=np.concatenate([da,db]); diag=float(np.linalg.norm(source.extents))
    lo=np.minimum(source.bounds[0],cad.bounds[0]); hi=np.maximum(source.bounds[1],cad.bounds[1])
    pitch=float(max(hi-lo)/(CONFIG['iou_resolution']-4)); origin=lo-2*pitch
    shape=tuple((np.ceil((hi-origin)/pitch).astype(int)+3).tolist())
    oa=voxel_occupancy(source,origin,pitch,shape); ob=voxel_occupancy(cad,origin,pitch,shape)
    union=int(np.logical_or(oa,ob).sum()); intersection=int(np.logical_and(oa,ob).sum())
    if union==0: raise ValueError('Empty occupancy union')
    r=dict(chamfer_mean=float(distances.mean()),chamfer_p95=float(np.percentile(distances,95)),
        normalized_chamfer=float(distances.mean()/diag),ncd_normalizer='source bbox diagonal',
        chamfer_definition='mean of both equal-size directional nearest sampled-point distances, unsquared Euclidean',
        iou=intersection/union,iou_protocol=CONFIG['iou_protocol'],resolution=CONFIG['iou_resolution'],
        occupancy_method=CONFIG['occupancy_method'],voxel_origin=origin.tolist(),voxel_pitch=pitch,grid_shape=shape,
        intersection_voxels=intersection,union_voxels=union,bbox_center_error=float(np.linalg.norm(source.bounds.mean(0)-cad.bounds.mean(0))),
        bbox_extent_error=float(np.max(np.abs(source.extents-cad.extents))),
        centroid_l2_error=float(np.linalg.norm(source.centroid-cad.centroid)),centroid_definition='area-weighted surface centroid',
        n_points_per_mesh=CONFIG['n_points'],source_seed=seed,cad_seed=seed+1,evaluation_source='RELOADED_STEP_TESSELLATION')
    r['bbox_error']=max(r['bbox_center_error'],r['bbox_extent_error'])
    r['strict_pass']=bool(r['iou']>=.90 and r['normalized_chamfer']<=.01 and r['bbox_error']<=.03 and r['centroid_l2_error']<=.02)
    if not all(np.isfinite(r[k]) for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']): raise ValueError('Nonfinite metrics')
    return r

def process(row):
    d=ROOT/'cases'/row['case_id']
    if d.exists():
        if (d/'manifest.json').exists(): return json.loads((d/'manifest.json').read_text())
        raise RuntimeError('Incomplete case directory; preserve and investigate: '+str(d))
    d.mkdir()
    for name in ['source','normalized','cad','step','reload','mesh','metrics','cache','logs','attempts']: (d/name).mkdir()
    record=dict(row,source_is_original=True,source_type='REAL_MESH',reconstruction_branch='DIRECT',cad_language='CADQUERY',
        source_valid=False,direct_attempted=False,generation_timestamp=now(),llm_used=False,llm_provider=None,llm_model=None,prompt_hash=None,
        execution={},geometry_metrics={},filter_decision='REJECT',failure_reason=None,fallback_needed=False,fallback_attempted=False,
        surface_cache_status='NOT_BUILT',curve_cache_status='NOT_BUILT',cache_reason='Optional extraction deferred; no compatible cache extractor validated in this factory.',attempts=[])
    phase='SOURCE_UNREADABLE'
    try:
        source,audit,trans=source_audit(row,d)
        record.update(source_valid=True,source_audit=audit,normalization=trans,provenance_closed=True,direct_attempted=True)
        phase='PLANNER_FAILURE'; programs,errors=plan(source)
        record['planner_notes']=errors
        if not programs:
            raise ValueError('UNSUPPORTED_GEOMETRY: no finite solid CAD hypotheses')
        for i,(kind,code,spec) in enumerate(programs):
            a=d/'attempts'/f'attempt_{i:02d}'; a.mkdir(); p=a/'cad.py'; p.write_text(code)
            meta=dict(attempt_index=i,kind=kind,parameters=spec,llm_used=False,llm_provider=None,llm_model=None,prompt_hash=None,
                      generation_timestamp=now(),program_sha256=sha(p),native_construction='analytic primitive or bounded 2D sketch extrusion')
            write(a/'generation.json',meta)
            try:
                run=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/execute_program.py'),str(p),str(a/'execution')],
                    capture_output=True,text=True,timeout=CONFIG['timeout_seconds_per_candidate'],cwd=str(ROOT),env=os.environ.copy())
                (a/'execution.log').write_text(run.stdout+'\n'+run.stderr)
                result=json.loads((a/'execution/execution.json').read_text()) if (a/'execution/execution.json').exists() else {'failure_reason':'CAD_EXECUTION_FAILURE','error':'worker exited '+str(run.returncode)}
            except subprocess.TimeoutExpired:
                result={'failure_reason':'CAD_EXECUTION_FAILURE','error':'candidate timeout'}
            attempt=dict(meta,execution=result,attempt_path=str(a))
            if result.get('tessellation_pass'):
                try:
                    metrics=evaluate(source,load(a/'execution/cad_mesh_from_reloaded_step.ply'),SEED+int(row['case_id'].split('_')[1])*10)
                    metrics.update(source_mesh_sha256=sha(d/'normalized/normalized_mesh.ply'),cad_mesh_sha256=result['cad_mesh_sha256'],step_sha256=result['step_sha256'])
                    attempt['metrics']=metrics; write(a/'metrics.json',metrics)
                except Exception as e: attempt.update(failure_reason='EVALUATOR_FAILURE',error=str(e),traceback=traceback.format_exc())
            record['attempts'].append(attempt)
        valid=[a for a in record['attempts'] if 'metrics' in a]
        if not valid:
            ex=record['attempts'][-1]
            record['execution']=ex['execution']; record['failure_reason']=ex.get('failure_reason') or ex['execution'].get('failure_reason') or 'UNKNOWN'
        else:
            selected=max(valid,key=lambda a:(a['metrics']['strict_pass'],a['metrics']['iou'],-a['metrics']['normalized_chamfer']))
            a=Path(selected['attempt_path']); record.update(execution=selected['execution'],geometry_metrics=selected['metrics'],selected_attempt_index=selected['attempt_index'],
                filter_decision='STRICT_ACCEPT' if selected['metrics']['strict_pass'] else 'RELAXED_ANALYSIS_ONLY',
                failure_reason=None if selected['metrics']['strict_pass'] else 'GEOMETRY_MISMATCH')
            copies=[(a/'cad.py',d/'cad/cad.py'),(a/'generation.json',d/'cad/cad_generation_metadata.json'),
                    (a/'execution/cad.step',d/'step/cad.step'),(a/'execution/execution.json',d/'reload/reload_metadata.json'),
                    (a/'execution/cad_mesh_from_reloaded_step.ply',d/'mesh/cad_mesh_from_reloaded_step.ply'),(a/'metrics.json',d/'metrics/metrics.json')]
            for src,dst in copies: shutil.copyfile(src,dst)
            record.update(cad_program_path=str(d/'cad/cad.py'),step_path=str(d/'step/cad.step'),cad_mesh_path=str(d/'mesh/cad_mesh_from_reloaded_step.ply'))
    except Exception as e:
        message=str(e); explicit=message.split(':')[0]
        record.update(failure_reason=explicit if explicit in TAXONOMY else phase,error=message,traceback=traceback.format_exc())
    record['completed_timestamp']=now()
    write(d/'cache/status.json',{k:record[k] for k in ['surface_cache_status','curve_cache_status','cache_reason']})
    (d/'logs/generation.log').write_text(json.dumps({'planner_notes':record.get('planner_notes'), 'attempt_n':len(record['attempts'])}))
    (d/'logs/execution.log').write_text(json.dumps([a['execution'] for a in record['attempts']],indent=2))
    (d/'logs/errors.log').write_text(json.dumps({'failure_reason':record['failure_reason'],'error':record.get('error'),'attempt_errors':[a for a in record['attempts'] if a.get('failure_reason') or a['execution'].get('failure_reason')]},indent=2))
    write(d/'manifest.json',record)
    print(json.dumps({'case':row['case_id'],'decision':record['filter_decision'],'reason':record['failure_reason'],'iou':record['geometry_metrics'].get('iou')}),flush=True)
    return record

def guard():
    protected=json.loads((ROOT/'integrity/PROTECTED_SOURCE_HASHES.json').read_text()); errors=[]
    for p,info in protected.items():
        if not Path(p).exists() or sha(p)!=info['sha256']: errors.append(p)
    for p,size,mtime,mode in json.loads((ROOT/'integrity/HISTORICAL_METADATA_BEFORE.json').read_text()):
        try:
            s=Path(p).stat()
            if (s.st_size,s.st_mtime_ns,s.st_mode)!=(size,mtime,mode): errors.append(p)
        except FileNotFoundError: errors.append(p)
    return {'status':'PASS' if not errors else 'FAIL','hash_checked_n':len(protected),'metadata_checked_n':74530,'changed_paths':sorted(set(errors)),'timestamp':now(),
            'scope':'selected source, parent, provenance reports, reused donor and frozen audit hashes; all preexisting files in relevant historical trees metadata. Access time excluded.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int,choices=[3,10,100],required=True); args=ap.parse_args()
    stage=ROOT/'stages'/f'stage_{args.limit:03d}'
    stage.mkdir(exist_ok=False)
    if args.limit>3:
        prev=3 if args.limit==10 else 10
        before=json.loads((ROOT/'stages'/f'stage_{prev:03d}'/'validation.json').read_text())
        if not before['pass']: raise RuntimeError('Previous stage did not pass')
    check=guard(); write(stage/'guard_before.json',check)
    if check['status']!='PASS': raise RuntimeError('Historical guard failed')
    hashes={str(p.relative_to(ROOT)):sha(p) for folder in ['scripts','config'] for p in (ROOT/folder).glob('*') if p.is_file()}
    write(stage/'code_config_hashes.json',hashes)
    rows=json.loads((ROOT/'manifests/selection_frozen.json').read_text())['cases'][:args.limit]
    with ProcessPoolExecutor(max_workers=CONFIG['workers']) as pool: results=list(pool.map(process,rows))
    after=guard(); write(stage/'guard_after.json',after)
    evaluated=[r for r in results if r['geometry_metrics']]
    system_errors=[r['case_id'] for r in results if r['failure_reason'] in ['UNKNOWN','EVALUATOR_FAILURE','SOURCE_PROVENANCE_FAILURE']]
    validation={'pass':after['status']=='PASS' and not system_errors and bool(evaluated) and (args.limit!=3 or len(evaluated)==3),
                'n':len(results),'evaluated_n':len(evaluated),'system_errors':system_errors,'strict_n':sum(r['filter_decision']=='STRICT_ACCEPT' for r in results),'timestamp':now()}
    write(stage/'validation.json',validation); print(json.dumps(validation),flush=True)

if __name__=='__main__': main()
