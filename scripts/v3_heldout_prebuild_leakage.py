#!/usr/bin/env python3
"""Read-only prebuild leakage audit for DeepCAD/Fusion360 V3 held-out candidates."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
TRAIN=ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
CAND=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/pool/NEW_BASE_COMPLETE_CANDIDATES.jsonl'
OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 train=json.loads(TRAIN.read_text())['records']; train_ids={r['cad_id'] for r in train}; train_paths={str(Path(r['surface_input']).parents[2]/'train'/Path(r['surface_input']).parent.name) for r in train}
 # Derive actual raw STEP hashes, avoiding an assumption that ID uniqueness is enough.
 train_step={}
 for r in train:
  sid=Path(r['surface_input']).parent.name; ds='DeepCAD' if r['source_dataset']=='deepcad' else 'Fusion360'; p=ROOT/'cad_spatial_dataset'/ds/'train'/sid/'model.step'
  if p.is_file():train_step[sha(p)]=r['cad_id']
 rows=[]; reject=[]
 for line in CAND.open():
  r=json.loads(line)
  if r['dataset'] not in ('DeepCAD','Fusion360') or not r['base_complete']:continue
  p=Path(r['source_path'])/'model.step'; h=sha(p) if p.is_file() else None
  reason=[]
  if r['candidate_id'] in train_ids:reason.append('exact_cad_id_overlap')
  if str(Path(r['source_path'])) in train_paths:reason.append('source_path_overlap')
  if h in train_step:reason.append('source_step_hash_overlap')
  x={**r,'source_step_sha256':h,'prebuild_leakage_pass':not reason,'prebuild_reject_reasons':reason}
  (reject if reason else rows).append(x)
 # Internal duplicate source bytes are excluded now too; deterministic first canonical id wins.
 seen={}; keep=[]; internal=[]
 for r in sorted(rows,key=lambda z:z['candidate_id']):
  if r['source_step_sha256'] in seen:
   r['prebuild_leakage_pass']=False;r['prebuild_reject_reasons']=['internal_source_step_hash_duplicate'];r['duplicate_of']=seen[r['source_step_sha256']];internal.append(r)
  else:seen[r['source_step_sha256']]=r['candidate_id'];keep.append(r)
 report={'phase':'PREBUILD_LEAKAGE_AUDIT','train_count':len(train),'source_total':len(rows)+len(reject),'exact_id_overlap':sum('exact_cad_id_overlap'in r['prebuild_reject_reasons'] for r in reject),'source_path_overlap':sum('source_path_overlap'in r['prebuild_reject_reasons'] for r in reject),'hash_overlap':sum('source_step_hash_overlap'in r['prebuild_reject_reasons'] for r in reject),'duplicate_group_overlap':'NOT_AVAILABLE_IN_CURRENT_V3_METADATA; deferred to final geometry-fingerprint audit','internal_source_hash_duplicates':len(internal),'remaining_candidates':len(keep),'by_dataset':dict(Counter(r['dataset'] for r in keep)),'train_candidate_intersection':0,'read_only':True}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'PREBUILD_LEAKAGE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 with (OUT/'PREBUILD_ELIGIBLE_CANDIDATES.jsonl').open('w') as f:
  for r in keep:f.write(json.dumps(r)+'\n')
 with (OUT/'PREBUILD_REJECTED_CANDIDATES.jsonl').open('w') as f:
  for r in reject+internal:f.write(json.dumps(r)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
