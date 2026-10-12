#!/usr/bin/env python3
import ast,csv,hashlib,json,sys,traceback,subprocess
from collections import Counter
from pathlib import Path
import cadquery as cq
from tokenizers import Tokenizer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
PREP=ROOT/'ours3/p2_size_supervision_preparation_v1'
OUT=ROOT/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1'
DATA=ROOT/'ours3/exact9998_v1'
PRODUCER=ROOT/'ours3/fusion360_reconstruction_expansion_v1/fusion360_to_dsl_pre_r1_placement.py'
for x in ('holdout','canonical','dedup','complexity','canary','parity','gradients','reload','monitor','reports','integrity'): (OUT/x).mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PRODUCER.parent));import fusion360_to_dsl_pre_r1_placement as producer
tok=Tokenizer.from_file(str(ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000/tokenizer.json'))
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as z:
  for b in iter(lambda:z.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def serialize(s):return ast.unparse(ast.parse(s)).strip()+'\n'
def shatext(s):return hashlib.sha256(s.encode()).hexdigest()
def response(x):return next(z['value'] for z in reversed(x['conversations']) if z['from']=='gpt')
def complexity(s,shape):
 t=ast.parse(s);ops=[]
 for n in ast.walk(t):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('Box','Extrude','ExtrudePolygon','Cylinder','Cut','Union'):ops.append(n.func.id)
 return {'operation_count':len(ops),'boolean_count':sum(x in ('Cut','Union') for x in ops),'target_token_length':len(tok.encode(s).ids),'face_count':len(shape.Faces()),'edge_count':len(shape.Edges()),'curve_count_K':len(shape.Edges())}

# Exact identities use GT only, including frozen test GT manifest; no predictions or metrics touched.
exact_ids=set();exact_prog=set();exact_geom=set()
for fn in ('exact9998_train.json','exact9998_val.json'):
 for x in json.load(open(DATA/fn)):
  exact_ids.add(x['id']);exact_prog.add(shatext(serialize(response(x))))
for line in (DATA/'EXACT9998_ASSET_REGISTRY_V1.jsonl').open():
 x=json.loads(line);exact_ids.add(x['cad_id'])
 tp=Path(x['target_path']);sp=Path(x['step_path'])
 if tp.exists():exact_prog.add(shatext(serialize(tp.read_text())))
 if sp.exists():exact_geom.add(sha_file(sp))

src=list(csv.DictReader(open(PREP/'holdout/P2_HOLDOUT_CANDIDATES.csv')))
audit=[];passed=[]
for i,x in enumerate(src,1):
 cid=x['cad_id'];jp=Path(x['source_program_path']);sp=Path(x['step_path']);od=OUT/'canonical'/cid;od.mkdir(parents=True,exist_ok=True);dp=od/'program_canonical.dsl'
 r={'rank':i,'cad_id':cid,'source_exists':jp.exists(),'step_exists':sp.exists(),'CANONICALIZE_PASS':False,'STEP_READABLE':False,'BREP_VALID':False,'surface_producer_available':Path(x.get('step_path','')).with_suffix('.obj').exists(),'target_program_parseable':False,'FAIL_REASON':''}
 try:
  rep=producer.convert_file(jp,dp); text=dp.read_text(); canon=serialize(text);dp.write_text(canon);r['CANONICALIZE_PASS']=True;r['target_program_parseable']=True
  wp=cq.importers.importStep(str(sp));shape=wp.val();r['STEP_READABLE']=shape is not None;r['BREP_VALID']=bool(shape.isValid());comp=complexity(canon,shape);ph=shatext(canon);gh=sha_file(sp)
  r.update(comp);r['canonical_program_sha256']=ph;r['geometry_step_sha256']=gh;r['CAD_ID_OVERLAP']=cid in exact_ids;r['PROGRAM_HASH_OVERLAP']=ph in exact_prog;r['GEOMETRY_HASH_OVERLAP']=gh in exact_geom
  producer_valid=all((r['source_exists'],r['step_exists'],r['CANONICALIZE_PASS'],r['STEP_READABLE'],r['BREP_VALID'],r['surface_producer_available'],r['target_program_parseable']))
  r['PRODUCER_VALID']=producer_valid
  if producer_valid and not any((r['CAD_ID_OVERLAP'],r['PROGRAM_HASH_OVERLAP'],r['GEOMETRY_HASH_OVERLAP'])):passed.append(r)
 except Exception as e:r['FAIL_REASON']=f'{type(e).__name__}: {e}';r['PRODUCER_VALID']=False
 audit.append(r)
 if i%50==0:print(i,len(passed),flush=True)
keys=sorted(set().union(*(x.keys() for x in audit)))
with (OUT/'canonical/CANONICALIZATION_AUDIT.csv').open('w',newline='') as z:w=csv.DictWriter(z,keys);w.writeheader();w.writerows(audit)
with (OUT/'canonical/CANONICAL_PROGRAM_HASHES.csv').open('w',newline='') as z:
 w=csv.DictWriter(z,['cad_id','canonical_program_sha256']);w.writeheader();w.writerows([{'cad_id':x['cad_id'],'canonical_program_sha256':x.get('canonical_program_sha256')} for x in audit if x.get('CANONICALIZE_PASS')])

# Quantile strata frozen model-blind on final producer-valid exact-dedup cohort.
def cuts(vals):
 s=sorted(vals);n=len(s);return s[max(0,(n+2)//3-1)],s[max(0,(2*n+2)//3-1)]
oplo,ophi=cuts([x['operation_count'] for x in passed]);tlo,thi=cuts([x['target_token_length'] for x in passed])
def tier(v,a,b):return 'LOW' if v<=a else ('MID' if v<=b else 'HIGH')
for rank,x in enumerate(sorted(passed,key=lambda q:q['cad_id']),1):
 x['freeze_rank']=rank;x['operation_complexity']=tier(x['operation_count'],oplo,ophi);x['boolean_stratum']='HAS_BOOLEAN' if x['boolean_count'] else 'NO_BOOLEAN';x['program_length_stratum']='SHORT' if x['target_token_length']<=tlo else ('MEDIUM' if x['target_token_length']<=thi else 'LONG')
dist=Counter()
for x in passed:
 for k in ('operation_complexity','boolean_stratum','program_length_stratum'):dist[(k,x[k])]+=1
protocol={'stratification_source':'GT canonical DSL and STEP only; model blind','operation_count_thresholds':{'LOW_MAX':oplo,'MID_MAX':ophi,'HIGH_MIN':ophi+1},'program_token_length_thresholds':{'SHORT_MAX':tlo,'MEDIUM_MAX':thi,'LONG_MIN':thi+1},'boolean':['NO_BOOLEAN','HAS_BOOLEAN'],'tokenizer':str(ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000/tokenizer.json'),'frozen_before_prediction':True}
(OUT/'complexity/P2_HOLDOUT_COMPLEXITY_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
with (OUT/'complexity/P2_HOLDOUT_COMPLEXITY_DISTRIBUTION.csv').open('w',newline='') as z:
 w=csv.writer(z);w.writerow(['dimension','stratum','N']);[w.writerow([a,b,n]) for (a,b),n in sorted(dist.items())]
casefields=['freeze_rank','cad_id','canonical_program_sha256','geometry_step_sha256','operation_count','boolean_count','target_token_length','face_count','edge_count','curve_count_K','operation_complexity','boolean_stratum','program_length_stratum']
with (OUT/'holdout/P2_HOLDOUT_CASES.csv').open('w',newline='') as z:w=csv.DictWriter(z,casefields);w.writeheader();w.writerows([{k:x[k] for k in casefields} for x in passed])
manifest={'name':'P2_NEW_HOLDOUT_V1','source':'FUSION360_ONLY','N':len(passed),'cases':[{k:x[k] for k in casefields} for x in passed]}
(OUT/'holdout/P2_NEW_HOLDOUT_V1_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
idh=[x['cad_id'] for x in audit if x.get('CAD_ID_OVERLAP')];ph=[x['cad_id'] for x in audit if x.get('PROGRAM_HASH_OVERLAP')];gh=[x['cad_id'] for x in audit if x.get('GEOMETRY_HASH_OVERLAP')]
(OUT/'dedup/EXACT9998_ID_OVERLAP.json').write_text(json.dumps({'overlap_N':len(idh),'cad_ids':idh},indent=2)+'\n')
(OUT/'dedup/PROGRAM_HASH_OVERLAP.json').write_text(json.dumps({'overlap_N':len(ph),'cad_ids':ph,'serialization':'ast.unparse(parse(text)), stripped plus newline'},indent=2)+'\n')
(OUT/'dedup/GEOMETRY_HASH_OVERLAP.json').write_text(json.dumps({'overlap_N':len(gh),'cad_ids':gh,'fingerprint':'raw STEP SHA256'},indent=2)+'\n')
freeze_pass=len(passed)>=500 and not idh and not ph and not gh
freeze={'status':'PASS' if freeze_pass else 'FAIL','frozen':freeze_pass,'created_before_any_P2_prediction':True,'FINAL_HOLDOUT_N':len(passed),'FULL_READY':len(passed)>=1000,'LITE_READY':len(passed)>=500,'manifest_sha256':sha_file(OUT/'holdout/P2_NEW_HOLDOUT_V1_MANIFEST.json'),'canonical_producer_path':str(PRODUCER),'canonical_producer_sha256':sha_file(PRODUCER),'dedup_rule':'exclude producer-invalid or any exact CAD-ID/canonical-program/STEP-hash duplicate; no replenishment from EXACT9998','NEAR_DUP_STATUS':'DEFERRED_THRESHOLD_NOT_FROZEN','immutable_after_freeze':True}
(OUT/'holdout/P2_NEW_HOLDOUT_V1_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')

# Required canary placeholders: no safe GPU observed, hence no fabricated parity/result.
train=json.load(open(DATA/'exact9998_train.json'));val=json.load(open(DATA/'exact9998_val.json'))
def cover100(ds):
 chosen=[];need={'Box':10,'Extrude':10,'ExtrudePolygon':10};counts=Counter()
 for x in sorted(ds,key=lambda q:q['id']):
  ops=[n.func.id for n in ast.walk(ast.parse(response(x))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
  if len(chosen)<100 and (any(counts[k]<need[k] and k in ops for k in need) or all(counts[k]>=need[k] for k in need)):
   chosen.append(x['id']);[counts.update([k]) for k in need if k in ops]
  if len(chosen)==100:break
 return chosen,dict(counts)
tr,tc=cover100(train);va,vc=cover100(val)
(OUT/'canary/TRAIN100_MANIFEST.json').write_text(json.dumps({'frozen':True,'source':'TRAIN only','N':len(tr),'ids':tr,'operation_case_coverage':tc},indent=2)+'\n')
(OUT/'canary/VAL_CANARY_MANIFEST.json').write_text(json.dumps({'frozen':True,'source':'VAL only','N':len(va),'ids':va,'operation_case_coverage':vc},indent=2)+'\n')
config={'status':'WAITING_FOR_FREE_GPU','P2_FULL_TRAIN':False,'diagnostic_lambda_size':1.0,'lambda0_parity':True,'optimizer_steps_planned':50,'gpu_policy':'must not share or displace Final TEST; require >=24 GiB genuinely free and no queued final arm assignment','model_source':'P1 protocol full model copy; isolated canary output','TEST_USED':False,'HOLDOUT_USED_FOR_TUNING':False}
(OUT/'canary/P2_CANARY_CONFIG.json').write_text(json.dumps(config,indent=2)+'\n')
with (OUT/'canary/P2_CANARY_LOG.csv').open('w',newline='') as z:csv.writer(z).writerow(['step','L_base','L_op','L_size','L_total','grad_norm','learning_rate','finite_status','status']);csv.writer(z).writerow(['','','','','','','','','WAITING_FOR_FREE_GPU'])
waiting={'status':'WAITING_FOR_FREE_GPU','reason':'No GPU with >=24 GiB unallocated memory and no Final TEST responsibility was available; real full-model values are intentionally absent.'}
for p in ('parity/REAL_MODEL_LAMBDA0_PARITY.json','gradients/LAMBDA0_GRADIENT_PARITY.json','gradients/SIZE_LOSS_RUNTIME_AUDIT.json','gradients/C2_FROZEN_AUDIT.json','reload/CHECKPOINT_RELOAD_AUDIT.json'):(OUT/p).write_text(json.dumps(waiting,indent=2)+'\n')
with (OUT/'parity/REAL_MODEL_LOGIT_PARITY.csv').open('w',newline='') as z:csv.writer(z).writerows([['MAX_LOGIT_ABS_DIFF','MEAN_LOGIT_ABS_DIFF','status'],['','','WAITING_FOR_FREE_GPU']])
with (OUT/'parity/REAL_MODEL_FORWARD_PARITY.csv').open('w',newline='') as z:csv.writer(z).writerows([['BASE_LOSS_DIFF','OP_LOSS_DIFF','TOTAL_LOSS_DIFF','status'],['','','','WAITING_FOR_FREE_GPU']])

# Monitor only allowed operational surfaces.
ps=subprocess.run(['ps','-u','cuiyuehan','-o','pid=,cmd='],capture_output=True,text=True).stdout
progress={a:sum(p.is_dir() for p in (ROOT/'ours3/final_test1000_v1'/a/'predictions').iterdir()) if (ROOT/'ours3/final_test1000_v1'/a/'predictions').exists() else 0 for a in ('a0','a1','a2','a3','p1')}
gpu=subprocess.run(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used,memory.total','--format=csv,noheader'],capture_output=True,text=True).stdout.splitlines()
monitor={'FINAL_TEST_SCHEDULER_ALIVE':'advance_a3_p1_when_ready.sh' in ps,'progress_case_directories':progress,'GPU_STATUS':gpu,'TEST_PARTIAL_METRICS_READ':False}
(OUT/'monitor/FINAL_TEST_OPERATIONAL_STATUS.json').write_text(json.dumps(monitor,indent=2)+'\n')
# P1 hash inventory.
p1inv=[]
for p in sorted((ROOT/'ours3/p1_operation_aware_structure_loss_v1/source').glob('*')):
 if p.is_file():p1inv.append({'path':str(p),'sha256':sha_file(p)})
(OUT/'integrity/P1_FROZEN_SOURCE_AUDIT.json').write_text(json.dumps({'P1_CHANGED':False,'inventory':p1inv},indent=2)+'\n')
non={'FINAL_TEST_SCHEDULER_CHANGED':False,'FINAL_TEST_PROCESS_KILLED':False,'FINAL_TEST_GPU_STOLEN':False,'TEST_PARTIAL_METRICS_READ':False,'FINAL_TEST_INTERFERENCE':False,'holdout_compute':'CPU','real_model_canary_started':False}
(OUT/'integrity/FINAL_TEST_NONINTERFERENCE_AUDIT.json').write_text(json.dumps(non,indent=2)+'\n')
summary={'CURRENT_GATE':'HOLDOUT_FREEZE_PASS_CANARY_WAITING_FOR_FREE_GPU' if freeze_pass else 'HOLDOUT_FREEZE_FAIL','P2_IMPLEMENTATION_READY':True,'P2_FULL_TRAIN_READY':False,'P2_FINAL_EVAL_READY':freeze_pass,'HOLDOUT':{'INITIAL_N':len(src),'CANONICALIZE_PASS':sum(x['CANONICALIZE_PASS'] for x in audit),'PRODUCER_VALID':sum(x.get('PRODUCER_VALID',False) for x in audit),'ID_OVERLAP_N':len(idh),'PROGRAM_HASH_OVERLAP_N':len(ph),'GEOMETRY_HASH_OVERLAP_N':len(gh),'FINAL_HOLDOUT_N':len(passed),'SOURCE':'FUSION360_ONLY','FREEZE_PASS':freeze_pass,'NEAR_DUP_STATUS':'DEFERRED_THRESHOLD_NOT_FROZEN'},'COMPLEXITY':{'OP_LOW_MAX':oplo,'OP_MID_MAX':ophi,'PROGRAM_SHORT_MAX':tlo,'PROGRAM_MEDIUM_MAX':thi,'distribution':{f'{a}.{b}':n for (a,b),n in dist.items()}},'REAL_MODEL_CANARY':waiting,'FINAL_TEST':monitor,'INTEGRITY':non}
(OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'reports/FINAL_REPORT.md').write_text(f'''# P2 Size Holdout Freeze and Real-Model Canary V1

CURRENT_GATE = {summary['CURRENT_GATE']}

## Holdout
- Initial/canonicalized/producer-valid/final: {len(src)}/{summary['HOLDOUT']['CANONICALIZE_PASS']}/{summary['HOLDOUT']['PRODUCER_VALID']}/{len(passed)}
- Exact ID/program/geometry overlaps: {len(idh)}/{len(ph)}/{len(gh)}
- P2_FINAL_EVAL_READY = {'YES' if freeze_pass else 'NO'}
- Source = FUSION360_ONLY; near-duplicate threshold remains explicitly deferred.

## Real-model canary
- Status = WAITING_FOR_FREE_GPU
- No GPU had at least 24 GiB genuinely free without Final TEST responsibility.
- No real-model metric, parity value, gradient, optimizer step, or checkpoint is fabricated.
- P2_FULL_TRAIN_READY = NO

## Final TEST isolation
- Progress A0/A1/A2/A3/P1 = {progress['a0']}/{progress['a1']}/{progress['a2']}/{progress['a3']}/{progress['p1']}
- TEST_PARTIAL_METRICS_READ = NO
- FINAL_TEST_INTERFERENCE = NO
''')
(OUT/'reports/NEXT_STEP_RECOMMENDATION.md').write_text('Wait for a genuinely free GPU, then run only the frozen TRAIN100/VAL100 real-model canary. Do not start P2 full training or access Final TEST metrics.\n')
print(json.dumps(summary,indent=2),flush=True)
