from pathlib import Path
from importlib.metadata import version
import json,platform
root=Path('/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_cad')
packages={}
for name in ['cadquery','cadquery-ocp','numpy','trimesh']:
    try:packages[name]=version(name)
    except Exception:pass
(root/'environment.json').write_text(json.dumps({'python':platform.python_version(),'packages':packages},indent=2))
(root/'requirements.txt').write_text('\n'.join(k+'=='+v for k,v in packages.items())+'\n')
for name in ['server_diagnose.py','server_fix_probe.py','server_import_probe.py','probe_fixed.step']:
    path=root/'scripts'/name
    if path.parent.resolve()!=(root/'scripts').resolve():raise RuntimeError('Unexpected cleanup target')
    path.unlink(missing_ok=True)
print(json.dumps(packages,indent=2))
