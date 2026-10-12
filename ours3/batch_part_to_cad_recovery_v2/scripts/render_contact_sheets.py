#!/usr/bin/env python3
import importlib.util,json,math
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection,PolyCollection
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'batch_part_to_cad_recovery_v2';AUD=ROOT/'batch_10_step_quality_audit_v1/scripts/audit_batch.py'
s=importlib.util.spec_from_file_location('audit',AUD);audit=importlib.util.module_from_spec(s);s.loader.exec_module(audit)
def proj(p):
 az,el=np.deg2rad(38),np.deg2rad(24);rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]]);rx=np.array([[1,0,0],[0,np.cos(el),-np.sin(el)],[0,np.sin(el),np.cos(el)]]);return p@(rz@rx).T
def lim(ax,p):
 lo=p[:,:2].min(0);hi=p[:,:2].max(0);span=np.maximum(hi-lo,1e-9);ax.set_xlim(lo[0]-.06*span[0],hi[0]+.06*span[0]);ax.set_ylim(lo[1]-.06*span[1],hi[1]+.06*span[1]);ax.set_aspect('equal');ax.axis('off')
def main():
 rows=json.loads((OUT/'artifacts/batch10_rows.json').read_text());figs=[]
 for mode in ['SHADED','TRUE_EDGES']:
  fig,axs=plt.subplots(2,5,figsize=(20,8),facecolor='#f4f5f7');fig.suptitle('Batch 10 Latest Best — '+('CAD Shaded' if mode=='SHADED' else 'True B-rep Edges'),fontsize=20,fontweight='bold')
  for ax,row in zip(axs.flat,rows):
   # CASE00's exact feature-complete historical STEP is 339 MB.  Reuse its
   # frozen, already STEP-derived audit render to avoid a second multi-minute
   # tessellation while preserving the exact SELECTED_BEST visualization.
   if row['CASE_ID']=='CASE_00':
    cached=ROOT/('batch_10_cad_shaded_render_v1/case_00/cad_shaded.png' if mode=='SHADED' else 'batch_10_step_quality_audit_v1/cases/CASE_00/brep_true_edges.png')
    ax.imshow(plt.imread(cached));ax.axis('off');ax.set_title(f"{row['CASE_ID']}  {row['GEOM_Q']}\n{row['STRUCTURAL_CLASS']}",fontsize=10);continue
   ok,roots,shape=audit.fresh_read(Path(row['SELECTED_BEST_PATH']));top=audit.topology_audit(shape);P=[]
   if mode=='SHADED':
    t=audit.tessellate(shape,top['BBOX_DIAGONAL']);v=proj(np.asarray(t['vertices']));faces=np.asarray(t['faces']);take=np.linspace(0,len(faces)-1,min(len(faces),9000),dtype=int);f=faces[take];poly=v[f,:2];n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);shade=.45+.45*np.clip(np.abs(n[:,2])/np.maximum(np.linalg.norm(n,axis=1),1e-12),0,1);colors=np.c_[.18+.24*shade,.42+.30*shade,.62+.30*shade,np.ones(len(shade))];order=np.argsort(v[f].mean(1)[:,2]);ax.add_collection(PolyCollection(poly[order],facecolors=colors[order],edgecolors='none'));P=v
   else:
    pts,lens,_=audit.edge_render_cache(shape,top['EDGE_COUNT'],top['BBOX_DIAGONAL'],max_edges=5000);v=proj(np.asarray(pts));segments=[];cur=0
    for n in lens:segments.append(v[cur:cur+int(n),:2]);cur+=int(n)
    ax.add_collection(LineCollection(segments,colors='#132a3a',linewidths=.45,alpha=.9));P=v
   lim(ax,np.asarray(P));ax.set_title(f"{row['CASE_ID']}  {row['GEOM_Q']}\n{row['STRUCTURAL_CLASS']}",fontsize=10)
  fig.tight_layout(rect=(0,0,1,.94));path=OUT/'artifacts'/('batch10_latest_best_cad_shaded.png' if mode=='SHADED' else 'batch10_latest_best_true_edges.png');fig.savefig(path,dpi=180,bbox_inches='tight');plt.close(fig);print(path)
if __name__=='__main__':main()
