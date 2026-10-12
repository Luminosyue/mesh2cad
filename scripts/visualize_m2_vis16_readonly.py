#!/usr/bin/env python3
"""Frozen M2 e18/e20 train-self-decode visualization (no training)."""
from __future__ import annotations
import ast, gc, importlib.util, json, math, shutil, sys, tempfile
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import trimesh
from scipy.spatial import cKDTree
from transformers import AutoTokenizer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
RUN=ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1'
OUT=RUN/'epoch20_result_inspection'
MANIFEST=ROOT/'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/spatiallm_geometry_prefix_v3')]
import train_v3_smoke as core

DEVICE=torch.device('cuda:0'); MAX_NEW=4096; EOS_IDS=(128001,128008,128009)
OPS=('Box','Cylinder','ExtrudePolygon','Extrude','Revolve','Union','Cut','Intersect','Circle','Rectangle','Polygon')

def op_f1(a,b):
    aa,bb=Counter(__import__('re').findall(r'\b('+'|'.join(OPS)+r')\s*\(',a)),Counter(__import__('re').findall(r'\b('+'|'.join(OPS)+r')\s*\(',b)); tp=sum((aa&bb).values())
    if not aa and not bb:return 1.0
    if not tp:return 0.0
    p,r=tp/max(sum(bb.values()),1),tp/max(sum(aa.values()),1);return 2*p*r/(p+r)

def parse_ok(text):
    try: ast.parse(text);return True
    except (SyntaxError,ValueError):return False

def load_exec():
    p=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
    spec=importlib.util.spec_from_file_location('vis_cad_dsl',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def make_selection(records, saved):
    by={x['cad_id']:dict(x,**{'difficulty_bin':records[x['cad_id']]['difficulty_bin'],'operation_count':records[x['cad_id']]['operation_count']}) for x in saved}
    used=set();out=[]
    def choose(bucket,diff,n,pred):
        pool=sorted((x for x in by.values() if x['difficulty_bin']==diff and pred(x)),key=lambda x:(-x['op_f1'],x['cad_id']))
        for x in pool:
            if x['cad_id'] not in used:
                used.add(x['cad_id']);out.append({'cad_id':x['cad_id'],'selection_bucket':bucket,'difficulty_bin':diff,'epoch20_saved_metrics':x});break
        else: raise RuntimeError(f'no candidate {bucket}/{diff}')
    # Quotas are frozen before any fresh generation: simple 4, medium 6, hard 6.
    choose('HIGH_OPF1','simple',1,lambda x:True); choose('MEDIUM_OPF1','simple',1,lambda x:True); choose('LOW_OR_PARSE_RISK','simple',1,lambda x:not x['dsl_parse_success']); choose('RUNAWAY_OR_LONG','simple',1,lambda x:x['unexpected_runaway'] or x['target_token_length']>400)
    for b,p in [('HIGH_OPF1',lambda x:True),('MEDIUM_OPF1',lambda x:True),('LOW_OR_PARSE_RISK',lambda x:not x['dsl_parse_success']),('RUNAWAY_OR_LONG',lambda x:x['unexpected_runaway'] or x['target_token_length']>400)]: choose(b,'medium',1,p)
    # Two extra medium representatives: high and low/parse-risk.
    choose('HIGH_OPF1','medium',1,lambda x:True);choose('LOW_OR_PARSE_RISK','medium',1,lambda x:not x['dsl_parse_success'])
    for b,p in [('HIGH_OPF1',lambda x:True),('MEDIUM_OPF1',lambda x:True),('LOW_OR_PARSE_RISK',lambda x:not x['dsl_parse_success']),('RUNAWAY_OR_LONG',lambda x:x['unexpected_runaway'] or x['target_token_length']>400)]: choose(b,'hard',1,p)
    choose('LOW_OR_PARSE_RISK','hard',1,lambda x:not x['dsl_parse_success']);choose('RUNAWAY_OR_LONG','hard',1,lambda x:x['unexpected_runaway'] or x['target_token_length']>400)
    assert len(out)==16 and Counter(x['difficulty_bin'] for x in out)=={'simple':4,'medium':6,'hard':6}
    return out

def prompt(tok):
    u=core.markers('m2')+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
    s='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+u+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
    return torch.tensor([tok.encode(s,add_special_tokens=False)],device=DEVICE)

def load_model(epoch):
    ck=RUN/f'checkpoint_epoch_{epoch:02d}'
    # Checkpoint is read only. Recreate the adapter architecture then load the
    # separately persisted summary module exactly as the training code did.
    model=core.module.SpatialLMLlamaForCausalLM.from_pretrained(ck,torch_dtype=torch.bfloat16,device_map=DEVICE,local_files_only=True)
    for p in model.point_backbone.parameters():p.requires_grad_(False)
    for p in model.point_proj.parameters():p.requires_grad_(False)
    model.edge_proj=core.GeometryPrefixAdapter(256,model.config.hidden_size,target_norm=1.9414176940917969).to(device=DEVICE,dtype=torch.bfloat16)
    model.edge_proj.load_state_dict(torch.load(ck/'geometry_prefix_adapter.pt',map_location=DEVICE,weights_only=True))
    model.config.separate_edge_tokens=True;model.separate_edge_tokens=True;model.config.use_cache=True;model.eval()
    state={};orig=core.install_precomputed_second(model,'m2',state)
    return model,state,orig,ck

def decode_epoch(epoch, rows, tok, plugin):
    model,state,orig,ck=load_model(epoch); result={}
    try:
        with torch.no_grad():
            for i,row in enumerate(rows,1):
                x,m=core.second_input(row,'m2');state['raw_mask']=m
                edge=x.to(DEVICE).unsqueeze(0)
                surf,_=plugin._load_cad_separate_edge(row['surface_input']);surf=torch.tensor(surf,device=DEVICE).unsqueeze(0)
                ids=prompt(tok)
                gen=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),point_clouds=surf,edge_clouds=edge,max_new_tokens=MAX_NEW,do_sample=False,use_cache=True,eos_token_id=list(EOS_IDS),pad_token_id=128001)
                new=gen[0,ids.shape[1]:].cpu(); text=tok.decode(new,skip_special_tokens=True)
                outdir=OUT/'predictions'/f'epoch{epoch}' ;outdir.mkdir(parents=True,exist_ok=True);(outdir/f"{row['cad_id']}.txt").write_text(text)
                result[row['cad_id']]={'checkpoint':str(ck),'pred_dsl':text,'generated_tokens':int(new.numel()),'eos':bool(new.numel() and int(new[-1]) in EOS_IDS),'hit_cap':bool(new.numel()>=MAX_NEW),'parse_pass':parse_ok(text)}
                print(f'e{epoch} {i}/{len(rows)} {row["cad_id"]} eos={result[row["cad_id"]]["eos"]}',flush=True)
    finally:
        core.module._splice_geometry=orig;del model;gc.collect();torch.cuda.empty_cache()
    return result

