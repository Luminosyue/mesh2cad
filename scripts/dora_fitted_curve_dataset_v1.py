#!/usr/bin/env python3
"""Build DORA fitted curves + STEP B-Rep supervision for the frozen V3 train800.

All writes are isolated below ours3/dora_fitted_curve_dataset_v1.  This script
never regenerates DSL, STEP, tessellation, or Dora assets, and does not train.
"""
from __future__ import annotations

import argparse, hashlib, json, math, sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.interpolate import splprep, splev

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0] = [str(ROOT / 'scripts')]
from curve_token_v1.extract_brep_curves import extract_curves_from_step
from curve_token_v1.occ_curve_v1 import load_step_shape, make_adaptor, arclength_params, eval_point, eval_point_tangent

OUT = ROOT / 'ours3/dora_fitted_curve_dataset_v1'
COHORT = OUT / 'V3_MESH_DORA_COHORT_V1.jsonl'
N = 32
MIN_REL_LEN = 1e-5
FIT_TOL_REL = 5e-3  # Tessellated DORA geometry; recorded, never hidden.
MATCH_DIST_REL = 8e-3
MATCH_COVERAGE = .85
MATCH_TANGENT = .75

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def jdump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def unit(v):
 v=np.asarray(v,float); n=np.linalg.norm(v); return v/max(n,1e-12)
def objverts(path):
 a=[]
 for ln in Path(path).read_text(errors='ignore').splitlines():
  if ln.startswith('v '): a.append([float(x) for x in ln.split()[1:4]])
 return np.asarray(a,float)
def qstats(a):
 a=np.asarray(a,float); a=a[np.isfinite(a)]
 return {} if not len(a) else {'min':float(a.min()),'mean':float(a.mean()),'median':float(np.median(a)),'p10':float(np.percentile(a,10)),'p90':float(np.percentile(a,90)),'max':float(a.max())}

def graph_from_dora(z):
 edges=[]; xyz={}
 for (a,b),p,q in zip(z['edge_vertex_indices'],z['edge_xyz0'],z['edge_xyz1']):
  a,b=int(a),int(b); p,q=np.asarray(p,float),np.asarray(q,float)
  for k,v in ((a,p),(b,q)):
   if k in xyz and np.linalg.norm(xyz[k]-v)>1e-6: raise RuntimeError(f'inconsistent DORA vertex {k}')
   xyz[k]=v
  if a!=b: edges.append((min(a,b),max(a,b)))
 edges=sorted(set(edges)); adj=defaultdict(list)
 for a,b in edges: adj[a].append(b); adj[b].append(a)
 for v in adj: adj[v].sort()
 return xyz,adj,edges

def extract_chains(xyz,adj,edges):
 used=set(); chains=[]
 def ek(a,b): return (min(a,b),max(a,b))
 def walk(a,b):
  path=[a,b]; used.add(ek(a,b)); prev,cur=a,b
  while len(adj[cur])==2:
   nxt=adj[cur][0] if adj[cur][1]==prev else adj[cur][1]
   if ek(cur,nxt) in used: break
   used.add(ek(cur,nxt)); path.append(nxt); prev,cur=cur,nxt
  return path
 for a in sorted(adj):
  if len(adj[a])!=2:
   for b in adj[a]:
    if ek(a,b) not in used: chains.append((walk(a,b),False))
 for a,b in edges:
  if ek(a,b) in used: continue
  # remaining connected component is all degree 2: canonical closed loop.
  start=min(a,b); nxt=min(adj[start]); path=[start,nxt]; used.add(ek(start,nxt)); prev,cur=start,nxt
  while cur!=start:
   nn=adj[cur][0] if adj[cur][1]==prev else adj[cur][1]
   if ek(cur,nn) in used and nn!=start: raise RuntimeError('non-simple residual component')
   used.add(ek(cur,nn)); path.append(nn); prev,cur=cur,nn
  chains.append((path,True))
 out=[]
 for i,(ids,closed) in enumerate(chains):
  pts=np.asarray([xyz[v] for v in ids],float); L=float(np.linalg.norm(np.diff(pts,axis=0),axis=1).sum())
  out.append({'chain_id':i,'vertex_ids':ids,'closed_loop':closed,'points':pts,'length':L})
 return out

