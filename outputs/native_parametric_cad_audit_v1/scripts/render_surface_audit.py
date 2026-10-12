"""Render original STEP with OCC surface normals and actual B-Rep edges."""
from validate_native_parametric_cad import *
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parents[1];D=O/'visualizations';D.mkdir(exist_ok=True)
COLORS={'PLANE':[84,157,220],'CYLINDER':[64,181,139],'CONE':[236,174,61],'SPHERE':[170,127,212],'TORUS':[224,123,82],'BSPLINE':[181,112,213],'BEZIER':[181,112,213],'SURFACE_OF_EXTRUSION':[56,179,197],'SURFACE_OF_REVOLUTION':[223,133,155],'OTHER':[140,140,140],'TRIANGLE':[224,68,73]}
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
az=np.deg2rad(35);el=np.deg2rad(25);z=np.array([np.cos(el)*np.sin(az),np.sin(el),np.cos(el)*np.cos(az)]);x=np.cross([0,1,0],z);x/=np.linalg.norm(x);y=np.cross(z,x);R=np.column_stack([x,y,z]);LIGHT=np.array([-.35,.55,.76]);LIGHT/=np.linalg.norm(LIGHT)
def raster(v,n,tris,color,center,span,buf,depth):
 size=len(depth);q=(v-center)@R;screen=q[:,:2]*size*.78/span+[size*.5,size*.55];screen[:,1]=size*1.1-screen[:,1];ns=n@R
 for tri in tris:
  xy=screen[tri];zz=q[tri,2];norm=ns[tri];lo=np.maximum(np.floor(xy.min(0)).astype(int),[0,75]);hi=np.minimum(np.ceil(xy.max(0)).astype(int),[size-1,size-35])
  if np.any(hi<lo):continue
  a,b,c=xy;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-12:continue
  xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5);w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1;zzp=w0*zz[0]+w1*zz[1]+w2*zz[2];ds=depth[lo[1]:hi[1]+1,lo[0]:hi[0]+1];mask=(w0>=-1e-8)&(w1>=-1e-8)&(w2>=-1e-8)&(zzp>ds)
  normal=w0[...,None]*norm[0]+w1[...,None]*norm[1]+w2[...,None]*norm[2];normal/=np.maximum(np.linalg.norm(normal,axis=-1,keepdims=True),1e-12);dot=normal@LIGHT;shade=.35+.6*np.maximum(dot,0)+.05*np.maximum(-dot,0);pixels=np.clip(shade[...,None]*color,0,255).astype(np.uint8);bs=buf[lo[1]:hi[1]+1,lo[0]:hi[0]+1];bs[mask]=pixels[mask];ds[mask]=zzp[mask]
