#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/a1_selective_curve_real_model_canary_v1'
for d in ['gpu','data','parity','selection','gradients','controls','train100','val100','reload','reports','integrity']:(O/d).mkdir(parents=True,exist_ok=True)
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(p):h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
linep=R/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A1_LINE_CURVE_VIEW.jsonl';nonp=R/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A2_NONLINE_CURVE_VIEW.jsonl'
L={x['cad_id']:x for x in map(json.loads,open(linep))};N={x['cad_id']:x for x in map(json.loads,open(nonp))}
def select(split):
 present=sorted(i for i in L if L[i]['split']==split and N[i]['selected_K']>0); absent=sorted(i for i in L if L[i]['split']==split and N[i]['selected_K']==0)
 chosen=[]
 for t in ['BSPLINE','ELLIPSE','CIRCLE']:
  z=[i for i in present if t in N[i]['selected_types']]
  if z and z[0] not in chosen:chosen.append(z[0])
 chosen += [i for i in present if i not in chosen][:50-len(chosen)];chosen+=absent[:50]
 return [{'cad_id':i,'split':split,'cohort':'NONLINE_PRESENT' if N[i]['selected_K'] else 'NONLINE_ABSENT','LINE_K':L[i]['selected_K'],'NONLINE_K':N[i]['selected_K'],'nonlinear_types':sorted(set(N[i]['selected_types'])),'selection_rule':'type-earliest coverage then lexical ascending' if N[i]['selected_K'] else 'lexical ascending first50'} for i in chosen]
tr,va=select('train'),select('val');dump(O/'data/A1_SCF_CANARY_TRAIN100_MANIFEST.json',{'N':100,'rows':tr});dump(O/'data/A1_SCF_CANARY_VAL100_MANIFEST.json',{'N':100,'rows':va})
test={json.loads(x)['cad_id'] for x in open(R/'ours3/exact9998_v1/EXACT9998_TEST.jsonl')};hp=R/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1/holdout/P2_NEW_HOLDOUT_V1_MANIFEST.json';hd=json.load(open(hp));
def ids(x):
 if isinstance(x,list):return {str(y.get('cad_id',y.get('id',''))) for y in x if isinstance(y,dict)}
 for k in ['rows','cases','samples','items']:
  if isinstance(x,dict) and isinstance(x.get(k),list):return ids(x[k])
 return set()
hold=ids(hd);ti={x['cad_id'] for x in tr};vi={x['cad_id'] for x in va};iso={'TRAIN100_N':len(ti),'VAL100_N':len(vi),'TRAIN_PRESENT_N':sum(x['cohort']=='NONLINE_PRESENT' for x in tr),'TRAIN_ABSENT_N':sum(x['cohort']=='NONLINE_ABSENT' for x in tr),'VAL_PRESENT_N':sum(x['cohort']=='NONLINE_PRESENT' for x in va),'VAL_ABSENT_N':sum(x['cohort']=='NONLINE_ABSENT' for x in va),'TRAIN_TEST_INTERSECTION_N':len(ti&test),'VAL_TEST_INTERSECTION_N':len(vi&test),'TRAIN_HOLDOUT_INTERSECTION_N':len(ti&hold),'VAL_HOLDOUT_INTERSECTION_N':len(vi&hold),'PASS':not((ti|vi)&(test|hold))};dump(O/'data/A1_SCF_CANARY_DATA_ISOLATION.json',iso)
dump(O/'gpu/SAFE_GPU_AUDIT.json',{'captured_local':'2026-09-14T10:27:52+08:00','single_check_only':True,'SAFE_GPU_FOUND':'YES','GPU_ID':1,'free_memory_MiB':45586,'utilization_percent':0,'compute_process_n':0,'final_test_process':False,'unknown_activity':False,'selected_rule':'lowest completely idle safe GPU','gpu_run_started':False,'reason_not_started':'REAL_MODEL_ADAPTER_MISSING'})
prep=R/'ours3/a1_selective_nonlinear_curve_fusion_preparation_v1';runner=prep/'runtime/run_a1_selective_curve_canary.py'
block={'CURRENT_GATE':'A1_SCF_CANARY_IMPLEMENTATION_BLOCKED','SAFE_GPU_FOUND':'YES','GPU_ID':1,'blocker':'No importable adapter module exporting build_canary_adapter(config); runner cannot load the real SpatialLM/A1 model path.','evidence':{'runner':str(runner),'runner_sha256':sha(runner),'requires_cli':'--adapter-module','adapter_search_result':'NONE'},'model_loaded':False,'training_started':False,'gpu_run_started':False,'no_fake_canary':True,'required_fix':'Implement and statically audit a concrete A1SpatialLMCanaryAdapter wired to pristine A1 initialization, frozen C2, A1 CurveProjector, dataset manifests, optimizer/scheduler, checkpoint save/reload, then rerun one GPU gate.','NEXT_ALLOWED_STAGE':'IMPLEMENT_A1_SCF_REAL_MODEL_ADAPTER_V1','FULL_TRAIN_READY':'NO','data_isolation':iso}
dump(O/'reports/FINAL_REPORT.json',block);(O/'reports/FINAL_REPORT.md').write_text('# A1-SCF real-model canary\n\nCURRENT_GATE = A1_SCF_CANARY_IMPLEMENTATION_BLOCKED\n\nA safe GPU was found, but the frozen runner requires a real-model adapter that does not exist. No model was loaded and no training was started; static selector checks were not reported as a real-model canary. TRAIN100/VAL100 manifests and isolation were frozen successfully.\n');(O/'reports/NEXT_STEP.md').write_text('# Next step\n\nImplement `A1SpatialLMCanaryAdapter` for the real A1/SpatialLM training path, then repeat the single safe-GPU gate and run the canary. Full training remains forbidden.\n')
guard={'NEW_TRAINING':'NO','NEW_DECODE':'NO','TEST1000_STATUS':'CONSUMED','TEST1000_REUSED':'NO','HOLDOUT958_CHANGED':'NO','HOLDOUT958_PREDICTION_N':0}
dump(O/'integrity/TEST1000_CONSUMED_GUARD.json',guard);dump(O/'integrity/HOLDOUT958_IMMUTABILITY.json',guard);dump(O/'integrity/A1_IMMUTABILITY.json',{'A1_CHANGED':'NO','C2_CHANGED':'NO','CurveProjector_CHANGED':'NO','checkpoint_changed':'NO'})
print(json.dumps(block,indent=2))
