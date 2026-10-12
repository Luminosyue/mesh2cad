#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,shutil,traceback,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image,ImageDraw

LIMIT=100
DIRS=['audit','extracted_parts','selected_parts','manifests','renders','reports','logs','scripts']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def decode(a):
 if isinstance(a,np.ndarray):
  if a.dtype==np.uint8:return a.tobytes()
  if a.dtype.kind=='S':return a.tobytes().rstrip(b'\x00')
  if a.shape==() and a.dtype.kind in ('S','V'):
   x=a.item();return bytes(x) if not isinstance(x,bytes) else x
 if isinstance(a,(bytes,bytearray,memoryview,np.bytes_)):return bytes(a)
 raise TypeError(f'unsupported encoded PLY dtype={getattr(a,"dtype",None)} shape={getattr(a,"shape",None)}')
def classify_key(k):
 s=Path(k).stem.lower()
 if 'part' in s:return 'part'
 if any(x in s for x in ('full','whole','object')):return 'full'
 return 'unknown'
def mesh_from_bytes(b):return trimesh.load(io.BytesIO(b),file_type='ply',process=False)
def edge_stats(f):
 if not len(f):return 0,0
 e=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);e.sort(axis=1);_,cnt=np.unique(e,axis=0,return_counts=True);return int(np.sum(cnt==1)),int(np.sum(cnt>2))
def mesh_audit(m):
 v=np.asarray(m.vertices);f=np.asarray(m.faces,dtype=np.int64);empty=len(v)==0 or len(f)==0;bbox=np.ptp(v,axis=0) if len(v) else np.zeros(3);eps=max(float(np.max(bbox)),1.)*1e-10;boundary,nonman=edge_stats(f)
 rep=np.sort(f,axis=1) if len(f) else f;dup=int(len(rep)-len(np.unique(rep,axis=0))) if len(f) else 0
 if len(f):
  tri=v[f];area2=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1);deg=int(np.sum((area2<=eps*eps)|(f[:,0]==f[:,1])|(f[:,1]==f[:,2])|(f[:,0]==f[:,2])))
 else:deg=0
 try:comps=int(len(trimesh.graph.connected_components(m.face_adjacency,nodes=np.arange(len(f))))) if len(f) else 0
 except:comps=0
 wt=bool(m.is_watertight);wind=bool(m.is_winding_consistent);volok=bool(m.is_volume);vol=float(m.volume) if math.isfinite(float(m.volume)) else 0.;area=float(m.area)
 reasons=[]
 if empty:reasons.append('EMPTY')
 if np.any(bbox<=eps):reasons.append('DEGENERATE_BBOX')
 if not wt:reasons.append('NOT_WATERTIGHT')
 if not wind:reasons.append('WINDING_INCONSISTENT')
 if not volok:reasons.append('NOT_VOLUME')
 if boundary>0:reasons.append('BOUNDARY_EDGES')
 if nonman>0:reasons.append('NONMANIFOLD_EDGES')
 strict=not reasons and len(f)>0 and len(v)>0 and vol>0
 if vol<=0 and 'NOT_VOLUME' not in reasons:reasons.append('NOT_VOLUME');strict=False
 return {'vertices':int(len(v)),'faces':int(len(f)),'components':comps,'connected_component_count':comps,'is_watertight':wt,'is_winding_consistent':wind,'is_volume':volok,'bbox_min':v.min(0).tolist() if len(v) else [0,0,0],'bbox_max':v.max(0).tolist() if len(v) else [0,0,0],'bbox_size':bbox.tolist(),'bbox_x':float(bbox[0]),'bbox_y':float(bbox[1]),'bbox_z':float(bbox[2]),'surface_area':area,'volume':vol,'euler_number':int(m.euler_number),'boundary_edges':boundary,'nonmanifold_edges':nonman,'degenerate_face_count':deg,'duplicate_face_count':dup,'strict_watertight_valid':strict,'invalid_reason':';'.join(reasons)}
