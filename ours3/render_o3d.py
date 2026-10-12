import json
from pathlib import Path
import numpy as np, open3d as o3d
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_batch_run')
for case in ['airplane','wheel','kettle','toaster','irregular_highpoly']:
 c=ROOT/case; pred=c/'predictions'/'A'; rows=[]; allm=[]
 for rf in sorted(pred.glob('PART_*/row.json')):
  r=json.loads(rf.read_text()); rows.append(r); sf=rf.parent/'global'/'pred.stl'
  if sf.exists():
   m=o3d.io.read_triangle_mesh(str(sf));
   if len(m.triangles): allm.append(m)
 if not allm: continue
 mesh=o3d.geometry.TriangleMesh()
 for m in allm: mesh+=m
 mesh.compute_vertex_normals(); mesh.paint_uniform_color([0.25,0.55,0.9])
 o3d.io.write_triangle_mesh(str(c/'p1_assembly_global.stl'),mesh)
 r=o3d.visualization.rendering.OffscreenRenderer(1000,800)
 r.scene.set_background([0.94,0.95,0.98,1]); mat=o3d.visualization.rendering.MaterialRecord(); mat.shader='defaultLit'; r.scene.add_geometry('cad',mesh,mat)
 bounds=mesh.get_axis_aligned_bounding_box(); center=bounds.get_center(); ext=np.asarray(bounds.get_extent()); dist=float(max(ext))*2.3
 r.setup_camera(55.0,center,center+np.array([dist,dist,dist]),[0,0,1]); img=r.render_to_image(); o3d.io.write_image(str(c/'p1_assembly_3d.png'),img,9)
 (c/'p1_report.json').write_text(json.dumps({'case':case,'method':'P1 arm A checkpoint-8000','segmented_parts':len(rows),'valid_parts':sum(bool(x.get('step_ok_global')) for x in rows),'parts':rows,'render':'p1_assembly_3d.png'},indent=2))
summary={}
for case in ['airplane','wheel','kettle','toaster','irregular_highpoly']:
 p=ROOT/case/'p1_report.json'
 if p.exists():
  x=json.loads(p.read_text()); summary[case]={'segmented_parts':x['segmented_parts'],'valid_parts':x['valid_parts'],'success_rate':x['valid_parts']/max(1,x['segmented_parts']),'render':str(ROOT/case/'p1_assembly_3d.png')}
(ROOT/'p1_summary.json').write_text(json.dumps(summary,indent=2))
