import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); TANK=ROOT/'p3_xpart_open_cases/tank'; OUT=ROOT/'ours3/case_part_visualization_v1/renders/contact_sheets'; OUT.mkdir(parents=True,exist_ok=True)
W,H=1600,1200; FONT=ImageFont.load_default()
paths=sorted((TANK/'p3_parts').glob('part_*.obj'))
def read_obj(p):
 v=[];f=[]
 for s in p.read_text(errors='ignore').splitlines():
  if s.startswith('v '): v.append([float(x) for x in s.split()[1:4]])
  elif s.startswith('f '):
   q=[int(x.split('/')[0])-1 for x in s.split()[1:]]
   for i in range(1,len(q)-1): f.append([q[0],q[i],q[i+1]])
 return np.asarray(v,float),np.asarray(f,int)
parts=[read_obj(p) for p in paths]; allv=np.vstack([x[0] for x in parts]); lo=allv.min(0);hi=allv.max(0); bounds=np.array([lo,hi])
az,el=np.radians(35),np.radians(24); rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]]); rx=np.array([[1,0,0],[0,np.cos(el),np.sin(el)],[0,-np.sin(el),np.cos(el)]]); R=rx@rz
q=bounds@R.T; mid=(q[:,:2].min(0)+q[:,:2].max(0))/2; span=max(q[:,:2].max(0)-q[:,:2].min(0))*1.08
def xy(v):
 p=v@R.T; z=p[:,2]; u=np.c_[(p[:,0]-mid[0])/span+.5,.5-(p[:,1]-mid[1])/span]; return u*np.array([W-80,H-100])+40,z
palette=[(55+(i*47)%170,85+(i*71)%145,115+(i*97)%120) for i in range(45)]
im=Image.new('RGBA',(W,H),(249,250,252,255)); d=ImageDraw.Draw(im)
for i,(v,f) in enumerate(parts):
 u,z=xy(v); ff=f
 if len(ff)>9000: ff=ff[np.linspace(0,len(ff)-1,9000).astype(int)]
 for j in np.argsort(z[ff].mean(1)):
  poly=[tuple(u[k]) for k in ff[j]]; d.polygon(poly,fill=palette[i]+(205,))
 d.text((int(u[:,0].mean()),int(u[:,1].mean())),f'{i:02d}',fill=(20,25,30),font=FONT)
d.rectangle((25,20,500,58),fill=(255,255,255,230));d.text((40,32),'Tank | 45-part assembled input mesh overview',fill=(20,30,40),font=FONT);im.convert('RGB').save(OUT/'tank_45_parts_overview.png')

cw,ch=320,245; cols,rows=5,9; sheet=Image.new('RGB',(cw*cols,ch*rows+42),(255,255,255));sd=ImageDraw.Draw(sheet);sd.text((14,14),'Tank | 45-part input mesh contact sheet',fill=(20,30,40),font=FONT)
for i,(v,f) in enumerate(parts):
 pxy,pz=xy(v); xmin, xmax=pxy[:,0].min(),pxy[:,0].max(); ymin,ymax=pxy[:,1].min(),pxy[:,1].max(); local=np.c_[((pxy[:,0]-xmin)/max(xmax-xmin,1e-9))*(cw-18)+9,((pxy[:,1]-ymin)/max(ymax-ymin,1e-9))*(ch-30)+8]
 x=(i%cols)*cw;y=42+(i//cols)*ch
 ff=f if len(f)<=2500 else f[np.linspace(0,len(f)-1,2500).astype(int)]
 for j in ff: sd.polygon([tuple(local[k]+[x,y]) for k in j],fill=(190,198,208),outline=(110,118,126))
 sd.text((x+8,y+ch-20),f'PART_{i:03d}',fill=(20,30,40),font=FONT)
sheet.save(OUT/'tank_45_parts_contact_sheet.png')
print('parts',len(parts),'overview',OUT/'tank_45_parts_overview.png','contact',OUT/'tank_45_parts_contact_sheet.png')
