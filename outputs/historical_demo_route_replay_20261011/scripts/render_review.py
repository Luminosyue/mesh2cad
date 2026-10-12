from pathlib import Path
import json
import numpy as np,trimesh,cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/historical_demo_route_replay_20261011')
B=O.parent
items=json.loads((O/'manifest.json').read_text())['cases']+json.loads((O/'historical_controls.json').read_text())
results={r['case_id']:r for r in json.loads((O/'comparison.json').read_text())}
for row in items:
 case=row.get('object',row.get('case'));pid=row['part'];key=case+'/'+pid;r=results[key]
 if 'after' not in r:continue
 src=trimesh.load(row['source'],force='mesh',process=True)
 if 'historical_cad_dir' in row:old=Path(row['historical_cad_dir'])/(pid+'.step')
 else:
  old=B/'targeted_cad_structure_diagnosis_v1/cases'/case/pid/'final/cad.step'
  if not old.exists():old=Path(row['baseline_dir'])/'cad/cad.step'
 s=cq.importers.importStep(str(old)).val();v,f=s.tessellate(float(max(src.extents))*.0005,.1);before=trimesh.Trimesh([x.toTuple() for x in v],f,process=True)
 after=trimesh.load(O/case/'xpart_parts_cadquery_features'/pid/'reloaded_eval.ply',force='mesh')
 meshes=[src,before,after];cen=src.bounds.mean(0);span=float(np.max(np.ptp(np.vstack([m.bounding_box.vertices for m in meshes]),axis=0)))
 display=[]
 for mesh in meshes:
  display.append(mesh.simplify_quadric_decimation(face_count=12000) if len(mesh.faces)>12000 else mesh)
 panels=[[(0,'#3385cc',1)],[(1,'#db9d40',1)],[(2,'#db9d40',1)],[(0,'#3385cc',.35),(2,'#dd632f',.45)]]
 fig=plt.figure(figsize=(18,5.4),facecolor='#f7f9fc');labels=['Source mesh','Before / stored CAD','Historical generator replay','Source / replay overlay']
 for j,panel in enumerate(panels):
  ax=fig.add_subplot(1,4,j+1,projection='3d',facecolor='#f7f9fc')
  for idx,color,alpha in panel:
   mesh=display[idx];light=np.array([.3,-.5,.8]);light/=np.linalg.norm(light);shade=.55+.45*np.clip(mesh.face_normals@light,0,1);colors=np.array(to_rgb(color))[None,:]*shade[:,None]
   ax.add_collection3d(Poly3DCollection(mesh.triangles,facecolors=colors,edgecolors='none',alpha=alpha,rasterized=True))
  ax.set(xlim=(cen[0]-span*.55,cen[0]+span*.55),ylim=(cen[1]-span*.55,cen[1]+span*.55),zlim=(cen[2]-span*.55,cen[2]+span*.55));ax.set_box_aspect((1,1,1));ax.view_init(22,35);ax.set_axis_off()
  title=labels[j]
  if j in [1,2]:m=r['before' if j==1 else 'after'];title+='\nIoU %.4f | NCD %.4f'%(m['iou'],m['normalized_chamfer'])
  ax.set_title(title,fontsize=11,pad=4)
 fig.suptitle(key+' | same camera, scale and coordinates',fontsize=14,y=.96)
 fig.text(.5,.025,'Display meshes simplified to at most 12k faces; metrics use full STEP tessellations.',ha='center',fontsize=10)
 fig.subplots_adjust(left=.01,right=.99,bottom=.08,top=.78,wspace=.02)
 fig.savefig(O/'visualizations'/(key.replace('/','_')+'.png'),dpi=140);plt.close(fig);print('RENDERED',key,flush=True)
