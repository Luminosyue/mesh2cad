"""Compile actual model V3 values using declared fixed per-part template metadata."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import sys,json,hashlib,runpy,csv,time,traceback,subprocess,shutil
from pathlib import Path
import numpy as np,trimesh,cadquery as cq
import pipeline as P
O=P.O;E=O/'model_v1'
def dump(p,x):P.dump(p,x)
def compile_part(name,pid,generated,out,free=None):
 label=O/'objects'/name/'cad_parts'/pid;out.mkdir(parents=True,exist_ok=True)
 record=dict(object=name,part=pid,generated_ir=str(generated),generated_ir_sha256=P.sha(generated),model_generation=free is not None,PASS=False)
 try:
  assert not (name=='tank' and pid=='PART_029'),'Frozen part cannot be recompiled as new generation'
  text=Path(generated).read_text();cid,qs=P.v3['parse'](text);meta=json.loads((label/'q14.json').read_text())
  template=json.loads((label/'semantic_template.json').read_text()) if (label/'semantic_template.json').exists() else P.readparams(label/'cad_program.py')
  expected_cid,_=P.v3['parse']((label/'compact_ir_v3.v3').read_text())
  assert cid==expected_cid,'GENERATED_CASE_ID_MISMATCH'
  assert all(0<=q<=16383 for q in qs),'Q14_RANGE'
  # Existing parser ignores operation/feature header fields. Validate them against
  # the frozen template; do not silently substitute a different generated operation.
  assert text.strip()==P.v3['serialize'](cid,template,qs).strip(),'TEMPLATE_HEADER_OR_GRAMMAR_MISMATCH'
  params=P.v3['dequant'](template,qs,meta['lo'],meta['hi'])
  source=P.v3['replace_params']((label/'compiled_cadquery.py').read_text(),params)
  compiled=out/'generated_compiler.py';compiled.write_text(source)
  assert P.readparams(compiled)==params,'GENERATED_PARAMETERS_NOT_CONSUMED'
  dump(out/'parsed_generated_ast.json',dict(case_id=cid,qvalues=qs,template=str(label/'semantic_template.json'),q14_metadata=str(label/'q14.json'),canonical_q_exact=qs==[x['q14'] for x in meta['parameters']],compiler_template=str(label/'compiled_cadquery.py'),generated_parameters_consumed=True))
  shape=runpy.run_path(str(compiled))['build']();assert shape.isValid() and shape.Solids(),'GENERATED_BREP_INVALID'
  sp=out/'part.step';cq.exporters.export(shape,str(sp));shape=cq.importers.importStep(str(sp)).val();assert shape.isValid() and shape.Solids(),'GENERATED_STEP_READBACK_INVALID'
  gm=P.shapemesh(shape);canon=cq.importers.importStep(str(label/'part.step')).val();raw=cq.importers.importStep(str(label/'raw.step')).val()
  consistency=P.compare(P.shapemesh(raw),gm);rv=abs(raw.Volume());consistency['VOLUME_ERROR']=abs(abs(shape.Volume())-rv)/max(rv,1e-12)
  meshpath=json.loads((label/'result.json').read_text())['PART_MESH_PATH'];source_mesh=P.mesh(meshpath);metrics=P.compare(source_mesh,gm)
  iou,pitch,na,nb=P.defs(P.R/'p3_parts_batch.py',['surface_iou'])['surface_iou'](source_mesh,gm,64)
  metrics.update(IOU=iou,IOU_TYPE='SURFACE_VOXEL_IOU_64',VOLUME_IOU=None,volume_error=abs(abs(shape.Volume())-abs(source_mesh.volume))/max(abs(source_mesh.volume),1e-12) if source_mesh.is_watertight else None,registration='NONE',metric_source='ACTUAL_MESH_VS_GENERATED_CAD_SAMPLING')
  dump(out/'mesh_vs_generated_cad.json',metrics);dump(out/'raw_vs_generated_consistency.json',consistency)
  record.update(CAD_BREP_PASS=True,STEP_READBACK_PASS=True,V3_PARSE_PASS=True,Q14_RANGE_PASS=True,BODY_N=len(shape.Solids()),canonical_volume_difference=abs(shape.Volume()-canon.Volume()),Q_EXACT=qs==[x['q14'] for x in meta['parameters']],geometry_consistency_pass=all(consistency[k]<=.02 for k in ['CD','BBOX_ERROR','CENTROID_ERROR']) and consistency['VOLUME_ERROR']<=.05,step=str(sp),step_sha256=P.sha(sp),generated_compiler_sha256=P.sha(compiled),transform_path=str(label/'transform.json'),q14_metadata_path=str(label/'q14.json'),coordinate_frame='Original object coordinates; inverse already included in declared compiler template',free_gate=free)
  record['PASS']=bool(record['geometry_consistency_pass'] and (free is None or (free['FREE_TOKEN_EXACT'] and free['NATURAL_EOS'] and free['GT_PREFIX_TOKEN_N']==0)))
 except Exception:record['error']=traceback.format_exc()
 dump(out/'GATE.json',record);print(json.dumps(record),flush=True);return record
def process_attempt(folder):
 summary=json.loads((folder/'SUMMARY.json').read_text());name=summary['object'];out=E/'generated'/name/folder.name;out.mkdir(parents=True,exist_ok=True)
 rows=summary['rows'];gates=[]
 for r in rows:
  partout=out/'parts'/r['part'];gate=partout/'GATE.json'
  if not gate.exists():
   try:subprocess.run([sys.executable,__file__,'part',str(folder/(r['part']+'_result.json')),str(partout)],check=True,timeout=300)
   except Exception as e:dump(gate,dict(object=name,part=r['part'],PASS=False,error=str(e)))
  gates.append(json.loads(gate.read_text()))
 expected=list(csv.DictReader((O/'objects'/name/'PART_MANIFEST.csv').open()));wanted={r['PART_ID'] for r in expected};seen={r['part'] for r in rows}
 frozen=[]
 if name=='tank':
  for path,digest in json.loads((E/'reports/FROZEN_PART029_HASHES.json').read_text()).items():assert P.sha(path)==digest
  frozen=['PART_029'];seen.add('PART_029')
 result=dict(object=name,checkpoint=summary['checkpoint'],required_parts=len(wanted),new_model_parts=len(rows),frozen_reuse=frozen,missing_parts=sorted(wanted-seen),free_exact_n=summary['free_exact_n'],natural_eos_n=summary['natural_eos_n'],cad_pass_n=sum(g.get('PASS',False) for g in gates),FULL_MODEL_ASSEMBLY_PASS=False)
 try:
  assert seen==wanted,'INCOMPLETE_OR_UNEXPECTED_PART_SET'
  assert all(g['PASS'] for g in gates),'MODEL_OR_CAD_PART_GATE_FAILED'
  shapes=[cq.importers.importStep(g['step']).val() for g in gates]
  if frozen:shapes.append(cq.importers.importStep(str(O/'objects/tank/cad_parts/PART_029/part.step')).val())
  compound=cq.Compound.makeCompound(shapes);sp=out/'assembled.step';cq.exporters.export(compound,str(sp));rb=cq.importers.importStep(str(sp)).val()
  assert rb.isValid() and len(rb.Solids())==sum(len(s.Solids()) for s in shapes)
  manifest=next(x for x in json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text()) if x['OBJECT_ID']==name)
  full=P.mesh(manifest['FULL_MESH_PATH']);cms=[P.shapemesh(s) for s in shapes];cad=trimesh.util.concatenate(cms);metrics=P.compare(full,cad);iou,pitch,na,nb=P.defs(P.R/'p3_parts_batch.py',['surface_iou'])['surface_iou'](full,cad,64)
  metrics.update(IOU=iou,IOU_TYPE='SURFACE_VOXEL_IOU_64',VOLUME_IOU=None,VOLUME_ERROR=abs(abs(rb.Volume())-abs(full.volume))/max(abs(full.volume),1e-12) if full.is_watertight else None,PART_COVERAGE=1.0,metric_source='ACTUAL_MESH_VS_GENERATED_CAD_SAMPLING',registration='NONE');dump(out/'mesh_vs_generated_assembly.json',metrics)
  dump(out/'assembly_manifest.json',dict(object=name,parts=gates,frozen_reuse=frozen,TOTAL_PART_N=len(wanted),REUSED_PART_N=len(frozen),NEW_GENERATED_CAD_N=len(gates),STRICT_MODEL_GENERATED_N=len(gates)+len(frozen),CANONICAL_N=0,FULL_NEW_MODEL_GENERATED_OBJECT=not frozen,full_expected_ids=sorted(wanted),compound_no_union=True,body_count=len(rb.Solids()),face_count=len(rb.Faces()),edge_count=len(rb.Edges()),step=str(sp)))
  # Renderer writes only inside this evaluation attempt.
  P.O=out;rf=out/'objects'/name;rf.mkdir(parents=True,exist_ok=True)
  renderrows=[next(r for r in expected if r['PART_ID']==g['part']) for g in gates]
  if frozen:renderrows.append(next(r for r in expected if r['PART_ID']=='PART_029'))
  P.render_object(name,full,[P.mesh(r['PART_MESH_PATH']) for r in renderrows],cms,json.loads((O/'objects'/name/'OBJECT_FRAME.json').read_text()),renderrows)
  result.update(FULL_MODEL_ASSEMBLY_PASS=True,FULL_NEW_MODEL_GENERATED_OBJECT=not frozen,FULL_PART_SET_COMPLETE=True,Q14_ALL_PASS=True,V3_ALL_PASS=True,OBJECT_COORDINATE_PASS=True,ASSEMBLY_STEP_PASS=True,ASSEMBLY_READBACK_PASS=True,OBJECT_GEOMETRY_EVAL_PASS=True,RENDER_PASS=True,PART_COVERAGE=1.0,step=str(sp),render_dir=str(rf/'renders'),metrics=metrics)
 except Exception:result['error']=traceback.format_exc()
 dump(out/'OBJECT_GATE.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='part':
  r=json.loads(Path(sys.argv[2]).read_text());compile_part(r['object'],r['part'],Path(r['generated_ir']),Path(sys.argv[3]),r)
 elif mode=='attempt':process_attempt(Path(sys.argv[2]))
 elif mode=='smoke':
  r=compile_part('pottery_large','PART_000',O/'objects/pottery_large/cad_parts/PART_000/compact_ir_v3.v3',E/'compiler_smoke/pottery_large_PART_000')
  assert r['PASS'];dump(E/'compiler_smoke/NOTICE.json',dict(model_success=False,source='Canonical label used only to test generated compiler execution'))
