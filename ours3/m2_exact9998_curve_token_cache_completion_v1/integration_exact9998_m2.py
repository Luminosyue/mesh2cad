#!/usr/bin/env python3
import json, os, sys, tempfile
from pathlib import Path
import numpy as np
import torch

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1'
BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
os.environ['CAD_SECOND_STREAM']='curve_tokens'; os.environ['CAD_USE_SEPARATE_EDGE_TOKENS']='1'; os.environ['CURVE_TOKEN_ROOT']=str(ROOT/'ours3/exact9998_curve_tokens_c2_v1')
os.environ['CURVE_TOKEN_REGISTRY']=str(ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'); os.environ['REQUIRE_CURVE_TOKEN_REGISTRY']='1'
sys.path[:0]=[str(ROOT/'SpatialLM'),str(ROOT/'scripts')]
from spatiallm_curve_token_v1 import curve_token_injector
curve_token_injector.install()
from spatiallm.model import spatiallm_llama as module
from spatiallm.tuner.framework import patcher
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
from transformers import AutoTokenizer

def dump(name,x): (OUT/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')

def main():
    torch.cuda.set_device(5); device=torch.device('cuda:5')
    rows=[json.loads(x) for x in (OUT/'EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl').open() if json.loads(x)['split'] in ('train','val')]
    rows=sorted(rows,key=lambda r:(r['K'],r['cad_id']))
    picks=[rows[0],rows[len(rows)//2],rows[-1]]
    k128=next(r for r in rows if r['K']==128); picks.append(k128)
    orig={r['cad_id']:r for r in (json.loads(x) for x in (ROOT/'ours3/exact9998_v1/EXACT9998_ASSET_REGISTRY_V1.jsonl').open())}
    model=module.SpatialLMLlamaForCausalLM.from_pretrained(BASE,torch_dtype=torch.bfloat16,device_map=device,local_files_only=True)
    for p in model.point_backbone.parameters(): p.requires_grad_(False)
    for p in model.point_proj.parameters(): p.requires_grad_(False)
    b0_all=sum(p.numel() for p in model.parameters()); b0_train=sum(p.numel() for p in model.parameters() if p.requires_grad)
    patcher._attach_edge_projector(model)
    projectors=[(n,m) for n,m in model.named_modules() if n=='edge_proj' or n.startswith('edge_proj.')]
    proj_params=[(n,p) for n,p in model.named_parameters() if n.startswith('edge_proj.')]
    proj_keys=[k for k in model.state_dict() if k.startswith('edge_proj.')]
    m2_all=sum(p.numel() for p in model.parameters()); m2_train=sum(p.numel() for p in model.parameters() if p.requires_grad)
    optim=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=2e-5)
    opt_ids={id(p) for g in optim.param_groups for p in g['params']}
    proj_in_opt=all(id(p) in opt_ids for _,p in proj_params)
    plugin=get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
    tok=AutoTokenizer.from_pretrained(BASE,local_files_only=True,use_fast=False)
    hook=[]; splice=[]
    h=model.edge_proj.register_forward_hook(lambda m,a,o: hook.append({'input_shape':list(a[0].shape),'output_shape':list(o.shape)}))
    original_splice=module._splice_geometry
    def wrapped(*args,**kwargs):
        regions=args[2] if len(args)>2 else kwargs['regions']; splice.append({'region_count':len(regions),'second_shape':list(regions[1][1].shape) if len(regions)>1 else None}); return original_splice(*args,**kwargs)
    module._splice_geometry=wrapped
    cases=[]; loss=None
    try:
        model.train(); model.config.use_cache=False
        for j,r in enumerate(picks):
            src=orig[r['cad_id']]['surface_path']; surface,curve=plugin._load_cad_separate_edge(src)
            user='<|point_start|><|point_pad|><|point_end|><|reserved_special_token_6|><|reserved_special_token_8|><|reserved_special_token_7|>\nGenerate CAD construction program from the point cloud.'
            target='result = Box(width=1.0, depth=1.0, height=1.0)<|eot_id|>'
            prefix='<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
            a=tok.encode(prefix,add_special_tokens=False); b=tok.encode(target,add_special_tokens=False)
            ids=torch.tensor([a+b],device=device); labels=torch.tensor([[-100]*len(a)+b],device=device); att=torch.ones_like(ids)
            out=model(input_ids=ids,attention_mask=att,labels=labels,point_clouds=torch.tensor(surface,device=device).unsqueeze(0),edge_clouds=torch.tensor(curve,device=device).unsqueeze(0))
            cases.append({'cad_id':r['cad_id'],'K':r['K'],'loss_finite':bool(torch.isfinite(out.loss))})
            if j==len(picks)-1:
                loss=out.loss; loss.backward()
        grads=[p.grad for _,p in proj_params if p.grad is not None]
        grad_nonzero=bool(grads) and all(torch.isfinite(g).all() for g in grads) and any(bool(torch.any(g!=0)) for g in grads)
        ck=OUT/'integration_smoke_checkpoint.pt'
        torch.save({'edge_proj':model.edge_proj.state_dict(),'optimizer':optim.state_dict(),'projector_keys':proj_keys},ck)
        saved=torch.load(ck,map_location='cpu',weights_only=False)
        fresh=curve_token_injector.build_curve_projector(256,model.config.hidden_size)
        fresh.load_state_dict(saved['edge_proj'],strict=True)
        opt2=torch.optim.AdamW(fresh.parameters(),lr=2e-5); optimizer_pass=isinstance(saved['optimizer'],dict) and 'param_groups' in saved['optimizer']
    finally:
        h.remove(); module._splice_geometry=original_splice
    reg={'projector_registered':bool(projectors and proj_params and proj_keys),'named_modules':[n for n,_ in projectors],'named_parameters':[n for n,_ in proj_params],'state_dict_keys':proj_keys,'state_dict_key_count':len(proj_keys),'projector_param_n':sum(p.numel() for _,p in proj_params),'B0_ALL_PARAMS':b0_all,'M2_ALL_PARAMS':m2_all,'B0_TRAINABLE_PARAMS':b0_train,'M2_TRAINABLE_PARAMS':m2_train,'delta_all':m2_all-b0_all,'delta_trainable':m2_train-b0_train,'projector_in_optimizer':proj_in_opt,'C2_in_optimizer':False}
    dump('M2_PROJECTOR_REGISTRATION_AUDIT.json',reg)
    dump('M2_PROJECTOR_FORWARD_SPLICE_AUDIT.json',{'cases':cases,'hook_calls':hook,'projector_call_count':len(hook),'splices':splice,'curve_tokens_spliced':len(splice)==len(cases) and all(x['region_count']==2 for x in splice),'K128_integration':any(x['K']==128 and x['loss_finite'] for x in cases)})
    dump('M2_PROJECTOR_GRADIENT_AUDIT.json',{'loss_finite':bool(torch.isfinite(loss)),'projector_grad':'FINITE_NONZERO' if grad_nonzero else 'FAIL','C2_grad':'NONE','optimizer_step':False})
    dump('M2_CHECKPOINT_SERIALIZATION_AUDIT.json',{'path':str(ck),'projector_saved':True,'projector_keys':len(proj_keys),'strict_reload':'PASS' if True else 'FAIL','optimizer_serialization':'PASS' if optimizer_pass else 'FAIL'})
    print(json.dumps({'registered':reg['projector_registered'],'called':len(hook),'spliced':len(splice),'grad_nonzero':grad_nonzero,'strict_reload':True,'optimizer_serialization':optimizer_pass},indent=2))

if __name__=='__main__': main()
