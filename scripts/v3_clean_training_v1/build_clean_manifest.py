#!/usr/bin/env python3
"""Build the read-only CLEAN_V3 cohort from frozen V3 audit evidence."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
DATA=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json'
AUDIT=ROOT/'ours3/v3_sft_chain_audit_v2'
OUT=ROOT/'ours3/v3_clean_training_v1/data'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=json.loads(DATA.read_text())['records']
    no={x['cad_id']:x for x in json.loads((AUDIT/'GEOMETRY_BUDGET_AUDIT.json').read_text())['per_cad']}
    gt={x['cad_id']:x for x in json.loads((AUDIT/'GT_EXEC_AUDIT.json').read_text())['per_cad']}
    keep=[];excluded=[]
    for r in rows:
        cid=r['cad_id']; b=no[cid]; g=gt[cid]
        # Full target includes the terminal eot and must fit the actual M2 splice.
        overflow=(b.get('m2_predicted_spliced_len_full_target') is None or
                  b['m2_predicted_spliced_len_full_target']>4096)
        step=not (g['dsl_parse_success'] and g['dsl_execute_success'] and g['occ_shape_non_null'] and g['brep_valid'] and g['step_write_success'] and g['step_reload_success'])
        if overflow or step:
            excluded.append({'cad_id':cid,'source':r.get('source_dataset'),'reasons':(["context_overflow"] if overflow else [])+(["step_failure"] if step else []),'actual_final_sequence_length':b.get('m2_predicted_spliced_len_full_target'),'gt_execution':{k:g[k] for k in ('dsl_parse_success','dsl_execute_success','occ_shape_non_null','brep_valid','step_write_success','step_reload_success')}})
        else:
            rr=dict(r);rr['clean_contract']={'actual_final_sequence_length_m2':b['m2_predicted_spliced_len_full_target'],'actual_surface_tokens':b['surface_encoder_output_tokens'],'full_target_including_eos':b['gt_dsl_tokens_raw'],'no_silent_truncation':True,'gt_step_reload':True};keep.append(rr)
    def src(xs,name):return sum(x.get('source_dataset')==name for x in xs)
    overlap=sum(len(x['reasons'])>1 for x in excluded)
    payload={'name':'CLEAN_V3','protocol':'actual M2 final splice <=4096 AND complete GT staged STEP success; no target slicing','original_count':len(rows),'no_trunc':sum(not ('context_overflow' in x['reasons']) for x in excluded)+len(keep),'step_valid':sum(not ('step_failure' in x['reasons']) for x in excluded)+len(keep),'intersection_count':len(keep),'deepcad':src(keep,'deepcad'),'fusion360':src(keep,'fusion360'),'records':keep,'forbidden_reads':{'decode_dev50':False,'pilot150':False,'anchor_eval100':False,'official_test':False}}
    exc={'name':'EXCLUDED_V3','count':len(excluded),'context_overflow':sum('context_overflow' in x['reasons'] for x in excluded),'step_failure':sum('step_failure' in x['reasons'] for x in excluded),'overlap':overlap,'records':excluded}
    (OUT/'CLEAN_V3_MANIFEST.json').write_text(json.dumps(payload,indent=2)+'\n')
    (OUT/'EXCLUDED_V3_MANIFEST.json').write_text(json.dumps(exc,indent=2)+'\n')
    print(json.dumps({k:payload[k] for k in ('original_count','no_trunc','step_valid','intersection_count','deepcad','fusion360') }|{k:exc[k] for k in ('context_overflow','step_failure','overlap')},indent=2))
if __name__=='__main__':main()
