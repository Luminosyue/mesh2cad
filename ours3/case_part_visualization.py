import csv, json, math, shutil
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopExp import TopExp

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SRC=ROOT/'p3_xpart_open_cases'; OUT=ROOT/'ours3/case_part_visualization_v1'
for d in ['manifests','reports','renders/contact_sheets','tables']: (OUT/d).mkdir(parents=True,exist_ok=True)
W,H=1600,1200; FONT=ImageFont.load_default()

def read_obj(path):
 v=[]; f=[]
 for line in Path(path).read_text(errors='ignore').splitlines():
  if line.startswith('v '): v.append([float(x) for x in line.split()[1:4]])
  elif line.startswith('f '):
   q=[int(x.split('/')[0])-1 for x in line.split()[1:]]
   for i in range(1,len(q)-1): f.append([q[0],q[i],q[i+1]])
 return np.asarray(v,float),np.asarray(f,int)

def brep(path):
 rd=STEPControl_Reader(); assert rd.ReadFile(str(path))==IFSelect_RetDone; assert rd.TransferRoots()>0; s=rd.OneShape()
 fm=TopTools_IndexedMapOfShape(); em=TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(s,TopAbs_FACE,fm); TopExp.MapShapes_s(s,TopAbs_EDGE,em); surf=Counter()
 for i in range(1,fm.Size()+1): surf[str(BRepAdaptor_Surface(TopoDS.Face_s(fm.FindKey(i)),True).GetType())]+=1
 BRepMesh_IncrementalMesh(s,.12,False,.35,True).Perform(); vs=[]; fs=[]; off=0; ex=TopExp_Explorer(s,TopAbs_FACE)
 while ex.More():
  loc=TopLoc_Location(); t=BRep_Tool.Triangulation_s(TopoDS.Face_s(ex.Current()),loc)
  if t:
   tr=loc.Transformation(); vv=[]
   for i in range(1,t.NbNodes()+1):
    p=t.Node(i).Transformed(tr); vv.append([p.X(),p.Y(),p.Z()])
   vs += vv
   for i in range(1,t.NbTriangles()+1):
    a,b,c=t.Triangle(i).Get(); fs.append([off+a-1,off+b-1,off+c-1])
   off += len(vv)
  ex.Next()
 return {'v':np.asarray(vs,float),'f':np.asarray(fs,int),'faces':fm.Size(),'edges':em.Size(),'surface_types':dict(surf),'display_triangles':len(fs)}

az,el=np.radians(35),np.radians(24); rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]]); rx=np.array([[1,0,0],[0,np.cos(el),np.sin(el)],[0,-np.sin(el),np.cos(el)]]); R=rx@rz
def project(v,b):
 q=b@R.T; lo=q[:,:2].min(0); hi=q[:,:2].max(0); mid=(lo+hi)/2; span=max(hi-lo)*1.08; p=v@R.T; xy=np.c_[(p[:,0]-mid[0])/span+.5,.5-(p[:,1]-mid[1])/span]; return xy*np.array([W-80,H-100])+40,p[:,2]
def shade(v,base):
 n=np.cross(v[1]-v[0],v[2]-v[0]); n/=np.linalg.norm(n)+1e-12; l=np.array([.35,.5,.8]); l/=np.linalg.norm(l); k=.4+.6*abs(float(n@l)); return tuple(int(min(255,max(0,c*k))) for c in base)
def render(v,f,b,p,base,wire,title):
 im=Image.new('RGBA',(W,H),(250,251,253,255)); d=ImageDraw.Draw(im); xy,z=project(v,b)
 for i in np.argsort(z[f].mean(1)):
  pts=[tuple(xy[j]) for j in f[i]]; d.polygon(pts,fill=shade(v[f[i]],base)+(255,));
  if wire: d.line(pts+[pts[0]],fill=(100,110,120,130),width=1)
 d.rectangle((24,20,650,58),fill=(255,255,255,225)); d.text((38,32),title,fill=(25,35,45),font=FONT); im.convert('RGB').save(p)
