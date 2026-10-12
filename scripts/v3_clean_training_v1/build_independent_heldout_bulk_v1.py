#!/usr/bin/env python3
"""Build an isolated clean V3 held-out pool using the frozen Canary20 path.

No training, decoding, test inference, Dora, or modification of legacy roots.
Assets are created only beneath eval_protocol_v2/new_heldout_pool/bulk_build_v1.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EVAL = ROOT / 'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool'
OUT = EVAL / 'bulk_build_v1'
CANDIDATES = EVAL / 'PREBUILD_ELIGIBLE_CANDIDATES.jsonl'
TRAIN_MANIFEST = ROOT / 'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
C2_CKPT = ROOT / 'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
C2_SHA = '553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
M2_CKPT = ROOT / 'ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_15'
LIMIT, TARGET, CHUNK = 4096, 200, 25
SEED = 'INDEPENDENT_HELDOUT_BULK_V1_2026-09-02'
DEVICE = torch.device(os.environ.get('BULK_BUILD_DEVICE', 'cuda:1'))

sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/spatiallm_geometry_prefix_v3')]
from geometry_pack_v1 import pack
import curve_token_v1.build_dataset as curves
import spatiallm_curve_token_c2_frozen_v2.export_curve_tokens as exporter
import train_v3_smoke as core
from v3_canary_surface_adapter import load_surface_for_encoder


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def stable_key(row: dict) -> str:
    return hashlib.sha256((SEED + '|' + row['candidate_id']).encode()).hexdigest()


def prompt(tokenizer, arm: str) -> list[int]:
    user = core.markers(arm) + '\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
    text = '<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n' + user + '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
    return tokenizer.encode(text, add_special_tokens=False)


def execute_gt(dsl: str, work: Path) -> dict:
    result = dict(dsl_parse=False, dsl_exec=False, step_write=False, step_reload=False, error_short=None)
    try:
        spec = importlib.util.spec_from_file_location('bulk_placement_v3_cad_dsl', ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py')
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
        code = module.extract_dsl_code(dsl); module.parse_dsl(code); result['dsl_parse'] = True
        import cadquery as cq
        step, stl = work / 'gt_replay.step', work / 'gt_replay.stl'
        module.execute_dsl(code, step, stl); result['dsl_exec'] = True
        result['step_write'] = step.is_file() and stl.is_file()
        if result['step_write']:
            cq.importers.importStep(str(step)); result['step_reload'] = True
    except Exception as e:
        result['error_short'] = (type(e).__name__ + ': ' + str(e))[-500:]
    return result


def capture_splice_labels(fn):
    """Use the production V3 label-splice implementation and retain its output."""
    captured = []
    original = core.module._splice_labels
    def wrapped(labels, regions, target_len):
        value = original(labels, regions, target_len)
        captured.append(value.detach().cpu())
        return value
    core.module._splice_labels = wrapped
    try:
        result = fn()
    finally:
        core.module._splice_labels = original
    return result, captured[-1] if captured else None


def freeze_inputs() -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=False)
    for d in ('manifests', 'DeepCAD', 'Fusion360', 'audits', 'clean', 'rejected'):
        (OUT / d).mkdir()
    train = json.loads(TRAIN_MANIFEST.read_text())
    freeze = {
        'TRAIN688_SHA256': sha256(TRAIN_MANIFEST), 'TRAIN688_COUNT': len(train['records']),
        'TRAIN688_FROZEN': True, 'legacy_roots_modified': False,
        'purpose': 'independent held-out construction only; no model evaluation',
    }
    (OUT / 'audits/BULK_BUILD_FREEZE_AUDIT.json').write_text(json.dumps(freeze, indent=2) + '\n')
    rows = [json.loads(x) for x in CANDIDATES.read_text().splitlines() if x]
    # Dataset-stratified deterministic order at the observed train688 ratio: 594:94.
    deep = sorted((r for r in rows if r['dataset'] == 'DeepCAD'), key=stable_key)
    fusion = sorted((r for r in rows if r['dataset'] == 'Fusion360'), key=stable_key)
    ordered, di, fi = [], 0, 0
    while di < len(deep) or fi < len(fusion):
        use_deep = (len(ordered) * 94) % 688 >= 94  # avoided below; retained only as explicit deterministic rule note
        # Choose next source so running share stays closest to frozen 594/688.
        want_deep = round((len(ordered) + 1) * 594 / 688)
        if (di < len(deep) and (di < want_deep or fi >= len(fusion))):
            ordered.append(deep[di]); di += 1
        elif fi < len(fusion):
            ordered.append(fusion[fi]); fi += 1
        else:
            ordered.append(deep[di]); di += 1
    out_rows = []
    for i, row in enumerate(ordered):
        out_rows.append({
            'index': i, 'cad_id': row['candidate_id'], 'dataset': row['dataset'],
            'source_path': row['source_path'], 'source_step_path': str(Path(row['source_path']) / 'model.step'),
            'source_step_sha256': row['source_step_sha256'], 'complexity': row.get('complexity', 'UNKNOWN'),
            'prebuild_leakage_pass': row['prebuild_leakage_pass'],
        })
    order = {'seed': SEED, 'algorithm': 'per-dataset SHA256 order, deterministically interleaved to train688 594:94 dataset ratio; no build-result feedback',
             'candidate_count': len(out_rows), 'complexity_status': 'UNKNOWN if absent in prebuild metadata', 'records': out_rows}
    order_path = OUT / 'manifests/BULK_CANDIDATE_ORDER.json'; order_path.write_text(json.dumps(order, indent=2) + '\n')
    (OUT / 'manifests/BULK_CANDIDATE_ORDER_SHA256.txt').write_text(sha256(order_path) + '\n')
    return out_rows


def phase_a(row: dict, c2_model) -> dict:
    cid, ds, sid = row['cad_id'], row['dataset'], row['cad_id'].split('__', 1)[1]
    base = OUT / ds / sid; base.mkdir(parents=True, exist_ok=False)
    gp, curve_dir = base / 'geometry_pack_v1' / sid, base / 'curve_data'
    audit = {
        **row, 'source_load_pass': False, 'mesh_tessellation_pass': False,
        'surface_build_pass': False, 'surface_shape_8192x6_pass': False,
        'surface_finite_pass': False, 'surface_normal_pass': False, 'surface_transform_pass': False,
        'dsl_exists': False, 'has_result': False, 'dsl_parse': False, 'dsl_exec': False,
        'step_write': False, 'step_reload': False, 'gt_curve_exists': False,
        'gt_curve_sanity': 'FAIL', 'c2_input_valid': False, 'c2_valid': False,
        'phase_a_pass': False, 'primary_reject_reason': None, 'secondary_reject_reasons': [],
    }
    try:
        source = Path(row['source_path']); step = source / 'model.step'
        audit['source_load_pass'] = step.is_file() and sha256(step) == row['source_step_sha256']
        if not audit['source_load_pass']: raise RuntimeError('SOURCE')
        (base / 'SOURCE_PROVENANCE.json').write_text(json.dumps({'source_path': str(source), 'source_step_path': str(step), 'source_step_sha256': sha256(step)}, indent=2) + '\n')
        pack.build_one(source, gp.parent, overwrite=False)
        surface = np.load(gp / 'surface_points.npy'); raw = np.load(gp / 'surface_points_source.npy')
        tf = json.loads((gp / 'coordinate_transform.json').read_text())
        norms = np.linalg.norm(surface[:, 3:], axis=1)
        audit.update({
            'mesh_tessellation_pass': (gp / 'mesh.obj').is_file(), 'surface_build_pass': (gp / 'surface_points.npy').is_file(),
            'surface_shape': list(surface.shape), 'surface_shape_8192x6_pass': surface.shape == (8192, 6),
            'surface_finite_pass': bool(np.isfinite(surface).all()), 'surface_normal_pass': bool(np.allclose(norms, 1, atol=1e-4)),
            'surface_transform_error': float(np.abs(raw * float(tf['scale']) + np.asarray(tf['translation']) - surface[:, :3]).max()),
        })
        audit['surface_transform_pass'] = audit['surface_transform_error'] <= 1e-5
        if not all(audit[k] for k in ('mesh_tessellation_pass', 'surface_build_pass', 'surface_shape_8192x6_pass', 'surface_finite_pass', 'surface_normal_pass', 'surface_transform_pass')): raise RuntimeError('SURFACE')
        dsl = (gp / 'cad_target.dsl').read_text(); audit['dsl_exists'] = True; audit['has_result'] = 'result =' in dsl
        if not audit['has_result']: raise RuntimeError('DSL_RESULT')
        audit.update(execute_gt(dsl, base))
        if not audit['step_reload']: raise RuntimeError('STEP')
        split, low = ('deepcad_train', 'deepcad') if ds == 'DeepCAD' else ('fusion360_train', 'fusion360')
        old_dir, old_pack = curves.cad_dir, curves.SPLITS[split]['track_a_pack']
        try:
            curves.cad_dir = lambda _split, _sid: curve_dir; curves.SPLITS[split]['track_a_pack'] = gp.parent
            curve_result = curves.build_one(split, sid, overwrite=False)
        finally:
            curves.cad_dir = old_dir; curves.SPLITS[split]['track_a_pack'] = old_pack
        if not curve_result.get('ok'): raise RuntimeError('GT_CURVE:' + str(curve_result.get('error')))
        samples = np.load(curve_dir / 'curve_samples.npz')
        n = int(samples['num_curves'][0]); sane = bool(n > 0 and np.isfinite(samples['curve_xyz_normalized']).all() and np.isfinite(samples['curve_tangent']).all())
        audit.update({'gt_curve_exists': True, 'curve_count': n, 'curve_sample_shape': list(samples['curve_xyz_normalized'].shape), 'c2_input_valid': sane, 'gt_curve_sanity': 'PASS' if sane else 'FAIL'})
        if not sane: raise RuntimeError('GT_CURVE_SANITY')
        old_root = exporter.PACK_ROOT[low]
        try:
            exporter.PACK_ROOT[low] = gp.parent
            exported = exporter.process_cad(low, sid, curve_dir, c2_model, DEVICE, True)
        finally:
            exporter.PACK_ROOT[low] = old_root
        if exported is None: raise RuntimeError('C2')
        c2dir = base / 'curve_tokens'; c2dir.mkdir(); np.save(c2dir / 'curve_tokens.npy', exported['tokens'])
        (c2dir / 'curve_tokens_meta.json').write_text(json.dumps(exported['meta'], indent=2) + '\n')
        tokens = exported['tokens']; audit.update({'c2_shape': list(tokens.shape), 'c2_valid': bool(tokens.ndim == 2 and tokens.shape[1] == 256 and np.isfinite(tokens).all()), 'curve_type_histogram': exported['meta'].get('type_counts', {})})
        if not audit['c2_valid']: raise RuntimeError('C2')
        audit['phase_a_pass'] = True
    except Exception as exc:
        audit['primary_reject_reason'] = str(exc).split(':', 1)[0]
        audit['clean_status'] = 'CLEAN_REJECT'
    (base / 'PER_CAD_AUDIT_PHASEA.json').write_text(json.dumps(audit, indent=2) + '\n')
    return audit


def build_raw(c2: np.ndarray) -> tuple[torch.Tensor, torch.Tensor]:
    if c2.ndim != 2 or c2.shape[1] != 256 or len(c2) > 128 or not np.isfinite(c2).all(): raise ValueError('C2_INPUT')
    raw = np.zeros((128, 256), np.float32); raw[:len(c2)] = c2
    mask = torch.zeros(128, dtype=torch.bool, device=DEVICE); mask[:len(c2)] = True
    return torch.tensor(raw, device=DEVICE).unsqueeze(0), mask


def audit_arm(model, state, tokenizer, arm: str, gp: Path, c2: np.ndarray | None, dataset: str, sid: str) -> dict:
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    surface, _ = load_surface_for_encoder(plugin, gp / 'surface_points.npy', dataset.lower(), sid)
    surface_t = torch.tensor(surface, device=DEVICE)
    target = tokenizer.encode((gp / 'cad_target.dsl').read_text() + '<|eot_id|>', add_special_tokens=False)
    p = prompt(tokenizer, arm); eos = tokenizer.convert_tokens_to_ids('<|eot_id|>')
    edge = None; summary_ok = True; summary_count = 0; active = 0
    if arm == 'm2':
        edge, mask = build_raw(c2); state['raw_mask'] = mask
        with torch.no_grad(): summary, smask = model.edge_proj(edge.to(dtype=next(model.edge_proj.parameters()).dtype), mask.unsqueeze(0))
        summary_count, active = int(summary.shape[1]), int(smask.sum())
        summary_ok = bool(summary.shape == (1, 8, model.config.hidden_size) and torch.isfinite(summary).all() and active == 8)
    else:
        state['raw_mask'] = torch.empty(0, dtype=torch.bool, device=DEVICE)
    with torch.no_grad(): S = int(model.forward_point_cloud(surface_t, DEVICE, torch.bfloat16, projector=model.point_proj).shape[1])
    total = len(p) + (S - 1) + (7 if arm == 'm2' else 0) + len(target)
    out = {'surface_token_count': S, 'prompt_tokens': len(p), 'dsl_tokens': len(target) - 1, 'eos_tokens': 1,
           'real_total': total, 'context_pass': total <= LIMIT, 'curve_summary_valid': summary_ok,
           'summary_token_count': summary_count, 'summary_active_count': active, 'splice_pass': False,
           'eos_supervised': False, 'result_complete': False}
    # Do not call an overflowing model forward: the context gate itself is the rejection evidence.
    if not out['context_pass']: return out
    ids = torch.tensor([p + target], device=DEVICE); labels = torch.tensor([[-100] * len(p) + target], device=DEVICE)
    actual = {}
    handle = model.model.register_forward_pre_hook(lambda mod, args, kwargs: actual.update({'length': int(kwargs['inputs_embeds'].shape[1]), 'attn': int(kwargs['attention_mask'].shape[1])}), with_kwargs=True)
    try:
        with torch.no_grad():
            z, spliced_labels = capture_splice_labels(lambda: model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels, point_clouds=surface_t.unsqueeze(0), edge_clouds=edge))
    finally:
        handle.remove()
    valid = spliced_labels[spliced_labels != -100] if spliced_labels is not None else torch.empty(0, dtype=torch.long)
    result_ids = tokenizer.encode('result =', add_special_tokens=False)
    out.update({'splice_pass': bool(torch.isfinite(z.loss)) and actual.get('length') == total and actual.get('attn') == total,
                'eos_supervised': bool(len(valid) and int(valid[-1]) == eos),
                'result_complete': any(valid[i:i+len(result_ids)].tolist() == result_ids for i in range(max(0, len(valid)-len(result_ids)+1))),
                'embedding_length': actual.get('length'), 'attention_length': actual.get('attn')})
    return out


def phase_b(phase_a_rows: list[dict]) -> list[dict]:
    rows = [r for r in phase_a_rows if r['phase_a_pass']]
    if not rows: return phase_a_rows
    core.heldout_geometry.install(); tokenizer = AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    for arm in ('b0', 'm2'):
        model = core.make_model(arm, DEVICE, 1.9414176940917969)
        if arm == 'm2': model.edge_proj.load_state_dict(torch.load(M2_CKPT / 'geometry_prefix_adapter.pt', map_location=DEVICE))
        model.eval(); state = {}; original = core.install_precomputed_second(model, arm, state)
        try:
            for row in rows:
                sid = row['cad_id'].split('__', 1)[1]; base = OUT / row['dataset'] / sid; gp = base / 'geometry_pack_v1' / sid
                c2 = np.load(base / 'curve_tokens/curve_tokens.npy') if arm == 'm2' else None
                row['B0' if arm == 'b0' else 'M2'] = audit_arm(model, state, tokenizer, arm, gp, c2, row['dataset'], sid)
        finally:
            core.module._splice_geometry = original; del model; gc.collect(); torch.cuda.empty_cache()
    for row in rows:
        b, m = row['B0'], row['M2']
        passes = [b['context_pass'], m['context_pass'], b['splice_pass'], m['splice_pass'], b['eos_supervised'], m['eos_supervised'], b['result_complete'], m['result_complete'], m['curve_summary_valid']]
        row['clean_status'] = 'CLEAN_PASS' if all(passes) else 'CLEAN_REJECT'
        if row['clean_status'] == 'CLEAN_REJECT':
            reasons = []
            if not b['context_pass'] or not m['context_pass']: reasons.append('CONTEXT_OVERFLOW')
            if not m['curve_summary_valid']: reasons.append('SUMMARY')
            if not b['splice_pass'] or not m['splice_pass']: reasons.append('SPLICE')
            if not b['eos_supervised'] or not m['eos_supervised']: reasons.append('EOS')
            if not b['result_complete'] or not m['result_complete']: reasons.append('RESULT')
            row['primary_reject_reason'] = reasons[0] if reasons else 'OTHER'; row['secondary_reject_reasons'] = reasons[1:]
        sid = row['cad_id'].split('__', 1)[1]; base = OUT / row['dataset'] / sid
        (base / 'PER_CAD_AUDIT.json').write_text(json.dumps(row, indent=2) + '\n')
    return phase_a_rows


def write_progress(rows: list[dict], complete: bool = False) -> None:
    clean = [r for r in rows if r.get('clean_status') == 'CLEAN_PASS']; rejected = [r for r in rows if r.get('clean_status') == 'CLEAN_REJECT']
    counts = {'attempted': len(rows), 'clean': len(clean), 'rejected': len(rejected), 'clean_yield': len(clean) / len(rows) if rows else 0}
    counts['by_dataset'] = {ds: {'attempted': sum(r['dataset'] == ds for r in rows), 'clean': sum(r['dataset'] == ds and r.get('clean_status') == 'CLEAN_PASS' for r in rows), 'rejected': sum(r['dataset'] == ds and r.get('clean_status') == 'CLEAN_REJECT' for r in rows)} for ds in ('DeepCAD', 'Fusion360')}
    reasons = Counter(r.get('primary_reject_reason') or 'OTHER' for r in rejected); counts['top_rejection_reasons'] = reasons.most_common(5)
    counts['complete'] = complete
    (OUT / 'audits/PROGRESS.json').write_text(json.dumps(counts, indent=2) + '\n')
    print(json.dumps(counts), flush=True)


def percentile(a: list[float]) -> dict:
    return {k: float(np.percentile(a, q)) for k, q in [('min', 0), ('median', 50), ('p90', 90), ('max', 100)]}


def freeze_final(rows: list[dict]) -> None:
    clean = [r for r in rows if r.get('clean_status') == 'CLEAN_PASS']
    # split has no model predictions or metrics and is frozen by independent deterministic hashes.
    for r in clean: r['_split_key'] = hashlib.sha256((SEED + '|split|' + r['cad_id']).encode()).hexdigest()
    by_ds = {ds: sorted([r for r in clean if r['dataset'] == ds], key=lambda r: r['_split_key']) for ds in ('DeepCAD', 'Fusion360')}
    total = len(clean); deep_fraction = sum(r['dataset'] == 'DeepCAD' for r in clean) / total
    dev_deep = round(50 * deep_fraction); test_deep = round(100 * deep_fraction)
    dev = by_ds['DeepCAD'][:dev_deep] + by_ds['Fusion360'][:50-dev_deep]
    remaining = {ds: [r for r in by_ds[ds] if r not in dev] for ds in by_ds}
    test = remaining['DeepCAD'][:test_deep] + remaining['Fusion360'][:100-test_deep]
    test_ids = {r['cad_id'] for r in test}; reserve = [r for r in clean if r['cad_id'] not in {x['cad_id'] for x in dev} | test_ids]
    for r in clean: r.pop('_split_key', None)
    distribution = {'clean_count': total, 'dataset': Counter(r['dataset'] for r in clean),
                    'dsl_tokens': percentile([r['M2']['dsl_tokens'] for r in clean]),
                    'surface_tokens': percentile([r['M2']['surface_token_count'] for r in clean]),
                    'curve_count': percentile([r['curve_count'] for r in clean]),
                    'm2_real_length': percentile([r['M2']['real_total'] for r in clean])}
    (OUT / 'audits/NEW_CLEAN_POOL_DISTRIBUTION.json').write_text(json.dumps(distribution, indent=2) + '\n')
    (OUT / 'audits/NEW_CLEAN_POOL_DISTRIBUTION.md').write_text('# New clean held-out pool distribution\n\n```json\n' + json.dumps(distribution, indent=2) + '\n```\n')
    train = json.loads(TRAIN_MANIFEST.read_text())['records']; train_ids = {r['cad_id'] for r in train}
    hashes = [r['source_step_sha256'] for r in clean]
    leakage = {'TRAIN_CLEAN_INTERSECTION': len(train_ids & {r['cad_id'] for r in clean}), 'DUPLICATE_CAD_IDS': len(clean)-len({r['cad_id'] for r in clean}), 'DUPLICATE_STEP_HASHES': len(hashes)-len(set(hashes)), 'PREBUILD_LEAKAGE_PROVENANCE': str(EVAL/'PREBUILD_LEAKAGE_AUDIT.json')}
    (OUT / 'audits/BULK_FINAL_LEAKAGE_AUDIT.json').write_text(json.dumps(leakage, indent=2) + '\n')
    def write(name: str, records: list[dict]):
        p = OUT / 'manifests' / f'{name}.jsonl'; p.write_text(''.join(json.dumps(r) + '\n' for r in records)); return {'path': str(p), 'sha256': sha256(p), 'count': len(records)}
    pool = write(f'NEW_CLEAN_POOL_{total}', clean); devm, testm, reservem = write('DECODE_DEV_50', dev), write('FINAL_TEST_100', test), write('HELDOUT_RESERVE', reserve)
    (OUT / 'manifests' / f'NEW_CLEAN_POOL_{total}_MANIFEST.json').write_text(json.dumps(pool, indent=2) + '\n')
    proposal = {'seed': SEED, 'method': 'deterministic hash within dataset, quotas follow clean-pool dataset ratio; no model result read', 'DEV50': devm, 'TEST100': testm, 'RESERVE': reservem,
                'TRAIN_DEV_INTERSECTION': len(train_ids & {r['cad_id'] for r in dev}), 'TRAIN_TEST_INTERSECTION': len(train_ids & {r['cad_id'] for r in test}), 'DEV_TEST_INTERSECTION': len({r['cad_id'] for r in dev} & {r['cad_id'] for r in test})}
    (OUT / 'manifests/SPLIT_PROPOSAL.json').write_text(json.dumps(proposal, indent=2) + '\n')
    # Explicit freeze names mandated by protocol.
    shutil.copy2(OUT/'manifests/DECODE_DEV_50.jsonl', OUT/'manifests/DECODE_DEV_50.json')
    shutil.copy2(OUT/'manifests/FINAL_TEST_100.jsonl', OUT/'manifests/FINAL_TEST_100.json')
    gate = 'INDEPENDENT_HELDOUT_POOL_READY' if total >= 180 and all(v == 0 for v in leakage.values() if isinstance(v, int)) else 'PARTIAL_HELDOUT_POOL_READY' if total >= 50 else 'HELDOUT_BULK_BUILD_INSUFFICIENT'
    (OUT / 'FINAL_SUMMARY.json').write_text(json.dumps({'CURRENT_GATE': gate, 'distribution': distribution, 'leakage': leakage, 'splits': proposal, 'TEST100_HAS_BEEN_EVALUATED': False, 'training_started': False, 'decode_started': False, 'dora_started': False}, indent=2) + '\n')


def main() -> None:
    if OUT.exists(): raise RuntimeError(f'output exists: {OUT}; never overwrite a run')
    if sha256(C2_CKPT) != C2_SHA: raise RuntimeError('C2 checkpoint hash mismatch')
    order = freeze_inputs(); all_rows: list[dict] = []
    old_cad_dir, old_packs, old_roots = curves.cad_dir, {k: v['track_a_pack'] for k, v in curves.SPLITS.items()}, dict(exporter.PACK_ROOT)
    try:
        index = 0
        while index < len(order) and sum(r.get('clean_status') == 'CLEAN_PASS' for r in all_rows) < TARGET:
            batch = order[index:index+CHUNK]; index += len(batch)
            c2_model, _ = exporter.load_backbone(C2_CKPT, DEVICE)
            phase = [phase_a(row, c2_model) for row in batch]
            del c2_model; gc.collect(); torch.cuda.empty_cache()
            phase = phase_b(phase); all_rows.extend(phase)
            (OUT / 'BULK_BUILD_PER_CAD.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in all_rows))
            write_progress(all_rows)
            if len(all_rows) >= 50 and sum(r.get('clean_status') == 'CLEAN_PASS' for r in all_rows) < 30:
                (OUT/'FINAL_SUMMARY.json').write_text(json.dumps({'CURRENT_GATE':'BULK_BUILD_ANOMALY_STOP','attempted':len(all_rows),'clean':sum(r.get('clean_status')=='CLEAN_PASS' for r in all_rows)},indent=2)+'\n')
                return
    finally:
        curves.cad_dir = old_cad_dir
        for k, v in old_packs.items(): curves.SPLITS[k]['track_a_pack'] = v
        exporter.PACK_ROOT.update(old_roots)
        gc.collect(); torch.cuda.empty_cache()
    write_progress(all_rows, complete=True)
    freeze_final(all_rows)


if __name__ == '__main__':
    main()
