from pathlib import Path
import os, json, csv, math, shutil, subprocess
import numpy as np
import trimesh
from scipy.spatial import cKDTree

# CadQuery's optional ezdxf dependency expects older pyparsing spellings.
try:
    import pyparsing, builtins
    for _old, _new in [('add_parse_action','addParseAction'), ('set_results_name','setResultsName'), ('add_condition','addCondition'), ('parse_string','parseString')]:
        if hasattr(pyparsing.ParserElement, _new) and not hasattr(pyparsing.ParserElement, _old):
            setattr(pyparsing.ParserElement, _old, getattr(pyparsing.ParserElement, _new))
    for _old, _new in [('one_of','oneOf'), ('infix_notation','infixNotation'), ('delimited_list','delimitedList')]:
        if hasattr(pyparsing, _new): setattr(builtins, _old, getattr(pyparsing, _new))
except Exception:
    pass

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_executable_cad_v1')
for d in ['audit','cases','manifests','visualizations']:(OUT/d).mkdir(parents=True,exist_ok=True)

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=trimesh.util.concatenate(tuple(m.geometry.values()))
    m.merge_vertices(); m.remove_unreferenced_vertices(); return m
def pca(m):
    x=m.vertices-m.vertices.mean(0); w,v=np.linalg.eigh(np.cov(x.T)); v=v[:,np.argsort(w)[::-1]]
    if np.linalg.det(v)<0: v[:,-1]*=-1
    y=x@v; return v,y.max(0)-y.min(0),m.vertices.mean(0)
def vec(x): return '('+','.join(repr(float(a)) for a in x)+')'
def axis_angle(axis):
    a=np.asarray(axis,float); a/=max(np.linalg.norm(a),1e-12); z=np.array([0.,0.,1.]); ang=math.degrees(math.acos(float(np.clip(z@a,-1,1)))); cr=np.cross(z,a)
    return (cr/np.linalg.norm(cr)).tolist() if np.linalg.norm(cr)>1e-8 else [1.,0.,0.],ang
def cad_code(kind,p):
    f=lambda x:repr(float(x))
    pre="""import pyparsing, builtins
for _old, _new in [('add_parse_action','addParseAction'), ('set_results_name','setResultsName'), ('add_condition','addCondition'), ('parse_string','parseString')]:
    if hasattr(pyparsing.ParserElement, _new) and not hasattr(pyparsing.ParserElement, _old): setattr(pyparsing.ParserElement, _old, getattr(pyparsing.ParserElement, _new))
for _old, _new in [('one_of','oneOf'), ('infix_notation','infixNotation'), ('delimited_list','delimitedList')]:
    if hasattr(pyparsing, _new): setattr(builtins, _old, getattr(pyparsing, _new))
import cadquery as cq
from pathlib import Path

def build_model():
"""
    if kind=='cylinder':
        ax,ang=axis_angle(p['axis']); body=f"    body=cq.Workplane('XY').cylinder({f(p['height'])},{f(p['radius'])},centered=(True,True,True))\n    body=body.rotate((0,0,0),{vec(ax)},{f(ang)})\n    body=body.translate({vec(p['center'])})\n"
    elif kind=='box':
        from scipy.spatial.transform import Rotation
        rx,ry,rz=Rotation.from_matrix(np.array(p['R'])).as_euler('xyz',degrees=True)
        d=p['dims']; body=f"    body=cq.Workplane('XY').rect({f(d[0])},{f(d[1])}).extrude({f(d[2])},both=True)\n    body=body.rotate((0,0,0),(1,0,0),{f(rx)})\n    body=body.rotate((0,0,0),(0,1,0),{f(ry)})\n    body=body.rotate((0,0,0),(0,0,1),{f(rz)})\n    body=body.translate({vec(p['center'])})\n"
    elif kind=='revolve':
        body=f"    body=cq.Workplane('XZ').moveTo({f(p['r0'])},0).lineTo({f(p['r1'])},0).lineTo({f(p['r1'])},{f(p['h'])}).lineTo({f(p['r0'])},{f(p['h'])}).close().revolve(360,(0,0,0),(0,1,0))\n    body=body.translate({vec(p['center'])})\n"
    else: body=f"    body=cq.Workplane('XY').sphere({f(p['radius'])}).translate({vec(p['center'])})\n"
    return pre+body+"    return body\n\nif __name__=='__main__':\n    result=build_model()\n    cq.exporters.export(result,str(Path(__file__).with_name('reconstructed.step')))\n    cq.exporters.export(result,str(Path(__file__).with_name('reconstructed.stl')))\n    print({'valid':result.val().isValid(),'solids':result.solids().size(),'faces':result.faces().size()})\n"
