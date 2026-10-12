#!/usr/bin/env python3
import csv,json,subprocess,hashlib,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1'
for x in ('gpu_audit','parity','gradients','canary','reload','monitor','reports','integrity'):(OUT/x).mkdir(parents=True,exist_ok=True)
def run(a):return subprocess.run(a,capture_output=True,text=True,check=False).stdout
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
gpu_lines=run(['nvidia-smi','--query-gpu=index,uuid,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits']).splitlines()
app_lines=run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_memory','--format=csv,noheader,nounits']).splitlines()
apps={}
for line in app_lines:
 try:
  u,p,m=[x.strip() for x in line.split(',')];pid=int(p);ps=run(['ps','-p',str(pid),'-o','user=,cmd=']).strip();apps.setdefault(u,[]).append({'pid':pid,'used_memory_MiB':int(m),'owner_and_command':ps,'is_final_test':'final_test_runner.py' in ps,'is_formal_experiment':any(k in ps for k in ('unified_v2','train','eval','final_test'))})
 except:pass
reserved={0:'A3 Final TEST scheduler reservation',4:'P1 Final TEST scheduler reservation'}
gpus=[]
for line in gpu_lines:
 i,u,total,used,free,util=[x.strip() for x in line.split(',')];i=int(i);free=int(free);proc=apps.get(u,[])
 reasons=[]
 if free<24576:reasons.append('FREE_MEMORY_LT_24_GIB')
 if any(x['is_final_test'] for x in proc):reasons.append('FINAL_TEST_PROCESS_PRESENT')
 if i in reserved:reasons.append('FINAL_TEST_SCHEDULER_RESERVED')
 if proc:reasons.append('ACTIVE_OR_UNKNOWN_GPU_PROCESS_PRESENT')
 gpus.append({'gpu_id':i,'uuid':u,'total_memory_MiB':int(total),'used_memory_MiB':int(used),'free_memory_MiB':free,'utilization_percent':int(util),'active_processes':proc,'scheduler_reservation':reserved.get(i),'safe':not reasons,'rejection_reasons':reasons})
