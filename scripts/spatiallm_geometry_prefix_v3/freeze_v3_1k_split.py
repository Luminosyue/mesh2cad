#!/usr/bin/env python3
"""Freeze 50 polluted decode-dev and untouched 150 pilot-eval records."""
import hashlib, json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data'
PHASE_D=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/phase_d_inference_diagnostic_v1/data/phase_d_50.json'
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'

def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(name,records,meta):
 obj={**meta,'count':len(records),'records':records};obj['content_sha256']=digest(records)
 (OUT/name).write_text(json.dumps(obj,indent=2)+'\n');return hashlib.sha256((OUT/name).read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=False)
 train=json.loads((DATA/'pilot_1k_train.json').read_text())['records'];val=json.loads((DATA/'pilot_1k_val.json').read_text())['records']
 dev_ids={x['cad_id'] for x in json.loads(PHASE_D.read_text())['records']}
 dev=[x for x in val if x['cad_id'] in dev_ids];ev=[x for x in val if x['cad_id'] not in dev_ids]
 if (len(train),len(val),len(dev),len(ev))!=(800,200,50,150):raise RuntimeError('split counts mismatch')
 common={'protocol':'V3_1K_FROZEN_SPLIT_V1','official_test_read':False,'training_started':False,'train_source':'frozen pilot_1k_train','val_source':'frozen pilot_1k_val','decode_dev_definition':'Phase-D 50 IDs; previously inspected and used only for selection','pilot_eval_definition':'remaining 150 IDs; held untouched until final checkpoint freeze'}
 hashes={'train':write('v3_1k_train.json',train,common),'decode_dev':write('v3_decode_dev_50.json',dev,common),'pilot_eval':write('v3_pilot_eval_150.json',ev,common)}
 manifest={**common,'counts':{'train':800,'decode_dev':50,'pilot_eval':150},'file_sha256':hashes,'disjoint':True}
 (OUT/'SPLIT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
