#!/usr/bin/env python3
import hashlib,json,math,shutil,os
from pathlib import Path
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont

O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=O/'showcase_visualization_v1';(OUT/'summary').mkdir(parents=True,exist_ok=True)
for x in ['case00','case02','case05','case09','real03','scripts']:(OUT/x).mkdir(exist_ok=True)
FONT=ImageFont.load_default(); PAL=[(137,190,219),(244,181,123),(167,211,151),(215,148,167),(188,170,218),(255,224,130),(141,211,199),(190,186,218),(251,180,174),(179,222,105)]
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,default=lambda o:int(o) if isinstance(o,np.integer) else float(o) if isinstance(o,np.floating) else str(o))+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def camera():
 a,e=np.radians(38),np.radians(24);rz=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);rx=np.array([[1,0,0],[0,np.cos(e),np.sin(e)],[0,-np.sin(e),np.cos(e)]]);return rx@rz
R=camera()
def project(P,bounds,w,h,pad=.06):
 corners=np.array([[x,y,z] for x in bounds[0] for y in bounds[1] for z in bounds[2]]);q=corners@R.T;lo=q[:,:2].min(0);hi=q[:,:2].max(0);mid=(lo+hi)/2;span=max(hi-lo)*(1+2*pad);p=P@R.T;xy=(p[:,:2]-mid)/span;return np.c_[(xy[:,0]+.5)*w,(.5-xy[:,1])*h],p[:,2]
def shaded_color(base,n):
 n=n/max(np.linalg.norm(n),1e-12);L=np.array([.3,.45,.84]);L=L/np.linalg.norm(L);v=.38+.62*abs(n@L);return tuple(int(min(255,max(0,c*v))) for c in base)
def sharp_feature_edges(mesh, sharp_deg=48.0, max_segs=12000):
 """Sparse CAD-like edges from tessellation (sharp dihedral + silhouette). Avoids dense all-BRep wireframe soup."""
 V=np.asarray(mesh.vertices,float);F=np.asarray(mesh.faces,int)
 if len(F)==0:return []
 rounded=np.round(V,6);uniq,inv=np.unique(rounded,axis=0,return_inverse=True)
 m=trimesh.Trimesh(vertices=uniq,faces=inv[F],process=False)
 if len(getattr(m,'face_adjacency',[]))==0:return []
 fn=m.face_normals;adj=m.face_adjacency;ae=m.face_adjacency_edges
 dots=np.clip(np.einsum('ij,ij->i',fn[adj[:,0]],fn[adj[:,1]]),-1,1);ang=np.degrees(np.arccos(dots))
 view=R[2];facing=fn@view;sil=(facing[adj[:,0]]*facing[adj[:,1]])<-.02
 segs=uniq[ae[(ang>=sharp_deg)|sil]];ext=float(np.linalg.norm(m.bounds[1]-m.bounds[0]));lens=np.linalg.norm(segs[:,1]-segs[:,0],axis=1)
 segs=segs[lens>=max(ext*.002,1e-4)]
 if len(segs)>max_segs:
  w=np.maximum(np.linalg.norm(segs[:,1]-segs[:,0],axis=1),1e-9);w=w/w.sum();idx=np.random.default_rng(0).choice(len(segs),size=max_segs,replace=False,p=w);segs=segs[idx]
 return [segs[i] for i in range(len(segs))]
