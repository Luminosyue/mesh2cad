from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); TANK=ROOT/'p3_xpart_open_cases/tank'; OUT=ROOT/'ours3/case_part_visualization_v1/renders/contact_sheets'; OUT.mkdir(parents=True,exist_ok=True)
FONT=ImageFont.load_default(); W,H=1600,1200
def step_mesh(path):
 r=STEPControl_Reader(); assert r.ReadFile(str(path))==IFSelect_RetDone; assert r.TransferRoots()>0; s=r.OneShape(); BRepMesh_IncrementalMesh(s,.12,False,.35,True).Perform(); vs=[];fs=[];off=0; ex=TopExp_Explorer(s,TopAbs_FACE)
 while ex.More():
  loc=TopLoc_Location(); t=BRep_Tool.Triangulation_s(TopoDS.Face_s(ex.Current()),loc)
  if t:
   tr=loc.Transformation(); vv=[]
   for i in range(1,t.NbNodes()+1):
    p=t.Node(i).Transformed(tr); vv.append([p.X(),p.Y(),p.Z()])
   vs+=vv
   for i in range(1,t.NbTriangles()+1):
    a,b,c=t.Triangle(i).Get(); fs.append([off+a-1,off+b-1,off+c-1])
   off+=len(vv)
  ex.Next()
 return np.asarray(vs,float),np.asarray(fs,int)
parts=[]
for i in range(45):
 p=TANK/'xpart_parts_cadquery_features'/f'PART_{i:03d}'/f'PART_{i:03d}.step'; parts.append((*step_mesh(p),p))
allv=np.vstack([x[0] for x in parts]); bounds=np.array([allv.min(0),allv.max(0)])
az,el=np.radians(35),np.radians(24); rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]]); rx=np.array([[1,0,0],[0,np.cos(el),np.sin(el)],[0,-np.sin(el),np.cos(el)]]); R=rx@rz; q=bounds@R.T; mid=(q[:,:2].min(0)+q[:,:2].max(0))/2; span=max(q[:,:2].max(0)-q[:,:2].min(0))*1.08
def xy(v):
 p=v@R.T; return np.c_[((p[:,0]-mid[0])/span+.5)*(W-80)+40,(.5-(p[:,1]-mid[1])/span)*(H-100)+40],p[:,2]
def shade(v,b):
 n=np.cross(v[1]-v[0],v[2]-v[0]); n/=np.linalg.norm(n)+1e-12; l=np.array([.35,.5,.8]); l/=np.linalg.norm(l); k=.42+.58*abs(float(n@l)); return tuple(int(min(255,max(0,c*k))) for c in b)
pal=[(45+(i*53)%170,75+(i*71)%150,110+(i*97)%120) for i in range(45)]
im=Image.new('RGBA',(W,H),(249,250,252,255)); d=ImageDraw.Draw(im)
for i,(v,f,_) in enumerate(parts):
 u,z=xy(v); ff=f if len(f)<12000 else f[np.linspace(0,len(f)-1,12000).astype(int)]
 for j in np.argsort(z[ff].mean(1)): d.polygon([tuple(u[k]) for k in ff[j]],fill=shade(v[ff[j]],pal[i])+(225,))
 d.text(tuple(xy(v.mean(0,keepdims=True))[0][0]),f'{i:02d}',fill=(15,20,25),font=FONT)
d.rectangle((25,20,570,58),fill=(255,255,255,230)); d.text((40,32),'Tank | 45-part canonical CAD BRep overview',fill=(20,30,40),font=FONT); im.convert('RGB').save(OUT/'tank_45_parts_cad_overview.png')
cw,ch=320,245; cols=5; sheet=Image.new('RGB',(cw*cols,ch*9+42),(255,255,255)); sd=ImageDraw.Draw(sheet); sd.text((14,14),'Tank | 45-part canonical CAD BRep contact sheet',fill=(20,30,40),font=FONT)
for i,(v,f,_) in enumerate(parts):
 u,z=xy(v); xmin,xmax=u[:,0].min(),u[:,0].max(); ymin,ymax=u[:,1].min(),u[:,1].max(); local=np.c_[((u[:,0]-xmin)/max(xmax-xmin,1e-9))*(cw-18)+9,((u[:,1]-ymin)/max(ymax-ymin,1e-9))*(ch-30)+8]; x=(i%cols)*cw; y=42+(i//cols)*ch; ff=f if len(f)<3500 else f[np.linspace(0,len(f)-1,3500).astype(int)]
 for j in ff: sd.polygon([tuple(local[k]+[x,y]) for k in j],fill=(78,145,96))
 sd.text((x+8,y+ch-20),f'PART_{i:03d} | CAD BRep',fill=(20,30,40),font=FONT)
sheet.save(OUT/'tank_45_parts_cad_contact_sheet.png'); print('rendered canonical CAD',len(parts))
