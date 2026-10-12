"""Resumeable object-complete q14 / existing Compact IR V3 / CAD assembly batch."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import ast,json,csv,math,hashlib,shutil,traceback,sys,time,runpy,copy,subprocess,concurrent.futures,signal
import numpy as np
R=Path('/data/home/cuiyuehan/project/mesh2cad'); O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'; S=R/'p3_xpart_open_cases'; CODE=O/'code'
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x))+'\n');q.replace(p)
def csvout(p,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for row in rows for k in row));q=p.with_suffix('.csv.tmp')
 with q.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
 q.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def link(src,dst):
 src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.is_symlink():assert dst.resolve()==src.resolve();return
 if not dst.exists():dst.symlink_to(src)
def defs(path,names,extra=None):
 tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
 ns=dict(math=math,json=json,np=np,Path=Path);ns.update(extra or {});exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
schema=json.loads((R/'ours3/p3_xpart_20case_compact_ir_v3/schema/V3_SCHEMA.json').read_text())
v3=defs(R/'ours3/build_p3_v3.py',['dequant','replace_params','serialize','parse'],dict(OPCODES=schema['operation_codes'],FEATURE_CODES=schema['feature_codes']))
quant=defs(R/'ours3/work_prepare_p3.py',['floats','qtree'])
def readparams(p):
 for n in ast.parse(Path(p).read_text(encoding='utf-8-sig')).body:
  if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='PARAMETERS' for a in n.targets):return json.loads(ast.literal_eval(n.value.args[0]))
 raise ValueError('No PARAMETERS')
def normalize_params(p,frame):
 p=copy.deepcopy(p);factor=frame['scale']/p['construction_scale']
 def scale(x):
  if isinstance(x,dict):return {k:scale(v) for k,v in x.items()}
  if isinstance(x,list):return [scale(v) for v in x]
  return x*factor if isinstance(x,float) else x
 for key in ['features','profile','center_xy']:
  if key in p:p[key]=scale(p[key])
 p['center']=((np.array(p['center'])-frame['center'])*frame['scale']).tolist();p['construction_scale']=1
 return p
def mesh(p):
 import trimesh
 return trimesh.load(str(p),force='mesh',process=False)
def shapemesh(s,tol=.0005):
 import trimesh
 v,f=s.tessellate(tol,.1);return trimesh.Trimesh([[x.x,x.y,x.z] for x in v],f,process=False)
def surface_sample(m,n=20000,seed=0):
 # Exact project area-weighted surface sampler.
 sys.path.insert(0,str(R/'scripts'))
 from geometry_pack_v1.surface import sample_surface_uniform
 return sample_surface_uniform(m.vertices,m.faces,n,seed)[0]
def compare(a,b,seed=0):
 from scipy.spatial import cKDTree
 pa=surface_sample(a,20000,seed);pb=surface_sample(b,20000,seed);da=cKDTree(pb).query(pa)[0];db=cKDTree(pa).query(pb)[0];diag=float(np.linalg.norm(a.extents))
 return dict(CD=float((da.mean()+db.mean())*.5/diag),H95=float(np.percentile(np.r_[da,db],95)/diag),BBOX_ERROR=float(np.max(np.abs(a.bounds-b.bounds))/diag),CENTROID_ERROR=float(np.linalg.norm(a.centroid-b.centroid)/diag))
def prepare():
 manifest=json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text());hashes=json.loads((O/'manifests/SHA256.json').read_text())
 for name,h in hashes.items():assert sha(O/'manifests'/name)==h
 for c in manifest:
  folder=O/'objects'/c['OBJECT_ID'];f=json.loads((folder/'OBJECT_FRAME.json').read_text());rs=list(csv.DictReader((folder/'PART_MANIFEST.csv').open()));vals=[]
  for row in rs:
   if row['HISTORICAL_CASE_ID'] or not row.get('CAD_PATH'):continue
   vals += [v for _,v in quant['floats'](normalize_params(readparams(row['CAD_PATH']),f))]
  f.update(common_q14_lo=min([-1.0]+vals),common_q14_hi=max([1.0]+vals),new_program_output_frame='FULL_OBJECT_BBOX_NORMALIZED',q14_scope='Existing q14 formula unchanged; all new parts normalized by the same full-object bbox center/scale, using a shared range. Existing q14/V3 parts retain original object coordinates.',normalization_recipe='Scale all feature/profile/center_xy dimensions by object_scale/construction_scale; center=(center-object_center)*object_scale; construction_scale=1. Restore via shared inverse matrix after compilation.')
  dump(folder/'OBJECT_FRAME.json',f)
  link(c['FULL_MESH_PATH'],folder/('full_mesh'+Path(c['FULL_MESH_PATH']).suffix))
  for row in rs:
   if row['PART_MESH_PATH']:link(row['PART_MESH_PATH'],folder/'parts'/(row['PART_ID']+Path(row['PART_MESH_PATH']).suffix))
 dump(O/'reports/EXECUTION_CONTRACT.json',dict(q14_source=str(R/'ours3/work_prepare_p3.py'),q14_source_sha256=sha(R/'ours3/work_prepare_p3.py'),v3_source=str(R/'ours3/build_p3_v3.py'),v3_source_sha256=sha(R/'ours3/build_p3_v3.py'),new_training=False,tank029_frozen=True,part_geometry_tolerances=dict(CD=.02,BBOX_ERROR=.02,CENTROID_ERROR=.02,relative_volume_error=.05),part_geometry_note='Explicit raw-versus-q14 consistency gates, not object reconstruction accuracy thresholds.',object_metrics=dict(CD='Existing unified CAD evaluation V2: 20000 area-weighted surface samples, seed 0, symmetric mean NN divided by full input bbox diagonal',IOU='Existing P3 surface_voxel_iou_64; volume IoU undefined for open full inputs and reported separately if available',chamfer_protocol=str(R/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/protocol/UNIFIED_CAD_EVAL_PROTOCOL_V2.json'),iou_source=str(R/'p3_parts_batch.py')),max_repairs=3,min_free_disk_gb=15,parallel_objects=2))
 return manifest
def process_part(name,pid):
 import cadquery as cq
 folder=O/'objects'/name;row=next(x for x in csv.DictReader((folder/'PART_MANIFEST.csv').open()) if x['PART_ID']==pid);out=folder/'cad_parts'/pid;out.mkdir(parents=True,exist_ok=True)
 record=out/'result.json'
 if record.exists() and json.loads(record.read_text()).get('PASS'):return
 rr=dict(OBJECT_ID=name,PART_ID=pid,PART_MESH_PATH=row['PART_MESH_PATH'],CAD_SOURCE='REUSED_EXISTING',SOURCE_CLASS=row['SOURCE'],RAW_CAD_PASS=False,Q14_PASS=False,V3_PASS=False,STEP_PASS=False,TRANSFORM_PASS=False,PART_GEOMETRY_PASS=False,ASSEMBLED=False,FAILURE_REASON='',PASS=False,QUALITY_STATUS=row['QUALITY_STATUS'])
 try:
  rawpath=Path(row['CAD_PATH']);rawstep=Path(row['STEP_PATH']);link(rawpath,out/'cad_program.py');link(rawstep,out/'raw.step');sourcehash=sha(rawpath)
  raw=cq.importers.importStep(str(rawstep)).val();assert raw.isValid() and raw.Solids(),'RAW_BREP_INVALID';rr['RAW_CAD_PASS']=True
  frame=json.loads((folder/'OBJECT_FRAME.json').read_text());rawparams=readparams(rawpath);cid=row['HISTORICAL_CASE_ID'];strict=name=='tank' and pid=='PART_029'
  if cid:
   base=R/'ours3/p3_xpart_20case_compact_ir_v1';base3=R/'ours3/p3_xpart_20case_compact_ir_v3';generated=R/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1/final_eval_v1'
   vp=generated/f'generated_ir/{cid}.v3' if strict else base3/f'compact_ir_v3/{cid}.v3';sp=generated/f'step/{cid}.step' if strict else base3/f'step_v3/{cid}.step'
   for src,dst in [(base/f'quantization/{cid}.json','q14.json'),(vp,'compact_ir_v3.v3'),(base3/f'compiler_v3/{cid}.py','compiled_cadquery.py'),(sp,'part.step')]:link(src,out/dst)
   qm=json.loads((out/'q14.json').read_text());expected=[x['q14'] for x in qm['parameters']]
   transport=vp.read_text();payload=transport.removesuffix('<|eot_id|>').rstrip()+'\n';pcid,qs=v3['parse'](payload);assert pcid==cid and qs==expected and all(0<=q<=16383 for q in qs),'Q_STREAM_MISMATCH'
   if strict:
    gr=json.loads((generated/f'reports/{cid}_gate.json').read_text());assert gr['free_generation']['natural_eos'] and gr['free_generation']['free_token_exact'] and gr['geometry_equivalence'];assert len(qs)==1529
    link(generated/f'reports/{cid}_gate.json',out/'STRICT_GENERATED_GATE.json');rr['CAD_SOURCE']='MODEL_GENERATED';rr['STRICT_MODEL_GENERATED']=True
   shape=cq.importers.importStep(str(sp)).val();normtype='HISTORICAL_ORIGINAL_OBJECT_COORDINATES';inverse=np.eye(4).tolist()
   frozen={str(p):sha(p) for p in [vp,sp,base/f'quantization/{cid}.json']};dump(out/'FROZEN_SOURCE_HASHES.json',frozen)
  else:
   norm=normalize_params(rawparams,frame);lo,hi=frame['common_q14_lo'],frame['common_q14_hi'];recs=[];dq=quant['qtree'](norm,lo,hi,records=recs);qs=[x['q14'] for x in recs];cid=name+'__'+pid
   text=v3['serialize'](cid,norm,qs);pcid,parsed=v3['parse'](text);assert pcid==cid and parsed==qs and all(0<=q<=16383 for q in qs)
   # Compiler consumes parser output, not a bypass of IR.
   compiled=v3['dequant'](norm,parsed,lo,hi);assert compiled==dq
   dump(out/'q14.json',dict(bits=14,lo=lo,hi=hi,parameters=recs,object_frame=str(folder/'OBJECT_FRAME.json')));(out/'compact_ir_v3.v3').write_text(text)
   dump(out/'semantic_template.json',norm);dump(out/'parsed_ast.json',dict(case_id=pcid,qvalues=parsed,normalization='FULL_OBJECT_BBOX_NORMALIZED',template=str(out/'semantic_template.json')))
   source=v3['replace_params'](rawpath.read_text(encoding='utf-8-sig'),compiled)
   # Shared object inverse is explicit; construction program/operations unchanged.
   source+='\n_original_normalized_build = build\ndef build():\n    return _original_normalized_build().scale('+repr(1/frame['scale'])+').translate('+repr(tuple(frame['center']))+')\n'
   source=source.replace('if __name__=="__main__":','if False:')
   repairs=[]
   for attempt in range(4):
    try:
     candidate=source
     if attempt>=1:
      helper='\ndef _q14_unique(points):\n    result=[]\n    for point in points:\n        if not result or sum((a-b)**2 for a,b in zip(point,result[-1]))>1e-24: result.append(point)\n    if len(result)>1 and sum((a-b)**2 for a,b in zip(result[0],result[-1]))<=1e-24: result.pop()\n    return result\n'
      candidate=candidate.replace('def sketch_wire(points, z, smooth=False):',helper+'\ndef sketch_wire(points, z, smooth=False):\n    if not isinstance(points,dict): points=_q14_unique(points)')
     if attempt>=2:candidate=candidate.replace('periodic=True)','periodic=True,tol=1e-9)')
     if attempt>=3:
      helper='\ndef _condition_q14(x):\n    if isinstance(x,dict): return {k:_condition_q14(v) for k,v in x.items()}\n    if isinstance(x,list): return [_condition_q14(v) for v in x]\n    return x*1000 if isinstance(x,float) else x\nfor _key in ["features","profile","center_xy"]:\n    if _key in PARAMETERS: PARAMETERS[_key]=_condition_q14(PARAMETERS[_key])\nPARAMETERS["construction_scale"]=1000\n'
      candidate+=helper
     candidate+='\nif __name__=="__main__":\n    result=build()\n    result.exportStep(str(Path(__file__).with_suffix(".step")))\n'
     if attempt:dump(out/'repairs.json',repairs)
     print('CAD_CONSTRUCTION_ATTEMPT',attempt,flush=True)
     (out/'compiled_cadquery.py').write_text(candidate);ns=runpy.run_path(str(out/'compiled_cadquery.py'));shape=ns['build']();assert shape.isValid() and shape.Solids(),'Q14_BREP_INVALID'
     if attempt:repairs[-1]['result']='PASS'
     break
    except Exception as e:
     if attempt:repairs[-1]['result']=type(e).__name__+': '+str(e)
     if attempt==3:dump(out/'repairs.json',repairs);raise
     repairs.append(dict(attempt=attempt+1,failure_type=type(e).__name__,failure=str(e),change=['Remove consecutive exactly coincident quantized spline/polyline points at CAD construction only; q stream unchanged','Use explicit spline tolerance 1e-9 in normalized object units','Condition CAD kernel construction dimensions by 1000 with exact inverse scale; q stream unchanged'][attempt],result='PENDING'));dump(out/'repairs.json',repairs)
   dump(out/'repairs.json',repairs)
   cq.exporters.export(shape,str(out/'part.step'));shape=cq.importers.importStep(str(out/'part.step')).val();normtype='FULL_OBJECT_BBOX_NORMALIZED';inverse=frame['inverse_matrix']
  rr['Q14_PASS']=True;rr['V3_PASS']=True;assert shape.isValid() and shape.Solids(),'STEP_READBACK_INVALID';rr['STEP_PASS']=True
  rm=shapemesh(raw);qmsh=shapemesh(shape);metrics=compare(rm,qmsh);rv=abs(raw.Volume());sv=abs(shape.Volume());metrics.update(RAW_VOLUME=rv,Q14_VOLUME=sv,VOLUME_ERROR=abs(sv-rv)/max(rv,1e-12),RAW_BODY_N=len(raw.Solids()),Q14_BODY_N=len(shape.Solids()),RAW_AREA=raw.Area(),Q14_AREA=shape.Area(),TOPOLOGY_BODY_COUNT_MATCH=len(raw.Solids())==len(shape.Solids()))
  geompass=all(metrics[k]<=.02 for k in ['CD','BBOX_ERROR','CENTROID_ERROR']) and metrics['VOLUME_ERROR']<=.05
  # Existing strict artifacts are immutable; report raw quantization differences honestly.
  rr.update(PART_GEOMETRY_PASS=geompass,TRANSFORM_PASS=True,BODY_N=len(shape.Solids()),Q_COUNT=len(qs),NORMALIZATION=normtype)
  dump(out/'geometry_report.json',metrics)
  dump(out/'transform.json',dict(program_frame=normtype,inverse_matrix=inverse,object_space_ready=True,source_local_center=rawparams['center'],source_construction_scale=rawparams['construction_scale'],source_basis=rawparams.get('basis'),original_input_mesh_modified=False,registration='NONE'))
  dump(out/'provenance.json',dict(cad_source=rr['CAD_SOURCE'],reused_existing=True,new_cad_generation=False,new_q14_v3=not bool(row['HISTORICAL_CASE_ID']),source_program=str(rawpath),source_program_sha256=sourcehash,source_step=str(rawstep),source_step_sha256=sha(rawstep),original_reconstruction_status=row['QUALITY_STATUS'],strict_model_generated=strict,compiler='Exact extracted existing V3 serialize/parse/dequant/replace_params',grammar_modified=False,object_normalization=normtype))
  rr['PASS']=bool(geompass);rr['FAILURE_REASON']='' if geompass else 'RAW_VS_Q14_GEOMETRY_TOLERANCE'
 except Exception as e:rr['FAILURE_REASON']=type(e).__name__+': '+str(e);rr['TRACEBACK']=traceback.format_exc()
 dump(record,rr);print(name,pid,rr['PASS'],rr['FAILURE_REASON'],flush=True)
def render_object(name,full,partmeshes,cadmeshes,frame,rows):
 import vtk,colorsys
 from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
 from PIL import Image,ImageDraw,ImageFont
 out=O/'objects'/name/'renders';out.mkdir(exist_ok=True)
 center=np.array(frame['center']);extent=1/frame['scale'];colors=[colorsys.hsv_to_rgb((i*.61803398875)%1,.40,.79) for i in range(len(rows))]
 up=(0,0,1) if name in ['fire_truck','mini_excavator','android_figure_orange','baby_car','birdhouse'] else (0,1,0);view=(2.5,1.8,2.8)
 if name=='aroma_stainless_steel_milk_frother_2_cup':up=(0,0,-1);view=(2.5,1.8,-2.8)
 dump(out/'CAMERA_SETTINGS.json',dict(view_position=view,view_up=up,render_only=True,assembly_transform_changed=False,all_panels_share_camera=True))
 def render(ms,cols,path,overlay=False,explode=False):
  ren=vtk.vtkRenderer();ren.SetBackground(.97,.978,.986)
  for j,(m,col) in enumerate(zip(ms,cols)):
   xyz=(np.asarray(m.vertices)-center)/extent
   if explode:xyz=xyz+((m.bounds.mean(0)-center)/extent)*.8
   p=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(xyz,deep=True));p.SetPoints(v);cells=vtk.vtkCellArray();cells.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces),3),m.faces].ravel().astype(np.int64),deep=True));p.SetPolys(cells)
   normals=vtk.vtkPolyDataNormals();normals.SetInputData(p);normals.SetFeatureAngle(55);normals.SplittingOn();normals.Update();mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper);prop=actor.GetProperty();prop.SetColor(*col);prop.SetAmbient(.28);prop.SetDiffuse(.72);prop.SetSpecular(.25);prop.SetSpecularPower(28);prop.EdgeVisibilityOff()
   if overlay and j==0:prop.SetOpacity(.25)
   ren.AddActor(actor)
  cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetPosition(*view);cam.SetViewUp(*up);cam.SetFocalPoint(0,0,0);ren.ResetCamera();cam.Zoom(1.05);ren.ResetCameraClippingRange();win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1600,1200);win.SetMultiSamples(4);win.AddRenderer(ren);win.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.Update();a=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(1200,1600,3);im=Image.fromarray(a[::-1].copy());win.Finalize();im.save(path)
 render([full],[(.56,.62,.69)],out/'full_mesh.png');render(partmeshes,colors,out/'mesh_parts.png');render(cadmeshes,colors,out/'cad_parts.png');render(cadmeshes,[(.53,.65,.76)]*len(cadmeshes),out/'assembled_cad.png');render([full]+cadmeshes,[(.88,.36,.25)]+[(.28,.57,.75)]*len(cadmeshes),out/'overlay.png',overlay=True);render(cadmeshes,colors,out/'exploded.png',explode=True)
 link(out/'mesh_parts.png',out/'all_mesh_parts.png');link(out/'cad_parts.png',out/'all_cad_parts.png')
 if name=='tank':
  highlight=[(.96,.40,.08) if r['PART_ID']=='PART_029' else (.70,.75,.80) for r in rows];p=out/'part_id_view.png';render(cadmeshes,highlight,p,explode=True);im=Image.open(p);dr=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28);dr.text((36,32),'PART_029 | Existing strict generated part',font=font,fill=(30,40,50));dr.text((36,72),'q-stream 1529/1529 exact | Other parts: reused canonical reconstruction',font=font,fill=(30,40,50));im.save(p)
def assemble(name):
 import cadquery as cq,trimesh
 folder=O/'objects'/name;rows=list(csv.DictReader((folder/'PART_MANIFEST.csv').open()));results=[json.loads((folder/'cad_parts'/r['PART_ID']/'result.json').read_text()) for r in rows];frame=json.loads((folder/'OBJECT_FRAME.json').read_text());c=next(c for c in json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text()) if c['OBJECT_ID']==name)
 result=dict(OBJECT_ID=name,CATEGORY=c['CATEGORY'],PART_N=len(rows),VALID_CAD_PART_N=sum(r['PASS'] for r in results),Q14_PASS_N=sum(r['Q14_PASS'] for r in results),V3_PASS_N=sum(r['V3_PASS'] for r in results),ASSEMBLED_PART_N=0,PART_COVERAGE=0,OBJECT_COORDINATE_PASS=all(r['TRANSFORM_PASS'] for r in results),ASSEMBLY_STEP_PASS=False,ASSEMBLY_READBACK_PASS=False,OBJECT_GEOMETRY_EVAL_PASS=False,RENDER_PASS=False,CD=None,IOU=None,BBOX_ERROR=None,CENTROID_ERROR=None,ASSEMBLY_TYPE='COMPOUND_MULTI_BODY',FULL_ASSEMBLY_PASS=False,DEMO_PATH='',FAILURE_REASON='')
 try:
  assert all(r['PASS'] for r in results),'FAILED_PARTS: '+','.join(r['PART_ID'] for r in results if not r['PASS'])
  out=folder/'assembly';out.mkdir(exist_ok=True);shapes=[cq.importers.importStep(str(folder/'cad_parts'/r['PART_ID']/'part.step')).val() for r in rows];expected=sum(len(s.Solids()) for s in shapes);compound=cq.Compound.makeCompound(shapes);path=out/'assembled.step';cq.exporters.export(compound,str(path));rb=cq.importers.importStep(str(path)).val();assert rb.isValid() and len(rb.Solids())==expected,'ASSEMBLY_READBACK_BODY_MISMATCH'
  result.update(ASSEMBLED_PART_N=len(rows),PART_COVERAGE=1.,ASSEMBLY_STEP_PASS=True,ASSEMBLY_READBACK_PASS=True,BODY_N=len(rb.Solids()),FACE_N=len(rb.Faces()),EDGE_N=len(rb.Edges()))
  dump(out/'assembly_manifest.json',dict(object_id=name,assembly_type='COMPOUND_MULTI_BODY',boolean_union=False,part_identity_preserved_in_manifest=True,TOTAL_PART_N=len(rows),REUSED_PART_N=len(rows),NEW_GENERATED_CAD_N=0,STRICT_MODEL_GENERATED_N=sum(r.get('STRICT_MODEL_GENERATED',False) for r in results),CANONICAL_N=sum(not r.get('STRICT_MODEL_GENERATED',False) for r in results),FULL_MODEL_GENERATED_OBJECT=False,BODY_N=len(rb.Solids()),EXPECTED_BODY_N=expected,FACE_N=len(rb.Faces()),EDGE_N=len(rb.Edges()),READBACK_PASS=True,body_count_explanation='A reconstructed part can contain multiple solids; expected body count is the sum of per-part solids, with no union.',parts=[dict(PART_ID=r['PART_ID'],step_path=str(folder/'cad_parts'/r['PART_ID']/'part.step'),source=q['CAD_SOURCE'],body_n=q['BODY_N'],placement=np.eye(4).tolist(),transform_path=str(folder/'cad_parts'/r['PART_ID']/'transform.json')) for r,q in zip(rows,results)]))
  full=mesh(c['FULL_MESH_PATH']);cadmeshes=[shapemesh(s) for s in shapes];cad=trimesh.util.concatenate(cadmeshes);metrics=compare(full,cad)
  ioufn=defs(R/'p3_parts_batch.py',['surface_iou'])['surface_iou'];iou,pitch,na,nb=ioufn(full,cad,64);metrics.update(IOU=iou,IOU_TYPE='SURFACE_VOXEL_IOU_64',IOU_PITCH=pitch,SOURCE_VOXELS=na,CAD_VOXELS=nb,FULL_MESH_WATERTIGHT=bool(full.is_watertight),VOLUME_ERROR=abs(abs(rb.Volume())-abs(full.volume))/max(abs(full.volume),1e-12) if full.is_watertight else None,VOLUME_IOU=None,VOLUME_IOU_NOTE='Not substituted for surface IoU; input mesh may be open; surface IoU follows established P3 protocol.',PART_COVERAGE=1.,registration='NONE')
  dump(folder/'metrics.json',metrics);result.update({k:metrics[k] for k in ['CD','IOU','BBOX_ERROR','CENTROID_ERROR']});result['OBJECT_GEOMETRY_EVAL_PASS']=all(math.isfinite(metrics[k]) for k in ['CD','IOU','BBOX_ERROR','CENTROID_ERROR'])
  partmeshes=[mesh(r['PART_MESH_PATH']) for r in rows];render_object(name,full,partmeshes,cadmeshes,frame,rows);result.update(RENDER_PASS=True,DEMO_PATH=str(folder/'renders/assembled_cad.png'))
  for r in results:r['ASSEMBLED']=True;dump(folder/'cad_parts'/r['PART_ID']/'result.json',r)
  result['FULL_ASSEMBLY_PASS']=all(result[k] for k in ['OBJECT_COORDINATE_PASS','ASSEMBLY_STEP_PASS','ASSEMBLY_READBACK_PASS','OBJECT_GEOMETRY_EVAL_PASS','RENDER_PASS']);(folder/'DONE').write_text('PASS\n')
 except Exception as e:result['FAILURE_REASON']=str(e);result['TRACEBACK']=traceback.format_exc()
 dump(folder/'OBJECT_RESULT.json',result);print('OBJECT',name,result['FULL_ASSEMBLY_PASS'],result['FAILURE_REASON'],flush=True)
def run_object(name):
 folder=O/'objects'/name
 if (folder/'DONE').exists():return
 free=shutil.disk_usage('/data').free/1e9;dump(folder/'disk_check.json',dict(free_gb=free,min_gb=15,timestamp=time.time()))
 if free<15:raise RuntimeError('DISK_GUARD: free GB < 15')
 rows=list(csv.DictReader((folder/'PART_MANIFEST.csv').open()))
 for r in rows:
  pid=r['PART_ID'];dest=folder/'cad_parts'/pid;dest.mkdir(parents=True,exist_ok=True)
  if (dest/'result.json').exists():continue
  dump(folder/'CURRENT.json',dict(part=pid,time=time.time()))
  with (dest/'execution.log').open('a') as log:
   try:subprocess.run([sys.executable,str(__file__),'part',name,pid],stdout=log,stderr=log,timeout=240,check=True)
   except Exception as e:
    if not (dest/'result.json').exists():dump(dest/'result.json',dict(OBJECT_ID=name,PART_ID=pid,PART_MESH_PATH=r['PART_MESH_PATH'],CAD_SOURCE='REUSED_EXISTING',RAW_CAD_PASS=False,Q14_PASS=False,V3_PASS=False,STEP_PASS=False,TRANSFORM_PASS=False,PART_GEOMETRY_PASS=False,ASSEMBLED=False,PASS=False,FAILURE_REASON='EXECUTION_TIMEOUT_OR_PROCESS_ERROR: '+str(e)))
  update_progress()
 with (folder/'assembly_render.log').open('a') as log:
  try:subprocess.run([sys.executable,str(__file__),'assemble',name],stdout=log,stderr=log,timeout=900,check=True)
  except Exception as e:dump(folder/'OBJECT_RESULT.json',dict(OBJECT_ID=name,PART_N=len(rows),FULL_ASSEMBLY_PASS=False,FAILURE_REASON='ASSEMBLY_PROCESS_ERROR: '+str(e)))
 update_progress()
def update_progress():
 # Multiple workers write only their part records. Serialize shared tables under flock.
 import fcntl
 with (O/'logs/progress.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);manifest=json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text());prs=[];ors=[];current=[]
  for c in manifest:
   d=O/'objects'/c['OBJECT_ID']
   for p in sorted((d/'cad_parts').glob('*/result.json')):prs.append(json.loads(p.read_text()))
   if (d/'OBJECT_RESULT.json').exists():ors.append(json.loads((d/'OBJECT_RESULT.json').read_text()))
   if (d/'CURRENT.json').exists() and not (d/'OBJECT_RESULT.json').exists():current.append(c['OBJECT_ID']+'/'+json.loads((d/'CURRENT.json').read_text())['part'])
  csvout(O/'tables/FULL20_ALL_PART_RESULTS.csv',prs);csvout(O/'tables/FULL20_PIPELINE_OBJECT_RESULTS.csv',ors)
  model_table=O/'tables/FULL20_OBJECT_RESULTS.csv'
  if model_table.exists():
   import csv as _csv
   model_rows=list(_csv.DictReader(model_table.open()))
   done=[r for r in model_rows if r.get('STATUS')=='DONE' and r.get('ASSEMBLY_PASS')=='True']
   partial=[r for r in model_rows if r.get('STATUS')=='PARTIAL_FREE_GENERATED']
   text='FULL MODEL ASSEMBLY:\n'+f'{len(done)}/20\n\nDONE:\n'+'\n'.join('- '+r['OBJECT_ID'] for r in done)+'\n\nPARTIAL:\n'+'\n'.join('- '+r['OBJECT_ID']+' | free='+r.get('FREE_PASS_N','0') for r in partial)+'\n\nCURRENT:\n'+'\n'.join(current)+'\n'
  else:
   ok=sum(r.get('FULL_ASSEMBLY_PASS',False) for r in ors);pok=sum(r.get('PASS',False) for r in prs);failed=[r for r in prs if not r.get('PASS')]
   text=f'FULL OBJECTS:\ncompleted {ok}/20\n\nTOTAL PARTS:\ncompleted {pok}/{sum(c["PART_N"] for c in manifest)} (evaluated {len(prs)})\n\nFULL ASSEMBLY PASS:\n{ok}/20\n\nCURRENT:\n'+ '\n'.join(current)+'\n\nFAILED PARTS:\n'+'\n'.join(r['OBJECT_ID']+'/'+r['PART_ID']+': '+r['FAILURE_REASON'] for r in failed)+'\n'
  q=O/'reports/PROGRESS.md.tmp';q.write_text(text);q.replace(O/'reports/PROGRESS.md');fcntl.flock(lock,fcntl.LOCK_UN)
def main():
 manifest=prepare();priority=['tank','aroma_stainless_steel_milk_frother_2_cup','baby_car','cube','pottery_large','android_figure_orange'];order=priority+[c['OBJECT_ID'] for c in manifest if c['OBJECT_ID'] not in priority and c['OBJECT_ID'] != 'airplane']
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  fut={ex.submit(run_object,n):n for n in order}
  for f in concurrent.futures.as_completed(fut):
   try:f.result()
   except Exception as e:print('OBJECT_DRIVER_ERROR',fut[f],repr(e),flush=True)
 update_progress();print('BATCH_INITIAL_COMPLETE',flush=True)
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'run'
 if mode=='part':process_part(sys.argv[2],sys.argv[3])
 elif mode=='assemble':assemble(sys.argv[2])
 elif mode=='prepare':prepare()
 elif mode=='object':run_object(sys.argv[2])
 else:main()
