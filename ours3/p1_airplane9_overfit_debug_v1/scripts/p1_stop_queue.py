from pathlib import Path
import os,signal,json
debug=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_overfit_debug_v1')
stopped=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
  if cmd.startswith('/usr/bin/python3') and str(debug/'scripts/p1_single_eval_queue.py') in cmd:
   os.kill(int(p.name),signal.SIGTERM);stopped.append(int(p.name))
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
(debug/'queue_stop.json').write_text(json.dumps({'pids':stopped,'reason':'Stage 9 pause: keep already-running checkpoint-200 evaluation; evaluate saved checkpoint-500 independently before any further steps'},indent=2));print(stopped)
