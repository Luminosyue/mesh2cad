from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent/'samples'; failed=[]
for script in sorted(root.rglob('cad_model.py')):
    p=subprocess.run([sys.executable,str(script)],cwd=script.parent,capture_output=True,text=True)
    if p.returncode: failed.append((str(script),p.stderr[-500:]))
print({'total':len(list(root.rglob('cad_model.py'))),'failed':len(failed)})
for x in failed: print(x)
if failed: raise SystemExit(1)