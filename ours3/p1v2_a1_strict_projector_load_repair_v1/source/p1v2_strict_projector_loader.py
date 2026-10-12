"""Canary-local strict A1 loader: attach frozen CurveProjector before loading weights."""
from __future__ import annotations
import hashlib
from pathlib import Path
import torch
from safetensors.torch import load_file
from transformers import AutoConfig, AutoModelForCausalLM
import spatiallm  # register SpatialLM classes
from spatiallm_curve_token_v1.curve_projector import build_curve_projector

EDGE_KEYS = (
    'edge_proj.net.0.weight', 'edge_proj.net.0.bias',
    'edge_proj.net.2.weight', 'edge_proj.net.2.bias',
)

def tensor_hash(items):
    h=hashlib.sha256()
    for key,tensor in sorted(items.items()):
        raw=tensor.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
        h.update(key.encode()); h.update(raw)
    return h.hexdigest()

def build_and_strict_load(checkpoint: str | Path):
    checkpoint=Path(checkpoint)
    cfg=AutoConfig.from_pretrained(checkpoint,local_files_only=True)
    # Build in checkpoint dtype (float32) so the restore audit can require
    # byte-exact equality rather than accepting runtime casting.
    model=AutoModelForCausalLM.from_config(cfg)
    model.edge_proj=build_curve_projector(256,cfg.hidden_size,'mlp')
    preload={k:model.state_dict()[k].detach().cpu().clone() for k in EDGE_KEYS}
    state={}
    for shard in sorted(checkpoint.glob('model-*-of-*.safetensors')):
        state.update(load_file(str(shard),device='cpu'))
    # HF tied embeddings are intentionally serialized once. Materialize the
    # standard alias so raw torch strict=True can validate the complete schema.
    tied_alias_materialized=False
    if 'lm_head.weight' not in state and getattr(cfg,'tie_word_embeddings',False):
        state['lm_head.weight']=state['model.embed_tokens.weight']
        tied_alias_materialized=True
    model_state=model.state_dict()
    shape_mismatch={k:[list(model_state[k].shape),list(v.shape)] for k,v in state.items() if k in model_state and model_state[k].shape!=v.shape}
    incompatible=model.load_state_dict(state,strict=True)
    return model,state,preload,{
        'missing_keys':list(incompatible.missing_keys),'unexpected_keys':list(incompatible.unexpected_keys),
        'shape_mismatch':shape_mismatch,'tied_lm_head_alias_materialized':tied_alias_materialized,
    }
