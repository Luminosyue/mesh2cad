from pathlib import Path
import numpy as np, trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results/samples/tank/xpart_parts')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results/visualization'); OUT.mkdir(parents=True,exist_ok=True)
def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=trimesh.util.concatenate(tuple(m.geometry.values()))
    m.remove_unreferenced_vertices(); return m
def edges(m,ang=25,maxn=260):
    try:
        e=m.face_adjacency_edges[np.degrees(m.face_adjacency_angles)>=ang]
    except: e=np.empty((0,2),int)
    try:
        eu=m.edges_unique; cnt=np.bincount(m.edges_unique_inverse,minlength=len(eu)); b=eu[cnt==1]
    except: b=np.empty((0,2),int)
    if len(e)>maxn:
        d=np.linalg.norm(m.vertices[e[:,0]]-m.vertices[e[:,1]],axis=1); e=e[np.argsort(d)[-maxn:]]
    if len(b)>maxn//2:
        d=np.linalg.norm(m.vertices[b[:,0]]-m.vertices[b[:,1]],axis=1); b=b[np.argsort(d)[-(maxn//2):]]
    return e,b
def tris(m,n=1700):
    f=m.faces if len(m.faces)<=n else m.faces[np.linspace(0,len(m.faces)-1,n,dtype=int)]
    return m.vertices[f]
def setup(ax,m):
    lo=m.vertices.min(axis=0); hi=m.vertices.max(axis=0); c=(lo+hi)/2; e=max(hi-lo)*.62
    ax.set_xlim(c[0]-e,c[0]+e); ax.set_ylim(c[1]-e,c[1]+e); ax.set_zlim(c[2]-e,c[2]+e); ax.set_box_aspect((1,1,1)); ax.view_init(25,38); ax.set_axis_off()
parts=[]; ids=[]
for p in sorted(ROOT.glob('PART_*'),key=lambda p:int(p.name.split('_')[1])):
    if (p/'cad_rebuilt.stl').exists(): ids.append(p.name); parts.append(load(p/'cad_rebuilt.stl'))
maxsize=max(max(m.extents) for m in parts); spacing=maxsize*2.25
cols=9; rows=(len(parts)+cols-1)//cols
fig=plt.figure(figsize=(18,10),facecolor='#F4F7FA')
for i,(pid,m) in enumerate(zip(ids,parts)):
    mm=m.copy(); mm.apply_translation(-mm.bounds.mean(axis=0))
    x=(i%cols-(cols-1)/2)*spacing; y=((rows-1)//2-i//cols)*spacing; z=(i%2)*maxsize*.35
    mm.apply_translation([x,y,z])
    ax=fig.add_subplot(rows,cols,i+1,projection='3d')
    ax.add_collection3d(Poly3DCollection(tris(mm),facecolor='#4EA8DE',edgecolor='none',alpha=.83))
    e,b=edges(mm)
    if len(e): ax.add_collection3d(Line3DCollection([mm.vertices[x] for x in e],colors='#D62728',linewidths=1.1,alpha=.95))
    if len(b): ax.add_collection3d(Line3DCollection([mm.vertices[x] for x in b],colors='#F4B942',linewidths=1.2,alpha=.95))
    setup(ax,mm); ax.set_title(pid.replace('PART_','P'),fontsize=8,pad=1)
fig.suptitle('Tank 45-part exploded catalog: CAD surfaces and marked edges',fontsize=18,fontweight='bold',y=.997)
fig.text(.5,.006,'Each part is separated into a catalog grid. Red = sharp/curve feature edges; yellow = open boundary edges.',ha='center',fontsize=10,color='#3E4C59')
fig.tight_layout(rect=[0,.012,1,.985]); fig.savefig(OUT/'tank_exploded_grid_surface_edges.png',dpi=220,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)
print('wrote',OUT/'tank_exploded_grid_surface_edges.png')

