import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
from pathlib import Path
import numpy as np,cadquery as cq
O=Path(__file__).resolve().parents[1]
def bbox(s):
 b=s.BoundingBox();return np.array([[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]])
rows=[]
for path in sorted((O/'objects').glob('*/assembly/assembly_metrics.json')):
 r=json.loads(path.read_text())
 if not r.get('step_reload_pass'):continue
 d=path.parent;obj=json.loads((d.parent/'source/provenance.json').read_text());T=np.array(obj['inverse_object_transform']);scale=float(T[0,0]);translation=T[:3,3]
 canonical=cq.importers.importStep(str(d/'assembly.step')).val();world=cq.importers.importStep(str(d/'object_reconstructed.step')).val();scope={};exec(compile((d/'object_reconstructed.py').read_text(),str(d/'object_reconstructed.py'),'exec'),scope);native=scope['result'].val()
 e=float(np.max(np.abs(bbox(canonical)*scale+translation-bbox(world))));e2=float(np.max(np.abs(bbox(native)-bbox(world))));v=abs(native.Volume()-world.Volume())/max(abs(world.Volume()),1e-15)
 passed=canonical.isValid() and world.isValid() and native.isValid() and len(world.Solids())==r['solid_count'] and e<max(scale,1)*1e-6 and e2<max(scale,1)*1e-6 and v<1e-6
 rows.append({'object_id':r['object_id'],'pass':passed,'source_coordinate_transform_bbox_error':e,'independent_native_program_bbox_error':e2,'relative_volume_error':v,'solid_count':len(world.Solids())})
out={'pass':all(r['pass'] for r in rows),'source_assemblies_checked':len(rows),'assemblies':rows}
(O/'integrity/ASSEMBLY_VALIDATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['pass']
