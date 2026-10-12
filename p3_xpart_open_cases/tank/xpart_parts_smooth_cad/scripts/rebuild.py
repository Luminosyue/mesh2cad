from pathlib import Path
import json,numpy as np
from regular_patch import patch_solid
from fit_revolve import build
import trimesh
def rebuild(folder):
 folder=Path(folder);spec=json.loads((folder/'parameters.json').read_text())
 if spec['method']=='original_tire_revolve':
  from reference_tire import build_smooth
  shape=build_smooth().translate(tuple(-np.array(spec['center']))).scale(spec['construction_scale'])
 elif spec['method']=='axisymmetric_spline_revolve':shape=build(spec)
 else:
  d=np.load(folder/'control_mesh.npz');m=trimesh.Trimesh(d['vertices'],d['faces'],process=False);shape=patch_solid(m,spec['curvature_strength'],d['normals'],spec.get('max_normal_projection'))
 if spec.get('apply_shape_fix'):shape=shape.fix()
 shape=shape.scale(1/spec['construction_scale']).translate(tuple(spec['center']))
 if not shape.isValid():raise ValueError('Rebuilt shape is invalid')
 target=folder/(folder.name+'_rebuilt.step');shape.exportStep(str(target),write_pcurves=spec.get('write_pcurves',True),precision_mode=0 if spec.get('step_patch_repair') else spec.get('precision_mode',0))
 if spec.get('repair_step_roundtrip'):
  import cadquery as cq
  result=cq.importers.importStep(str(target)).val()
  if spec.get('step_patch_repair'):
   from step_patch_repair import repair_patches,valid
   result,_=repair_patches(result,spec['center'],spec['construction_scale']);result.exportStep(str(target),precision_mode=spec.get('precision_mode',1));result=cq.importers.importStep(str(target)).val()
   if not valid(result) or len(result.Solids())!=1:raise ValueError('Targeted STEP face repair failed')
   return result
  if not result.isValid():
   result=result.fix();result.exportStep(str(target),write_pcurves=spec.get('write_pcurves',True),precision_mode=spec.get('precision_mode',0));result=cq.importers.importStep(str(target)).val()
  if not result.isValid() or len(result.Solids())!=1:raise ValueError('STEP roundtrip repair failed')
 return shape
