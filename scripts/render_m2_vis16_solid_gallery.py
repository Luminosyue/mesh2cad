#!/usr/bin/env python3
"""Render saved VIS16 assets only: no model loading, decoding, or evaluation edits."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
import cadquery as cq

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');RUN=ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1';OUT=RUN/'epoch20_result_inspection';MAN=ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
FIG=OUT/'figures';CASE=FIG/'solid_cases';DISPLAY=OUT/'display_meshes';TOL=0.05;ANG=0.1;ELEV=25;AZIM=-55
def loadmesh(p):
 m=trimesh.load(str(p),force='mesh');return m.dump(concatenate=True) if isinstance(m,trimesh.Scene) else m
def step_to_stl(step,out):
 if out.exists():return out
 obj=cq.importers.importStep(str(step));cq.exporters.export(obj,str(out),tolerance=TOL,angularTolerance=ANG);return out
def canonical_input_mesh(source,out,tf_path):
 """Visualization-only copy in the frozen canonical frame used by V3 points."""
 if out.exists():return out
 m=loadmesh(source);tf=json.loads(Path(tf_path).read_text());m.vertices=m.vertices*float(tf['scale'])+np.asarray(tf['translation'],dtype=float);m.export(out);return out
def bounds(paths):
 b=np.array([loadmesh(p).bounds for p in paths if p and Path(p).is_file()]);return b[:,0].min(0),b[:,1].max(0)
def setcam(ax,b):
 lo,hi=b;pad=max(float(np.max(hi-lo))*.04,1e-8);ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),zlim=(lo[2]-pad,hi[2]+pad));ax.view_init(ELEV,AZIM);ax.set_proj_type('ortho');ax.set_axis_off()
def shade(ax,path,b,color,alpha=1,title=''):
 if not path or not Path(path).is_file():
  ax.text2D(.5,.5,title+'\nNO PRED STEP',ha='center',va='center',transform=ax.transAxes,fontsize=9);ax.set_axis_off();return
 m=loadmesh(path);faces=m.vertices[m.faces];poly=Poly3DCollection(faces,facecolor=color,edgecolor=(0,0,0,.08),linewidth=.03,alpha=alpha);ax.add_collection3d(poly);setcam(ax,b);ax.set_title(title,fontsize=8)
def render_four(case,out):
 paths=[case['input_mesh'],case['display']['gt'],case['display'].get('pred')];b=bounds(paths);fig=plt.figure(figsize=(18,4.7))
 shade(fig.add_subplot(1,4,1,projection='3d'),case['input_mesh'],b,'#94a3b8',.95,'INPUT MESH')
 shade(fig.add_subplot(1,4,2,projection='3d'),case['display']['gt'],b,'#9ca3af',1,'GT CAD')
 e=case['epoch20'];title=f"M2 E20 PRED\nOpF1={e['op_f1']:.3f} EOS={e['eos']}\nParse={e['exec']['parse_pass']} Exec={e['exec']['exec_pass']} STEP={e['exec']['step_reload_pass']}";shade(fig.add_subplot(1,4,3,projection='3d'),case['display'].get('pred'),b,'#ef4444',.9,title)
 ax=fig.add_subplot(1,4,4,projection='3d');shade(ax,case['display']['gt'],b,'#64748b',.35,'GT + E20 PRED');
 if case['display'].get('pred'):shade(ax,case['display']['pred'],b,'#ef4444',.45,'GT + E20 PRED')
 fig.suptitle(case['cad_id'],fontsize=11);fig.tight_layout();fig.savefig(out,dpi=200);plt.close(fig)
def main():
 FIG.mkdir(exist_ok=True);CASE.mkdir(exist_ok=True);DISPLAY.mkdir(exist_ok=True)
 pred={x['cad_id']:x for x in (json.loads(z) for z in (OUT/'M2_VIS16_PREDICTIONS.jsonl').read_text().splitlines() if z)};records={x['cad_id']:x for x in json.loads(MAN.read_text())['records']};sel=json.loads((OUT/'M2_VIS16_MANIFEST.json').read_text())['records'];cases=[]
 for s in sel:
  cid=s['cad_id'];p=pred[cid];d=OUT/'steps'/cid;source=Path(records[cid]['surface_input']).parent;inp=source/'mesh.obj';gt=d/'gt.step';pr=d/'epoch20_pred.step';dd=DISPLAY/cid;dd.mkdir(exist_ok=True);im=canonical_input_mesh(inp,dd/'input_mesh_canonical.stl',source/'coordinate_transform.json');gst=step_to_stl(gt,dd/'gt_display.stl') if gt.exists() else None;pst=step_to_stl(pr,dd/'epoch20_pred_display.stl') if pr.exists() else None
  c={'cad_id':cid,'bucket':s['selection_bucket'],'input_mesh':str(im),'display':{'gt':str(gst) if gst else None,'pred':str(pst) if pst else None},'epoch20':p['epochs']['20']};cases.append(c);render_four(c,CASE/f'{cid}.png')
 for start in range(0,16,8):
  batch=cases[start:start+8];fig=plt.figure(figsize=(18,4.2*len(batch)))
  for r,c in enumerate(batch):
   b=bounds([c['input_mesh'],c['display']['gt'],c['display'].get('pred')]);e=c['epoch20'];
   shade(fig.add_subplot(len(batch),4,4*r+1,projection='3d'),c['input_mesh'],b,'#94a3b8',.95,f"{c['cad_id']}\nINPUT MESH")
   shade(fig.add_subplot(len(batch),4,4*r+2,projection='3d'),c['display']['gt'],b,'#9ca3af',1,'GT CAD')
   shade(fig.add_subplot(len(batch),4,4*r+3,projection='3d'),c['display'].get('pred'),b,'#ef4444',.9,f"M2 E20\nF1={e['op_f1']:.2f} EOS={e['eos']}\nP={e['exec']['parse_pass']} E={e['exec']['exec_pass']} S={e['exec']['step_reload_pass']}")
   ax=fig.add_subplot(len(batch),4,4*r+4,projection='3d');shade(ax,c['display']['gt'],b,'#64748b',.35,'GT + PRED');
   if c['display'].get('pred'):shade(ax,c['display']['pred'],b,'#ef4444',.45,'GT + PRED')
  fig.tight_layout();fig.savefig(FIG/f'M2_EPOCH20_SOLID_GALLERY_{start+1:02d}_{start+len(batch):02d}.png',dpi=200);plt.close(fig)
 # Fixed six explanatory displays: two lowest-Chamfer valid, two median valid, and three failures (first six after dedupe).
 valid=[c for c in cases if c['display'].get('pred')];valid.sort(key=lambda c:c['epoch20'].get('geometry',{}).get('chamfer_norm',float('inf')));focus=valid[:2]+valid[max(0,len(valid)//2-1):len(valid)//2+1]+[c for c in cases if not c['display'].get('pred')][:2]
 fig=plt.figure(figsize=(13,3.5*len(focus)))
 for r,c in enumerate(focus):
  b=bounds([c['input_mesh'],c['display']['gt'],c['display'].get('pred')]);shade(fig.add_subplot(len(focus),3,3*r+1,projection='3d'),c['display']['gt'],b,color='#9ca3af',title=c['cad_id']+' GT');shade(fig.add_subplot(len(focus),3,3*r+2,projection='3d'),c['display'].get('pred'),b,color='#ef4444',title='E20 Pred');ax=fig.add_subplot(len(focus),3,3*r+3,projection='3d');shade(ax,c['display']['gt'],b,'#64748b',.35,'Overlay');
  if c['display'].get('pred'):shade(ax,c['display']['pred'],b,'#ef4444',.45,'Overlay')
 fig.tight_layout();fig.savefig(FIG/'M2_EPOCH20_SOLID_BEST_WORST_6.png',dpi=220);plt.close(fig)
 (FIG/'GEOMETRY_METRIC_POINTCLOUD_GALLERY.md').write_text('Existing M2_GT_E18_E20_GALLERY_*.png files are retained as GEOMETRY_METRIC_POINTCLOUD_GALLERY for Chamfer/Hausdorff inspection. New M2_EPOCH20_SOLID_* files are qualitative shaded-mesh views.\n')
 (OUT/'SOLID_RENDERING_CONFIG.json').write_text(json.dumps({'input':'existing clean triangulated mesh.obj transformed only into its frozen V3 canonical frame: xyz*coordinate_transform.scale + translation','gt':'existing gt.step tessellated to display STL','pred':'existing epoch20_pred.step tessellated to display STL','linear_deflection':TOL,'angular_deflection':ANG,'camera':{'elevation':ELEV,'azimuth':AZIM,'projection':'orthographic'},'axis_limits':'union(canonical input mesh, GT display mesh, predicted display mesh) per CAD','ICP_used':False,'model_inference':False},indent=2)+'\n')
 print(json.dumps({'VIS16_TOTAL':len(cases),'PRED_STEP_AVAILABLE':sum(bool(c['display'].get('pred')) for c in cases),'NO_PRED_STEP':sum(not c['display'].get('pred') for c in cases)},indent=2))
if __name__=='__main__':main()
