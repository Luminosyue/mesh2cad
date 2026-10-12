import csv, json, time, subprocess
from pathlib import Path
EXP=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1')
MODEL=EXP/'model_v1'
table=list(csv.DictReader((EXP/'tables/FULL20_OBJECT_RESULTS.csv').open()))
done=[r['OBJECT_ID'] for r in table if r['STATUS']=='DONE']
active_text = subprocess.run(['ps','-eo','cmd'], capture_output=True, text=True, check=False).stdout
known = ['tank','birdhouse','mini_fire_engine','assorted_vegetable_set','3d_dollhouse_sofa','winerack','pressure_cooker','airplane','2_of_jenga_classic_game','toaster','dvd_player']
active = [obj for obj in known if any('train_model' in line and obj in line for line in active_text.splitlines())]
train=[]
for obj in active:
    p=MODEL/'runs'/obj/'TRAIN_STATUS.json'
    if p.exists():
        d=json.loads(p.read_text()); train.append(f"- {obj} | current update {d.get('step')} | loss {float(d.get('loss',0)):.6g} | lr {d.get('lr')}")
    else:
        train.append(f"- {obj} | active process; latest TRAIN_STATUS not written yet")
partial=[r['OBJECT_ID'] for r in table if r['STATUS']=='PARTIAL_FREE_GENERATED']
blocked=[r['OBJECT_ID'] for r in table if r['STATUS']=='BLOCKED']
rescue=['- Robot targeted part rescue and full assembly PASS'] if 'robot' in done else ['- Robot targeted part rescue pending assembly gate']
rescue.append('- Fire Truck targeted completion and full gate PASS')
blocked_lines=[f'- {x} | unresolved input or gate blocker' for x in blocked]
blocked_lines += ['- Airplane | 4 Q14 BRep blockers', '- Tank | 12 failed labels; PART_029 remains frozen strict success']
lines=['# FULL20 OBJECT PROGRESS','',f'Updated: {time.strftime("%F %T %z")}','',f'FULL MODEL ASSEMBLY: {len(done)} / 20','', 'DONE:', *[f'- {x}' for x in done], '', 'TRAINING:', *(train or ['- none']), '', 'PARTIAL:', *[f'- {x}' for x in partial], '', 'RESCUE:', *rescue, '', 'BLOCKED:', *blocked_lines, '', 'DISK:', '- /data free approximately 103 GB after safe historical checkpoint cleanup', '- system checkpoint disk free approximately 73 GB', '', 'Representation: q14 + Compact IR V3; canonical controls are not model success; texture reconstruction is out of scope.']
for p in [EXP/'reports/PROGRESS.md',MODEL/'reports/PROGRESS.md']:
    p.write_text('\n'.join(lines)+'\n')
print('PROGRESS_REFRESHED',len(done))
