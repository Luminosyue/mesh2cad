"""Estimate assembled solid-union IoU by shared scrambled Sobol volume samples."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,time,sys,subprocess,traceback
from concurrent.futures import ThreadPoolExecutor
import numpy as np,trimesh,open3d as o3d
from scipy.stats import qmc
R=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922');OUT=R/'assembly_iou';OUT.mkdir(exist_ok=True)
def occupancy(meshes,points):
    inside=np.zeros(len(points),dtype=bool)
    for mesh in meshes:
        bounds=mesh.bounds
        candidates=np.flatnonzero(~inside & np.all(points>=bounds[0],axis=1)&np.all(points<=bounds[1],axis=1))
        if not len(candidates):continue
        scene=o3d.t.geometry.RaycastingScene(nthreads=1)
        scene.add_triangles(o3d.t.geometry.TriangleMesh(o3d.core.Tensor(np.asarray(mesh.vertices,dtype='float32')),o3d.core.Tensor(np.asarray(mesh.faces,dtype='uint32'))))
        for start in range(0,len(candidates),32768):
            ix=candidates[start:start+32768];values=scene.compute_occupancy(o3d.core.Tensor(points[ix]),nthreads=1,nsamples=3).numpy();inside[ix]=values>.5
    return inside
def one(case,power):
    start=time.time();sources=[];cads=[];issues=[];reports=[]
    for path in sorted((R/'cases'/case).glob('PART_*/report.json')):
        report=json.loads(path.read_text());reports.append(report)
        source=trimesh.load(report['source_path'],force='mesh',process=False);source.process(validate=True);source.remove_unreferenced_vertices()
        cad=trimesh.load(path.parent/'model.stl',force='mesh',process=True)
        for label,mesh in [('source',source),('cad_tessellation',cad)]:
            if not mesh.is_watertight:issues.append(report['part_id']+': '+label+' not watertight')
            if not mesh.is_winding_consistent:issues.append(report['part_id']+': '+label+' inconsistent winding')
        sources.append(source);cads.append(cad)
    bounds=np.array([m.bounds for m in sources+cads]);lo=bounds[:,0].min(0);hi=bounds[:,1].max(0);center=(lo+hi)/2;scale=(hi-lo).max()
    for mesh in sources+cads:mesh.vertices=(mesh.vertices-center)/scale
    lo=(lo-center)/scale;hi=(hi-center)/scale
    points=(qmc.Sobol(d=3,scramble=True,seed=92817+power).random_base2(power)*(hi-lo)+lo).astype('float32')
    a=occupancy(sources,points);b=occupancy(cads,points);inter=int(np.count_nonzero(a&b));union=int(np.count_nonzero(a|b))
    result=dict(case_id=case,parts=len(reports),accepted_parts=sum(r['status']=='ACCEPTED' for r in reports),needs_refinement_parts=sum(r['status']!='ACCEPTED' for r in reports),sample_power=power,samples=len(points),intersection_samples=inter,union_samples=union,iou=inter/union if union else None,source_volume_samples=int(a.sum()),cad_volume_samples=int(b.sum()),source_coverage=inter/int(a.sum()) if a.any() else None,cad_precision=inter/int(b.sum()) if b.any() else None,closed_mesh_inputs=not issues,issues=issues,seconds=time.time()-start,method='scrambled Sobol common samples; Open3D parity occupancy with three rays; Boolean OR across parts; source numeric coordinates retained; CAD tessellation from delivered STEP')
    (OUT/(case+f'_p{power}.json')).write_text(json.dumps(result,indent=2));print(case,round(result['iou'] or 0,5),'closed',not issues,round(result['seconds'],1),flush=True)
def main():
    if '--one' in sys.argv:return one(sys.argv[2],int(sys.argv[3]))
    power=20 if '--refine' in sys.argv else 18
    cases=sorted(p.name for p in (R/'cases').iterdir() if p.is_dir() and p.name!='tank')
    if power==20:
        coarse=json.loads((OUT/'ranking_p18.json').read_text())
        candidates=sorted([r for r in coarse if r['closed_mesh_inputs'] and r['iou'] is not None],key=lambda r:-r['iou'])[:15]
        cases=[r['case_id'] for r in candidates]
    def run(case):
        target=OUT/(case+f'_p{power}.json')
        if target.exists():return
        with (OUT/(case+f'_p{power}.log')).open('w') as f:
            try:rr=subprocess.run([sys.executable,__file__,'--one',case,str(power)],stdout=f,stderr=subprocess.STDOUT,timeout=600);print('DONE',case,rr.returncode,flush=True)
            except Exception as e:print('FAILED',case,str(e),flush=True)
    with ThreadPoolExecutor(max_workers=10) as pool:list(pool.map(run,cases))
    results=[json.loads((OUT/(c+f'_p{power}.json')).read_text()) for c in cases if (OUT/(c+f'_p{power}.json')).exists()]
    results.sort(key=lambda r:-(r['iou'] or 0));(OUT/f'ranking_p{power}.json').write_text(json.dumps(results,indent=2));print('FINISHED',power,len(results),flush=True)
if __name__=='__main__':main()
