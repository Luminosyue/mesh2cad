from pathlib import Path
import numpy as np, trimesh, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

BASE=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases_cad_results')
SRC=BASE/'samples/tank/xpart_parts'; OUT=BASE/'visualization/tank_curve_style'; (OUT/'parts').mkdir(parents=True,exist_ok=True)

def load(p):
    m=trimesh.load(p,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=trimesh.util.concatenate(tuple(m.geometry.values()))
    m.merge_vertices(); m.remove_unreferenced_vertices(); return m
def curve_edges(m,threshold=27,maxn=1100):
    a=np.degrees(m.face_adjacency_angles); e=m.face_adjacency_edges[a>=threshold]
    if len(e)>maxn:
        d=np.linalg.norm(m.vertices[e[:,0]]-m.vertices[e[:,1]],axis=1); e=e[np.argsort(d)[-maxn:]]
    return e
def triangles(m,n=5000):
    f=m.faces if len(m.faces)<=n else m.faces[np.linspace(0,len(m.faces)-1,n,dtype=int)]
    return m.vertices[f]
def limits(m):
    lo=m.vertices.min(0); hi=m.vertices.max(0); c=(lo+hi)/2; r=max(hi-lo)*.58
    return c-r,c+r
def render(ax,m,view,only_lines=False,threshold=27):
    v=m.vertices; f=m.faces; lo,hi=limits(m)
    if not only_lines:
        tri=triangles(m); n=m.face_normals[:len(tri)] if len(tri)==len(m.faces) else np.ones(len(tri))
        # cyan shaded planar surfaces, with light edge-free rendering
        ax.add_collection3d(Poly3DCollection(tri,facecolor='#61B5DB',edgecolor='none',alpha=.93))
    e=curve_edges(m,threshold)
    if len(e): ax.add_collection3d(Line3DCollection([v[x] for x in e],colors='#173F5F',linewidths=1.0 if only_lines else .72,alpha=.95))
    c=(lo+hi)/2; ax.set_xlim(c[0]-(hi-lo).max()*.58,c[0]+(hi-lo).max()*.58); ax.set_ylim(c[1]-(hi-lo).max()*.58,c[1]+(hi-lo).max()*.58); ax.set_zlim(c[2]-(hi-lo).max()*.58,c[2]+(hi-lo).max()*.58)
    ax.set_box_aspect((1,1,1)); ax.view_init(*view); ax.set_axis_off()
def panel(pid,m):
    fig=plt.figure(figsize=(16,11),facecolor='#F1F6FA')
    views=[(25,38),(25,-52),(72,0),(-70,0)]
    titles=['Surface + boundary curves','Boundary curves only','Top view: surface + curves','Bottom view: surface + curves']
    for i,(v,title) in enumerate(zip(views,titles)):
        ax=fig.add_subplot(2,2,i+1,projection='3d'); render(ax,m,v,only_lines=(i==1),threshold=27); ax.set_title(title,fontsize=16,color='#173F5F',pad=7)
    fig.suptitle(f'{pid} CAD | surface boundary curves',fontsize=24,fontweight='bold',color='#173F5F',x=.04,ha='left',y=.98)
    fig.text(.04,.94,'Surface + boundary curves / curves only',fontsize=15,color='#173F5F')
    fig.text(.04,.018,'Blue curves: connected tessellated edges with dihedral angle >= 27 deg; STEP is faceted CAD, not analytic NURBS.',fontsize=10,color='#52697A')
    fig.subplots_adjust(left=.02,right=.98,top=.88,bottom=.05,wspace=.02,hspace=.08)
    fig.savefig(OUT/f'{pid}_curve_style.png',dpi=210,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)
parts=[]
for p in sorted(SRC.glob('PART_*'),key=lambda q:int(q.name[-3:])):
    if (p/'cad_rebuilt.stl').exists(): parts.append((p.name,load(p/'cad_rebuilt.stl')))
panel('PART_005',dict(parts)[ 'PART_005'])
for page in range(3):
    fig=plt.figure(figsize=(16,10),facecolor='#F1F6FA')
    for j,(pid,m) in enumerate(parts[page*15:(page+1)*15]):
        ax=fig.add_subplot(3,5,j+1,projection='3d'); render(ax,m,(25,38),False,27); ax.set_title(pid,fontsize=10,color='#173F5F',pad=1)
    fig.suptitle(f'Tank parts 路 CAD surfaces + continuous feature curves 路 {page+1}/3',fontsize=18,fontweight='bold',color='#173F5F')
    fig.text(.5,.01,'Blue lines: selected high-curvature / surface-transition edges (27掳 threshold).',ha='center',fontsize=10,color='#52697A')
    fig.subplots_adjust(left=.02,right=.98,top=.92,bottom=.04,wspace=.03,hspace=.18)
    fig.savefig(OUT/f'parts_curve_sheet_{page+1}.png',dpi=190,bbox_inches='tight',facecolor=fig.get_facecolor()); plt.close(fig)
meta={'parts':len(parts),'threshold_deg':27,'description':'feature curve polylines from tessellated mesh dihedral edges; no analytic curve fitting'}
(OUT/'README.txt').write_text('Tank curve-style visualization. The STEP outputs are faceted triangle CAD, so the blue lines are connected tessellated feature/transition edges selected by dihedral angle >= 27 degrees. They approximate the requested surface-boundary curves; they are not analytic NURBS curves.\n')
(OUT/'curve_render_meta.json').write_text(json.dumps(meta,indent=2))
print('rendered',len(parts),OUT)

