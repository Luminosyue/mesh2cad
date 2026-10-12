import subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
with (root/'finish_pipeline.log').open('a') as f:
    p=subprocess.Popen(['/usr/bin/python3','-u',str(root/'finish_pipeline.py')],cwd=root,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
print(p.pid)
