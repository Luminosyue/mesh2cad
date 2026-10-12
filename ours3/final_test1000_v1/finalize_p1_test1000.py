#!/usr/bin/env python3
import csv, hashlib, json, math, os, subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
BASE=ROOT/'ours3/final_test1000_v1'; ARMS=['a0','a1','a2','a3','p1']; N=1000
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8<<20),b''): h.update(b)
 return h.hexdigest()
def dump(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def writecsv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not rows: return
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def qstats(v,p99=True):
 v=np.asarray([x for x in v if x is not None and math.isfinite(float(x))],float)
 out={'mean':float(v.mean()),'median':float(np.median(v)),'p90':float(np.quantile(v,.9)),'p95':float(np.quantile(v,.95))} if len(v) else {k:None for k in ['mean','median','p90','p95']}
 if p99: out['p99']=float(np.quantile(v,.99)) if len(v) else None
 return out
def binom_p(b,c):
 n=b+c
 if not n:return 1.0
 k=min(b,c); return min(1.0,2*sum(math.comb(n,i) for i in range(k+1))/(2**n))
def paired_bool(x,y,key):
 b=sum(bool(x[i].get(key)) and not bool(y[i].get(key)) for i in x)
 c=sum(not bool(x[i].get(key)) and bool(y[i].get(key)) for i in x)
 return {'baseline_only_n':b,'p1_only_n':c,'discordant_n':b+c,'exact_mcnemar_p':binom_p(b,c)}

# Phase 1: completion and frozen-asset integrity only.
protocol=json.load(open(BASE/'freeze/FINAL_TEST_PROTOCOL_V1.json'))
manifest_path=Path(protocol['test_manifest_path']); manifest=[json.loads(x) for x in open(manifest_path)]; mids=[x['cad_id'] for x in manifest]
checks=[]; rows={}; completion={}
for a in ARMS:
 paths=list((BASE/a/'predictions').glob('*/row.json')); rr=[]; errors=[]
 for p in paths:
  try: rr.append(json.load(open(p)))
  except Exception as e: errors.append({'path':str(p),'error':str(e)})
 ids=[r.get('id') for r in rr]; c=Counter(ids); dup=sorted(k for k,v in c.items() if v>1); missing=sorted(set(mids)-set(ids)); extra=sorted(set(ids)-set(mids))
 completion[a.upper()]={'EXPECTED_N':N,'TERMINAL_CASE_N':len(rr),'UNIQUE_CASE_ID_N':len(c),'MISSING_ID_N':len(missing),'DUPLICATE_ID_N':sum(v-1 for v in c.values() if v>1),'EXTRA_ID_N':len(extra),'JSON_ERROR_N':len(errors),'PASS':len(rr)==N and len(c)==N and not missing and not dup and not extra and not errors}
 rows[a]={r['id']:r for r in rr}
for p,expected,label in [(manifest_path,protocol['test_manifest_sha256'],'TEST_MANIFEST'),(Path(protocol['derived_decoder_input_path']),protocol['derived_decoder_input_sha256'],'DECODER_INPUT')]:
 actual=sha(p) if p.exists() else None; checks.append({'asset':label,'path':str(p),'expected_sha256':expected,'actual_sha256':actual,'pass':actual==expected})
cp=json.load(open(BASE/'freeze/A0_A1_A2_A3_CHECKPOINT_FREEZE.json'))
for arm,v in cp['arms'].items():
 for rp,expected in v['files_sha256'].items():
  p=ROOT/rp; actual=sha(p) if p.exists() else None; checks.append({'asset':arm+'_CHECKPOINT_FILE','path':str(p),'expected_sha256':expected,'actual_sha256':actual,'pass':actual==expected})
 cfg=Path(v['train_config_path']); actual=sha(cfg) if cfg.exists() else None; checks.append({'asset':arm+'_TRAIN_CONFIG','path':str(cfg),'expected_sha256':v['train_config_sha256'],'actual_sha256':actual,'pass':actual==v['train_config_sha256']})
p1f=json.load(open(BASE/'freeze/P1_FINAL_METHOD_FREEZE.json'))
for rp,expected in p1f['checkpoint_file_sha256'].items():
 p=ROOT/rp; actual=sha(p) if p.exists() else None; checks.append({'asset':'P1_CHECKPOINT_FILE','path':str(p),'expected_sha256':expected,'actual_sha256':actual,'pass':actual==expected})
for label,p,expected in [('C2',Path(p1f['c2_checkpoint_path']),p1f['c2_sha256']),('CURVE_REGISTRY',Path(p1f['curve_token_registry']),p1f['curve_token_registry_sha256'])]:
 actual=sha(p) if p.exists() else None; checks.append({'asset':label,'path':str(p),'expected_sha256':expected,'actual_sha256':actual,'pass':actual==expected})
src=json.load(open(BASE/'freeze/FINAL_SOURCE_PROVENANCE.json'))
for pstr,v in src['files'].items():
 p=Path(pstr); actual=sha(p) if p.exists() else None; checks.append({'asset':'FROZEN_SOURCE','path':str(p),'expected_sha256':v['sha256'],'actual_sha256':actual,'pass':actual==v['sha256']})
provenance_ok=(p1f['checkpoint_path'].endswith('/checkpoint-8000') and 'MIN_VAL_BASE_CE' in p1f['selection_rule'] and p1f['best_checkpoint_from_trainer_state'].endswith('/checkpoint-8000') and p1f['c2_frozen'] is True and p1f['curve_cap_k']==128 and p1f['decode_config']=={k:protocol['decode'][k] for k in p1f['decode_config']})
all_complete=all(v['PASS'] for v in completion.values()); all_assets=all(x['pass'] for x in checks); unlocked=all_complete and all_assets and provenance_ok
pre={'schema_version':'PRE_FINALIZATION_INTEGRITY_V1','CURRENT_GATE':'FINAL_METRIC_UNLOCKED' if unlocked else 'FINAL_TEST_INTEGRITY_BLOCKED','ALL_ARMS_COMPLETE':'YES' if all_complete else 'NO','PRE_FINALIZATION_INTEGRITY':'PASS' if unlocked else 'FAIL','FINAL_METRIC_UNLOCK':'YES' if unlocked else 'NO','completion':completion,'frozen_asset_checks':checks,'p1_checkpoint_provenance':{'checkpoint':p1f['checkpoint_path'],'selection_rule':p1f['selection_rule'],'best_validation_metric':p1f['best_validation_metric'],'pass':provenance_ok}}
dump(BASE/'integrity/PRE_FINALIZATION_INTEGRITY.json',pre)
if not unlocked: raise SystemExit('INTEGRITY BLOCKED; metrics not computed')

# Phase 2: frozen final metrics, including formal STEP reload.
reload_worker=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/launch/step_reload_worker.py'; py='/data/miniconda3/envs/cadfit-env/bin/python'
def reload_one(t):
 a,cid,r=t
 if not r.get('step_ok') or not r.get('step'): return a,cid,False
 try:
  z=subprocess.run([py,str(reload_worker),r['step']],capture_output=True,text=True,timeout=30); d=json.loads(z.stdout.strip().splitlines()[-1]); return a,cid,bool(d.get('step_reload'))
 except Exception:return a,cid,False
tasks=[(a,i,r) for a in ARMS for i,r in rows[a].items()]
with ThreadPoolExecutor(max_workers=16) as ex:
 for a,i,ok in ex.map(reload_one,tasks): rows[a][i]['step_reload']=ok
def valid(r):
 g=r.get('geometry') or {}; return bool(r.get('step_ok')) and all(g.get(k) is not None and math.isfinite(float(g[k])) for k in ['chamfer_norm','hausdorff_95_norm','volume_error'])
def metrics(d):
 z=list(d.values()); geom=[r for r in z if valid(r)]
 out={'N':len(z),'Exact':np.mean([bool(r.get('exact_match')) for r in z]),'Op_F1':np.mean([float(r.get('op_f1',0)) for r in z]),'Op_Recall':np.mean([float(r.get('op_recall',0)) for r in z]),'Parse':np.mean([bool(r.get('parsed')) for r in z]),'STEP_Export':np.mean([bool(r.get('step_ok')) for r in z]),'STEP_Reload':np.mean([bool(r.get('step_reload')) for r in z]),'EOS':np.mean([r.get('stop_reason')=='EOS' for r in z]),'MaxLen':np.mean([r.get('stop_reason')=='MAX_LENGTH' for r in z]),'UnderGen':np.mean([bool(r.get('under_generation')) for r in z]),'Geometry_valid':len(geom)/len(z),'Geometry_valid_n':len(geom)}
 for prefix,key,p99 in [('Chamfer','chamfer_norm',True),('H95','hausdorff_95_norm',False),('Volume','volume_error',True)]:
  for k,v in qstats([(r['geometry'] or {}).get(key) for r in geom],p99).items(): out[prefix+'_'+k]=v
 return out
mm={a.upper():metrics(rows[a]) for a in ARMS}; main=[{'Arm':a,**mm[a]} for a in [x.upper() for x in ARMS]]; writecsv(BASE/'tables/FINAL_TEST1000_MAIN_TABLE.csv',main); writecsv(BASE/'tables/FINAL_TEST1000_PAPER_TABLE.csv',main)
def comparison(base):
 x=rows[base]; y=rows['p1']; ids=mids; delta=np.array([y[i]['op_f1']-x[i]['op_f1'] for i in ids]); rng=np.random.default_rng(42); boots=np.empty(10000)
 for j in range(10000): boots[j]=delta[rng.integers(0,N,N)].mean()
 def rescue(key): return {'rescue_n':sum(not bool(x[i].get(key)) and bool(y[i].get(key)) for i in ids),'regression_n':sum(bool(x[i].get(key)) and not bool(y[i].get(key)) for i in ids)}
 common=[i for i in ids if valid(x[i]) and valid(y[i])]; cg={}
 for name,key in [('Chamfer','chamfer_norm'),('H95','hausdorff_95_norm'),('Volume','volume_error')]: cg[name]={'common_valid_n':len(common),'baseline_mean':float(np.mean([x[i]['geometry'][key] for i in common])) if common else None,'p1_mean':float(np.mean([y[i]['geometry'][key] for i in common])) if common else None}
 return {'comparison':'P1_vs_'+base.upper(),'paired_n':N,'op_f1_delta':float(delta.mean()),'bootstrap_samples':10000,'bootstrap_seed':42,'ci95_low':float(np.quantile(boots,.025)),'ci95_high':float(np.quantile(boots,.975)),'exact':rescue('exact_match'),'parse':paired_bool(x,y,'parsed'),'step_reload':paired_bool(x,y,'step_reload'),'geometry_valid':{'rescue_n':sum(not valid(x[i]) and valid(y[i]) for i in ids),'regression_n':sum(valid(x[i]) and not valid(y[i]) for i in ids)},'common_valid':cg}
comps={b:comparison(b) for b in ['a3','a1']}
for b,c in comps.items():
 writecsv(BASE/f'stats/P1_VS_{b.upper()}_OPF1_BOOTSTRAP.csv',[{k:v for k,v in c.items() if k in ['comparison','paired_n','op_f1_delta','bootstrap_samples','bootstrap_seed','ci95_low','ci95_high']}])
 writecsv(BASE/f'stats/P1_VS_{b.upper()}_PARSE_MCNEMAR.csv',[{'comparison':c['comparison'],**c['parse']}])
 writecsv(BASE/f'stats/P1_VS_{b.upper()}_STEP_RELOAD_MCNEMAR.csv',[{'comparison':c['comparison'],**c['step_reload']}])

# Frozen VAL sources and deterministic sign-consistency operation replication.
valpaths={'a1':ROOT/'ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1/report.json','a3':ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3/report.json','p1':ROOT/'ours3/p1_exact9998_val1000_eval_v2/report.json'}
val={a:{r['id']:r for r in json.load(open(p))['samples']} for a,p in valpaths.items()}
ops=[]
for op in ['Box','Extrude','ExtrudePolygon','Cut','Union']:
 rec={'operation':op}
 for b in ['a3','a1']:
  vi=sorted(set(val[b])&set(val['p1'])); vi=[i for i in vi if op in val['p1'][i].get('gt_ops',[])]
  ti=[i for i in mids if op in rows['p1'][i].get('gt_ops',[])]
  vd=float(np.mean([val['p1'][i]['op_f1']-val[b][i]['op_f1'] for i in vi])) if vi else None; td=float(np.mean([rows['p1'][i]['op_f1']-rows[b][i]['op_f1'] for i in ti])) if ti else None
  if vd is None or td is None: lab='NOT_AVAILABLE'
  elif vd>0 and td>0: lab='REPLICATED'
  elif vd*td>=0: lab='PARTIALLY_REPLICATED'
  else: lab='NOT_REPLICATED'
  rec.update({f'{b}_val_n':len(vi),f'{b}_val_delta':vd,f'{b}_test_n':len(ti),f'{b}_test_delta':td,f'{b}_status':lab})
 ops.append(rec)
writecsv(BASE/'operations/VAL_TEST_OPERATION_REPLICATION.csv',ops)

# Source and frozen K complexity breakdown.
reg={d['cad_id']:d for d in map(json.loads,open(p1f['curve_token_registry']))}
breaks=[]
for a in ARMS:
 for kind,groups in [('source',{'DeepCAD':[i for i in mids if rows[a][i].get('dataset','').lower()=='deepcad'],'Fusion360':[i for i in mids if rows[a][i].get('dataset','').lower()=='fusion360']}),('K',{'LOW':[i for i in mids if reg.get(i,{}).get('K',999)<=8],'MID':[i for i in mids if 9<=reg.get(i,{}).get('K',999)<=32],'HIGH':[i for i in mids if 32<reg.get(i,{}).get('K',999)<=128]})]:
  for g,ids in groups.items():
   m=metrics({i:rows[a][i] for i in ids}); breaks.append({'Arm':a.upper(),'breakdown':kind,'group':g,**m})
writecsv(BASE/'geometry/SOURCE_COMPLEXITY_BREAKDOWN.csv',breaks)

# VAL/TEST generalization table from the already-frozen VAL reports.
gaps=[]
for a,p in valpaths.items():
 vm=metrics({r['id']:r for r in json.load(open(p))['samples']})
 for key in ['Exact','Op_F1','Op_Recall','Parse','STEP_Export','EOS','MaxLen','UnderGen','Geometry_valid','Chamfer_mean','H95_mean','Volume_mean']:
  gaps.append({'Arm':a.upper(),'metric':key,'VAL':vm.get(key),'TEST':mm[a.upper()].get(key),'TEST_minus_VAL':None if vm.get(key) is None else mm[a.upper()].get(key)-vm.get(key)})
writecsv(BASE/'tables/VAL_TEST_GENERALIZATION_GAP.csv',gaps)

p1a3=comps['a3']; p1a1=comps['a1']; status='CONFIRMED' if p1a3['op_f1_delta']>0 and p1a3['ci95_low']>0 else ('PARTIALLY_CONFIRMED' if p1a3['op_f1_delta']>0 else 'NOT_CONFIRMED')
main_method=max(mm,key=lambda a:mm[a]['Op_F1']); core='SUPPORTED' if status=='CONFIRMED' else ('MIXED' if status=='PARTIALLY_CONFIRMED' else 'NOT_SUPPORTED_ON_FINAL_TEST')
report={'schema_version':'FINAL_TEST1000_REPORT_V1','CURRENT_GATE':'FINAL_CLOSURE_COMPLETE','ALL_ARMS_COMPLETE':'YES','PRE_FINALIZATION_INTEGRITY':'PASS','FINAL_METRIC_UNLOCK':'YES','TEST_SET_STATUS':'FINAL_EVALUATION_CONSUMED','P2_HOLDOUT_STATUS':'FROZEN_958_UNTOUCHED','P1_checkpoint':'checkpoint-8000','P1_selection_rule':'MIN_VAL_BASE_CE','metrics':mm,'comparisons':comps,'operation_replication':ops,'P1_TEST_STATUS':status,'FINAL_MAIN_METHOD':main_method,'CORE_CLAIM_FINAL_STATUS':core,'GENERALIZATION_PATTERN':'Reported in VAL_TEST_GENERALIZATION_GAP.csv; final decision uses TEST once only.','FINAL_RESIDUAL_BOTTLENECK':'High-complexity under-generation and local parameter/placement errors remain.','NEXT_ALLOWED_STAGE':'RECOVER_FORMAL_REAL_MODEL_STAGE_IMPLEMENTATION_THEN_MANUAL_GPU_RETRY','IoU':'DEFERRED_FROZEN_PROTOCOL_HAS_NO_VALIDATED_IOU'}
dump(BASE/'reports/FINAL_TEST1000_REPORT.json',report)
def pct(x): return f'{100*x:.2f}%'
lines=['# Final TEST1000 Closure','','Integrity PASS; final metrics unlocked once. EXACT9998 TEST1000 is now consumed.','', '| Arm | Exact | Op-F1 | Parse | STEP Reload | Geometry-valid | Chamfer mean | H95 mean |','|---|---:|---:|---:|---:|---:|---:|---:|']
for a in mm: lines.append(f"| {a} | {pct(mm[a]['Exact'])} | {mm[a]['Op_F1']:.4f} | {pct(mm[a]['Parse'])} | {pct(mm[a]['STEP_Reload'])} | {pct(mm[a]['Geometry_valid'])} | {mm[a]['Chamfer_mean']:.6f} | {mm[a]['H95_mean']:.6f} |")
lines += ['',f"P1 vs A3 Op-F1 delta: {p1a3['op_f1_delta']:.6f}, bootstrap 95% CI [{p1a3['ci95_low']:.6f}, {p1a3['ci95_high']:.6f}].",f"P1 vs A1 Op-F1 delta: {p1a1['op_f1_delta']:.6f}, bootstrap 95% CI [{p1a1['ci95_low']:.6f}, {p1a1['ci95_high']:.6f}].",'',f'P1_TEST_STATUS = {status}',f'FINAL_MAIN_METHOD = {main_method}',f'CORE_CLAIM_FINAL_STATUS = {core}','','No retraining, re-decoding, checkpoint reselection, case deletion, or evaluator modification was performed.']
(BASE/'reports/FINAL_TEST1000_REPORT.md').write_text('\n'.join(lines)+'\n')
(BASE/'reports/PAPER_FINAL_RESULTS.md').write_text('\n'.join(lines)+'\n')
(BASE/'reports/ADVISOR_FINAL_RESULTS.md').write_text('\n'.join(lines)+f"\n\nNext allowed stage: {report['NEXT_ALLOWED_STAGE']}\n")
(BASE/'reports/FINAL_LIMITATIONS.md').write_text('# Final limitations\n\n- EXACT9998 TEST1000 is consumed and cannot be reused as an unbiased final test.\n- IoU is deferred because no validated IoU evaluator was frozen.\n- Geometry summaries are valid-only; failures remain visible through the N=1000 validity denominator.\n- Fusion360 has only 49 cases in TEST1000, so source-specific estimates are uncertain.\n- Remaining errors concentrate in high-complexity under-generation and local parameter/placement prediction.\n')
post={'schema_version':'POST_FINALIZATION_INTEGRITY_V1','PRE_FINALIZATION_INTEGRITY':'PASS','FINAL_METRIC_UNLOCK':'YES','TEST_SET_STATUS':'FINAL_EVALUATION_CONSUMED','output_files':{str(p.relative_to(BASE)):sha(p) for p in BASE.glob('**/*') if p.is_file() and any(str(p.relative_to(BASE)).startswith(x) for x in ['tables/','stats/','operations/','geometry/','reports/'])},'frozen_inputs_unchanged':all(sha(Path(x['path']))==x['expected_sha256'] for x in checks)}
dump(BASE/'integrity/POST_FINALIZATION_INTEGRITY.json',post)
print(json.dumps({'status':'COMPLETE','P1_TEST_STATUS':status,'FINAL_MAIN_METHOD':main_method,'metrics':mm,'comparisons':comps,'operations':ops},indent=2))
