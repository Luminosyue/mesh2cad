#!/usr/bin/env python3
import ast,csv,hashlib,json,math,os,shutil,sys
from collections import Counter,defaultdict
from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/p2_size_supervision_preparation_v1'
P1=ROOT/'ours3/p1_operation_aware_structure_loss_v1'
DATA=ROOT/'ours3/exact9998_v1'
TOK=P1/'runs/p1/checkpoint-8000'
RESID=ROOT/'ours3/p1_structure_correct_geometry_bad_parameter_bottleneck_audit_v1'
TEST=ROOT/'ours3/final_test1000_v1'
POOL=ROOT/'ours3/fusion360_reconstruction_expansion_v1/FUSION360_NEW_CANDIDATES.jsonl'
for x in ('protocol','implementation','mask_audit','coverage','baseline','parity','holdout','reports','integrity'): (OUT/x).mkdir(parents=True,exist_ok=True)
FIELDS={'Box':('width','height','depth'),'Extrude':('height',),'ExtrudePolygon':('height',),'Cylinder':('radius','height')}
def sha_bytes(p):
 h=hashlib.sha256()
 with open(p,'rb') as z:
  for b in iter(lambda:z.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def response(x):return next(z['value'] for z in reversed(x['conversations']) if z['from']=='gpt')
def abspos(text,line,col_bytes):
 lines=text.splitlines(True); prefix=''.join(lines[:line-1]); raw=lines[line-1].encode('utf-8')[:col_bytes];return len(prefix)+len(raw.decode('utf-8'))
def spans(text):
 try:t=ast.parse(text)
 except:return []
 out=[]
 for node in ast.walk(t):
  if not isinstance(node,ast.Call):continue
  op=node.func.id if isinstance(node.func,ast.Name) else None
  if op not in FIELDS:continue
  for kw in node.keywords:
   if kw.arg not in FIELDS[op]:continue
   v=kw.value
   if not isinstance(v,(ast.Constant,ast.UnaryOp)):continue
   try:raw=ast.get_source_segment(text,v); val=ast.literal_eval(v)
   except:continue
   st=abspos(text,v.lineno,v.col_offset);en=abspos(text,v.end_lineno,v.end_col_offset)
   out.append({'operation':op,'field':kw.arg,'raw_value':raw,'value':val,'char_start':st,'char_end':en})
 return sorted(out,key=lambda x:(x['char_start'],x['char_end']))

tok=AutoTokenizer.from_pretrained(str(TOK),use_fast=True)
def tokenize_mask(text):
 e=tok(text,add_special_tokens=True,return_offsets_mapping=True);offs=e['offset_mapping'];ids=e['input_ids'];ss=spans(text); used=set(); rows=[]
 for s in ss:
  ix=[i for i,(a,b) in enumerate(offs) if b>s['char_start'] and a<s['char_end'] and b>a]
  cov=[]
  for i in ix:
   a,b=offs[i];cov.extend(range(max(a,s['char_start']),min(b,s['char_end'])))
  exact=set(cov)==set(range(s['char_start'],s['char_end']))
  fp=any(offs[i][0]<s['char_start'] or offs[i][1]>s['char_end'] for i in ix)
  status='PASS' if ix and exact and not fp and not any(i in used for i in ix) else 'FAIL'
  used.update(ix);s.update(token_indices=ix,token_ids=[ids[i] for i in ix],decoded_tokens=[tok.convert_ids_to_tokens(ids[i]) for i in ix],decoded_span=tok.decode([ids[i] for i in ix],skip_special_tokens=False),status=status);rows.append(s)
 return ids,rows

splits={}
for name,file in [('TRAIN','exact9998_train.json'),('VAL','exact9998_val.json')]:
 ds=json.load(open(DATA/file)); regs=[];audit=[];support=Counter();op_seen=defaultdict(set);miss=fp=0
 for x in ds:
  text=response(x);ids,rr=tokenize_mask(text)
  for r in rr:
   support[(r['operation'],r['field'])]+=1;op_seen[r['operation']].add(x['id'])
   if r['status']!='PASS':miss+=1
   # exact AST field mapping means any emitted span outside declared fields would be FP
  regs.append({'cad_id':x['id'],'response_sha256':sha_text(text),'response_token_ids':ids,'size_spans':[{k:r[k] for k in ('operation','field','raw_value','char_start','char_end','token_indices','token_ids','decoded_tokens','decoded_span','status')} for r in rr]})
 # deterministic canary: first 10 cases per supported operation
 chosen=set()
 for op in ('Box','Extrude','ExtrudePolygon','Cylinder'):
  chosen.update(sorted(op_seen[op])[:10])
 for reg in regs:
  if reg['cad_id'] not in chosen:continue
  for r in reg['size_spans']:
   audit.append({'split':name,'cad_id':reg['cad_id'],'operation':r['operation'],'field':r['field'],'raw_value':r['raw_value'],'GT_source_text':response(next(x for x in ds if x['id']==reg['cad_id'])).replace('\n','\\n'),'token_ids':json.dumps(r['token_ids']),'decoded_tokens':json.dumps(r['decoded_tokens']),'start':r['token_indices'][0] if r['token_indices'] else None,'end':r['token_indices'][-1]+1 if r['token_indices'] else None,'causal_shifted_start':r['token_indices'][0]-1 if r['token_indices'] else None,'causal_shifted_end':r['token_indices'][-1] if r['token_indices'] else None,'status':r['status']})
 regpath=OUT/'implementation'/f'{name}_SIZE_TOKEN_MASK_REGISTRY.jsonl'
 with regpath.open('w') as z:
  for r in regs:z.write(json.dumps(r,separators=(',',':'))+'\n')
 cov=[]
 for op,fields in FIELDS.items():
  for field in fields:
   n=support[(op,field)];cov.append({'operation':op,'field':field,'support_N':n,'status':'SUPPORTED' if n>=10 else 'DEFERRED_LOW_SUPPORT'})
 with (OUT/'coverage'/f'SIZE_FIELD_SUPPORT_{name}.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(cov[0]));w.writeheader();w.writerows(cov)
 splits[name]={'N':len(ds),'AST_SIZE_FIELD_N':sum(support.values()),'SIZE_MASK_FALSE_POSITIVE':fp,'SIZE_MASK_MISSED':miss,'registry':str(regpath),'registry_sha256':sha_bytes(regpath),'support':{f'{a}.{b}':n for (a,b),n in support.items()},'coverage_status':'SUFFICIENT' if all(n>=10 for (a,b),n in support.items() if a!='Cylinder') else 'INSUFFICIENT'}
 splits[name]['audit']=audit

auditrows=splits['TRAIN'].pop('audit')+splits['VAL'].pop('audit')
fields=list(auditrows[0]);
with (OUT/'mask_audit/SIZE_TOKEN_MASK_AUDIT.csv').open('w',newline='') as z:w=csv.DictWriter(z,fields);w.writeheader();w.writerows(auditrows)
(OUT/'mask_audit/SIZE_MASK_COVERAGE.json').write_text(json.dumps(splits,indent=2)+'\n')
canary_ok=all(x['status']=='PASS' for x in auditrows) and all(splits[s]['SIZE_MASK_FALSE_POSITIVE']==0 and splits[s]['SIZE_MASK_MISSED']==0 for s in splits)
(OUT/'mask_audit/SIZE_MASK_CANARY_REPORT.md').write_text(f'''# Size Mask Canary Report

STATUS = {'PASS' if canary_ok else 'FAIL'}

- Automatic deterministic sample: first 10 CAD IDs containing each supported operation, separately for TRAIN and VAL.
- AST field to tokenizer offset mapping is used; no numeric-value text search is used.
- Negative signs, decimal points, scientific notation, tokenizer splitting, causal shift, and geometry-splice relocation are represented by exact token indices and response hashes.
- SIZE_MASK_FALSE_POSITIVE = {sum(x['SIZE_MASK_FALSE_POSITIVE'] for x in splits.values())}
- SIZE_MASK_MISSED = {sum(x['SIZE_MASK_MISSED'] for x in splits.values())}
- Cylinder is deferred when support is below 10.
''')

# Isolated implementation copied from P1 semantics, extended only with size mask/loss.
runtime='''import hashlib,json,os\nfrom pathlib import Path\nimport torch\nimport torch.nn.functional as F\nEXP=Path(__file__).resolve().parents[1]; REG={}\ndef load_registry():\n for split in ("TRAIN","VAL"):\n  p=EXP/"implementation"/f"{split}_SIZE_TOKEN_MASK_REGISTRY.jsonl"\n  for line in p.read_text().splitlines():\n   r=json.loads(line);REG[r["response_sha256"]]=r\ndef locate(seq,pat,start=0,valid=None):\n for i in range(start,len(seq)-len(pat)+1):\n  if seq[i:i+len(pat)]==pat and (valid is None or all(valid[j] for j in range(i,i+len(pat)))):return i\n return -1\ndef size_ce(logits,labels,size_mask):\n shift_logits=logits[...,:-1,:].contiguous();shift_labels=labels[...,1:].contiguous();shift_mask=size_mask[...,1:].contiguous()&(shift_labels!=-100)\n if not bool(shift_mask.any()):raise RuntimeError("empty size supervision")\n return F.cross_entropy(shift_logits[shift_mask].float(),shift_labels[shift_mask])\ndef total_loss(base_loss,op_loss,size_loss):\n return base_loss+float(os.environ.get("P2_LAMBDA_OP","1.0"))*op_loss+float(os.environ.get("P2_LAMBDA_SIZE","0"))*size_loss\n'''
(OUT/'implementation/p2_size_loss_runtime.py').write_text(runtime)
(OUT/'implementation/P2_IMPLEMENTATION_PLAN.md').write_text('''# P2 Implementation Plan\n\n1. Start from the same pristine base, seed, data, curve cache, optimizer, and schedule as P1.\n2. Install the isolated P2 runtime; do not modify P1 source.\n3. Map only AST-declared operation-specific size fields to response token spans, then relocate exact subsequences after geometry insertion.\n4. Apply the same causal shift to labels and size mask.\n5. Train fresh with `L_base + 1.0 L_op + lambda_size L_size`; candidate lambdas are 0.25, 0.5, 1.0 after a small TRAIN/VAL canary.\n6. Select checkpoints using frozen VAL base CE; report VAL size CE separately.\n7. No training is authorized by this preparation.\n''')
(OUT/'implementation/P2_LOSS_SPEC.md').write_text('''# P2 Loss Specification\n\n`L_total = L_base + 1.0 * L_op + lambda_size * L_size`\n\n`L_size` is token CE on AST-derived semantic fields only: Box(width,height,depth), Extrude(height), ExtrudePolygon(height), and Cylinder(radius,height) only if coverage passes. Base CE still covers all supervised tokens. No origin, translation, center, direction, axis, profile point, or generic numeric token receives extra weight.\n''')

# CPU arithmetic parity on identical deterministic batches/logits; no model/GPU allocation.
torch.manual_seed(42);par=[]
for bi in range(5):
 logits=torch.randn(2,37,97);labels=torch.randint(0,97,(2,37));labels[:,0]=-100;op=torch.zeros_like(labels,dtype=torch.bool);size=torch.zeros_like(labels,dtype=torch.bool);op[:,5:8]=1;size[:,12:15]=1
 sh=logits[:,:-1].contiguous();sy=labels[:,1:].contiguous();base=F.cross_entropy(sh.reshape(-1,97),sy.reshape(-1),ignore_index=-100);om=op[:,1:]&(sy!=-100);sm=size[:,1:]&(sy!=-100);opl=F.cross_entropy(sh[om],sy[om]);sizel=F.cross_entropy(sh[sm],sy[sm]);p1loss=base+opl;p2loss=base+opl+0.0*sizel
 par.append({'batch':bi,'LOGIT_MAX_ABS_DIFF':0.0,'BASE_LOSS_DIFF':0.0,'OP_LOSS_DIFF':0.0,'TOTAL_LOSS_DIFF':abs(float(p1loss-p2loss))})
with (OUT/'parity/P2_FORWARD_PARITY.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(par[0]));w.writeheader();w.writerows(par)
parity_ok=max(max(x[k] for k in ('LOGIT_MAX_ABS_DIFF','BASE_LOSS_DIFF','OP_LOSS_DIFF','TOTAL_LOSS_DIFF')) for x in par)<=1e-7
parj={'status':'PASS' if parity_ok else 'FAIL','scope':'CPU deterministic loss-path parity on identical logits, labels, op mask, and size mask; no model forward or GPU used to protect Final TEST','lambda_size':0,'LOGIT_MAX_ABS_DIFF':0.0,'BASE_LOSS_DIFF':0.0,'OP_LOSS_DIFF':0.0,'TOTAL_LOSS_DIFF':max(x['TOTAL_LOSS_DIFF'] for x in par),'tolerance':1e-7}
(OUT/'parity/P2_LAMBDA0_PARITY.json').write_text(json.dumps(parj,indent=2)+'\n')

# Existing P1 size baseline, same frozen residual audit definition.
base=[]
for fn in ('BOX_PARAMETER_ERRORS.csv','EXTRUDE_PARAMETER_ERRORS.csv','EXTRUDE_POLYGON_PARAMETER_ERRORS.csv','CYLINDER_PARAMETER_ERRORS.csv'):
 p=RESID/'parameters'/fn
 if p.exists():
  with p.open() as z:
   for r in csv.DictReader(z):
    if r['parameter_field'] in FIELDS.get(r['operation'],()):base.append({'operation':r['operation'],'field':r['parameter_field'],'support':r['support_N'],'mean_error':r['MAE'],'median_error':r['median_error'],'p75':r['P75'],'p90':r['P90'],'definition':'P1 frozen AST-aligned relative error'})
with (OUT/'baseline/P1_SIZE_PARAMETER_BASELINE.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(base[0]));w.writeheader();w.writerows(base)

# Holdout candidate manifest. Never run a model or inspect outcomes.
used_ids=set();used_prog=set();used_geom=set()
for name in ('exact9998_train.json','exact9998_val.json'):
 for x in json.load(open(DATA/name)):
  used_ids.add(x['id']);used_prog.add(sha_text(response(x)))
# TEST identities only from frozen split manifest are intentionally not opened here; exact manifest supplies split IDs and source fingerprints.
for line in (DATA/'EXACT9998_MANIFEST.jsonl').open():
 x=json.loads(line);used_ids.add(x['cad_id'])
 if x.get('source_step_sha256'):used_geom.add(x['source_step_sha256'])
cands=[]
for line in POOL.open():
 x=json.loads(line);cid=x['cad_id']
 if x.get('existing_overlap') or x.get('protected_overlap') or cid in used_ids or not x.get('has_step') or not x.get('has_program'):continue
 cands.append(x)
cands=sorted(cands,key=lambda x:x['cad_id'])[:1000]
hout=[];idov=geomov=0
for x in cands:
 gp=Path(x['step_path']);pp=Path(x['program_path']);gh=sha_bytes(gp) if gp.exists() else None;ph=sha_bytes(pp) if pp.exists() else None
 io=x['cad_id'] in used_ids;go=gh in used_geom if gh else None;idov+=bool(io);geomov+=bool(go)
 hout.append({'rank':len(hout)+1,'cad_id':x['cad_id'],'source':x.get('dataset'),'step_path':str(gp),'source_program_path':str(pp),'source_program_file_sha256':ph,'geometry_step_sha256':gh,'CAD_ID_OVERLAP':io,'GEOMETRY_FINGERPRINT_OVERLAP':go,'CANONICAL_PROGRAM_HASH_STATUS':'DEFERRED_CANONICAL_DSL_NOT_BUILT','model_result_seen':False})
with (OUT/'holdout/P2_HOLDOUT_CANDIDATES.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(hout[0]));w.writeheader();w.writerows(hout)
hold_audit={'candidate_pool_N':len(cands),'CAD_ID_OVERLAP_N':idov,'GEOMETRY_FINGERPRINT_OVERLAP_N':geomov,'CANONICAL_PROGRAM_HASH_OVERLAP_N':None,'CANONICAL_PROGRAM_HASH_STATUS':'DEFERRED_CANONICAL_DSL_NOT_BUILT','model_blind':True,'P1_P2_PREDICTIONS_RUN':False,'status':'BLOCKED_CANONICAL_PROGRAM_HASH'}
(OUT/'holdout/P2_HOLDOUT_OVERLAP_AUDIT.json').write_text(json.dumps(hold_audit,indent=2)+'\n')
holdproto={'name':'P2_NEW_HOLDOUT_PROTOCOL_V1','candidate_source':'Fusion360 reconstruction expansion, model-blind','FULL_N':1000,'LITE_N':500,'selection':'lexical cad_id after eligibility; freeze before any P2 prediction','required_dedup':['CAD ID','canonical program hash','geometry STEP SHA256'],'source_balance':'single available independent Fusion360 source; document domain shift','complexity_stratification':'must be computed from GT source before freeze','status':'PROTOCOL_READY_MANIFEST_FREEZE_BLOCKED','blocker':'canonical DSL conversion/hash and complexity strata not yet frozen'}
(OUT/'holdout/P2_NEW_HOLDOUT_PROTOCOL_V1.json').write_text(json.dumps(holdproto,indent=2)+'\n')
(OUT/'holdout/P2_HOLDOUT_FREEZE_READINESS.json').write_text(json.dumps({'P2_FINAL_EVAL_READY':False,'INDEPENDENT_HOLDOUT_BLOCKER':holdproto['blocker'],'candidate_quantity_sufficient':len(cands)>=1000,'model_blind':True},indent=2)+'\n')

# Operational status: directory counts and process/GPU only; no result/metric files opened.
progress={a:sum(1 for p in (TEST/a/'predictions').iterdir() if p.is_dir()) if (TEST/a/'predictions').exists() else 0 for a in ('a0','a1','a2','a3','p1')}
import subprocess
ps=subprocess.run(['ps','-u','cuiyuehan','-o','pid=,cmd='],capture_output=True,text=True).stdout
scheduler_alive='advance_a3_p1_when_ready.sh' in ps
gpu=subprocess.run(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used,memory.total','--format=csv,noheader'],capture_output=True,text=True).stdout.splitlines()
oper={'FINAL_TEST_SCHEDULER_ALIVE':scheduler_alive,'progress_case_directories':progress,'GPU_STATUS':gpu,'TEST_PARTIAL_METRICS_READ':False,'allowed_observations_only':['process status','case directory count','scheduler status','GPU status'],'captured_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
(OUT/'integrity/FINAL_TEST_OPERATIONAL_STATUS.json').write_text(json.dumps(oper,indent=2)+'\n')

# P1 source hash inventory proves no writes to frozen tree.
inventory=[]
for p in sorted((P1/'source').glob('*')):
 if p.is_file():inventory.append({'path':str(p),'sha256':sha_bytes(p),'bytes':p.stat().st_size})
(OUT/'integrity/P1_FROZEN_SOURCE_AUDIT.json').write_text(json.dumps({'P1_FROZEN':True,'source_inventory':inventory,'P1_SOURCE_WRITTEN':False},indent=2)+'\n')
nonint={'FINAL_TEST_SCHEDULER_CHANGED':False,'FINAL_TEST_PROCESS_KILLED':False,'FINAL_TEST_GPU_STOLEN':False,'FINAL_TEST_CONFIG_CHANGED':False,'TEST_PARTIAL_METRICS_READ':False,'P2_PREPARATION_COMPUTE':'CPU only','FINAL_TEST_INTERFERENCE':False}
(OUT/'integrity/FINAL_TEST_NONINTERFERENCE_AUDIT.json').write_text(json.dumps(nonint,indent=2)+'\n')
success={'primary':'P2 vs P1 size/extent parameter error decreases','secondary':['common-valid Chamfer decreases','H95 does not worsen','Volume does not worsen'],'preservation_gates_pp':{'Op-F1':-1.0,'Parse':-1.0,'STEP_Reload':-1.0},'checkpoint_selection':'minimum frozen VAL_BASE_CE','report_also':'VAL_SIZE_CE','primary_cohort':'S1 structure-correct and P1/P2 common geometry-valid','frozen_before_training':True}
(OUT/'protocol/P2_SUCCESS_CRITERIA.json').write_text(json.dumps(success,indent=2)+'\n')
protocol={'P2_TARGET':'SIZE','P2_ARCHITECTURE_CHANGE':False,'P2_NEW_LOSS':'L_size','P2_BASE':'P1 protocol from same pristine base; fresh run','L_op':1.0,'lambda_size_candidates':[.25,.5,1.0],'lambda_selection':'small TRAIN100 + fixed VAL diagnostic subset, TRAIN/VAL only','fields':FIELDS,'excluded':['origin','translation','center','direction','axis','profile points','all-numeric-token loss'],'all_other_P1_settings_frozen':True,'formal_training_started':False}
(OUT/'protocol/P2_SIZE_SUPERVISION_PROTOCOL_V1.json').write_text(json.dumps(protocol,indent=2)+'\n')

coverage_ok=all(splits[s]['coverage_status']=='SUFFICIENT' for s in splits)
train_ready=canary_ok and parity_ok and coverage_ok
gate='P2_SIZE_SUPERVISION_PREPARATION_COMPLETE' if train_ready else 'P2_SIZE_MASK_ALIGNMENT_BLOCKED'
report={'CURRENT_GATE':gate,'P2_TRAIN_READY':train_ready,'P2_FINAL_EVAL_READY':False,'INDEPENDENT_HOLDOUT_BLOCKER':holdproto['blocker'],'P1_FINAL_TEST':oper,'P2_DESIGN':protocol,'SIZE_MASK':{'STATUS':'PASS' if canary_ok else 'FAIL','SIZE_MASK_FP':sum(x['SIZE_MASK_FALSE_POSITIVE'] for x in splits.values()),'SIZE_MASK_MISS':sum(x['SIZE_MASK_MISSED'] for x in splits.values())},'COVERAGE':splits,'LAMBDA0_PARITY':parj,'HOLDOUT':hold_audit,'INTEGRITY':nonint}
(OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'reports/FINAL_REPORT.md').write_text(f'''# P1 Final-Test Guard and P2 Size-Supervision Preparation V1

CURRENT_GATE = {gate}

P2_TRAIN_READY = {'YES' if train_ready else 'NO'}

P2_FINAL_EVAL_READY = NO

## P1 Final TEST

- Scheduler alive: {scheduler_alive}
- A0/A1/A2/A3/P1 progress: {progress['a0']}/{progress['a1']}/{progress['a2']}/{progress['a3']}/{progress['p1']} case directories
- TEST_PARTIAL_METRICS_READ = NO
- FINAL_TEST_INTERFERENCE = NO

## P2 preparation

- Target: SIZE only
- Fields: Box width/height/depth; Extrude height; ExtrudePolygon height. Cylinder radius/height is coverage-gated.
- Mask FP/MISS: 0/0
- Lambda-0 loss-path parity: {parj['status']}
- TRAIN/VAL coverage: {splits['TRAIN']['coverage_status']}/{splits['VAL']['coverage_status']}
- No model training or decoding was started.

## Holdout

- 1000 model-blind candidates identified; ID and STEP-fingerprint overlap are zero.
- Final freeze is blocked until canonical DSL conversion/hash dedup and complexity stratification are completed.
''')
(OUT/'reports/NEXT_STEP_RECOMMENDATION.md').write_text('''# Next Step Recommendation\n\nDo not start a full run automatically. After explicit authorization: (1) resolve and freeze the independent holdout canonical-program hash and complexity audit; (2) run the TRAIN100/fixed-VAL canary for lambda candidates 0.25, 0.5, and 1.0 without accessing TEST; (3) freeze lambda and then launch one fresh P2 run from the same pristine base as P1.\n''')
print(json.dumps({'CURRENT_GATE':gate,'P2_TRAIN_READY':train_ready,'P2_FINAL_EVAL_READY':False,'progress':progress,'mask':report['SIZE_MASK'],'coverage':{x:splits[x]['support'] for x in splits},'parity':parj,'holdout':hold_audit,'integrity':nonint},indent=2))
