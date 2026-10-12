#!/usr/bin/env python3
"""Freeze the D/F held-out canary before any construction is attempted."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); IN=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/PREBUILD_ELIGIBLE_CANDIDATES.jsonl'; OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/canary20'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 rows=[json.loads(x) for x in IN.read_text().splitlines() if x]
 chosen=[]
 for ds in ('DeepCAD','Fusion360'):
  xs=sorted([r for r in rows if r['dataset']==ds],key=lambda r:r['candidate_id'])
  # DSL character length is the only already-frozen available complexity proxy.
  for r in xs:r['_dsl_chars']=len((Path(r['source_path'])/'program_canonical.dsl').read_text())
  xs=sorted(xs,key=lambda r:(r['_dsl_chars'],r['candidate_id']))
  idx=np.floor((np.arange(10)+.5)*len(xs)/10).astype(int)
  for i in idx:chosen.append(xs[int(i)])
 assert len(chosen)==20 and len({x['candidate_id'] for x in chosen})==20
 data=[]
 for i,r in enumerate(chosen):data.append({'canary_index':i,'cad_id':r['candidate_id'],'dataset':r['dataset'],'source_id':r['source_id'],'source_path':r['source_path'],'source_step_path':str(Path(r['source_path'])/'model.step'),'source_step_sha256':r['source_step_sha256'],'selection_reason':'deterministic DSL-length decile stratification within dataset; prebuild eligible only','prebuild_leakage_pass':True,'dsl_chars_proxy':r['_dsl_chars']})
 OUT.mkdir(parents=True,exist_ok=False); payload={'protocol':'ISOLATED_DF_CANARY20_BUILD','selection':'frozen before build; DeepCAD/Fusion360 each 10; length deciles','records':data}; payload['manifest_sha256']=sha(json.dumps(payload,sort_keys=True,separators=(',',':')).encode());(OUT/'CANARY20_MANIFEST.json').write_text(json.dumps(payload,indent=2)+'\n');print(payload['manifest_sha256'])
if __name__=='__main__':main()
