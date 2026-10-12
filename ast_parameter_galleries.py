#!/usr/bin/env python3
import csv,json
from pathlib import Path
src=Path(__file__).with_name('visualization_protocol_v2.py').read_text(encoding='utf-8');ns={'__name__':'__defs__'};exec(src.split('eligible=',1)[0],ns)
np=ns['np'];plt=ns['plt'];Poly3DCollection=ns['Poly3DCollection'];load_shape=ns['load_shape'];bounds=ns['bounds'];tess=ns['tess'];ROOT=ns['ROOT'];B=ns['B'];manifest=ns['manifest']
OUT=ROOT/'ours3/a0_a3_val1000_ast_aligned_parameter_error_audit_v1'
sp=list(csv.DictReader((OUT/'tables/STRUCTURE_CORRECT_PARAMETER_WRONG_AUDIT.csv').open()));sc=list(csv.DictReader((OUT/'tables/SCALE_COLLAPSE_ROOT_CAUSE.csv').open()))
sp=sorted(sp,key=lambda r:(float(r['largest_error'] or -1),r['cad_id']),reverse=True)[:10];sc=sorted(sc,key=lambda r:(float(r['diag_ratio']),r['cad_id']))[:8]
cache={}
def paths(cid):return [Path(manifest[cid]['gt_step_path']),B/'predictions/a0'/cid/'pred.step',B/'predictions/a3'/cid/'pred.step']
def assets(cid):
 if cid in cache:return cache[cid]
 ss=[load_shape(p) for p in paths(cid)];lo,hi=bounds(ss[0]);lin=max(.001*float(np.linalg.norm(hi-lo)),1e-6);ms=[tess(s,lin) for s in ss];cache[cid]=(ms,(lo+hi)/2,max(float(np.max(hi-lo))/2,1e-9));return cache[cid]
def draw(ax,m,title,c,s,color):
 ax.set_title(title,fontsize=8);ax.set_axis_off();ax.set_proj_type('ortho');ax.view_init(24,-55,roll=0);ax.set_box_aspect((1,1,1));ax.set(xlim=(-1.08,1.08),ylim=(-1.08,1.08),zlim=(-1.08,1.08))
 if m is None:ax.text2D(.5,.5,'N/A',transform=ax.transAxes,ha='center');return
 v=(np.asarray(m.vertices)-c)/s;f=np.asarray(m.faces)
 if len(f)>8000:f=f[np.random.default_rng(42).choice(len(f),8000,replace=False)]
 q=Poly3DCollection(v[f],linewidths=.05,edgecolors=(.08,.1,.13,.18));q.set_facecolor(color);ax.add_collection3d(q)
def gallery(rows,target,title,label):
 fig=plt.figure(figsize=(12,3.2*len(rows)),facecolor='white')
 for i,r in enumerate(rows):
  cid=r['cad_id'];ms,c,s=assets(cid)
  for j,(m,n,col) in enumerate(zip(ms,['GT','A0','A3'],['#8fa8bd','#d38b75','#63ad83'])):draw(fig.add_subplot(len(rows),3,3*i+j+1,projection='3d'),m,n,c,s,col)
  fig.text(.01,1-(i+.92)/len(rows),label(r),fontsize=7)
 fig.suptitle(title,fontsize=14);fig.tight_layout(rect=(.03,0,1,.993));fig.savefig(OUT/'gallery'/target,dpi=160,bbox_inches='tight');plt.close(fig)
gallery(sp,'STRUCTURE_CORRECT_PARAMETER_WRONG_GALLERY.png','Structure Correct / Parameter Wrong (Shared GT Transform)',lambda r:f"{r['cad_id']} | matched ops={r['matched_operations']} | largest={r['largest_operation']}.{r['largest_field']} | GT={r['GT_value']} | A3={r['A3_value']} | err={r['largest_error']} | {r['labels']}")
gallery(sc,'A3_SCALE_COLLAPSE_ROOT_CAUSE_GALLERY.png','A3 Scale Collapse Root Causes (Shared GT Transform)',lambda r:f"{r['cad_id']} | diag ratio={float(r['diag_ratio']):.4f} | cause={r['root_cause']} | fields={r['scale_fields']} | ratios={r['ratios']}")
(OUT/'gallery/GALLERY_PROTOCOL.json').write_text(json.dumps({'GT_SHARED_TRANSFORM':'YES','PER_OBJECT_AUTO_FIT':'NO','camera':[24,-55,0],'projection':'orthographic','selection':{'structure_wrong':'largest parameter error top 10','scale_collapse':'smallest A3 diag ratio top 8'},'TEST_TOUCHED':'NO'},indent=2)+'\n')
print(json.dumps({'structure_n':len(sp),'collapse_n':len(sc)}))
