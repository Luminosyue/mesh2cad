import json,hashlib,tarfile,datetime
from pathlib import Path
O=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
for name in ['FINAL_VALIDATION.json','ASSEMBLY_VALIDATION.json','READ_ONLY_GUARD.json']:
 r=json.loads((O/'integrity'/name).read_text());assert r['pass'],name
initial=json.loads((O/'integrity/IMPLEMENTATION_INITIAL_SHA256.json').read_text());current={str(p.relative_to(O)):sha(p) for folder in ['scripts','config','runtime'] for p in sorted((O/folder).rglob('*')) if p.is_file()}
(O/'integrity/IMPLEMENTATION_FINAL_SHA256.json').write_text(json.dumps(current,indent=2))
(O/'integrity/IMPLEMENTATION_CHANGE_NOTE.json').write_text(json.dumps({'note':'Initial hashes capture the first implementation snapshot, not an immutable prohibition on engineering fixes. Before finalization, updates added reporting/validation and visualization, made CPU worker count configurable, and prevented premature assembly of unfinished objects. Fitting algorithms, candidate budgets, thresholds and metric seeds were unchanged during stages 3/5/20. Final script hashes are authoritative for replay.','initial_manifest':initial,'final_manifest':current},indent=2))
files={str(p.relative_to(O)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.rglob('*')) if p.is_file() and p.name!='DELIVERY_FILES_SHA256.json'}
(O/'integrity/DELIVERY_FILES_SHA256.json').write_text(json.dumps(files))
archive=O.parent/'P3_HIGH_DETAIL_SMOKE20_DELIVERY.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=3) as t:t.add(O,arcname=O.name)
meta={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'file_n':len(files)+1,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
archive.with_suffix('.sha256.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
review=O.parent/'P3_HIGH_DETAIL_SMOKE20_REVIEW.tar.gz'
with tarfile.open(review,'w:gz') as t:
 for folder in ['reports','tables','manifests','visualizations','scripts','config','integrity']:t.add(O/folder,arcname=O.name+'/'+folder)
print('REVIEW',str(review),review.stat().st_size)