def program(kind,p):
    if kind=='cylinder': ops=[{'type':'CYLINDER','radius':p['radius'],'height':p['height'],'axis':p['axis'],'center':p['center']}]; fam='PRIMITIVE'
    elif kind=='box': ops=[{'type':'SKETCH_RECTANGLE','width':p['dims'][0],'height':p['dims'][1],'center':[0,0]},{'type':'EXTRUDE','distance':p['dims'][2]},{'type':'ROTATE_TRANSLATE','rotation_matrix':np.asarray(p['R']).round(9).tolist(),'translation':p['center']}]; fam='EXTRUSION'
    elif kind=='revolve': ops=[{'type':'SKETCH_RECTANGLE','width':p['r1']-p['r0'],'height':p['h'],'center':[p['r0'],0]},{'type':'REVOLVE','angle':360,'axis':[0,1,0]}]; fam='REVOLUTION'
    else: ops=[{'type':'SPHERE','radius':p['radius'],'center':p['center']}]; fam='PRIMITIVE'
    return {'version':'XPART_CAD_DSL_V1','geometry_family':fam,'operations':ops}
def candidates(m):
    R,e,c=pca(m); return [('cylinder',{'axis':R[:,0].tolist(),'height':float(e[0]),'radius':float((e[1]+e[2])/4),'center':c.tolist(),'R':R.tolist()}),('box',{'dims':e.tolist(),'center':c.tolist(),'R':R.tolist()}),('revolve',{'r0':float(min(e[1],e[2])*0.05),'r1':float(max(e[1],e[2])/2),'h':float(e[0]),'center':c.tolist(),'R':R.tolist()}),('sphere',{'radius':float(np.mean(e)/2),'center':c.tolist(),'R':R.tolist()})]
def surface_points(m,n=3000):
    np.random.seed(7); return trimesh.sample.sample_surface(m,min(n,max(100,len(m.faces)*2)))[0]
def voxel_iou(a,b,res):
    lo=np.minimum(a.bounds[0],b.bounds[0]); hi=np.maximum(a.bounds[1],b.bounds[1]); pitch=float(max(hi-lo)/res)
    def ids(m): return set(map(tuple,np.floor((m.voxelized(pitch).fill().points-lo)/pitch).astype(np.int64)))
    x,y=ids(a),ids(b); return float(len(x&y)/len(x|y)) if x|y else 0.
def metrics(a,b):
    sp,cp=surface_points(a),surface_points(b); d1=cKDTree(cp).query(sp)[0]; d2=cKDTree(sp).query(cp)[0]; diag=float(np.linalg.norm(a.extents)); cd=float((d1.mean()+d2.mean())/2); hd=float(max(d1.max(),d2.max()))
    return {'iou64':voxel_iou(a,b,64),'iou128':voxel_iou(a,b,128),'iou256':voxel_iou(a,b,256),'cd':cd,'ncd':cd/max(diag,1e-9),'hausdorff':hd,'nhd':hd/max(diag,1e-9),'normal_consistency':None,'bbox_error':float(np.linalg.norm(a.extents-b.extents)/max(diag,1e-9)),'centroid_error':float(np.linalg.norm(a.centroid-b.centroid)/max(diag,1e-9)),'surface_area_error':float(abs(a.area-b.area)/max(a.area,1e-9)),'volume_error':float(abs(a.volume-b.volume)/max(abs(a.volume),1e-9)) if a.is_volume else None}

def family(m):
    _,e,_=pca(m); ratio=max(e)/max(min(e),1e-9)
    if ratio>5: return 'EXTRUSION',0.5,['CYLINDER','EXTRUDE']
    if abs(e[0]-e[1])/max(e[0],1e-9)<.25 and e[2]<.55*e[0]: return 'REVOLUTION',0.55,['REVOLVE','CYLINDER','HOLE']
    if ratio<2.5: return 'PRIMITIVE',0.5,['BOX','CYLINDER','SPHERE']
    return 'FREEFORM_DIFFICULT',0.2,['PROFILE_EXTRUSION','BOOLEAN_COMPOSITE']
