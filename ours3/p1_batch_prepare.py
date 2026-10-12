import json, shutil
from pathlib import Path
import numpy as np, trimesh
REPO=Path('/data/home/cuiyuehan/project/mesh2cad'); BASE=REPO/'ours3'/'p1_batch_inputs'; OUT=REPO/'ours3'/'p1_batch_run'; TARGET=6.0
def prep_mesh(mesh_path, case):
 mesh=trimesh.load(str(mesh_path), force='mesh', process=True)
 if isinstance(mesh,trimesh.Scene): mesh=trimesh.util.concatenate(tuple(g for g in mesh.geometry.values()))
 mesh.remove_unreferenced_vertices(); comps=mesh.split(only_watertight=False); comps=[m for m in comps if len(m.faces)>=20]
 if not comps: comps=[mesh]
 comps=sorted(comps,key=lambda m:m.area,reverse=True)[:40]; case_root=OUT/case
 if case_root.exists(): shutil.rmtree(case_root)
 (case_root/'packs').mkdir(parents=True); parts=[]
 for i,m in enumerate(comps):
  pid=f'PART_{i:03d}'; parts.append(pid); bbox=m.bounds; diag=float(np.linalg.norm(bbox[1]-bbox[0])); scale=TARGET/max(diag,1e-9); trans=-bbox[0]*scale
  pts,fi=trimesh.sample.sample_surface(m,8192); norm=m.face_normals[fi]; pts_c=pts*scale+trans; pack=case_root/'packs'/pid; pack.mkdir()
  np.save(pack/'surface_points.npy',np.concatenate([pts_c,norm],axis=1).astype(np.float32))
  tf={'part_id':pid,'source_coordinate':'original','p1_coordinate':'canonical normalized','transform':{'source_bbox_min':bbox[0].tolist(),'source_bbox_max':bbox[1].tolist(),'source_diagonal':diag,'target_diagonal':TARGET,'scale':scale,'translation':trans.tolist()},'inverse':{'formula':'p_original=(p_p1-translation)/scale','scale':scale,'translation':trans.tolist()}}
  (pack/'transform.json').write_text(json.dumps(tf,indent=2)); (pack/'coordinate_transform.json').write_text(json.dumps(tf['transform'],indent=2)); (pack/'input_meta.json').write_text(json.dumps({'part_id':pid,'source_mesh':str(mesh_path),'n_faces':int(len(m.faces))},indent=2)); (pack/'prepare_summary.json').write_text(json.dumps({'empty_sharp_fallback':True,'n_curve_tokens':0},indent=2)); m.export(case_root/f'{pid}.obj')
 (case_root/'parts.json').write_text(json.dumps({'case':case,'parts':parts,'source':str(mesh_path)},indent=2)); return parts
for case,path in {'wheel':BASE/'wheel.stl','kettle':BASE/'kettle.obj','irregular_highpoly':BASE/'irregular_highpoly.stl'}.items(): print(case,prep_mesh(path,case))
