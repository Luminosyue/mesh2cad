from pathlib import Path
import json,os,signal,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1')
assert (E/'audits/gpu_lease_released.json').exists()
pid=json.loads((E/'control/orchestrator_pid.json').read_text())['pid'];os.kill(pid,signal.SIGTERM);time.sleep(1)
state=json.loads((E/'audits/orchestrator.json').read_text());paused=[]
for job in state['active']:
 p=Path(f"/proc/{job['pid']}/cmdline")
 if p.exists() and str(E/'launch/a2_runtime.py').encode() in p.read_bytes().split(b'\0'):
  os.kill(job['pid'],signal.SIGCONT);os.kill(job['pid'],signal.SIGTERM);paused.append(job)
time.sleep(5)
for job in paused:
 p=Path(f"/proc/{job['pid']}/cmdline");assert not p.exists() or not p.read_bytes()
(E/'audits/evaluation_rebalance.json').write_text(json.dumps({'paused_jobs':paused,'resume_method':'own saved prediction tokens; independent last-block replay must match exactly','time':time.time()},indent=2))
(E/'control/workers.json').write_text(json.dumps({'training':0,'finished':12,'pause_during_training':True,'gpu_pool':['1','0','4','5'],'workers_per_gpu':3}))
print('PAUSED_FOR_VERIFIED_RESUME',len(paused))
