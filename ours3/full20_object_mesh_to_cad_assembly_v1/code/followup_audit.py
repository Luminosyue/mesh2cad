import json,csv,hashlib
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def writecsv(p,rs):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
aud={r['OBJECT_ID']:r for r in csv.DictReader((O/'selection/FULL_PART_SET_CORRECTION_AUDIT.csv').open())};rs=list(csv.DictReader((O/'selection/ALL_FULL_OBJECT_CANDIDATES.csv').open()))
for r in rs:
 a=aud[r['OBJECT_ID']];r['PART_N']=a['EXPECTED_PART_N'];r['ALL_PARTS_PRESENT']=a['COMPLETE'];r['NOTES']='Full expected set audited against P3 metadata, P3 file IDs and XPART_ATTEMPTED_PARTS. Missing IDs: '+a['MISSING_IDS']
writecsv(O/'selection/ALL_FULL_OBJECT_CANDIDATES.csv',rs)
missing={};recoverable=[]
for name,a in aud.items():
 if not (O/'objects'/name).exists() or a['COMPLETE']=='True':continue
 ids=set(a['MISSING_IDS'].split(','));dirs=list((R/'ours3').glob(name+'*'))+list(R.glob('*'+name+'*'));found={pid:[] for pid in ids}
 for d in dirs:
  if not d.is_dir():continue
  for p in d.rglob('*'):
   if p.suffix.lower() not in ['.obj','.stl','.ply'] or not p.is_file():continue
   # Completed X-Part geometry only; P3 originals and downstream CAD tessellation excluded.
   if not ('xpart' in str(p.relative_to(d)).lower() and ('complete' in p.name.lower() or p.parent.name.upper() in ids)):continue
   for pid in ids:
    if pid.lower() in p.name.lower() or p.parent.name.upper()==pid:found[pid].append(str(p))
 missing[name]=found
dump(O/'reports/MISSING_XPART_HISTORY_SEARCH.json',missing)
legacy={}
for d in [R/'ours3/airplane9_14bit_compact_ir_v1',R/'ours3/quantized_cad_representation_audit_v2']:
 legacy[str(d)]=dict(file_n=sum(1 for p in d.rglob('*') if p.is_file()),note='Legacy alternate IR uses per-section/AST quantization and a different semantic compiler; not byte-compatible with the frozen PARAMETERS-based Compact IR V3 dequantizer. Preserved; not presented as V3 PASS without compatible compilation.')
dump(O/'reports/LEGACY_QUANTIZATION_AUDIT.json',legacy)
print(json.dumps({name:{pid:len(ps) for pid,ps in ds.items() if ps} for name,ds in missing.items()},indent=2))
