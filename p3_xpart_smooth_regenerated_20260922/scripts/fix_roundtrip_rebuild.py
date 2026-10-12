from pathlib import Path
import shutil,json,sys
from concurrent.futures import ThreadPoolExecutor
from audit_regenerated import run
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
override='''
# Reproduce the STEP roundtrip used during candidate validation before partitioning.
def build_model(spec):
    from pathlib import Path
    import tempfile
    scale=spec['construction_scale'];center=spec['center']
    world=build_normalized(spec).scale(1/scale).translate(tuple(center))
    with tempfile.TemporaryDirectory(prefix='native_cad_roundtrip_') as td:
        path=Path(td)/'candidate.step'
        world.exportStep(str(path))
        world=cq.importers.importStep(str(path)).val()
    if spec.get('partition_final',False):
        normalized=world.translate(tuple(-v for v in center)).scale(scale)
        world=partition_periodic_faces(normalized).scale(1/scale).translate(tuple(center))
    return world
'''
parts=[('school_bus','PART_017'),('garden_swing','PART_006')]
if '--all-failed' in sys.argv:
    for p in (r/'validation').glob('*/*.json'):
        a=json.loads(p.read_text());errors=' '.join(a.get('errors',[]))
        if not a.get('passed') and ('geometry or topology mismatch' in errors or 'AssertionError' in errors):parts.append((a['case_id'],a['part_id']))
parts=sorted(set(parts))
paths=[]
for case,part in parts:
    od=r/'cases'/case/part;path=od/'cad.py';code=path.read_text();backup=r/'validation/original_scripts'/case/(part+'.py');backup.parent.mkdir(parents=True,exist_ok=True)
    if not backup.exists():shutil.copy2(path,backup)
    if '# Reproduce the STEP roundtrip' not in code:
        code=code.replace('\nPARAMETERS = ',override+'\nPARAMETERS = ');path.write_text(code)
    paths.append(od)
with ThreadPoolExecutor(max_workers=2) as pool:
    for result in pool.map(run,paths):print(json.dumps(result),flush=True)
