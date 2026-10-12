#!/usr/bin/env python3
"""One-time frozen Dev50 zero-touch evaluation for B0 vs M2-Oracle.

The script reads only the frozen independent Dev50 assets. It never reads
Test100, trains, searches checkpoints, slices targets, or alters data.
"""
from __future__ import annotations
import hashlib, importlib.util, json, re, shutil, sys, tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
POOL = ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/bulk_build_v1'
DEV = POOL/'manifests/DECODE_DEV_50.jsonl'
OUT = POOL/'zero_touch_dev50_v1'
B0 = ROOT/'ours3/v3_clean_training_v1/runs/b0_clean/checkpoint_epoch_08'
M2 = ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_15'
EXECUTOR = ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
TARGET_NORM = 1.9414176940917969
MAX_NEW = 4096
EOS_IDS = (128001, 128008, 128009)
OPS = ('Box','Cylinder','ExtrudePolygon','Extrude','Revolve','Union','Cut','Intersect','Circle','Rectangle','Polygon')
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'scripts/spatiallm_geometry_prefix_v3')]
import train_v3_smoke as core
from geometry_prefix_adapter import GeometryPrefixAdapter
from v3_canary_surface_adapter import load_surface_for_encoder


def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def prompt(tok, arm):
    user=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
    return tok.encode('<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n',add_special_tokens=False)

def ops(s): return re.findall(r'\b('+'|'.join(OPS)+r')\s*\(',s)
def opf1(a,b):
    a,b=Counter(a),Counter(b); tp=sum((a&b).values())
    if not a and not b:return 1.0
    if not tp:return 0.0
    p,r=tp/max(sum(b.values()),1),tp/max(sum(a.values()),1);return 2*p*r/(p+r)

def module():
    spec=importlib.util.spec_from_file_location('zero_touch_placement_v3',EXECUTOR)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m

def mesh_metrics(gt_path,pred_path):
    import trimesh
    from scipy.spatial import cKDTree
    gt=trimesh.load(str(gt_path),force='mesh'); pr=trimesh.load(str(pred_path),force='mesh')
    if isinstance(gt,trimesh.Scene):gt=gt.dump(concatenate=True)
    if isinstance(pr,trimesh.Scene):pr=pr.dump(concatenate=True)
    diag=float(np.linalg.norm(gt.bounds[1]-gt.bounds[0]));
    if diag<=1e-12:return {}
    a,_=trimesh.sample.sample_surface(gt,5000,seed=911);b,_=trimesh.sample.sample_surface(pr,5000,seed=912)
    da=cKDTree(b).query(a,k=1)[0];db=cKDTree(a).query(b,k=1)[0]
    return {'chamfer_norm':float((da.mean()+db.mean())*.5/diag),'hausdorff95_norm':float(max(np.percentile(da,95),np.percentile(db,95))/diag),'bbox_center_error_norm':float(np.linalg.norm(((gt.bounds[0]+gt.bounds[1])-(pr.bounds[0]+pr.bounds[1]))*.5)/diag),'bbox_extent_error_norm':float(np.linalg.norm((gt.bounds[1]-gt.bounds[0])-(pr.bounds[1]-pr.bounds[0]))/diag)}

def execute(text, gt_stl, outdir):
    r={'dsl_parse':False,'dsl_execute':False,'occ_non_null':False,'brep_valid':False,'step_write':False,'step_reload':False,'failure_stage':None,'reason':None}
    try:
        m=module();code=m.extract_dsl_code(text);m.parse_dsl(code);r['dsl_parse']=True
        step,stl=outdir/'pred.step',outdir/'pred.stl';m.execute_dsl(code,step,stl);r['dsl_execute']=True;r['step_write']=step.is_file() and stl.is_file()
        if not r['step_write']: raise RuntimeError('STEP_WRITE')
        import cadquery as cq
        from OCP.BRepCheck import BRepCheck_Analyzer
        shape=cq.importers.importStep(str(step)).val().wrapped
        r['occ_non_null']=not shape.IsNull();r['brep_valid']=bool(r['occ_non_null'] and BRepCheck_Analyzer(shape).IsValid())
        if not r['brep_valid']:raise RuntimeError('BREP_INVALID')
        r['step_reload']=True;r.update(mesh_metrics(gt_stl,stl))
    except Exception as e:
        if not r['dsl_parse']:r['failure_stage']='PARSE'
        elif not r['dsl_execute']:r['failure_stage']='EXECUTE'
        elif not r['step_write']:r['failure_stage']='STEP_WRITE'
        elif not r['brep_valid']:r['failure_stage']='BREP_VALID'
        else:r['failure_stage']='STEP_RELOAD'
        r['reason']=(type(e).__name__+': '+str(e))[-500:]
    return r

