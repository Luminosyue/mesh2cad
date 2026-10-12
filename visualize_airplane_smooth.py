from pathlib import Path
import json, numpy as np, trimesh
from PIL import Image, ImageDraw
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
SRC=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/visualizations')
OUT.mkdir(parents=True,exist_ok=True)

def load(p):
 m=trimesh.load(p,force='mesh',process=False)
 if isinstance(m,trimesh.Scene):m=m.to_mesh()
 m.merge_vertices();m.remove_unreferenced_vertices();return m

def prep(m,maxf):
 f=np.asarray(m.faces)
 if len(f)>maxf:f=f[np.linspace(0,len(f)-1,maxf).astype(int)]
 ids=np.unique(f);rem=-np.ones(len(m.vertices),int);rem[ids]=np.arange(len(ids))
 return np.asarray(m.vertices)[ids],rem[f]

def static():
 source=load(next((SRC/'airplane'/'source').glob('*')))
 rows=[]
 for p in sorted((ROOT/'cases'/'airplane').glob('*/metrics.json')):
  d=json.loads(p.read_text())
  if '/xpart_parts/' in d.get('source_path',''):
   rows.append((d['part_id'],load(p.parent/'reconstructed.stl')))
 cam=np.array([2.4,-3,2.0]);cam/=np.linalg.norm(cam);right=np.cross([0,0,1],cam);right/=np.linalg.norm(right);up=np.cross(cam,right);R=np.stack([right,up,cam],1)
 fig,axs=plt.subplots(1,3,figsize=(19,7),facecolor='#f4f7fb')
 def add(ax,m,color,alpha,maxf):
  v,f=prep(m,maxf);q=v@R;tri=q[f][:,:,:2];z=q[f][:,:,2].mean(1);o=np.argsort(z)
  base=np.array(matplotlib.colors.to_rgb(color));fc=np.column_stack([np.tile(base,(len(f),1)),np.full(len(f),alpha)])
  ax.add_collection(PolyCollection(tri[o],facecolors=fc[o],edgecolors='none'))
 allm=[source]+[m for _,m in rows];xy=np.concatenate([(m.vertices@R)[:,:2] for m in allm]);lo=xy.min(0);hi=xy.max(0);pad=max(hi-lo)*.05
 add(axs[0],source,'#8996a3',.35,30000)
 for i,(pid,m) in enumerate(rows):add(axs[1],m,plt.cm.tab20((i%20)/19),.9,5000)
 add(axs[2],source,'#8996a3',.25,30000)
 for i,(pid,m) in enumerate(rows):add(axs[2],m,plt.cm.tab20((i%20)/19),.8,5000)
 for ax,title in zip(axs,['COMPLETE AIRPLANE SOURCE','9-PART X-PART CAD ASSEMBLY','SOURCE / CAD OVERLAY']):
  ax.set_xlim(lo[0]-pad,hi[0]+pad);ax.set_ylim(lo[1]-pad,hi[1]+pad);ax.set_aspect('equal');ax.set_axis_off();ax.set_facecolor('#f4f7fb');ax.set_title(title,fontsize=15,fontweight='bold')
 fig.suptitle('Airplane · X-Part assembly visualization',fontsize=22,fontweight='bold')
 fig.text(.5,.025,'Gray = complete source airplane; colored = 9 X-Part CAD components. PART_000 smooth B-spline validated: 3 faces, IoU128=0.9818.',ha='center',fontsize=10)
 fig.subplots_adjust(left=.01,right=.99,top=.86,bottom=.09,wspace=.03)
 fig.savefig(OUT/'airplane_smooth_assembly_visualization.png',dpi=220,bbox_inches='tight');plt.close(fig)
 return source,rows

def html(source,rows):
 fig=go.Figure()
 def trace(name,m,color,opacity,maxf):
  v,f=prep(m,maxf);return go.Mesh3d(x=v[:,0],y=v[:,1],z=v[:,2],i=f[:,0],j=f[:,1],k=f[:,2],name=name,color=color,opacity=opacity,flatshading=True)
 fig.add_trace(trace('Complete original airplane',source,'#8996a3',.25,18000))
 pal=px.colors.qualitative.Set3+px.colors.qualitative.Dark24
 for i,(pid,m) in enumerate(rows):fig.add_trace(trace(pid,m,pal[i%len(pal)],.9,3500))
 n=1+len(rows); allv=[True]*n; cad=[False]+[True]*len(rows); src=[True]+[False]*len(rows)
 fig.update_layout(template='plotly_dark',height=820,title='Airplane · 9-part X-Part CAD assembly + complete body',scene=dict(aspectmode='data',camera=dict(eye=dict(x=1.45,y=-1.7,z=1.0)),xaxis_title='X',yaxis_title='Y',zaxis_title='Z'),showlegend=False,updatemenus=[dict(type='buttons',x=.02,y=1.06,buttons=[dict(label='CAD + body',method='update',args=[{'visible':allv}]),dict(label='CAD only',method='update',args=[{'visible':cad}]),dict(label='Original body',method='update',args=[{'visible':src}])])])
 (OUT/'airplane_smooth_assembly_visualization.html').write_text(fig.to_html(full_html=True,include_plotlyjs=True,config={'responsive':True,'scrollZoom':True,'displaylogo':False}),encoding='utf-8')

if __name__=='__main__':
 s,r=static();html(s,r)

