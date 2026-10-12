from pathlib import Path
import json,collections,shutil
root=Path('/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_cad')
records=[json.loads(p.read_text()) for p in root.glob('*/*_report.json')]
print(json.dumps({'reported':len(records),'status':dict(collections.Counter(r['status'] for r in records)),
                  'representation':dict(collections.Counter(r.get('representation','failed') for r in records)),
                  'output_gb':sum(p.stat().st_size for p in root.glob('*/*') if p.is_file())/1e9,
                  'free_gb':shutil.disk_usage(root).free/1e9},indent=2))
if (root/'progress.json').exists():print((root/'progress.json').read_text())
for r in records:
    if r['status']=='FAILED':print(r['relative_path'],r['error'].strip().splitlines()[-1])
