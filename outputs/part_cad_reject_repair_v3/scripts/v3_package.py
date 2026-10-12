from v2_common import *
import tarfile
assert read(O/'integrity/VALIDATION.json')['pass']
assert len(read(O/'tables/part_v2_v3_comparison.json'))==209
assert (O/'visualizations/index.html').exists()
files=sorted(p for p in O.rglob('*') if p.is_file() and p.name!='DELIVERY_FILES.json');dump(O/'integrity/DELIVERY_FILES.json',{'files':[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]})
full=O.parent/'PART_CAD_REJECT_REPAIR_V3_DELIVERY.tar.gz';review=O.parent/'PART_CAD_REJECT_REPAIR_V3_REVIEW.tar.gz'
with tarfile.open(full,'w:gz',compresslevel=5) as t:t.add(O,arcname=O.name)
with tarfile.open(review,'w:gz',compresslevel=5) as t:
 for name in ['reports','tables','visualizations','integrity','config','manifests','scripts','REPRODUCE.md']:t.add(O/name,arcname=str(Path(O.name)/name))
out={p.name:{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [full,review]};dump(O.parent/'PART_CAD_REJECT_REPAIR_V3_DELIVERY.sha256.json',out);print(json.dumps(out,indent=2))