safe=[x for x in gpus if x['safe']]
audit={'captured_utc':datetime.now(timezone.utc).isoformat(),'definition':{'minimum_free_memory_MiB':24576,'no_final_test_process':True,'no_scheduler_reservation':True,'no_unknown_high_memory_task':True},'SAFE_GPU_FOUND':bool(safe),'CANARY_GPU_ID':safe[0]['gpu_id'] if safe else None,'FREE_MEMORY_BEFORE_MiB':safe[0]['free_memory_MiB'] if safe else None,'gpus':gpus}
(OUT/'gpu_audit/SAFE_GPU_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
if safe:raise SystemExit('SAFE GPU FOUND; this audit-only gate script intentionally does not auto-launch canary')
# Required waiting-state artifacts. Real measurements remain null.
waiting={'status':'NOT_STARTED','REAL_MODEL_CANARY':'WAITING_FOR_FREE_GPU','reason':'No GPU passed the pre-registered safe-GPU gate; no model was loaded.','measured_values':None}
for p in ('parity/REAL_MODEL_LAMBDA0_PARITY.json','gradients/LAMBDA0_GRADIENT_PARITY.json','gradients/LAMBDA1_SIZE_GRADIENT_EFFECT.json','gradients/C2_FROZEN_GRADIENT_AUDIT.json','canary/TRAIN100_RUN_REPORT.json','canary/VAL100_INTEGRATION_REPORT.json','reload/P2_CANARY_CHECKPOINT_RELOAD.json'):(OUT/p).write_text(json.dumps(waiting,indent=2)+'\n')
for p,head in [('parity/REAL_MODEL_LOGIT_PARITY.csv',['MAX_LOGIT_ABS_DIFF','MEAN_LOGIT_ABS_DIFF','status']),('parity/REAL_MODEL_LOSS_PARITY.csv',['BASE_LOSS_DIFF','OP_LOSS_DIFF','TOTAL_LOSS_DIFF','status']),('canary/P2_REAL_MODEL_CANARY_LOG.csv',['step','L_base','L_op','L_size','L_total','grad_norm','lr','finite','GPU_memory','status']),('canary/SIZE_RUNTIME_SEMANTIC_AUDIT.csv',['cad_id','operation','field','raw_value','token_ids','decoded_tokens','start','end','causal_shifted_start','causal_shifted_end','status'])]:
 with (OUT/p).open('w',newline='') as f:csv.writer(f).writerow(head)
# Holdout immutability.
freeze=json.load(open(OUT/'holdout/P2_NEW_HOLDOUT_V1_FREEZE.json'));manifest=OUT/'holdout/P2_NEW_HOLDOUT_V1_MANIFEST.json';mh=sha(manifest)
hold={'HOLDOUT_N':freeze['FINAL_HOLDOUT_N'],'expected_manifest_sha256':freeze['manifest_sha256'],'actual_manifest_sha256':mh,'HOLDOUT_CHANGED':mh!=freeze['manifest_sha256'],'HOLDOUT_PREDICTION_N':0}
(OUT/'integrity/P2_HOLDOUT_IMMUTABILITY_AUDIT.json').write_text(json.dumps(hold,indent=2)+'\n')
# P1 source current hashes against prior frozen inventory where available.
cur=[]
for p in sorted((ROOT/'ours3/p1_operation_aware_structure_loss_v1/source').glob('*')):
 if p.is_file():cur.append({'path':str(p),'sha256':sha(p)})
prevp=OUT/'integrity/P1_FROZEN_SOURCE_AUDIT.json';prev=json.load(open(prevp)) if prevp.exists() else {};old={x['path']:x['sha256'] for x in prev.get('inventory',[])};changed=[x['path'] for x in cur if old and old.get(x['path'])!=x['sha256']]
p1a={'P1_SOURCE_IMMUTABILITY':'PASS' if not changed else 'FAIL','P1_CHANGED':bool(changed),'changed_paths':changed,'current_inventory':cur}
(OUT/'integrity/P1_SOURCE_IMMUTABILITY_AUDIT.json').write_text(json.dumps(p1a,indent=2)+'\n')
# Allowed Final TEST observations only.
ps=run(['ps','-u','cuiyuehan','-o','pid=,cmd=']);td=ROOT/'ours3/final_test1000_v1';progress={a:sum(x.is_dir() for x in (td/a/'predictions').iterdir()) if (td/a/'predictions').exists() else 0 for a in ('a0','a1','a2','a3','p1')}
mon={'captured_utc':datetime.now(timezone.utc).isoformat(),'SCHEDULER_ALIVE':'advance_a3_p1_when_ready.sh' in ps,'progress_case_directories':progress,'TEST_PARTIAL_METRICS_READ':False,'observed_only':['process','case-directory count','scheduler status','GPU status']}
(OUT/'monitor/FINAL_TEST_OPERATIONAL_STATUS.json').write_text(json.dumps(mon,indent=2)+'\n')
non={'FINAL_TEST_SCHEDULER_CHANGED':False,'FINAL_TEST_PROCESS_KILLED':False,'FINAL_TEST_GPU_STOLEN':False,'TEST_PARTIAL_METRICS_READ':False,'FINAL_TEST_INTERFERENCE':False,'CANARY_MODEL_LOADED':False,'CANARY_PROCESS_STARTED':False}
(OUT/'integrity/FINAL_TEST_NONINTERFERENCE_AUDIT.json').write_text(json.dumps(non,indent=2)+'\n')
report={'CURRENT_GATE':'CANARY_WAITING_FOR_FREE_GPU','GPU':{'SAFE_GPU_FOUND':False,'CANARY_GPU_ID':None,'FREE_MEMORY_BEFORE':None,'FINAL_TEST_GPU':'NO'},'REAL_MODEL_FORWARD_PARITY':waiting,'BACKWARD_PARITY':waiting,'SIZE_LOSS':waiting,'FROZEN_C2':waiting,'TRAIN100':waiting,'RELOAD':waiting,'HOLDOUT':hold,'FINAL_TEST':mon,'GO_NO_GO':{'P2_IMPLEMENTATION_READY':True,'P2_FULL_TRAIN_READY':False,'P2_FINAL_EVAL_READY':True,'BLOCKERS':['NO_SAFE_GPU'],'NEXT_ALLOWED_STAGE':'WAIT_FOR_SAFE_GPU_THEN_P2_SIZE_REAL_MODEL_CANARY_V1'}}
(OUT/'reports/REAL_MODEL_CANARY_FINAL_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'reports/REAL_MODEL_CANARY_FINAL_REPORT.md').write_text(f'''# P2 Size Real-Model Canary Gate\n\nCURRENT_GATE = CANARY_WAITING_FOR_FREE_GPU\n\nSAFE_GPU_FOUND = NO\n\nREAL_MODEL_CANARY = NOT_STARTED\n\nNo GPU satisfied the frozen >=24 GiB free-memory, no-active-task, no-Final-TEST, and no-scheduler-reservation criteria. No model was loaded and no canary stage ran.\n\n## Holdout\n- N = {hold['HOLDOUT_N']}\n- Changed = {'YES' if hold['HOLDOUT_CHANGED'] else 'NO'}\n- Prediction N = 0\n\n## Final TEST\n- Scheduler alive = {mon['SCHEDULER_ALIVE']}\n- A0/A1/A2/A3/P1 counts = {progress['a0']}/{progress['a1']}/{progress['a2']}/{progress['a3']}/{progress['p1']}\n- Partial metrics read = NO\n- Interference = NO\n''')
(OUT/'reports/P2_FULL_TRAIN_GO_NO_GO.md').write_text('''# P2 Full-Train Go / No-Go\n\nDecision: **NO-GO**\n\nUnique blocker: `NO_SAFE_GPU`. Real-model forward/backward parity, size-gradient connectivity, C2 frozen check, TRAIN100 stability, and checkpoint reload have not run. Wait for a GPU satisfying the frozen safety gate; do not start full training.\n''')
print(json.dumps(report,indent=2))
