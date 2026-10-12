#!/usr/bin/env python3
"""Read-only AUDIT30 render with actual fitted continuous curves in column 4."""
from __future__ import annotations
import importlib.util,json,pathlib,sys
import numpy as np
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');sys.path.insert(0,str(ROOT/'scripts'))
from dora_input_render_audit30 import mesh,setax,lines,gt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
spec=importlib.util.spec_from_file_location('fitmod',ROOT/'scripts/dora_fitted_curve_dataset_v1.py');fitmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(fitmod)
OUT=ROOT/'ours3/dora_input_data_audit_v1';BUILD=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'
def fitted(ax,fs):
 for f in fs:
  try:
   p,_,_,_=fitmod.sample_fit(f);ax.plot(p[:,0],p[:,1],p[:,2],color='#ef8a24',lw=1.2)
  except Exception: pass
def main():
 out=OUT/'figures_true_fitted';out.mkdir(exist_ok=True);sel=json.load(open(OUT/'AUDIT30_MANIFEST.json'))['records']; prov={json.loads(x)['cad_id']:json.loads(x) for x in open(OUT/'per_cad_provenance.jsonl')}
 for page in range((len(sel)+4)//5):
  fig=plt.figure(figsize=(21,15))
  for ri,r in enumerate(sel[page*5:(page+1)*5]):
   cid=r['cad_id'];b=BUILD/cid;p=prov[cid];raw=np.load(p['paths']['dora_raw_path']);g=json.load(open(b/'gt_brep_curves.json'));fs=json.load(open(b/'dora/fitted_curves.json'))['curves'];co=json.load(open(b/'correspondence.json'))['records'];
   for col,title in enumerate(('Mesh','GT B-Rep','Dora raw edge','Dora fitted continuous','GT + fitted','GT + raw')):
    ax=fig.add_subplot(5,6,ri*6+col+1,projection='3d');v=mesh(ax,p['paths']['mesh_path'])
    if col in (1,4,5):gt(ax,g)
    if col in (3,4):fitted(ax,fs)
    if col in (2,5):lines(ax,raw,'#e23b35',1.0)
    setax(ax,v);ax.set_title(title if ri==0 else '',fontsize=8)
   fig.text(.01,.94-ri*.185,f'{cid} | {r["source_dataset"]} | GT={len(g["curves"])} raw={len(raw["edge_length"])} fitted={len(fs)} | 1:1={sum(x["classification"]=="MATCHED_1_TO_1" for x in co)}/{len(co)}',fontsize=8)
  fig.suptitle('AUDIT30 — actual continuous fitted curves (orange), common object frame',fontsize=14);fig.tight_layout(rect=(.03,0,.99,.98));fig.savefig(out/f'gallery_true_fitted_{page+1:02d}.png',dpi=180);plt.close(fig)
 print('wrote',page+1,'pages')
if __name__=='__main__':main()
