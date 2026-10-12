import hashlib,json,math,shutil
from pathlib import Path
import numpy as np,trimesh
from PIL import Image,ImageDraw
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SRC=ROOT/'mesh2cad_stl/parts'; OUT=ROOT/'ours3/GPT6_PARTSAM_REALMESH_PSEUDOCAD_DATASET_V1'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def audit(p):
 m=trimesh.load_mesh(p,process=False)
 if isinstance(m,trimesh.Scene):m=trimesh.util.concatenate(tuple(m.geometry.values()))
 bb=np.asarray(m.bounds,float);x=np.asarray(m.vertices,float);x-=x.mean(0);_,vt=np.linalg.eigh(np.cov(x,rowvar=False));vt=vt[::-1]
 return m,{'vertices':len(m.vertices),'faces':len(m.faces),'watertight':bool(m.is_watertight),'connected_components':len(m.split(only_watertight=False)),'bbox':bb,'bbox_extent':bb[1]-bb[0],'centroid':m.centroid,'surface_area':float(m.area),'volume':float(abs(m.volume)) if m.is_volume else None,'pca_axes':vt.tolist(),'source_mesh_sha256':sha(p)}
def render(m,p,az,el):
 v=np.asarray(m.vertices);f=np.asarray(m.faces);ca,sa=np.cos(az),np.sin(az);ce,se=np.cos(el),np.sin(el);R=np.array([[ca,-sa,0],[sa,ca,0],[0,0,1.]])@np.array([[1,0,0],[0,ce,-se],[0,se,ce]]);q=v@R.T;lo=q[:,:2].min(0);sp=np.maximum(q[:,:2].max(0)-lo,1e-9);q=(q[:,:2]-lo)/sp;im=Image.new('RGB',(320,320),'white');d=ImageDraw.Draw(im);ids=np.arange(len(f));ids=ids if len(ids)<6000 else np.linspace(0,len(f)-1,6000,dtype=int)
 for j in ids[np.argsort(q[f[ids]].mean((1,2)))]:
  d.polygon([(int(q[k,0]*280+20),int(300-q[k,1]*280)) for k in f[j]],fill=(180,195,215))
 im.save(p)
files=sorted(SRC.glob('*/*.stl')); groups={}
for p in files:groups.setdefault(p.parent.name,[]).append(p)
order=[]
for oid,ps in sorted(groups.items()):
 order.append(min(ps,key=lambda p:hashlib.sha256((oid+'|'+p.name).encode()).hexdigest()))
rest=[p for p in files if p not in order];rest.sort(key=lambda p:hashlib.sha256((p.parent.name+'|'+p.name).encode()).hexdigest());chosen=(order+rest)[:100]
OUT.mkdir(parents=True,exist_ok=True);manifest=[]
for i,p in enumerate(chosen):
 oid=p.parent.name;sid=f'pilot100_{i:03d}_{oid}_{p.stem}';d=OUT/'samples'/sid;(d/'renders').mkdir(parents=True,exist_ok=True);m,a=audit(p);shutil.copy2(p,d/'source_mesh.stl')
 for n,az,el in [('front',0,0),('back',3.14,0),('left',1.57,0),('right',-1.57,0),('top',0,1.57),('bottom',0,-1.57),('persp_a',.65,.45),('persp_b',-.85,.55)]:render(m,d/'renders'/f'{n}.png',az,el)
 r={'sample_id':sid,'object_id':oid,'part_id':p.stem,'source_mesh':str(d/'source_mesh.stl'),'source_original':str(p),'source_mesh_sha256':a['source_mesh_sha256'],'geometry_summary':a,'prompt_version':'gpt6_astra_realmesh_v1','gpt_model':'gpt-6-astra','status':'READY_FOR_GPT_RESPONSES_API','attempts':[]};(d/'geometry_summary.json').write_text(json.dumps(a,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x));manifest.append(r)
objs=sorted(set(r['object_id'] for r in manifest),key=lambda x:hashlib.sha256(x.encode()).hexdigest());spl={o:('test' if i%10==0 else 'val' if i%10==1 else 'train') for i,o in enumerate(objs)}
for r in manifest:r['split']=spl[r['object_id']]
(OUT/'pilot100_manifest.json').write_text(json.dumps(manifest,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x));(OUT/'selection_report.json').write_text(json.dumps({'TOTAL':len(manifest),'OBJECTS':len(objs),'split_counts':{s:sum(r['split']==s for r in manifest) for s in ['train','val','test']},'selection':'deterministic hash, object-first'},indent=2));print(json.dumps({'TOTAL':len(manifest),'OBJECTS':len(objs)}))