def descriptors(m,r):
 v=np.asarray(m.vertices);c=v-v.mean(0);vals,vecs=np.linalg.eigh(np.cov(c.T));o=np.argsort(vals)[::-1];vals,vecs=vals[o],vecs[:,o];dims=np.ptp(c@vecs,axis=0);pos=dims[dims>1e-12];aspect=float(pos.max()/pos.min()) if len(pos) else 0
 normals=np.asarray(m.face_normals);areas=np.asarray(m.area_faces);q=np.round(np.abs(normals),1);_,inv=np.unique(q,axis=0,return_inverse=True);bins=np.bincount(inv,weights=areas);planar=float(np.sort(bins)[-min(6,len(bins)):].sum()/max(areas.sum(),1e-30))
 axis=vecs[:,0];t=c@axis;rad=np.linalg.norm(c-np.outer(t,axis),axis=1);rot=max(0.,1-float(rad.std())/max(float(rad.mean()),1e-30));cyl=float(np.average(np.abs(normals@axis)<.25,weights=areas)) if areas.sum() else 0
 try:conv=float(m.volume/m.convex_hull.volume) if m.convex_hull.volume>0 else 0
 except:conv=0
 compact=float(m.volume/np.prod(m.extents)) if np.prod(m.extents)>0 else 0
 if cyl>.55 and rot>.55:cat='REVOLVE_CYLINDER_LIKE'
 elif planar>.62 and conv>.55:cat='BOX_BOOLEAN_LIKE'
 elif planar>.42:cat='EXTRUDE_LIKE'
 elif compact<.18 or min(dims)<.12*max(dims):cat='SHELL_LIKE'
 else:cat='HARDER_FREEFORM'
 return {'pca_eigenvalues':vals.tolist(),'pca_axes':vecs.T.tolist(),'bbox_aspect_ratio':aspect,'convexity':conv,'compactness':compact,'planar_tendency':planar,'rotational_symmetry_tendency':rot,'cylindrical_tendency':cyl,'geometry_category':cat}
def render(m,out):
 pts=m.sample(min(25000,max(4000,len(m.faces)*2)));c=(m.bounds[0]+m.bounds[1])/2;q=pts-c;az,el=np.radians([35,25]);view=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);up=np.array([0.,0.,1.]);right=np.cross(view,up);right/=np.linalg.norm(right);up=np.cross(right,view);xy=np.c_[q@right,q@up];scale=430/max(np.ptp(xy[:,0]),np.ptp(xy[:,1]),1e-12);xy=xy*scale+250
 im=Image.new('RGB',(500,500),'white');d=ImageDraw.Draw(im)
 for x,y in xy[::2]:d.ellipse((x-1,y-1,x+1,y+1),fill=(55,130,210))
 im.save(out)
