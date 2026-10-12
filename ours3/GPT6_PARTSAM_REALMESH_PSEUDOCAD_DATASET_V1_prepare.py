#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, shutil
from pathlib import Path
import numpy as np, trimesh
from PIL import Image, ImageDraw
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SRC=ROOT/'mesh2cad_stl/parts'; OUT=ROOT/'ours3/GPT6_PARTSAM_REALMESH_PSEUDOCAD_DATASET_V1'; PROMPT_VERSION='gpt6_astra_realmesh_v1'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def js(x):
 if isinstance(x,dict): return {k:js(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [js(v) for v in x]
 if isinstance(x,np.ndarray): return x.tolist()
 if isinstance(x,np.generic): return x.item()
 if isinstance(x,float) and not math.isfinite(x): return None
 return x
def render(m,path,az,el):
 v=np.asarray(m.vertices,float); f=np.asarray(m.faces,int)
 if len(f)==0:return
 ca,sa=np.cos(az),np.sin(az); ce,se=np.cos(el),np.sin(el)
 R=np.array([[ca,-sa,0],[sa,ca,0],[0,0,1.]])@np.array([[1,0,0],[0,ce,-se],[0,se,ce]])
 q=v@R.T; lo=q[:,:2].min(0); hi=q[:,:2].max(0); span=np.maximum(hi-lo,1e-9); q=(q[:,:2]-lo)/span
 im=Image.new('RGB',(448,448),'white'); d=ImageDraw.Draw(im); ids=np.arange(len(f))
 if len(ids)>12000: ids=np.linspace(0,len(f)-1,12000,dtype=int)
 z=q[f[ids]].mean((1,2))
 for j in ids[np.argsort(z)]:
  pts=[(int(q[k,0]*408+20),int(428-q[k,1]*408)) for k in f[j]]; d.polygon(pts,fill=(180,195,215),outline=(65,75,90))
 im.save(path)
def audit(p):
 m=trimesh.load_mesh(p,process=False)
 if isinstance(m,trimesh.Scene): m=trimesh.util.concatenate(tuple(g for g in m.geometry.values()))
 comps=m.split(only_watertight=False); bb=np.asarray(m.bounds,float); vol=float(abs(m.volume)) if m.is_volume else None
 x=np.asarray(m.vertices,float)-np.asarray(m.vertices,float).mean(0); _,vt=np.linalg.eigh(np.cov(x,rowvar=False)); vt=vt[::-1]
 return m,{'vertices':int(len(m.vertices)),'faces':int(len(m.faces)),'watertight':bool(m.is_watertight),'connected_components':int(len(comps)),'bbox':bb,'bbox_extent':bb[1]-bb[0],'centroid':m.centroid,'surface_area':float(m.area),'volume':vol,'pca_axes':vt[:3],'source_mesh_sha256':sha(p)}
def main():
 files=sorted(SRC.glob('*/*.stl')); rows=[]
 for p in files:
  try: m,a=audit(p); rows.append((p.parent.name,p,a))
  except Exception: pass
 order=sorted(range(len(rows)),key=lambda i:(hashlib.sha256((rows[i][0]+'|'+rows[i][1].name).encode()).hexdigest(),rows[i][0],rows[i][1].name)); chosen=[]; seen=set()
 for i in order:
  if rows[i][0] not in seen: chosen.append(i); seen.add(rows[i][0])
  if len(chosen)>=100: break
 for i in order:
  if i not in chosen: chosen.append(i)
  if len(chosen)>=100: break
 OUT.mkdir(parents=True,exist_ok=True); manifest=[]
 for j,i in enumerate(chosen):
  oid,p,a=rows[i]; sid=f'pilot100_{j:03d}_{oid}_{p.stem}'; d=OUT/'samples'/sid; (d/'renders').mkdir(parents=True,exist_ok=True); m,_=audit(p); shutil.copy2(p,d/'source_mesh.stl')
  for name,az,el in [('front',0,0),('back',math.pi,0),('left',math.pi/2,0),('right',-math.pi/2,0),('top',0,math.pi/2),('bottom',0,-math.pi/2),('persp_a',0.65,0.45),('persp_b',-0.85,0.55)]: render(m,d/'renders'/f'{name}.png',az,el)
  row={'sample_id':sid,'object_id':oid,'part_id':p.stem,'source_mesh':str(d/'source_mesh.stl'),'source_original':str(p),'source_mesh_sha256':a['source_mesh_sha256'],'geometry_summary':a,'prompt_version':PROMPT_VERSION,'gpt_model':'gpt-6-astra','status':'READY_FOR_GPT_RESPONSES_API','attempts':[]}
  (d/'geometry_summary.json').write_text(json.dumps(js(a),indent=2)); (d/'input_manifest.json').write_text(json.dumps(js(row),indent=2)); manifest.append(row)
 objs=sorted(set(r['object_id'] for r in manifest),key=lambda x:hashlib.sha256(x.encode()).hexdigest()); split={o:('test' if k%10==0 else 'val' if k%10==1 else 'train') for k,o in enumerate(objs)}
 for r in manifest:r['split']=split[r['object_id']]
 (OUT/'pilot100_manifest.json').write_text(json.dumps(js(manifest),indent=2)); (OUT/'selection_report.json').write_text(json.dumps({'TOTAL':len(manifest),'OBJECTS':len(objs),'split_counts':{s:sum(v==s for v in split.values()) for s in set(split.values())},'selection':'deterministic hash order; object-first'},indent=2)); print(json.dumps({'TOTAL':len(manifest),'OBJECTS':len(objs),'OUT':str(OUT)}))
if __name__=='__main__': main()