def execute(code,step,stl):
    out={'parse_pass':False,'exec_pass':False,'step_write_pass':False,'step_reload_pass':False,'failure_stage':None,'reason':None}
    try:
        m=load_exec();clean=m.extract_dsl_code(code);m.parse_dsl(clean);out['parse_pass']=True
    except Exception as e:out.update(failure_stage='PARSE',reason=f'{type(e).__name__}: {e}');return out
    try:
        m.execute_dsl(clean,step,stl);out['exec_pass']=True;out['step_write_pass']=step.exists()
    except Exception as e:out.update(failure_stage='EXEC',reason=f'{type(e).__name__}: {e}');return out
    try:
        import cadquery as cq;cq.importers.importStep(str(step));out['step_reload_pass']=True
    except Exception as e:out.update(failure_stage='STEP_RELOAD',reason=f'{type(e).__name__}: {e}')
    return out

def mesh_metrics(gt,pr):
    g=trimesh.load(str(gt),force='mesh');p=trimesh.load(str(pr),force='mesh')
    if isinstance(g,trimesh.Scene):g=g.dump(concatenate=True)
    if isinstance(p,trimesh.Scene):p=p.dump(concatenate=True)
    a,_=trimesh.sample.sample_surface(g,8192,seed=42);b,_=trimesh.sample.sample_surface(p,8192,seed=43)
    da=cKDTree(b).query(a,k=1)[0];db=cKDTree(a).query(b,k=1)[0]
    diag=float(np.linalg.norm(g.bounds[1]-g.bounds[0])); cen=float(np.linalg.norm((g.bounds.mean(0)-p.bounds.mean(0)))/max(diag,1e-12)); ext=float(np.linalg.norm((g.extents-p.extents))/max(diag,1e-12))
    return {'chamfer_norm':float((da.mean()+db.mean())/2/max(diag,1e-12)),'hausdorff95_norm':float(max(np.percentile(da,95),np.percentile(db,95))/max(diag,1e-12)),'bbox_center_error_norm':cen,'bbox_extent_error_norm':ext}

def points(step,n=3000):
    m=trimesh.load(str(step),force='mesh');m=m.dump(concatenate=True) if isinstance(m,trimesh.Scene) else m;return trimesh.sample.sample_surface(m,n,seed=42)[0],m.bounds
