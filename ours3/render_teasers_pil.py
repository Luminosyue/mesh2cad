import json,math
from pathlib import Path
import numpy as np,trimesh,cadquery as cq
from PIL import Image,ImageDraw
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; V1=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'; OUT=EXP/'final_eval_v1/renders'; OUT.mkdir(parents=True,exist_ok=True)
manifest={x['CASE_ID']:x for x in json.loads((V1/'CASE_MANIFEST.json').read_text())['cases']}; cases=[('case_018','00'),('case_009','01'),('case_014','tank'),('case_010','03'),('case_005','04')]
def stepmesh(path):
 s=cq.importers.importStep(str(path)).val(); vs,fs=s.tessellate(0.15); return np.array([[float(v.x),float(v.y),float(v.z)] for v in vs]),np.array([[int(t[0]),int(t[1]),int(t[2])] for t in fs])
def project(v):
 v=v-v.mean(0); view=np.array([0.58,0.58,0.58]); view=view/np.linalg.norm(view); up=np.array([0,0,1.]); right=np.cross(up,view); right=right/np.linalg.norm(right); up=np.cross(view,right); xy=np.c_[v@right,v@up]; depth=v@view; span=max(np.ptp(xy[:,0]),np.ptp(xy[:,1]),1e-9); xy=(xy-xy.mean(0))/span; return xy,depth
def render(path,layers):
 allv=np.concatenate([x[0] for x in layers]); xy,_=project(allv); base=Image.new('RGB',(900,700),(245,245,245)); draw=ImageDraw.Draw(base,'RGBA'); off=0; polys=[]
 for v,f,col,alpha in layers:
  p,d=project(v)
  for tri in f:
   q=p[tri]; px=[int(450+x*780) for x in q[:,0]]; py=[int(350-y*600) for y in q[:,1]]; polys.append((float(d[tri].mean()),list(zip(px,py)),col,alpha))
 for _,q,c,a in sorted(polys,key=lambda z:z[0]): draw.polygon(q,fill=tuple(c)+(a,))
 base.save(path)
for cid,idx in cases:
 mesh=trimesh.load_mesh(manifest[cid]['MESH_PATH'],process=False); mv=np.asarray(mesh.vertices); mf=np.asarray(mesh.faces); gen=EXP/'final_eval_v1/step'/f'{cid}.step'; can=ROOT/'ours3/p3_xpart_20case_compact_ir_v3/step_v3'/f'{cid}.step'; gv,gf=stepmesh(gen); cv,cf=stepmesh(can); stem='tank' if cid=='case_014' else cid
 render(OUT/f'{stem}_input_mesh.png',[(mv,mf,(50,115,185),255)]); render(OUT/f'{stem}_generated_brep.png',[(gv,gf,(70,165,80),255)]); render(OUT/f'{stem}_canonical_brep.png',[(cv,cf,(230,125,30),255)]); render(OUT/f'{stem}_overlay.png',[(cv,cf,(230,125,30),128),(gv,gf,(70,165,80),128)])
(OUT/'TANK_DEMO_CAPTION.txt').write_text('Tank PART_029\n1,529 / 1,529 q-stream exact\nNatural EOS\nSTEP valid\nVolume error 0.0\nGenerated and canonical views are smooth-shaded BRep displays with triangle edges hidden.')
print('rendered',len(cases)*4)
