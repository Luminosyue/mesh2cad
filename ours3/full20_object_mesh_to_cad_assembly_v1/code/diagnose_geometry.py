from pathlib import Path
import sys,json,runpy
import numpy as np,cadquery as cq
sys.path.insert(0,str(Path(__file__).parent));import pipeline as p
rows=[]
for file in p.O.glob('objects/*/cad_parts/*/result.json'):
 r=json.loads(file.read_text())
 if r.get('FAILURE_REASON')!='RAW_VS_Q14_GEOMETRY_TOLERANCE':continue
 d=file.parent;raw=cq.importers.importStep(str(d/'raw.step')).val();q=cq.importers.importStep(str(d/'part.step')).val();b=raw.BoundingBox();diag=(b.xlen*b.xlen+b.ylen*b.ylen+b.zlen*b.zlen)**.5
 pr=p.readparams(d/'cad_program.py');ints=[]
 def walk(x,path=''):
  if isinstance(x,dict):
   for k,v in x.items():walk(v,path+'.'+k)
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,path+f'[{i}]')
  elif type(x) is int and x!=0:ints.append((path,x))
 walk(pr.get('features',[]));walk(pr.get('profile',[]));ca=np.array(raw.Center().toTuple());cb=np.array(q.Center().toTuple())
 rows.append(dict(object=r['OBJECT_ID'],part=r['PART_ID'],reported=json.loads((d/'geometry_report.json').read_text()),brep_volume_centroid_error=float(np.linalg.norm(ca-cb)/diag),nonzero_geometry_ints=ints[:15],raw_area=raw.Area(),q_area=q.Area(),raw_solids=len(raw.Solids()),q_solids=len(q.Solids())))
p.dump(p.O/'reports/GEOMETRY_FAILURE_DIAGNOSTIC.json',rows);print(json.dumps(rows,indent=2))
