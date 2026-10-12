import csv, glob, json, os
from pathlib import Path

EXP=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1')
MODEL=EXP/'model_v1'
MAN=json.loads((EXP/'manifests/FULL20_OBJECT_MANIFEST.json').read_text())

def gate_for(obj):
    paths=sorted(glob.glob(str(MODEL/'generated'/obj/'*/OBJECT_GATE.json')))
    if not paths: return None
    # Prefer an execution-success gate over an earlier partial gate.
    paths.sort(key=lambda p: (json.loads(Path(p).read_text()).get('FULL_MODEL_ASSEMBLY_PASS',False), p))
    return json.loads(Path(paths[-1]).read_text())

rows=[]
for m in MAN:
    obj=m['OBJECT_ID']; g=gate_for(obj); n=int(m.get('PART_N',0));
    if g:
        metrics=g.get('metrics',{}); full=bool(g.get('FULL_MODEL_ASSEMBLY_PASS',False)); free=int(g.get('free_exact_n',0) or 0); cad=int(g.get('cad_pass_n',0) or 0)
        status='DONE' if full else ('PARTIAL_FREE_GENERATED' if free else 'BLOCKED')
        demo=(str(Path(g.get('render_dir',''))/'assembled_cad.png') if g.get('render_dir') else '')
        step=g.get('step','')
    else:
        metrics={}; full=False; free=0; cad=0; status='QUEUED'; demo=''; step=''
    rows.append(dict(OBJECT_ID=obj,PART_N=n,TRAINABLE_PART_N=n,FROZEN_PART_N=0,FAILED_LABEL_N=max(0,n-free),FREE_PASS_N=free,CAD_STEP_PASS_N=cad,ASSEMBLED_PART_N=n if full else 0,ASSEMBLY_PASS=str(full),CD=metrics.get('CD',''),IOU64=metrics.get('IOU',''),VOLUME_ERROR=metrics.get('VOLUME_ERROR',''),STATUS=status,DEMO_PATH=demo,STEP_PATH=step))
for p in [EXP/'tables/FULL20_OBJECT_RESULTS.csv',MODEL/'tables/FULL20_OBJECT_RESULTS.csv']:
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print('REFRESHED',len(rows),'rows')
