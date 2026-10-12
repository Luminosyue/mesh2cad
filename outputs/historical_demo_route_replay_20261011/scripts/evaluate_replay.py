import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import sys,json,hashlib
import numpy as np,trimesh,cadquery as cq
B=Path('/data/home/cuiyuehan/project/mesh2cad/outputs')
O=B/'historical_demo_route_replay_20261011'
sys.path.insert(0,str(B/'part_cad_fitting_v2_native/scripts'))
from metric_runtime import evaluate
sys.path.insert(0,str(B/'cad_render_v4/scripts'))
from cad_render_utils import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(O/'manifest.json');items=[]
for r in manifest['cases']:
 old=B/'targeted_cad_structure_diagnosis_v1/cases'/r['object']/r['part']/'final/cad.step'
 if not old.exists():old=Path(r['baseline_dir'])/'cad/cad.step'
 items.append(dict(r,case=r['object'],old_step=str(old),group='current_P3_input'))
for r in read(O/'historical_controls.json'):
 items.append(dict(r,old_step=str(Path(r['historical_cad_dir'])/(r['part']+'.step')),seed=20261011,group='historical_XPart_positive_control'))
cache={r['case_id']:r for r in read(O/'comparison.json')} if (O/'comparison.json').exists() else {}
results=[];(O/'visualizations').mkdir(exist_ok=True)
for row in items:
 case,pid=row['case'],row['part'];d=O/case/'xpart_parts_cadquery_features'/pid;src=trimesh.load(row['source'],force='mesh',process=True)
 assert sha(Path(row['source']))==row['source_sha256']
 new=d/(pid+'.step');old=Path(row['old_step'])
 cached=cache.get(case+'/'+pid)
 if cached and cached.get('source_sha256')==row['source_sha256'] and cached.get('before_step_sha256')==sha(old) and cached.get('after_step_sha256')==sha(new):
  results.append(cached);print('VERIFIED_CACHED_METRICS',case,pid,flush=True);continue
 if not new.exists():
  results.append({'case_id':case+'/'+pid,'group':row['group'],'status':'NO_VALID_CAD'});continue
 scale=1/float(max(src.extents)) if row['group'].startswith('historical') else 1.
 center=src.bounds.mean(0) if scale!=1 else np.zeros(3)
 def norm(mesh):
  m=mesh.copy();m.apply_translation(-center);m.apply_scale(scale);return m
 mets=[];meshes=[]
 for step in [old,new]:
  shape=cq.importers.importStep(str(step)).val();assert shape.isValid() and len(shape.Solids())>0
  v,f=shape.tessellate(.00025/scale,.1);mesh=trimesh.Trimesh([x.toTuple() for x in v],f,process=True);meshes.append(mesh)
  mets.append(evaluate(norm(src),norm(mesh),row['seed']))
 meshes[1].export(d/'reloaded_eval.ply')
 result={'case_id':case+'/'+pid,'group':row['group'],'before':mets[0],'after':mets[1],'historical_report':read(d/'job_status.json'),'source_sha256':row['source_sha256'],'before_step_sha256':sha(old),'after_step_sha256':sha(new),'normalization_scale':scale,'normalization_center':center.tolist(),'candidate_attempt_n':len(read(d/'attempts.json'))}
 results.append(result);(O/'comparison.json').write_text(json.dumps(results,indent=2))
 print(json.dumps({'case':result['case_id'],'before_iou':mets[0]['iou'],'after_iou':mets[1]['iou'],'before_ncd':mets[0]['normalized_chamfer'],'after_ncd':mets[1]['normalized_chamfer'],'strict':mets[1]['strict_pass']}),flush=True)
 if os.environ.get('EVAL_ONLY')=='1':continue
 cen=src.bounds.mean(0);span=float(np.max(np.ptp(np.vstack([x.bounding_box.vertices for x in [src]+meshes]),axis=0)))
 fig=plt.figure(figsize=(18,5),facecolor='#f7f9fc')
 labels=['Source mesh','Before / stored CAD','Historical generator replay','Source / replay overlay']
 panels=[[(src,'#3385cc',1)],[(meshes[0],'#db9d40',1)],[(meshes[1],'#db9d40',1)],[(src,'#3385cc',.3),(meshes[1],'#dd632f',.45)]]
 for j,panel in enumerate(panels):
  ax=fig.add_subplot(1,4,j+1,projection='3d',facecolor='#f7f9fc')
  for mesh,color,alpha in panel:
   coll=Poly3DCollection(mesh.triangles,facecolors=color,edgecolors='none',linewidths=0,alpha=alpha,rasterized=True);ax.add_collection3d(coll)
  ax.set(xlim=(cen[0]-span*.55,cen[0]+span*.55),ylim=(cen[1]-span*.55,cen[1]+span*.55),zlim=(cen[2]-span*.55,cen[2]+span*.55));ax.set_box_aspect((1,1,1));ax.view_init(22,35);ax.set_axis_off()
  title=labels[j]
  if j in [1,2]:title+='\nIoU %.4f | NCD %.4f'%(mets[j-1]['iou'],mets[j-1]['normalized_chamfer'])
  ax.set_title(title,fontsize=11)
 fig.suptitle(case+'/'+pid+' | same camera, scale and coordinates',fontsize=13);fig.tight_layout();fig.savefig(O/'visualizations'/f'{case}_{pid}.png',dpi=140);plt.close(fig)
for r in manifest['historical_scripts']:assert sha(Path(r['path']))==r['sha256']
page='<meta charset="utf-8"><title>Historical CAD replay</title><style>body{font:18px system-ui;margin:30px;background:#f7f9fc}img{width:100%}section{margin:40px 0}</style><h1>旧 CAD 生成流程复现</h1><p>左起：原 mesh、已有 CAD、旧生成器重新生成、原 mesh 与新 CAD 叠加。所有模型按同一相机、尺度、坐标显示。</p><p>两组分开统计：当前 P3 输入 3 件；历史 X-Part 成功案例 3 件（正对照，不能用于估计泛化成功率）。旧输入复用已有 X-Part 文件，没有重新运行补全模型。</p>'
for r in results:
 if 'after' not in r:continue
 page+='<section><h2>'+r['case_id']+'</h2><p>'+r['group']+' | IoU %.3f → %.3f | NCD %.4f → %.4f | Strict: %s</p>'%(r['before']['iou'],r['after']['iou'],r['before']['normalized_chamfer'],r['after']['normalized_chamfer'],r['after']['strict_pass'])+'<img src="'+r['case_id'].replace('/','_')+'.png"></section>'
(O/'visualizations/index.html').write_text(page,encoding='utf-8')
(O/'comparison.json').write_text(json.dumps(results,indent=2))
print('VERIFIED_HISTORICAL_READ_ONLY',flush=True)
