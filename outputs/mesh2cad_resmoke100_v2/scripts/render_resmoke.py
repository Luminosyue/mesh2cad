import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.collections import PolyCollection
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');OLD=O/'mesh2cad_data_factory_v1_smoke100';D=O/'mesh2cad_reconstruction_diagnosis_v1';R=O/'mesh2cad_resmoke100_v2'
selected=json.loads((D/'visualizations/selection.json').read_text())['cases']
old={r['case_id']:r for r in [json.loads(l) for l in (OLD/'manifests/cases.jsonl').read_text().splitlines()]}
def draw(ax,m,color,alpha=1):
 ax.add_collection3d(Poly3DCollection(m.triangles,facecolor=color,edgecolor='#334155' if len(m.faces)<200 else 'none',linewidth=.2,alpha=alpha))
for cid in selected:
 a=old[cid];b=json.loads((R/'cases'/cid/'manifest.json').read_text());s=trimesh.load(R/'cases'/cid/'normalized/normalized_mesh.ply',force='mesh',process=True)
 v1=trimesh.load(a['cad_mesh_path'],force='mesh',process=True) if a.get('cad_mesh_path') else None
 v2=trimesh.load(b['cad_mesh_path'],force='mesh',process=True) if b.get('cad_mesh_path') else None
 fig=plt.figure(figsize=(15,4));axes=[fig.add_subplot(1,4,j+1,projection='3d') for j in range(4)]
 draw(axes[0],s,'#60a5fa')
 if v1 is not None:draw(axes[1],v1,'#fb923c')
 else:axes[1].text(0,0,0,'NO V1 CAD')
 if v2 is not None:draw(axes[2],v2,'#34d399');draw(axes[3],s,'#60a5fa',.5);draw(axes[3],v2,'#34d399',.4)
 else:axes[2].text(0,0,0,'NO V2 CAD')
 bounds=np.concatenate([m.bounds for m in [s,v1,v2] if m is not None]);c=(bounds.min(0)+bounds.max(0))/2;rad=max(np.ptp(bounds,axis=0))*.58
 for ax,title in zip(axes,['Source','V1 CAD','V2 CAD','Source / V2 overlay']):
  ax.set(xlim=(c[0]-rad,c[0]+rad),ylim=(c[1]-rad,c[1]+rad),zlim=(c[2]-rad,c[2]+rad),title=title);ax.view_init(22,-55);ax.set_box_aspect((1,1,1));ax.set_axis_off()
 am=a['geometry_metrics'];bm=b.get('metrics',{});label=f'{cid} | V1 {am.get("iou",float("nan")):.3f} -> V2 {bm.get("iou",float("nan")):.3f} IoU | {b["status"]}'
 if b.get('thickness_assumed'):label+=' | assumed thin-solid thickness'
 fig.suptitle(label,fontsize=11);fig.tight_layout();fig.savefig(R/'visualizations'/(cid+'.png'),dpi=130);plt.close(fig)
(R/'visualizations/index.html').write_text('<meta charset="utf-8"><h1>Same-source V1 / V2 comparison</h1><p>Identical camera, frame and scale within each row. Assumed thickness is labeled, not original design truth.</p>'+''.join(f'<h2>{c}</h2><img style="width:100%" src="{c}.png">' for c in selected))
unsupported=[r for r in old.values() if r['filter_decision']=='REJECT'];fig,axes=plt.subplots(1,3,figsize=(12,4))
for ax,r in zip(axes,unsupported):
 m=trimesh.load(OLD/'cases'/r['case_id']/'normalized/normalized_mesh.ply',force='mesh');c=m.vertices.mean(0);_,_,vh=np.linalg.svd(m.vertices-c,full_matrices=False);p=(m.vertices-c)@vh[:2].T
 ax.add_collection(PolyCollection(p[m.faces],facecolor='#60a5fa',edgecolor='#334155',linewidth=.5));ax.autoscale_view();ax.set_aspect('equal');ax.set_title(r['case_id']+' | source plane view');ax.set_xlabel('in-plane axis 1');ax.set_ylabel('in-plane axis 2')
fig.suptitle('Unsupported V1 cases: planar profiles, thickness not observed');fig.tight_layout();fig.savefig(D/'visualizations/unsupported_plane_views.png',dpi=140);plt.close(fig)
print(json.dumps({'v2_comparisons':len(selected),'unsupported_profile_views':3}))
