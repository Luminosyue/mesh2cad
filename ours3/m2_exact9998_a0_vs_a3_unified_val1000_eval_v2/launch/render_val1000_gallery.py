#!/usr/bin/env python3
import json, textwrap
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
B=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'
G=B/'gallery'; (G/'cases').mkdir(parents=True,exist_ok=True)
manifest={json.loads(x)['cad_id']:json.loads(x) for x in (B/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()}
def rows(arm): return {p.parent.name:json.loads(p.read_text()) for p in (B/'predictions'/arm).glob('*/row.json')}
a0,a3=rows('a0'),rows('a3'); ids=sorted(set(a0)&set(a3))
def ch(r): return r.get('geometry',{}).get('chamfer_norm')
def mesh(path):
 try:
  m=trimesh.load(str(path),force='mesh'); m=m.dump(concatenate=True) if isinstance(m,trimesh.Scene) else m
  return m if len(m.faces) else None
 except Exception:return None
def gt_path(cid):
 p=Path(manifest[cid]['gt_program_path']).parent/'model.obj'
 return p if p.exists() else None
eligible=[i for i in ids if gt_path(i)]
opf=sorted((i for i in eligible if a3[i].get('step_ok')),key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'],i),reverse=True)[:4]
geom=sorted((i for i in eligible if ch(a0[i]) is not None and ch(a3[i]) is not None),key=lambda i:(ch(a0[i])-ch(a3[i]),i),reverse=True)[:4]
step=sorted((i for i in eligible if not a0[i].get('step_ok') and a3[i].get('step_ok')),key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'],i),reverse=True)[:4]
reg_pool=[i for i in eligible if a0[i].get('step_ok') and not a3[i].get('step_ok')]
reg_pool+=sorted((i for i in eligible if i not in reg_pool),key=lambda i:(a3[i]['op_f1']-a0[i]['op_f1'], -(0 if ch(a0[i]) is None or ch(a3[i]) is None else ch(a3[i])-ch(a0[i])),i))
reg=[]
for i in reg_pool:
 if i not in reg:reg.append(i)
 if len(reg)==4:break
good=sorted((i for i in eligible if a0[i]['op_f1']>=.9 and a3[i]['op_f1']>=.9 and a0[i].get('step_ok') and a3[i].get('step_ok')),key=lambda i:(max(ch(a0[i]) or 9,ch(a3[i]) or 9),i))[:3]
fail=sorted((i for i in eligible if not a0[i].get('step_ok') and not a3[i].get('step_ok')),key=lambda i:(-(manifest[i]['K']),i))[:3]
groups={'Program Rescue':opf,'Geometry Rescue':geom,'STEP Rescue':step,'Regression':reg,'Both Good':good,'Both Fail':fail}
def draw(ax,m,title,color,center,scale):
 ax.set_title(title,fontsize=8);ax.set_axis_off();ax.view_init(24,-55);ax.set_box_aspect((1,1,1));ax.set_xlim(-1.05,1.05);ax.set_ylim(-1.05,1.05);ax.set_zlim(-1.05,1.05)
 if m is None:ax.text2D(.5,.5,'N/A',transform=ax.transAxes,ha='center',va='center',fontsize=13,color='#777');return
 v=(np.asarray(m.vertices)-center)/scale;f=np.asarray(m.faces)
 if len(f)>6000:f=f[np.random.default_rng(42).choice(len(f),6000,replace=False)]
 coll=Poly3DCollection(v[f],linewidths=.06,edgecolors=(.1,.12,.16,.20));coll.set_facecolor(color);ax.add_collection3d(coll)
def info(cid):
 x,y=a0[cid],a3[cid];c0=ch(x);c3=ch(y);fmt=lambda z:'N/A' if z is None else f'{z:.4f}'
 return f"{cid} | {manifest[cid]['source']} | K={manifest[cid]['K']}\nOp-F1 {x['op_f1']:.2f}→{y['op_f1']:.2f} | STEP {int(bool(x.get('step_ok')))}→{int(bool(y.get('step_ok')))} | Ch {fmt(c0)}→{fmt(c3)}"
def render_case(cid,out):
 gt=mesh(gt_path(cid));m0=mesh(B/'predictions/a0'/cid/'pred.stl');m3=mesh(B/'predictions/a3'/cid/'pred.stl')
 center=gt.bounds.mean(0);scale=max(float(np.max(gt.extents))/2,1e-9)
 fig=plt.figure(figsize=(12,3.4),facecolor='white')
 for j,(m,t,c) in enumerate([(gt,'GT','#8fa8bd'),(m0,'A0 Surface-only','#d38b75'),(m3,'A3 Surface + Curves','#63ad83')]):draw(fig.add_subplot(1,3,j+1,projection='3d'),m,t,c,center,scale)
 fig.suptitle(info(cid),fontsize=10,y=.98);fig.tight_layout(rect=(0,0,.99,.93));fig.savefig(out,dpi=150,bbox_inches='tight');plt.close(fig)
for cid in sorted(set(sum(groups.values(),[]))):render_case(cid,G/'cases'/f'{cid}.png')
def contact(selected,out,title):
 fig=plt.figure(figsize=(12,3.0*len(selected)),facecolor='white')
 for r,(grp,cid) in enumerate(selected):
  gt=mesh(gt_path(cid));m0=mesh(B/'predictions/a0'/cid/'pred.stl');m3=mesh(B/'predictions/a3'/cid/'pred.stl');center=gt.bounds.mean(0);scale=max(float(np.max(gt.extents))/2,1e-9)
  for c,(m,name,color) in enumerate([(gt,f'{grp}\nGT','#8fa8bd'),(m0,'A0','#d38b75'),(m3,'A3','#63ad83')]):draw(fig.add_subplot(len(selected),3,r*3+c+1,projection='3d'),m,name,color,center,scale)
  fig.text(.01,1-(r+.93)/len(selected),info(cid),fontsize=7.5)
 fig.suptitle(title,fontsize=14,y=.999);fig.tight_layout(rect=(.03,0,1,.985));fig.savefig(out,dpi=145,bbox_inches='tight');plt.close(fig)
main=[]
for grp,n in [('Program Rescue',3),('Geometry Rescue',3),('STEP Rescue',2),('Regression',2)]:main += [(grp,i) for i in groups[grp][:n]]
full=[]
for grp in groups:full += [(grp,i) for i in groups[grp]]
contact(main,G/'A0_A3_VAL1000_MAIN_EFFECT_GALLERY.png','EXACT9998 VAL1000 — A0 vs A3 Main Effects')
contact(full,G/'A0_A3_VAL1000_FULL_DIAGNOSTIC_GALLERY.png','EXACT9998 VAL1000 — Full Diagnostic Gallery')
(G/'GALLERY_SELECTION.json').write_text(json.dumps({'SELECTION_RULE':'Frozen metric-based automatic selection; no manual cherry-picking','groups':groups,'main':main,'full':full},indent=2)+'\n')
print(json.dumps({'main_n':len(main),'full_n':len(full),'groups':{k:len(v) for k,v in groups.items()}},indent=2))
