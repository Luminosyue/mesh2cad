import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,argparse
from pathlib import Path
import numpy as np,trimesh
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parents[1]
def panel(points,colors,title,center,span):
 res=640;im=Image.new('RGB',(res,res),'white');draw=ImageDraw.Draw(im);draw.text((12,12),title,fill='black')
 if points is None:draw.text((160,300),'NO STRICT ACCEPTED CAD',fill='#a02020');return im
 rz=np.deg2rad(-38);rx=np.deg2rad(24);Rz=np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]]);Rx=np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]]);q=(points-center)@(Rz@Rx).T
 xy=q[:,:2]*(res*.50/span)+res/2;xy[:,1]=res-xy[:,1];order=np.argsort(q[:,2]);pixels=np.asarray(im).copy()
 for idx in order:
  x,y=np.rint(xy[idx]).astype(int)
  if 2<=x<res-2 and 35<=y<res-2:pixels[y-1:y+2,x-1:x+2]=colors[idx] if np.ndim(colors)==2 else colors
 im=Image.fromarray(pixels);return im
ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,required=True);a=ap.parse_args();records=[]
for obj in json.loads((O/'manifests/objects_frozen.json').read_text())[:a.limit]:
 d=O/'objects'/obj['object_id'];src=trimesh.load(obj['canonical_path'],force='mesh',process=True);p,ids=trimesh.sample.sample_surface(src,65000,seed=20261006);center=src.bounds.mean(0);span=max(src.extents)
 labelpath=d/'p3/face_labels.npy';colored=np.tile([80,140,220],(len(p),1))
 if labelpath.exists():
  labels=np.load(labelpath);rng=np.random.default_rng(20261006);palette=rng.integers(45,220,(max(int(labels.max())+2,2),3));colored=palette[labels[ids]+1]
 light=np.array([.3,-.4,.866]);shade=(.35+.65*np.abs(src.face_normals[ids]@light))[:,None]
 source_colors=(np.array([75,145,220])*shade).astype(np.uint8);colored=(colored*shade).astype(np.uint8)
 assembled=d/'assembly/assembly_mesh.obj';cp=None;cad_colors=[230,140,50];assembly_colors=[70,180,130]
 if assembled.exists():
  cm=trimesh.load(assembled,force='mesh',process=True);cp,ci=trimesh.sample.sample_surface(cm,65000,seed=20261007);cs=(.35+.65*np.abs(cm.face_normals[ci]@light))[:,None];cad_colors=(np.array(cad_colors)*cs).astype(np.uint8);assembly_colors=(np.array(assembly_colors)*cs).astype(np.uint8)
 panes=[panel(p,source_colors,'Original mesh: '+obj['name'][:50],center,span),panel(p,colored,'P3 source-face labels',center,span),panel(cp,cad_colors,'Strict accepted part CADs',center,span),panel(cp,assembly_colors,'Final assembly (missing parts remain absent)',center,span)]
 canvas=Image.new('RGB',(1280,1280),'white')
 for i,im in enumerate(panes):canvas.paste(im,((i%2)*640,(i//2)*640))
 canvas.save(O/'visualizations'/(obj['object_id']+'.png'))
 if cp is not None:
  strict_points=np.vstack([p,cp]);strict_colors=np.vstack([np.tile([75,145,220],(len(p),1)),np.tile([230,100,50],(len(cp),1))])
  panel(strict_points,strict_colors,'STRICT SUBSET: source blue / CAD orange; missing parts absent',center,span).save(O/'visualizations'/(obj['object_id']+'_strict_overlay.png'))
 if len(records)<5 or cp is not None:
  diagnostic=[];pm=json.loads((d/'p3/parts_manifest.json').read_text())
  for part in pm['parts']:
   rp=d/'parts'/part['part_id']/'result.json'
   if not rp.exists():continue
   rec=json.loads(rp.read_text())
   if not rec.get('cad_mesh_path'):continue
   dm=trimesh.load(rec['cad_mesh_path'],force='mesh',process=True);dm.apply_transform(part['world_transform']);dp,_=trimesh.sample.sample_surface(dm,max(400,int(65000*part['area_fraction'])),seed=20261008);diagnostic.append(dp)
  dc=np.vstack(diagnostic) if diagnostic else None
  pts=np.vstack([p,dc]) if dc is not None else p;colors=np.vstack([np.tile([75,145,220],(len(p),1)),np.tile([230,100,50],(len(dc),1))]) if dc is not None else np.tile([75,145,220],(len(p),1))
  panel(pts,colors,'DIAGNOSTIC: source blue / best CAD orange (includes rejected)',center,span).save(O/'visualizations'/(obj['object_id']+'_overlay.png'))
 records.append(dict(obj,has_assembly=cp is not None))
(O/'visualizations/index.html').write_text('<meta charset="utf-8"><h1>High-detail object / P3 parts / strict CAD / assembly</h1><p>Fixed camera and source scale. No assembly is shown when no part passes the strict gate. Point rendering uses deterministic area-uniform samples and normal shading.</p><h2>Diagnostic overlays (include rejected candidates; not accepted assemblies)</h2>'+''.join(f'<a href="{r["object_id"]}_overlay.png">{r["object_id"]} source vs best CAD</a><br>' for i,r in enumerate(records) if i<5 or r['has_assembly'])+'<h2>Strict-subset overlays</h2>'+''.join(f'<a href="{r["object_id"]}_strict_overlay.png">{r["object_id"]} source vs strict subset</a><br>' for r in records if r['has_assembly'])+''.join(f'<h2>{r["object_id"]}: {r["name"]}</h2><img style="max-width:1280px;width:100%" src="{r["object_id"]}.png">' for r in records))
contact=Image.new('RGB',(1280,((len(records)+4)//5)*276),'white')
for i,r in enumerate(records):
 im=Image.open(O/'visualizations'/(r['object_id']+'.png')).resize((256,256));x=i%5*256;y=i//5*276;contact.paste(im,(x,y+20));ImageDraw.Draw(contact).text((x+5,y+4),r['object_id'],fill='black')
contact.save(O/'visualizations/contact_sheet.png')
print('VISUALIZED',len(records))