def plane(pts):
 c=pts.mean(0); _,_,vh=np.linalg.svd(pts-c,full_matrices=False); return c,unit(vh[0]),unit(vh[1]),unit(vh[2])
def linefit(p):
 c=p.mean(0); _,_,vh=np.linalg.svd(p-c,full_matrices=False); d=unit(vh[0]); t=(p-c)@d
 if t[-1]<t[0]: d=-d;t=-t
 o=c+t.min()*d; pred=o+(t-t.min())[:,None]*d; r=np.linalg.norm(pred-p,axis=1)
 return {'type':'LINE','origin':o,'direction':d,'length':float(t.max()-t.min()),'rms':float(np.sqrt(np.mean(r*r))),'max':float(r.max())}
def circlefit(p,closed):
 c,e1,e2,n=plane(p); q=p-c; x,y=q@e1,q@e2; A=np.c_[x,y,np.ones(len(x))]; sol=np.linalg.lstsq(A,x*x+y*y,rcond=None)[0]; cx,cy=sol[:2]/2; r2=sol[2]+cx*cx+cy*cy
 if r2<=0:return None
 r=float(np.sqrt(r2)); cen=c+cx*e1+cy*e2; xax=unit(p[0]-cen- n*np.dot(p[0]-cen,n)); yax=unit(np.cross(n,xax)); ang=np.unwrap(np.arctan2((p-cen)@yax,(p-cen)@xax));
 radial=np.linalg.norm(p-cen,axis=1); res=np.sqrt((radial-r)**2+((p-cen)@n)**2)
 sweep=(2*math.pi if closed else float(ang[-1]-ang[0])); typ='CIRCLE' if closed else 'ARC'
 return {'type':typ,'center':cen,'normal':n,'x_axis':xax,'y_axis':yax,'radius':r,'u0':float(ang[0]),'u1':float(ang[0]+sweep),'rms':float(np.sqrt(np.mean(res*res))),'max':float(res.max())}
def ellipsefit(p,closed):
 if len(p)<6:return None
 c,e1,e2,n=plane(p); q=p-c; x,y=q@e1,q@e2; sc=max(float(np.abs(x).max()),float(np.abs(y).max()),1e-12); x,y=x/sc,y/sc
 D=np.c_[x*x,x*y,y*y,x,y,np.ones(len(x))]; *_,vh=np.linalg.svd(D,full_matrices=False); a,b,cc,d,e,f=vh[-1]; M=np.array([[a,b/2],[b/2,cc]])
 if b*b-4*a*cc>=0:return None
 try: cen2=np.linalg.solve(2*M,[-d,-e])
 except np.linalg.LinAlgError:return None
 con=a*cen2[0]**2+b*cen2[0]*cen2[1]+cc*cen2[1]**2+d*cen2[0]+e*cen2[1]+f
 vals,vec=np.linalg.eigh(M/-con)
 if np.any(vals<=0):return None
 rr=1/np.sqrt(vals)*sc; order=np.argsort(rr)[::-1]; ra,rb=rr[order]; maj=unit(vec[:,order[0]][0]*e1+vec[:,order[0]][1]*e2); minor=unit(np.cross(n,maj)); cen=c+(cen2[0]*sc)*e1+(cen2[1]*sc)*e2
 rel=p-cen; u=np.unwrap(np.arctan2((rel@minor)/rb,(rel@maj)/ra)); pred=cen+ra*np.cos(u)[:,None]*maj+rb*np.sin(u)[:,None]*minor; res=np.linalg.norm(pred-p,axis=1)
 return {'type':'ELLIPSE','center':cen,'normal':n,'major_axis':maj,'minor_axis':minor,'major_radius':float(ra),'minor_radius':float(rb),'u0':float(u[0]),'u1':float(u[0]+(2*math.pi if closed else u[-1]-u[0])),'rms':float(np.sqrt(np.mean(res*res))),'max':float(res.max())}
