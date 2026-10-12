#!/usr/bin/env python3
"""Build the isolated Qwen V3 geometry base: Instruct LLM + SpatialLM1.1-Qwen encoder."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, shutil, sys

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0] = [str(ROOT / 'SpatialLM'), str(ROOT / 'scripts')]

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from spatiallm.model.spatiallm_qwen import SpatialLMQwenForCausalLM

QWEN_INSTRUCT = ROOT / 'SpatialLM/models/Qwen2.5-0.5B-Instruct'
SPATIAL_QWEN = ROOT / 'SpatialLM/models/SpatialLM1.1-Qwen-0.5B'
OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/qwen05_v3_1k/QWEN_GEOMETRY_BASE_V1'

# Reuse unused Qwen special-token ids (no vocab / embedding resize).
TOKEN_RENAMES = {
    '<|image_pad|>': '<|edge_start|>',
    '<|video_pad|>': '<|edge_end|>',
    '<|object_ref_start|>': '<|edge_pad|>',
}
EDGE_START_ID = 151655
EDGE_END_ID = 151656
EDGE_PAD_ID = 151646


def sha_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def llm_hash(model) -> str:
    h = hashlib.sha256()
    for k, t in sorted(model.state_dict().items()):
        if k.startswith(('point_backbone.', 'point_proj.', 'edge_proj.')):
            continue
        x = t.detach().cpu().contiguous()
        h.update(k.encode() + b'\0')
        h.update(str(tuple(x.shape)).encode() + b'\0')
        h.update(str(x.dtype).encode() + b'\0')
        h.update(x.view(torch.uint8).numpy().tobytes())
    return h.hexdigest()


def rewrite_tokenizer_files(src: pathlib.Path, dst: pathlib.Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in (
        'tokenizer.json',
        'tokenizer_config.json',
        'special_tokens_map.json',
        'added_tokens.json',
        'vocab.json',
        'merges.txt',
        'generation_config.json',
    ):
        p = src / name
        if p.exists():
            shutil.copy2(p, dst / name)
    for name in ('tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json', 'added_tokens.json'):
        p = dst / name
        if not p.exists():
            continue
        text = p.read_text()
        for old, new in TOKEN_RENAMES.items():
            text = text.replace(old, new)
        p.write_text(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--device', default='cpu')
    a = ap.parse_args()
    if OUT.exists():
        raise RuntimeError(f'refusing to overwrite {OUT}')
    if not (SPATIAL_QWEN / 'model.safetensors').exists() and not (SPATIAL_QWEN / 'model.safetensors.index.json').exists():
        raise RuntimeError(f'missing SpatialLM1.1-Qwen weights at {SPATIAL_QWEN}')
    if not (QWEN_INSTRUCT / 'model.safetensors').exists():
        raise RuntimeError(f'missing Qwen Instruct weights at {QWEN_INSTRUCT}')

    print('Loading SpatialLM1.1-Qwen (encoder + projector)...', flush=True)
    model = SpatialLMQwenForCausalLM.from_pretrained(
        SPATIAL_QWEN, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True, local_files_only=True
    )
    print('Loading Qwen2.5-0.5B-Instruct LLM...', flush=True)
    llm = AutoModelForCausalLM.from_pretrained(
        QWEN_INSTRUCT, torch_dtype=torch.bfloat16, local_files_only=True
    )
    before_encoder = {k: v.detach().cpu().clone() for k, v in model.state_dict().items() if k.startswith(('point_backbone.', 'point_proj.'))}
    missing, unexpected = model.load_state_dict(llm.state_dict(), strict=False)
    missing_nontime = [k for k in missing if not k.startswith(('point_backbone.', 'point_proj.'))]
    if missing_nontime:
        raise RuntimeError(f'LLM load left non-encoder missing keys: {missing_nontime[:20]}')
    if unexpected:
        raise RuntimeError(f'LLM load unexpected keys: {unexpected[:20]}')
    for k, v in before_encoder.items():
        now = model.state_dict()[k].detach().cpu()
        if not torch.equal(v, now):
            raise RuntimeError(f'encoder tensor mutated during LLM load: {k}')
    del llm

    model.config.architectures = ['SpatialLMQwenForCausalLM']
    model.config.model_type = 'spatiallm_qwen'
    model.config.use_cache = False
    model.config.edge_start_token_id = EDGE_START_ID
    model.config.edge_end_token_id = EDGE_END_ID
    model.config.edge_token_id = EDGE_PAD_ID
    model.config.separate_edge_tokens = False

    OUT.mkdir(parents=True)
    rewrite_tokenizer_files(SPATIAL_QWEN, OUT)
    tok = AutoTokenizer.from_pretrained(OUT, local_files_only=True, use_fast=False)
    for name, expected in (
        ('<|point_start|>', 151652),
        ('<|point_end|>', 151653),
        ('<|point_pad|>', 151654),
        ('<|edge_start|>', EDGE_START_ID),
        ('<|edge_end|>', EDGE_END_ID),
        ('<|edge_pad|>', EDGE_PAD_ID),
        ('<|im_end|>', 151645),
    ):
        got = tok.convert_tokens_to_ids(name)
        if got != expected:
            raise RuntimeError(f'tokenizer id mismatch {name}: {got} != {expected}')
    tok.save_pretrained(OUT)
    print('Saving SpatialLM-Qwen geometry base...', flush=True)
    model.save_pretrained(OUT, safe_serialization=True, max_shard_size='2GB')

    contract = {
        'contract': 'QWEN_GEOMETRY_BASE_V1',
        'status': 'FROZEN',
        'parent_for_arms': ['B0', 'B1_V3', 'M2_V3'],
        'llm': {
            'name': 'Qwen2.5-0.5B-Instruct',
            'path': str(QWEN_INSTRUCT),
            'hidden_size': int(model.config.hidden_size),
            'vocab_size': int(model.config.vocab_size),
            'state_sha256': llm_hash(model),
            'source_sha256': sha_file(QWEN_INSTRUCT / 'model.safetensors'),
        },
        'geometry_frontend': {
            'sonata': {'source': 'SpatialLM1.1-Qwen-0.5B', 'frozen': True},
            'surface_projector': {'source': 'SpatialLM1.1-Qwen-0.5B', 'frozen': True},
        },
        'marker_contract': {
            'point_start': 151652,
            'point_end': 151653,
            'point_pad': 151654,
            'edge_start': EDGE_START_ID,
            'edge_end': EDGE_END_ID,
            'edge_pad': EDGE_PAD_ID,
            'im_end': 151645,
            'vocab_size': 151936,
            'embedding_rows_added': 0,
        },
        'chat_template': 'qwen_im_start',
        'llama_v3_run_untouched': True,
        'official_test_read': False,
        'files': {p.name: {'size': p.stat().st_size, 'sha256': sha_file(p)} for p in sorted(OUT.iterdir()) if p.is_file()},
    }
    (OUT / 'BASE_CONTRACT.json').write_text(json.dumps(contract, indent=2) + '\n')
    print(json.dumps({k: contract[k] for k in ('contract', 'llm', 'marker_contract')}, indent=2))


if __name__ == '__main__':
    main()
