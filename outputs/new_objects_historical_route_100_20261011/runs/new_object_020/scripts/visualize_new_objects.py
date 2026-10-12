from pathlib import Path
import json,html
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_historical_route_100_20261011/runs/new_object_020')
objects=json.loads((O/'manifests/objects_frozen.json').read_text());summary=json.loads((O/'summary.json').read_text()) if (O/'summary.json').exists() else None
palette=plt.get_cmap('tab20');light=np.array([.3,-.5,.8]);light/=np.linalg.norm(light)
def display_mesh(p):
 m=trimesh.load(p,force='mesh',process=True)
 m=m.simplify_quadric_decimation(face_count=5000) if len(m.faces)>5000 else m
 m.apply_transform(np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]]))
 return m
cards=[]
for obj in objects:
 oid=obj['object_id'];d=O/'objects'/oid;source=display_mesh(obj['canonical_path']);parts=json.loads((d/'p3/parts_manifest.json').read_text())['parts']
 segmented=[];completed=[];cads=[]
 for i,p in enumerate(parts):
  color=palette(i%20)[:3];segmented.append((display_mesh(p['part_mesh_path']),color));num=int(p['part_id'].split('_')[-1]);upper=f'PART_{num:03d}'
  xp=list((d/'xpart_parts'/upper).glob('complete*.obj'))
  if xp:completed.append((display_mesh(xp[0]),color))
  fit=d/'xpart_parts_cadquery_features'/upper;cad=fit/'cad_evaluation_mesh.ply'
  if not cad.exists():cad=fit/(upper+'_preview.stl')
  if cad.exists():cads.append((display_mesh(cad),color))
 panels=[('Source object',[(source,to_rgb('#3d82ba'))]),('New P3 parts (%d)'%len(segmented),segmented),('New XPart parts (%d)'%len(completed),completed),('New CAD parts (%d)'%len(cads),cads)]
 allmesh=[m for _,group in panels for m,c in group];center=source.bounds.mean(0);span=2*float(np.max(np.abs(np.vstack([m.bounds for m in allmesh])-center)))
 fig=plt.figure(figsize=(18,5.5),facecolor='#f7f9fc')
 for j,(label,group) in enumerate(panels):
  ax=fig.add_subplot(1,4,j+1,projection='3d',facecolor='#f7f9fc')
  for mesh,color in group:
   shade=.55+.45*np.clip(mesh.face_normals@light,0,1);colors=np.array(color)[None,:]*shade[:,None]
   ax.add_collection3d(Poly3DCollection(mesh.triangles,facecolors=colors,edgecolors='none',rasterized=True))
  ax.set(xlim=(center[0]-span*.55,center[0]+span*.55),ylim=(center[1]-span*.55,center[1]+span*.55),zlim=(center[2]-span*.55,center[2]+span*.55));ax.set_box_aspect((1,1,1));ax.view_init(22,35);ax.set_axis_off();ax.set_title(label,fontsize=12)
  if not group:ax.text2D(.3,.5,'Pending',transform=ax.transAxes)
 fig.suptitle(obj['name'],fontsize=13,y=.97);fig.text(.5,.025,'Same coordinates, camera and scale. Display-only decimation; CAD panel contains all valid candidates, including rejects.',ha='center',fontsize=10);fig.subplots_adjust(left=.01,right=.99,bottom=.08,top=.8,wspace=.02)
 name=oid+'.png';fig.savefig(O/'visualizations'/name,dpi=130);plt.close(fig);cards.append((obj,name,len(segmented),len(completed),len(cads)));print('RENDERED',oid,flush=True)
page='''<!doctype html><meta charset="utf-8"><title>全新物体 · Mesh to CAD</title><style>body{max-width:1700px;margin:32px auto;padding:0 20px;font:17px system-ui;background:#f5f7fa;color:#172536}section{background:white;border-radius:14px;padding:20px;margin:24px 0}img{width:100%}table{border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ddd}a{color:#215aa0}</style><h1>全新物体：旧流程的新数据试跑</h1><p>本物体源文件哈希已排除旧两批及首批 3 个物体；本轮重新运行 P3、X-Part 和 CAD 拟合。</p><p>每行从左到右：原始物体 → P3 拆件 → X-Part 补全 → 新生成的 CAD。最后一栏包含所有有效候选，不代表全部严格合格。</p>'''
if summary:
 page+='<p><b>零件总数 %d；有效 CAD %d；匹配补全 mesh 的严格合格数 %d；匹配原始 P3 mesh 的严格合格数 %d。</b></p>'%(summary['p3_part_n'],summary['cad_valid_n'],summary['strict_completed_n'],summary['strict_original_n'])
 page+='<p>补全可能改变几何，两个合格口径分开报告。IoU 是原协议的近似体素占据指标，不是精确实体布尔体积。</p>'
else:page+='<p><b>运行中：P3 已完成，X-Part 权重恢复/补全及 CAD 拟合尚未全部完成。空栏表示待运行。</b></p>'
for obj,name,ps,xs,cs in cards:
 page+='<section><h2>'+html.escape(obj['name'])+'</h2><p>P3 %d 件 · X-Part %d 件 · CAD %d 件</p>'%(ps,xs,cs)+'<img src="'+name+'"></section>'
if summary:
 page+='<section><h2>逐零件检查</h2><p>两组数值分别以原始 P3 mesh、X-Part 补全 mesh 为参照。CAD 有效仅表示 STEP 可以重新导入且包含有效实体。</p><table><tr><th>物体 / 零件</th><th>CAD 方法</th><th>原始 IoU</th><th>补全 IoU</th><th>判定</th></tr>'
 for r in json.loads((O/'part_results.json').read_text()):
  orig=r.get('cad_vs_original',{}).get('iou');comp=r.get('cad_vs_completed',{}).get('iou')
  page+='<tr><td>'+html.escape(r['object_id']+' / '+r['part_id'])+'</td><td>'+html.escape(r.get('method','—'))+'</td><td>'+('%.4f'%orig if orig is not None else '—')+'</td><td>'+('%.4f'%comp if comp is not None else '—')+'</td><td>'+html.escape(r['status'])+'</td></tr>'
 page+='</table><p><a href="../summary.json">完整汇总 JSON</a> · <a href="../part_results.json">逐零件指标 JSON</a></p></section>'
(O/'visualizations/index.html').write_text(page,encoding='utf-8')
