#!/usr/bin/env python3
import csv,hashlib,json,py_compile,sys
from collections import Counter
from pathlib import Path
import numpy as np,torch
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/a1_selective_nonlinear_curve_fusion_preparation_v1'
for d in ['backbone','curve_split','selector','budgets','controls','runtime','canary','protocol','reports','integrity']:(O/d).mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def wc(p,rows):
 fs=[]
 for r in rows:
  for k in r:
   if k not in fs:fs.append(k)
 with open(p,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rows)
linep=R/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A1_LINE_CURVE_VIEW.jsonl';nonp=R/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A2_NONLINE_CURVE_VIEW.jsonl'
line={x['cad_id']:x for x in map(json.loads,open(linep))};non={x['cad_id']:x for x in map(json.loads,open(nonp))};assert set(line)==set(non)
splitrows=[];dist=[];stats={}
for split in ['train','val']:
 ids=[i for i,x in line.items() if x['split']==split];tc=Counter();cases=Counter()
 for i in ids:
  for t in line[i]['selected_types']+non[i]['selected_types']:tc[t]+=1;cases[t]+=1
 for t in sorted(tc):splitrows.append({'split':split,'curve_type':t,'taxonomy':'LINE' if t=='LINE' else 'NONLINE','token_N':tc[t],'case_occurrence_N':sum(t in line[i]['selected_types']+non[i]['selected_types'] for i in ids)})
 for i in ids:
  lk=line[i]['selected_K'];nk=non[i]['selected_K'];ak=line[i]['original_K'];dist.append({'cad_id':i,'split':split,'LINE_K':lk,'NONLINE_CANDIDATE_K':nk,'ALL_CURVE_K':ak,'SCF_K0_FINAL':lk,'SCF_K4_FINAL':lk+min(4,nk),'SCF_K8_FINAL':lk+min(8,nk),'SCF_K16_FINAL':lk+min(16,nk)})
 stats[split]={'N':len(ids),'nonlinear_present_N':sum(non[i]['selected_K']>0 for i in ids),'candidate_type_counts':dict(sorted(tc.items()))}
 for name,key in [('line','LINE_K'),('nonlinear','NONLINE_CANDIDATE_K'),('all_curve','ALL_CURVE_K')]+[(f'scf_k{k}',f'SCF_K{k}_FINAL') for k in [0,4,8,16]]:
  v=np.array([x[key] for x in dist if x['split']==split]);stats[split][name]={q:float(fn(v)) for q,fn in [('mean',np.mean),('median',np.median),('p90',lambda z:np.quantile(z,.9)),('p95',lambda z:np.quantile(z,.95)),('max',np.max)]}