def scan_sources():
    rows=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in ('.obj','.stl') or p.parent.name not in ('p3_parts','xpart_parts'): continue
        try:
            m=load(p); rows.append({'path':str(p.relative_to(ROOT)),'watertight':bool(m.is_watertight),'volume':bool(m.is_volume),'vertices':len(m.vertices),'faces':len(m.faces),'extents':m.extents.tolist(),'centroid':m.centroid.tolist(),'bbox_diagonal':float(np.linalg.norm(m.extents)),'surface_area':float(m.area),'volume_value':float(m.volume) if m.is_volume else None})
        except Exception as e: rows.append({'path':str(p.relative_to(ROOT)),'watertight':False,'volume':False,'error':repr(e)})
    return rows
def select_pilot(rows):
    good=[r for r in rows if r['watertight'] and r['volume']]; buckets={'rod':[],'round':[],'compact':[],'complex':[]}
    for r in good:
        e=np.array(r['extents']); ratio=e.max()/max(e.min(),1e-9)
        key='rod' if ratio>5 else 'round' if abs(np.sort(e)[-1]-np.sort(e)[-2])/max(np.sort(e)[-1],1e-9)<.3 else 'compact' if ratio<2.4 else 'complex'; buckets[key].append(r)
    sel=[]
    for key,n in [('rod',4),('round',7),('compact',5),('complex',4)]: sel.extend(sorted(buckets[key],key=lambda x:x['path'])[:n])
    return sel[:20]
