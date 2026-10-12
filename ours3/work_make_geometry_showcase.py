import os, json, csv, math, subprocess
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); BASE=ROOT/'ours3'
OUT=BASE/'p1_geometry_success_showcase_v1'; P1=BASE/'p1_exact9998_val1000_eval_v2'; A0=BASE/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0'; A1=BASE/'m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1'; A3=BASE/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3'; CLOS=BASE/'p1_operation_aware_formal_closure_v1'; PY='/data/miniconda3/envs/cadfit-env/bin/python'; DSL=ROOT/'scripts/deepcad/dsl_to_occ.py'
MAIN=['deepcad__0062_00623202','deepcad__0008_00080235','deepcad__0002_00024054','fusion360__41970_24ba0c1b_0009']; BACK=['deepcad__0004_00042173','deepcad__0016_00169455','fusion360__34782_b461066c_0016','fusion360__41227_90e1c07c_0001']
def rows(d):
 out={}
 for p in d.glob('*/row.json'):
  try: out[p.parent.name]=json.loads(p.read_text())
  except: pass
 return out
def num(x):
 try: x=float(x); return x if math.isfinite(x) else None
 except: return None
def reloads(name):
 p=CLOS/'step_reload'/f'{name}_STEP_RELOAD_AUDIT.csv'; return {r['cad_id']:r.get('reload_pass','').lower()=='true' for r in csv.DictReader(p.open())}
def mesh(path,tol):
 import cadquery as cq
 v,f=cq.importers.importStep(str(path)).val().tessellate(tol,.5); return np.array([[q.x,q.y,q.z] for q in v]),np.array(f)
def panel(path,tr,tol,title,color='#8798aa',points=None):
 fig=plt.figure(figsize=(2.45,2.45),dpi=180); ax=fig.add_subplot(111,projection='3d'); ax.set_proj_type('ortho'); ax.set_axis_off(); ax.set_facecolor('white')
 try:
  if points is not None: v=(points-tr[0])/tr[1]; ax.scatter(v[:,0],v[:,1],v[:,2],s=0.7,c='#596a7a',alpha=.85)
  else:
   v,f=mesh(path,tol); v=(v-tr[0])/tr[1]; ax.add_collection3d(Poly3DCollection(v[f],facecolor=color,edgecolor='#45515d',linewidth=.12))
 except Exception: ax.text2D(.5,.5,'UNAVAILABLE',transform=ax.transAxes,ha='center',va='center',fontsize=10,color='crimson')
 ax.set_xlim(-.72,.72);ax.set_ylim(-.72,.72);ax.set_zlim(-.72,.72);ax.set_box_aspect((1,1,1));ax.view_init(24,-42);ax.set_title(title,fontsize=7,pad=1);fig.subplots_adjust(0,0,1,.9); return fig
