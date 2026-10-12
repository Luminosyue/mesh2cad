import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,hashlib,ast
from pathlib import Path
import numpy as np,trimesh
O=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
errors=[];part_n=0;max_error=0.;candidate_n=0
rows=read(O/'manifests/objects_frozen.json')
for obj in rows:
 d=O/'objects'/obj['object_id'];m=trimesh.load(obj['canonical_path'],force='mesh',process=True);pm=read(d/'p3/parts_manifest.json');ids=[]
 if sha(d/'source/object_mesh.obj')!=obj['source_object_sha256']:errors.append(obj['object_id']+':source hash')
 for p in pm['parts']:
  part_n+=1;pd=d/'parts'/p['part_id'];ids.extend(np.load(p['source_face_indices_path']).tolist())
  if sha(Path(p['part_mesh_path']))!=p['part_mesh_sha256']:errors.append(p['part_mesh_path']+':part hash')
  if (pd/'source/part_local.ply').exists():
   lm=trimesh.load(pd/'source/part_local.ply',force='mesh',process=True);lm.apply_transform(p['world_transform']);orig=trimesh.load(p['part_mesh_path'],force='mesh',process=True)
   e=float(np.max(np.abs(lm.bounds-orig.bounds)));max_error=max(max_error,e)
   if e>1e-6:errors.append(str(pd)+':transform bounds')
  if (pd/'result.json').exists():
   r=read(pd/'result.json')
   if len(r['attempts'])>8:errors.append(str(pd)+':candidate budget')
   for a in r['attempts']:
    candidate_n+=1;code=Path(a['path'])/'cad.py';tree=ast.parse(code.read_text());attrs=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    if any(x in attrs for x in ['importStep','importShape','makePolygon','makeShell','makeSolid','makeFromWires']):errors.append(str(code)+':mesh wrapper or unsupported construction')
    if sum(attrs.count(x) for x in ['extrude','revolve','loft','box','sphere'])>8 or sum(attrs.count(x) for x in ['union','cut','intersect'])>6:errors.append(str(code)+':complexity budget')
   if r['status']=='STRICT_ACCEPT':
    g=r['metrics']
    if not(g['iou']>=.90 and g['normalized_chamfer']<=.01 and g['bbox_error']<=.03 and g['centroid_l2_error']<=.02):errors.append(str(pd)+':strict threshold')
  elif p['size_class']!='MICRO_PART' and p['part_quality']!='DEGENERATE':errors.append(str(pd)+':missing CAD attempt')
 if len(ids)!=len(m.faces) or not np.array_equal(np.sort(ids),np.arange(len(m.faces))):errors.append(str(d)+':face coverage')
 for p in ['assembly/assembly_metrics.json','provenance_complete.json']:
  if not (d/p).exists():errors.append(str(d/p)+':missing')
for kind in ['pseudo','exact']:
 for pair in read(O/'manifests'/f'{kind}_pairs.json'):
  if pair.get('part_id'):
   r=read(O/'objects'/pair['object_id']/'parts'/pair['part_id']/'result.json')
   if r['status']!='STRICT_ACCEPT':errors.append(str(pair)+':nonstrict pair')
  if kind=='exact' and (not pair['higher_triangle_count'] or not Path(pair['mesh_path']).exists()):errors.append(str(pair)+':exact mesh')
out={'pass':not errors,'object_n':len(rows),'part_n':part_n,'candidate_n':candidate_n,'max_part_transform_bbox_error':max_error,'errors':errors}
(O/'integrity/FINAL_VALIDATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
assert not errors
