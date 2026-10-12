from structure_common import *
import zipfile
assert read(O/'integrity/FINAL_VALIDATION.json')['pass']
paths=sorted(p for p in O.rglob('*') if p.is_file() and p.suffix!='.zip' and p.name not in ['ARTIFACT_SHA256.json','DELIVERY_SHA256.json'] and '__pycache__' not in p.parts)
manifest={str(p.relative_to(O.parent)):sha(p) for p in paths};dump(O/'ARTIFACT_SHA256.json',manifest);paths.append(O/'ARTIFACT_SHA256.json');dest=O/'TARGETED_CAD_STRUCTURE_DIAGNOSIS_V1_DELIVERY.zip'
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in paths:z.write(p,str(p.relative_to(O.parent)))
record={'archive':str(dest),'sha256':sha(dest),'bytes':dest.stat().st_size,'artifact_n':len(manifest),'archive_entry_n':len(paths)};dump(O/'DELIVERY_SHA256.json',record);print(json.dumps(record,indent=2),flush=True)
