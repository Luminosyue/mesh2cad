from pathlib import Path
import os,signal,subprocess,time
EXP=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1')
me=os.getpid()
for p in Path('/proc').iterdir():
 if not p.name.isdigit() or int(p.name)==me:continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if str(EXP/'launch/a2_orchestrate.py').encode() in args and args[0].endswith(b'python3'):os.kill(int(p.name),signal.SIGTERM)
with (EXP/'logs/orchestrator.log').open('a') as log:
 p=subprocess.Popen(['/usr/bin/python3','-u',str(EXP/'launch/a2_orchestrate.py')],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
print('ORCHESTRATOR_PID',p.pid)
