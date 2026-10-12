from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); OLD=ROOT/'ours3/cadquery_native_cohort_completion_v1'; OUT=ROOT/'ours3/zero_to_cad_canary_completion_v1'
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 old=json.loads((OLD/'CURRENT_CADQUERY6_AUDIT.json').read_text()); rows=old['rows']; valid=sum(r['execution_status']=='PASS' and r['step_reload']=='PASS' for r in rows)
 inp={'previous_valid_native_pair_n':5,'tank_excluded':True,'missing_case_n_before':3,'zero_to_cad_streaming_attempted':True,'dataset':'ADSKAILab/Zero-To-CAD-1m','network_status':'UNAVAILABLE','error':'Network is unreachable while connecting to huggingface.co','full_dataset_downloaded':False}
 (OUT/'INPUT_COHORT_RECOUNT.json').write_text(json.dumps(inp,indent=2)+'\n')
 (OUT/'ZERO_TO_CAD_STREAMING_AUDIT.json').write_text(json.dumps({'streaming_api':'load_dataset(..., streaming=True)','attempted':True,'status':'FAILED_NETWORK','full_download':False,'error':inp['error']},indent=2)+'\n')
 (OUT/'ZERO_TO_CAD_CANDIDATES.jsonl').write_text(json.dumps({'status':'NO_CANDIDATES_MATERIALIZED','reason':'external dataset unreachable; no source or STEP downloaded'})+'\n')
 (OUT/'ZERO_TO_CAD_EXECUTION_AUDIT.jsonl').write_text(''); (OUT/'ZERO_TO_CAD_PAIR_GEOMETRY.jsonl').write_text(''); (OUT/'ZERO_TO_CAD_SELECTED_CASES.json').write_text(json.dumps({'selected':[],'count':0},indent=2)+'\n')
 manifest={'count':valid,'status':'INCOMPLETE_NOT_CANARY8','records':rows,'external_zero_to_cad_selected':0,'cohort_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
 (OUT/'CADQUERY_NATIVE_CANARY8_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 report={'CURRENT_GATE':'CADQUERY_NATIVE_COHORT_STILL_INCOMPLETE','PREVIOUS_VALID_NATIVE_PAIR_N':valid,'MISSING_CASE_N_BEFORE':3,'ZERO_TO_CAD_SELECTED_N':0,'FINAL_CANARY_N':valid,'SOURCE_PARSE':f'{valid}/{valid}','SOURCE_EXEC':f'{valid}/{valid}','STEP_RELOAD':f'{valid}/{valid}','PAIR_GEOMETRY_VERIFIED':'NOT_ESTABLISHED','REVOLVE_PRESENT':'NO_VERIFIED_NATIVE_CANDIDATE','FILLET_PRESENT':'NO_VERIFIED_NATIVE_CANDIDATE','CHAMFER_PRESENT':'NO_VERIFIED_NATIVE_CANDIDATE','MULTI_OP_PRESENT':'YES_IN_LOCAL_BUT_NOT_COVERAGE_VERIFIED','TRAINING_RUN':'NO','PLACEMENT_CHANGED':'NO','C2_CHANGED':'NO','SONATA_CHANGED':'NO','SPATIALLM_CHANGED':'NO','DSL_CHANGED':'NO','CADQUERY_NATIVE_CANARY8_READY':'NO','NEXT_STEP':'MORE_NATIVE_DATA_REQUIRED','EXTERNAL_DATASET_STATUS':'UNAVAILABLE_NETWORK'}
 (OUT/'FINAL_REPORT.json').write_text(json.dumps(report,indent=2)+'\n'); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
