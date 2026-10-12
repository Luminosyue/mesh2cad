#!/usr/bin/env python3
"""Postprocess already-saved VIS16 prediction text. Does not call any model."""
from __future__ import annotations
import ast,importlib.util,json,sys
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from transformers import AutoTokenizer
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');RUN=ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1';OUT=RUN/'epoch20_result_inspection';MAN=ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
OPS=('Box','Cylinder','ExtrudePolygon','Extrude','Revolve','Union','Cut','Intersect','Circle','Rectangle','Polygon')
def module():
 p=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py';s=importlib.util.spec_from_file_location('vis_cad_dsl',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def parse(s):
 try:ast.parse(s);return True
 except:return False
def f1(a,b):
 aa,bb=Counter(__import__('re').findall(r'\b('+'|'.join(OPS)+r')\s*\(',a)),Counter(__import__('re').findall(r'\b('+'|'.join(OPS)+r')\s*\(',b));tp=sum((aa&bb).values())
 if not aa and not bb:return 1.
 if not tp:return 0.
 p,r=tp/max(sum(bb.values()),1),tp/max(sum(aa.values()),1);return 2*p*r/(p+r)
def execute(code,step,stl):
 o={'parse_pass':False,'exec_pass':False,'step_write_pass':False,'step_reload_pass':False,'failure_stage':None,'reason':None}
 try:m=module();clean=m.extract_dsl_code(code);m.parse_dsl(clean);o['parse_pass']=True
 except Exception as e:o.update(failure_stage='PARSE',reason=f'{type(e).__name__}: {e}');return o
 try:m.execute_dsl(clean,step,stl);o['exec_pass']=True;o['step_write_pass']=step.exists()
 except Exception as e:o.update(failure_stage='EXEC',reason=f'{type(e).__name__}: {e}');return o
 try:
  import cadquery as cq;cq.importers.importStep(str(step));o['step_reload_pass']=True
 except Exception as e:o.update(failure_stage='STEP_RELOAD',reason=f'{type(e).__name__}: {e}')
 return o
def mesh(path):
 m=trimesh.load(str(path),force='mesh');return m.dump(concatenate=True) if isinstance(m,trimesh.Scene) else m
def metric(gt,pr):
 a=mesh(gt);b=mesh(pr);x,_=trimesh.sample.sample_surface(a,8192,seed=42);y,_=trimesh.sample.sample_surface(b,8192,seed=43);da=cKDTree(y).query(x)[0];db=cKDTree(x).query(y)[0];d=np.linalg.norm(a.bounds[1]-a.bounds[0]);return {'chamfer_norm':float((da.mean()+db.mean())/2/d),'hausdorff95_norm':float(max(np.percentile(da,95),np.percentile(db,95))/d),'bbox_center_error_norm':float(np.linalg.norm(a.bounds.mean(0)-b.bounds.mean(0))/d),'bbox_extent_error_norm':float(np.linalg.norm(a.extents-b.extents)/d)}
def draw(ax,step,bounds,title,c='tab:blue',over=None):
 if not step or not Path(step).exists():ax.text2D(.5,.5,title+'\nNO STEP',ha='center',transform=ax.transAxes);ax.axis('off');return
 m=mesh(step);p,_=trimesh.sample.sample_surface(m,3000,seed=42);ax.scatter(p[:,0],p[:,1],p[:,2],s=.25,c=c)
 if over and Path(over).exists():q,_=trimesh.sample.sample_surface(mesh(over),3000,seed=43);ax.scatter(q[:,0],q[:,1],q[:,2],s=.2,c='tab:red',alpha=.6)
 lo,hi=bounds;pad=.05*np.max(hi-lo);ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),zlim=(lo[2]-pad,hi[2]+pad),title=title);ax.view_init(25,-55);ax.axis('off')
