#!/usr/bin/env python3
"""Read-only visual audit: Mesh | GT | Dora raw | chains | overlay."""
from __future__ import annotations
import json,pathlib
from collections import Counter
import numpy as np, matplotlib.pyplot as plt, trimesh
from mpl_toolkits.mplot3d import Axes3D  # registers the 3D projection
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'ours3/dora_input_data_audit_v1';BUILD=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'
def setax(ax,pts):
 if len(pts):
  lo,hi=pts.min(0),pts.max(0);c=(lo+hi)/2;r=max((hi-lo).max()/2,1e-5)
  ax.set_xlim(c[0]-r,c[0]+r);ax.set_ylim(c[1]-r,c[1]+r);ax.set_zlim(c[2]-r,c[2]+r)
 ax.set_axis_off();ax.view_init(25,-55)
def mesh(ax,p):
 m=trimesh.load(p,force='mesh');m=m.dump(concatenate=True) if isinstance(m,trimesh.Scene) else m
 ax.plot_trisurf(m.vertices[:,0],m.vertices[:,1],m.vertices[:,2],triangles=m.faces,color='#b7c2cc',alpha=.28,linewidth=0.05);return m.vertices
def lines(ax,a,color,lw=1,alpha=1):
 for x,y in zip(a['edge_xyz0'],a['edge_xyz1']):
  p=np.stack([x,y]);ax.plot(p[:,0],p[:,1],p[:,2],color=color,lw=lw,alpha=alpha)
def chains(ax,verts,z,color,lw=1):
 f=z['vertex_indices_flat'];o=z['offsets']
 for i in range(len(o)-1):
  p=verts[f[o[i]:o[i+1]]];ax.plot(p[:,0],p[:,1],p[:,2],color=color,lw=lw)
def gt(ax,g):
 # Exact line edges plus clearly marked chord fallback for unavailable non-line samplers.
 for x in g['curves']:
  a=np.array(x['start_point']);b=np.array(x['end_point']);p=np.stack([a,b]);ax.plot(p[:,0],p[:,1],p[:,2],color='#13a8c7',lw=1.2,alpha=.85)
def assess(co):
 c=Counter(x['classification'] for x in co['records']);n=max(len(co['records']),1);mr=c['MATCHED_1_TO_1']/n
 return ('GOOD' if mr>=.65 else 'PARTIAL' if mr>=.35 else 'BAD'),mr,c
def main():
 out=OUT/'figures';out.mkdir(exist_ok=True);sel=json.load(open(OUT/'AUDIT30_MANIFEST.json'))['records'];quality=[]
 for page in range((len(sel)+4)//5):
  fig=plt.figure(figsize=(18,15))
  for ri,r in enumerate(sel[page*5:(page+1)*5]):
   cid=r['cad_id'];b=BUILD/cid;prov=next(json.loads(x) for x in open(OUT/'per_cad_provenance.jsonl') if json.loads(x)['cad_id']==cid);mfile=prov['paths']['mesh_path'];raw=np.load(prov['paths']['dora_raw_path']);z=np.load(b/'dora/chains.npz');g=json.load(open(b/'gt_brep_curves.json'));co=json.load(open(b/'correspondence.json'));fit=json.load(open(b/'dora/fitted_curves.json'));label,mr,cc=assess(co)
   for col,title in enumerate(('Mesh','GT B-Rep','Dora raw edge','Dora chain/fitted source','GT + Dora raw')):
    ax=fig.add_subplot(5,5,ri*5+col+1,projection='3d');v=mesh(ax,mfile)
    if col in (1,4):gt(ax,g)
    if col in (2,4):lines(ax,raw,'#e23b35',1.1)
    if col==3:chains(ax,v,z,'#f08a24',1.4)
    setax(ax,v);ax.set_title(title if ri==0 else '',fontsize=9)
   fig.text(.01,.94-ri*.185,f'{cid} | {label} | 1:1={cc["MATCHED_1_TO_1"]}/{len(co["records"])} ({mr:.2f}) | raw={len(raw["edge_length"])} chains={len(z["offsets"])-1} fit={len(fit["curves"])}',fontsize=8)
   quality.append({'cad_id':cid,'rule_label':label,'matched_ratio':mr,'raw_edge_points_or_segments':len(raw['edge_length']),'chain_count':len(z['offsets'])-1,'fitted_curve_count':len(fit['curves']),'classification_counts':dict(cc),'interpretation':'Rule label is correspondence-based proxy; visual panel required for causal layer assignment.'})
  fig.suptitle('DORA_INPUT_DATA_AUDIT_V1 — fixed AUDIT30, common CAD coordinates',fontsize=14);fig.tight_layout(rect=(.03,0,.99,.98));fig.savefig(out/f'GT_vs_DORA_gallery_{page+1:02d}.png',dpi=180);plt.close(fig)
 (OUT/'raw_edge_quality.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in quality));print('pages',page+1,'records',len(quality))
if __name__=='__main__':main()
