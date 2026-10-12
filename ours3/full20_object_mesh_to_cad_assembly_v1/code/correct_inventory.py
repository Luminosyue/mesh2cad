import json,csv,hashlib,shutil,time
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';S=R/'p3_xpart_open_cases'
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def writecsv(p,rs):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
audit={r['OBJECT_ID']:r for r in csv.DictReader((O/'selection/FULL_PART_SET_CORRECTION_AUDIT.csv').open())};mp=O/'manifests/FULL20_OBJECT_MANIFEST.json';manifest=json.loads(mp.read_text());backup=O/'manifests/initial_incorrect_count_audit';backup.mkdir(exist_ok=True)
for p in [mp,O/'manifests/FULL20_OBJECT_MANIFEST.csv',O/'manifests/SHA256.json',O/'reports/SELECTION_AUDIT.json']:
 if not (backup/p.name).exists():shutil.copy2(p,backup/p.name)
changes=[];missingn=0
for c in manifest:
 name=c['OBJECT_ID'];a=audit[name];expected=int(a['EXPECTED_PART_N']);old=c['PART_N'];c['PART_N']=expected;d=O/'objects'/name;rs=list(csv.DictReader((d/'PART_MANIFEST.csv').open()));existing={r['PART_ID'] for r in rs}
 for p in sorted((S/name/'p3_parts').glob('part_*.obj')):
  pid=p.stem.upper()
  if pid in existing:continue
  r={k:'' for k in rs[0]};r.update(PART_ID=pid,PART_MESH_PATH='',RAW_CAD_READY='False',Q14_READY='False',V3_READY='False',STEP_READY='False',GENERATED_PROGRAM_READY='False',GENERATED_STEP_READY='False',NORMALIZATION_READY='False',INVERSE_TRANSFORM_READY='False',SOURCE='FAILED',STATUS='FAILED_MISSING_XPART',QUALITY_STATUS='UNAVAILABLE')
  rs.append(r);pd=d/'cad_parts'/pid;pd.mkdir(parents=True,exist_ok=True);dump(pd/'result.json',dict(OBJECT_ID=name,PART_ID=pid,PART_MESH_PATH='',ORIGINAL_P3_MESH_PATH=str(p),CAD_SOURCE='UNAVAILABLE',RAW_CAD_PASS=False,Q14_PASS=False,V3_PASS=False,STEP_PASS=False,TRANSFORM_PASS=False,PART_GEOMETRY_PASS=False,ASSEMBLED=False,PASS=False,FAILURE_REASON='MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET',STATUS='FAILED'));missingn+=1
 rs.sort(key=lambda r:r['PART_ID']);assert len(rs)==expected;writecsv(d/'PART_MANIFEST.csv',rs)
 if expected!=old:
  changes.append(dict(OBJECT_ID=name,PREVIOUS_INCORRECT_PART_N=old,CORRECT_FULL_PART_N=expected,MISSING_XPART_N=expected-old,SELECTION_REPLACED=False))
  if (d/'DONE').exists():(d/'DONE').rename(d/'INVALIDATED_INCOMPLETE_DONE')
  if (d/'OBJECT_RESULT.json').exists():
   p=d/'OBJECT_RESULT.json';shutil.copy2(p,d/'INITIAL_INVALIDATED_OBJECT_RESULT.json');r=json.loads(p.read_text());r.update(PART_N=expected,PART_COVERAGE=r.get('ASSEMBLED_PART_N',0)/expected,FULL_ASSEMBLY_PASS=False,FULL_PART_SET_COMPLETE=False,FAILURE_REASON='MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET');dump(p,r)
  if (d/'assembly/assembly_manifest.json').exists():
   p=d/'assembly/assembly_manifest.json';r=json.loads(p.read_text());r.update(FULL_PART_SET_COMPLETE=False,TOTAL_PART_N=expected,MISSING_PART_N=expected-old,FORMAL_COMPLETE_DEMO=False);dump(p,r)
dump(mp,manifest);writecsv(O/'manifests/FULL20_OBJECT_MANIFEST.csv',manifest);dump(O/'manifests/SHA256.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'manifests').glob('FULL20_OBJECT_MANIFEST.*')})
rec=dict(reason='n_xpart_parts counted successful subset, not original complete part set. Correct expected count uses P3 files, num_parts, and XPART_ATTEMPTED_PARTS; exact ID set equality required.',OBJECT_IDS_CHANGED=False,INITIAL_AUDIT_INVALIDATED=True,SELECTED_OBJECT_N=20,FULL_INPUT_GATE_PASS_N=20-len(changes),TOTAL_EXPECTED_PART_N=sum(c['PART_N'] for c in manifest),EXISTING_XPART_N=sum(c['PART_N'] for c in manifest)-missingn,MISSING_XPART_N=missingn,changes=changes,original_manifest_preserved=str(backup),timestamp=time.time());dump(O/'reports/INVENTORY_CORRECTION.json',rec)
(O/'reports/INVENTORY_CORRECTION.md').write_text('# Explicit completeness correction\n\n'+json.dumps(rec,indent=2)+'\n\nThe same 20 object identities remain frozen. No runtime-failed object is replaced. Five objects are retained as full-input-gate failures unless their original missing X-Part assets are recovered. Partial assemblies are not valid complete demos.\n')
print(json.dumps(rec,indent=2))