def render(row,label):
 shape=cq.importers.importStep(row['step_path']).val();b=np.array(row['bbox']);center=b.mean(0);corners=np.array([[a,b0,c] for a in b[:,0] for b0 in b[:,1] for c in b[:,2]]);span=max(np.ptp((corners-center)@R,axis=0)[:2]);size=600
 smooth=np.full((size,size,3),249,dtype=np.uint8);types=smooth.copy();zs=np.full((size,size),-np.inf);zt=zs.copy()
 for i,face in enumerate(shape.Faces()):
  vv,ff=face.tessellate(max(span*.0003,1e-5),.04);v=np.array([p.toTuple() for p in vv]);tri=np.array(ff)
  if not len(tri):continue
  normals=[]
  for p in vv:
   try:normals.append(face.normalAt(p).toTuple())
   except Exception:normals.append(face.normalAt().toTuple())
  n=np.array(normals);fd=row['faces'][i];typ='TRIANGLE' if fd['triangle_planar'] else fd['surface_type']
  raster(v,n,tri,np.array([129,172,208]),center,span,smooth,zs);raster(v,n,tri,np.array(COLORS[typ]),center,span,types,zt)
 edges=smooth.copy()
 for edge in shape.Edges():
  pts,_=edge.sample(100);v=np.array([p.toTuple() for p in pts]);q=(v-center)@R;xy=q[:,:2]*size*.78/span+[size*.5,size*.55];xy[:,1]=size*1.1-xy[:,1]
  for j in range(len(xy)-1):
   nn=max(2,int(np.linalg.norm(xy[j+1]-xy[j])*2));tt=np.linspace(0,1,nn);pp=np.rint(xy[j]+tt[:,None]*(xy[j+1]-xy[j])).astype(int);zz=q[j,2]+tt*(q[j+1,2]-q[j,2]);valid=(pp[:,0]>=0)&(pp[:,0]<size)&(pp[:,1]>=75)&(pp[:,1]<size-35);pp=pp[valid];zz=zz[valid];visible=zz>=zs[pp[:,1],pp[:,0]]-span*.002;pp=pp[visible];edges[pp[:,1],pp[:,0]]=[29,43,62]
 panels=[]
 for buf,title in [(smooth,'STEP smooth shading'),(edges,'Actual B-Rep edges'),(types,'B-Rep surface types')]:
  im=Image.fromarray(buf);dr=ImageDraw.Draw(im);dr.text((18,12),title,font=font(24),fill='#182536');dr.text((18,43),f"{row['step_face_count']} faces | {row['triangle_planar_face_count']} planar triangles",font=font(16),fill='#536477');panels.append(im)
 out=Image.new('RGB',(1800,690),'#f9f9f9')
 for i,im in enumerate(panels):out.paste(im,(600*i,55))
 dr=ImageDraw.Draw(out);dr.text((18,12),label,font=font(24),fill='#182536');xx=20
 for typ in ['PLANE','CYLINDER','CONE','BSPLINE','TRIANGLE']:
  dr.rectangle((xx,653,xx+18,671),fill=tuple(COLORS[typ]));dr.text((xx+25,650),typ,font=font(17),fill='#243448');xx+=270
 path=D/(row.get('version','TEST')+'_'+row.get('case_id','faceted_control').replace('/','_')+'.png');out.save(path);return path.name
if __name__=='__main__':
 rows=[json.loads(p.read_text()) for p in (O/'cases/V3').glob('*/*/audit.json')];assert len(rows)==209
 selected=[]
 for predicate in [lambda r:r['face_type_counts']['CYLINDER']>0,lambda r:r['face_type_counts']['CONE']>0,lambda r:r['face_type_counts']['BSPLINE']>0,lambda r:r['step_face_count']==6,lambda r:r['previous_status']=='STRICT_ACCEPT']:
  options=[r for r in rows if predicate(r) and r not in selected]
  if options:selected.append(sorted(options,key=lambda r:r['step_face_count'])[0])
 for r in sorted(rows,key=lambda r:(r['step_face_count'],r['tiny_face_count']),reverse=True):
  if r not in selected:selected.append(r)
  if len(selected)>=10:break
 manifest=[]
 for r in selected:
  title=f"V3 {r['case_id']} | {r['classification']} | {r['current_status']}";name=render(r,title);manifest.append({'image':name,'case_id':r['case_id'],'classification':r['classification'],'selection':'surface diversity / most complex native topology, NOT alleged faceted case'});print(name,flush=True)
 control=json.loads((O/'tests/faceted_positive_control/audit.json').read_text());name=render(control,'SYNTHETIC CONTROL ONLY: 320 mesh triangles wrapped as B-Rep (not a dataset case)');manifest.append({'image':name,'synthetic_control':True,'included_in_dataset_counts':False})
 dump(D/'manifest.json',manifest)
 page='<meta charset="utf-8"><title>Native CAD surface audit</title><style>body{font:17px system-ui;max-width:1600px;margin:30px auto}img{width:100%}</style><h1>STEP surface audit</h1><p>Left: interpolated OCC surface normals. Middle: actual B-Rep edges, not tessellation edges. Right: underlying surface types. The last image is a synthetic triangle-wrapper negative control, excluded from dataset counts.</p>'
 for r in manifest:page+=f'<img src="{r["image"]}">'
 (D/'index.html').write_text(page)