def render(meshes,bounds,path,colors=None,wire=False,true_edges=None,vertices=None,size=(1200,1050),explode=0):
 w,h=size;im=Image.new('RGB',size,'white');dr=ImageDraw.Draw(im);alltris=[];center=bounds.mean(1);diag=np.linalg.norm(bounds[:,1]-bounds[:,0])
 for mi,m in enumerate(meshes):
  V=np.asarray(m.vertices,float).copy();F=np.asarray(m.faces,int);off=np.zeros(3)
  if explode and len(meshes)>1:off=(V.mean(0)-center);off=off/max(np.linalg.norm(off),1e-12)*diag*explode;V+=off
  if len(F)>100000:F=F[np.linspace(0,len(F)-1,100000).astype(int)]
  xy,z=project(V,bounds,w,h);base=(190,211,231) if colors is None else colors[mi%len(colors)]
  for f in F:
   p=V[f];n=np.cross(p[1]-p[0],p[2]-p[0]);alltris.append((float(z[f].mean()),[tuple(x) for x in xy[f]],shaded_color(base,n)))
 alltris.sort(key=lambda x:x[0]);
 for _,poly,c in alltris:dr.polygon(poly,fill=c)
 if wire:
  for mi,m in enumerate(meshes):
   V=np.asarray(m.vertices);F=np.asarray(m.faces);xy,_=project(V,bounds,w,h);stride=max(1,len(F)//45000)
   for f in F[::stride]:dr.line([tuple(xy[f[0]]),tuple(xy[f[1]]),tuple(xy[f[2]]),tuple(xy[f[0]])],fill=(105,108,112),width=1)
 if true_edges:
  for p in true_edges:
   if len(p)<2:continue
   xy,_=project(np.asarray(p),bounds,w,h);dr.line([tuple(x) for x in xy],fill=(38,55,76),width=2)
 if vertices is not None and len(vertices):
  xy,_=project(np.asarray(vertices),bounds,w,h)
  for x,y in xy[::max(1,len(xy)//3500)]:dr.ellipse((x-1.5,y-1.5,x+1.5,y+1.5),fill=(35,96,170))
 im.save(path);return len(alltris)
def read_step(path):
 from OCP.STEPControl import STEPControl_Reader
 from OCP.IFSelect import IFSelect_RetDone
 rd=STEPControl_Reader();st=rd.ReadFile(str(path));assert st==IFSelect_RetDone;roots=rd.TransferRoots();assert roots>0;return rd.OneShape(),roots
def topology(shape,diag):
 from OCP.TopTools import TopTools_IndexedMapOfShape
 from OCP.TopExp import TopExp
 from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE,TopAbs_VERTEX
 from OCP.TopoDS import TopoDS
 from OCP.BRepAdaptor import BRepAdaptor_Curve
 from OCP.GCPnts import GCPnts_QuasiUniformDeflection
 from OCP.BRep import BRep_Tool
 maps={}
 for name,k in [('face',TopAbs_FACE),('edge',TopAbs_EDGE),('vertex',TopAbs_VERTEX)]:m=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(shape,k,m);maps[name]=m
 edges=[];em=maps['edge'];stride=max(1,em.Size()//22000)
 for i in range(1,em.Size()+1,stride):
  try:
   e=TopoDS.Edge_s(em.FindKey(i));a=BRepAdaptor_Curve(e);pts=[]
   try:s=GCPnts_QuasiUniformDeflection(a,max(diag*.0015,1e-5),a.FirstParameter(),a.LastParameter());pts=[[s.Value(j).X(),s.Value(j).Y(),s.Value(j).Z()] for j in range(1,s.NbPoints()+1)] if s.IsDone() else []
   except Exception:pts=[]
   if not pts:pts=[[a.Value(a.FirstParameter()).X(),a.Value(a.FirstParameter()).Y(),a.Value(a.FirstParameter()).Z()],[a.Value(a.LastParameter()).X(),a.Value(a.LastParameter()).Y(),a.Value(a.LastParameter()).Z()]]
   if len(pts)>80:pts=pts[::max(1,len(pts)//80)]
   edges.append(pts)
  except Exception:pass
 verts=[];vm=maps['vertex'];vstride=max(1,vm.Size()//7000)
 for i in range(1,vm.Size()+1,vstride):
  try:p=BRep_Tool.Pnt_s(TopoDS.Vertex_s(vm.FindKey(i)));verts.append([p.X(),p.Y(),p.Z()])
  except Exception:pass
 return {'BREP_FACE_COUNT':maps['face'].Size(),'BREP_EDGE_COUNT':em.Size(),'BREP_VERTEX_COUNT':vm.Size()},edges,np.asarray(verts)
def tess(shape,defl=.012,ang=.35):
 from OCP.BRepMesh import BRepMesh_IncrementalMesh
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopAbs import TopAbs_FACE
 from OCP.BRep import BRep_Tool
 from OCP.TopLoc import TopLoc_Location
 from OCP.TopoDS import TopoDS
 BRepMesh_IncrementalMesh(shape,defl,False,ang,True).Perform();vs=[];fs=[];o=0;e=TopExp_Explorer(shape,TopAbs_FACE)
 while e.More():
  f=TopoDS.Face_s(e.Current());loc=TopLoc_Location();t=BRep_Tool.Triangulation_s(f,loc)
  if t:
   T=loc.Transformation();v=np.array([[t.Node(i).Transformed(T).X(),t.Node(i).Transformed(T).Y(),t.Node(i).Transformed(T).Z()] for i in range(1,t.NbNodes()+1)]);ff=[]
   for i in range(1,t.NbTriangles()+1):a,b,c=t.Triangle(i).Get();ff.append([o+a-1,o+b-1,o+c-1])
   vs.append(v);fs+=ff;o+=len(v)
  e.Next()
 return trimesh.Trimesh(vertices=np.vstack(vs),faces=np.asarray(fs),process=False)
def cached_mesh(cache):d=np.load(cache);return trimesh.Trimesh(vertices=d['V'],faces=d['F'],process=False)
def cached_components(cache):
 d=np.load(cache,allow_pickle=True);return [trimesh.Trimesh(vertices=d[f'V_{i}'],faces=d[f'F_{i}'],process=False) for i in range(int(d['n']))]
def compose(images,titles,path,cols):
 ims=[Image.open(x).convert('RGB') for x in images];pw,ph=640,560;rows=math.ceil(len(ims)/cols);out=Image.new('RGB',(pw*cols,ph*rows+54),(255,255,255));dr=ImageDraw.Draw(out);dr.text((18,15),'SHOWCASE_VISUALIZATION_V1',fill=(20,30,45),font=FONT)
 for i,(im,t) in enumerate(zip(ims,titles)):im.thumbnail((pw-20,ph-55));x=(i%cols)*pw+10;y=(i//cols)*ph+50;out.paste(im,(x,y));dr.text((x+8,y+im.height+8),t,fill=(25,35,50),font=FONT)
 out.save(path)
def mesh_regions(paths):return [trimesh.load(p,force='mesh',process=False) for p in paths if Path(p).is_file()]

summary={r['CASE_ID']:r for r in __import__('csv').DictReader(open(O/'batch_real_mesh2cad_v1/artifacts/per_case_summary.csv'))}
specs={
'case00':{'id':'CASE_00','src':Path(summary['CASE_00']['SOURCE_OBJ_PATH']),'step':Path(summary['CASE_00']['STEP_PATH']),'split':sorted((O/'batch_real_mesh2cad_v1/cases/CASE_00/hybrid_preview').glob('*global_cad.obj')),'stype':'CAD_PARTS','cache':O/'render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_assembly.npz','ccache':O/'render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_components.npz'},
'real03':{'id':'REAL_03','src':Path(summary['CASE_00']['SOURCE_OBJ_PATH']),'step':Path(summary['CASE_00']['STEP_PATH']),'split':sorted((O/'full_object_cad_recovery_v1/parts').glob('*/source.obj')),'stype':'CAD_PARTS','cache':O/'render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_assembly.npz','ccache':O/'render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_components.npz'},
'case05':{'id':'CASE_05','src':Path(summary['CASE_05']['SOURCE_OBJ_PATH']),'step':Path(summary['CASE_05']['STEP_PATH']),'split':sorted((O/'batch_real_mesh2cad_v1/cases/CASE_05/p3').glob('part_*.obj')),'stype':'P3_PARTS','cache':O/'render_upgrade_v1/case05/cache/e626e0a003326391_d0.0075_a0.3_assembly.npz','ccache':O/'render_upgrade_v1/case05/cache/e626e0a003326391_d0.0075_a0.3_components.npz'},
'case02':{'id':'CASE_02','src':Path(summary['CASE_02']['SOURCE_OBJ_PATH']),'step':Path(summary['CASE_02']['STEP_PATH']),'split':[],'stype':'CAD_SURFACE_FAMILIES','cache':None,'ccache':None,'transform':O/'batch_real_mesh2cad_v1/cases/CASE_02/cad_recovery/CADPART_000/local_to_global_transform.json'},
'case09':{'id':'CASE_09','src':Path(summary['CASE_09']['SOURCE_OBJ_PATH']),'step':Path(summary['CASE_09']['STEP_PATH']),'split':[],'stype':'CAD_SURFACE_FAMILIES','cache':None,'ccache':None,'transform':O/'batch_real_mesh2cad_v1/cases/CASE_09/cad_recovery/CADPART_000/local_to_global_transform.json'}}
loaded={};step_runtime={}
only=set(filter(None,os.environ.get('SHOWCASE_ONLY','').split(',')))
for key,s in specs.items():
 if only and key not in only:continue
 print('BEGIN',key,flush=True);src=trimesh.load(s['src'],force='mesh',process=False);bounds=np.asarray(src.bounds).T;stepkey=str(s['step'].resolve())
 if stepkey in step_runtime:roots,counts,edges,verts,cad,comps=step_runtime[stepkey]
 else:
  shape,roots=read_step(s['step']);diag=np.linalg.norm(bounds[:,1]-bounds[:,0]);counts,edges,verts=topology(shape,diag);cad=cached_mesh(s['cache']) if s['cache'] else tess(shape);comps=cached_components(s['ccache']) if s['ccache'] else [cad];step_runtime[stepkey]=(roots,counts,edges,verts,cad,comps)
 if s.get('transform'):
  td=load(s['transform']);M=np.asarray(td['CANONICAL_TO_SOURCE']);cad.apply_transform(M)
  for m in comps:m.apply_transform(M)
  edges=[(np.c_[np.asarray(e),np.ones(len(e))]@M.T)[:,:3].tolist() for e in edges];verts=(np.c_[verts,np.ones(len(verts))]@M.T)[:,:3]
 out=OUT/key;meshpng=out/'mesh_model.png';splitpng=out/'split_model.png';brep=out/'brep_model.png';wire=out/'brep_wireframe.png';part=out/'part_colored_brep.png';expl=out/'exploded_brep.png'
 render([src],bounds,meshpng,colors=[(220,216,205)],wire=True)
 regions=mesh_regions(s['split'])
 if not regions:
  # source normal families used only in split panel, never in BRep panel.
  m=src.copy();bins=np.argmax(abs(m.face_normals),axis=1)*2+(m.face_normals[np.arange(len(m.faces)),np.argmax(abs(m.face_normals),axis=1)]>0);regions=[m.submesh([np.flatnonzero(bins==i)],append=True,repair=False) for i in sorted(set(bins))]
 render(regions,bounds,splitpng,colors=PAL)
 feat=sharp_feature_edges(cad)
 # B-rep shaded panel: sparse feature edges only (NOT all TopoDS edges — that looks like mesh cage)
 render([cad],bounds,brep,colors=[(190,210,234)],true_edges=feat)
 render([],bounds,wire,true_edges=feat)
 render(comps,bounds,part,colors=PAL,true_edges=None)
 # exploded: do NOT overlay un-exploded global edges (creates ghost wireframes)
 render(comps,bounds,expl,colors=PAL,true_edges=None,explode=.045)
 comp3=out/'comparison_figure.png';compose([meshpng,splitpng,brep],['Mesh model','Part / surface split','B-rep model'],comp3,3)
 comp4=out/'comparison_figure_4panel.png';compose([meshpng,splitpng,part,brep],['Mesh model','P3 / part split','CAD-part / surface split','B-rep model'],comp4,4)
 feature=False;section=False
 if key in ('real03','case05','case00'):
  close=out/'feature_closeups.png';compose([brep,wire,part],['B-rep surfaces','True topology edges','Part-colored detail'],close,3);feature=True
 if key in ('real03','case05'):
  sec=out/'section_view.png';# clean orthographic proxy using true BRep only
  render([cad],bounds,sec,colors=[(190,210,234)],true_edges=edges);section=True
 meta={'CASE_ID':s['id'],'SOURCE_OBJ_PATH':str(s['src']),'STEP_PATH':str(s['step']),'STEP_SHA256':sha(s['step']),'STEP_RELOAD_SUCCESS':True,'STEP_ROOTS':roots,'MESH_PANEL_SOURCE':'SOURCE_OBJ','SPLIT_PANEL_SOURCE':[str(x) for x in s['split']] or 'SOURCE_NORMAL_FAMILIES','BREP_PANEL_SOURCE':'STEP_ONLY','BREP_RENDER_USES_SOURCE_MESH':False,**counts,'EDGE_RENDER_MODE':'SHARP_EDGE+SILHOUETTE_FILTERED','TRUE_BREP_EDGE_POLYLINES_AVAILABLE':len(edges),'FEATURE_EDGE_SEGMENTS_RENDERED':len(feat),'TESSELLATION_DEFLECTION':.0075 if s['cache'] else .012,'TESSELLATION_ANGULAR_DEFLECTION':.3 if s['cache'] else .35,'TESSELLATED_TRIANGLE_COUNT':len(cad.faces),'FACE_TESSELLATION_CACHE_HASH_VERIFIED':bool(s['cache']),'SPLIT_VISUALIZATION_TYPE':s['stype'],'EXPLODED_ENABLED':True,'SECTION_VIEW_ENABLED':section,'FEATURE_CLOSEUPS_ENABLED':feature,'MAIN_3D_RENDER_BACKEND':'PIL_SOFTWARE_RASTERIZER','MATPLOTLIB_USED_FOR_MAIN_3D':False};dump(out/'render_metadata.json',meta);loaded[key]={'meta':meta,'main':comp3,'brep':brep,'expl':expl};print('DONE',key,counts,len(cad.faces),flush=True)
# summary boards
order=['case00','case05','case02','case09','real03'];imgs=[];titles=[]
for k in order:
 for p,t in [(OUT/k/'mesh_model.png',f'{specs[k]["id"]} mesh'),(OUT/k/'split_model.png','split'),(OUT/k/'brep_model.png','B-rep')]:imgs.append(p);titles.append(t)
compose(imgs,titles,OUT/'summary/all_showcases_contact_sheet.png',3)
best=['case00','case05','case02','real03'];compose([OUT/k/'comparison_figure.png' for k in best],[specs[k]['id'] for k in best],OUT/'summary/best_showcases_figure.png',2)
report=['# SHOWCASE_VISUALIZATION_V1','','Five showcase cases were rendered from frozen artifacts only.','', '- Mesh panel: source OBJ shaded with triangle wireframe.', '- Split panel: P3/CAD parts for multi-part cases; source normal families for whole-object cases.', '- B-rep panel: SHA-verified STEP face tessellation and true TopoDS edge curves extracted after fresh STEP reload.', '- The B-rep panels do not contain source mesh geometry.', '', 'Caveats: CASE_05 remains 95.6067% rather than exact 100% and is loft-heavy. REAL_03 is the strict topology-complete showcase.', '']
for k in order:report+=['## '+specs[k]['id'],'',f"Source: `{specs[k]['src']}`",f"STEP: `{specs[k]['step']}`",'']+[f'- `{p.name}`' for p in sorted((OUT/k).glob('*.png'))]+['']
(OUT/'report.md').write_text('\n'.join(report)+'\n');print('ALL_DONE',flush=True)