def load_model(arm, checkpoint, device):
    tok=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True,use_fast=False)
    model=core.module.SpatialLMLlamaForCausalLM.from_pretrained(checkpoint,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
    if arm=='m2':
        model.edge_proj=GeometryPrefixAdapter(256,model.config.hidden_size,target_norm=TARGET_NORM).to(device=device,dtype=torch.bfloat16)
        model.edge_proj.load_state_dict(torch.load(checkpoint/'geometry_prefix_adapter.pt',map_location=device,weights_only=True))
        model.config.separate_edge_tokens=True;model.separate_edge_tokens=True
    else:model.edge_proj=None
    for p in model.parameters():p.requires_grad_(False)
    model.eval();state={};original=core.install_precomputed_second(model,arm,state)
    return model,tok,state,original

def edge_tokens(row, arm, device):
    if arm=='b0':return None,torch.empty(0,dtype=torch.bool,device=device)
    sid=row['cad_id'].split('__',1)[1];arr=np.load(POOL/row['dataset']/sid/'curve_tokens/curve_tokens.npy')
    if arr.ndim!=2 or arr.shape[1]!=256 or len(arr)>128:raise RuntimeError('frozen C2 asset invalid')
    raw=np.zeros((128,256),np.float32);raw[:len(arr)]=arr
    mask=torch.zeros(128,dtype=torch.bool,device=device);mask[:len(arr)]=True
    return torch.tensor(raw,device=device).unsqueeze(0),mask

def run_arm(arm, checkpoint, rows, device):
    armout=OUT/arm;armout.mkdir();(armout/'predictions').mkdir();model,tok,state,original=load_model(arm,checkpoint,device)
    plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);allrows=[]
    try:
        for i,row in enumerate(rows,1):
            sid=row['cad_id'].split('__',1)[1];gp=POOL/row['dataset']/sid/'geometry_pack_v1'/sid
            surface,_=load_surface_for_encoder(plugin,gp/'surface_points.npy',row['dataset'].lower(),sid)
            st=torch.tensor(surface,device=device).unsqueeze(0);edge,mask=edge_tokens(row,arm,device);state['raw_mask']=mask
            target=(gp/'cad_target.dsl').read_text();p=prompt(tok,arm);labels=torch.tensor([[-100]*len(p)+tok.encode(target+'<|eot_id|>',add_special_tokens=False)],device=device);ids=torch.tensor([p+tok.encode(target+'<|eot_id|>',add_special_tokens=False)],device=device)
            with torch.no_grad():ce=float(model(input_ids=ids,attention_mask=torch.ones_like(ids),labels=labels,point_clouds=st,edge_clouds=edge).loss)
            state['raw_mask']=mask
            with torch.no_grad():gen=model.generate(input_ids=torch.tensor([p],device=device),attention_mask=torch.ones((1,len(p)),device=device,dtype=torch.long),point_clouds=st,edge_clouds=edge,max_new_tokens=MAX_NEW,do_sample=False,use_cache=True,eos_token_id=list(EOS_IDS),pad_token_id=128001)
            new=gen[0,len(p):].cpu();text=tok.decode(new,skip_special_tokens=True);pred_dir=armout/'predictions'/row['cad_id'];pred_dir.mkdir();(pred_dir/'pred.dsl').write_text(text)
            ev=execute(text,POOL/row['dataset']/sid/'gt_replay.stl',pred_dir)
            out={'cad_id':row['cad_id'],'dataset':row['dataset'],'ce':ce,'target_token_length':len(tok.encode(target,add_special_tokens=False)),'generated_token_length':int(new.numel()),'generated_target_ratio':float(new.numel()/max(1,len(tok.encode(target,add_special_tokens=False)))),'hit_max_new_tokens':bool(new.numel()>=MAX_NEW),'unexpected_runaway':bool(new.numel()>=MAX_NEW and len(tok.encode(target,add_special_tokens=False))<=MAX_NEW),'eos_emitted':bool(new.numel() and int(new[-1]) in EOS_IDS),'op_f1':opf1(ops(target),ops(text)),'exact_match':text.strip()==target.strip(),'second_stream_active':0 if arm=='b0' else int(state['entry']['second_stream_active']),**ev};allrows.append(out)
            if i%10==0:print(f'[{arm}] {i}/50 EOS={sum(x["eos_emitted"] for x in allrows)} STEP={sum(x["step_reload"] for x in allrows)}',flush=True)
    finally:
        core.module._splice_geometry=original;del model;torch.cuda.empty_cache()
    (armout/'PER_CAD.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in allrows));valid=[x for x in allrows if x['step_reload']]
    summary={'arm':arm,'checkpoint':str(checkpoint),'checkpoint_sha256_model_index':sha(checkpoint/'model.safetensors.index.json') if (checkpoint/'model.safetensors.index.json').is_file() else None,'n':len(allrows),'dev_ce':float(np.mean([x['ce'] for x in allrows])),'eos_n':sum(x['eos_emitted'] for x in allrows),'unexpected_runaway_n':sum(x['unexpected_runaway'] for x in allrows),'dsl_parse_n':sum(x['dsl_parse'] for x in allrows),'dsl_execute_n':sum(x['dsl_execute'] for x in allrows),'brep_valid_n':sum(x['brep_valid'] for x in allrows),'step_reload_n':sum(x['step_reload'] for x in allrows),'mean_op_f1':float(np.mean([x['op_f1'] for x in allrows])),'exact_n':sum(x['exact_match'] for x in allrows),'mean_chamfer_norm':float(np.mean([x['chamfer_norm'] for x in valid])) if valid else None,'mean_hausdorff95_norm':float(np.mean([x['hausdorff95_norm'] for x in valid])) if valid else None,'second_stream_active_values':sorted(set(x['second_stream_active'] for x in allrows))}
    (armout/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');return allrows,summary

def main():
    if OUT.exists():raise RuntimeError('zero-touch output already exists; do not rerun')
    rows=[json.loads(x) for x in DEV.read_text().splitlines() if x]
    if len(rows)!=50:raise RuntimeError('frozen Dev50 count mismatch')
    OUT.mkdir(parents=True);shutil.copy2(DEV,OUT/'FROZEN_DECODE_DEV_50.jsonl')
    contract={'protocol':'one-time independent Dev50 zero-touch evaluation','dev_manifest':str(DEV),'dev_manifest_sha256':sha(DEV),'checkpoints':{'B0':str(B0),'M2_ORACLE':str(M2)},'max_new_tokens':MAX_NEW,'decode':'greedy','executor':str(EXECUTOR),'executor_sha256':sha(EXECUTOR),'official_test_read':False,'test100_read':False,'training_started':False,'checkpoint_search':False}
    (OUT/'ZERO_TOUCH_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')
    core.heldout_geometry.install();device=torch.device('cuda:1');brows,bs=run_arm('b0',B0,rows,device);mrows,ms=run_arm('m2',M2,rows,device)
    byb={x['cad_id']:x for x in brows};bym={x['cad_id']:x for x in mrows};common=[cid for cid in byb if byb[cid]['step_reload'] and bym[cid]['step_reload']]
    paired={'common_valid_n':len(common),'m2_better_opf1_n':sum(bym[c]['op_f1']>byb[c]['op_f1'] for c in common),'b0_better_opf1_n':sum(byb[c]['op_f1']>bym[c]['op_f1'] for c in common),'tie_opf1_n':sum(byb[c]['op_f1']==bym[c]['op_f1'] for c in common),'common_valid_chamfer':{'b0':float(np.mean([byb[c]['chamfer_norm'] for c in common])) if common else None,'m2_oracle':float(np.mean([bym[c]['chamfer_norm'] for c in common])) if common else None}}
    result={'CURRENT_GATE':'INDEPENDENT_DEV50_ZERO_TOUCH_COMPLETE','B0':bs,'M2_ORACLE':ms,'PAIRED':paired,'TEST100_HAS_BEEN_EVALUATED':False,'TRAINING_STARTED':False}
    (OUT/'FINAL_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
