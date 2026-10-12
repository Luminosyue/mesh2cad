"""Conservative, fail-closed native CadQuery representation validator.

No historical output is written. Unknown Python is never executed. The supported
straight-line numeric CadQuery grammar is deliberately smaller than Python.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import ast, json, sys, math, re, hashlib, argparse, subprocess, shutil
from pathlib import Path
from collections import Counter
import numpy as np
import cadquery as cq
import trimesh
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve

FEATURES=set('box sphere cylinder cone rect circle ellipse polygon polyline spline extrude revolve loft sweep union cut intersect fillet chamfer shell workplane sketch'.split())
METHODS=FEATURES|{'close','translate','rotate','moveTo','lineTo','threePointArc','spline','workplane','tag','toPending'}
BUILD={'box','sphere','cylinder','cone','extrude','revolve','loft','sweep'}
SURFACES={'GeomAbs_Plane':'PLANE','GeomAbs_Cylinder':'CYLINDER','GeomAbs_Cone':'CONE','GeomAbs_Sphere':'SPHERE','GeomAbs_Torus':'TORUS','GeomAbs_BezierSurface':'BEZIER','GeomAbs_BSplineSurface':'BSPLINE','GeomAbs_SurfaceOfExtrusion':'SURFACE_OF_EXTRUSION','GeomAbs_SurfaceOfRevolution':'SURFACE_OF_REVOLUTION'}
ANALYTIC={'PLANE','CYLINDER','CONE','SPHERE','TORUS','SURFACE_OF_EXTRUSION','SURFACE_OF_REVOLUTION'}
LOWLEVEL={'makePolygon','makeFace','makeFromWires','makeShell','makeSolid','BRepBuilderAPI_MakePolygon','BRepBuilderAPI_MakeFace','TopoDS_Face','makeFromMesh'}

def dump(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def numeric(v):
 if isinstance(v,bool):return True
 if isinstance(v,(int,float)):return math.isfinite(v)
 if isinstance(v,(list,tuple)):return all(numeric(x) for x in v)
 return False

def code_audit(code):
 r={'ast_parse_pass':False,'safe_grammar':False,'native_feature_ops':[],'native_feature_count':0,'feature_ops':[], 'mesh_import_detected':False,'embedded_vertices_detected':False,'embedded_faces_detected':False,'mesh_wrapper_detected':False,'source_scan_hits':[], 'unsupported_reasons':[]}
 try:t=ast.parse(code);r['ast_parse_pass']=True
 except Exception as e:r['unsupported_reasons']=[str(e)];return r
 nodes=list(ast.walk(t));calls=[n for n in nodes if isinstance(n,ast.Call)]
 names=[n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else '<dynamic>' for n in calls]
 counts=Counter(x for x in names if x in FEATURES);r.update(native_feature_ops=sorted(counts),feature_ops=sorted(counts),native_feature_count=sum(counts.values()),feature_op_count=sum(counts.values()),feature_op_counts=dict(counts))
 for key,ops in {'primitive_count':BUILD,'sketch_count':{'rect','circle','ellipse','polygon','polyline','spline','sketch'},'extrude_count':{'extrude'},'revolve_count':{'revolve'},'loft_count':{'loft'},'sweep_count':{'sweep'},'boolean_union_count':{'union'},'boolean_cut_count':{'cut'},'boolean_intersect_count':{'intersect'},'fillet_count':{'fillet'},'chamfer_count':{'chamfer'}}.items():r[key]=sum(counts[x] for x in ops)
 meshwords=re.compile(r'\b(vertices|faces|triangles|indices|mesh|trimesh)\b|\.(obj|stl|ply|npy)\b|makePolygon|makeFace|makeFromWires|makeShell|makeSolid|BRepBuilderAPI|TopoDS_Face',re.I)
 r['source_scan_hits']=[{'line':i,'text':s[:500]} for i,s in enumerate(code.splitlines(),1) if meshwords.search(s)]
 imports=[ast.unparse(n) for n in nodes if isinstance(n,(ast.Import,ast.ImportFrom))];r['imports']=imports
 strings=[n.value for n in nodes if isinstance(n,ast.Constant) and isinstance(n.value,str)]
 r['mesh_import_detected']=any(re.search(r'\.(obj|stl|ply|npy)$',s,re.I) for s in strings) or any('trimesh' in s or 'meshio' in s for s in imports) or any(x in names for x in ['importStl','importSTL','read_stl','read_triangle_mesh'])
 literal_arrays=[]
 for n in nodes:
  if isinstance(n,(ast.List,ast.Tuple)):
   try:v=ast.literal_eval(n)
   except Exception:continue
   if len(v)>=3 and all(isinstance(x,(list,tuple)) and len(x)==3 and all(isinstance(y,(int,float)) for y in x) for x in v):literal_arrays.append(v)
 r['embedded_vertices_detected']=bool(literal_arrays)
 r['embedded_faces_detected']=any(all(isinstance(y,int) and y>=0 for x in v for y in x) for v in literal_arrays)
 low=sorted(set(names)&LOWLEVEL);r['low_level_constructors']=low
 r['triangle_iteration_detected']=any(isinstance(n,(ast.For,ast.ListComp,ast.GeneratorExp)) for n in nodes) and bool(low)
 r['mesh_wrapper_detected']=bool(low and (r['mesh_import_detected'] or literal_arrays or r['triangle_iteration_detected'])) or any(x in names for x in ['importStl','importSTL','makeFromMesh'])
 env={};profile_n=0;live=set();literal_parameters=0
 def expr(n):
  nonlocal profile_n,literal_parameters
  if isinstance(n,ast.Name):
   if n.id not in env:raise ValueError('Unbound/forbidden name '+n.id)
   return env[n.id]
  if isinstance(n,(ast.Constant,ast.List,ast.Tuple,ast.UnaryOp)):
   v=ast.literal_eval(n)
   if not numeric(v) and not (isinstance(v,str) and v in {'XY','XZ','YZ','front','back','left','right','top','bottom'}):raise ValueError('Non-numeric parameter or external payload')
   literal_parameters+=1;return ('literal',set(),v)
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute):
   meth=n.func.attr
   if isinstance(n.func.value,ast.Name) and n.func.value.id=='cq':
    if meth not in {'Workplane','Plane'}:raise ValueError('Forbidden cq constructor '+meth)
    typ='wp' if meth=='Workplane' else 'plane';deps=set()
   else:
    typ,deps,_=expr(n.func.value)
    if typ!='wp' or meth not in METHODS:raise ValueError('Forbidden method or receiver '+meth)
    deps=set(deps)
   args=[expr(x) for x in n.args]+[expr(x.value) for x in n.keywords]
   if any(k.arg is None for k in n.keywords):raise ValueError('Expanded kwargs not allowed')
   for at,ad,av in args:deps|=ad
   if meth in FEATURES:deps.add((n.lineno,n.col_offset,meth))
   if meth in {'polyline','spline'}:
    if not args or args[0][0]!='literal':raise ValueError('Profile must be a numeric literal')
    pts=args[0][2]
    if not isinstance(pts,(list,tuple)) or not all(isinstance(p,(list,tuple)) and len(p)==2 for p in pts):raise ValueError('Only 2D numeric sketch profiles supported; 3D arrays require review')
    if meth=='spline' and len(pts)>20:raise ValueError('Spline control/interpolation point budget exceeded')
    profile_n+=len(pts)
   elif meth in {'moveTo','lineTo','circle','ellipse','polygon','rect'}:profile_n+=1
   elif meth=='threePointArc':profile_n+=2
   return (typ,deps,None)
  raise ValueError('Unsupported expression '+type(n).__name__)
 try:
  if len(code)>60000:raise ValueError('Program length budget exceeded')
  imported=False
  for n in t.body:
   if isinstance(n,ast.Import):
    if imported or len(n.names)!=1 or n.names[0].name!='cadquery' or n.names[0].asname!='cq':raise ValueError('Only one import cadquery as cq')
    imported=True
   elif isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
    target=n.targets[0].id
    if target=='cq' or '__' in target:raise ValueError('Forbidden assignment target')
    env[target]=expr(n.value)
   else:raise ValueError('Unsupported statement '+type(n).__name__)
  if not imported or 'result' not in env or env['result'][0]!='wp':raise ValueError('Missing native result')
  live=env['result'][1]
  if not any(x[2] in BUILD for x in live):raise ValueError('Result has no live solid-building feature')
  if r['primitive_count']>10 or sum(counts[x] for x in ['union','cut','intersect'])>8 or profile_n>96:raise ValueError('Compact feature budget exceeded')
  if literal_arrays:raise ValueError('Embedded 3D vertex/index arrays require rejection/review')
  r['safe_grammar']=True
 except Exception as e:r['unsupported_reasons'].append(str(e))
 r.update(sketch_entity_count=profile_n,live_result_feature_ops=sorted({x[2] for x in live}),live_result_feature_count=len(live),numeric_parameter_nodes=literal_parameters)
 return r

def bounds(s):
 b=s.BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def topology(shape,details=True):
 faces=shape.Faces();rows=[];types=Counter();areas=[];tri=0;quad=0;ngon=0;planar_n=0;edge3=0
 for i,f in enumerate(faces):
  enum=str(BRepAdaptor_Surface(f.wrapped,True).GetType()).split('.')[-1];typ=SURFACES.get(enum,'OTHER');types[typ]+=1
  edges=f.Edges();ec=len(edges);vc=len(f.Vertices());wc=len(f.Wires());lines=all(str(BRepAdaptor_Curve(e.wrapped).GetType()).endswith('GeomAbs_Line') for e in edges)
  triangle=typ=='PLANE' and ec==3 and vc==3 and wc==1 and lines
  tri+=int(triangle);edge3+=int(typ=='PLANE' and ec==3);planar_n+=int(typ=='PLANE');quad+=int(typ=='PLANE' and ec==4 and vc==4 and wc==1 and lines);ngon+=int(typ=='PLANE' and ec>4 and wc==1 and lines)
  area=float(f.Area());areas.append(area);b=np.asarray(bounds(f))
  if details:rows.append({'face_id':i,'surface_type':typ,'occ_enum':enum,'edge_count':ec,'vertex_count':vc,'wire_count':wc,'all_edges_linear':lines,'triangle_planar':triangle,'area':area,'bbox':b.tolist(),'bbox_size':(b[1]-b[0]).tolist()})
 total=sum(areas);nf=len(faces)
 for r in rows:r['relative_face_area']=r['area']/total if total else 0
 solids=shape.Solids();shells=shape.Shells()
 return {'step_reload_pass':True,'solid_count':len(solids),'shell_count':len(shells),'step_face_count':nf,'face_count_total':nf,'step_edge_count':len(shape.Edges()),'step_vertex_count':len(shape.Vertices()),'closed':bool(shells) and all(x.Closed() for x in shells),'shape_closed_flag':bool(shape.Closed()),'valid':bool(shape.isValid()),'face_type_counts':{x:types[x] for x in list(SURFACES.values())+['OTHER']},'analytic_face_count':sum(types[x] for x in ANALYTIC),'spline_face_count':types['BSPLINE']+types['BEZIER'],'unknown_face_count':types['OTHER'],'analytic_face_ratio':sum(types[x] for x in ANALYTIC)/nf if nf else 0,'triangle_planar_face_count':tri,'triangle_planar_face_ratio':tri/nf if nf else 0,'triangle_face_count':tri,'triangle_face_ratio':tri/nf if nf else 0,'planar_triangle_face_ratio':tri/planar_n if planar_n else 0,'planar_edge3_count':edge3,'quad_face_count':quad,'ngon_face_count':ngon,'median_face_area':float(np.median(areas)) if areas else 0,'p10_face_area':float(np.quantile(areas,.1)) if areas else 0,'p90_face_area':float(np.quantile(areas,.9)) if areas else 0,'tiny_face_threshold_relative':.001,'tiny_face_count':sum(a<total*.001 for a in areas),'tiny_planar_face_count':sum(r['surface_type']=='PLANE' and r['relative_face_area']<.001 for r in rows),'area':total,'volume':float(shape.Volume()),'bbox':bounds(shape),'faces':rows}

def isolated_worker(program,out):
 code=Path(program).read_text();ca=code_audit(code)
 if not ca['safe_grammar']:raise ValueError('Unsafe/unsupported input; refused execution')
 def importer(name,globals=None,locals=None,fromlist=(),level=0):
  if name!='cadquery' or level:raise ImportError(name)
  return cq
 scope={'__builtins__':{'__import__':importer}}
 exec(compile(code,'cad.py','exec'),scope)
 result=scope['result'];shape=result.val()
 r=topology(shape,False);r['execution_pass']=bool(r['valid'] and r['solid_count'] and r['closed']);r['input_files']=['cad.py'];r['source_mesh_available_in_workdir']=False
 dump(out,r)

def validate(cad_path,step_path,source_mesh_path,work_dir):
 cad_path=Path(cad_path);step_path=Path(step_path);source_mesh_path=Path(source_mesh_path);work_dir=Path(work_dir);work_dir.mkdir(parents=True,exist_ok=True)
 r={'cad_path':str(cad_path),'step_path':str(step_path),'source_mesh_path':str(source_mesh_path),'classification':'E_UNCERTAIN','self_contained':False,'isolated_reexecution_pass':False,'accepted_for_parametric_dataset':False,'is_native_parametric_cad':'UNCERTAIN','reasons':[],'missing':[]}
 for name,p in [('cad',cad_path),('step',step_path),('source_mesh',source_mesh_path)]:
  if not p.is_file():r['missing'].append(name+':MISSING')
  else:r[name+'_sha256']=sha(p)
 if r['missing']:r['reasons']=r['missing'];return r
 ca=code_audit(cad_path.read_text());r.update(ca)
 mesh=trimesh.load(source_mesh_path,force='mesh',process=False);r.update(source_vertex_count=len(mesh.vertices),source_triangle_count=len(mesh.faces))
 try:shape=cq.importers.importStep(str(step_path)).val();r.update(topology(shape))
 except Exception as e:r['reasons']=['STEP reload failed: '+str(e)];return r
 nf=r['step_face_count'];nt=r['source_triangle_count'];r.update(compression_ratio=nt/nf if nf else None,face_triangle_ratio=nf/nt if nt else None)
 if ca['safe_grammar']:
  iso=work_dir/'isolated';iso.mkdir(exist_ok=True);shutil.copyfile(cad_path,iso/'cad.py')
  try:
   proc=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(iso/'cad.py'),str(iso/'result.json')],cwd=iso,capture_output=True,text=True,timeout=180,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
   (iso/'execution.log').write_text(proc.stdout+'\n'+proc.stderr)
   if proc.returncode==0:
    reg=json.loads((iso/'result.json').read_text());r['isolated_reexecution_pass']=reg['execution_pass'];r['self_contained']=reg['execution_pass']
    bberr=float(np.max(np.abs(np.asarray(reg['bbox'])-r['bbox'])));verr=abs(reg['volume']-r['volume'])/max(abs(r['volume']),1e-12);aerr=abs(reg['area']-r['area'])/max(r['area'],1e-12)
    r['reconstruction_comparison']={'bbox_max_error':bberr,'relative_volume_error':verr,'relative_area_error':aerr,'same_face_type_counts':reg['face_type_counts']==r['face_type_counts'],'same_face_edge_vertex_counts':all(reg[k]==r[k] for k in ['step_face_count','step_edge_count','step_vertex_count','solid_count'])}
    r['code_step_correspondence_pass']=bberr<1e-5 and verr<1e-5 and aerr<1e-5 and all([r['reconstruction_comparison']['same_face_type_counts'],r['reconstruction_comparison']['same_face_edge_vertex_counts']])
   else:r['reasons'].append('Isolated code execution failed; see execution.log')
  except Exception as e:r['reasons'].append('Isolated execution: '+str(e))
 triangular_soup=nf>=100 and r['triangle_planar_face_ratio']>=.8
 close_source=nf>=100 and nt>0 and .5<=nf/nt<=2
 suspicious_patches=nf>=500 and r['tiny_face_count']/nf>.8 and nt>0 and nf/nt>.3
 r['faceted_topology_warning']=triangular_soup or close_source or suspicious_patches
 if r['mesh_wrapper_detected']:
  r['classification']='D_MESH_WRAPPER';r['reasons'].append('Mesh import/embedded triangle topology flows into low-level B-Rep construction')
 elif triangular_soup and (close_source or r['triangle_iteration_detected'] or r['embedded_faces_detected']):
  r['classification']='C_FACETED_BREP';r['reasons'].append('Dense triangular B-Rep topology corroborated by code or source face-count evidence')
 elif ca['safe_grammar'] and r['self_contained'] and r.get('code_step_correspondence_pass') and r['valid'] and r['closed'] and not r['faceted_topology_warning'] and not r['unknown_face_count']:
  r['classification']='A_NATIVE_PARAMETRIC';r['reasons'].append('Live compact numeric feature construction; isolated execution matches STEP topology, bounds, volume and area; no mesh dependency or triangle-soup evidence')
 elif not r['faceted_topology_warning'] and r['valid'] and not ca['native_feature_count'] and not ca['mesh_import_detected'] and not ca['embedded_vertices_detected'] and any('importStep' in ast.unparse(n) for n in ast.walk(ast.parse(cad_path.read_text())) if isinstance(n,ast.Call)):
  r['classification']='B_NATIVE_BREP_NONPARAMETRIC';r['reasons'].append('Imported native B-Rep without self-contained feature construction; review required')
 else:r['reasons']+=ca['unsupported_reasons']+['Insufficient or conflicting construction/topology evidence; fail closed']
 r['accepted_for_parametric_dataset']=r['classification']=='A_NATIVE_PARAMETRIC';r['is_native_parametric_cad']='YES' if r['accepted_for_parametric_dataset'] else 'NO' if r['classification'] in ['B_NATIVE_BREP_NONPARAMETRIC','C_FACETED_BREP','D_MESH_WRAPPER'] else 'UNCERTAIN'
 r['faceted_pseudo_cad']=r['classification'] in ['C_FACETED_BREP','D_MESH_WRAPPER'];r['primary_reason']=r['reasons'][0];r['dataset_acceptance_scope']='Representation only; geometric quality must pass separately'
 return r

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='--worker':isolated_worker(sys.argv[2],sys.argv[3])
 else:
  ap=argparse.ArgumentParser();ap.add_argument('--cad',required=True);ap.add_argument('--step',required=True);ap.add_argument('--source-mesh',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);r=validate(a.cad,a.step,a.source_mesh,out.parent/'execution');dump(out,r);print(json.dumps({k:v for k,v in r.items() if k!='faces'},indent=2));sys.exit(0 if r['accepted_for_parametric_dataset'] else 2)
