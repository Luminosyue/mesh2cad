from pathlib import Path
import json,cadquery as cq
R=Path('/data/home/cuiyuehan/project/mesh2cad/partsam_p1_training_v1')
for p in R.glob('PartSAM/geometry_pack_v1/*/record.json'):
 r=json.loads(p.read_text())
 if r.get('status')=='geometry_ready':
  s=json.loads((p.parent/'fitted_parameters_canonical.json').read_text())
  h=(s['zmax']-s['zmin']) if s['kind']!='box' else min(b-a for a,b in zip(s['mins'],s['maxs']))
  shape=cq.importers.importStep(str(p.parent/'model.step')).val();eff=2*shape.Volume()/shape.Area()/6
  print(r['sample_id'],s['kind'],'height',round(h,8),'effective',round(eff,8),'keep',h>=.0006 and eff>=.0001)