def render(ax,step,bounds,title,color='tab:blue',overlay=None):
    if not step or not Path(step).is_file():ax.text(.5,.5,title+'\nNO STEP',ha='center',va='center');ax.set_axis_off();return
    p,_=points(step);ax.scatter(p[:,0],p[:,1],p[:,2],s=.25,c=color)
    if overlay and Path(overlay).is_file():q,_=points(overlay);ax.scatter(q[:,0],q[:,1],q[:,2],s=.18,c='tab:red',alpha=.65)
    lo,hi=bounds;pad=.05*np.max(hi-lo);ax.set(xlim=(lo[0]-pad,hi[0]+pad),ylim=(lo[1]-pad,hi[1]+pad),zlim=(lo[2]-pad,hi[2]+pad),title=title);ax.view_init(25,-55);ax.set_axis_off()

def galleries(cases):
    figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
    valid=[x for x in cases if x['gt_exec']['step_reload_pass'] and (x['epochs']['18']['exec']['step_reload_pass'] or x['epochs']['20']['exec']['step_reload_pass'])]
    for start in range(0,len(valid),8):
        batch=valid[start:start+8];fig=plt.figure(figsize=(12,3*len(batch)))
        for i,x in enumerate(batch):
            gt=x['steps']['gt'];_,bounds=points(gt)
            render(fig.add_subplot(len(batch),3,3*i+1,projection='3d'),gt,bounds,x['cad_id']+' GT','gray')
            e=x['epochs']['18'];render(fig.add_subplot(len(batch),3,3*i+2,projection='3d'),x['steps'].get('epoch18'),bounds,f"E18 F1={e['op_f1']:.2f} tok={e['generated_tokens']}")
            e=x['epochs']['20'];render(fig.add_subplot(len(batch),3,3*i+3,projection='3d'),x['steps'].get('epoch20'),bounds,f"E20 F1={e['op_f1']:.2f} tok={e['generated_tokens']}")
        fig.tight_layout();fig.savefig(figdir/f'M2_GT_E18_E20_GALLERY_{start//8+1:02d}.png',dpi=170);plt.close(fig)
    # Epoch20 overlays; GT frame determines every plot scale.
    fig=plt.figure(figsize=(8,3*max(1,len(valid))))
    for i,x in enumerate(valid):
        _,bounds=points(x['steps']['gt']);render(fig.add_subplot(len(valid),2,2*i+1,projection='3d'),x['steps']['gt'],bounds,x['cad_id']+' GT','gray');render(fig.add_subplot(len(valid),2,2*i+2,projection='3d'),x['steps'].get('epoch20'),bounds,'E20 red over GT gray','tab:red',x['steps']['gt'])
    fig.tight_layout();fig.savefig(figdir/'M2_EPOCH20_GT_PRED_OVERLAY_GALLERY.png',dpi=170);plt.close(fig)
    failed=[x for x in cases if not x['epochs']['18']['exec']['step_reload_pass'] or not x['epochs']['20']['exec']['step_reload_pass']]
    fig=plt.figure(figsize=(10,3*max(1,len(failed))))
    for i,x in enumerate(failed):
        _,bounds=points(x['steps']['gt']);render(fig.add_subplot(len(failed),2,2*i+1,projection='3d'),x['steps']['gt'],bounds,x['cad_id']+' GT','gray')
        e=x['epochs']['20'];ax=fig.add_subplot(len(failed),2,2*i+2);ax.axis('off');ax.text(.01,.98,f"E20 FAILURE_STAGE={e['exec']['failure_stage']}\nEOS={e['eos']} tokens={e['generated_tokens']}\n{e['exec']['reason'] or ''}\n\nDSL:\n{e['pred_dsl'][:700]}",va='top',family='monospace',fontsize=7,wrap=True)
    fig.tight_layout();fig.savefig(figdir/'M2_FAILURE_GALLERY.png',dpi=170);plt.close(fig)
    return len(valid),len(failed)

