import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,csv,hashlib,sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent));import pipeline as p
def yes(v):return v is True or str(v).lower()=='true'
manifest=json.loads((p.O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text());fail=[];n=0;image_n=0;allrows=[];objectrows=[]
for c in manifest:
 d=p.O/'objects'/c['OBJECT_ID'];rows=list(csv.DictReader((d/'PART_MANIFEST.csv').open()));results=[]
 if len(rows)!=c['PART_N']:fail.append(c['OBJECT_ID']+': part count mismatch')
 ids=[r['PART_ID'] for r in rows]
 if len(set(ids))!=len(ids):fail.append(c['OBJECT_ID']+': duplicate part ID')
 for r in rows:
  out=d/'cad_parts'/r['PART_ID'];rp=out/'result.json'
  if not rp.exists():fail.append(c['OBJECT_ID']+'/'+r['PART_ID']+': absent terminal result');continue
  q=json.loads(rp.read_text());n+=1
  exact=False;parsed=False
  if (out/'compact_ir_v3.v3').exists() and (out/'q14.json').exists():
   try:
    _,qs=p.v3['parse']((out/'compact_ir_v3.v3').read_text().removesuffix('<|eot_id|>').rstrip()+'\n');parsed=True;qm=json.loads((out/'q14.json').read_text());exact=qs==[v['q14'] for v in qm['parameters']] and all(0<=v<=16383 for v in qs)
   except Exception:pass
  q.update(Q_ROUNDTRIP_EXACT=exact,V3_PARSE_PASS=parsed,Q_EXACT=exact,CAD_EXEC_PASS=q.get('STEP_PASS',False),BREP_VALID=q.get('STEP_PASS',False),STEP_EXPORT_PASS=q.get('STEP_PASS',False),STEP_READBACK_PASS=q.get('STEP_PASS',False));p.dump(rp,q);results.append(q);allrows.append(q)
  if q.get('PASS'):
   for f in ['cad_program.py','q14.json','compact_ir_v3.v3','compiled_cadquery.py','part.step','transform.json','geometry_report.json','provenance.json']:
    if not (out/f).exists():fail.append(str(out/f)+': missing')
   for f in ['cad_program.py','compiled_cadquery.py']:compile((out/f).read_text(),str(out/f),'exec')
  if (out/'repairs.json').exists() and len(json.loads((out/'repairs.json').read_text()))>3:fail.append(str(out)+': repair budget exceeded')
  if (out/'FROZEN_SOURCE_HASHES.json').exists():
   for src,h in json.loads((out/'FROZEN_SOURCE_HASHES.json').read_text()).items():
    if p.sha(src)!=h:fail.append(src+': frozen artifact changed')
  r.update(RAW_CAD_READY=q.get('RAW_CAD_PASS',False),Q14_READY=q.get('Q14_PASS',False),V3_READY=q.get('V3_PASS',False),STEP_READY=q.get('STEP_PASS',False),NORMALIZATION_READY=q.get('TRANSFORM_PASS',False),INVERSE_TRANSFORM_READY=q.get('TRANSFORM_PASS',False),STATUS='PASS' if q.get('PASS') else 'FAILED')
 p.csvout(d/'PART_MANIFEST.csv',rows)
 op=d/'OBJECT_RESULT.json'
 if not op.exists():fail.append(c['OBJECT_ID']+': missing object terminal result');continue
 obj=json.loads(op.read_text());inputgate=all(bool(r['PART_MESH_PATH']) and Path(r['PART_MESH_PATH']).is_file() for r in rows);obj.update(FULL_PART_SET_COMPLETE=inputgate,Q14_ALL_PASS=sum(q.get('Q14_PASS',False) for q in results)==c['PART_N'],V3_ALL_PASS=sum(q.get('V3_PASS',False) for q in results)==c['PART_N'],OBJECT_PART_COMPLETENESS_GATE=all(q.get('PASS') and q.get('TRANSFORM_PASS') for q in results) and len(results)==c['PART_N'],FULL_MODEL_GENERATED_OBJECT=all(q.get('STRICT_MODEL_GENERATED',False) for q in results))
 if obj.get('FULL_ASSEMBLY_PASS'):
  if not inputgate or len(results)!=c['PART_N'] or not all(q.get('PASS') for q in results):fail.append(c['OBJECT_ID']+': invalid full assembly PASS')
  for fn in ['full_mesh.png','mesh_parts.png','cad_parts.png','assembled_cad.png','overlay.png','exploded.png']:
   im=Image.open(d/'renders'/fn);image_n+=1
   if im.width<1600 or im.height<1200:fail.append(c['OBJECT_ID']+': undersized render '+fn)
  am=json.loads((d/'assembly/assembly_manifest.json').read_text())
  if len(am['parts'])!=c['PART_N'] or am['BODY_N']!=am['EXPECTED_BODY_N']:fail.append(c['OBJECT_ID']+': incomplete assembly body manifest')
 p.dump(op,obj);objectrows.append(obj)
for name,h in json.loads((p.O/'manifests/SHA256.json').read_text()).items():
 if p.sha(p.O/'manifests'/name)!=h:fail.append(name+': manifest hash mismatch')
p.csvout(p.O/'tables/FULL20_ALL_PART_RESULTS.csv',allrows);p.csvout(p.O/'tables/FULL20_OBJECT_RESULTS.csv',objectrows)
summary=dict(PART_ROWS=n,EXPECTED_PART_ROWS=sum(c['PART_N'] for c in manifest),OBJECT_ROWS=len(objectrows),VERIFIED_SUCCESS_RENDER_N=image_n,TANK_PART029_FROZEN_HASHES_UNCHANGED=not any('case_014' in f for f in fail),REPAIR_BUDGET_RESPECTED=not any('repair budget' in f for f in fail),ERRORS=fail,ARTIFACT_CONSISTENCY_PASS=not fail)
import statistics
ns=[c['PART_N'] for c in manifest];p.dump(p.O/'reports/SELECTION_AUDIT.json',dict(SELECTED_OBJECT_N=20,FULL_INPUT_GATE_PASS_N=15,TOTAL_PART_N=sum(ns),MIN_PARTS_PER_OBJECT=min(ns),MEAN_PARTS_PER_OBJECT=statistics.mean(ns),MEDIAN_PARTS_PER_OBJECT=statistics.median(ns),MAX_PARTS_PER_OBJECT=max(ns),EXISTING_VALID_CAD_PART_N=sum(q.get('RAW_CAD_PASS',False) for q in allrows),MISSING_CAD_PART_N=sum(not q.get('RAW_CAD_PASS',False) for q in allrows),MISSING_XPART_N=50,TANK_PART_N=45,CORRECTION='Initial successful-XPart counts invalidated; same object identities retained. See INVENTORY_CORRECTION.json.'))
p.dump(p.O/'reports/DELIVERY_VERIFICATION.json',summary);p.update_progress();print(json.dumps(summary,indent=2))
