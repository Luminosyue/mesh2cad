from pathlib import Path
import json,gzip
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1')
for step in [20,30,40]:
 for part in ['PART_005','PART_008']:
  p=E/f'scans/checkpoint-{step}/{part}/teacher_tokens.jsonl.gz'
  if not p.exists():continue
  rows=[json.loads(l) for l in gzip.open(p,'rt')]
  print(step,part,[{'global_token':i+1,**{k:r[k] for k in ['block','token_in_block','gt_id','gt_token','top1_id','top1_token','TOKEN_MARGIN','EOS']}} for i,r in enumerate(rows) if not r['CORRECT']])
