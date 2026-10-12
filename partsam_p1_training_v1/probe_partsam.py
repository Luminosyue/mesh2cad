from pathlib import Path
import trimesh,numpy as np,json,collections,csv
R=Path('/data/home/cuiyuehan/project/mesh2cad');F=R/'partsam_cad_iou_top1000_v1'
rows=list(csv.DictReader((F/'manifests/top1000.csv').open()))
print('KINDS',collections.Counter(r['geometry_class'] for r in rows))
for r in rows[:3]:
 a=trimesh.load(R/'partsam/PartObjaverse-Tiny_instance_stl'/r['object_id']/f"part_{int(r['part_id']):03d}.stl",force='mesh',process=True)
 b=trimesh.load(r['source_mesh_path'],force='mesh',process=True)
 print(r['case_id'],'STL',a.bounds.tolist(),len(a.faces),'FIT',b.bounds.tolist(),len(b.faces))
 print('ratio',a.extents/b.extents)
PY=R/'scripts'
print('PYTHON DEPS')
import torch,transformers,rtree
print(torch.__version__,transformers.__version__)
