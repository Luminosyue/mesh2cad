from pathlib import Path
import json,os,time,subprocess
r=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_cadrecode_parts21_20260926_v2')
print('TIME',time.time())
for method in ['cadrille','cadrecode']:
 print(method)
 for p in sorted((r/method).glob('*'))[:5]: print(p,p.stat().st_mtime)
 print('DONE',(r/method/'SHARD_0.DONE').read_text())
 files=sorted((r/method).glob('*/PART_*/STATUS.json'),key=lambda p:p.stat().st_mtime)
 for p in [files[0],files[-1]]:print(p,p.stat().st_mtime,p.read_text()[:650])
print(subprocess.run(['ps','-p','3170808,3170809','-o','pid,etime,stat,args'],capture_output=True,text=True).stdout)
print(subprocess.run(['free','-h'],capture_output=True,text=True).stdout)
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  s=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
  if 'parts21' in s and 'inspect' not in s:print(p.name,s[:500])
 except:pass