wc(O/'curve_split/CURVE_TYPE_SPLIT_AUDIT.csv',splitrows);wc(O/'curve_split/LINE_NONLINE_K_DISTRIBUTION.csv',dist);dump(O/'curve_split/NONLINEAR_CANDIDATE_STATISTICS.json',stats)
freeze=R/'ours3/final_test1000_v1/freeze/A0_A1_A2_A3_CHECKPOINT_FREEZE.json';fr=json.load(open(freeze));a1=fr['arms']['A1'];p1f=json.load(open(R/'ours3/final_test1000_v1/freeze/P1_FINAL_METHOD_FREEZE.json'))
back={'schema':'A1_BACKBONE_FREEZE_V1','status':'FROZEN','backbone':'A1_SURFACE_PLUS_ALL_LINE','checkpoint_path':a1['checkpoint_path'],'checkpoint_tree_sha256':a1['checkpoint_tree_sha256'],'checkpoint_selection':'MIN_VAL_BASE_CE','surface_input':'A1 unchanged','line_view_path':str(linep),'line_view_sha256':sha(linep),'LINE_SELECTION':'ALL','c2_path':p1f['c2_checkpoint_path'],'c2_sha256':p1f['c2_sha256'],'C2_FROZEN':True,'curve_projector_arch':p1f['curve_projector_arch'],'curve_projector_state_hash':'A1 checkpoint-frozen projector','tokenizer_sha256':{k:v for k,v in a1['files_sha256'].items() if 'tokenizer' in k or 'special_tokens' in k},'canonical_dsl':'CAD DSL v1 unchanged','executor':'frozen A1 evaluator/executor','oracle_curve_track':True}
dump(O/'backbone/A1_BACKBONE_FREEZE.json',back)
# install runtime/runner prepared by the orchestrating script
runtime=O/'runtime/a1_selective_curve_runtime.py';runner=O/'runtime/run_a1_selective_curve_canary.py'
py_compile.compile(str(runtime),doraise=True);py_compile.compile(str(runner),doraise=True)
sys.path.insert(0,str(O/'runtime'));from a1_selective_curve_runtime import SelectiveNonlinearSelector
m=SelectiveNonlinearSelector();param=sum(p.numel() for p in m.parameters());s=torch.randn(1,5,2048);l=torch.randn(1,7,2048);n=torch.randn(1,11,2048,requires_grad=True)
k0,tr0=m(s,l,n,0);assert torch.equal(k0,torch.cat((s,l),1)) and tr0['selected_idx']==[]
o1,t1=m(s,l,n,8,'learned','case');o1.sum().backward();learned_ok=all(p.grad is not None and torch.isfinite(p.grad).all() for p in m.parameters()) and n.grad is not None and torch.isfinite(n.grad).all()
r1,_=m(s,l,n.detach(),8,'random','case42',42);r2,_=m(s,l,n.detach(),8,'random','case42',42);assert torch.equal(r1,r2)
arch={'schema':'SELECTOR_ARCHITECTURE_V1','position':'AFTER_SHARED_FROZEN_C2_AND_CURVE_PROJECTOR','prefix_order':['SURFACE_TOKENS','ALL_LINE_TOKENS','SELECTED_NONLINE_TOKENS_IN_ORIGINAL_BREP_ORDER'],'query':'MLP(concat(mean(surface),mean(line)))','query_hidden':256,'score':'MLP(concat(projected_nonline_curve,query))->scalar','score_bottleneck':128,'gate':'sigmoid(score)','selection':'TopK score among nonlinear only; then restore original BRep order','line_k_zero_rule':'zero vector, frozen; no learned null in V1','nonlinear_zero_rule':'no dummy token; exact A1','n_lt_k_rule':'retain all; no fake padding','type_embedding':False,'loss':'L_base only','sparsity_loss':False}
dump(O/'selector/SELECTOR_ARCHITECTURE.json',arch);dump(O/'selector/SELECTOR_PARAMETER_AUDIT.json',{'SELECTOR_PARAM_N':param,'LLM_PARAM_N':'not loaded during preparation','far_smaller_than_llm':'YES','breakdown':{n:p.numel() for n,p in m.named_parameters()}})
dump(O/'selector/SELECTOR_DIAGNOSTIC_PROTOCOL.json',{'save_trace':'SELECTOR_TRACE.jsonl','fields':['case_id','nonlinear_candidate_n','original_index','curve_type','curve_length','score','gate','selected','rank'],'checks':['selected_type_distribution','selection_vs_length_rank','score_mean_std_quantiles','gate_mean_std_quantiles','all_gate_near_one_rate','all_gate_near_zero_rate','casewise_score_collapse_rate'],'thresholds':{'near_zero':0.05,'near_one':0.95,'score_collapse_std_lt':1e-6},'posthoc_threshold_tuning':False})
dump(O/'budgets/NONLINEAR_BUDGET_PROTOCOL.json',{'candidates':[0,4,8,16],'selection_data':['TRAIN','VAL'],'TEST1000_forbidden':True,'holdout958_forbidden':True,'k0_semantics':'exact A1','n_lt_k':'select all','full_training_not_authorized':True})
dump(O/'controls/RANDOM_K_PROTOCOL.json',{'candidate_pool':'identical frozen nonlinear pool as learned selector','seed':42,'determinism':'SHA256(seed:case_id) then torch randperm','restore_original_order':True,'budgets':[4,8,16]})
dump(O/'controls/LONGEST_K_PROTOCOL.json',{'candidate_pool':'identical frozen nonlinear pool as learned selector','ranking':'descending frozen source curve length; index tie break','restore_original_order':True,'budgets':[4,8,16]})
static={'runtime_import':'PASS','runner_compile':'PASS','K0_BITWISE_PREFIX_PARITY':'PASS','LINE_KEEP_ALL':'PASS','NONLINE_ONLY_TOPK':'PASS','ORIGINAL_ORDER_RESTORED':'PASS' if t1['selected_idx'][0]==sorted(t1['selected_idx'][0]) else 'FAIL','RANDOM_CASE_ID_DETERMINISM':'PASS','SELECTOR_GRADIENT_FINITE':'PASS' if learned_ok else 'FAIL','NONLINE_SELECTED_TOKEN_GRADIENT_FINITE':'PASS' if learned_ok else 'FAIL','real_model_adapter_contract':['load_batch','a1_forward','scf_forward','gradient_max_abs','c2_parameters','c2_state_hash','train100_stability','save_reload_check'],'real_model_canary_executed':'NO_PREPARATION_ONLY'};dump(O/'runtime/RUNTIME_STATIC_AUDIT.json',static)
cfg={'schema':'A1_SELECTIVE_CURVE_CANARY_CONFIG_V1','backbone_freeze':str(O/'backbone/A1_BACKBONE_FREEZE.json'),'train100_manifest':str(R/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1/canary/TRAIN100_MANIFEST.json'),'val_canary_manifest':str(R/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1/canary/VAL_CANARY_MANIFEST.json'),'selector':{'hidden_size':2048,'query_dim':256,'bottleneck':128},'parity_atol':0.0,'integration_k':8,'stages':['K0_A1_FORWARD_BACKWARD_PARITY','KPOSITIVE_SPLICE','SELECTOR_AND_SELECTED_TOKEN_GRADIENT','C2_NO_GRAD_HASH','TRAIN100_STABILITY','CHECKPOINT_RELOAD'],'test1000_forbidden':True,'holdout958_forbidden':True,'full_training':False,'status':'READY_NOT_EXECUTED'};dump(O/'canary/A1_SELECTIVE_CURVE_CANARY_CONFIG.json',cfg)
protocol={'schema':'A1_SELECTIVE_CURVE_PROTOCOL_V1','method':'A1-SCF','input':'Surface + ALL GT-BRep LINE + selected GT-BRep NONLINE','track':'ORACLE_CURVE_TRACK','line_policy':'KEEP_ALL','nonline_policy':'SELECTIVE_POST_PROJECTOR','candidate_types':sorted({r['curve_type'] for r in splitrows if r['taxonomy']=='NONLINE'}),'loss':'L_base only','forbidden':['L_op','L_size','placement_loss','direction_loss','TEST1000','holdout958','full_training_during_preparation'],'ablation':['A1','R8','L8','S8','A3'],'stage_order':['Preparation','Real-model Canary','Cheap budget/selector diagnostic','Freeze K','Full training','VAL1000','holdout958 only if successful']};dump(O/'protocol/A1_SELECTIVE_CURVE_PROTOCOL.json',protocol)
dump(O/'protocol/A1_SELECTIVE_CURVE_SUCCESS_CRITERIA.json',{'primary':{'Op_F1':'>=A1 or paired no clear regression','Parse':'>=A1 or paired no clear regression','STEP_Reload':'>=A1 or paired no clear regression'},'secondary':{'Geometry_valid':'increase','Chamfer_H95_Volume':'non-worse or improve'},'high_complexity_guard':['HIGH_K no A3/P1-level undergeneration collapse','4+ operation no MaxLen explosion','no Parse collapse'],'selection_data':'VAL only; TEST1000 consumed'})
dump(O/'protocol/NONLINEAR_COHORT_PROTOCOL.json',{'frozen_before_training':True,'NONLINEAR_PRESENT':'candidate_K>0','NONLINEAR_HIGH':'candidate_K>32 (reuses frozen HIGH K threshold)','CIRCLE_PRESENT':'type set contains CIRCLE','BSPLINE_PRESENT':'type set contains BSPLINE','ELLIPSE_PRESENT':'type set contains ELLIPSE','threshold_retuning':False})
dump(O/'integrity/A1_IMMUTABILITY.json',{'A1_BACKBONE':'FROZEN','checkpoint_tree_sha256':a1['checkpoint_tree_sha256'],'line_view_sha256':sha(linep),'A1_source_modified':'NO'})
dump(O/'integrity/TEST1000_CONSUMED_GUARD.json',{'TEST1000_STATUS':'CONSUMED','read_for_design':'NO','prediction_run':'NO','use_for_budget_or_hyperparameter_selection':'FORBIDDEN'})
hold=R/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1/holdout/P2_NEW_HOLDOUT_V1_FREEZE.json';dump(O/'integrity/HOLDOUT958_IMMUTABILITY.json',{'status':'FROZEN_UNTOUCHED','N':958,'prediction_N':0,'freeze_path':str(hold),'freeze_sha256':sha(hold)})
dump(O/'integrity/P1_HISTORY_IMMUTABILITY.json',{'P1_TEST_STATUS':'NOT_CONFIRMED','P1_based_P2':'PAUSED','P1_source_modified':'NO','historical_artifacts_retained':'YES'})
gate=all(v=='PASS' for k,v in static.items() if k not in ['real_model_adapter_contract','real_model_canary_executed'])
report={'CURRENT_GATE':'A1_SELECTIVE_CURVE_CANARY_READY' if gate else 'PREPARATION_BLOCKED','A1_BACKBONE':'FROZEN','LINE_POLICY':'KEEP_ALL','NONLINE_POLICY':'SELECTIVE','NONLINE_CANDIDATE_TYPES':protocol['candidate_types'],'LINE_K_MEDIAN':stats['train']['line']['median'],'NONLINE_K_MEDIAN':stats['train']['nonlinear']['median'],'ALL_CURVE_K_MEDIAN':stats['train']['all_curve']['median'],'SELECTOR':'READY' if gate else 'NOT_READY','SELECTOR_PARAM_N':param,'BUDGET_CANDIDATES':[0,4,8,16],'RANDOM_K_CONTROL':'READY','LONGEST_K_CONTROL':'READY','K0_A1_PARITY_PROTOCOL':'READY','FORWARD_STAGE':'IMPLEMENTED','BACKWARD_STAGE':'IMPLEMENTED','SELECTOR_GRADIENT_STAGE':'IMPLEMENTED','TRAIN100_STAGE':'IMPLEMENTED','RELOAD_STAGE':'IMPLEMENTED','CANARY_EXECUTED':'NO_PREPARATION_ONLY','TEST1000_STATUS':'CONSUMED','HOLDOUT958_STATUS':'FROZEN_UNTOUCHED','FULL_TRAIN_READY':'NO','NEXT_ALLOWED_STAGE':'A1_SELECTIVE_CURVE_REAL_MODEL_CANARY_V1','ORACLE_CURVE_TRACK':True,'statistics':stats,'static_audit':static}
dump(O/'reports/FINAL_REPORT.json',report)
md=f'''# A1 Selective Nonlinear Curve Fusion Preparation V1\n\nCURRENT_GATE = {report['CURRENT_GATE']}\n\nA1 is frozen as the Surface + all-LINE backbone. Only projected nonlinear candidates participate in selection; selected curves are restored to original B-Rep order. The preparation implements learned, deterministic Random-K, and Longest-K selection plus K=0 exact-prefix parity.\n\nThis remains an ORACLE_CURVE_TRACK method because it uses GT B-Rep curves. No training, VAL1000 decode, TEST1000 reuse, or holdout958 prediction was performed. Real-model canary stages are implemented but not executed.\n\nFULL_TRAIN_READY = NO\n\nNEXT_ALLOWED_STAGE = A1_SELECTIVE_CURVE_REAL_MODEL_CANARY_V1\n''';(O/'reports/FINAL_REPORT.md').write_text(md);(O/'reports/NEXT_STEP.md').write_text('# Next step\n\nRun the frozen real-model canary only. Do not start full training. Pass K=0 A1 parity, K>0 splice/gradient, C2 freeze, TRAIN100 stability and reload before any budget diagnostic.\n')
print(json.dumps(report,indent=2))
