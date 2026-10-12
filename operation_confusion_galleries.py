#!/usr/bin/env python3
import csv,json
from pathlib import Path
src=Path(__file__).with_name('visualization_protocol_v2.py').read_text(encoding='utf-8');ns={'__name__':'__defs__'};exec(src.split('eligible=',1)[0],ns)
np=ns['np'];plt=ns['plt'];Poly3DCollection=ns['Poly3DCollection'];load_shape=ns['load_shape'];bounds=ns['bounds'];tess=ns['tess'];ROOT=ns['ROOT'];B=ns['B'];manifest=ns['manifest'];a0=ns['a0'];a3=ns['a3'];ch=ns['ch']
OUT=ROOT/'ours3/a0_a3_val1000_operation_confusion_equivalence_audit_v1';report=json.loads((OUT/'reports/FINAL_REPORT.json').read_text());thr=report['diagnostic_low_geometry_error_threshold']
arms=list(csv.DictReader((OUT/'alignment/OPERATION_ARMS.csv').open()));mismatch=[r for r in arms if r['arm']=='a3' and r['status']=='WRONG_TYPE_SUBSTITUTION' and ch(a3[r['cad_id']]) is not None and a3[r['cad_id']].get('step_ok')]
def unique(rows,key,limit):
 out=[];seen=set()
 for r in sorted(rows,key=key):
  if r['cad_id'] not in seen:seen.add(r['cad_id']);out.append(r)
  if len(out)>=limit:break
 return out
close=unique([r for r in mismatch if ch(a3[r['cad_id']])<=thr],lambda r:(ch(a3[r['cad_id']]),r['cad_id']),12)
bad=unique(mismatch,lambda r:(-ch(a3[r['cad_id']]),r['cad_id']),10)
box=unique([r for r in mismatch if r['gt_type']=='Box'],lambda r:(ch(a3[r['cad_id']]),r['cad_id']),10)
cache={}
def paths(cid):return [Path(manifest[cid]['gt_step_path']),B/'predictions/a0'/cid/'pred.step',B/'predictions/a3'/cid/'pred.step']
def assets(cid):
 if cid in cache:return cache[cid]
 ss=[load_shape(p) for p in paths(cid)];lo,hi=bounds(ss[0]);lin=max(.001*float(np.linalg.norm(hi-lo)),1e-6);cache[cid]=([tess(s,lin) for s in ss],(lo+hi)/2,max(float(np.max(hi-lo))/2,1e-9));return cache[cid]
def draw(ax,m,title,c,s,color):
 ax.set_title(title,fontsize=8);ax.set_axis_off();ax.set_proj_type('ortho');ax.view_init(24,-55,roll=0);ax.set_box_aspect((1,1,1));ax.set(xlim=(-1.08,1.08),ylim=(-1.08,1.08),zlim=(-1.08,1.08))
 if m is None:ax.text2D(.5,.5,'N/A',transform=ax.transAxes,ha='center');return
 v=(np.asarray(m.vertices)-c)/s;f=np.asarray(m.faces)
 if len(f)>8000:f=f[np.random.default_rng(42).choice(len(f),8000,replace=False)]
 q=Poly3DCollection(v[f],linewidths=.05,edgecolors=(.08,.1,.13,.18));q.set_facecolor(color);ax.add_collection3d(q)
def ops(cid,arm):
 z=[r for r in arms if r['cad_id']==cid and r['arm']==('a0' if arm=='gt' else arm)]
 return ','.join(r['gt_type'] if arm=='gt' else r['pred_type'] for r in z)
def gallery(rows,name,title):
 fig=plt.figure(figsize=(12,max(3,3.15*len(rows))),facecolor='white')
 if not rows:fig.text(.5,.5,'No qualifying VAL cases',ha='center',va='center')
 for i,r in enumerate(rows):
  cid=r['cad_id'];ms,c,s=assets(cid)
  for j,(m,n,col) in enumerate(zip(ms,['GT','A0','A3'],['#8fa8bd','#d38b75','#63ad83'])):draw(fig.add_subplot(len(rows),3,3*i+j+1,projection='3d'),m,n,c,s,col)
  x,y=a0[cid],a3[cid];lab=f"{cid} | {r['gt_type']}->{r['pred_type']} | GT ops: {ops(cid,'gt')} | A0: {ops(cid,'a0')} | A3: {ops(cid,'a3')} | Exact {int(x['exact_match'])}/{int(y['exact_match'])} | F1 {x['op_f1']:.3f}/{y['op_f1']:.3f} | STEP {int(x['step_ok'])}/{int(y['step_ok'])} | Ch {ch(x) if ch(x) is not None else 'N/A'}/{ch(y):.5f}"
  fig.text(.01,1-(i+.92)/len(rows),lab,fontsize=6.5)
 fig.suptitle(title,fontsize=14);fig.tight_layout(rect=(.03,0,1,.993));fig.savefig(OUT/'gallery'/name,dpi=160,bbox_inches='tight');plt.close(fig)
gallery(close,'ALTERNATIVE_CONSTRUCTION_GALLERY.png',f'Operation-Different Geometry-Close (diagnostic Chamfer <= {thr:.5g})')
gallery(bad,'OPERATION_SUBSTITUTION_BAD_GEOMETRY_GALLERY.png','Operation Substitution: Highest Geometry Error')
gallery(box,'BOX_TO_OTHER_CONSTRUCTION_GALLERY.png','GT Box -> Other Construction (lowest Chamfer first)')
(OUT/'gallery/GALLERY_PROTOCOL.json').write_text(json.dumps({'GT_SHARED_TRANSFORM':'YES','PER_OBJECT_AUTO_FIT':'NO','projection':'orthographic','camera':[24,-55,0],'low_geometry_threshold':thr,'selection':{'alternative':'all qualifying unique cases up to 12, lowest Chamfer','bad':'top 10 unique highest Chamfer','box':'top 10 unique lowest Chamfer Box substitutions'},'counts':{'alternative':len(close),'bad':len(bad),'box':len(box)},'TEST_TOUCHED':'NO'},indent=2)+'\n')
print(json.dumps({'alternative':len(close),'bad':len(bad),'box':len(box)}))
