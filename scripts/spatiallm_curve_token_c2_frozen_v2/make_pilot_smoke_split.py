#!/usr/bin/env python3
import hashlib,json
from collections import Counter,defaultdict,deque
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
MAN=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected/runs/run1/MANIFEST.json'
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_smoke_v1/data'

def chash(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def kbin(k):return 'low_le16' if k<=16 else ('high_ge64' if k>=64 else 'mid')
def feature(r):
 for k in ('has_hole','has_cut','has_join','has_circle','has_rectangle','has_polygon'):
  if r[k]:return k[4:]
 return 'other'
def take_balanced(pool,n):
 bins=defaultdict(deque)
 for r in sorted(pool,key=lambda x:x['cad_id']):bins[(r['difficulty_bin'],kbin(r['k_valid']),feature(r))].append(r)
 out=[]; keys=sorted(bins)
 while len(out)<n:
  progressed=False
  for k in keys:
   if bins[k] and len(out)<n:out.append(bins[k].popleft());progressed=True
  if not progressed:raise RuntimeError('insufficient pool')
 return out

rows=json.loads(MAN.read_text())['rows']; chosen={}
quotas={'train':{'deepcad':154,'fusion360':38},'val':{'deepcad':38,'fusion360':10}}
remaining=list(rows)
for split in ('val','train'):
 chosen[split]=[]
 for src in ('deepcad','fusion360'):
  pool=[r for r in remaining if r['source_dataset']==src]
  got=take_balanced(pool,quotas[split][src]);chosen[split]+=got
  used={r['cad_id'] for r in got};remaining=[r for r in remaining if r['cad_id'] not in used]
 chosen[split].sort(key=lambda r:r['cad_id'])
 doc={'name':f'pilot_smoke_{split}','source_manifest_sha256':'ef20bd0ef95e97f61c07116ff4e19e7e9a7938d5775520a19d5a351b65244f7c','count':len(chosen[split]),'cad_ids':[r['cad_id'] for r in chosen[split]],'records':chosen[split]}
 doc['content_sha256']=chash(doc);chosen[split]=doc
if set(chosen['train']['cad_ids'])&set(chosen['val']['cad_ids']):raise RuntimeError('train/val overlap')
summary={'train':{'count':192,'source':dict(Counter(r['source_dataset'] for r in chosen['train']['records'])),'difficulty':dict(Counter(r['difficulty_bin'] for r in chosen['train']['records'])),'k_bin':dict(Counter(kbin(r['k_valid']) for r in chosen['train']['records']))},'val':{'count':48,'source':dict(Counter(r['source_dataset'] for r in chosen['val']['records'])),'difficulty':dict(Counter(r['difficulty_bin'] for r in chosen['val']['records'])),'k_bin':dict(Counter(kbin(r['k_valid']) for r in chosen['val']['records']))},'feature_coverage':{k:{s:sum(r[k] for r in chosen[s]['records']) for s in ('train','val')} for k in ('has_circle','has_rectangle','has_polygon','has_hole','has_cut','has_join')},'overlap':0}
OUT.mkdir(parents=True,exist_ok=False)
for split in ('train','val'):(OUT/f'pilot_smoke_{split}.json').write_text(json.dumps(chosen[split],indent=2)+'\n')
(OUT/'SPLIT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
