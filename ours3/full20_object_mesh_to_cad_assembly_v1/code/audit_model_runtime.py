import json,hashlib,sys,shutil
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
fails=[]
for p in sorted((O/'objects/tank/cad_parts').glob('*/result.json')):
 r=json.loads(p.read_text())
 if not r['PASS']:
  record=dict(part=r['PART_ID'],reason=r['FAILURE_REASON'],traceback=r.get('TRACEBACK'),label=str(p.parent))
  for name in ['geometry_report.json','repairs.json']:
   if (p.parent/name).exists():record[name]=json.loads((p.parent/name).read_text())
  fails.append(record)
dump(E/'reports/TANK_LABEL_BLOCKERS.json',fails)
print('TANK_BLOCKERS')
for r in fails:print(r['part'],r['reason'])
print('SOURCE_MODEL_CONFIGS')
for rel in ['airplane3_fullseq_14bit_ir_v1','airplane000_fullseq_14bit_ir_v1','airplane_part000_fullseq_14bit_ir_v1','p1v2_controlled_full_train_v1']:
 d=R/'ours3'/rel
 for p in list(d.glob('*.yaml'))[:8]:
  print(p.name,next((s for s in p.read_text().splitlines() if s.startswith('model_name_or_path')),''))
print('FROZEN_CHECK',all(sha(p)==h for p,h in json.loads((E/'reports/FROZEN_PART029_HASHES.json').read_text()).items()))
