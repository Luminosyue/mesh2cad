import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path
import cadquery as cq
import numpy as np
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');O=B/'p1_geometry_scale_coordinate_audit_v1';S=B/'p1_geometry_success_showcase_v1/renders';ids=['deepcad__0062_00623202','deepcad__0008_00080235','deepcad__0002_00024054','fusion360__41970_24ba0c1b_0009'];labs=['GT','A0','A1','A3','P1'];dirs={'GT':S,'A0':B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0','A1':B/'m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1','A3':B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3','P1':B/'p1_exact9998_val1000_eval_v2'}
fig,ax=plt.subplots(len(ids),len(labs),figsize=(15,10),subplot_kw={'projection':'3d'})
for i,c in enumerate(ids):
 for j,l in enumerate(labs):
  p=(dirs[l]/f'{c}__{l}.step') if l=='GT' else dirs[l]/c/'pred.step'; a=ax[i,j];a.set_axis_off();
  try:
   s=cq.importers.importStep(str(p)).val();v,f=s.tessellate(.001);v=np.array([[q.x,q.y,q.z] for q in v]);mn=v.min(0);mx=v.max(0);v=(v-(mn+mx)/2)/max(np.linalg.norm(mx-mn),1e-9);a.add_collection3d(Poly3DCollection(v[f],facecolor='#86a2b8',edgecolor='#40505f',linewidth=.15));a.set_xlim(-.65,.65);a.set_ylim(-.65,.65);a.set_zlim(-.65,.65);a.view_init(24,-42);a.set_box_aspect((1,1,1))
  except: pass
  if i==0:a.set_title(l,fontsize=11)
fig.suptitle('P1 NORMALIZED SHAPE VIEW — NOT TO WORLD SCALE',fontsize=16,fontweight='bold');fig.savefig(O/'renders/P1_NORMALIZED_SHAPE_VIEW_4CASE.png',dpi=240,bbox_inches='tight');plt.close(fig)
