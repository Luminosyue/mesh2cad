"""Reproducible STL -> standalone faceted CadQuery -> STEP roundtrip evaluation."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[key]='1'
from pathlib import Path
import json,csv,time,hashlib,subprocess,sys,shutil,traceback
from concurrent.futures import ProcessPoolExecutor,as_completed
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=ROOT.with_name('p3_parts_cad_results')
QUARANTINE=ROOT.with_name('p3_parts_cad_quarantine')
THRESHOLD=0.90
MODEL_CODE=r'''
from pathlib import Path
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCP.ShapeFix import ShapeFix_Shape, ShapeFix_Solid
UNIT_SCALE=1.0  # original STL numerical coordinates, unknown physical units
def build_model():
    sew=BRepBuilderAPI_Sewing(TOLERANCE)
    for face in FACES:
        points=[cq.Vector(*VERTICES[i]) for i in face]
        sew.Add(cq.Face.makeFromWires(cq.Wire.makePolygon(points,close=True)).wrapped)
    sew.Perform()
    fixer=ShapeFix_Shape(sew.SewedShape());fixer.Perform()
    shape=cq.Shape.cast(fixer.Shape())
    shells=shape.Shells()
    # Only promote genuinely closed shells. Open shells remain surface CAD.
    if shells and sum(len(s.Faces()) for s in shells)==len(shape.Faces()):
        parts=[]
        for shell in shells:
            if shell.Closed():
                solid=cq.Solid.makeSolid(shell)
                sf=ShapeFix_Solid(solid.wrapped);sf.Perform()
                candidate=cq.Shape.cast(sf.Solid())
                parts.append(candidate if candidate.isValid() else shell)
            else: parts.append(shell)
        shape=parts[0] if len(parts)==1 else cq.Compound.makeCompound(parts)
    return shape.scale(UNIT_SCALE) if UNIT_SCALE!=1 else shape
if __name__=='__main__':
    result=build_model()
    cq.exporters.export(result,str(Path(__file__).with_name('model.step')))
    print({'valid':result.isValid(),'faces':len(result.Faces()),'solids':len(result.Solids())})
elif 'show_object' in globals():
    show_object(build_model())
'''
def surface_iou(a,b,resolution):
    import numpy as np
    # Both voxelizers use the same pitch and world-aligned lattice.
    bounds=np.vstack([a.bounds,b.bounds]);pitch=float(np.ptp(bounds,axis=0).max()/resolution)
    def occupied(m):
        indices=np.rint(m.voxelized(pitch).points/pitch).astype('int64')
        return set(map(tuple,indices.tolist()))
    sa,sb=occupied(a),occupied(b)
    return len(sa&sb)/len(sa|sb),pitch,len(sa),len(sb)
def volume_iou(a,b,resolution=64):
    import numpy as np,open3d as o3d
    if not(a.is_watertight and b.is_watertight and a.is_winding_consistent and b.is_winding_consistent):
        return None,'undefined: source or STEP tessellation is not a closed, consistently oriented mesh'
    scenes=[]
    for m in [a,b]:
        mesh=o3d.t.geometry.TriangleMesh(o3d.core.Tensor(m.vertices.astype('float32')),o3d.core.Tensor(m.faces.astype('uint32')))
        scene=o3d.t.geometry.RaycastingScene(nthreads=1);scene.add_triangles(mesh);scenes.append(scene)
    lo=np.minimum(a.bounds[0],b.bounds[0]);hi=np.maximum(a.bounds[1],b.bounds[1])
    pitch=max(hi-lo)/resolution
    axes=[np.arange(lo[i]+pitch*.5,hi[i],pitch) for i in range(3)]
    if any(len(axis)==0 for axis in axes): return None,'object too thin at this grid resolution'
    pts=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3).astype('float32')
    ins=[scene.compute_occupancy(o3d.core.Tensor(pts),nthreads=1,nsamples=3).numpy()>.5 for scene in scenes]
    union=int(np.count_nonzero(ins[0]|ins[1]))
    return (float(np.count_nonzero(ins[0]&ins[1])/union) if union else None),'64 cells along longest union-bounds axis; common voxel centers'
def process(src_string):
    import numpy as np,trimesh,open3d as o3d,cadquery as cq
    src=Path(src_string);rel=src.relative_to(ROOT);folder=OUT/'samples'/rel.with_suffix('')
    folder.mkdir(parents=True,exist_ok=True);t=time.time()
    rec={'source':str(rel),'output':str(folder.relative_to(OUT)),'status':'error','reason':None}
    try:
        rec['source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
        mesh=trimesh.load_mesh(src,process=False);mesh.merge_vertices();mesh.remove_unreferenced_vertices()
        rec.update(source_faces=len(mesh.faces),source_watertight=bool(mesh.is_watertight))
        if not np.isfinite(mesh.vertices).all() or len(mesh.faces)==0: raise ValueError('empty or nonfinite mesh')
        scale=float(mesh.extents.max())
        om=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(mesh.vertices),o3d.utility.Vector3iVector(mesh.faces))
        if len(mesh.faces)>5000: om=om.simplify_quadric_decimation(target_number_of_triangles=5000)
        om.remove_duplicated_triangles();om.remove_degenerate_triangles();om.remove_duplicated_vertices()
        dm=trimesh.Trimesh(np.asarray(om.vertices),np.asarray(om.triangles),process=True)
        dm.export(folder/'mesh_decimated.stl')
        # Use double precision embedded coordinates; generated code needs no STL input.
        code='"""Standalone mesh-derived faceted CAD; not a recovered parametric feature tree."""\n'
        code+='VERTICES='+repr(dm.vertices.tolist())+'\nFACES='+repr(dm.faces.tolist())+'\n'
        code+='TOLERANCE='+repr(max(scale*1e-7,1e-9))+'\n'+MODEL_CODE
        (folder/'cad_model.py').write_text(code)
        run=subprocess.run([sys.executable,str(folder/'cad_model.py')],capture_output=True,text=True,timeout=300)
        (folder/'rebuild.log').write_text(run.stdout+'\n'+run.stderr)
        if run.returncode: raise RuntimeError('generated code failed: '+run.stderr[-1200:])
        # Evaluate actual CAD output, not the pre-CAD decimation surrogate.
        shape=cq.importers.importStep(str(folder/'model.step')).val()
        verts,faces=shape.tessellate(max(scale*1e-5,1e-8))
        cad=trimesh.Trimesh([v.toTuple() for v in verts],faces,process=True)
        cad.export(folder/'cad_rebuilt.stl')
        rec.update(cad_valid=bool(shape.isValid()),cad_faces=len(shape.Faces()),cad_solids=len(shape.Solids()),
                   cad_shells=len(shape.Shells()),cad_watertight=bool(cad.is_watertight),rebuild_test_passed=True,
                   cad_mesh_faces=len(cad.faces),source_extent=mesh.extents.tolist())
        iou,pitch,na,nb=surface_iou(mesh,cad,64)
        rec.update(surface_iou_64=iou,voxel_pitch=pitch,source_surface_voxels=na,cad_surface_voxels=nb)
        vi,reason=volume_iou(mesh,cad)
        rec.update(volume_iou_64=vi,volume_iou_note=reason)
        # Higher resolution diagnostic for borderline outcomes, no silent threshold change.
        if .85<=iou<=.95: rec['surface_iou_128']=surface_iou(mesh,cad,128)[0]
        reasons=[]
        if iou<THRESHOLD: reasons.append('low_surface_iou')
        if not rec['cad_valid']: reasons.append('invalid_cad')
        rec.update(status='rejected' if reasons else 'kept',reason=','.join(reasons) if reasons else 'passed')
    except Exception as e:
        rec.update(status='error',reason=repr(e),traceback=traceback.format_exc())
    rec['elapsed_sec']=time.time()-t
    (folder/'metrics.json').write_text(json.dumps(rec,indent=2))
    return rec
def write_csv(path,rows):
    keys=sorted({key for row in rows for key in row})
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def main():
    OUT.mkdir(exist_ok=True)
    files=sorted(p for p in ROOT.rglob('p3_parts/*') if p.is_file() and p.suffix.lower() in {'.obj','.stl'})
    inventory=[str(p.relative_to(ROOT)) for p in files]
    (OUT/'input_inventory.json').write_text(json.dumps(inventory,indent=2))
    print('inputs',len(files),flush=True)
    results=[]
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(process,str(p)):p for p in files}
        for future in as_completed(futures):
            rec=future.result();results.append(rec)
            print(len(results),rec['source'],rec['status'],rec.get('surface_iou_64'),flush=True)
    results.sort(key=lambda r:r['source'])
    # Report only; source data are never moved or modified.
    write_csv(OUT/'all_manifest.csv',results)
    moves=[]
    (OUT/'quarantine_plan.json').write_text(json.dumps(moves,indent=2))
    (OUT/'quarantine_completed.json').write_text(json.dumps(moves,indent=2))
    for status in ['kept','rejected','error']: write_csv(OUT/(status+'_manifest.csv'),[r for r in results if r['status']==status])
    kept=[r for r in results if r['status']=='kept']
    vals=[r['surface_iou_64'] for r in kept]
    summary={'total_stl':len(results),'kept':len(kept),'rejected':sum(r['status']=='rejected' for r in results),
      'errors':sum(r['status']=='error' for r in results),'low_surface_iou':sum(r.get('surface_iou_64',1)<THRESHOLD for r in results),
      'invalid_cad':sum(r.get('cad_valid') is False for r in results),'threshold':THRESHOLD,
      'filter_metric':'surface_voxel_iou_64_of_source_and_STEP_roundtrip','volume_iou_defined':sum(r.get('volume_iou_64') is not None for r in results),
      'mean_kept_iou':sum(vals)/len(vals) if vals else None,'min_kept_iou':min(vals) if vals else None,
      'source_stl_remaining':sum(p.suffix.lower()=='.stl' for p in ROOT.rglob('*') if p.is_file()),
      'generated_code_count':len(list((OUT/'samples').rglob('cad_model.py')))}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__': main()

