from pathlib import Path
import json,collections,time
from server_batch_cad import OUT,SRC
active=set()
for p in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        active.update(a for a in p.read_bytes().decode(errors='replace').split('\0')
                      if a.startswith(str(OUT)) and a.endswith('_cad.py'))
    except (PermissionError,FileNotFoundError,ProcessLookupError):pass
rows=[]
for p in OUT.glob('*/*_report.json'):
    r=json.loads(p.read_text())
    if str(p.with_name(p.name.replace('_report.json','_cad.py'))) in active:r['status']='RUNNING'
    rows.append(r)
counts=collections.Counter(r['status'] for r in rows)
summary={'phase':'retrying' if active else 'verification','total':len(list(SRC.rglob('*.stl'))),'processed':len(rows),
         'status_counts':dict(counts),'representation_counts':dict(collections.Counter(r.get('representation','pending') for r in rows)),
         'complete':len(rows)==2112 and counts['SUCCESS']==2112 and not active,'output_root':str(OUT)}
(OUT/'progress.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
for path in sorted(active):
    p=Path(path);log=p.with_name(p.name.replace('_cad.py','_conversion.log'))
    content=log.read_text(errors='replace').splitlines() if log.exists() else []
    stages=[x for x in content if x.startswith('CAD_STAGE')]
    print('ACTIVE',str(p.relative_to(OUT)),stages[-1] if stages else 'earlier runtime',flush=True)
