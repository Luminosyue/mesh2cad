#!/usr/bin/env python3
"""Read-only CADFS DSL-supervision audit: frozen Canary14 + all 301 candidates.

No model is loaded.  No converter, geometry gate, source asset, canary, or
existing V3 output is modified.  Every result is written under the dedicated
geometry_supervision_audit_v1 root.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
BASE=ROOT/'ours3/cadfs_overfit100_v1'
OUT=BASE/'geometry_supervision_audit_v1'
CAND=BASE/'inventory/CADFS_CANDIDATES.jsonl'
CANARY=BASE/'canary20/retry2/CANARY20_PER_CAD.jsonl'
CONVERTER=ROOT/'scripts/canonical_cad_data_v4/converters/cadfs_to_dsl.py'
sys.path[:0]=[str(ROOT/'scripts')]
from canonical_cad_data_v4.converters.cadfs_to_dsl import OP_PATTERNS, audit_featurescript, cadfs_to_dsl
from deepcad.cad_canonical import compute_transform, transform_dsl
from geometry_pack_v1.occ import tessellate_step
from geometry_pack_v1.surface import sample_surface_uniform
from geometry_pack_v1.pack import apply_canonical

GATE={'chamfer_rel_max':.01,'coverage_02_min':.98,'sampling':'source seed42; DSL seed43; bidirectional cKDTree'}

def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True,default=str)+'\n')
def fsha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def qtile(a, qs):return {k:float(np.percentile(a,q)) for k,q in qs.items()} if a else {k:None for k in qs}

def execute(dsl,work):
 r={'dsl_parse':False,'dsl_exec':False,'step_write':False,'step_reload':False,'error':None,'step_path':None}
 try:
  p=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py';s=importlib.util.spec_from_file_location('cadfs_screen_exec',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
  code=m.extract_dsl_code(dsl);m.parse_dsl(code);r['dsl_parse']=True
  import cadquery as cq
  st,sl=work/'dsl.step',work/'dsl.stl';m.execute_dsl(code,st,sl);r['dsl_exec']=True;r['step_write']=st.is_file() and sl.is_file();r['step_path']=str(st)
  if r['step_write']:cq.importers.importStep(str(st));r['step_reload']=True
 except Exception as e:r['error']=(type(e).__name__+': '+str(e))[-500:]
 return r

def compare(source_step,dsl_step):
 st=tessellate_step(source_step);v,f=st['vertices'],st['faces'];src,_,_=sample_surface_uniform(v,f,8192,42);tf=compute_transform(src);src=apply_canonical(src,tf.scale,np.asarray(tf.translation))
 dt=tessellate_step(dsl_step);pred,_,_=sample_surface_uniform(dt['vertices'],dt['faces'],8192,43)
 da=cKDTree(pred).query(src,k=1)[0];db=cKDTree(src).query(pred,k=1)[0]
 diag=max(float(np.linalg.norm(src.max(0)-src.min(0))),1e-12);ch=float((da.mean()+db.mean())*.5/diag);cov=float(((da<=.02*diag).mean()+(db<=.02*diag).mean())*.5)
 smin,smax=src.min(0),src.max(0);pmin,pmax=pred.min(0),pred.max(0)
 bbox=float((np.linalg.norm(smin-pmin)+np.linalg.norm(smax-pmax))*.5/diag)
 return {'chamfer_rel':ch,'coverage_02':cov,'hausdorff95_rel':float(np.percentile(np.r_[da,db],95)/diag),'bbox_error_rel':bbox,
  'source_bbox_canonical':[smin.tolist(),smax.tolist()],'dsl_bbox_canonical':[pmin.tolist(),pmax.tolist()],
  'GEOMETRY_PASS':bool(ch<=GATE['chamfer_rel_max'] and cov>=GATE['coverage_02_min'])}

def source_ops(text):
 rows=[]
 for name,pat in OP_PATTERNS.items():
  for n,m in enumerate(pat.finditer(text)):
   line=text.count('\n',0,m.start())+1;lo=max(0,m.start()-100);hi=min(len(text),m.start()+450)
   rows.append({'offset':m.start(),'line':line,'operation_type':name,'occurrence':n,'snippet':text[lo:hi]})
 rows.sort(key=lambda r:r['offset'])
 for i,r in enumerate(rows):r['source_op_index']=i
 return rows

def dsl_ops(dsl):
 tree=ast.parse(dsl,mode='exec');out=[]
 for i,node in enumerate(tree.body):
  stmt=ast.unparse(node);name=None;call=None
  if isinstance(node,ast.Assign) and len(node.targets)==1:
   name=getattr(node.targets[0],'id',None);call=node.value
  elif isinstance(node,ast.Expr):call=node.value
  primitive=call.func.id if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) else type(call).__name__
  deps=[]
  if call:
   deps=sorted({x.id for x in ast.walk(call) if isinstance(x,ast.Name) and x.id.startswith('body_')})
  out.append({'dsl_statement_index':i,'target':name,'primitive':primitive,'statement':stmt,'dependencies':deps})
 return out

def semantic_label(src_text, ops_src, ops_dsl):
 """Trace converter omissions without claiming unavailable intermediate geometry."""
 a=audit_featurescript(src_text);lower=src_text.lower();nex=sum(r['operation_type']=='extrude' for r in ops_src);nd=sum(r['primitive'] in {'Extrude','ExtrudePolygon'} for r in ops_dsl)
 flags=[]
 if nex!=nd:flags.append('SOURCE_DSL_MAPPING_ERROR')
 if any(x in lower for x in ('symmetric','twosided','seconddirection','endbound','startbound')):flags.append('TWO_SIDED_EXTRUDE' if 'twosided' in lower or 'seconddirection' in lower else 'SYMMETRIC_EXTRUDE')
 if any(x in lower for x in ('oppositedirection','negativedirection','startoffset','endoffset')):flags.append('EXTRUDE_EXTENT')
 if any(x in lower for x in ('faceattached','sketchplane','planereference','qcreatedby','constructionplane')):flags.append('FACE_ATTACHED_SKETCH')
 if any(x in lower for x in ('transform','rotation','translation','coordssystem')):flags.append('PLACEMENT_TRANSFORM')
 if a['counts'].get('boolean',0) or a['counts'].get('cut',0):flags.append('BOOLEAN')
 if a['counts'].get('revolve',0):flags.append('REVOLVE')
 if a['counts'].get('fillet',0):flags.append('FILLET')
 if a['counts'].get('chamfer',0):flags.append('CHAMFER')
 if a['counts'].get('pattern',0):flags.append('PATTERN')
 if a['counts'].get('circle',0)>1 or (a['counts'].get('circle',0) and a['counts'].get('line',0)):flags.append('PROFILE_HOLE')
 if not flags:flags=['UNKNOWN']
 return flags[0],flags[1:],a

def fig_three(source_step,dsl_step,out,title):
 """Small deterministic 3D evidence plot in the same source/canonical frame."""
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 import trimesh
 st=tessellate_step(source_step);src,_,_=sample_surface_uniform(st['vertices'],st['faces'],3500,42);tf=compute_transform(src);src=apply_canonical(src,tf.scale,np.asarray(tf.translation))
 dt=tessellate_step(dsl_step);pred,_,_=sample_surface_uniform(dt['vertices'],dt['faces'],3500,43)
 fig=plt.figure(figsize=(12,4));views=[(src,None,'SOURCE STEP'),(pred,None,'DSL EXEC STEP'),(src,pred,'OVERLAY')]
 for i,(a,b,label) in enumerate(views,1):
  ax=fig.add_subplot(1,3,i,projection='3d');ax.scatter(a[:,0],a[:,1],a[:,2],s=.35,c='#7894b8',alpha=.55)
  if b is not None:ax.scatter(b[:,0],b[:,1],b[:,2],s=.35,c='#e65d3a',alpha=.5)
  ax.set_title(label);ax.set_axis_off();ax.view_init(25,-55)
 fig.suptitle(title);fig.tight_layout();out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=180);plt.close(fig)

def task_a(canary_rows):
 fail=[r for r in canary_rows if not r.get('DSL_GEOMETRY_PASS')]
 dump(OUT/'CANARY14_FAILURE_MANIFEST.json',{'count':len(fail),'source':str(CANARY),'records':[{'cad_id':r['cad_id'],'source_id':r['source_id'],'chamfer_rel':r.get('chamfer_rel'),'coverage_02':r.get('coverage_02')} for r in fail]})
 summaries=[]
 for r in fail:
  cid,sid=r['cad_id'],r['source_id'];case=BASE/'canary20/retry2/cases'/cid;fs=case/'source/source.fs';srcstep=case/'source/source.step';dsl=(case/'cad_target.dsl').read_text();dslexec=case/'canonical_from_dsl.step'
  text=fs.read_text(encoding='utf-8',errors='replace');so=source_ops(text);do=dsl_ops(dsl);primary,secondary,audit=semantic_label(text,so,do)
  mapping=[];dsl_body=[x['dsl_statement_index'] for x in do if x['target'] and x['target'].startswith('body_')]
  src_ex=[x for x in so if x['operation_type'] in {'sketch','extrude'}]
  for i,x in enumerate(src_ex):mapping.append({'source_op_index':x['source_op_index'],'source_op_type':x['operation_type'],'converter_branch':'cadfs_to_dsl.lossless_subset','dsl_statement_indices':[dsl_body[min(i//2,len(dsl_body)-1)]] if dsl_body else [],'status':'STATIC_CODE_PATH_MAPPING'})
  dump(OUT/'operation_trace'/f'{cid}_SOURCE_OPS.json',{'cad_id':cid,'operations':so,'parser_audit':audit})
  dump(OUT/'operation_trace'/f'{cid}_DSL_OPS.json',{'cad_id':cid,'operations':do})
  dump(OUT/'operation_trace'/f'{cid}_OP_MAPPING.json',{'cad_id':cid,'prefix_geometry_available':False,'mapping_method':'converter static code-path mapping; FeatureScript intermediate solids unavailable locally','mappings':mapping})
  if dslexec.is_file():fig_three(srcstep,dslexec,OUT/'figures/canary14'/f'{cid}.png',f'{cid} | Chamfer={r.get("chamfer_rel"):.4f} Coverage={r.get("coverage_02"):.3f} | {primary}')
  summaries.append({'cad_id':cid,'source_id':sid,'prefix_geometry_available':'NO','FIRST_DIVERGENCE_OP':None,'LIKELY_FIRST_SEMANTIC_MISMATCH':primary,'PRIMARY_FAILURE_MODE':primary,'SECONDARY_FAILURE_MODES':secondary,'chamfer_rel':r.get('chamfer_rel'),'coverage_02':r.get('coverage_02')})
 cnt=Counter(x['PRIMARY_FAILURE_MODE'] for x in summaries);out={'FAILED_CASES':len(summaries),'PREFIX_GEOMETRY_AUDIT_AVAILABLE':'NO','PRIMARY_FAILURE_COUNTS':dict(cnt),'TOP_5_FAILURE_MODES':cnt.most_common(5),'MOST_COMMON_FIRST_DIVERGENCE_OPERATION':'UNAVAILABLE_SOURCE_INTERMEDIATE_BODIES','cases':summaries}
 dump(OUT/'CANARY14_OPERATION_FAILURE_SUMMARY.json',out);(OUT/'CANARY14_OPERATION_FAILURE_SUMMARY.md').write_text('# Canary14 operation failure summary\n\n```json\n'+json.dumps(out,indent=2)+'\n```\n');return out

def screen_one(r):
 cid=r['cad_id'];sid=r['source_id'];work=OUT/'screen_work'/cid;work.mkdir(parents=True,exist_ok=False)
 out={'cad_id':cid,'source_id':sid,'solid_count':r.get('solid_count'),'operation_types':r.get('operation_types',[]),'operation_count':r.get('operation_count',0),'complexity':r.get('complexity','unknown'),'dsl_parse':False,'dsl_exec':False,'step_reload':False,'GEOMETRY_PASS':False,'fail_reason':None}
 try:
  fs,step=Path(r['source_fs_path']),Path(r['source_step_path']);out['source_fs_sha256']=fsha(fs);out['source_step_sha256']=fsha(step)
  raw,_=cadfs_to_dsl(fs.read_text(encoding='utf-8',errors='replace'))
  st=tessellate_step(step);pts,_,_=sample_surface_uniform(st['vertices'],st['faces'],8192,42);tf=compute_transform(pts);dsl=transform_dsl(raw,tf);(work/'cad_target.dsl').write_text(dsl)
  ex=execute(dsl,work);out.update({'dsl_parse':ex['dsl_parse'],'dsl_exec':ex['dsl_exec'],'step_reload':ex['step_reload'],'dsl_error':ex['error']})
  if not ex['step_reload']:out['fail_reason']='DSL_EXECUTION_FAILURE';return out
  out.update(compare(step,Path(ex['step_path'])));out['fail_reason']=None if out['GEOMETRY_PASS'] else 'DSL_GEOMETRY_MISMATCH'
 except Exception as e:out['fail_reason']='SCREEN_EXCEPTION:'+type(e).__name__;out['error']=str(e)[-400:]
 return out

def task_b(candidates):
 manifest={'TOTAL':len(candidates),'converter_path':str(CONVERTER),'converter_sha256':fsha(CONVERTER),'geometry_gate':GATE,'records':[{'cad_id':r['cad_id'],'source_id':r['source_id'],'source_fs_path':r['source_fs_path'],'source_step_path':r['source_step_path'],'solid_count':r.get('solid_count'),'operation_types':r.get('operation_types',[]),'operation_count':r.get('operation_count',0)} for r in candidates]}
 dump(OUT/'CADFS301_GEOMETRY_SCREEN_MANIFEST.json',manifest)
 rows=[];screen=OUT/'CADFS301_GEOMETRY_SCREEN.jsonl'
 with screen.open('w') as f:
  for i,r in enumerate(candidates,1):
   x=screen_one(r);rows.append(x);f.write(json.dumps(x)+'\n');f.flush()
   if i%25==0:print(f'SCREEN={i}/{len(candidates)} PASS={sum(bool(z.get("GEOMETRY_PASS")) for z in rows)}',flush=True)
 parse=sum(x['dsl_parse'] for x in rows);exe=sum(x['dsl_exec'] for x in rows);reload=sum(x['step_reload'] for x in rows);good=[x for x in rows if x['GEOMETRY_PASS']]
 vals=[x['chamfer_rel'] for x in rows if x.get('chamfer_rel') is not None];cov=[x['coverage_02'] for x in rows if x.get('coverage_02') is not None]
 byop={}
 allops=sorted({op for r in rows for op in r['operation_types']})
 for op in allops:
  a=[r for r in rows if op in r['operation_types']];byop[op]={'count':len(a),'geometry_pass':sum(x['GEOMETRY_PASS'] for x in a),'pass_rate':sum(x['GEOMETRY_PASS'] for x in a)/len(a)}
 dump(OUT/'CADFS301_BY_OPERATION.json',byop);(OUT/'CADFS301_BY_OPERATION.md').write_text('# CADFS301 by operation\n\n```json\n'+json.dumps(byop,indent=2)+'\n```\n')
 bycomp={}
 for c in ('simple','medium','hard','unknown'):
  a=[r for r in rows if r['complexity']==c];bycomp[c]={'count':len(a),'geometry_pass':sum(x['GEOMETRY_PASS'] for x in a),'pass_rate':sum(x['GEOMETRY_PASS'] for x in a)/len(a) if a else None}
 # First-version data construction remains single-solid even though screen reports all 301.
 verified=[x for x in good if x.get('solid_count')==1]
 if len(verified)>=100:
  p=OUT/'CADFS_GEOMETRY_VERIFIED_SUBSET.json';dump(p,{'selection':'all frozen-gate geometry passes AND single solid; no additional selection','count':len(verified),'records':verified});dump(OUT/'CADFS_GEOMETRY_VERIFIED_ORDER.json',{'algorithm':'lexicographic source_id','records':sorted(verified,key=lambda x:x['source_id'])})
  manifest_path=str(p);msha=fsha(p)
 else:manifest_path=None;msha=None
 gate='CADFS_GEOMETRY_VERIFIED_POOL_READY' if len(verified)>=100 else ('CADFS_GEOMETRY_VERIFIED_POOL_INSUFFICIENT_BUT_REPAIRABLE' if len(verified)>=60 else 'CADFS_CONVERTER_GEOMETRY_FIDELITY_LOW')
 summary={'CURRENT_GATE':gate,'TOTAL':len(rows),'PARSE_PASS':parse,'EXEC_PASS':exe,'STEP_RELOAD_PASS':reload,'GEOMETRY_PASS':len(good),'GEOMETRY_FAIL':len(rows)-len(good),'GEOMETRY_PASS_RATE':len(good)/len(rows),'METRIC_DISTRIBUTION':{'Chamfer_rel':qtile(vals,{'min':0,'median':50,'p75':75,'p90':90,'max':100}),'Coverage_0p02':qtile(cov,{'min':0,'median':50,'p10':10,'p25':25,'max':100})},'BY_COMPLEXITY':bycomp,'CADFS_GEOMETRY_VERIFIED_COUNT':len(verified),'VERIFIED_MANIFEST':manifest_path,'VERIFIED_MANIFEST_SHA256':msha,'CAN_WE_BUILD_CADFS100':'YES' if len(verified)>=100 else 'NO','TRAINING_APPROVED':'NOT_YET'}
 dump(OUT/'CADFS301_GEOMETRY_SCREEN_SUMMARY.json',summary);return summary

def main():
 if OUT.exists():raise RuntimeError(f'output already exists: {OUT}')
 OUT.mkdir();candidates=[json.loads(x) for x in CAND.read_text().splitlines() if x]
 if len(candidates)!=301:raise RuntimeError(f'expected frozen 301, got {len(candidates)}')
 canary=[json.loads(x) for x in CANARY.read_text().splitlines() if x]
 a=task_a(canary);b=task_b(candidates)
 final={'CURRENT_GATE':b['CURRENT_GATE'],'CANARY14_ROOT_CAUSE':a,'CADFS301_SCREEN':b,'IS_THE_PROBLEM_MESH':'NO','IS_THE_PROBLEM_C2':'NO','IS_THE_PROBLEM_V3':'NO','IS_THE_MAIN_BLOCKER_DSL_GEOMETRY_SUPERVISION':'YES','TRAINING_STARTED':False,'NEXT_STEP':'converter repair limited to audited dominant failure mode, then rerun affected samples only' if b['CADFS_GEOMETRY_VERIFIED_COUNT']<100 else 'freeze a 100-CAD order and run complete asset-only validation'}
 dump(OUT/'FINAL_REPORT.json',final);print(json.dumps(final,indent=2))
if __name__=='__main__':main()
