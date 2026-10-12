import ast,json,csv,sys
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1'
keys={};fkeys={}
for p in (O/'objects').glob('*/PART_MANIFEST.csv'):
 for r in csv.DictReader(p.open()):
  ns={};t=ast.parse(Path(r['CAD_PATH']).read_text(encoding='utf-8-sig'))
  for n in t.body:
   if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='PARAMETERS' for a in n.targets):v=json.loads(ast.literal_eval(n.value.args[0]));break
  op=v.get('operation');keys.setdefault(op,set()).update(v)
  for f in v.get('features',[]):fkeys.setdefault(f.get('type'),set()).update(f)
print({k:sorted(v) for k,v in keys.items()});print({k:sorted(v) for k,v in fkeys.items()})
import cadquery,trimesh,vtk
print('ENV_OK',cadquery.__version__,vtk.vtkVersion.GetVTKVersion())
