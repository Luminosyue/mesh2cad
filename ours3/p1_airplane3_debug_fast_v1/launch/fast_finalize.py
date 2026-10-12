from pathlib import Path
import json,hashlib,gzip,ast,subprocess,csv,os,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1';parts=['PART_000','PART_001','PART_005'];read=lambda p:json.loads(p.read_text());summaries=[];checks=[]
for d in (E/'evaluations').iterdir():
 if not d.is_dir():continue
 rows=[]
 for part in parts:
  f=d/part
  if not (f/'result.json').exists():continue
  r=read(f/'result.json');gt=sum(read(f/'gt_tokens.json'),[]);pred=sum((b['token_ids'] for b in read(f/'predicted_tokens.json')),[])
  assert r['SEQUENCE_EXACT_MATCH']==(gt==pred)
  assert gt==read(OLD/'audits/gt_supervised_tokens_for_status.json')[part]
  assert (f/'prediction.py').read_text()==''.join(b+'\n' for b in read(f/'predicted_blocks.json'))
  with gzip.open(f/'teacher_tokens.jsonl.gz','rt') as z:tf=[json.loads(line) for line in z]
  assert [t['gt_id'] for t in tf]==gt and sum(not t['CORRECT'] for t in tf)==r['TOKEN_ERRORS']
  assert r['PART_GATE_PASS']==(all(r[k] for k in ['SEQUENCE_EXACT_MATCH','BLOCK_COUNT_EXACT','BLOCK_EXACT_MATCH','EOS_TERMINATED','CAD_PARSE_PASS','CAD_EXECUTION_PASS','STEP_EXPORT_PASS','STEP_READBACK_PASS']) and not r['SAFETY_CAP_HIT'])
  rows.append(r);checks.append({'evaluation':d.name,'part':part,'raw_tokens_independently_verified':True,'prediction_reconstructed_without_edits':True,'TF_errors_recounted':r['TOKEN_ERRORS']})
 if len(rows)==3:
  summary={'tag':d.name,'complete_case_n':3,'exact_n':sum(r['SEQUENCE_EXACT_MATCH'] for r in rows),'cad_step_readback_n':sum(r['CAD_EXECUTION_PASS'] and r['STEP_READBACK_PASS'] for r in rows),'TF_errors':sum(r['TOKEN_ERRORS'] for r in rows),'gate_n':sum(r['PART_GATE_PASS'] for r in rows),'checkpoint':rows[0]['checkpoint']}
  (d/'summary.json').write_text(json.dumps(summary,indent=2));summaries.append(summary)
assert summaries
def score(r):
 step=int(r['tag'].split('-')[-1]) if r['tag'].startswith('checkpoint-') else -1
 return (r['exact_n'],r['cad_step_readback_n'],-r['TF_errors'],-step)
best=max(summaries,key=score);best['resolved_checkpoint']=str(Path(best['checkpoint']).resolve());(E/'best_checkpoint.json').write_text(json.dumps(best,indent=2))
audit={'PASS':True,'cases':checks,'best':best,'ranking':'exact count -> CAD/STEP-readback count -> fewer TF errors; earlier update breaks complete ties'}
if best['gate_n']==3:
 import cadquery as cq
 for part in parts:
  shape=cq.importers.importStep(str(E/f"evaluations/{best['tag']}/{part}/prediction.step")).val();assert shape.isValid() and shape.Solids()
 audit['best_STEP_independent_readback']=True
 (E/'audits/weighted_trial_decision.json').write_text(json.dumps({'RUN_WEIGHTED_TRIAL':False,'reason':'Strict 3/3 raw-token exact, CAD execution and independent STEP readback already passed; no residual TF errors at best checkpoint','new_optimizer_updates_used':150,'unused_update_budget':150},indent=2))
frozen=read(E/'audits/frozen_sources.json');assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in frozen.items());audit['frozen_sources_pass']=True
restored=read(E/'audits/gpu_lease_restored_2.json');snapshot=read(E/'audits/gpu_reservations_snapshot_2.json');gpu_rows=list(csv.reader(subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_memory','--format=csv,noheader,nounits'],text=True).splitlines()));gpu_checks=[]
for r in restored:
 before=next(b for b in snapshot if b['gpu']==r['gpu']);p=Path(f"/proc/{r['pid']}");assert p.stat().st_uid==os.getuid() and hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==before['cmdline_sha256'];row=next(v for v in gpu_rows if int(v[0])==r['pid']);memory=int(row[2]);assert memory>=44094-128
 gpu_checks.append({'gpu':r['gpu'],'restored_pid':r['pid'],'memory_MiB':memory,'original_command_same':True})
audit['gpu_reservation_restored']=gpu_checks
(E/'audits/final_validation.json').write_text(json.dumps(audit,indent=2))
status=read(E/'status.json');status.update(phase='COMPLETE',FAST_GATE='PASS' if best['gate_n']==3 else 'FAIL',best_checkpoint=best['checkpoint'],GPU5_restored=True,complete_evaluation_count=len(checks),elapsed_seconds=time.time()-read(E/'control/run_clock.json')['start']);(E/'status.json').write_text(json.dumps(status,indent=2))
print('INDEPENDENT_VALIDATION_PASS',best,flush=True)
