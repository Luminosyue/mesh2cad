#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_operation_aware_structure_loss_v1'
files=[ROOT/'scripts/spatiallm_curve_token_v1/train_curve_token_spatiallm.py',ROOT/'scripts/spatiallm_curve_token_v1/curve_token_injector.py',ROOT/'scripts/spatiallm_curve_token_v1/curve_projector.py',ROOT/'scripts/spatiallm_curve_token_v1/config.py',ROOT/'SpatialLM/spatiallm/tuner/trainer.py',ROOT/'SpatialLM/spatiallm/tuner/data/collator.py',ROOT/'SpatialLM/spatiallm/tuner/data/mm_plugin.py',ROOT/'SpatialLM/spatiallm/tuner/data/template.py',ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/launch/train_corrected_m2_entrypoint.py',ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/launch/corrected_m2_runtime_audit.py',ROOT/'ours3/m2_exact9998_corrected_m2_train_v1/configs/m2_exact9998_train.yaml']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files};mode=sys.argv[1];out=EXP/'audits'/f'MAIN_SOURCE_INVENTORY_{mode.upper()}.json'
data={'files':now,'file_n':len(now),'ORIGINAL_SOURCE_CHANGED_N':0}
if mode=='after':
 before=json.loads((EXP/'audits/MAIN_SOURCE_INVENTORY_BEFORE.json').read_text())['files'];data['ORIGINAL_SOURCE_CHANGED_N']=sum(before.get(k)!=v for k,v in now.items())
out.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2));raise SystemExit(0 if data['ORIGINAL_SOURCE_CHANGED_N']==0 else 2)
