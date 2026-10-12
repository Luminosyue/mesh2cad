from v2_common import *
import tarfile

assert read(O/'integrity/VALIDATION.json')['pass']
assert read(O/'integrity/READ_ONLY_GUARD.json')['pass']
assert read(O/'reports/summary.json')['TOTAL_PART_N']==209
assert read(O/'visualizations/manifest.json')['counts']['reject_examples']==10
files=sorted(p for p in O.rglob('*') if p.is_file() and p.name!='DELIVERY_FILES.json')
dump(O/'integrity/DELIVERY_FILES.json',{'files':[{ 'path':str(p.relative_to(O)), 'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]})
full=O.parent/'PART_CAD_FITTING_V2_DELIVERY.tar.gz'
review=O.parent/'PART_CAD_FITTING_V2_REVIEW.tar.gz'
with tarfile.open(full,'w:gz',compresslevel=5) as t:t.add(O,arcname=O.name)
with tarfile.open(review,'w:gz',compresslevel=5) as t:
    for name in ['reports','tables','visualizations','config','manifests','integrity','scripts','REPRODUCE.md']:
        t.add(O/name,arcname=str(Path(O.name)/name))
out={p.name:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [full,review]}
dump(O.parent/'PART_CAD_FITTING_V2_DELIVERY.sha256.json',out)
print(json.dumps(out,indent=2))
