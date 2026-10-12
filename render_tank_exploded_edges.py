from pathlib import Path
import math
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results/samples/tank/xpart_parts')
OUT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results/visualization')
OUT.mkdir(parents=True, exist_ok=True)

def load(p):
    m = trimesh.load(p, force='mesh', process=False)
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    m.remove_unreferenced_vertices()
    return m

def feature_edges(m, angle_deg=25.0, max_edges=380):
    edges=[]; boundary=[]
    try:
        ae = m.face_adjacency_edges
        ang = np.degrees(m.face_adjacency_angles)
        edges = ae[ang >= angle_deg]
    except Exception:
        edges = np.empty((0,2), dtype=int)
    try:
        eu = m.edges_unique
        inv = m.edges_unique_inverse
        counts = np.bincount(inv, minlength=len(eu))
        boundary = eu[counts == 1]
    except Exception:
        boundary = np.empty((0,2), dtype=int)
    # Keep the longest/highest-contrast edges for legibility.
    if len(edges) > max_edges:
        d = m.vertices[edges[:,0]] - m.vertices[edges[:,1]]
        keep = np.argsort(np.linalg.norm(d, axis=1))[-max_edges:]
        edges = edges[keep]
    if len(boundary) > max_edges//2:
        d = m.vertices[boundary[:,0]] - m.vertices[boundary[:,1]]
        keep = np.argsort(np.linalg.norm(d, axis=1))[-max_edges//2:]
        boundary = boundary[keep]
    return edges, boundary

def tris_for(m, limit=1400):
    if len(m.faces) <= limit: return m.triangles
    idx = np.linspace(0, len(m.faces)-1, limit, dtype=int)
    return m.vertices[m.faces[idx]]

def bounds_all(parts):
    b = np.vstack([m.bounds for m in parts])
    return b.min(axis=0), b.max(axis=0)

def setup(ax, lo, hi, elev=25, azim=38):
    c=(lo+hi)/2; e=max(hi-lo)*0.54
    ax.set_xlim(c[0]-e,c[0]+e); ax.set_ylim(c[1]-e,c[1]+e); ax.set_zlim(c[2]-e,c[2]+e)
    ax.set_box_aspect((1,1,1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()

ids=[]; parts=[]
for p in sorted(ROOT.glob('PART_*'), key=lambda x:int(x.name.split('_')[1])):
    stl=p/'cad_rebuilt.stl'
    if not stl.exists(): stl=p/'mesh_decimated.stl'
    if stl.exists(): ids.append(p.name); parts.append(load(stl))

# Explode from the assembly center: preserve world arrangement and add a deterministic radial offset.
lo,hi=bounds_all(parts); assembly_c=(lo+hi)/2; diag=np.linalg.norm(hi-lo)
exploded=[]
for i,m in enumerate(parts):
    c=m.bounds.mean(axis=0)
    v=c-assembly_c; n=np.linalg.norm(v)
    direction=v/n if n>1e-8 else np.array([0.,0.,1.])
    a=2*math.pi*i/max(1,len(parts)); ring=np.array([math.cos(a),math.sin(a),0.25*math.sin(2*a)])
    offset=direction*(0.65*diag) + ring*(0.42*diag)
    exploded.append(m.copy())
    exploded[-1].apply_translation(offset)

# 1) Overall exploded view with surfaces and marked feature/curve edges.
fig=plt.figure(figsize=(15,11), facecolor='#F4F7FA'); ax=fig.add_subplot(111, projection='3d')
elo,ehi=bounds_all(exploded)
colors=plt.cm.tab20(np.linspace(0,1,len(parts)))
for i,(pid,m,col) in enumerate(zip(ids,exploded,colors)):
    ax.add_collection3d(Poly3DCollection(tris_for(m), facecolor=col, edgecolor='none', alpha=0.76))
    sharp,bound=feature_edges(m)
    for ed,c,lw in [(sharp,'#D62728',1.15),(bound,'#FFD166',1.45)]:
        if len(ed):
            seg=[m.vertices[e] for e in ed]
            ax.add_collection3d(Line3DCollection(seg, colors=c, linewidths=lw, alpha=0.92))
    c=m.bounds.mean(axis=0); ax.text(c[0],c[1],c[2],pid.replace('PART_','P'),fontsize=7,color='#202020',ha='center',va='center')
setup(ax,elo,ehi,28,38)
ax.set_title('Tank 45-part exploded CAD view: surfaces + marked curve/feature edges',fontsize=18,fontweight='bold',pad=18)
fig.text(0.5,0.018,'Filled color = CAD surface    Red = sharp/curve feature edges    Yellow = open boundary edges',ha='center',fontsize=11,color='#3E4C59')
fig.savefig(OUT/'tank_exploded_cad_surface_edges.png',dpi=220,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)

# 2) 45-part contact sheet, each panel shows surface and marked edges.
cols=5; rows=math.ceil(len(parts)/cols)
fig=plt.figure(figsize=(18,3.25*rows),facecolor='#F4F7FA')
for i,(pid,m) in enumerate(zip(ids,parts)):
    ax=fig.add_subplot(rows,cols,i+1,projection='3d')
    lo2,hi2=m.bounds
    ax.add_collection3d(Poly3DCollection(tris_for(m,1100),facecolor='#58B7D4',edgecolor='none',alpha=0.82))
    sharp,bound=feature_edges(m,25,180)
    if len(sharp): ax.add_collection3d(Line3DCollection([m.vertices[e] for e in sharp],colors='#D62728',linewidths=1.0,alpha=.95))
    if len(bound): ax.add_collection3d(Line3DCollection([m.vertices[e] for e in bound],colors='#F4B942',linewidths=1.15,alpha=.95))
    setup(ax,lo2,hi2,24,38); ax.set_title(pid,fontsize=8,pad=1)
fig.suptitle('Tank components: CAD surfaces with highlighted curve/feature edges',fontsize=18,fontweight='bold',y=.997)
fig.text(0.5,0.004,'Red = sharp/curve feature edges    Yellow = boundary edges',ha='center',fontsize=10,color='#3E4C59')
fig.tight_layout(rect=[0,0.01,1,0.985])
fig.savefig(OUT/'tank_all_parts_surface_curve_edges.png',dpi=190,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)

# 3) Two-panel exploded source-vs-CAD overview, with CAD edges on the right.
srcparts=[]
srcroot=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases/tank/xpart_parts')
for i in range(len(parts)):
    p=srcroot/f'PART_{i:03d}.stl'
    if p.exists(): srcparts.append(load(p))
    else: srcparts.append(None)
fig=plt.figure(figsize=(16,8),facecolor='#F4F7FA')
for panel,(title,ms,draw_edges) in enumerate([('Source mesh exploded',srcparts,False),('Generated CAD exploded + edges',exploded,True)]):
    ax=fig.add_subplot(1,2,panel+1,projection='3d')
    valid=[m for m in ms if m is not None]
    if panel==0:
        ex=[]
        for i,m in enumerate(valid):
            mm=m.copy(); c=mm.bounds.mean(axis=0); v=c-assembly_c; n=np.linalg.norm(v); d=v/n if n>1e-8 else np.array([0.,0.,1.]); a=2*math.pi*i/max(1,len(valid)); mm.apply_translation(d*(.65*diag)+np.array([math.cos(a),math.sin(a),.25*math.sin(2*a)])*(.42*diag)); ex.append(mm)
        ms=ex
    for i,m in enumerate(ms):
        if m is None: continue
        ax.add_collection3d(Poly3DCollection(tris_for(m,900),facecolor=colors[i%len(colors)],edgecolor='none',alpha=.78))
        if draw_edges:
            sharp,bound=feature_edges(m,25,120)
            if len(sharp): ax.add_collection3d(Line3DCollection([m.vertices[e] for e in sharp],colors='#D62728',linewidths=.9,alpha=.9))
            if len(bound): ax.add_collection3d(Line3DCollection([m.vertices[e] for e in bound],colors='#FFD166',linewidths=1,alpha=.9))
    vv=[m for m in ms if m is not None]; l,h=bounds_all(vv); setup(ax,l,h,28,38); ax.set_title(title,fontsize=15,fontweight='bold',pad=10)
fig.text(0.5,0.02,'Red/yellow edge marks are shown on the generated CAD panel.',ha='center',fontsize=10,color='#3E4C59')
fig.tight_layout(rect=[0,0.04,1,1]); fig.savefig(OUT/'tank_exploded_source_vs_cad_edges.png',dpi=210,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)
print('parts',len(parts)); print('outputs',OUT/'tank_exploded_cad_surface_edges.png',OUT/'tank_all_parts_surface_curve_edges.png',OUT/'tank_exploded_source_vs_cad_edges.png')