def main():
 tok=AutoTokenizer.from_pretrained(RUN/'checkpoint_epoch_20',local_files_only=True,use_fast=False);recs={r['cad_id']:r for r in json.loads(MAN.read_text())['records']};sel=json.loads((OUT/'M2_VIS16_MANIFEST.json').read_text())['records'];steps=OUT/'steps';cases=[]
 for s in sel:
  cid=s['cad_id'];r=recs[cid];d=steps/cid;d.mkdir(exist_ok=True);gt=Path(r['target_dsl']).read_text();g=execute(gt,d/'gt.step',d/'gt.stl');item={'cad_id':cid,'selection_bucket':s['selection_bucket'],'difficulty_bin':s['difficulty_bin'],'gt_dsl':gt,'gt_token_count':len(tok.encode(gt,add_special_tokens=False)),'gt_exec':g,'steps':{'gt':str(d/'gt.step') if g['step_reload_pass'] else None},'meshes':{'gt':str(d/'gt.stl') if g['step_reload_pass'] else None},'epochs':{}}
  for ep in (18,20):
   text=(OUT/'predictions'/f'epoch{ep}'/f'{cid}.txt').read_text();e=execute(text,d/f'epoch{ep}_pred.step',d/f'epoch{ep}_pred.stl');q={'pred_dsl':text,'decoded_text_token_count':len(tok.encode(text,add_special_tokens=False)),'generated_token_count_exact':'not persisted before visualizer crash','eos':'e18 all true from generation log' if ep==18 else 'e20 true except 0005_00058074 and 0058_00588469 from generation log','hit_cap':'known true for the two e20 no-EOS cases; otherwise not persisted','parse_pass':parse(text),'exec':e,'op_f1':f1(gt,text),'exact_match':text.strip()==gt.strip()}
   if e['step_reload_pass'] and g['step_reload_pass']:q['geometry']=metric(d/'gt.stl',d/f'epoch{ep}_pred.stl')
   item['epochs'][str(ep)]=q;item['steps'][f'epoch{ep}']=str(d/f'epoch{ep}_pred.step') if e['step_reload_pass'] else None;item['meshes'][f'epoch{ep}']=str(d/f'epoch{ep}_pred.stl') if e['step_reload_pass'] else None
  cases.append(item)
 (OUT/'M2_VIS16_PREDICTIONS.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in cases));(OUT/'M2_VIS16_METRICS.jsonl').write_text(''.join(json.dumps({'cad_id':x['cad_id'],'epoch18':x['epochs']['18'].get('geometry'),'epoch20':x['epochs']['20'].get('geometry'),'gt_step':x['gt_exec']['step_reload_pass'],'e18_step':x['epochs']['18']['exec']['step_reload_pass'],'e20_step':x['epochs']['20']['exec']['step_reload_pass']})+'\n' for x in cases))
 txt=[]
 for x in cases:txt.extend(['='*72,'CAD_ID = '+x['cad_id'],'GT:\n'+x['gt_dsl'],'EPOCH18:\n'+x['epochs']['18']['pred_dsl'],'EPOCH20:\n'+x['epochs']['20']['pred_dsl'],f"GT token count={x['gt_token_count']} E18 decoded={x['epochs']['18']['decoded_text_token_count']} E20 decoded={x['epochs']['20']['decoded_text_token_count']}",f"E18 EOS={x['epochs']['18']['eos']} E20 EOS={x['epochs']['20']['eos']}"])
 (OUT/'M2_VIS16_DSL_COMPARISON.txt').write_text('\n\n'.join(txt))
 figdir=OUT/'figures';figdir.mkdir(exist_ok=True);valid=[x for x in cases if x['gt_exec']['step_reload_pass'] and (x['epochs']['18']['exec']['step_reload_pass'] or x['epochs']['20']['exec']['step_reload_pass'])]
 for st in range(0,len(valid),8):
  b=valid[st:st+8];fig=plt.figure(figsize=(12,3*len(b)))
  for i,x in enumerate(b):
   bounds=mesh(x['meshes']['gt']).bounds;draw(fig.add_subplot(len(b),3,3*i+1,projection='3d'),x['meshes']['gt'],bounds,x['cad_id']+' GT','gray');draw(fig.add_subplot(len(b),3,3*i+2,projection='3d'),x['meshes']['epoch18'],bounds,f"E18 F1={x['epochs']['18']['op_f1']:.2f}");draw(fig.add_subplot(len(b),3,3*i+3,projection='3d'),x['meshes']['epoch20'],bounds,f"E20 F1={x['epochs']['20']['op_f1']:.2f}")
  fig.tight_layout();fig.savefig(figdir/f'M2_GT_E18_E20_GALLERY_{st//8+1:02d}.png',dpi=170);plt.close(fig)
 fig=plt.figure(figsize=(8,3*max(1,len(valid))))
 for i,x in enumerate(valid):
  bounds=mesh(x['meshes']['gt']).bounds;draw(fig.add_subplot(len(valid),2,2*i+1,projection='3d'),x['meshes']['gt'],bounds,x['cad_id']+' GT','gray');draw(fig.add_subplot(len(valid),2,2*i+2,projection='3d'),x['meshes']['epoch20'],bounds,'E20 red / GT gray','tab:red',x['meshes']['gt'])
 fig.tight_layout();fig.savefig(figdir/'M2_EPOCH20_GT_PRED_OVERLAY_GALLERY.png',dpi=170);plt.close(fig)
 fail=[x for x in cases if not x['epochs']['18']['exec']['step_reload_pass'] or not x['epochs']['20']['exec']['step_reload_pass']];fig=plt.figure(figsize=(10,3*max(1,len(fail))))
 for i,x in enumerate(fail):
  ax=fig.add_subplot(len(fail),1,i+1);ax.axis('off');e=x['epochs']['20'];ax.text(.01,.98,f"{x['cad_id']}\nE20 failure={e['exec']['failure_stage']} {e['exec']['reason']}\n{e['pred_dsl'][:1000]}",va='top',family='monospace',fontsize=7,wrap=True)
 fig.tight_layout();fig.savefig(figdir/'M2_FAILURE_GALLERY.png',dpi=170);plt.close(fig)
 e18=e20=tie=0
 for x in cases:
  a,b=x['epochs']['18'],x['epochs']['20'];sa=(a['exec']['step_reload_pass'],a['op_f1']);sb=(b['exec']['step_reload_pass'],b['op_f1']);e18+=sa>sb;e20+=sb>sa;tie+=sa==sb
 summary={'VISUALIZATION_STATUS':'PASS','label':'TRAIN_SELF_DECODE_ONLY_NOT_HELDOUT','VIS_SAMPLES':16,'EPOCH18':{'EOS':16,'PARSE':sum(x['epochs']['18']['parse_pass'] for x in cases),'EXEC':sum(x['epochs']['18']['exec']['exec_pass'] for x in cases),'STEP_RELOAD':sum(x['epochs']['18']['exec']['step_reload_pass'] for x in cases)},'EPOCH20':{'EOS':14,'PARSE':sum(x['epochs']['20']['parse_pass'] for x in cases),'EXEC':sum(x['epochs']['20']['exec']['exec_pass'] for x in cases),'STEP_RELOAD':sum(x['epochs']['20']['exec']['step_reload_pass'] for x in cases)},'E18_BETTER_CASES':e18,'E20_BETTER_CASES':e20,'TIES':tie,'STEP_VISUALIZED':len(valid),'FAILURE_CASES':len(fail)};(OUT/'M2_VIS16_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