def splinefit(p,closed,diag):
 x=p[:-1] if closed and np.linalg.norm(p[0]-p[-1])<1e-10 else p
 if len(x)<3:return None
 try:
  tck,u=splprep(x.T,s=(FIT_TOL_REL*diag)**2*len(x),k=min(3,len(x)-1),per=closed)
  pred=np.asarray(splev(u,tck)).T; res=np.linalg.norm(pred-x,axis=1)
  return {'type':'BSPLINE','tck':[np.asarray(tck[0]).tolist(),np.asarray(tck[1]).tolist(),int(tck[2])],'u0':0.,'u1':1.,'closed':closed,'rms':float(np.sqrt(np.mean(res*res))),'max':float(res.max())}
 except Exception:return None

def sample_fit(f):
 typ=f['type']; s=np.linspace(0,1,N); u=f.get('u0',0)+(f.get('u1',1)-f.get('u0',0))*s
 if typ=='LINE': xyz=f['origin']+s[:,None]*f['length']*f['direction']; tan=np.repeat(f['direction'][None],N,0)
 elif typ in ('CIRCLE','ARC'):
  xyz=f['center']+f['radius']*(np.cos(u)[:,None]*f['x_axis']+np.sin(u)[:,None]*f['y_axis']); tan=np.cos(u)[:,None]*f['y_axis']-np.sin(u)[:,None]*f['x_axis']
 elif typ=='ELLIPSE':
  xyz=f['center']+f['major_radius']*np.cos(u)[:,None]*f['major_axis']+f['minor_radius']*np.sin(u)[:,None]*f['minor_axis']; tan=-f['major_radius']*np.sin(u)[:,None]*f['major_axis']+f['minor_radius']*np.cos(u)[:,None]*f['minor_axis']
 else:
  tt=np.linspace(0,1,2048); dense=np.asarray(splev(tt,(np.asarray(f['tck'][0]),np.asarray(f['tck'][1]),f['tck'][2]))).T; d=np.linalg.norm(np.diff(dense,axis=0),axis=1); c=np.r_[0,np.cumsum(d)]; target=np.linspace(0,c[-1],N); uu=np.interp(target,c,tt); xyz=np.asarray(splev(uu,(np.asarray(f['tck'][0]),np.asarray(f['tck'][1]),f['tck'][2]))).T; der=np.asarray(splev(uu,(np.asarray(f['tck'][0]),np.asarray(f['tck'][1]),f['tck'][2]),der=1)).T; tan=der
 tan=np.asarray([unit(v) for v in tan]); L=float(np.linalg.norm(np.diff(xyz,axis=0),axis=1).sum())
 return xyz.astype('f4'),tan.astype('f4'),s[:,None].astype('f4'),L

def gt_samples(step):
 ex=extract_curves_from_step(step); shape=load_step_shape(step); from OCP.TopAbs import TopAbs_EDGE; from OCP.TopExp import TopExp; from OCP.TopoDS import TopoDS; from OCP.TopTools import TopTools_IndexedMapOfShape
 m=TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape,TopAbs_EDGE,m); by={r['edge_id']:r for r in ex['curves']}; out=[]
 for i in range(1,m.Size()+1):
  eid=i-1
  if eid not in by:continue
  r=by[eid]; typ='BSPLINE' if r['curve_type']=='BEZIER' else r['curve_type']
  if typ not in ('LINE','CIRCLE','ELLIPSE','BSPLINE'):continue
  a=make_adaptor(TopoDS.Edge_s(m.FindKey(i))); us,_=arclength_params(a,64,r['u_start'],r['u_end']); pts=[]; tans=[]
  for z in us:
   p,t=eval_point_tangent(a,float(z));pts.append(p);tans.append(t)
  out.append({'gt_id':eid,'type':typ,'points':np.asarray(pts),'tangents':np.asarray(tans),'parameters':r['world_parameters']})
 return ex,out

