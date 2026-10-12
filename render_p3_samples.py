import csv, os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

P3 = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results')
MAN = OUT/'all_manifest.csv'
DEST = OUT/'visualization'
DEST.mkdir(parents=True, exist_ok=True)

def load(path):
    x = trimesh.load(path, force='mesh', process=False)
    if isinstance(x, trimesh.Scene):
        x = trimesh.util.concatenate(tuple(g for g in x.geometry.values()))
    return x

def sample(mesh, n=4500):
    if len(mesh.faces) <= n: return mesh
    idx = np.linspace(0, len(mesh.faces)-1, n, dtype=int)
    return trimesh.Trimesh(vertices=mesh.vertices.copy(), faces=mesh.faces[idx], process=False)

def draw(ax, mesh, color):
    m = sample(mesh)
    tri = m.triangles
    p = Poly3DCollection(tri, facecolor=color, edgecolor='none', linewidth=0, alpha=0.96)
    ax.add_collection3d(p)
    mins, maxs = m.bounds
    c = (mins + maxs)/2
    e = max(maxs-mins)*0.55
    ax.set_xlim(c[0]-e,c[0]+e); ax.set_ylim(c[1]-e,c[1]+e); ax.set_zlim(c[2]-e,c[2]+e)
    ax.set_box_aspect((1,1,1)); ax.view_init(elev=24, azim=38)
    ax.set_axis_off()

rows=[]
with open(MAN, newline='') as f:
    for r in csv.DictReader(f):
        if r.get('status') != 'kept': continue
        src = P3 / r['source']
        base = OUT / r['output']
        cad = base/'cad_rebuilt.stl'
        if src.exists() and cad.exists():
            rows.append((r,src,cad))

# Use a spread of cases, including the first and several different object families.
pick=[]
for key in ['tank/','robot/','toaster/','vase/','school_bus/','airplane/']:
    for x in rows:
        if key in x[0]['source']:
            pick.append(x); break
for x in rows:
    if len(pick)>=6: break
    if x not in pick: pick.append(x)
pick=pick[:6]

fig, axes = plt.subplots(len(pick), 2, figsize=(9, 3.0*len(pick)), subplot_kw={'projection':'3d'})
if len(pick)==1: axes=np.array([axes])
for i,(r,src,cad) in enumerate(pick):
    sm=load(src); cm=load(cad)
    draw(axes[i,0], sm, '#E69F00'); draw(axes[i,1], cm, '#0072B2')
    name=r['source'].replace('/xpart_parts/','/').replace('.stl','')
    iou=r.get('volume_iou_64') or r.get('surface_iou_64') or ''
    axes[i,0].set_title(f'Original mesh\n{name}', fontsize=10, pad=2)
    axes[i,1].set_title(f'Generated CAD\nIoU={iou}', fontsize=10, pad=2)
fig.suptitle('P3 XPart: original mesh vs reconstructed CAD', fontsize=16, fontweight='bold', y=0.995)
fig.text(0.5,0.004,'Orange = source mesh    Blue = CAD rebuilt from generated code/STEP',ha='center',fontsize=10,color='#44546A')
fig.tight_layout(rect=[0,0.02,1,0.98])
fig.savefig(DEST/'mesh_vs_cad_samples.png', dpi=180, bbox_inches='tight', facecolor='#F5F7FA')
print('wrote', DEST/'mesh_vs_cad_samples.png', 'samples', [r['source'] for r,_,_ in pick])
