from pathlib import Path
import json,sys,os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np,cadquery as cq
E=Path(os.environ.get('A2_RENDER_ROOT','/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_exact_overfit_v1'));ckpt=sys.argv[1]
parts=['PART_000','PART_001','PART_005']
def mesh(path):
 s=cq.importers.importStep(str(path)).val();v,f=s.tessellate(.12,.25)
 return np.asarray([[p.x,p.y,p.z] for p in v]),np.asarray(f)
def draw(ax,v,f,lo,hi,color):
 tri=v[f];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-12)
 light=np.array([.2,-.5,.85]);shade=.45+.5*np.abs(normal@light);rgb=np.asarray(matplotlib.colors.to_rgb(color));colors=np.clip(shade[:,None]*rgb,0,1)
 ax.add_collection3d(Poly3DCollection(tri,facecolors=colors,edgecolors='none',rasterized=True))
 center=(lo+hi)/2;half=max(hi-lo)*.55
 ax.set_xlim(center[0]-half,center[0]+half);ax.set_ylim(center[1]-half,center[1]+half);ax.set_zlim(center[2]-half,center[2]+half)
 ax.set_box_aspect([1,1,1],zoom=1.65);ax.view_init(24,-64);ax.set_axis_off()
fig=plt.figure(figsize=(16,8),dpi=150,facecolor='white')
fig.suptitle('P1-A2 airplane | '+ckpt,fontsize=20,fontweight='bold',y=.985)
fig.text(.5,.925,'Top: reference CAD. Bottom: actual deterministic free-decoding CAD. Exact status uses complete raw token sequences.',ha='center',fontsize=10,color='#475569')
for col,p in enumerate(parts):
 d=E/'evaluations'/ckpt/p;r=json.loads((d/'result.json').read_text());v,f=mesh(E/'gt_preflight'/p/'prediction.step')
 actual=mesh(d/'prediction.step') if r['STEP_EXPORT_PASS'] else None
 points=np.concatenate([v,actual[0]]) if actual else v;lo,hi=points.min(0),points.max(0)
 ax=fig.add_subplot(2,3,col+1,projection='3d');draw(ax,v,f,lo,hi,'#94a3b8');ax.set_title(p+' | Reference',fontsize=13,fontweight='bold')
 ax=fig.add_subplot(2,3,col+4,projection='3d')
 if actual:draw(ax,*actual,lo,hi,'#3b82f6')
 else:ax.set_axis_off();ax.text2D(.15,.5,'No executable CAD / STEP',transform=ax.transAxes,color='#b91c1c',fontsize=13)
 ax.set_title(p+' | '+('EXACT' if r['SEQUENCE_EXACT_MATCH'] else 'NOT EXACT'),fontsize=13,fontweight='bold',color='#15803d' if r['SEQUENCE_EXACT_MATCH'] else '#b91c1c')
 ax.text2D(.02,.04,f"Blocks {r['PRED_BLOCK_COUNT']}/{r['GT_BLOCK_COUNT']}  |  END+EOS {r['EOS_TERMINATED']}\nCAD execution {r['CAD_EXECUTION_PASS']}  |  STEP {r['STEP_EXPORT_PASS']}\nFirst divergence token: {r['FIRST_DIVERGENCE_TOKEN']}",transform=ax.transAxes,fontsize=9,color='#334155')
fig.subplots_adjust(left=.025,right=.975,top=.85,bottom=.04,wspace=.02,hspace=.08)
out=Path(os.environ.get('A2_RENDER_OUTPUT',str(E/f'{ckpt}_cad_comparison.png')));fig.savefig(out);print(out)