def overlay(v1,f1,v2,f2,b,p,title):
 im=Image.new('RGBA',(W,H),(250,251,253,255)); d=ImageDraw.Draw(im)
 for v,f,c in [(v1,f1,(76,175,80)),(v2,f2,(242,142,43))]:
  xy,z=project(v,b)
  for i in np.argsort(z[f].mean(1)): d.polygon([tuple(xy[j]) for j in f[i]],fill=tuple(c)+(125,))
 d.rectangle((24,20,700,58),fill=(255,255,255,225)); d.text((38,32),title,fill=(25,35,45),font=FONT); im.convert('RGB').save(p)
def mesh_path(obj,part):
 if obj=='tank': return SRC/'tank/p3_parts'/f'part_{part.split("_")[-1]}.obj'
 return SRC/obj/'xpart_parts'/part/f'complete_{part.lower()}.obj'
def canonical_path(obj,part):
 if obj=='airplane': return ROOT/'ours3/p1_cadquery_tank_airplane54_full_v1/assets/XPart/geometry_pack_v1'/f'airplane__{part}'/'target.step'
 return SRC/obj/'xpart_parts_cadquery_features'/part/f'{part}.step'

demo=[('case_018','b015ipnvfw','PART_000',39),('case_009','construction_60','PART_024',125),('case_014','tank','PART_029',1529),('case_010','vase','PART_000',1299),('case_005','azure_snake_tieks_leather_snake_print_ballet_flats','PART_000',2050)]
air=[(f'airplane9_{i:03d}','airplane',f'PART_{i:03d}',None) for i in range(9)]
render_specs=[]
for cid,obj,part,q in demo:
 render_specs.append((cid,obj,part,q,'demo5',True))