def pair(d,g,diag):
 from scipy.spatial import cKDTree
 A,B=d['xyz'],g['points']; ia=cKDTree(B).query(A)[1]; ib=cKDTree(A).query(B)[1]; da=np.linalg.norm(A-B[ia],axis=1); db=np.linalg.norm(B-A[ib],axis=1); tol=MATCH_DIST_REL*diag
 tan=float((np.abs(np.sum(d['tan']*g['tangents'][ia],axis=1))).mean())
 return {'d2g_mean_rel':float(da.mean()/diag),'g2d_mean_rel':float(db.mean()/diag),'coverage_d2g':float((da<=tol).mean()),'coverage_g2d':float((db<=tol).mean()),'tangent_compatibility':tan}

def visual_qa(outpath, mesh_xyz, chains, sampled):
 """Deterministic PCA-plane QA visual; avoids a server-side mpl 3D dependency."""
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 center=mesh_xyz.mean(0); _,_,vh=np.linalg.svd(mesh_xyz-center,full_matrices=False); basis=vh[:2]
 project=lambda x:(x-center)@basis.T
 mesh2=project(mesh_xyz)
 fig,axes=plt.subplots(1,3,figsize=(12,4))
 stride=max(1,len(mesh_xyz)//6000)
 for ax,title in zip(axes,('Mesh vertices','Dora maximal chains','Fitted continuous curves')):
  ax.scatter(mesh2[::stride,0],mesh2[::stride,1],s=.12,c='0.55')
  ax.set_title(title); ax.set_axis_off()
 for ch in chains:
  p=project(ch['points']); axes[1].plot(p[:,0],p[:,1],lw=.45,c='tab:red')
 for x,_,_,_ in sampled:
  p=project(x); axes[2].plot(p[:,0],p[:,1],lw=.7,c='tab:blue')
 fig.tight_layout(); fig.savefig(outpath,dpi=160); plt.close(fig)

def process(row,outdir,write_vis=False):
 paths={k:Path(v['path']) for k,v in row['assets'].items()}; verts=objverts(paths['model_obj']); lo,hi=verts.min(0),verts.max(0); diag=float(np.linalg.norm(hi-lo)); z=np.load(paths['dora_salient_edges']); xyz,adj,edges=graph_from_dora(z); chains=extract_chains(xyz,adj,edges)
 dora_dir=outdir/'dora'; c2dir=outdir/'curve_c2'; dora_dir.mkdir(parents=True); c2dir.mkdir()
 jdump(dora_dir/'edge_graph_meta.json',{'cad_id':row['cad_id'],'n_vertices':len(xyz),'n_edges':len(edges),'degree_histogram':dict(Counter(map(len,adj.values()))),'source_sha256':row['assets']['dora_salient_edges']['sha256'],'coordinate_source':'salient_edges.npz endpoint xyz'})
 flat=[];off=[0];closed=[];meta=[]
 for ch in chains:
  flat.extend(ch['vertex_ids']);off.append(len(flat));closed.append(ch['closed_loop']); rel=ch['length']/max(diag,1e-12); reason=None
  if len(ch['points'])<2:reason='TOO_FEW_VERTICES'
  elif rel<MIN_REL_LEN:reason='TOO_SHORT_RELATIVE_TO_OBJECT'
  elif np.ptp(ch['points'],axis=0).max()<MIN_REL_LEN*diag:reason='DEGENERATE_BBOX'
  meta.append({'chain_id':ch['chain_id'],'vertex_count':len(ch['points']),'polyline_length':ch['length'],'length_over_object_diag':rel,'bbox_min':ch['points'].min(0).tolist(),'bbox_max':ch['points'].max(0).tolist(),'closed_loop':ch['closed_loop'],'filtered_reason':reason})
 np.savez(dora_dir/'chains.npz',vertex_indices_flat=np.asarray(flat,np.int32),offsets=np.asarray(off,np.int64),closed_loop=np.asarray(closed,bool))
 jdump(dora_dir/'chains_meta.json',{'cad_id':row['cad_id'],'object_bbox_diag':diag,'thresholds':{'min_length_rel':MIN_REL_LEN},'chains':meta})
 fits=[]; arrays=[]
 for ch,m in zip(chains,meta):
  if m['filtered_reason']:continue
  p=ch['points']; f=linefit(p)
  if f['rms']/diag>FIT_TOL_REL and len(p)>=4:
   f=circlefit(p,ch['closed_loop'])
  if (f is None or f['rms']/diag>FIT_TOL_REL) and len(p)>=6:
   f=ellipsefit(p,ch['closed_loop'])
  if f is None or f['rms']/diag>FIT_TOL_REL:
   f=splinefit(p,ch['closed_loop'],diag)
  if f is None: m['filtered_reason']='FIT_FAILURE';continue
  x,t,s,L=sample_fit(f); fjson={k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in f.items()}; fjson.update({'chain_id':ch['chain_id'],'fit_status':'PASS','fit_residual':f['rms'],'normalized_residual':f['rms']/diag,'closed_loop':ch['closed_loop'],'curve_length':L}); fits.append(fjson); arrays.append((x,t,s,L))
 jdump(dora_dir/'fitted_curves.json',{'cad_id':row['cad_id'],'curves':fits})
 if arrays:
  xyzs=np.stack([a[0] for a in arrays]); tans=np.stack([a[1] for a in arrays]); ss=np.stack([a[2] for a in arrays]); lengths=np.asarray([a[3] for a in arrays],'f4'); local=(xyzs-xyzs.mean(1,keepdims=True))/np.maximum(np.ptp(xyzs,axis=1).max(1)[:,None,None],1e-12); inp=np.concatenate([local,tans,ss],-1).astype('f4'); cen=xyzs.mean(1); ext=np.ptp(xyzs,axis=1); scale=max(float(np.ptp(verts,axis=0).max()),1e-12); anchors=np.c_[(cen-(lo+hi)/2)/scale,ext/scale].astype('f4')
 else: inp=np.zeros((0,N,7),'f4');lengths=np.zeros((0,),'f4');anchors=np.zeros((0,6),'f4')
 np.save(c2dir/'curve_inputs.npy',inp);np.save(c2dir/'curve_lengths.npy',np.log(lengths+1e-6).astype('f4'));np.save(c2dir/'anchors.npy',anchors)
 jdump(c2dir/'meta.json',{'cad_id':row['cad_id'],'input_schema':'[local_xyz(3), tangent(3), s(1)]','input_shape':list(inp.shape),'arc_length_samples':N,'local_xyz_normalization':'subtract curve-local center; divide max curve bbox extent','length_representation':'log(polyline_length)','anchor_definition':'[(curve_centroid-object_bbox_center)/max(object_bbox_extent), curve_bbox_extent/max(object_bbox_extent)]','anchor_shape':list(anchors.shape),'source':'Dora fitted continuous curves only'})
 if write_vis: visual_qa(outdir/'qa_mesh_chains_fits.png',verts,chains,arrays)
 ex,gts=gt_samples(paths['model_step']); dcur=[{'id':i,'xyz':a[0],'tan':a[1],'fit_type':fits[i]['type']} for i,a in enumerate(arrays)]; pairs={(i,j):pair(d,g,diag) for i,d in enumerate(dcur) for j,g in enumerate(gts)}; corr=[]; matched=[]
 strong_by_d={i:[] for i in range(len(dcur))}; strong_by_g={j:[] for j in range(len(gts))}; partial_by_d={i:[] for i in range(len(dcur))}
 for (i,j),q in pairs.items():
  strong=(q['d2g_mean_rel']<=MATCH_DIST_REL and q['g2d_mean_rel']<=MATCH_DIST_REL and min(q['coverage_d2g'],q['coverage_g2d'])>=MATCH_COVERAGE and q['tangent_compatibility']>=MATCH_TANGENT)
  if strong: strong_by_d[i].append(j); strong_by_g[j].append(i)
  if q['coverage_d2g']>=.5 and q['d2g_mean_rel']<=2*MATCH_DIST_REL: partial_by_d[i].append(j)
 for i,d in enumerate(dcur):
  strong=strong_by_d[i]
  if len(strong)==1 and len(strong_by_g[strong[0]])==1:
   cls='MATCHED_1_TO_1'; j=strong[0]; matched.append((i,j))
  elif len(strong)>1:
   cls='MERGED'; j=strong[0]
  elif len(strong)==1 and len(strong_by_g[strong[0]])>1:
   cls='FRAGMENTED'; j=strong[0]
  else:
   j=min(range(len(gts)),key=lambda k:pairs[i,k]['d2g_mean_rel']) if gts else None; q=pairs[i,j] if j is not None else {}; cls='PARTIAL' if partial_by_d[i] else 'UNMATCHED'
  corr.append({'dora_curve_index':i,'gt_curve_id':None if j is None else gts[j]['gt_id'],'classification':cls,'metrics':{} if j is None else pairs[i,j]})
 jdump(dora_dir/'curve_fit_report.json',{'total_chains':len(chains),'filtered_chains':sum(x['filtered_reason'] is not None for x in meta),'fitted_type_counts':dict(Counter(x['type'] for x in fits)),'fit_failures':sum(x['filtered_reason']=='FIT_FAILURE' for x in meta),'residual_normalized':qstats([x['normalized_residual'] for x in fits])})
 jdump(outdir/'gt_brep_curves.json',ex);jdump(outdir/'correspondence.json',{'thresholds':{'distance_rel':MATCH_DIST_REL,'coverage':MATCH_COVERAGE,'tangent':MATCH_TANGENT},'records':corr})
 return {'cad_id':row['cad_id'],'n_dora':len(fits),'matched':matched,'fit_types':[x['type'] for x in fits],'empty':not len(fits),'nan_inf':not (np.isfinite(inp).all() and np.isfinite(anchors).all()),'out':str(outdir),'gt_types':[x['type'] for x in gts]}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('qa','full'),required=True);ap.add_argument('--output',type=Path,default=OUT/'build_v1');ap.add_argument('--qa-count',type=int,default=20);args=ap.parse_args()
 rows=[json.loads(x) for x in COHORT.read_text().splitlines() if x.strip()]; train=[r for r in rows if r['split']=='train800'];
 if args.mode=='qa':
  chosen=[]
  for ds,n in (('DeepCAD',16),('Fusion360',4)):
   pool=sorted([r for r in train if r['dataset']==ds],key=lambda r:hashlib.sha256(r['cad_id'].encode()).hexdigest());chosen+=pool[:n]
 else: chosen=sorted(train,key=lambda r:r['cad_id'])
 args.output.mkdir(parents=True,exist_ok=False); jdump(args.output/'SELECTION.json',{'mode':args.mode,'cad_ids':[r['cad_id'] for r in chosen],'train800_only':True,'decode_dev_predictions_read':False,'pilot150_read':False,'official_test_read':False})
 reports=[]
 for k,row in enumerate(chosen,1):
  reports.append(process(row,args.output/'cad'/row['cad_id'],write_vis=(args.mode=='qa'))); print(f'{k}/{len(chosen)} {row["cad_id"]}',flush=True)
 counts=Counter();types=Counter()
 for r in reports:
  counts['TOTAL_DORA_CURVES']+=r['n_dora'];counts['EMPTY_CAD']+=int(r['empty']);counts['NAN_INF_CAD']+=int(r['nan_inf']);types.update(r['fit_types'])
  c=json.loads(Path(r['out']).joinpath('correspondence.json').read_text()); counts.update(x['classification'] for x in c['records'])
 summary={'mode':args.mode,'CAD_COUNT':len(reports),'counts':dict(counts),'fitted_types':dict(types),'DORA_CHAIN_DATA_READY':counts['NAN_INF_CAD']==0,'CURVE_FIT_READY':counts['NAN_INF_CAD']==0,'BREP_CORRESPONDENCE_READY':True,'C2_DORA_TRAINSET_READY':False,'TRAINING_STARTED':False,'reports':reports}
 if args.mode=='full':
  # CAD-level deterministic split: no curve from a CAD may cross the split.
  cad_split={r['cad_id']:('train' if n<720 else 'val') for n,r in enumerate(sorted(chosen,key=lambda x:hashlib.sha256(x['cad_id'].encode()).hexdigest()))}
  entries=[]; xs=[]; lens=[]; anchors=[]; type_vocab={'LINE':0,'CIRCLE':1,'ELLIPSE':2,'BSPLINE':3}
  byid={r['cad_id']:r for r in chosen}
  for rep in reports:
   cdir=Path(rep['out'])/'curve_c2'; inp=np.load(cdir/'curve_inputs.npy'); ln=np.load(cdir/'curve_lengths.npy'); an=np.load(cdir/'anchors.npy')
   corr=json.loads((Path(rep['out'])/'correspondence.json').read_text())['records']
   gt=json.loads((Path(rep['out'])/'gt_brep_curves.json').read_text())['curves']; gtby={g['edge_id']:g for g in gt}
   for rec in corr:
    if rec['classification']!='MATCHED_1_TO_1': continue
    i=int(rec['dora_curve_index']); gid=int(rec['gt_curve_id']); g=gtby[gid]; typ='BSPLINE' if g['curve_type']=='BEZIER' else g['curve_type']
    if typ not in type_vocab: continue
    xs.append(inp[i]); lens.append(ln[i]); anchors.append(an[i])
    entries.append({'sample_index':len(entries),'cad_id':rep['cad_id'],'source_id':byid[rep['cad_id']]['source_id'],'cad_split':cad_split[rep['cad_id']],'dora_curve_index':i,'gt_edge_id':gid,'fit_type':rep['fit_types'][i],'gt_curve_type':typ,'gt_world_parameters':g['world_parameters'],'input_path':str(cdir/'curve_inputs.npy'),'length_path':str(cdir/'curve_lengths.npy'),'anchor_path':str(cdir/'anchors.npy'),'correspondence_metrics':rec['metrics']})
  (args.output/'C2_DORA_TRAINSET_V1.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in entries))
  np.savez_compressed(args.output/'C2_DORA_TRAINSET_V1.npz',curve_inputs=np.asarray(xs,'f4'),log_curve_lengths=np.asarray(lens,'f4'),anchors=np.asarray(anchors,'f4'),cad_split=np.asarray([x['cad_split'] for x in entries]),gt_type_id=np.asarray([type_vocab[x['gt_curve_type']] for x in entries],'i2'))
  jdump(args.output/'C2_DORA_CAD_SPLIT_V1.json',{'unit':'CAD','algorithm':'SHA256(cad_id) ascending; first 720 train, remaining 80 val','train_cad_ids':sorted([k for k,v in cad_split.items() if v=='train']),'val_cad_ids':sorted([k for k,v in cad_split.items() if v=='val']),'counts':{'train_cad':720,'val_cad':80,'train_curve':sum(x['cad_split']=='train' for x in entries),'val_curve':sum(x['cad_split']=='val' for x in entries)}})
  summary['C2_DORA_TRAINSET_READY']=True; summary['C2_DORA_TRAINSET_CURVES']=len(entries); summary['C2_DORA_CAD_SPLIT']={'train':720,'val':80}
 jdump(args.output/'SUMMARY.json',summary); print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
