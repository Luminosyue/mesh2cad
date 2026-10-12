from pathlib import Path
import numpy as np, trimesh, json, hashlib
out=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/tire_part006_p1_inference_20260919')
mesh=trimesh.load(out/'source.stl',force='mesh',process=True)
diag=float(np.linalg.norm(mesh.extents)); scale=6/diag
tf=dict(source_bbox_min=mesh.bounds[0].tolist(),source_bbox_max=mesh.bounds[1].tolist(),source_diagonal=diag,target_diagonal=6.,scale=scale,translation=(-scale*mesh.bounds[0]).tolist())
points,fi=trimesh.sample.sample_surface(mesh,8192,seed=20260919)
feats=np.c_[points*scale+tf['translation'],mesh.face_normals[fi]].astype('float32')
dst=out/'inputs/PART_006'; dst.mkdir(parents=True,exist_ok=True)
np.save(dst/'surface_points.npy',feats)
(dst/'transform.json').write_text(json.dumps({'transform':tf},indent=2))
(dst/'input_meta.json').write_text(json.dumps({'source_sha256':hashlib.sha256((out/'source.stl').read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'faces':len(mesh.faces),'watertight':bool(mesh.is_watertight),'surface_shape':list(feats.shape)},indent=2))
print((dst/'input_meta.json').read_text())
