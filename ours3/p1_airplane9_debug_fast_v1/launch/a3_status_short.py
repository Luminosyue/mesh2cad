from pathlib import Path
import json
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1')
def read(p):return json.loads(p.read_text())
print('STATUS',read(E/'status.json'))
print('TRAJECTORY',[(r['step'],r['total_tf_errors'],r['zero_parts'],r['free_exact_n']) for r in read(E/'trajectory.json')])
for tag in sorted((E/'evaluations').iterdir()):
 rows=[]
 for p in sorted(tag.glob('PART_*')):
  r=read(p/'result.json') if (p/'result.json').exists() else None
  traces=read(p/'predicted_tokens.json') if (p/'predicted_tokens.json').exists() else []
  rows.append({'part':p.name,'blocks':len(traces),'tokens':sum(len(t['token_ids']) for t in traces),'exact':r['SEQUENCE_EXACT_MATCH'] if r else None,'gate':r['PART_GATE_PASS'] if r else None})
 print(tag.name,rows)
p=E/'audits/gpu_progress.json'
if p.exists():
 r=read(p);print('TRAIN',r['global_step'],r['microbatches'])
for name in ['failure.json','outcome.json']:
 if (E/name).exists():print(name,read(E/name))
