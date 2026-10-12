from pathlib import Path
import os,sys,json,hashlib,signal,time,subprocess
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1')
SNAP=E/'audits/gpu_reservations_snapshot.json';PIDS={0:237952,4:4182513,5:4182515}
mode=sys.argv[1]
if mode=='snapshot':
 assert not SNAP.exists()
 rows=[]
 for gpu,pid in PIDS.items():
  p=Path(f'/proc/{pid}');raw=(p/'cmdline').read_bytes();argv=[v.decode() for v in raw.split(b'\0') if v];env={}
  for item in (p/'environ').read_bytes().split(b'\0'):
   k,sep,v=item.partition(b'=')
   if k.decode(errors='replace') in ['CUDA_VISIBLE_DEVICES','LEAVE_BYTES','LD_LIBRARY_PATH','PATH','PYTHONPATH']:env[k.decode()]=v.decode()
  assert p.stat().st_uid==os.getuid();assert 'torch.empty' in argv[-1] and 'sleep' in argv[-1]
  rows.append({'gpu':gpu,'pid':pid,'start_ticks':(p/'stat').read_text().split()[21],'argv':argv,'selected_env':env,'cwd':os.readlink(p/'cwd'),'cmdline_sha256':hashlib.sha256(raw).hexdigest()})
 SNAP.write_text(json.dumps(rows,indent=2));print('SNAPSHOT_ONLY_NO_PROCESSES_CHANGED',[(r['gpu'],r['pid']) for r in rows])
elif mode=='release':
 # Execute only after explicit user authorization arrives in this task.
 assert (E/'control/gpu_lease_user_authorized.json').exists()
 rows=json.loads(SNAP.read_text())
 for r in rows:
  p=Path(f"/proc/{r['pid']}");assert p.stat().st_uid==os.getuid()
  assert (p/'stat').read_text().split()[21]==r['start_ticks'];assert hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==r['cmdline_sha256']
 for r in rows:os.kill(r['pid'],signal.SIGTERM)
 time.sleep(3)
 assert all(not Path(f"/proc/{r['pid']}/cmdline").exists() or not Path(f"/proc/{r['pid']}/cmdline").read_bytes() for r in rows)
 (E/'audits/gpu_lease_released.json').write_text(json.dumps({'time':time.time(),'pids':[r['pid'] for r in rows]},indent=2));print('RELEASED')
elif mode=='restore':
 assert (E/'audits/gpu_lease_released.json').exists()
 restored=json.loads((E/'audits/gpu_lease_restored.json').read_text()) if (E/'audits/gpu_lease_restored.json').exists() else []
 requested={int(v) for v in sys.argv[2:]} if len(sys.argv)>2 else set(PIDS)
 for r in json.loads(SNAP.read_text()):
  if r['gpu'] not in requested or any(x['gpu']==r['gpu'] for x in restored):continue
  env=os.environ.copy();env.update(r['selected_env'])
  with (E/f"logs/gpu_reservation_restore_{r['gpu']}.log").open('w') as log:
   p=subprocess.Popen(r['argv'],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,cwd=r['cwd'],env=env,start_new_session=True)
  restored.append({'gpu':r['gpu'],'pid':p.pid})
 target=E/'audits/gpu_lease_restored.json';tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(restored,indent=2));tmp.replace(target);print('RESTORED',restored)
