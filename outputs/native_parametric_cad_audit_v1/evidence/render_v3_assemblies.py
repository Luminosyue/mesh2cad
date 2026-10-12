import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
from pathlib import Path
import json,hashlib,colorsys,html
from concurrent.futures import ProcessPoolExecutor
import numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
V=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_reject_repair_v3')
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_v3_assembly_visualizations')
OBJECTS=json.loads((V/'manifests/objects.json').read_text());ROWS=json.loads((V/'manifests/cases.json').read_text())
NAMES=['Toaster (2 slice)','Pressure cooker','Build-a-robot','School bus','Fire truck','Refrigerator','Sink','Sofa','Swing','Android Lego','Kitchen rack','Wooden wine rack','Utility cart','Coat rack / shoe bench','Kettle','White chair','Glass cabinet','Toaster (4 slice)','Taxi / police car','Object 20']
STATUS={'STRICT_ACCEPT':[45,175,115],'NEAR_PASS':[235,167,40],'REJECT':[215,75,80]}
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
def view(az=35,el=22):
 a=np.deg2rad(az);e=np.deg2rad(el);z=np.array([np.cos(e)*np.sin(a),np.sin(e),np.cos(e)*np.cos(a)]);x=np.cross([0,1,0],z);x/=np.linalg.norm(x);y=np.cross(z,x);return np.column_stack([x,y,z])
def sample(mesh,n,seed):
 p,idx=trimesh.sample.sample_surface(mesh,n,seed=seed);return p,mesh.face_normals[idx]
def render(points,normals,colors,title,subtitle,center,span,R,size=800):
 im=Image.new('RGB',(size,size),(247,249,252));pixels=np.asarray(im).copy().reshape(-1,3);depth=np.full(size*size,-np.inf,dtype=np.float32);q=(points-center)@R;xy=q[:,:2]*(size*.78/span)+[size*.5,size*.54];xy[:,1]=size*1.08-xy[:,1];xy=np.rint(xy).astype(int)
 ns=normals@R;light=np.array([-.35,.5,.79]);light/=np.linalg.norm(light);shade=.34+.56*np.maximum(ns@light,0)+.1*np.maximum(ns@(-light),0);color=np.asarray(colors)
 if color.ndim==1:color=np.tile(color,(len(points),1))
 color=np.clip(color*shade[:,None],0,255).astype(np.uint8);order=np.argsort(q[:,2])[::-1]
 for dx in [-1,0,1]:
  for dy in [-1,0,1]:
   xx=xy[order,0]+dx;yy=xy[order,1]+dy;valid=(xx>3)&(xx<size-4)&(yy>105*size/800)&(yy<size-45*size/800);ids=order[valid];flat=yy[valid]*size+xx[valid];unique,first=np.unique(flat,return_index=True);idx=ids[first];closer=q[idx,2]>depth[unique];dest=unique[closer];src=idx[closer];depth[dest]=q[src,2];pixels[dest]=color[src]
 im=Image.fromarray(pixels.reshape(size,size,3));d=ImageDraw.Draw(im);d.text((24*size/800,18*size/800),title,font=font(int(27*size/800)),fill='#182536');d.text((24*size/800,58*size/800),subtitle,font=font(int(17*size/800)),fill='#536477');return im
