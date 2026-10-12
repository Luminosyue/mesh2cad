import json
from pathlib import Path
import numpy as np, open3d as o3d
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_batch_run')
for case in ['airplane','wheel','kettle']:
 c=ROOT/case; pred=c/'predictions'/'B'; rows=[]; allm=[]
 for rf in sorted(pred.glob('PART_*/row.json')):
  rows.append(json.loads(rf.read_text())); sf=rf.parent/'global'/'pred.stl'
  if sf.exists():
   m=o3d.io.read_triangle_mesh(str(sf))
   if len(m.triangles): allm.append(m)
 if not allm: continue
 mesh=o3d.geometry.TriangleMesh()
 for m in allm: mesh+=m
 mesh.compute_vertex_normals(); mesh.paint_uniform_color([0.12,0.48,0.92])
 o3d.io.write_triangle_mesh(str(c/'p1_surface_curve_assembly.stl'),mesh)
 r=o3d.visualization.rendering.OffscreenRenderer(1100,850); r.scene.set_background([0.93,0.95,0.99,1]); mat=o3d.visualization.rendering.MaterialRecord(); mat.shader='defaultLit'; r.scene.add_geometry('cad',mesh,mat)
 b=mesh.get_axis_aligned_bounding_box(); center=b.get_center(); d=float(max(np.asarray(b.get_extent())))*2.4; r.setup_camera(52,center,center+np.array([d,d,d]),[0,0,1]); o3d.io.write_image(str(c/'p1_surface_curve_3d.png'),r.render_to_image(),9)
 (c/'p1_surface_curve_report.json').write_text(json.dumps({'case':case,'method':'P1 arm B Surface+Curve','parts':rows,'valid_parts':sum(bool(x.get('step_ok_global')) for x in rows)},indent=2))