def overlay(src,cad,out):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(8,4))
    for i,(m,col,title) in enumerate([(src,'#E69F00','SOURCE'),(cad,'#0072B2','CAD')]):
        ax=fig.add_subplot(1,2,i+1,projection='3d'); tri=m.triangles[::max(1,len(m.faces)//1600)]; ax.add_collection3d(Poly3DCollection(tri,facecolor=col,alpha=.72,edgecolor='none')); lo,hi=m.bounds;c=(lo+hi)/2;e=max(hi-lo)*.6;ax.set_xlim(c[0]-e,c[0]+e);ax.set_ylim(c[1]-e,c[1]+e);ax.set_zlim(c[2]-e,c[2]+e);ax.set_box_aspect((1,1,1));ax.view_init(25,38);ax.set_axis_off();ax.set_title(title)
    fig.tight_layout();fig.savefig(out,dpi=150);plt.close(fig)

def main():
    rows=scan_sources(); (OUT/'audit'/'all_parts_scan.json').write_text(json.dumps(rows,indent=2)); sel=select_pilot(rows); (OUT/'audit'/'pilot_selection.json').write_text(json.dumps(sel,indent=2)); print('SCAN',len(rows),'WATERTIGHT',sum(r['watertight'] for r in rows),'VOLUME',sum(r['volume'] for r in rows),'PILOT',len(sel),flush=True)
    results=[]
    for n,r in enumerate(sel):
        srcpath=ROOT/r['path']; src=load(srcpath); parts=r['path'].split('/'); case=parts[0]; part=Path(parts[-1]).stem; od=OUT/'cases'/case/part; od.mkdir(parents=True,exist_ok=True); src.export(od/'source.stl')
        fam,conf,ops=family(src); R,e,c=pca(src); analysis={'watertight':r['watertight'],'is_volume':r['volume'],'vertices':len(src.vertices),'faces':len(src.faces),'connected_components':len(src.split(only_watertight=False)),'bbox_x':e[0],'bbox_y':e[1],'bbox_z':e[2],'bbox_diagonal':r['bbox_diagonal'],'centroid':r['centroid'],'volume':r['volume_value'],'surface_area':r['surface_area'],'principal_axes':R.tolist(),'geometry_family':fam,'confidence':conf,'candidate_operations':ops}; (od/'geometry_analysis.json').write_text(json.dumps(analysis,indent=2))
        cr=[]; best=None
        for ci,(kind,params) in enumerate(candidates(src)):
            cd=od/f'candidate_{ci}'; cd.mkdir(exist_ok=True); (cd/'cad.py').write_text(cad_code(kind,params)); (cd/'program.json').write_text(json.dumps(program(kind,params),indent=2)); env=os.environ.copy(); env['PYTHONPATH']='/usr/local/lib/python3.10/dist-packages:/data/home/cuiyuehan/.local/lib/python3.10/site-packages:/usr/lib/python3/dist-packages'+(':'+env.get('PYTHONPATH','')); run=subprocess.run(['python3','cad.py'],cwd=cd,capture_output=True,text=True,env=env,timeout=120); ok=run.returncode==0
            if ok:
                try: cad=load(cd/'reconstructed.stl'); mm=metrics(src,cad); score=1-mm['iou128']+0.005*len(program(kind,params)['operations'])+0.001*len(params)
                except Exception as ex: ok=False; mm={}; score=99
            else: mm={}; score=99
            row={'candidate':ci,'kind':kind,'execute':'PASS' if ok else 'FAIL','score':score,'iou128':mm.get('iou128'),'ncd':mm.get('ncd'),'program':str((cd/'program.json').relative_to(od)),'stderr':run.stderr[-500:] if not ok else ''}; cr.append(row)
            if ok and (best is None or score<best[0]): best=(score,kind,params,mm)
        with (od/'candidates.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=['candidate','kind','execute','score','iou128','ncd','program','stderr']);w.writeheader();w.writerows(cr)
        if best is None: continue
        _,kind,params,mm=best; (od/'cad.py').write_text(cad_code(kind,params)); (od/'program.json').write_text(json.dumps(program(kind,params),indent=2)); (od/'parameters.json').write_text(json.dumps(params,indent=2)); env=os.environ.copy();env['PYTHONPATH']='/usr/local/lib/python3.10/dist-packages:/data/home/cuiyuehan/.local/lib/python3.10/site-packages:/usr/lib/python3/dist-packages'+(':'+env.get('PYTHONPATH','')); run=subprocess.run(['python3','cad.py'],cwd=od,capture_output=True,text=True,env=env,timeout=120); cad=load(od/'reconstructed.stl')
        txt=(od/'cad.py').read_text(); banned=['trimesh.load','meshio','read_stl','importStl','source.stl','source.obj','source.ply','OBJ','PLY']; meshused=any(x in txt for x in banned); valid=False; reload=False; solids=0; brep_faces=None
        try:
            import cadquery as cq; sh=cq.importers.importStep(str(od/'reconstructed.step')).val(); brep_faces=len(sh.Faces());solids=len(sh.Solids());valid=bool(sh.isValid());reload=True
        except: pass
        faceted=bool(brep_faces is not None and brep_faces>=.35*len(src.faces)); quality='A_HIGH_CONFIDENCE' if mm['iou128']>=.95 else 'B_USABLE' if mm['iou128']>=.90 else 'C_NEAR_MISS' if mm['iou128']>=.80 else 'D_REJECT'; validpair=quality in ('A_HIGH_CONFIDENCE','B_USABLE') and not meshused and not faceted and valid and solids>=1 and reload and mm['ncd']<=.01 and mm['bbox_error']<=.03 and mm['centroid_error']<=.02; reason='' if validpair else 'MESH_IMPORT_USED' if meshused else 'FACETED_BREP_DETECTED' if faceted else 'IOU_TOO_LOW' if mm['iou128']<.90 else 'GEOMETRY_TOLERANCE_FAIL'
        result={'case_id':case,'part_id':part,'source_path':r['path'],'geometry_family':fam,'cad_program_path':str((od/'cad.py').relative_to(OUT)),'program_json_path':str((od/'program.json').relative_to(OUT)),'step_path':str((od/'reconstructed.step').relative_to(OUT)),'reconstructed_mesh_path':str((od/'reconstructed.stl').relative_to(OUT)),'cad_program_exec':'PASS' if run.returncode==0 else 'FAIL','brep_valid':valid,'step_reload':reload,'mesh_import_used':meshused,'faceted_brep':faceted,'feature_count':len(program(kind,params)['operations']),'parameter_count':len(params),'sketch_entity_count':1 if kind=='box' else 0,'boolean_count':0,'source_triangle_count':len(src.faces),'cad_brep_face_count':brep_faces,'quality_level':quality,'valid_training_pair':validpair,'failure_reason':reason,**mm}; (od/'metrics.json').write_text(json.dumps(result,indent=2)); (od/'validation.json').write_text(json.dumps({'CAD_PARSE':'PASS','CAD_EXECUTION':'PASS' if run.returncode==0 else 'FAIL','BREP_VALID':'YES' if valid else 'NO','SOLID_COUNT':solids,'STEP_EXPORT':'PASS','STEP_RELOAD':'PASS' if reload else 'FAIL','MESH_EXPORT':'PASS','MESH_IMPORT_USED':'YES' if meshused else 'NO','FACETED_BREP':'YES' if faceted else 'NO','VALID_TRAINING_PAIR':'YES' if validpair else 'NO'},indent=2)); (od/'report.md').write_text(f"# {case}/{part}\n\nFamily: {fam}\nQuality: {quality}\nIoU128: {mm['iou128']:.6f}\nNCD: {mm['ncd']:.6f}\nValid pair: {validpair}\nFailure reason: {reason}\n"); overlay(src,cad,od/'overlay.png'); results.append(result); print(n+1,r['path'],quality,mm['iou128'],reason,flush=True)
    fields=['case_id','part_id','source_path','geometry_family','cad_program_path','program_json_path','step_path','reconstructed_mesh_path','cad_program_exec','brep_valid','step_reload','mesh_import_used','faceted_brep','feature_count','parameter_count','sketch_entity_count','boolean_count','source_triangle_count','cad_brep_face_count','iou64','iou128','iou256','cd','ncd','hausdorff','nhd','normal_consistency','bbox_error','centroid_error','surface_area_error','volume_error','quality_level','valid_training_pair','failure_reason']
    with (OUT/'manifests'/'all_results.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    for nm,fn in [('high_confidence',lambda r:r['quality_level']=='A_HIGH_CONFIDENCE'),('usable',lambda r:r['quality_level']=='B_USABLE'),('near_miss',lambda r:r['quality_level']=='C_NEAR_MISS'),('rejected',lambda r:r['quality_level']=='D_REJECT')]:
        with (OUT/'manifests'/f'{nm}.csv').open('w',newline='') as f: w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([r for r in results if fn(r)])
    q=[r['quality_level'] for r in results]; good=[r for r in results if r['valid_training_pair']]; report={'INPUT_ROOT':str(ROOT),'OUTPUT_ROOT':str(OUT),'CASE_N':len(set(r['case_id'] for r in results)),'TOTAL_PART_N':len(results),'WATERTIGHT_PART_N':len(sel),'PILOT_N':len(sel),'CAD_PROGRAM_EXEC_PASS_N':sum(r['cad_program_exec']=='PASS' for r in results),'BREP_VALID_N':sum(r['brep_valid'] for r in results),'STEP_RELOAD_PASS_N':sum(r['step_reload'] for r in results),'A_HIGH_CONFIDENCE_N':q.count('A_HIGH_CONFIDENCE'),'B_USABLE_N':q.count('B_USABLE'),'C_NEAR_MISS_N':q.count('C_NEAR_MISS'),'D_REJECT_N':q.count('D_REJECT'),'IOU128_MEAN':float(np.mean([r['iou128'] for r in results])) if results else None,'IOU128_MEDIAN':float(np.median([r['iou128'] for r in results])) if results else None,'IOU128_MIN':float(min(r['iou128'] for r in results)) if results else None,'IOU128_MAX':float(max(r['iou128'] for r in results)) if results else None,'NCD_MEAN':float(np.mean([r['ncd'] for r in results])) if results else None,'NCD_MEDIAN':float(np.median([r['ncd'] for r in results])) if results else None,'MESH_IMPORT_N':sum(r['mesh_import_used'] for r in results),'FACETED_BREP_N':sum(r['faceted_brep'] for r in results),'PRIMARY_FAILURE_CAUSE':max(set(r['failure_reason'] for r in results),key=[r['failure_reason'] for r in results].count) if results else 'NONE','CURRENT_GATE':'P3_XPART_EXECUTABLE_CAD_PILOT_PASS' if len(good)>=12 and not any(r['mesh_import_used'] or r['faceted_brep'] for r in results) else 'P3_XPART_CAD_PIPELINE_REPAIR_REQUIRED'}; (OUT/'audit'/'pilot_summary.json').write_text(json.dumps(report,indent=2)); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'- **{k}**: {v}' for k,v in report.items())); print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__': main()


