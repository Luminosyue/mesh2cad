import json
from pathlib import Path
import numpy as np, trimesh, cadquery as cq
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; V1=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'; OUT=EXP/'final_eval_v1/renders'; OUT.mkdir(parents=True,exist_ok=True)
manifest={x['CASE_ID']:x for x in json.loads((V1/'CASE_MANIFEST.json').read_text())['cases']}; cases=[('case_018','00'),('case_009','01'),('case_014','tank'),('case_010','03'),('case_005','04')]
def tris_from_step(path):
    s=cq.importers.importStep(str(path)).val(); vs,fs=s.tessellate(0.15); return np.array([[float(v.x),float(v.y),float(v.z)] for v in vs]),np.array([[int(t[0]),int(t[1]),int(t[2])] for t in fs])
def draw(path, layers, title):
    fig=plt.figure(figsize=(8,6),dpi=130); ax=fig.add_subplot(111,projection='3d')
    allv=[]
    for verts,faces,color,alpha in layers:
        allv.append(verts); poly=Poly3DCollection(verts[faces],facecolor=color,edgecolor='none',linewidth=0,alpha=alpha); ax.add_collection3d(poly)
    v=np.concatenate(allv); lo=v.min(0); hi=v.max(0); mid=(lo+hi)/2; span=max(hi-lo); ax.set_xlim(mid[0]-span/2,mid[0]+span/2); ax.set_ylim(mid[1]-span/2,mid[1]+span/2); ax.set_zlim(mid[2]-span/2,mid[2]+span/2); ax.view_init(elev=24,azim=35); ax.set_axis_off(); ax.set_title(title); plt.tight_layout(); fig.savefig(path,bbox_inches='tight'); plt.close(fig)
for cid,idx in cases:
    mesh=trimesh.load_mesh(manifest[cid]['MESH_PATH'],process=False); mv=np.asarray(mesh.vertices); mf=np.asarray(mesh.faces); genpath=EXP/'final_eval_v1/step'/f'{cid}.step' if cid!='case_014' else EXP/'final_eval_v1/step/case_014.step'; canpath=ROOT/'ours3/p3_xpart_20case_compact_ir_v3/step_v3'/f'{cid}.step'; gv,gf=tris_from_step(genpath); cv,cf=tris_from_step(canpath)
    stem='tank' if cid=='case_014' else cid
    draw(OUT/f'{stem}_input_mesh.png',[(mv,mf,'#4c78a8',1.0)],f'{cid} input mesh')
    draw(OUT/f'{stem}_generated_brep.png',[(gv,gf,'#59a14f',1.0)],f'{cid} generated smooth BRep')
    draw(OUT/f'{stem}_canonical_brep.png',[(cv,cf,'#f28e2b',1.0)],f'{cid} canonical smooth BRep')
    draw(OUT/f'{stem}_overlay.png',[(cv,cf,'#f28e2b',0.5),(gv,gf,'#59a14f',0.5)],f'{cid} generated / canonical overlay')
(OUT/'TANK_DEMO_CAPTION.txt').write_text('Tank PART_029\n1,529 / 1,529 q-stream exact\nNatural EOS\nSTEP valid\nVolume error 0.0\nGenerated and canonical renders use tessellated display of smooth BRep with triangle edges hidden.')
print('rendered',len(cases)*4)
