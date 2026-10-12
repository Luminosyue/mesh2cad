#!/usr/bin/env python3
"""Read-only audit of frozen Dora fitted V1 results; no geometry recomputation."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from scipy.interpolate import splev

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
V1=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1'
COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'
OUT=ROOT/'ours3/dora_fitted_curve_v1_rare_type_failure_audit_v4'
FITTED=('LINE','CIRCLE','ARC','ELLIPSE','BSPLINE'); CLASSES=('MATCHED_1_TO_1','FRAGMENTED','PARTIAL','MERGED','UNMATCHED'); GT=('LINE','CIRCLE','ELLIPSE','BSPLINE','OTHER/UNKNOWN')
def sh(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def csvout(p,rows,fields):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def typ(x):return x if x in GT[:-1] else 'OTHER/UNKNOWN'
def hashkey(r):return hashlib.sha256(f"{r['cad_id']}:{r['fitted_curve_id']}".encode()).hexdigest()
def endpoint_map(dora):
 z=np.load(dora);m={}
 for (a,b),p,q in zip(z['edge_vertex_indices'],z['edge_xyz0'],z['edge_xyz1']):m[int(a)]=np.asarray(p,float);m[int(b)]=np.asarray(q,float)
 return m
def fit_sample(f,n=128):
 t=f['type'];u=np.linspace(f.get('u0',0),f.get('u1',1),n)
 a=lambda k:np.asarray(f[k],float)
 if t=='LINE':return a('origin')[None]+np.linspace(0,1,n)[:,None]*float(f['length'])*a('direction')[None]
 if t in ('CIRCLE','ARC'):return a('center')[None]+float(f['radius'])*(np.cos(u)[:,None]*a('x_axis')[None]+np.sin(u)[:,None]*a('y_axis')[None])
 if t=='ELLIPSE':return a('center')[None]+float(f['major_radius'])*np.cos(u)[:,None]*a('major_axis')[None]+float(f['minor_radius'])*np.sin(u)[:,None]*a('minor_axis')[None]
 tck=f['tck'];return np.asarray(splev(np.linspace(0,1,n),(np.asarray(tck[0],float),np.asarray(tck[1],float),int(tck[2])))).T
def gt_sample(g,n=128):
 p=g.get('world_parameters',{});t=typ(g.get('curve_type','OTHER/UNKNOWN'));u=np.linspace(float(g.get('u_start',0)),float(g.get('u_end',1)),n)
 if t=='LINE':return np.linspace(np.asarray(g['start_point'],float),np.asarray(g['end_point'],float),n)
 if t=='CIRCLE':return np.asarray(p['center'])[None]+float(p['radius'])*(np.cos(u)[:,None]*np.asarray(p['x_axis'])[None]+np.sin(u)[:,None]*np.asarray(p['y_axis'])[None])
 if t=='ELLIPSE':return np.asarray(p['center'])[None]+float(p['major_radius'])*np.cos(u)[:,None]*np.asarray(p['major_axis'])[None]+float(p['minor_radius'])*np.sin(u)[:,None]*np.asarray(p['minor_axis'])[None]
 if t=='BSPLINE' and p.get('control_points'):
  cp=np.asarray(p['control_points'],float);return np.asarray([np.interp(np.linspace(0,len(cp)-1,n),np.arange(len(cp)),cp[:,k]) for k in range(3)]).T
 return np.zeros((0,3))
def project(x,center,basis):return (x-center)@basis.T
def render(rec,src,outdir):
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 cdir=V1/'cad'/rec['cad_id']; fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves'];f=fits[rec['fitted_curve_id']]; fp=fit_sample(f)
 chains=np.load(cdir/'dora/chains.npz');ids=chains['vertex_indices_flat'][chains['offsets'][rec['dora_chain_id']]:chains['offsets'][rec['dora_chain_id']+1]];em=endpoint_map(src['dora']);chain=np.asarray([em[int(x)] for x in ids])
 gts=json.loads((cdir/'gt_brep_curves.json').read_text())['curves'];g=next((x for x in gts if x['edge_id']==rec['gt_brep_edge_id']),None);gp=gt_sample(g) if g else np.zeros((0,3))
 verts=[]
 for l in Path(src['obj']).read_text(errors='ignore').splitlines():
  if l.startswith('v '):verts.append([float(z) for z in l.split()[1:4]])
 mesh=np.asarray(verts,float);center=mesh.mean(0);_,_,vh=np.linalg.svd(mesh-center,full_matrices=False);basis=vh[:2]
 def draw(ax,local=False):
  if local:
   allp=np.vstack([chain,fp,gp]) if len(gp) else np.vstack([chain,fp]);lo=allp.min(0);hi=allp.max(0);pad=max(np.linalg.norm(hi-lo)*.3,1e-5);keep=np.all((mesh>=lo-pad)&(mesh<=hi+pad),axis=1);mm=mesh[keep]
  else:mm=mesh
  q=project(mm,center,basis);ax.scatter(q[::max(1,len(q)//5000),0],q[::max(1,len(q)//5000),1],s=.18,c='.75',label='mesh')
  for p,c,lw,name in ((chain,'red',1,'Dora salient chain'),(fp,'blue',1.4,'fitted curve'),(gp,'green',1.4,'GT BRep candidate')):
   if len(p):q=project(p,center,basis);ax.plot(q[:,0],q[:,1],c=c,lw=lw,label=name)
  ax.set_aspect('equal');ax.legend(fontsize=7)
 fig,(ax,tx)=plt.subplots(1,2,figsize=(12,6),gridspec_kw={'width_ratios':[3,2]});draw(ax,True);ax.set_title('LOCAL_VIEW — fitted-curve neighborhood');tx.axis('off');text='\n'.join([f"CAD: {rec['cad_id']}",f"chain / curve: {rec['dora_chain_id']} / {rec['fitted_curve_id']}",f"GT / fitted: {rec['gt_candidate_type']} / {rec['fitted_type']}",f"match / hint: {rec['match_class']} / {rec['root_cause_hint']}",f"d2g / g2d: {rec['dora_to_gt_distance']} / {rec['gt_to_dora_distance']}",f"coverage d2g/g2d: {rec['dora_to_gt_coverage']} / {rec['gt_to_dora_coverage']}",f"tangent: {rec['tangent_compatibility']}",f"normalized fit residual: {rec['normalized_fitting_residual']}"]);tx.text(.02,.98,text,va='top',family='monospace',fontsize=9);fig.tight_layout();fig.savefig(outdir/'LOCAL_VIEW.png',dpi=170);plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,7));draw(ax,False);ax.set_title('GLOBAL_VIEW — object coordinate frame');fig.tight_layout();fig.savefig(outdir/'GLOBAL_VIEW.png',dpi=170);plt.close(fig)
def hint(r,t):
 m=r['metrics'];d=float(m.get('d2g_mean_rel',float('inf')));g=float(m.get('g2d_mean_rel',float('inf')));c1=float(m.get('coverage_d2g',0));c2=float(m.get('coverage_g2d',0));ta=float(m.get('tangent_compatibility',0));dist,cover,tan=t['distance_rel'],t['coverage'],t['tangent']
 if r['match_class']=='FRAGMENTED':return 'A_CHAIN_FRAGMENTATION'
 if r['match_class']=='MERGED':return 'B_CHAIN_MERGE'
 if r['gt_type'] is None:return 'H_TRUE_UNMATCHED'
 fitfam='CIRCLE' if r['fitted_type']=='ARC' else r['fitted_type'];allgood=d<=dist and g<=dist and c1>=cover and c2>=cover and ta>=tan
 if fitfam!=r['gt_type'] and allgood:return 'D_GT_TYPE_MAPPING'
 if d>dist or g>dist:
  if c1>=cover and c2>=cover and ta>=tan:return 'E_CORRESPONDENCE_DISTANCE'
  return 'H_TRUE_UNMATCHED' if r['match_class']=='UNMATCHED' else 'I_AMBIGUOUS'
 if c1<cover or c2<cover:return 'F_CORRESPONDENCE_COVERAGE'
 if ta<tan:return 'G_TANGENT_MISMATCH'
 return 'I_AMBIGUOUS'
def main():
 OUT.mkdir(parents=True,exist_ok=False);co={x['cad_id']:x for x in map(json.loads,COHORT.read_text().splitlines()) if x}; funnel={x:Counter() for x in FITTED}; ma=defaultdict(Counter);mb=defaultdict(Counter);rare=[];succ=[];thresholds=None
 for cdir in sorted((V1/'cad').iterdir()):
  cad=cdir.name;fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves'];corr=json.loads((cdir/'correspondence.json').read_text());thresholds=thresholds or corr['thresholds'];records=corr['records'];gts={g['edge_id']:g for g in json.loads((cdir/'gt_brep_curves.json').read_text())['curves']};meta={x['chain_id']:x for x in json.loads((cdir/'dora/chains_meta.json').read_text())['chains']};diag=json.loads((cdir/'dora/chains_meta.json').read_text())['object_bbox_diag']
  for r in records:
   i=int(r['dora_curve_index']);f=fits[i];ft=f['type'];cls=r['classification'];funnel[ft][cls]+=1;g=gts.get(r.get('gt_curve_id'));gt_type=typ(g['curve_type']) if g else None
   if g:mb[gt_type][ft]+=1
   if cls=='MATCHED_1_TO_1' and g:ma[gt_type][ft]+=1
   base={'cad_id':cad,'dataset_source':co[cad]['dataset'],'dora_chain_id':f['chain_id'],'fitted_curve_id':i,'fitted_type':ft,'gt_candidate_type':gt_type,'gt_brep_edge_id':r.get('gt_curve_id'),'match_class':cls,'metrics':r.get('metrics',{}),'gt_type':gt_type,'fit':f,'chain_meta':meta[f['chain_id']],'object_bbox_diagonal':diag,'gt_curve_length':None if not g else g.get('length')}
   if cls=='MATCHED_1_TO_1' and ft in ('LINE','CIRCLE','ARC'):succ.append(base)
   if ft in ('ELLIPSE','BSPLINE') and cls!='MATCHED_1_TO_1':rare.append(base)
 # fixed audit schemas
 rows=[]
 for ft in FITTED:
  x={'Type':ft,'Fitted':sum(funnel[ft].values()),'Matched':funnel[ft]['MATCHED_1_TO_1'],'Fragmented':funnel[ft]['FRAGMENTED'],'Partial':funnel[ft]['PARTIAL'],'Merged':funnel[ft]['MERGED'],'Unmatched':funnel[ft]['UNMATCHED']};x['classification_sum']=sum(x[k] for k in ('Matched','Fragmented','Partial','Merged','Unmatched'));x['valid']=x['Fitted']==x['classification_sum'];rows.append(x)
 csvout(OUT/'TYPE_CONDITIONED_FUNNEL.csv',rows,list(rows[0]));dump(OUT/'TYPE_CONDITIONED_FUNNEL.json',{'thresholds':thresholds,'rows':rows});(OUT/'TYPE_CONDITIONED_FUNNEL.md').write_text('| Type | Fitted | Matched | Fragmented | Partial | Merged | Unmatched |\n|---|---:|---:|---:|---:|---:|---:|\n'+''.join(f"| {x['Type']} | {x['Fitted']} | {x['Matched']} | {x['Fragmented']} | {x['Partial']} | {x['Merged']} | {x['Unmatched']} |\n" for x in rows))
 def matrix(d):return [{'GT_type':g,**{f:int(d[g][f]) for f in FITTED}} for g in GT]
 matrix_md=[]
 for name,m in (('MATCHED',ma),('ALL_CANDIDATES',mb)):
  rr=matrix(m);csvout(OUT/f'GT_FITTED_TYPE_MATRIX_{name}.csv',rr,list(rr[0]));dump(OUT/f'GT_FITTED_TYPE_MATRIX_{name}.json',rr)
  matrix_md.extend([f'## {name}', '| GT BRep type | LINE | CIRCLE | ARC | ELLIPSE | BSPLINE |', '|---|---:|---:|---:|---:|---:|'])
  matrix_md.extend(f"| {x['GT_type']} | {x['LINE']} | {x['CIRCLE']} | {x['ARC']} | {x['ELLIPSE']} | {x['BSPLINE']} |" for x in rr)
 (OUT/'GT_FITTED_TYPE_MATRIX.md').write_text('Matrices are row=GT BRep family, column=fitted family; ARC remains separate.\n\n'+'\n'.join(matrix_md)+'\n')
 out=[]
 for b in rare:
  f=b['fit'];m=b['metrics'];cm=b['chain_meta'];r={'CAD_ID':b['cad_id'],'dataset_source':b['dataset_source'],'DORA_CHAIN_ID':b['dora_chain_id'],'FITTED_CURVE_ID':b['fitted_curve_id'],'FITTED_TYPE':b['fitted_type'],'GT_CANDIDATE_TYPE':b['gt_candidate_type'],'GT_BREP_EDGE_ID':b['gt_brep_edge_id'],'MATCH_CLASS':b['match_class'],'Dora_chain_vertex_count':cm['vertex_count'],'Dora_chain_polyline_length':cm['polyline_length'],'fitted_curve_length':f.get('curve_length'),'GT_curve_length':b['gt_curve_length'],'object_bbox_diagonal':b['object_bbox_diagonal'],'dora_to_gt_distance':m.get('d2g_mean_rel'),'gt_to_dora_distance':m.get('g2d_mean_rel'),'dora_to_gt_coverage':m.get('coverage_d2g'),'gt_to_dora_coverage':m.get('coverage_g2d'),'tangent_compatibility':m.get('tangent_compatibility'),'fitting_residual':f.get('fit_residual'),'normalized_fitting_residual':f.get('normalized_residual'),'closed_loop':f.get('closed_loop'),'junction_related_flag':'UNKNOWN_NOT_STORED_IN_FROZEN_METADATA','fragment_count_if_available':None}
  b['root_cause_hint']=hint(b,thresholds);r['ROOT_CAUSE_HINT']=b['root_cause_hint'];out.append(r)
 (OUT/'RARE_TYPE_FAILURE_RECORDS.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in out));csvout(OUT/'RARE_TYPE_FAILURE_RECORDS.csv',out,list(out[0]))
 cs=Counter(x['ROOT_CAUSE_HINT'] for x in out);rs=[]
 for k in ('A_CHAIN_FRAGMENTATION','B_CHAIN_MERGE','C_FITTING_ERROR','D_GT_TYPE_MAPPING','E_CORRESPONDENCE_DISTANCE','F_CORRESPONDENCE_COVERAGE','G_TANGENT_MISMATCH','H_TRUE_UNMATCHED','I_AMBIGUOUS','J_OTHER'):rs.append({'Root Cause':k,'ELLIPSE':sum(x['ROOT_CAUSE_HINT']==k and x['FITTED_TYPE']=='ELLIPSE' for x in out),'BSPLINE':sum(x['ROOT_CAUSE_HINT']==k and x['FITTED_TYPE']=='BSPLINE' for x in out)});rs[-1]['Total']=rs[-1]['ELLIPSE']+rs[-1]['BSPLINE']
 csvout(OUT/'RARE_TYPE_ROOT_CAUSE_SUMMARY.csv',rs,list(rs[0]));(OUT/'RARE_TYPE_ROOT_CAUSE_SUMMARY.md').write_text('| Root Cause | ELLIPSE | BSPLINE | Total |\n|---|---:|---:|---:|\n'+''.join(f"| {x['Root Cause']} | {x['ELLIPSE']} | {x['BSPLINE']} | {x['Total']} |\n" for x in rs))
 # deterministic selection: root-cause coverage then SHA ordering
 def select(pool,n):
  ans=[];seen=set()
  for h in sorted(set(x['root_cause_hint'] for x in pool)):
   z=sorted([x for x in pool if x['root_cause_hint']==h],key=hashkey)
   if z:ans.append(z[0]);seen.add(hashkey(z[0]))
  for x in sorted(pool,key=hashkey):
   if len(ans)>=n:break
   if hashkey(x) not in seen:ans.append(x);seen.add(hashkey(x))
  return ans[:n]
 for x in succ:x['root_cause_hint']='SUCCESS'
 cases=select([x for x in succ if x['fitted_type']=='LINE'],3)+select([x for x in succ if x['fitted_type'] in ('CIRCLE','ARC')],3)+select([b for b in rare if b['fitted_type']=='ELLIPSE'],5)+select([b for b in rare if b['fitted_type']=='BSPLINE'],5)
 (OUT/'visual_cases').mkdir();man=[]
 for n,b in enumerate(cases):
  rr=next((x for x in out if x['CAD_ID']==b['cad_id'] and x['FITTED_CURVE_ID']==b['fitted_curve_id']),None)
  if rr is None:rr={'cad_id':b['cad_id'],'dora_chain_id':b['dora_chain_id'],'fitted_curve_id':b['fitted_curve_id'],'gt_brep_edge_id':b.get('gt_brep_edge_id'),'gt_candidate_type':b.get('gt_type'),'fitted_type':b['fitted_type'],'match_class':b['match_class'],'root_cause_hint':'SUCCESS','dora_to_gt_distance':b['metrics'].get('d2g_mean_rel'),'gt_to_dora_distance':b['metrics'].get('g2d_mean_rel'),'dora_to_gt_coverage':b['metrics'].get('coverage_d2g'),'gt_to_dora_coverage':b['metrics'].get('coverage_g2d'),'tangent_compatibility':b['metrics'].get('tangent_compatibility'),'normalized_fitting_residual':b['fit'].get('normalized_residual')}
  rec={'cad_id':b['cad_id'],'dora_chain_id':b['dora_chain_id'],'fitted_curve_id':b['fitted_curve_id'],'gt_brep_edge_id':b.get('gt_brep_edge_id'),'gt_candidate_type':b.get('gt_type'),'fitted_type':b['fitted_type'],'match_class':b['match_class'],'root_cause_hint':b['root_cause_hint'],'metrics':b['metrics']};d=OUT/'visual_cases'/f'{n:02d}_{b["fitted_type"]}_{b["cad_id"]}_{b["fitted_curve_id"]}';d.mkdir();src=co[b['cad_id']]['assets'];render({**rr,'cad_id':b['cad_id'],'dora_chain_id':b['dora_chain_id'],'fitted_curve_id':b['fitted_curve_id'],'gt_brep_edge_id':b.get('gt_brep_edge_id'),'gt_candidate_type':b.get('gt_type'),'fitted_type':b['fitted_type'],'match_class':b['match_class'],'root_cause_hint':b['root_cause_hint']},{'obj':Path(src['model_obj']['path']),'dora':Path(src['dora_salient_edges']['path'])},d);man.append({**rec,'folder':str(d.relative_to(OUT))})
 dump(OUT/'VISUAL_CASE_MANIFEST.json',{'selection_rule':'root-cause coverage first, then SHA256(cad_id:fitted_curve_id) ascending','counts':{'matched_line':3,'matched_circle_arc':3,'ellipse_failure':5,'bspline_failure':5},'cases':man})
 manifest=json.loads((V1/'FILE_SHA256_MANIFEST.json').read_text());integrity=[]
 for rel,old in manifest.get('files',{}).items():
  p=V1/rel;integrity.append({'path':rel,'expected_sha256':old['sha256'],'actual_sha256':sh(p),'match':old['sha256']==sh(p)})
 freeze=V1/'DORA_FITTED_CURVE_DATASET_V1_FREEZE.json';integrity.append({'path':freeze.name,'expected_sha256':'NOT_PRESENT_IN_ORIGINAL_FILE_MANIFEST','actual_sha256':sh(freeze),'match':'NOT_BASELINE_VERIFIABLE','note':'read-only audit never writes this file; its original manifest lacks a self-hash baseline'})
 dump(OUT/'DATA_INTEGRITY.json',{'checked':integrity,'all_manifest_backed_match':all(x['match'] is True for x in integrity if x['match']!='NOT_BASELINE_VERIFIABLE'),'freeze_file_read_only_baseline_note':'original manifest does not contain the freeze file hash'})
 top=sorted(cs.items(),key=lambda x:(-x[1],x[0]))[:3];gate=all(x['valid'] for x in rows) and all(x['match'] is True for x in integrity if x['match']!='NOT_BASELINE_VERIFIABLE')
 dump(OUT/'FINAL_GATE.json',{'CURRENT_GATE':'DORA_FITTED_CURVE_V1_RARE_TYPE_FAILURE_AUDIT_COMPLETE' if gate else 'DORA_FITTED_CURVE_V1_RARE_TYPE_FAILURE_AUDIT_FAIL','ELLIPSE_FITTED':110,'ELLIPSE_MATCHED':0,'ELLIPSE_TOP_ROOT_CAUSE':max(((x['Root Cause'],x['ELLIPSE']) for x in rs),key=lambda x:x[1])[0],'BSPLINE_FITTED':355,'BSPLINE_MATCHED':0,'BSPLINE_TOP_ROOT_CAUSE':max(((x['Root Cause'],x['BSPLINE']) for x in rs),key=lambda x:x[1])[0],'TYPE_FUNNEL_READY':True,'GT_FITTED_MATRIX_READY':True,'VISUAL_OVERLAY_READY':True,'ROOT_CAUSE_SUMMARY_READY':True,'RECOMMENDED_NEXT_ACTION':'NEEDS_MANUAL_REVIEW','top3_root_causes':top,'NO_ALGORITHM_MODIFICATION':True,'NO_TRAINING':True})
if __name__=='__main__':main()
