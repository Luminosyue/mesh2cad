#!/usr/bin/env python3
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_fullstack_mesh2cad_mac_v6')
for pid in [f'CADPART_{i:03d}' for i in range(8)]:
    source=ROOT/'02_cad_part_graph'/pid/'source_part.obj'
    for d in sorted((ROOT/'08_multi_candidate_mac'/pid).glob('CANDIDATE_*')):
        step=d/'candidate.step';backup=d/'candidate.pre_dispatch_fix.step'
        if step.is_file():
            if backup.is_file():backup.unlink()
            step.rename(backup)
        started=time.time();run=subprocess.run([sys.executable,str(d/'generated_code.py'),'--source-mesh',str(source),'--output',str(step)],text=True,capture_output=True,timeout=300)
        (d/'reexecution_v6_runtime.stdout.log').write_text(run.stdout);(d/'reexecution_v6_runtime.stderr.log').write_text(run.stderr)
        manifest=d/'candidate_manifest.json';x=json.loads(manifest.read_text());x.update({'execution_exit_code':run.returncode,'step_exists':step.is_file(),'runtime_reexecuted_after_dispatch_fix':True,'runtime_reexecution_elapsed_seconds':time.time()-started});manifest.write_text(json.dumps(x,indent=2)+'\n')
        print(pid,d.name,run.returncode,step.is_file(),flush=True)