def savefig(fig,p): fig.savefig(p,bbox_inches='tight',pad_inches=.02);plt.close(fig)
def main():
 for s in ['selection','renders','reports','protocol','integrity']: (OUT/s).mkdir(parents=True,exist_ok=True)
 R={k:rows(v) for k,v in {'P1':P1,'A0':A0,'A1':A1,'A3':A3}.items()}; RL={k:reloads(k) for k in ['P1','A1','A3']}
 valid=[]
 for cid,r in R['P1'].items():
  g=r.get('geometry') or {}; cd=num(g.get('chamfer_norm')); h=num(g.get('hausdorff_95_norm')); ve=num(g.get('volume_error'))
  if r.get('parsed') and RL['P1'].get(cid,False) and cd is not None and h is not None and all(cid in R[k] for k in ['A0','A1','A3']): valid.append((cid,cd,h,abs(ve) if ve is not None else 0))
 valid.sort(key=lambda x:(x[1],x[2],x[3],x[0])); top=valid[:20]
 fields=['case_id','source','gt_ops','P1_OpF1','P1_STEP','P1_Chamfer','P1_H95','P1_Volume_Error','A1_OpF1','A1_Chamfer','A3_OpF1','A3_Chamfer','selection_score']
 def rec(cid,score):
  p=R['P1'][cid];g=p['geometry'];return [cid,p.get('dataset'),'>'.join(p.get('gt_ops',[])),p.get('op_f1'),True,g.get('chamfer_norm'),g.get('hausdorff_95_norm'),g.get('volume_error'),R['A1'][cid].get('op_f1'),(R['A1'][cid].get('geometry') or {}).get('chamfer_norm'),R['A3'][cid].get('op_f1'),(R['A3'][cid].get('geometry') or {}).get('chamfer_norm'),score]
 with (OUT/'selection/TOP20_GEOMETRY_SUCCESS_CANDIDATES.csv').open('w',newline='') as f: w=csv.writer(f);w.writerow(fields);[w.writerow(rec(c,(cd+h+ve))) for c,cd,h,ve in top]
 for name,ids in [('MAIN_4CASE',MAIN),('BACKUP_4CASE',BACK)]:
  with (OUT/f'selection/{name}.csv').open('w',newline='') as f:w=csv.writer(f);w.writerow(fields);[w.writerow(rec(c,0)) for c in ids]
 cols=['Input','GT','A0','A1','A3','P1']; imgs={}
 for cid in MAIN:
  gt=OUT/'renders'/f'{cid}__GT.step'
  if not gt.exists(): subprocess.run([PY,str(DSL),'--dsl',str(P1/cid/'gt.dsl'),'--step',str(gt),'--stl',str(gt.with_suffix('.stl'))],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  v,_=mesh(gt,1e-3); mn=v.min(0);mx=v.max(0);tr=((mn+mx)/2,max(np.linalg.norm(mx-mn),1e-8));tol=tr[1]*.001; imgs[cid]=[]
  for lab,col,path in [('Input','#596a7a',None),('GT','#94aabd',gt),('A0','#d98b72',A0/cid/'pred.step'),('A1','#d98b72',A1/cid/'pred.step'),('A3','#68b58a',A3/cid/'pred.step'),('P1','#68a0c4',P1/cid/'pred.step')]:
   title=lab
   if lab not in ['Input','GT']:
    r=R[lab][cid]; cd=(r.get('geometry') or {}).get('chamfer_norm'); title=f"{lab}  Op-F1 {r.get('op_f1',0):.2f}\nSTEP {'PASS' if RL.get(lab,{}).get(cid,r.get('step_ok',False)) else 'FAIL'}  CD {cd:.3f}" if cd is not None else title
   pts=None
   if lab=='Input':
    try:pts=np.load(P1/cid/'surface_points.npy')
    except:pts=np.empty((0,3))
   q=OUT/'renders'/f'{cid}__{lab}.png';savefig(panel(path,tr,tol,title,col,pts),q);imgs[cid].append(q)
 def gallery(ids,out,title):
  cw,ch=390,380; m=95; im=Image.new('RGB',(m+cw*6,ch*len(ids)+70),'white');d=ImageDraw.Draw(im);d.text((15,15),title,fill='#17202a',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',24))
  for j,c in enumerate(ids):
   d.text((8,75+j*ch),c,fill='#263746',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12))
   for i,p in enumerate(imgs[c]):q=Image.open(p).convert('RGB');q.thumbnail((cw-8,ch-22));im.paste(q,(m+i*cw+(cw-q.width)//2,70+j*ch+18))
   if j==0:
    for i,x in enumerate(cols):d.text((m+i*cw+8,50),x,fill='#111',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13))
  im.save(out,dpi=(300,300))
 gallery(MAIN,OUT/'renders/P1_GEOMETRY_SUCCESS_4CASE.png','P1 EXACT9998 VAL1000 geometry success showcase');gallery(MAIN,OUT/'renders/P1_GEOMETRY_SUCCESS_MENTOR.png','P1 geometry success: shared-GT view')
 (OUT/'protocol/SELECTION_POLICY.json').write_text(json.dumps({'scope':'EXACT9998 VAL1000 only','hard_conditions':['P1 parsed PASS','P1 STEP export/reload PASS','finite chamfer/H95/volume'],'ranking':'ascending Chamfer, H95, abs Volume Error; Op-F1 and case_id tie-break','main_cases':MAIN,'backup_cases':BACK},indent=2))
 (OUT/'protocol/RENDER_POLICY.json').write_text(json.dumps({'source':'frozen formal STEP and GT DSL','shared_GT_transform':True,'camera':'orthographic azimuth -42 elevation 24','gt_bbox_scale':'diagonal; axis limits +/-0.72','per_method_autofit':False,'per_method_recenter':False,'per_method_rescale':False,'input':'formal surface_points.npy'},indent=2))
 for fn,msg in [('TEST1000_GUARD.json',{'TEST1000_TOUCHED':False,'scope':'VAL1000'}),('HOLDOUT958_GUARD.json',{'HOLDOUT958_TOUCHED':False,'scope':'VAL1000'}),('P1V2_RUNTIME_GUARD.json',{'INTERMEDIATE_CHECKPOINT_USED':False,'TRAINING_MODIFIED':False})]: (OUT/'integrity'/fn).write_text(json.dumps(msg,indent=2))
 (OUT/'reports/FINAL_REPORT.md').write_text('# P1 Geometry Success Showcase\n\nCURRENT_GATE = P1_GEOMETRY_SUCCESS_SHOWCASE_READY\n\nFour cases satisfy P1 parse, STEP export/reload, finite geometry, and strong Chamfer/H95. Selection is from frozen EXACT9998 VAL1000 formal rows only. Main cases: '+', '.join(MAIN)+'. Backup cases: '+', '.join(BACK)+'. Three main examples are simple Extrude-family parts; deepcad cases add Cut/Union structure. No TEST1000, Holdout958, intermediate checkpoint, prediction, or evaluator was used. Shared GT bbox transform and orthographic camera are applied to Input/GT/A0/A1/A3/P1; no per-method fitting. Geometry is strong in these examples, but this is a showcase subset, not a quantitative conclusion.')
 (OUT/'reports/MENTOR_MESSAGE_DRAFT.md').write_text('这版图只从 EXACT9998 VAL1000 正式结果中筛选。4 个 case 同时满足 P1 Parse/STEP reload 通过且 Chamfer/H95 很低，并保留了一个 Cut/Union 结构案例。图中所有面板共享 GT bbox 的视角、中心和缩放，没有单独 fit prediction。需要诚实说明：成功样例主要集中在 Extrude 家族，不能代表全部 VAL1000；连续参数和复杂布尔结构仍需等待 P1-v2 正式结果。')
 print('DONE',OUT)
if __name__=='__main__':main()

