#!/usr/bin/env python3
import csv, json
from pathlib import Path

# Reuse the frozen V2 STEP loader/tessellator definitions, but do not execute its selections.
src=Path(__file__).with_name('visualization_protocol_v2.py').read_text(encoding='utf-8')
ns={'__name__':'__gallery_defs__'}
exec(src.split('eligible=',1)[0],ns)
np=ns['np']; plt=ns['plt']; Poly3DCollection=ns['Poly3DCollection']
load_shape=ns['load_shape']; bounds=ns['bounds']; tess=ns['tess']
ROOT=ns['ROOT']; B=ns['B']; manifest=ns['manifest']; a0=ns['a0']; a3=ns['a3']; ch=ns['ch']
OUT=ROOT/'ours3/a0_a3_val1000_placement_scale_parameter_error_audit_v1'
rows=list(csv.DictReader((OUT/'tables/PLACEMENT_SCALE_PER_CASE.csv').open(encoding='utf-8')))
by={(r['model'],r['cad_id']):r for r in rows}
both=sorted(set(i for m,i in by if m=='a0') & set(i for m,i in by if m=='a3'))
def val(m,i,k): return float(by[(m,i)][k])
def choose(pool,key,n=4,reverse=False): return sorted(set(pool),key=lambda i:(key(i),i),reverse=reverse)[:n]
collapse=[i for i in both if min(val('a0',i,'diag_ratio'),val('a3',i,'diag_ratio'))<.5]
placement=[i for i in both if max(val('a0',i,'center_error_rel'),val('a3',i,'center_error_rel'))>.25]
sggb=[i for i in both if 'STRUCTURE_CORRECT_PARAMETER_WRONG' in by[('a3',i)]['labels']]
groups={
 'Scale Collapse':choose(collapse,lambda i:min(val('a0',i,'diag_ratio'),val('a3',i,'diag_ratio'))),
 'Placement Shift':choose(placement,lambda i:max(val('a0',i,'center_error_rel'),val('a3',i,'center_error_rel')),reverse=True),
 'Structure-good / Geometry-bad':choose(sggb,lambda i:val('a3',i,'chamfer'),reverse=True),
 'A3 Geometry Rescue':choose(both,lambda i:val('a3',i,'chamfer')-val('a0',i,'chamfer')),
}
cache={}
def paths(cid): return [Path(manifest[cid]['gt_step_path']),B/'predictions/a0'/cid/'pred.step',B/'predictions/a3'/cid/'pred.step']
def assets(cid):
 if cid in cache:return cache[cid]
 ss=[load_shape(p) for p in paths(cid)];lo,hi=bounds(ss[0]);lin=max(.001*float(np.linalg.norm(hi-lo)),1e-6)
 ms=[tess(s,lin) for s in ss];center=(lo+hi)/2;scale=max(float(np.max(hi-lo))/2,1e-9)
 cache[cid]=(ms,center,scale,lin);return cache[cid]
def draw(ax,m,title,center,scale,color):
 ax.set_title(title,fontsize=8);ax.set_axis_off();ax.set_proj_type('ortho');ax.view_init(24,-55,roll=0);ax.set_box_aspect((1,1,1));ax.set(xlim=(-1.08,1.08),ylim=(-1.08,1.08),zlim=(-1.08,1.08))
 if m is None:ax.text2D(.5,.5,'N/A',transform=ax.transAxes,ha='center',va='center');return
 v=(np.asarray(m.vertices)-center)/scale;f=np.asarray(m.faces)
 if len(f)>8000:f=f[np.random.default_rng(42).choice(len(f),8000,replace=False)]
 c=Poly3DCollection(v[f],linewidths=.05,edgecolors=(.08,.1,.13,.18));c.set_facecolor(color);ax.add_collection3d(c)
items=[(g,i) for g,ids in groups.items() for i in ids]
fig=plt.figure(figsize=(12,3.25*len(items)),facecolor='white')
for r,(grp,cid) in enumerate(items):
 ms,cen,sc,lin=assets(cid)
 for j,(m,n,c) in enumerate(zip(ms,[f'{grp} | GT','A0','A3'],['#8fa8bd','#d38b75','#63ad83'])):draw(fig.add_subplot(len(items),3,3*r+j+1,projection='3d'),m,n,cen,sc,c)
 x,y=by[('a0',cid)],by[('a3',cid)]
 label=(f"{cid} | K={manifest[cid]['K']} | Op-F1 {float(x['op_f1']):.3f}/{float(y['op_f1']):.3f} | "
        f"Chamfer {float(x['chamfer']):.4f}/{float(y['chamfer']):.4f} | Center {float(x['center_error_rel']):.3f}/{float(y['center_error_rel']):.3f} | "
        f"Extent {float(x['extent_error_rel']):.3f}/{float(y['extent_error_rel']):.3f} | Diag {float(x['diag_ratio']):.3f}/{float(y['diag_ratio']):.3f}")
 fig.text(.01,1-(r+.92)/len(items),label,fontsize=7)
fig.suptitle('A0 vs A3 Placement / Scale Diagnostic (Shared GT Transform)',fontsize=14)
fig.tight_layout(rect=(.03,0,1,.993));target=OUT/'gallery/PLACEMENT_SCALE_DIAGNOSTIC_GALLERY.png';fig.savefig(target,dpi=150,bbox_inches='tight');plt.close(fig)
(OUT/'audits/PLACEMENT_SCALE_GALLERY_PROTOCOL.json').write_text(json.dumps({'selection':groups,'GT_SHARED_TRANSFORM':'YES','PER_OBJECT_AUTO_FIT':'NO','projection':'orthographic','camera':[24,-55,0],'axis_limits':[-1.08,1.08],'tessellation':'same absolute max(0.001*GT_diag,1e-6) for GT/A0/A3','test_touched':'NO'},indent=2)+'\n')
print(json.dumps({'gallery':str(target),'groups':groups},indent=2))
