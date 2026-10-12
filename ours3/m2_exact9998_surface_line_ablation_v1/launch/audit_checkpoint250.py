#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
import torch
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
EXP=ROOT/'ours3/m2_exact9998_surface_line_ablation_v1'
CK=EXP/'runs/a1/checkpoint-250'
sys.path[:0]=[str(ROOT),str(ROOT/'SpatialLM'),str(ROOT/'scripts')]
os.environ.update(CAD_SECOND_STREAM='curve_tokens',CAD_USE_SEPARATE_EDGE_TOKENS='1',CURVE_ABLATION_ARM='line',CURVE_ABLATION_VIEW=str(ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A1_LINE_CURVE_VIEW.jsonl'))
import curve_ablation_runtime
curve_ablation_runtime.install()
from spatiallm.model.spatiallm_llama import SpatialLMLlamaForCausalLM
from spatiallm.tuner.framework import patcher
from transformers import AutoConfig, get_cosine_schedule_with_warmup
from transformers.trainer import get_parameter_names, ALL_LAYERNORM_LAYERS
from safetensors.torch import load_file

def main():
    required=['optimizer.pt','scheduler.pt','trainer_state.json','rng_state.pth','model.safetensors.index.json']
    present={name:(CK/name).is_file() for name in required}
    config=AutoConfig.from_pretrained(CK,local_files_only=True)
    model=SpatialLMLlamaForCausalLM(config)
    patcher._attach_edge_projector(model)
    index=json.load(open(CK/'model.safetensors.index.json'))['weight_map']
    state={}
    for shard in sorted(set(index.values())):
        state.update(load_file(CK/shard,device='cpu'))
    tied_alias_added=False
    if 'lm_head.weight' not in state and 'model.embed_tokens.weight' in state:
        state['lm_head.weight']=state['model.embed_tokens.weight']; tied_alias_added=True
    model.load_state_dict(state,strict=True)
    model.tie_weights()
    del state
    for p in model.point_backbone.parameters(): p.requires_grad_(False)
    decay=set(get_parameter_names(model,ALL_LAYERNORM_LAYERS))
    decay={name for name in decay if 'bias' not in name}
    named=[(name,p) for name,p in model.named_parameters() if p.requires_grad]
    groups=[{'params':[p for name,p in named if name in decay],'weight_decay':0.0},{'params':[p for name,p in named if name not in decay],'weight_decay':0.0}]
    optimizer=torch.optim.AdamW(groups,lr=2e-5)
    optimizer.load_state_dict(torch.load(CK/'optimizer.pt',map_location='cpu',weights_only=False))
    scheduler=get_cosine_schedule_with_warmup(optimizer,num_warmup_steps=1200,num_training_steps=39980)
    scheduler.load_state_dict(torch.load(CK/'scheduler.pt',map_location='cpu',weights_only=False))
    trainer=json.load(open(CK/'trainer_state.json'))
    rng=torch.load(CK/'rng_state.pth',map_location='cpu',weights_only=False)
    keys=sorted(k for k in model.state_dict() if k.startswith('edge_proj.'))
    report={'checkpoint':str(CK),'GLOBAL_STEP':trainer['global_step'],'files_present':present,'PROJECTOR_KEYS':len(keys),'projector_key_names':keys,'PROJECTOR_PARAM_N':sum(p.numel() for p in model.edge_proj.parameters()),'MODEL_STRICT_RELOAD':'PASS','tied_lm_head_alias_restored':tied_alias_added,'PROJECTOR_RELOAD':'PASS','OPTIMIZER_RELOAD':'PASS','SCHEDULER_RELOAD':'PASS','TRAINER_STATE_RELOAD':'PASS','RNG_RELOAD':'PASS','optimizer_state_entries':len(optimizer.state),'scheduler_last_epoch':scheduler.last_epoch,'rng_keys':sorted(rng) if isinstance(rng,dict) else None,'pass':all(present.values()) and len(keys)==4 and trainer['global_step']==250}
    (EXP/'audits/A1_CHECKPOINT250_AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
