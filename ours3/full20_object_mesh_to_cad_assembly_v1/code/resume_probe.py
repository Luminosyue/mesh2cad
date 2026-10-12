import json,subprocess,shutil,datetime,ast
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1'
states=[]
for name in ['android_figure_orange','tank']:
 d=E/'runs'/name;tr=json.loads((d/'TRAIN_STATUS.json').read_text());ck=json.loads((d/'LATEST_CHECKPOINT.json').read_text());pr=json.loads((E/'logs'/f'{name}_process.json').read_text());tfs=sorted(d.glob('TF_*.json'),key=lambda x:int(x.stem.split('_')[1]));tf=json.loads(tfs[-1].read_text()) if tfs else []
 states.append(dict(ACTIVE_OBJECT=name,ACTIVE_PID=pr['pid'],GPU=pr['gpu'],CHECKPOINT=ck['path'],CURRENT_UPDATE=tr['step'],CURRENT_LOSS=tr['loss'],CURRENT_TF_ERRORS=sum(x['errors'] for x in tf) if tf else None,TF_AUDIT_UPDATE=int(tfs[-1].stem.split('_')[1]) if tf else None))
state=dict(CURRENT_TIME=datetime.datetime.now().isoformat(),ACTIVE=states,FREE_DISK_GB=shutil.disk_usage('/data').free/1e9,CHECKPOINT_DISK_FREE_GB=shutil.disk_usage('/var/tmp').free/1e9)
(O/'reports/CURRENT_RUNTIME_STATE.json').write_text(json.dumps(state,indent=2));print(json.dumps(state,indent=2))
p=O/'objects/tank/cad_parts/PART_004/compiled_cadquery.py';tree=ast.parse(p.read_text());print('TANK_COMPILER_FUNCTIONS')
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name not in ['build','_condition_q14']:
  s=ast.get_source_segment(p.read_text(),n)
  print(s[:12000])
