from pathlib import Path
import concurrent.futures,json
from server_batch_cad import OUT,SRC,one
reports=[p for p in OUT.glob('*/*_report.json') if json.loads(p.read_text()).get('status')=='FAILED']
active=set()
for p in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        argv=p.read_bytes().decode(errors='replace').split('\0')
        active.update(a for a in argv if a.startswith(str(OUT)) and a.endswith('_cad.py'))
    except (PermissionError,FileNotFoundError,ProcessLookupError):pass
files=[SRC/json.loads(p.read_text())['relative_path'] for p in reports
       if str(p.with_name(p.name.replace('_report.json','_cad.py'))) not in active]
print('Retrying',len(files),'failed parts',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    for r in pool.map(one,files):print(r['relative_path'],r['status'],r.get('representation'),r.get('error','')[-300:],flush=True)
