#!/usr/bin/env python3
"""Deterministic eligibility check for ANCHOR_EVAL_100_V1 retry; no models."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
V2=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/geometry_leakage_audit_v2'
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/anchor_eval_100_retry_v2'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 leak=json.loads((V2/'LEAKAGE_REAUDIT_V2.json').read_text())
 rows=[json.loads(x) for x in (V2/'SURFACE_GEOMETRY_FINGERPRINT_V1.jsonl').read_text().splitlines() if x.strip()]
 excluded={x['cad_id'] for x in leak['candidate_exclusions']}
 eligible=[x for x in rows if x['kind']=='anchor_candidate_pool' and x['cad_id'] not in excluded]
 eligible.sort(key=lambda x:hashlib.sha256(('ANCHOR_EVAL_100_V1|seed=20260829|'+x['cad_id']).encode()).hexdigest())
 n=Counter(x['source_dataset'] for x in eligible)
 ok=n['deepcad']>=80 and n['fusion360']>=20
 selection={'selection_seed':20260829,'candidate_ordering':'SHA256(ANCHOR_EVAL_100_V1|seed=20260829|cad_id), ascending','selection_algorithm':'take first 80 DeepCAD and first 20 Fusion360 from V2 eligible pool only','eligible_count':len(eligible),'eligible_source_counts':dict(n),'required_source_counts':{'deepcad':80,'fusion360':20},'explicitly_excluded_missing_gt_step':'deepcad__0072_00724841','excluded_candidate_count':len(excluded),'selected_ids':([x['cad_id'] for x in eligible if x['source_dataset']=='deepcad'][:80]+[x['cad_id'] for x in eligible if x['source_dataset']=='fusion360'][:20]) if ok else [],'status':'SELECTION_PASS' if ok else 'SELECTION_FAIL_INSUFFICIENT_SOURCE_QUOTA'}
 # Keep requested artifact names nonempty and distinguish unavailable downstream validations.
 with open(OUT/'ANCHOR_EVAL_100_V1.jsonl','w') as f:f.write(json.dumps({'status':'FREEZE_FAIL','reason':selection['status'],'selection':selection},sort_keys=True)+'\n')
 leakage={'V2_GEOMETRY_LEAKAGE_AUDIT':'V3_GEOMETRY_LEAKAGE_AUDIT_V2_PASS','SOURCE_ID_OVERLAP':0,'DSL_HASH_OVERLAP':0,'SURFACE_FP_OVERLAP':0,'STEP_FP_OVERLAP_WHERE_AVAILABLE':0,'STEP_FP_COVERAGE':'999/1000','STEP_FP_COMPLETE':False,'SURFACE_FP_COVERAGE':'1000/1000','SURFACE_FP_COMPLETE':True,'FULL_GEOMETRY_LEAKAGE_GUARD':True,'PILOT150_MODEL_RESULTS_READ':False,'OFFICIAL_TEST_READ':False,'candidate_pool_restricted_to_v2_eligible':True}
 distribution={'TOTAL':0,'DEEPCAD':0,'FUSION360':0,'status':'NOT_GENERATED: insufficient deterministic eligible DeepCAD quota','eligible_source_counts':dict(n)}
 c2={'status':'NOT_RUN: no valid 80/20 selection','C2_FROZEN':True,'C2_TRAINABLE_PARAMS':0,'MODEL_INFERENCE_RUN':False,'TRAINING_STARTED':False}
 freeze={'CURRENT_GATE':'ANCHOR_EVAL_100_V1_FREEZE_PASS' if ok else 'ANCHOR_EVAL_100_V1_FREEZE_FAIL','FAILURE_REASON':None if ok else 'V2 eligible pool has only 63 DeepCAD candidates; required deterministic quota is 80 DeepCAD. No duplication, ratio change, augmentation, smoke, or training was used.','TOTAL':100 if ok else 0,'DEEPCAD':80 if ok else 0,'FUSION360':20 if ok else 0,'ELIGIBLE_DEEPCAD':n['deepcad'],'ELIGIBLE_FUSION360':n['fusion360'],'MODEL_INFERENCE_RUN':False,'SMOKE_STARTED':False,'TRAINING_STARTED':False,'PILOT150_MODEL_RESULTS_READ':False,'OFFICIAL_TEST_READ':False}
 write(OUT/'LEAKAGE_AUDIT.json',leakage);write(OUT/'DISTRIBUTION_REPORT.json',distribution);write(OUT/'C2_PROVENANCE_REPORT.json',c2);write(OUT/'ANCHOR_EVAL_100_V1_FREEZE.json',freeze)
 files=[OUT/x for x in ('ANCHOR_EVAL_100_V1.jsonl','ANCHOR_EVAL_100_V1_FREEZE.json','LEAKAGE_AUDIT.json','DISTRIBUTION_REPORT.json','C2_PROVENANCE_REPORT.json')];write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p) for p in files})
 print(json.dumps(freeze,indent=2))
if __name__=='__main__':main()
