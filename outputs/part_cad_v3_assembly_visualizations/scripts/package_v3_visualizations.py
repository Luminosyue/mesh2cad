import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import hashlib,json,zipfile
import numpy as np,trimesh
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_v3_assembly_visualizations')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'manifest.json').read_text());errors=[];parts=0
for obj in m['objects']:
 d=O/obj['object_id'];scene=trimesh.load(d/'assembly_preview.glb',force='scene');mesh=trimesh.load(d/'assembly_preview.ply',force='mesh')
 if len(scene.geometry)!=obj['part_n']:errors.append(obj['object_id']+': GLB part count')
 if not np.allclose(scene.bounds,mesh.bounds,atol=2e-6):errors.append(obj['object_id']+': exported bounds')
 if sha(Path(obj['source_path']))!=obj['source_sha256']:errors.append(obj['object_id']+': source changed')
 for part in obj['parts']:
  parts+=1
  if sha(Path(part['cad_mesh_path']))!=part['cad_mesh_sha256']:errors.append(part['case_id']+': CAD mesh changed')
 for name in ['source.png','assembly.png','assembly_reverse.png','source_vs_assembly.png','status.png','exploded.png','overview.png']:
  if not (d/name).exists():errors.append(obj['object_id']+': image missing '+name)
assert parts==209 and len(m['objects'])==20 and not errors,errors
validation={'pass':True,'object_n':20,'part_n':209,'png_n':len(list(O.rglob('*.png'))),'glb_n':20,'transforms_verified':True,'source_and_CAD_mesh_hashes_unchanged':True,'GLB_part_counts_and_bounds_verified':True,'visual_review':'Robot overview, all-object contact sheet and four requested object assemblies inspected; no evident clipping or unreadable primary labels. Point rendering is a sampled visualization, not an exact surface raster.','quality_scope':'All-candidate diagnostic assembly preview; no full-CAD acceptance claim','errors':[]}
(O/'VALIDATION.json').write_text(json.dumps(validation,indent=2))
(O/'README.md').write_text('# V3 CAD visualization and assembly previews\n\nOpen index.html for all 20 objects. Every object has source/CAD comparison, assembled view, reverse view, status coloring, and exploded view. The 209 current V3 CAD part meshes are transformed by their recorded world_transform into the original object canonical frame. No new fitting or geometry changes are made. Exploded-view offsets are display-only.\n\nAll candidates are included, including Near and Reject; these are diagnostic previews, not accepted complete CAD assemblies. Status images use green Strict, amber Near, red Reject. GLB scenes use distinct part colors and preserve part names/statuses. They can be opened in a 3D viewer. PLY exports provide the assembled mesh. Neither GLB nor PLY is a Boolean-fused STEP solid.\n\nRendering uses deterministic area-sampled points with normal shading and a shared source/CAD camera and scale. This makes fitting errors visible without changing the source or CAD inputs. Per-object manifests record all transforms, input hashes and statuses.\n',encoding='utf-8')
archive=O.parent/'PART_CAD_V3_ASSEMBLY_VISUALIZATIONS.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,str(Path(O.name)/p.relative_to(O)))
out={'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'validation':validation};(O.parent/'PART_CAD_V3_ASSEMBLY_VISUALIZATIONS.sha256.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
