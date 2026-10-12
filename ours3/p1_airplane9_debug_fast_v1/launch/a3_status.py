from pathlib import Path
import json
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1')
for name in ['status.json','outcome.json','failure.json','trajectory.json']:
 p=E/name
 if p.exists():print(name,p.read_text())
p=E/'audits/gpu_progress.json'
if p.exists():
 r=json.loads(p.read_text());print('TRAIN',r['global_step'],r['microbatches'],r['elapsed_seconds'],r['part_exposures'])
for tag in sorted((E/'scans').iterdir(),key=lambda p:int(p.name.split('-')[-1])):
 print('SCAN',tag.name,[(p.parent.name,json.loads(p.read_text())['TOKEN_ERRORS']) for p in sorted(tag.glob('PART_*/summary.json'))])
for tag in (E/'evaluations').iterdir():
 print('DECODE',tag.name,[(p.parent.name,len(json.loads(p.read_text()))) for p in sorted(tag.glob('PART_*/predicted_tokens.json'))])