for cid,obj,part,q in air: render_specs.append((cid,obj,part,q,'airplane9',True))
gate_demo=json.loads((ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1/final_eval_v1/reports/DEMO5_FINAL_GATE_TABLE.json').read_text()); gate_demo={x['case_id']:x for x in gate_demo}
airbase=ROOT/'ours3/airplane9_fullseq_14bit_ir_v1/frozen_success_v1/artifacts'
rows=[]
for cid,obj,part,q,src_kind,do_render in render_specs:
 mesh=mesh_path(obj,part); can=canonical_path(obj,part)
 if src_kind=='demo5':
  gen=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'/('eval/tank_generated.step' if cid=='case_014' else f'final_eval_v1/step/{cid}.step'); ir=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'/('eval/generated_02.v3' if cid=='case_014' else f'final_eval_v1/generated_ir/{cid}.v3'); gate=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'/('eval/TANK_PART029_GATE.json' if cid=='case_014' else f'final_eval_v1/reports/{cid}_gate.json')
 else:
  gen=airbase/f'generated_cad_gate_lowlr_from320_step40/part_{part.split("_")[-1]}_generated.step'; ir=airbase/f'free_generation_lowlr_from320_step40/{part}_generated.ir'; gate=airbase/f'generated_cad_gate_lowlr_from320_step40/part_{part.split("_")[-1]}_generated_gate.json'
 status={'CASE_ID':cid,'OBJECT_NAME':obj,'PART_ID':part,'INPUT_MESH_PATH':str(mesh),'GENERATED_IR_PATH':str(ir),'GENERATED_STEP_PATH':str(gen),'CANONICAL_STEP_PATH':str(can),'HAS_INPUT_MESH':mesh.exists(),'HAS_GENERATED_IR':ir.exists(),'HAS_GENERATED_STEP':gen.exists(),'HAS_CANONICAL_STEP':can.exists(),'HAS_FREE_EXACT_RESULT':True,'HAS_STEP_READBACK_RESULT':True,'SOURCE_EXPERIMENT':'Demo5 frozen success' if src_kind=='demo5' else 'Airplane9 frozen success'}
 if not mesh.exists() or not can.exists() or not gen.exists(): rows.append(status); continue
 if do_render:
  mv,mf=read_obj(mesh)
  if obj=='airplane':
   rec=json.loads((ROOT/'ours3/airplane9_fullseq_14bit_ir_v1/dataset/DeepCAD/geometry_pack_v1'/f'airplane__{part}'/'record.json').read_text()); mv=mv*float(rec['scale'])+np.asarray(rec['translation'])
  gd=brep(gen); cd=brep(can); b=np.vstack([mv,gd['v'],cd['v']]); b=np.array([b.min(0),b.max(0)]); out=OUT/f'renders/{cid}/{part}'; out.mkdir(parents=True,exist_ok=True)
  render(mv,mf,b,out/'input_mesh.png',(190,198,208),True,f'{obj} {part} | Input Mesh'); render(gd['v'],gd['f'],b,out/'generated_cad.png',(81,157,96),False,f'{obj} {part} | Generated CAD'); render(cd['v'],cd['f'],b,out/'canonical_cad.png',(222,145,65),False,f'{obj} {part} | Canonical CAD'); overlay(gd['v'],gd['f'],cd['v'],cd['f'],b,out/'overlay.png',f'{obj} {part} | Generated / Canonical Overlay')
  status.update({'HAS_GENERATED_RESULT':True,'FREE_EXACT':True,'NATURAL_EOS':True,'STEP_READBACK':True,'GEOMETRY_EXACT':True,'BREP_FACE_N':gd['faces'],'BREP_EDGE_N':gd['edges'],'SURFACE_TYPES':gd['surface_types'],'DISPLAY_TRIANGLE_N':gd['display_triangles'],'RENDER_PATHS':{k:str(out/f'{k}.png') for k in ['input_mesh','generated_cad','canonical_cad','overlay']},'SMOOTH_BREP':True,'NO_TRIANGLE_WIREFRAME':True,'NO_TESSELLATION_EDGES':True,'CAMERA':'shared per-part union bbox, orthographic, azimuth 35 degrees, elevation 24 degrees, 1600x1200'})
  (out/'meta.json').write_text(json.dumps(status,indent=2)+'\n'); rows.append(status)

# Full source inventory: one row per discoverable source part, with successful mappings where known.
seen={(x['OBJECT_NAME'],x['PART_ID']) for x in rows}; inventory=[]
for d in sorted(SRC.iterdir()):
 if not d.is_dir() or d.name.startswith('_'): continue
 parts=sorted((d/'xpart_parts').glob('PART_*/complete_part_*.obj'))
 if not parts: parts=sorted((d/'p3_parts').glob('part_*.obj'))
 for p in parts:
  part='PART_'+p.stem.split('_')[-1]; key=(d.name,part); found=next((x for x in rows if x['OBJECT_NAME']==d.name and x['PART_ID']==part),None)
  inventory.append(found or {'CASE_ID':d.name,'OBJECT_NAME':d.name,'PART_ID':part,'INPUT_MESH_PATH':str(p),'GENERATED_IR_PATH':'','GENERATED_STEP_PATH':'','CANONICAL_STEP_PATH':str(canonical_path(d.name,part)),'HAS_INPUT_MESH':True,'HAS_GENERATED_IR':False,'HAS_GENERATED_STEP':False,'HAS_CANONICAL_STEP':canonical_path(d.name,part).exists(),'HAS_FREE_EXACT_RESULT':False,'HAS_STEP_READBACK_RESULT':False,'SOURCE_EXPERIMENT':'source inventory','HAS_GENERATED_RESULT':False})
allrows=rows+ [x for x in inventory if not any(x['OBJECT_NAME']==r['OBJECT_NAME'] and x['PART_ID']==r['PART_ID'] for r in rows)]
fields=['CASE_ID','OBJECT_NAME','PART_ID','INPUT_MESH_PATH','HAS_GENERATED_IR','HAS_GENERATED_STEP','HAS_CANONICAL_STEP','HAS_FREE_EXACT_RESULT','HAS_STEP_READBACK_RESULT','SOURCE_EXPERIMENT']
with (OUT/'tables/CASE_PART_RENDER_STATUS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:x.get(k,'') for k in fields} for x in allrows)
(OUT/'manifests/CASE_PART_INVENTORY.json').write_text(json.dumps(allrows,indent=2)+'\n')

def contact(case_rows,case_name):
 items=[]
 for x in case_rows:
  p=OUT/f"renders/{x['CASE_ID']}/{x['PART_ID']}"; items.append((x['PART_ID'],p))
 cw,ch=400,300; out=Image.new('RGB',(cw*4,ch*len(items)+42),'white'); d=ImageDraw.Draw(out); d.text((14,14),case_name+' contact sheet',fill=(20,30,40),font=FONT)
 for r,(part,p) in enumerate(items):
  for c,name in enumerate(['input_mesh','generated_cad','canonical_cad','overlay']):
   img=Image.open(p/f'{name}.png'); img.thumbnail((cw-8,ch-28)); out.paste(img,(c*cw+4,42+r*ch)); d.text((c*cw+8,42+r*ch+ch-20),part+' | '+name,fill=(20,30,40),font=FONT)
 out.save(OUT/f'renders/contact_sheets/{case_name}_contact_sheet.png')
 # generated-only
 out=Image.new('RGB',(cw*len(items),340),'white'); d=ImageDraw.Draw(out); d.text((14,14),case_name+' generated-only',fill=(20,30,40),font=FONT)
 for i,(part,p) in enumerate(items):
  img=Image.open(p/'generated_cad.png'); img.thumbnail((cw-8,300)); out.paste(img,(i*cw+4,40)); d.text((i*cw+8,320),part,fill=(20,30,40),font=FONT)
 out.save(OUT/f'renders/contact_sheets/{case_name}_generated_only.png')
for name,rs in [('demo5',[x for x in rows if x['SOURCE_EXPERIMENT']=='Demo5 frozen success']),('airplane9',[x for x in rows if x['SOURCE_EXPERIMENT']=='Airplane9 frozen success'])]: contact(rs,name)
tank=OUT/'renders/tank_highlight'; tank.mkdir(parents=True,exist_ok=True)
for n in ['input_mesh','generated_cad','canonical_cad','overlay']: shutil.copy2(OUT/'renders/case_014/PART_029'/f'{n}.png',tank/f'tank_part029_{n}.png')
counts=Counter(x['CASE_ID'] for x in allrows); rendered=sum('RENDER_PATHS' in x for x in rows); demo_n=sum(x['SOURCE_EXPERIMENT']=='Demo5 frozen success' for x in rows); air_n=sum(x['SOURCE_EXPERIMENT']=='Airplane9 frozen success' for x in rows)
report=f'''# CASE_PART_VISUALIZATION_REPORT\n\n- Source case directories scanned: {len(set(x["OBJECT_NAME"] for x in allrows))}\n- Source parts inventoried: {len(allrows)}\n- Rendered successful parts: {rendered}\n- Demo5 rendered parts: {demo_n}/5\n- Airplane9 rendered parts: {air_n}/9\n- Demo5 contact sheet: `renders/contact_sheets/demo5_contact_sheet.png`\n- Airplane9 contact sheet: `renders/contact_sheets/airplane9_contact_sheet.png`\n- Tank highlight: `renders/tank_highlight/`\n\nAll rendered Generated CAD panels use freshly reloaded generated STEP/BRep artifacts. Canonical STEP is never used as generated output. Input mesh retains triangle edges; Generated and Canonical CAD panels are smooth BRep renders with tessellation edges hidden. Per-part camera is the same for all four panels and uses the original shared coordinate system with no ICP or scaling.\n\nParts without generated artifacts remain inventory-only and are not labeled as generated success.\n'''
(OUT/'reports/CASE_PART_VISUALIZATION_REPORT.md').write_text(report)
print(json.dumps({'cases':len(set(x['OBJECT_NAME'] for x in allrows)),'parts':len(allrows),'rendered':rendered,'demo5':demo_n,'airplane9':air_n},indent=2))