def main():
    core.heldout_geometry.install();plugin=core.get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True);tok=AutoTokenizer.from_pretrained(RUN/'checkpoint_epoch_20',local_files_only=True,use_fast=False)
    records={x['cad_id']:x for x in json.loads(MANIFEST.read_text())['records']};saved=[json.loads(x) for x in (RUN/'decode_dev_epoch_20.jsonl').read_text().splitlines() if x];sel=make_selection(records,saved)
    (OUT/'M2_VIS16_MANIFEST.json').write_text(json.dumps({'label':'TRAIN_SELF_DECODE_ONLY','selection_frozen_before_decode':True,'records':sel},indent=2)+'\n')
    rows=[records[x['cad_id']] for x in sel];p18=decode_epoch(18,rows,tok,plugin);p20=decode_epoch(20,rows,tok,plugin)
    cases=[];steps=OUT/'steps';steps.mkdir(exist_ok=True)
    for s,row in zip(sel,rows):
        cid=row['cad_id'];d=steps/cid;d.mkdir(exist_ok=True);gt=row['target_dsl'];gt_code=Path(gt).read_text();gt_exec=execute(gt_code,d/'gt.step',d/'gt.stl')
        rec={'cad_id':cid,'selection_bucket':s['selection_bucket'],'difficulty_bin':s['difficulty_bin'],'gt_dsl':gt_code,'gt_token_count':len(tok.encode(gt_code,add_special_tokens=False)),'gt_exec':gt_exec,'steps':{'gt':str(d/'gt.step') if gt_exec['step_reload_pass'] else None},'epochs':{}}
        for ep,pred in [(18,p18[cid]),(20,p20[cid])]:
            ex=execute(pred['pred_dsl'],d/f'epoch{ep}_pred.step',d/f'epoch{ep}_pred.stl');pred['exec']=ex;pred['op_f1']=op_f1(gt_code,pred['pred_dsl']);pred['exact_match']=pred['pred_dsl'].strip()==gt_code.strip();
            if ex['step_reload_pass'] and gt_exec['step_reload_pass']:
                pred['geometry']=mesh_metrics(d/'gt.step',d/f'epoch{ep}_pred.stl')
            rec['epochs'][str(ep)]=pred;rec['steps'][f'epoch{ep}']=str(d/f'epoch{ep}_pred.step') if ex['step_reload_pass'] else None
        cases.append(rec)
    (OUT/'M2_VIS16_PREDICTIONS.jsonl').write_text(''.join(json.dumps({'cad_id':x['cad_id'],'epoch18':x['epochs']['18'],'epoch20':x['epochs']['20']})+'\n' for x in cases))
    (OUT/'M2_VIS16_METRICS.jsonl').write_text(''.join(json.dumps({'cad_id':x['cad_id'],'epoch18':x['epochs']['18'].get('geometry'),'epoch20':x['epochs']['20'].get('geometry'),'gt_step':x['gt_exec']['step_reload_pass'],'e18_step':x['epochs']['18']['exec']['step_reload_pass'],'e20_step':x['epochs']['20']['exec']['step_reload_pass']})+'\n' for x in cases))
    comp=[]
    for x in cases:comp.extend(['='*70,f"CAD_ID = {x['cad_id']}",f"GT:\n{x['gt_dsl']}",f"EPOCH18:\n{x['epochs']['18']['pred_dsl']}",f"EPOCH20:\n{x['epochs']['20']['pred_dsl']}",f"GT token count={x['gt_token_count']} E18={x['epochs']['18']['generated_tokens']} E20={x['epochs']['20']['generated_tokens']}",f"E18 EOS={x['epochs']['18']['eos']} E20 EOS={x['epochs']['20']['eos']}"])
    (OUT/'M2_VIS16_DSL_COMPARISON.txt').write_text('\n\n'.join(comp))
    valid,failed=galleries(cases)
    e18_better=e20_better=ties=0
    for x in cases:
        a,b=x['epochs']['18'],x['epochs']['20'];sa=(int(a['exec']['step_reload_pass']),a['op_f1'],-(a.get('geometry') or {}).get('chamfer_norm',float('inf')));sb=(int(b['exec']['step_reload_pass']),b['op_f1'],-(b.get('geometry') or {}).get('chamfer_norm',float('inf')))
        if sa>sb:e18_better+=1
        elif sb>sa:e20_better+=1
        else:ties+=1
    summary={'VISUALIZATION_STATUS':'PASS','label':'TRAIN_SELF_DECODE_ONLY_NOT_HELDOUT','VIS_SAMPLES':16,'EPOCH18':{k:sum(x['epochs']['18'][k] for x in cases) for k in ['eos','parse_pass']},'EPOCH20':{k:sum(x['epochs']['20'][k] for x in cases) for k in ['eos','parse_pass']},'E18_BETTER_CASES':e18_better,'E20_BETTER_CASES':e20_better,'TIES':ties,'STEP_VISUALIZED':valid,'FAILURE_CASES':failed}
    summary['EPOCH18'].update(exec=sum(x['epochs']['18']['exec']['exec_pass'] for x in cases),STEP_RELOAD=sum(x['epochs']['18']['exec']['step_reload_pass'] for x in cases));summary['EPOCH20'].update(exec=sum(x['epochs']['20']['exec']['exec_pass'] for x in cases),STEP_RELOAD=sum(x['epochs']['20']['exec']['step_reload_pass'] for x in cases))
    (OUT/'M2_VIS16_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