def process(obj):
 oid=obj['object_id'];index=int(oid.split('_')[-1]);name=NAMES[index];d=O/oid;d.mkdir(parents=True,exist_ok=True);source=trimesh.load(obj['canonical_path'],force='mesh',process=True);parts=[];evidence=[];counts={k:0 for k in STATUS};scene=trimesh.Scene();trans_error=[]
 for row in [r for r in ROWS if r['object_id']==oid]:
  p=V/'cases'/row['case_id'];r=json.loads((p/'result.json').read_text());prov=json.loads((p/'source/provenance.json').read_text());T=np.asarray(prov['world_transform']);inv=np.asarray(prov['local_transform']);trans_error.append(float(np.max(np.abs(T@inv-np.eye(4)))));mesh=trimesh.load(p/'cad/cad_mesh.ply',force='mesh',process=True);mesh.apply_transform(T);st=r['v3_status'];counts[st]+=1;pid=row['part_id'];col=(np.asarray(colorsys.hsv_to_rgb((int(pid.split('_')[-1])*.61803398875)%1,.55,.88))*255).astype(np.uint8);display=mesh.copy();display.visual.face_colors=np.r_[col,255];scene.add_geometry(display,geom_name=pid+'_'+st,node_name=pid);parts.append((mesh,st,col,pid));evidence.append({'case_id':row['case_id'],'status':st,'cad_mesh_path':str(p/'cad/cad_mesh.ply'),'cad_mesh_sha256':sha(p/'cad/cad_mesh.ply'),'world_transform':T.tolist(),'step_path':str(p/'cad/cad.step')})
 assert max(trans_error)<1e-9
 scene.export(d/'assembly_preview.glb');merged=trimesh.util.concatenate([x[0] for x in parts]);merged.export(d/'assembly_preview.ply')
 srcp,srcn=sample(source,190000,20261007+index);total=sum(m.area for m,_,_,_ in parts);points=[];normals=[];statuscolors=[];partcolors=[];exploded=[];center=source.bounds.mean(0)
 for i,(m,st,col,pid) in enumerate(parts):
  p,n=sample(m,max(800,int(190000*m.area/total)),2026100700+index*100+i);points.append(p);normals.append(n);statuscolors.append(np.tile(STATUS[st],(len(p),1)));partcolors.append(np.tile(col,(len(p),1)));delta=m.bounds.mean(0)-center;norm=np.linalg.norm(delta);shift=delta/max(norm,.10)*max(source.extents)*.22;exploded.append(p+shift)
 cp=np.vstack(points);cn=np.vstack(normals);sc=np.vstack(statuscolors);pc=np.vstack(partcolors);ep=np.vstack(exploded);R=view();allbounds=np.vstack([source.bounding_box.vertices,merged.bounding_box.vertices]);span=float(max(np.ptp((allbounds-center)@R,axis=0)[:2]));summary=f"{len(parts)} parts | Strict {counts['STRICT_ACCEPT']} | Near {counts['NEAR_PASS']} | Reject {counts['REJECT']}"
 original=render(srcp,srcn,[85,160,225],name+' - source mesh','Original object in its canonical coordinates',center,span,R)
 assembly=render(cp,cn,[115,163,198],name+' - CAD assembly','All candidates at original part positions; diagnostic preview',center,span,R)
 status=render(cp,cn,sc,'CAD fitting status',summary,center,span,R);dr=ImageDraw.Draw(status);x=24
 for label,c in [('Strict',[45,175,115]),('Near',[235,167,40]),('Reject',[215,75,80])]:dr.rectangle((x,766,x+15,781),fill=tuple(c));dr.text((x+23,763),label,font=font(18),fill='#27364a');x+=145
 exp_span=float(max(np.ptp((ep-center)@R,axis=0)[:2]));exp=render(ep,cn,pc,name+' - exploded parts','Part colors; offsets are for visualization only',center,exp_span,R)
 comparison=Image.new('RGB',(1600,800),'white');comparison.paste(original,(0,0));comparison.paste(assembly,(800,0));comparison.save(d/'source_vs_assembly.png');overview=Image.new('RGB',(1600,1600),'white')
 for i,panel in enumerate([original,assembly,status,exp]):overview.paste(panel,((i%2)*800,(i//2)*800))
 overview.save(d/'overview.png');assembly.save(d/'assembly.png');status.save(d/'status.png');exp.save(d/'exploded.png');original.save(d/'source.png')
 # Additional view uses the same real coordinates and all the same part candidates.
 R2=view(-40,18);span2=float(max(np.ptp((allbounds-center)@R2,axis=0)[:2]));render(cp,cn,[115,163,198],name+' - reverse view','All candidates; not an accepted full CAD assembly',center,span2,R2).save(d/'assembly_reverse.png')
 meta={'object_id':oid,'name':name,'original_name':obj['name'],'part_n':len(parts),'counts':counts,'preview_only':True,'includes_rejected_parts':counts['REJECT']>0,'source_path':obj['canonical_path'],'source_sha256':sha(Path(obj['canonical_path'])),'max_transform_roundtrip_error':max(trans_error),'view_matrix':R.tolist(),'center':center.tolist(),'common_source_cad_span':span,'parts':evidence};dump(d/'manifest.json',meta);print(oid,summary,flush=True);return meta

if __name__=='__main__':
 O.mkdir(exist_ok=True);(O/'scripts').mkdir(exist_ok=True)
 with ProcessPoolExecutor(max_workers=8) as pool:records=list(pool.map(process,OBJECTS))
 dump(O/'manifest.json',{'objects':records,'object_n':len(records),'part_n':sum(x['part_n'] for x in records),'interpretation':'Diagnostic transformed visualization of all V3 part candidates; includes Near and Reject. No Boolean fusion, no new fitting, no acceptance-gate override. Original V3/V2 outputs unchanged.'})
 contact=Image.new('RGB',(2000,1600),(247,249,252))
 for i,r in enumerate(records):contact.paste(Image.open(O/r['object_id']/'assembly.png').resize((400,400)),((i%5)*400,(i//5)*400))
 contact.save(O/'all_20_assemblies.png')
 focus=Image.new('RGB',(1600,1600),(247,249,252))
 for i,idx in enumerate([13,14,15,16]):focus.paste(Image.open(O/f'object_{idx:05d}'/'assembly.png'),((i%2)*800,(i//2)*800))
 focus.save(O/'coat_rack_kettle_chair_cabinet.png')
 page='''<!doctype html><meta charset="utf-8"><title>V3 CAD 装配可视化</title><style>body{max-width:1400px;margin:30px auto;padding:0 20px;background:#f7f9fc;color:#182536;font:16px system-ui}img{width:100%;height:auto;border-radius:8px}section{margin:40px 0}a{color:#1767ad;margin-right:20px}p{line-height:1.7}</style><h1>V3 部件 CAD 与装配预览</h1><p>全部 20 个物体、209 个部件。按原始变换拼回位置，包含 Near 与 Reject 候选；属于诊断预览，不代表完整 CAD 已通过验收。绿色 Strict，黄色 Near，红色 Reject。爆炸图中的位移仅用于展示。</p><img src="coat_rack_kettle_chair_cabinet.png"><h2>全部装配概览</h2><img src="all_20_assemblies.png">'''
 for r in records:
  oid=r['object_id'];page+=f'<section><h2>{oid} — {html.escape(r["name"])}</h2><p>{r["counts"]}</p><a href="{oid}/source_vs_assembly.png">原始 mesh / CAD 对比</a><a href="{oid}/assembly.png">装配图</a><a href="{oid}/assembly_reverse.png">另一视角</a><a href="{oid}/exploded.png">爆炸图</a><a href="{oid}/assembly_preview.glb">下载 GLB 场景</a><img loading="lazy" src="{oid}/overview.png"></section>'
 (O/'index.html').write_text(page,encoding='utf-8');print('VISUALIZATION_COMPLETE',len(records),flush=True)
