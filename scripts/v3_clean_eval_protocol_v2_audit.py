#!/usr/bin/env python3
"""Read-only evaluation-protocol audit for the current V3 clean B0/M2 runs."""
from __future__ import annotations
import hashlib,json,os,pathlib,subprocess
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
DATA=ROOT/'ours3/v3_clean_training_v1/data'; RUNS=ROOT/'ours3/v3_clean_training_v1/runs'
OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2'
def dump(n,x): (OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def checkpoints(d):
 out=[]
 for p in sorted(d.glob('checkpoint_epoch_*')):
  idx=p/'model.safetensors.index.json'; adapter=p/'geometry_prefix_adapter.pt'
  files=list(p.glob('model-*.safetensors'))
  out.append({'path':str(p),'epoch':int(p.name.rsplit('_',1)[-1]),'model_index_exists':idx.is_file(),'model_shards':[{ 'name':x.name,'bytes':x.stat().st_size} for x in files],'adapter_exists':adapter.is_file(),'checkpoint_loadable_structural':bool(idx.is_file() and files and all(x.stat().st_size>0 for x in files))})
 return out
def arm(name):
 d=RUNS/name; rep=json.loads((d/'TRAINING_REPORT.json').read_text()); c=checkpoints(d)
 return {'run_dir':str(d),'report_status':rep.get('status'),'report_latest_completed_epoch':len(rep.get('curve',[])),'latest_checkpoint':c[-1] if c else None,'all_checkpoints':c,'optimizer_state_saved':False,'scheduler_state_saved':False,'resume_supported_by_current_runner':False,'note':'The current runner only saves model/tokenizer (+ M2 adapter); it serializes no optimizer/scheduler/global-step state.'}
def main():
 OUT.mkdir(parents=True,exist_ok=False)
 clean=json.loads((DATA/'CLEAN_V3_MANIFEST.json').read_text()); excl=json.loads((DATA/'EXCLUDED_V3_MANIFEST.json').read_text())
 train=clean['records']; tids={r['cad_id'] for r in train}; current_dev_ids=set(tids)
 exc=excl['records']; candidates=[r for r in exc if not r.get('reasons')]
 # Excluded records fail at least one frozen eligibility condition; none may become held-out silently.
 current={'CURRENT_GATE':'V3_CLEAN_EVAL_PROTOCOL_AUDIT_V2','B0':arm('b0_clean'),'M2':arm('m2_clean_retry1'),'train_count':len(tids),'current_dev_count':len(current_dev_ids),'train_dev_intersection':len(tids&current_dev_ids),'current_dev_status':'INVALID_AS_GENERALIZATION_DEV','current_dev_interpretation':'TRAIN_SELF_DECODE only; memorization and generation sanity, not held-out generalization.'}
 dump('CURRENT_RUN_AUDIT.json',current)
 split={'clean_universe':clean['original_count'],'clean_train_intersection':len(train),'excluded_count':len(exc),'exclusion_summary':{'context_overflow':excl['context_overflow'],'step_failure':excl['step_failure'],'overlap':excl['overlap']},'TRAIN_IDS_count':len(tids),'CURRENT_DEV_IDS_count':len(current_dev_ids),'TRAIN_DEV_INTERSECTION':len(tids&current_dev_ids),'CURRENT_DEV_STATUS':'INVALID_AS_GENERALIZATION_DEV','independent_candidates_meeting_all_clean_conditions':len(candidates),'INDEPENDENT_DEV_AVAILABLE':False,'reason':'All 112 non-train records are explicitly excluded by one or more frozen clean criteria. A held-out dev50 cannot be fabricated from the train688 or these excluded records.','required_future_split':'Freeze a larger clean universe, or retrain a new 638-train/50-dev split from a valid pool; neither action is taken by this audit.'}
 dump('SPLIT_AUDIT.json',split); dump('data/DECODE_DEV_50_MANIFEST.json',{'available':False,'count':0,'reason':split['reason'],'train_intersection':0}) if (OUT/'data').mkdir() is None else None
 # The current generation code's exact behavior is documented rather than changed in place.
 (OUT/'EVAL_LOOP_AUDIT.md').write_text('''# Evaluation loop audit\n\n**Old behavior:** `train_clean_v3.py` calls `util.eval_dev(model, ..., rows, ..., 4096, ...)` after every epoch. `rows` is the same 688-record training list. `eval_dev` greedily decodes every record with `max_new_tokens=4096`, then parses and invokes the CAD evaluator. This is why logs say `dev=i/50` while i reaches 688.\n\n**Optimizer/model impact:** evaluation uses `model.eval()` and `torch.no_grad()`; it does not update optimizer or model state. It is nevertheless expensive and invalid as generalization validation.\n\n**Required V2 evaluator behavior:** train CE/checkpoint every epoch; optional fixed 5–10 train sanity decodes; only a frozen, disjoint decode-dev may drive full decode/checkpoint selection. Evaluation must retain deterministic greedy decoding, finite `MAX_NEW_TOKENS`, EOS tracking, and parser oversize protection.\n\n**Current-run safety:** the active process has no evaluator flag and serializes no optimizer/scheduler state. It cannot be safely interrupted and exactly resumed with its current implementation. This audit therefore does not alter or stop it.\n''')
 (OUT/'TRAIN_SELF_DECODE_INTERPRETATION.md').write_text('''# TRAIN_SELF_DECODE interpretation\n\nThe existing per-epoch outputs are retained as `TRAIN_SELF_DECODE`. They may measure memorization, EOS/runaway behavior, and training-chain sanity. They must not be called dev accuracy, held-out performance, or generalization.\n''')
 print(json.dumps({'train':len(tids),'current_dev':len(current_dev_ids),'intersection':len(tids&current_dev_ids),'independent_dev_available':False},indent=2))
if __name__=='__main__': main()
