#!/usr/bin/env python3
from __future__ import annotations

import ast
import collections
import hashlib
import json
import os
import sys
import shutil
import types
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
CHECKPOINT = Path('/var/tmp/cuiyuehan_mesh2cad/m2_spatial_anchor_q_ablation_formal_train800_v1/A3_ANCHOR_Q32/checkpoint_epoch_07')
OUT = Path('/var/tmp/cuiyuehan_mesh2cad/operation_conditioned_parameter_head_v2')
REPORT_OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/operation_conditioned_parameter_head_v2'
OLD = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1'
sys.path[:0] = [
    str(ROOT / 'scripts/m2_c2_spatial_anchor_q_ablation_v1'),
    str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'),
    str(ROOT / 'scripts/spatiallm_m2_spatial_anchor_v1'),
    str(ROOT / 'scripts/parameter_head_oracle_v1'),
    str(ROOT / 'scripts'), str(ROOT / 'SpatialLM'),
    str(ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code'),
]
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import train_v3_smoke as v3  # noqa: E402
from geometry_prefix_adapter import GeometryPrefixAdapter  # noqa: E402
from spatiallm_m2_spatial_anchor_v1.m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1  # noqa: E402
from run_four_arm_100step_impl import encode, load_anchor, load_raw  # noqa: E402
from common import DEV_MANIFEST, TRAIN_MANIFEST, load_manifest, object_frame  # noqa: E402

CHECKPOINT_TREE_SHA256 = '9dcb175c2667a6403604939d7d0de6321c26f2e6dc86a7a310e06179529c1704'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def operation_char_offsets(text: str) -> dict[tuple[str, int], tuple[int, str]]:
    lines = text.splitlines(keepends=True)
    starts, total = [], 0
    for line in lines:
        starts.append(total); total += len(line)
    result, order = {}, -1
    for stmt in ast.parse(text).body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        name = stmt.targets[0].id
        if name == 'result' or not isinstance(stmt.value, ast.Call) or not isinstance(stmt.value.func, ast.Name):
            continue
        order += 1
        func = stmt.value.func
        result[(name, order)] = (starts[func.lineno - 1] + func.col_offset, func.id)
    return result


def find_operation_token(tokenizer, target_ids: list[int], text: str, char_offset: int, op_name: str) -> tuple[int, str]:
    approx = len(tokenizer.encode(text[:char_offset], add_special_tokens=False))
    candidates = []
    for i in range(max(0, approx - 4), min(len(target_ids), approx + 5)):
        decoded = tokenizer.decode(target_ids[i:i + 4], skip_special_tokens=False)
        pos = decoded.find(op_name)
        if pos >= 0:
            candidates.append((abs(i - approx), i, decoded))
    if not candidates:
        raise RuntimeError(f'cannot locate operation token {op_name} near {approx}')
    _, index, decoded = min(candidates)
    return index, decoded


def full_curve_memory(row: dict) -> np.ndarray:
    tokens = np.load(row['m2_full_c2_tokens']).astype(np.float32)
    curves = np.load(row['m2_full_curves'], allow_pickle=True)
    xyz = curves['curve_xyz'][np.arange(len(tokens), dtype=np.int64)]
    center, scale, _, _ = object_frame(row)
    anchors = np.concatenate([(xyz.mean(1) - center) / scale, (xyz.max(1) - xyz.min(1)) / scale], axis=1).astype(np.float32)
    if tokens.shape[1] != 256 or anchors.shape != (len(tokens), 6):
        raise RuntimeError(f'curve memory contract failed: {row["cad_id"]}')
    return np.concatenate([tokens, anchors], axis=1)


def install_geometry(model, branch, runtime: dict):
    original_splice = v3.module._splice_geometry

    def forward_geometry(self, surface_points, edge_points=None, device=None, dtype=None):
        surface = runtime['precomputed_surface'].to(device=device, dtype=dtype)
        z = edge_points.to(device=device, dtype=next(branch.parameters()).dtype)
        if z.ndim == 2: z = z.unsqueeze(0)
        anchors = runtime['selected_anchors'].to(device=device, dtype=z.dtype).unsqueeze(0)
        valid = runtime['selected_mask'].to(device).unsqueeze(0)
        fused = branch.anchor_mlp(z, anchors)
        second, summary_mask = branch.geometry_adapter(fused, valid)
        runtime['surface_memory'] = surface.detach()
        runtime['summary_mask'] = summary_mask[0]
        return surface, second.to(dtype)

    def splice(embeds, mask, regions):
        masks = [torch.ones(regions[0][1].shape[0], dtype=torch.bool, device=mask.device), runtime['summary_mask'].to(mask.device)]
        return v3.splice_geometry_masked(embeds, mask, regions, masks)

    model.forward_geometry = types.MethodType(forward_geometry, model)
    v3.module._splice_geometry = splice
    return original_splice


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f'refusing overwrite: {OUT}')
    OUT.mkdir(parents=True); (OUT / 'features').mkdir(); REPORT_OUT.mkdir(parents=True, exist_ok=False)
    train_rows, dev_rows = load_manifest(TRAIN_MANIFEST), load_manifest(DEV_MANIFEST)
    train_labels = load_jsonl(OLD / 'oracle_labels_train.jsonl'); dev_labels = load_jsonl(OLD / 'oracle_labels_dev.jsonl')
    labels_by_split = {'train': train_labels, 'dev': dev_labels}
    rows_by_split = {'train': {r['cad_id']: r for r in train_rows}, 'dev': {r['cad_id']: r for r in dev_rows}}
    v3.heldout_geometry.install()
    plugin = v3.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT, local_files_only=True, use_fast=False)
    device = torch.device('cuda:0')
    model = v3.module.SpatialLMLlamaForCausalLM.from_pretrained(CHECKPOINT, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    adapter = GeometryPrefixAdapter(256, model.config.hidden_size, num_queries=32, target_norm=1.9414).to(device=device, dtype=torch.bfloat16)
    branch = M2C2SpatialAnchorV1(adapter).to(device=device, dtype=torch.bfloat16)
    branch.load_state_dict(torch.load(CHECKPOINT / 'geometry_branch.pt', map_location=device, weights_only=True))
    model.edge_proj = branch; model.config.separate_edge_tokens = True; model.separate_edge_tokens = True; model.config.use_cache = False
    for p in model.parameters(): p.requires_grad_(False)
    model.eval()
    # Hidden-state extraction does not need vocabulary logits or CE.
    original_loss = v3.module._chunked_lm_loss
    v3.module._chunked_lm_loss = lambda lm_head, hidden, labels: hidden.sum() * 0.0
    runtime = {}; original_splice = install_geometry(model, branch, runtime)
    audit_rows, instance_rows = [], []
    try:
        for split in ('train', 'dev'):
            grouped = collections.defaultdict(list)
            for label in labels_by_split[split]: grouped[label['cad_id']].append(label)
            for cad_index, cad_id in enumerate(sorted(grouped), 1):
                row = rows_by_split[split][cad_id]; target_text = Path(row['target_dsl']).read_text()
                encoded_ids, _, prompt_len = encode(tokenizer, row, 32)
                prompt_ids = encoded_ids[0, :prompt_len].tolist()
                target_ids = tokenizer.encode(target_text + '<|eot_id|>', add_special_tokens=False)
                geometry_extra = int(row['B1']['total_llm_input_length']) - int(row['k_valid']) + 32
                allowance = max(32, 4096 - geometry_extra - prompt_len)
                offsets = operation_char_offsets(target_text)
                surface_np, _ = plugin._load_cad_separate_edge(row['surface_input'])
                surface_single = torch.tensor(surface_np, device=device)
                surface = surface_single.unsqueeze(0)
                with torch.inference_mode():
                    runtime['precomputed_surface'] = model.forward_point_cloud(surface_single, device, torch.bfloat16, projector=model.point_proj).detach()
                selected_raw, selected_mask = load_raw(row)
                runtime['selected_mask'] = selected_mask
                runtime['selected_anchors'] = load_anchor(row)
                edge = selected_raw.to(device).unsqueeze(0)
                surface_memory = runtime['precomputed_surface'][0].float().cpu().numpy().astype(np.float16)
                curve_memory = full_curve_memory(row).astype(np.float16)
                operations = collections.defaultdict(dict)
                for label in grouped[cad_id]: operations[(label['assignment'], label['operation_order'])][label['head_type']] = label
                query_vectors, op_meta = [], []
                for (assignment, operation_order), kinds in sorted(operations.items(), key=lambda x: x[0][1]):
                    char_offset, op_name = offsets[(assignment, operation_order)]
                    target_index, decoded = find_operation_token(tokenizer, target_ids, target_text, char_offset, op_name)
                    window_start = max(0, target_index - allowance + 1)
                    window = target_ids[window_start:target_index + 1]
                    ids = torch.tensor([prompt_ids + window], dtype=torch.long)
                    labels = torch.tensor([[-100] * prompt_len + window], dtype=torch.long)
                    original_index = prompt_len + target_index - window_start
                    point_start = int(torch.where(ids[0] == model.config.point_start_token_id)[0][0]); point_end = int(torch.where(ids[0] == model.config.point_end_token_id)[0][0])
                    edge_start = int(torch.where(ids[0] == model.edge_start_token_id)[0][0]); edge_end = int(torch.where(ids[0] == model.edge_end_token_id)[0][0])
                    regions = [(point_start, surface_memory.shape[0], point_end), (edge_start, 32, edge_end)]
                    with torch.inference_mode():
                        output = model(input_ids=ids.to(device), attention_mask=torch.ones_like(ids, device=device), labels=labels.to(device),
                                       point_clouds=surface, edge_clouds=edge, output_hidden_states=True, return_dict=True)
                    hidden = output.hidden_states[-1][0]
                    spliced_index = original_index
                    for start, count, end in regions:
                        if original_index >= end: spliced_index += count - (end - start - 1)
                    if spliced_index >= hidden.shape[0]: raise RuntimeError(f'hidden index overflow {cad_id}/{assignment}')
                    query = hidden[spliced_index].float().cpu().numpy().astype(np.float16)
                    if query.shape != (2048,) or not np.isfinite(query).all(): raise RuntimeError('invalid operation query')
                    query_vectors.append(query)
                    base = next(iter(kinds.values()))
                    related = sorted({int(row['selected_m2_indices'][i]) for label in kinds.values() for i in label['token_indices']})
                    targets = {}
                    if 'circle' in kinds:
                        targets['circle'] = kinds['circle']['target_norm']
                    if 'extrude' in kinds:
                        targets['extrude'] = kinds['extrude']['target_norm']
                        targets['extrude']['depth_two_active'] = bool(kinds['extrude'].get('two_sided')) and not bool(kinds['extrude'].get('symmetric'))
                    if 'box' in kinds: targets['box'] = kinds['box']['target_norm']
                    op_meta.append({'cad_id': cad_id, 'split': split, 'assignment': assignment, 'operation_order': operation_order,
                                    'operation_type': op_name, 'query_token_original_index': original_index, 'query_token_spliced_index': spliced_index,
                                    'query_token_decoded_window': decoded, 'target_prefix_window_start': window_start,
                                    'target_prefix_left_truncated': window_start > 0, 'related_curve_full_indices': related, 'targets': targets,
                                    'object_center': base['object_center'], 'object_scale': base['object_scale'], 'target_dsl': base['target_dsl']})
                feature_path = OUT / 'features' / f'{cad_id}.npz'
                np.savez_compressed(feature_path, operation_queries=np.stack(query_vectors), surface_memory=surface_memory, curve_memory=curve_memory)
                for local_index, meta in enumerate(op_meta):
                    meta['feature_path'] = str(feature_path); meta['feature_operation_index'] = local_index
                    instance_rows.append(meta)
                audit_rows.append({'cad_id': cad_id, 'split': split, 'operation_count': len(op_meta), 'query_shape': [len(op_meta), 2048],
                                   'surface_memory_shape': list(surface_memory.shape), 'curve_memory_shape': list(curve_memory.shape),
                                   'surface_finite': bool(np.isfinite(surface_memory).all()), 'curve_finite': bool(np.isfinite(curve_memory).all()),
                                   'operation_indices': [m['operation_order'] for m in op_meta], 'operation_assignments': [m['assignment'] for m in op_meta],
                                   'feature_sha256': sha256(feature_path)})
                if cad_index % 20 == 0 or cad_index == len(grouped):
                    print(f'[{split}] feature extraction {cad_index}/{len(grouped)}', flush=True)
    finally:
        v3.module._splice_geometry = original_splice; v3.module._chunked_lm_loss = original_loss
    with (OUT / 'instances.jsonl').open('w') as f:
        for item in instance_rows: f.write(json.dumps(item) + '\n')
    report = {
        'EXPERIMENT': 'OPERATION_CONDITIONED_PARAMETER_HEAD_V2', 'PHASE': 'DATASET_OPERATION_QUERY_AUDIT',
        'BEST_ARM': 'A3_ANCHOR_Q32', 'BEST_EPOCH': 7, 'BEST_CHECKPOINT': str(CHECKPOINT), 'BEST_CHECKPOINT_TREE_SHA256': CHECKPOINT_TREE_SHA256,
        'OPERATION_QUERY_CONTRACT': 'Frozen A3 final-layer hidden state at first token of GT constructor name under teacher forcing; causal target-prefix is left-truncated only when required by frozen 4096 context',
        'OPERATION_QUERY_DIM': 2048, 'SURFACE_MEMORY_DIM': 2048, 'CURVE_MEMORY_DIM': 262,
        'CURVE_MEMORY_SCOPE': 'all frozen C2 tokens plus frozen-recipe 6D anchors; no oracle hard attention mask',
        'TRAIN_SOURCE_CAD_COUNT': 800, 'DEV_SOURCE_CAD_COUNT': 50,
        'TRAIN_PARAMETER_CAD_COUNT': sum(r['split'] == 'train' for r in audit_rows), 'DEV_PARAMETER_CAD_COUNT': sum(r['split'] == 'dev' for r in audit_rows),
        'TRAIN_OPERATION_INSTANCE_COUNT': sum(i['split'] == 'train' for i in instance_rows), 'DEV_OPERATION_INSTANCE_COUNT': sum(i['split'] == 'dev' for i in instance_rows),
        'ALL_QUERY_SHAPES_VALID': all(r['query_shape'][1] == 2048 for r in audit_rows),
        'ALL_SURFACE_MEMORY_VALID': all(r['surface_memory_shape'][1] == 2048 and r['surface_finite'] for r in audit_rows),
        'ALL_CURVE_MEMORY_VALID': all(r['curve_memory_shape'][1] == 262 and r['curve_finite'] for r in audit_rows),
        'GT_LABELS_AND_ACTIVE_MASK_SOURCE': 'PARAMETER_HEAD_ORACLE_V1 oracle labels plus Routing V2 semantics',
        'AUDIT_ROWS': audit_rows,
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (REPORT_OUT / 'DATASET_OPERATION_QUERY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    (REPORT_OUT / 'FEATURE_CACHE_POINTER.json').write_text(json.dumps({'CACHE_ROOT': str(OUT), 'INSTANCES': str(OUT / 'instances.jsonl')}, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'AUDIT_ROWS'}, indent=2))


if __name__ == '__main__': main()
