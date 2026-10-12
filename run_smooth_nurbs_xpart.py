import os,sys,json,subprocess,shutil,traceback
from pathlib import Path
import numpy as np
import trimesh
import cadquery as cq
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad')
import pilot_repaired as base

OLD=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_nurbs_air_tank_v1')
ENV=base.ENV.copy(); ENV.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=m.to_mesh()
    m.merge_vertices();m.remove_unreferenced_vertices();return m

def code(pr):
    return '''import cadquery as cq
from pathlib import Path

def build_model():
    sections=%r
    origin=%r
    xdir=%r
    normal=%r
    wires=[]
    for sec in sections:
        plane=cq.Plane(origin=tuple(origin[i]+normal[i]*sec["z"] for i in range(3)),xDir=tuple(xdir),normal=tuple(normal))
        pts=[tuple(p) for p in sec["points"]][::4]
        # Periodic closed B-spline: smooth analytic section instead of polygon edges.
        wires.append(cq.Workplane(plane).spline(pts,periodic=True).close().val())
    body=cq.Solid.makeLoft(wires,False)
    return cq.Workplane(obj=body)

if __name__=="__main__":
    body=build_model()
    out=Path(__file__).resolve().parent
    cq.exporters.export(body,str(out/"reconstructed.step"))
    cq.exporters.export(body,str(out/"reconstructed.stl"),tolerance=1e-5,angularTolerance=0.10)
    print({"valid":body.val().isValid(),"solids":body.solids().size(),"faces":body.faces().size()})
'''%(pr['sections'],pr['origin'],pr['xdir'],pr['normal'])

def main():
    results=[]
    tasks=[]
    for case in ('airplane','tank'):
        for olddir in sorted((OLD/'cases'/case).glob('xpart_parts__*/')):
            mp=olddir/'metrics.json'; pp=olddir/'parameters.json'
            if not mp.exists() or not pp.exists(): continue
            d=json.loads(mp.read_text())
            if '/xpart_parts/' not in d.get('source_path',''): continue
            tasks.append((case,olddir,d,json.loads(pp.read_text())))
    print('TASKS',len(tasks),flush=True)
    for idx,(case,olddir,d,pr) in enumerate(tasks,1):
        part=olddir.name; od=OUT/'cases'/case/part; od.mkdir(parents=True,exist_ok=True)
        try:
            source=olddir/'source.stl'; shutil.copy2(source,od/'source.stl')
            (od/'cad.py').write_text(code(pr),encoding='utf-8')
            (od/'parameters.json').write_text(json.dumps(pr,indent=2),encoding='utf-8')
            program={'version':'XPART_SMOOTH_NURBS_CAD_V1','geometry_family':'PERIODIC_BSPLINE_SECTION_LOFT','operations':[{'type':'SKETCH_BSPLINE_SECTION','count':len(pr['sections']),'points_per_section':len(pr['sections'][0]['points']),'periodic':True},{'type':'SMOOTH_LOFT','ruled':False}],'source_path':d['source_path']}
            (od/'program.json').write_text(json.dumps(program,indent=2),encoding='utf-8')
            run=subprocess.run([sys.executable,'cad.py'],cwd=od,env=ENV,capture_output=True,text=True,timeout=60)
            if run.returncode!=0: raise RuntimeError(run.stderr[-1000:])
            m=load(source); cm=load(od/'reconstructed.stl'); mm=base.metrics(m,cm,high=True)
            sh=cq.importers.importStep(str(od/'reconstructed.step')).val(); faces=len(sh.Faces()); solids=len(sh.Solids()); valid=bool(sh.isValid()) and solids>=1
            quality='A_HIGH_CONFIDENCE' if mm['iou128']>=.90 and mm['ncd']<=.08 else ('B_USABLE' if mm['iou128']>=.80 and mm['ncd']<=.15 else ('C_NEAR_MISS' if mm['iou128']>=.65 else 'D_REJECT'))
            validpair=bool(valid and quality in ('A_HIGH_CONFIDENCE','B_USABLE'))
            result={'case_id':case,'part_id':part,'source_path':d['source_path'],'geometry_family':'PERIODIC_BSPLINE_SECTION_LOFT','feature_sequence':'BSPLINE_SECTION x%d -> SMOOTH_LOFT'%len(pr['sections']),'cad_program_exec':'PASS','brep_valid':valid,'step_reload':True,'mesh_import_used':False,'faceted_brep':False,'source_triangle_count':len(m.faces),'cad_brep_face_count':faces,'cad_brep_solid_count':solids,'quality_level':quality,'valid_training_pair':validpair,'failure_reason':'' if validpair else 'IOU_OR_DISTANCE_THRESHOLD',**mm}
            (od/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
            (od/'validation.json').write_text(json.dumps({'CAD_PARSE':'PASS','CAD_EXECUTION':'PASS','BREP_VALID':'YES' if valid else 'NO','SOLID_COUNT':solids,'STEP_EXPORT':'PASS','STEP_RELOAD':'PASS','MESH_EXPORT':'PASS','MESH_IMPORT_USED':'NO','SMOOTH_BSPLINE':'YES','VALID_TRAINING_PAIR':'YES' if validpair else 'NO'},indent=2),encoding='utf-8')
            (od/'report.md').write_text(f'# {case}/{part}\\n\\nPeriodic closed B-spline sections with smooth loft.\\n\\nIoU128={mm["iou128"]:.6f}; NCD={mm["ncd"]:.6f}; quality={quality}; valid_pair={validpair}.\\n',encoding='utf-8')
            results.append(result)
            print('DONE',idx,'/',len(tasks),case,part,'iou',round(mm['iou128'],4),'faces',faces,quality,flush=True)
        except Exception as e:
            result={'case_id':case,'part_id':part,'source_path':d.get('source_path'),'cad_program_exec':'FAIL','failure_reason':str(e)}
            (od/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); results.append(result)
            print('FAIL',idx,case,part,str(e)[:300],flush=True)
    for case in ('airplane','tank'):
        rs=[r for r in results if r['case_id']==case]; good=[r for r in rs if r.get('cad_program_exec')=='PASS']
        from collections import Counter
        summary={'case':case,'total_xpart':len(rs),'generated':len(good),'valid_pairs':sum(r.get('valid_training_pair',False) for r in good),'iou128_mean':float(np.mean([r['iou128'] for r in good])) if good else None,'quality_counts':dict(Counter(r.get('quality_level') for r in good))}
        (OUT/f'summary_{case}.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (OUT/'all_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('FINISHED',len(results),flush=True)

if __name__=='__main__': main()



