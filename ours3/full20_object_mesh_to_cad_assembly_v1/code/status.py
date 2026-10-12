import json,collections,time
from pathlib import Path
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1')
rs=[json.loads(p.read_text()) for p in O.glob('objects/*/OBJECT_RESULT.json')];ps=[json.loads(p.read_text()) for p in O.glob('objects/*/cad_parts/*/result.json')]
print(json.dumps(dict(terminal_objects=len(rs),assembly_pass=sum(r.get('FULL_ASSEMBLY_PASS',False) for r in rs),evaluated_parts=len(ps),part_pass=sum(r.get('PASS',False) for r in ps),failure_types=dict(collections.Counter(r['FAILURE_REASON'].split(':')[0] for r in ps if not r.get('PASS'))),successes=[dict(name=r['OBJECT_ID'],parts=r['PART_N'],CD=r['CD'],IoU=r['IOU']) for r in rs if r.get('FULL_ASSEMBLY_PASS')]),indent=2))
