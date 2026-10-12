import json
from pathlib import Path
import numpy as np,trimesh
from scipy.spatial import cKDTree
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V=O/'case05_residual_part003_recovery_v3';V2=O/'best_multipart_full_recovery_v2';SRC=O/'batch_real_mesh2cad_v1/cases/CASE_05'
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
p=load(V2/'metrics/part_results.json');old=[x for x in p if x['quality']!='TRUE_FAILURE'];cfg=load(V/'metrics/decomposition_search.json')['selected'];new=[x for x in cfg['subparts'] if x['quality']!='FAIL'];meshes=[]
for x in old:meshes.append((x['part_id'],x['quality'],trimesh.load(V2/'parts'/x['part_id']/'accepted/cad_mesh.obj',force='mesh',process=False)))
for x in new:meshes.append(('CADPART_003_SUBPART_00',x['quality'],trimesh.load(Path(x['directory'])/'accepted/cad_mesh.obj',force='mesh',process=False)))
scene=trimesh.Scene()
for n,q,m in meshes:scene.add_geometry(m,node_name=f'{n}_{q}',geom_name=n)
scene.export(V/'viewer/CASE05_full_cad_v3.glb');src=trimesh.load(SRC/'source/source.obj',force='mesh',process=False);cad=trimesh.util.concatenate([m for _,_,m in meshes]);np.random.seed(42);sp=src.sample(100000);cp=cad.sample(100000);diag=np.linalg.norm(src.bounds[1]-src.bounds[0]);d1=cKDTree(cp).query(sp)[0]/diag;d2=cKDTree(sp).query(cp)[0]/diag;both=np.r_[d1,d2];w={'WHOLE_OBJECT_CHAMFER':float((d1.mean()+d2.mean())/2),'WHOLE_OBJECT_P95':float(np.percentile(both,95)),'WHOLE_OBJECT_COVERAGE02':float(np.mean(d1<=.02)),'ICP_USED':False,'sample_count':100000,'frame_correction':'fresh_source_frame meshes consumed without duplicate transform'};dump(V/'metrics/whole_object_qa.json',w)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
def panel(ax,m,title,color):p=np.asarray(m.vertices);p=p[::max(1,len(p)//16000)];ax.scatter(p[:,0],p[:,2],s=.15,c=color,alpha=.7);ax.set_title(title);ax.axis('off');ax.set_aspect('equal')
fig,axs=plt.subplots(1,2,figsize=(14,7));panel(axs[0],src,'Original High Mesh','#777');panel(axs[1],cad,'CAD/BRep Assembly v3','#35a67a');fig.tight_layout();fig.savefig(V/'artifacts/CASE05_full_cad_v3_vs_source.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,7));colors={'Q1':'#18a558','Q2':'#f2a900','S1':'#744fc6'}
for n,q,m in meshes:panel(ax,m,'',colors[q]);failed=trimesh.load(Path(cfg['subparts'][1]['directory'])/'source.obj',force='mesh',process=False);panel(ax,failed,'','#d62728');ax.set_title('Q1 green / S1 purple / FAILED red');fig.savefig(V/'artifacts/CASE05_final_coverage_map.png',dpi=180);plt.close(fig)
s=load(V/'metrics/summary.json');s.update({k:w[k] for k in ['WHOLE_OBJECT_CHAMFER','WHOLE_OBJECT_P95','WHOLE_OBJECT_COVERAGE02']});dump(V/'metrics/summary.json',s);(V/'artifacts/case05_residual_part003_recovery_v3_report.md').write_text('# CASE05_RESIDUAL_PART003_RECOVERY_V3\n\n```json\n'+json.dumps(s,indent=2)+'\n```\n');print(json.dumps(w,indent=2))