def write_csv(p,rows,fields=None):
 rows=list(rows);fields=fields or (list(rows[0]) if rows else [])
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--npz-root',type=Path,required=True);ap.add_argument('--output-root',type=Path,required=True);a=ap.parse_args();root=a.npz_root.resolve();out=a.output_root.resolve()
 for d in DIRS:(out/d).mkdir(parents=True,exist_ok=True)
 paths=sorted(root.rglob('*.npz'))[:LIMIT]
 if not paths:raise SystemExit('NO_NPZ_FOUND')
 # Required schema inspection on lexicographically first NPZ.
 sample={'npz_path':str(paths[0]),'sha256':sha(paths[0]),'keys':[]}
 try:
  with np.load(paths[0],allow_pickle=False) as z:
   for k in z.files:
    x=z[k];sample['keys'].append({'key':k,'dtype':str(x.dtype),'shape':list(x.shape),'nbytes':int(x.nbytes),'encoding_kind':x.dtype.kind,'semantic_class':classify_key(k)})
  sample['status']='OK'
 except Exception as e:sample.update(status='LOAD_FAIL',error=repr(e))
 dump(out/'audit/NPZ_SCHEMA_SAMPLE.json',sample);(out/'audit/NPZ_SCHEMA_SAMPLE.md').write_text('# NPZ schema sample\n\n'+f"- Path: {paths[0]}\n- Status: {sample['status']}\n\n"+'\n'.join(f"- `{x['key']}`: dtype={x['dtype']}, shape={x['shape']}, nbytes={x['nbytes']}, class={x['semantic_class']}" for x in sample.get('keys',[]))+'\n',encoding='utf-8')
 npz_rows=[];parts=[];per_npz=[]
 log=(out/'logs/audit.log').open('w',encoding='utf-8',buffering=1)
 for idx,p in enumerate(paths):
  nr={'npz_index':idx,'npz_path':str(p),'npz_filename':p.name,'sha256':sha(p),'key_count':0,'has_full_mesh':False,'part_key_count':0,'unknown_key_count':0,'status':'LOAD_FAIL'};counts={'total':0,'strict':0}
  try:
   with np.load(p,allow_pickle=False) as z:
    keys=z.files;classes={k:classify_key(k) for k in keys};nr.update(key_count=len(keys),has_full_mesh=any(x=='full' for x in classes.values()),part_key_count=sum(x=='part' for x in classes.values()),unknown_key_count=sum(x=='unknown' for x in classes.values()),unknown_keys=';'.join(k for k,v in classes.items() if v=='unknown'),status='OK')
    npzid=p.stem;destdir=out/'extracted_parts'/npzid;destdir.mkdir(parents=True,exist_ok=True)
    for key in keys:
     if classes[key]!='part':continue
     counts['total']+=1;partid=Path(key).stem;dest=destdir/(partid+'.ply');base={'npz_id':npzid,'npz_path':str(p),'part_key':key,'part_id':partid,'part_path':str(dest),'scene_geometry_n':0,'load_success':False}
     try:
      b=decode(z[key]);dest.write_bytes(b);base['raw_ply_sha256']=hashlib.sha256(b).hexdigest();obj=mesh_from_bytes(b)
      if isinstance(obj,trimesh.Scene):
       base['scene_geometry_n']=len(obj.geometry)
       if len(obj.geometry)!=1:base.update(invalid_reason='MULTI_GEOMETRY_UNRESOLVED',strict_watertight_valid=False);parts.append(base);continue
       obj=next(iter(obj.geometry.values()))
      if not isinstance(obj,trimesh.Trimesh):raise TypeError(type(obj).__name__)
      base['scene_geometry_n']=1;base['load_success']=True;base.update(mesh_audit(obj));base.update(descriptors(obj,base));counts['strict']+=int(base['strict_watertight_valid']);parts.append(base)
     except Exception as e:
      base.update(strict_watertight_valid=False,invalid_reason='LOAD_FAIL',error=repr(e));parts.append(base);log.write(f'{p} {key} LOAD_FAIL {e!r}\n')
  except Exception as e:nr['status']='LOAD_FAIL';nr['error']=repr(e);log.write(f'[{idx}] {p} NPZ_LOAD_FAIL {e!r}\n')
  npz_rows.append(nr);per_npz.append({'npz_index':idx,'npz_id':p.stem,'npz_path':str(p),'part_n':counts['total'],'strict_watertight_n':counts['strict'],'status':nr['status']});log.write(f'[{idx+1}/{len(paths)}] {p.name} status={nr["status"]} parts={counts["total"]} strict={counts["strict"]}\n')
 log.close();write_csv(out/'manifests/NPZ100_MANIFEST.csv',npz_rows)
 fields=['npz_id','npz_path','part_key','part_id','part_path','raw_ply_sha256','scene_geometry_n','load_success','vertices','faces','components','connected_component_count','is_watertight','is_winding_consistent','is_volume','boundary_edges','nonmanifold_edges','degenerate_face_count','duplicate_face_count','euler_number','surface_area','volume','bbox_min','bbox_max','bbox_size','bbox_x','bbox_y','bbox_z','strict_watertight_valid','invalid_reason','geometry_category','bbox_aspect_ratio','convexity','compactness','planar_tendency','rotational_symmetry_tendency','cylindrical_tendency','error']
 write_csv(out/'manifests/PART_AUDIT_ALL.csv',parts,fields)
 with (out/'manifests/PART_AUDIT_ALL.jsonl').open('w',encoding='utf-8') as f:
  for r in parts:f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')
 strict=[r for r in parts if r.get('strict_watertight_valid')];eligible=[r for r in strict if r['faces']>=100 and r['vertices']>=50]
 selected=[];used=set();cats=['BOX_BOOLEAN_LIKE','EXTRUDE_LIKE','REVOLVE_CYLINDER_LIKE','SHELL_LIKE','HARDER_FREEFORM']
 def score(r):return (r['components']!=1,-math.log10(r['faces']+1),r['npz_id'],r['part_id'])
 for cat in cats:
  cand=sorted([r for r in eligible if r['geometry_category']==cat],key=score)
  for r in cand:
   if len([x for x in selected if x['geometry_category']==cat])>=4:break
   if r['npz_id'] not in used:selected.append(r);used.add(r['npz_id'])
  for r in cand:
   if len([x for x in selected if x['geometry_category']==cat])>=4:break
   if r not in selected:selected.append(r);used.add(r['npz_id'])
 for r in sorted(eligible,key=lambda x:(x['npz_id'] in used,)+score(x)):
  if len(selected)>=20:break
  if r not in selected:selected.append(r);used.add(r['npz_id'])
 selected=selected[:20]
 pilots=[];recheck=[]
 if len(strict)>=20 and len(selected)==20:
  for i,r in enumerate(selected):
   cid=f"HY3D_{r['npz_id']}_PART_{r['part_id'].replace('part_','')}";link=out/'selected_parts'/f'{cid}.ply'
   if link.exists() or link.is_symlink():link.unlink()
   try:link.symlink_to(Path(r['part_path']))
   except:shutil.copy2(r['part_path'],link)
   x={'case_index':i,'case_id':cid,'npz_id':r['npz_id'],'source_npz':r['npz_path'],'part_key':r['part_key'],'source_part_path':str(link),'sha256':sha(link),'vertices':r['vertices'],'faces':r['faces'],'is_watertight':r['is_watertight'],'is_volume':r['is_volume'],'volume':r['volume'],'surface_area':r['surface_area'],'bbox_size_x':r['bbox_x'],'bbox_size_y':r['bbox_y'],'bbox_size_z':r['bbox_z'],'geometry_category':r['geometry_category']};pilots.append(x)
   try:m=mesh_from_bytes(link.read_bytes());rr=mesh_audit(m);ok=rr['strict_watertight_valid'] and sha(link)==x['sha256'];recheck.append({'case_id':cid,'path':str(link),'sha256':sha(link),**rr,'pass':bool(ok)});render(m,out/'renders'/f'{cid}_iso.png')
   except Exception as e:recheck.append({'case_id':cid,'pass':False,'error':repr(e)})
 pilot_fields=['case_index','case_id','npz_id','source_npz','part_key','source_part_path','sha256','vertices','faces','is_watertight','is_volume','volume','surface_area','bbox_size_x','bbox_size_y','bbox_size_z','geometry_category']
 write_csv(out/'manifests/PILOT20.csv',pilots,pilot_fields);dump(out/'audit/PILOT20_RECHECK.json',{'pilot_n':len(pilots),'pass_n':sum(x['pass'] for x in recheck),'results':recheck})
 # Contact sheet.
 if pilots:
  sheet=Image.new('RGB',(2000,2500),'white');d=ImageDraw.Draw(sheet)
  for i,r in enumerate(pilots):
   x=(i%4)*500;y=(i//4)*500;im=Image.open(out/'renders'/f"{r['case_id']}_iso.png").convert('RGB');im.thumbnail((480,400));sheet.paste(im,(x,y));d.text((x+8,y+405),r['case_id'][:52],fill='black');d.text((x+8,y+425),f"{r['geometry_category']} faces={r['faces']}",fill='black');d.text((x+8,y+445),f"volume={r['volume']:.6g} watertight=YES",fill='black')
  sheet.save(out/'reports/PILOT20_CONTACT_SHEET.png')
 total=len(parts);loadn=sum(r.get('load_success',False) for r in parts);strictn=len(strict);reason=Counter()
 for r in parts:
  for z in r.get('invalid_reason','').split(';'):
   if z:reason[z]+=1
 passn=sum(x['pass'] for x in recheck);gate=strictn>=20 and passn==20
 summary={'NPZ_ROOT':str(root),'NPZ_AUDIT_N':len(paths),'TOTAL_PART_N':total,'LOAD_SUCCESS_N':loadn,'STRICT_WATERTIGHT_N':strictn,'STRICT_WATERTIGHT_RATE':strictn/total if total else 0,'NOT_WATERTIGHT_N':reason['NOT_WATERTIGHT'],'NOT_VOLUME_N':reason['NOT_VOLUME'],'BOUNDARY_EDGE_N':reason['BOUNDARY_EDGES'],'NONMANIFOLD_N':reason['NONMANIFOLD_EDGES'],'LOAD_FAIL_PART_N':reason['LOAD_FAIL'],'NPZ_LOAD_FAIL_N':sum(r['status']!='OK' for r in npz_rows),'PILOT20_N':len(pilots),'PILOT_UNIQUE_OBJECTS':len({r['npz_id'] for r in pilots}),'PILOT20_RECHECK_PASS':f'{passn}/{len(pilots)}','PILOT_CATEGORY_DISTRIBUTION':dict(Counter(r['geometry_category'] for r in pilots)),'CURRENT_GATE':'HY3D_WATERTIGHT_AUDIT_PASS' if gate else 'HY3D_WATERTIGHT_AUDIT_REVIEW','NEXT_ALLOWED_STAGE':'HY3D_LLM_CAD_PILOT20' if gate else 'NONE','per_npz':per_npz,'invalid_reason_counts':dict(reason)};dump(out/'reports/WATERTIGHT_AUDIT_SUMMARY.json',summary)
 md=['# Watertight audit summary','']+[f'- {k}: {summary[k]}' for k in ['NPZ_ROOT','NPZ_AUDIT_N','TOTAL_PART_N','LOAD_SUCCESS_N','STRICT_WATERTIGHT_N','STRICT_WATERTIGHT_RATE','NOT_WATERTIGHT_N','NOT_VOLUME_N','BOUNDARY_EDGE_N','NONMANIFOLD_N','NPZ_LOAD_FAIL_N','PILOT20_N','PILOT_UNIQUE_OBJECTS','PILOT20_RECHECK_PASS','PILOT_CATEGORY_DISTRIBUTION','CURRENT_GATE','NEXT_ALLOWED_STAGE']]+['','## Per NPZ','']+[f"- {x['npz_index']} {x['npz_id']}: parts={x['part_n']}, strict={x['strict_watertight_n']}, status={x['status']}" for x in per_npz];(out/'reports/WATERTIGHT_AUDIT_SUMMARY.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 report=f"""# HY3D Part Watertight Audit V1

## Dataset

NPZ root: {root}. The first {len(paths)} files in full-path lexical order were audited. They contain {total} recognized part keys.

## NPZ schema

The first NPZ contains uint8-encoded PLY bytes with one `full.ply` key and `part_N.ply` keys. Full meshes were excluded from part statistics. Unknown keys are preserved in NPZ100_MANIFEST.csv. {summary['NPZ_LOAD_FAIL_N']} of the fixed NPZ100 could not be opened and were not replaced.

## Watertight audit

{loadn} parts loaded successfully. Strict valid: {strictn}/{total} ({summary['STRICT_WATERTIGHT_RATE']:.6f}). NOT_WATERTIGHT={reason['NOT_WATERTIGHT']}, NOT_VOLUME={reason['NOT_VOLUME']}, BOUNDARY_EDGES={reason['BOUNDARY_EDGES']}, NONMANIFOLD_EDGES={reason['NONMANIFOLD_EDGES']}.

## Pilot20

Pilot count={len(pilots)}, unique objects={summary['PILOT_UNIQUE_OBJECTS']}, independent recheck={passn}/{len(pilots)}. Actual category distribution: {summary['PILOT_CATEGORY_DISTRIBUTION']}.

## Data integrity

Extracted PLY files are byte-for-byte copies decoded from NPZ arrays. SHA-256 is recorded. No repair, remesh, simplification, smoothing, welding, hole filling, or source mutation was performed.

## Conclusion

{'At least 20 original strict-watertight parts exist and the fixed Pilot20 is eligible for a later strict Volume-IoU Mesh-to-CAD experiment.' if gate else 'The fixed NPZ100 sample did not satisfy the strict gate; watertight criteria were not relaxed.'}
""";(out/'reports/FINAL_REPORT.md').write_text(report,encoding='utf-8')
 print('HY3D_PART_WATERTIGHT_AUDIT_V1\n');
 for k in ['NPZ_ROOT','NPZ_AUDIT_N','TOTAL_PART_N','LOAD_SUCCESS_N','STRICT_WATERTIGHT_N','STRICT_WATERTIGHT_RATE','NOT_WATERTIGHT_N','NOT_VOLUME_N','BOUNDARY_EDGE_N','NONMANIFOLD_N','PILOT20_N','PILOT_UNIQUE_OBJECTS','PILOT20_RECHECK_PASS']:print(f'{k}={summary[k]}')
 print(f"\nPART_MANIFEST={out/'manifests/PART_AUDIT_ALL.csv'}\nPILOT20_MANIFEST={out/'manifests/PILOT20.csv'}\nFINAL_REPORT={out/'reports/FINAL_REPORT.md'}\n\nCURRENT_GATE={summary['CURRENT_GATE']}\nNEXT_ALLOWED_STAGE={summary['NEXT_ALLOWED_STAGE']}")
 return 0 if gate else 2
if __name__=='__main__':raise SystemExit(main())
