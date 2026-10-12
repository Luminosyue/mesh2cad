from pathlib import Path
import json,subprocess,csv,hashlib,os
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1')
original={r['gpu']:r for r in json.loads((E/'audits/gpu_reservations_snapshot.json').read_text())};restored=json.loads((E/'audits/gpu_lease_restored.json').read_text());assert {r['gpu'] for r in restored}=={0,4,5}
expected={0:43542,4:40898,5:44094}
gpu_rows=list(csv.reader(subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid','--format=csv,noheader,nounits'],text=True).splitlines()));indices={r[1].strip():int(r[0]) for r in gpu_rows}
apps=list(csv.reader(subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_memory','--format=csv,noheader,nounits'],text=True).splitlines()));results=[]
for r in restored:
 p=Path(f"/proc/{r['pid']}");assert p.stat().st_uid==os.getuid();assert hashlib.sha256((p/'cmdline').read_bytes()).hexdigest()==original[r['gpu']]['cmdline_sha256']
 app=next(row for row in apps if int(row[0])==r['pid']);assert indices[app[1].strip()]==r['gpu'];memory=int(app[2].strip());assert memory>=expected[r['gpu']]-128
 results.append(dict(r,used_memory_MiB=memory,previous_used_memory_MiB=expected[r['gpu']],original_command_restored=True))
(E/'audits/gpu_restore_verification.json').write_text(json.dumps({'PASS':True,'rows':results},indent=2));print(json.dumps(results,indent=2))
