#!/usr/bin/env python3
import csv, hashlib, json, os, re, sys, traceback
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'p1_p3_realmesh_multicase_probe_v1'; OUT.mkdir(parents=True,exist_ok=True)
CASES=['cube','canister','car','toaster','vase','recordplayer','pressure_cooker','speaker_small','school_bus','mini_excavator']
CASE_DIR={c:ROOT/f'{c}_p3_xpart_cadfit_routea_v1' for c in CASES}
P1=ROOT/'toaster_p1_edge_condition_ablation_v1'; C2=ROOT/'curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'; CKPT=ROOT/'p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000'

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def dump(p,x): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def main():
 import trimesh, torch
 sys.path[:0]=[str(ROOT.parent/'scripts'),str(ROOT.parent/'scripts/geometry_pack_v1'),str(ROOT.parent/'scripts/separate_edge_tokens_v1')]
 from geometry_pack_v1.mesh_edges import detect_sharp_edges
 from mesh_edge_to_curve_v1.grouping import resample_polyline,tangents_from_points
 from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import curve_inputs,load_backbone
 from spatiallm_curve_token_v1.config import CURVE_TOKEN_DIM,MAX_CURVE_TOKENS
 from curve_encoder_scale_curvature_v1.config import TYPE_TO_ID
 from curve_token_v1.fit_curves_from_points import fit_circle,fit_ellipse,fit_line
 import importlib.util
 sp=importlib.util.spec_from_file_location('dec',P1/'scripts/decode_arm_c2_val.py'); dec=importlib.util.module_from_spec(sp); sp.loader.exec_module(dec)
 dec._setup_paths()
 device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
 enc,_=load_backbone(C2,device)
 model,tok=dec._load_j2_curve(CKPT,torch.bfloat16)
 from separate_edge_tokens_v1.common import make_plugin
 plugin=make_plugin(separate_edge=True)
 from geometry_pack_v1.decode_joint_j0_j2 import generate_dsl
 from decode_eval_split import _exec_step,_solid_op_count,_op_multiset
 from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code
 from cad_canonical import CoordinateTransform,transform_dsl
 selected=[]; audit=[]
 for c in CASES:
  parts=sorted((CASE_DIR[c]/'p3').glob('part_*.obj'))
  rows=[]
  for p in parts:
   m=trimesh.load(str(p),force='mesh',process=False); v=np.asarray(m.vertices); f=np.asarray(m.faces); diag=float(np.linalg.norm(m.extents)); area=float(m.area)
   adj=np.asarray(m.face_adjacency); ae=np.asarray(m.face_adjacency_edges)
   sharp=detect_sharp_edges(v,f,adj,ae,30.0) if len(adj) else {'dihedral_deg':np.zeros(0)}
   curv=float(np.mean(np.abs(np.asarray(sharp.get('dihedral_deg',[]))))) if len(sharp.get('dihedral_deg',[])) else 0.0
   rows.append({'case':c,'part_id':p.stem,'obj_path':str(p),'vertex_n':len(v),'face_n':len(f),'bbox':m.bounds.tolist(),'bbox_diag':diag,'surface_area':area,'curvature':curv,'topology_complexity':int(len(adj)),'mesh_sha256':sha(p)})
  if c in ('cube','canister','car') or len(rows)<=10: chosen=rows
  else:
   # deterministic coverage of size, area, curvature, and topology extremes
   keys=['bbox_diag','surface_area','curvature','topology_complexity']; idx=set()
   for k in keys:
    s=sorted(range(len(rows)),key=lambda i:rows[i][k]); idx.update([s[0],s[len(s)//2],s[-1]])
   chosen=[rows[i] for i in sorted(idx)][:10]
  for r in chosen:r['selection_reason']='ALL_PARTS' if c in ('cube','canister','car') or len(rows)<=10 else 'DETERMINISTIC_EXTREME_COVERAGE_SIZE_AREA_CURVATURE_TOPOLOGY'
  selected.extend(chosen); audit.extend(rows)
 dump(OUT/'selected_parts.json',selected); dump(OUT/'config.json',{'root':str(ROOT),'cases':CASES,'selection_policy':'all cube/canister/car; all <=10; otherwise deterministic bbox/area/curvature/topology extremes','p1_checkpoint':str(CKPT),'checkpoint_sha256':sha(CKPT/'model-00001-of-00002.safetensors'),'tokenizer':str(CKPT),'c2_checkpoint':str(C2),'c2_checkpoint_sha256':sha(C2),'gt_sharp_used':False,'gt_curve_used':False,'gt_brep_used':False,'cuda_device':os.environ.get('CUDA_VISIBLE_DEVICES')})
 with open(OUT/'input_audit.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=sorted(audit[0]));w.writeheader();w.writerows(audit)
 curve_rows=[]; inf_rows=[]; cad_rows=[]
 for n,s in enumerate(selected):
  c,pid=s['case'],s['part_id']; p=Path(s['obj_path']); idir=OUT/'parts'/c/pid; idir.mkdir(parents=True,exist_ok=True); curve_path=idir/'curves_meta.json'
  try:
   m=trimesh.load(str(p),force='mesh',process=False); v=np.asarray(m.vertices,float); f=np.asarray(m.faces,int); center=(m.bounds[0]+m.bounds[1])/2; scale=6.0/max(float(np.linalg.norm(m.extents)),1e-9); vc=(v-center)*scale; mc=trimesh.Trimesh(vertices=vc,faces=f,process=False)
   pts,face_idx=trimesh.sample.sample_surface(mc,8192,seed=20260916+n); pts=pts.astype(np.float32); normals=np.asarray(mc.face_normals)[face_idx].astype(np.float32); cloud=np.concatenate([pts,normals],axis=1); np.save(idir/'surface_points.npy',cloud); tf={'center':center.tolist(),'scale':scale,'rotation':None,'forward_transform':{'scale':scale,'translation':(-center*scale).tolist()},'inverse_transform':{'scale':1/scale,'translation':center.tolist()}};dump(idir/'transform.json',tf)
   adj=np.asarray(mc.face_adjacency); ae=np.asarray(mc.face_adjacency_edges); sharp=detect_sharp_edges(np.asarray(mc.vertices),f,adj,ae,30.0) if len(adj) else {'v0':np.zeros((0,3)),'v1':np.zeros((0,3)),'vertex_indices':np.zeros((0,2),int),'dihedral_deg':np.zeros(0)}
   from collections import defaultdict
   pairs=np.asarray(sharp['vertex_indices'],int); chains=[]; graph=defaultdict(list)
   for i,(a,b) in enumerate(pairs): graph[int(a)].append((int(b),i));graph[int(b)].append((int(a),i))
   used=set()
   for i,(a,b) in enumerate(pairs):
    if i in used:continue
    path=[i];used.add(i);cur=int(b);prev=int(a)
    while len(graph[cur])==2:
     z=next((z for z in graph[cur] if z[1] not in used and z[0]!=prev),None)
     if z is None:break
     prev,cur=cur,z[0];used.add(z[1]);path.append(z[1])
    if len(path)>=3:chains.append(path)
   feats=[]; scales=[]; metas=[]
   for ci,ch in enumerate(chains):
    vids=[int(pairs[ch[0],0]),int(pairs[ch[0],1])]
    for si in ch[1:]:
     a,b=map(int,pairs[si]); vids.append(b if a==vids[-1] else a if b==vids[-1] else b)
    poly=np.asarray(mc.vertices)[vids]; xyz=resample_polyline(poly,32); tan=tangents_from_points(xyz); cand=[]
    for typ,fn in [('LINE',fit_line),('CIRCLE',fit_circle),('ELLIPSE',fit_ellipse)]:
     try:
      z=fn(xyz); cand.append((typ,float(z.get('rms_residual',1e9))))
     except Exception:pass
    typ,rms=min(cand,key=lambda x:x[1]) if cand else ('BSPLINE',float('inf')); typ=typ if typ in TYPE_TO_ID else 'BSPLINE'; ff,ss=curve_inputs(xyz,tan.astype(np.float32));feats.append(ff);scales.append(ss);metas.append({'curve_index':ci,'type':typ,'poly_len':float(np.linalg.norm(np.diff(poly,axis=0),axis=1).sum()),'fit_residual':rms,'n_segs':len(ch)})
   order=np.argsort([-x['poly_len'] for x in metas])[:MAX_CURVE_TOKENS] if metas else []; toks=np.zeros((1,CURVE_TOKEN_DIM),np.float32) if not len(order) else enc(torch.from_numpy(np.stack([feats[i] for i in order])).to(device),torch.from_numpy(np.stack([scales[i] for i in order])).to(device))['token'].float().cpu().numpy()
   np.save(idir/'curve_tokens.npy',toks); cr={'case':c,'part_id':pid,'curve_count':len(order),'curve_type_distribution':{k:sum(metas[i]['type']==k for i in order) for k in TYPE_TO_ID},'total_curve_length':float(sum(metas[i]['poly_len'] for i in order)),'mean_curve_length':float(np.mean([metas[i]['poly_len'] for i in order])) if order.size else 0.0,'fit_residual':float(np.mean([metas[i]['fit_residual'] for i in order])) if order.size else None,'coverage':float(sum(metas[i]['poly_len'] for i in order)/max(float(mc.extents.sum())*4,1e-9)),'failed_curve_n':0,'source':'OBJ->mesh dihedral Dora-equivalent extraction','gt_used':False};dump(curve_path,{**cr,'curves':[metas[i] for i in order]});curve_rows.append(cr)
   surf=plugin._voxelize_6ch(cloud); surface_t=np.concatenate([surf[0].astype(np.float32),surf[1],surf[2]],axis=1); pred,meta=generate_dsl(model,tok,torch.as_tensor(surface_t[None]),torch.as_tensor(toks[None]),separate_edge=True,max_new_tokens=4096); (idir/'program_raw.txt').write_text(pred); code=extract_dsl_code(pred); (idir/'program.dsl').write_text(code+'\n'); local=_exec_step(code,idir); tfobj=CoordinateTransform.from_json(tf); global_exec={'parsed':False,'step_ok':False};
   try: global_exec=_exec_step(transform_dsl(code,tfobj,inverse=True),idir/'global')
   except Exception as e: global_exec={'parsed':False,'step_ok':False,'exception':str(e)}
   ops=int(_solid_op_count(code)); ir={'case':c,'part_id':pid,'generated_token_n':int(meta.get('num_generated_tokens',0)),'EOS_position':meta.get('eos_position'),'operation_count':ops,'operation_types':_op_multiset(code),'multi_op':ops>1,'premature_EOS':bool(ops==0 or (ops<=1 and int(meta.get('num_generated_tokens',0))<32)),'parse_success':bool(local.get('parsed',False))}; inf_rows.append(ir); cad_rows.append({'case':c,'part_id':pid,'P1_PARSE':bool(local.get('parsed',False)),'CAD_EXEC':bool(local.get('step_ok',False)),'STEP_EXPORT':bool(local.get('step_ok',False)),'STEP_RELOAD':bool(global_exec.get('step_ok',False)),'failure_stage':None if global_exec.get('step_ok') else 'STEP_RELOAD','exception':local.get('exception') or global_exec.get('exception')})
  except Exception as e:
   curve_rows.append({'case':c,'part_id':pid,'curve_count':0,'curve_type_distribution':{},'total_curve_length':0,'mean_curve_length':0,'fit_residual':None,'coverage':0,'failed_curve_n':1,'source':'FAILED','gt_used':False});inf_rows.append({'case':c,'part_id':pid,'generated_token_n':0,'EOS_position':None,'operation_count':0,'operation_types':{},'multi_op':False,'premature_EOS':True,'parse_success':False});cad_rows.append({'case':c,'part_id':pid,'P1_PARSE':False,'CAD_EXEC':False,'STEP_EXPORT':False,'STEP_RELOAD':False,'failure_stage':'CURVE_EXTRACTION_FAIL','exception':f'{type(e).__name__}: {e}'});(idir/'exception.txt').write_text(traceback.format_exc())
  if n%5==0: print('progress',n+1,'/',len(selected),flush=True)
 for name,rows in [('curve_audit.csv',curve_rows),('inference_results.csv',inf_rows),('cad_execution_results.csv',cad_rows)]:
  with open(OUT/name,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)
 def rate(rows,k):return sum(bool(r.get(k)) for r in rows)/len(rows) if rows else 0
 part_rows=[]
 for s,cr,ir,ca in zip(selected,curve_rows,inf_rows,cad_rows): part_rows.append({**{k:s[k] for k in ('case','part_id')},'P1_PARSE':ca['P1_PARSE'],'CAD_EXEC':ca['CAD_EXEC'],'STEP_EXPORT':ca['STEP_EXPORT'],'STEP_RELOAD':ca['STEP_RELOAD'],'operation_count':ir['operation_count'],'multi_op':ir['multi_op'],'premature_EOS':ir['premature_EOS'],'curve_count':cr['curve_count'],'curve_fit_residual':cr['fit_residual'],'Chamfer Distance':None,'failure_stage':ca['failure_stage']})
 with open(OUT/'metrics_part.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=sorted(part_rows[0]));w.writeheader();w.writerows(part_rows)
 obj=[]
 for c in CASES:
  rs=[r for r in part_rows if r['case']==c];obj.append({'case':c,'PART_N':len(rs),'P1_VALID_N':sum(x['P1_PARSE'] and x['CAD_EXEC'] for x in rs),'P1_VALID_RATE':rate(rs,'P1_PARSE'),'STEP_RELOAD_N':sum(x['STEP_RELOAD'] for x in rs),'STEP_RELOAD_RATE':rate(rs,'STEP_RELOAD'),'MULTI_OP_N':sum(x['multi_op'] for x in rs),'VALID_MULTI_OP_N':sum(x['multi_op'] and x['CAD_EXEC'] for x in rs),'PREMATURE_EOS_N':sum(x['premature_EOS'] for x in rs),'PREMATURE_EOS_RATE':rate(rs,'premature_EOS'),'ASSEMBLY_CD':None})
 with open(OUT/'metrics_object.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=sorted(obj[0]));w.writeheader();w.writerows(obj)
 summary={'CURRENT_GATE':'P1_X_P3_REAL_MESH_MULTICASE_PROBE_V1','CASE_N':len(CASES),'SELECTED_PART_N':len(selected),'CURVE_VALID_N':sum(x['curve_count']>0 for x in curve_rows),'P1_PARSE_N':sum(x['P1_PARSE'] for x in cad_rows),'CAD_EXEC_N':sum(x['CAD_EXEC'] for x in cad_rows),'STEP_RELOAD_N':sum(x['STEP_RELOAD'] for x in cad_rows),'MULTI_OP_RATE':rate(inf_rows,'multi_op'),'PREMATURE_EOS_RATE':rate(inf_rows,'premature_EOS'),'MEAN_CD':None,'MAIN_FAILURE_MODE':'CURVE_EXTRACTION_FAIL' if sum(x['curve_count']==0 for x in curve_rows)>sum(not x['P1_PARSE'] for x in cad_rows) else 'LLM_PROGRAM_GENERATION','READY_FOR_139_CASE_SCALEUP':'NO','NEXT_RECOMMENDED_STAGE':'audit curve conditioning and program collapse before scale-up'};dump(OUT/'summary.json',summary)
 report=['# P1 x P3 REAL-MESH MULTI-CASE PROBE v1','',f"CURRENT_GATE={summary['CURRENT_GATE']}",f"CASE_N={len(CASES)} SELECTED_PART_N={len(selected)}",'', '| Case | Part N | Curve OK | P1 Parse | CAD Exec | STEP Reload | Multi-op Rate | Premature EOS Rate | Mean CD | Assembly CD |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for o in obj: report.append(f"| {o['case']} | {o['PART_N']} | - | {o['P1_VALID_N']} | - | {o['STEP_RELOAD_N']} | {o['MULTI_OP_N']/o['PART_N']:.3f} | {o['PREMATURE_EOS_RATE']:.3f} | - | - |")
 report += ['', '## Diagnostic answers',f"Q1: {'YES' if summary['P1_PARSE_N'] else 'NO'}; P1 parsed {summary['P1_PARSE_N']}/{len(selected)} parts.",f"Q2: premature EOS rate={summary['PREMATURE_EOS_RATE']:.3f}; multi-op rate={summary['MULTI_OP_RATE']:.3f}.",f"Q3: Main failure mode: {summary['MAIN_FAILURE_MODE']}.","Q4: See inference_results.csv for good-curve plus collapse cases.","Q5: READY_FOR_139_CASE_SCALEUP=NO; this is diagnostic only and requires real-mesh conditioning/program stability review."]
 (OUT/'reports').mkdir(exist_ok=True);(OUT/'reports/FINAL_REPORT.md').write_text('\n'.join(report)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
