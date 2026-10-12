from pathlib import Path
import json,zipfile,hashlib
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_additional100_20261012/runs/new_object_101')
assert (O/'summary.json').is_file()
summary=json.loads((O/'summary.json').read_text())
notes='''NEW OBJECTS - HISTORICAL ROUTE REPLAY

Three source objects: Blender, CoffeeMaker, BlackKitchenChair.
Source hashes were excluded from both earlier 20-object batches.
P3 and X-Part were rerun for these objects. Historical CAD candidates were not reused.
Pipeline: P3 parts -> official X-Part completion -> section-based CadQuery fitting.

Counts:
'''+json.dumps({k:v for k,v in summary.items() if k.endswith('_n')},indent=2)+'''

Quality labels:
CAD validity means a reloaded STEP contains valid solids. This is not a geometry acceptance test.
STRICT_ORIGINAL compares CAD against the original P3 segment.
STRICT_COMPLETED_ONLY passes only against the X-Part completed segment.
Thresholds: voxel IoU >= 0.90, normalized Chamfer <= 0.01,
bbox error <= 0.03, surface centroid error <= 0.02.
IoU is a 128-grid approximate occupancy metric; open input meshes can affect its meaning.
X-Part may change the source geometry. Both reference comparisons are retained.
Assemblies contain all valid candidates, including geometry rejects; they are diagnostic, not strict ground truth.
Dense lofts are inferred parametric approximations, not recovered original design histories.

Files:
objects/*/xpart_parts_cadquery_features/PART_*/PART_*.py: standalone CadQuery programs.
Run each program with a compatible CadQuery Python environment to regenerate the adjacent STEP.
objects/*/assembly/diagnostic_original_coordinates.step: assembly in original input coordinates.
objects/*/assembly/diagnostic_canonical.step: normalized assembly used by this experiment.
visualizations/index.html: stage comparisons and per-part metrics.
summary.json and part_results.json: complete evaluation results.
delivery_manifest.json: SHA-256 hashes for delivered files.

Model weights and large mesh intermediates remain on the server and are not included in this archive.
Remote absolute paths in manifests record provenance; pipeline drivers require the server dataset/environment.
'''
(O/'README.txt').write_text(notes)
files=set()
for name in ['README.txt','summary.json','part_results.json','generation_status.json','gpu_assignment.json','program_validation.json']:
 p=O/name
 if p.is_file():files.add(p)
for folder in ['manifests','config','scripts','visualizations']:
 files.update(p for p in (O/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for d in (O/'objects').iterdir():
 if not d.is_dir():continue
 for name in ['run_status.json','source/provenance.json','p3/parts_manifest.json','p3/part_metadata.json','xpart_parts/manifest.json','assembly/result.json','assembly/diagnostic_canonical.step','assembly/diagnostic_original_coordinates.step']:
  p=d/name
  if p.is_file():files.add(p)
 for p in (d/'xpart_parts_cadquery_features').rglob('*'):
  if p.is_file() and p.suffix in ['.py','.step','.json','.log'] and 'checkpoint' not in p.parts:files.add(p)
manifest=[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
(O/'delivery_manifest.json').write_text(json.dumps(manifest,indent=2))
files.add(O/'delivery_manifest.json')
dest=O/'new_objects_cad_results.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files):z.write(p,str(p.relative_to(O)))
print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'file_count':len(files)}),flush=True)
