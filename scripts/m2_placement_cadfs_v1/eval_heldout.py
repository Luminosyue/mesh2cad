#!/usr/bin/env python3
"""PHASE F: held-out25 paired B0 / old M2 / M2-Placement evaluation."""
from __future__ import annotations

import ast
import hashlib
import json
import math
import pathlib
import shutil
import sys
import tempfile
from collections import Counter, defaultdict

import numpy as np
import torch

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'))
sys.path.insert(0, str(ROOT / 'scripts/m2_placement_cadfs_v1'))
import cadfs_noisy100_overfit_v1 as old
import train_v3_smoke as core
import train_v3_1k_dev as util
import cad_execution_failure_audit as audit
from geometry_prefix_adapter import GeometryPrefixAdapter
sys.path.insert(0, str(ROOT / 'scripts/m2_placement_cadfs_v1'))
import train as m2p_train
PlacementMLP = m2p_train.PlacementMLP
install_placement = m2p_train.install_placement
load_c2_desc = m2p_train.load_c2_desc
TARGET_NORM = m2p_train.TARGET_NORM

EXP = ROOT / 'ours3/m2_placement_cadfs_v1'
HOLD_MAN = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/data/HOLDOUT_FINAL_MANIFEST.json'
HOLD_INDEX = EXP / 'data/HELDOUT25_INDEX.json'
HOLD_DATA = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/data'
B0_CKPT = ROOT / 'ours3/cadfs_noisy_overfit100_v1/runs_retrain_v1/B0_CADFS100_NOISY_RETRAIN_V1/checkpoint_epoch_20'
M2_CKPT = ROOT / 'ours3/cadfs_noisy_overfit100_v1/runs_retrain_v1/M2_ORACLE_CADFS100_NOISY_RETRAIN_V1/checkpoint_epoch_20'
B0_DEC = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/B0'
M2_DEC = ROOT / 'ours3/cadfs_noisy_heldout_pilot_v1/decode_e20_v1/M2'
EOS_IDS = (128001, 128008, 128009)
DIR_THR = 0.1
POS_THR = 0.001
CANONICAL_DIAG = 6.0
TIE_EPS = 1e-12


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, allow_nan=False) + '\n')


def load_rows():
    hold = {r['cad_id']: r for r in json.loads(HOLD_MAN.read_text())['records']}
    idx = json.loads(HOLD_INDEX.read_text())['records']
    rows = []
    for rec in idx:
        h = hold[rec['cad_id']]
        n = int(np.load(rec['c2_token_path'], mmap_mode='r').shape[0])
        audit_path = HOLD_DATA / rec['cad_id'] / 'HOLDOUT_BUILD_AUDIT.json'
        surface_tokens = int(json.loads(audit_path.read_text())['M2']['surface_token_count'])
        rows.append({
            'cad_id': rec['cad_id'],
            'surface_input': h['noisy_surface'],
            'target_dsl': h['canonical_dsl'],
            'm2_full_c2_tokens': rec['c2_token_path'],
            'placement_descriptor': rec['placement_descriptor'],
            'selected_m2_indices': list(range(n)),
            'k_valid': n,
            'surface_tokens': surface_tokens,
            'noisy_mesh': h['noisy_mesh'],
            'source_step': h['source_step'],
        })
    if len(rows) != 25:
        raise RuntimeError('heldout25 count mismatch')
    return rows


def geom_pair(gt_mesh, pred_mesh):
    import trimesh
    from scipy.spatial import cKDTree
    gt = trimesh.load(str(gt_mesh), force='mesh')
    pr = trimesh.load(str(pred_mesh), force='mesh')
    if isinstance(gt, trimesh.Scene):
        gt = gt.dump(concatenate=True)
    if isinstance(pr, trimesh.Scene):
        pr = pr.dump(concatenate=True)
    diag = float(np.linalg.norm(gt.bounds[1] - gt.bounds[0]))
    if diag <= 1e-12:
        return {'chamfer_rel': None, 'hausdorff95_rel': None, 'bbox_error_rel': None}
    np.random.seed(41)
    a, _ = trimesh.sample.sample_surface(gt, 3000)
    np.random.seed(43)
    b, _ = trimesh.sample.sample_surface(pr, 3000)
    da = cKDTree(b).query(a, k=1)[0]
    db = cKDTree(a).query(b, k=1)[0]
    d = np.concatenate((da, db)) / diag
    bbox = float(np.linalg.norm((pr.bounds - gt.bounds).ravel()) / diag)
    return {
        'chamfer_rel': float(d.mean()),
        'hausdorff95_rel': float(np.quantile(d, 0.95)),
        'bbox_error_rel': bbox,
    }


def execute_dsl(mod, text, work: pathlib.Path):
    rec = audit.staged_execute(text, work)
    step = work / 'pred.step'
    stl = work / 'pred.stl'
    if rec.get('step_write_success') and step.exists() and not stl.exists():
        try:
            import cadquery as cq
            cq.exporters.export(cq.importers.importStep(str(step)), str(stl))
        except Exception as exc:
            rec['stl_error'] = f'{type(exc).__name__}: {exc}'[-300:]
    rec['step_path'] = str(step) if step.exists() else None
    rec['stl_path'] = str(stl) if stl.exists() else None
    return rec


def walk_ops(node, out):
    if isinstance(node, dict) and 'op' in node:
        out.append(node)
        for a in node.get('args') or []:
            walk_ops(a, out)
        for v in (node.get('kwargs') or {}).values():
            walk_ops(v, out)
    elif isinstance(node, list):
        for x in node:
            walk_ops(x, out)


def dsl_ops(mod, text):
    prog = mod.parse_dsl(mod.extract_dsl_code(text))
    out = []
    for name, node in prog.assignments.items():
        walk_ops(node, out)
    return out


def angle_deg(a, b):
    ua = np.asarray(a, dtype=np.float64).reshape(3)
    ub = np.asarray(b, dtype=np.float64).reshape(3)
    na = np.linalg.norm(ua)
    nb = np.linalg.norm(ub)
    if na < 1e-12 or nb < 1e-12:
        return 180.0
    c = float(np.clip(np.dot(ua / na, ub / nb), -1.0, 1.0))
    return float(math.degrees(math.acos(c)))


def placement_error(mod, gt_text, pred_text):
    try:
        gt = dsl_ops(mod, gt_text)
        pred = dsl_ops(mod, pred_text)
    except Exception as exc:
        return {'ok': False, 'error': f'{type(exc).__name__}: {exc}'[-300:], 'has_global_placement_error': False}
    gmap = defaultdict(list)
    pmap = defaultdict(list)
    for o in gt:
        gmap[o['op']].append(o)
    for o in pred:
        pmap[o['op']].append(o)
    hits = []
    for op, glist in gmap.items():
        plist = pmap.get(op, [])
        for g, p in zip(glist, plist):
            gk = g.get('kwargs') or {}
            pk = p.get('kwargs') or {}
            if 'origin' in gk or 'origin' in pk:
                gv = np.asarray(gk.get('origin', (0, 0, 0)), dtype=np.float64)
                pv = np.asarray(pk.get('origin', (0, 0, 0)), dtype=np.float64)
                raw = float(np.linalg.norm(gv - pv))
                norm = raw / CANONICAL_DIAG
                hits.append({'op': op, 'parameter': 'origin', 'kind': 'position', 'normalized_error': norm, 'fail': norm > POS_THR})
            for name in ('axis', 'x_axis'):
                if name in gk or name in pk:
                    ang = angle_deg(gk.get(name, (0, 0, 1)), pk.get(name, (0, 0, 1)))
                    hits.append({'op': op, 'parameter': name, 'kind': 'direction', 'angle_error_deg': ang, 'fail': ang > DIR_THR})
    return {
        'ok': True,
        'n_compared': len(hits),
        'n_fail': sum(h['fail'] for h in hits),
        'has_global_placement_error': any(h['fail'] for h in hits),
        'hits': hits,
    }


def existing_pred(dec_root: pathlib.Path, cad_id: str) -> str:
    return (dec_root / 'predictions' / cad_id / 'pred_raw.txt').read_text()


def load_cadfs_surface(plugin, npy_path: str):
    """Match CADFS overfit100 train loader: no DeepCAD cache key, voxelize frozen noisy 8192."""
    from spatiallm_curve_token_v1 import heldout_geometry as hg
    surface = np.load(npy_path).astype(np.float64)
    if surface.ndim != 2 or surface.shape[1] != 6:
        raise RuntimeError(f'bad surface {npy_path} {surface.shape}')
    tensor, _ = hg._voxelize_surface_edge(plugin, surface, None)
    return tensor


def decode_placement(rows, ckpt: pathlib.Path, device, out: pathlib.Path):
    tok = core.AutoTokenizer.from_pretrained(ckpt, local_files_only=True, use_fast=False)
    model = core.module.SpatialLMLlamaForCausalLM.from_pretrained(ckpt, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    model.edge_proj = GeometryPrefixAdapter(256, model.config.hidden_size, target_norm=TARGET_NORM).to(device=device, dtype=torch.bfloat16)
    model.edge_proj.load_state_dict(torch.load(ckpt / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
    placement_mlp = PlacementMLP().to(device=device, dtype=torch.bfloat16)
    placement_mlp.load_state_dict(torch.load(ckpt / 'placement_mlp.pt', map_location=device, weights_only=True))
    model.config.separate_edge_tokens = True
    model.separate_edge_tokens = True
    for p in model.parameters():
        p.requires_grad_(False)
    for p in placement_mlp.parameters():
        p.requires_grad_(False)
    model.config.use_cache = True
    if hasattr(model, 'gradient_checkpointing_disable'):
        model.gradient_checkpointing_disable()
    model.eval()
    placement_mlp.eval()
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    state = {}
    original = install_placement(model, placement_mlp, state)
    preds = {}
    try:
        with torch.no_grad():
            for i, row in enumerate(rows, 1):
                ids, labels, _, _ = old.encode_full(tok, row, 'm2')
                prompt = int((labels[0] == -100).sum())
                pids = ids[:, :prompt].to(device)
                surface = load_cadfs_surface(plugin, row['surface_input'])
                surface = torch.tensor(surface, device=device).unsqueeze(0)
                c2, g, mask = load_c2_desc(row)
                state['raw_mask'] = mask
                state['placement'] = g
                gen = model.generate(
                    input_ids=pids,
                    attention_mask=torch.ones_like(pids),
                    point_clouds=surface,
                    edge_clouds=c2.to(device).unsqueeze(0),
                    max_new_tokens=4096,
                    do_sample=False,
                    use_cache=True,
                    eos_token_id=list(EOS_IDS),
                    pad_token_id=128001,
                )
                text = tok.decode(gen[0, pids.shape[1]:].cpu(), skip_special_tokens=True)
                preds[row['cad_id']] = text
                cad_dir = out / 'predictions' / row['cad_id']
                cad_dir.mkdir(parents=True, exist_ok=True)
                (cad_dir / 'pred_raw.txt').write_text(text)
                shutil.copy(row['target_dsl'], cad_dir / 'gt.dsl')
                print(f'[decode m2p] {i}/25 {row["cad_id"]} chars={len(text)}', flush=True)
    finally:
        core.module._splice_geometry = original
        del model
        torch.cuda.empty_cache()
    return preds


def wtl(old_v, new_v, lower_better=True):
    if old_v is None or new_v is None:
        return 'na'
    if abs(old_v - new_v) <= TIE_EPS:
        return 'tie'
    if lower_better:
        return 'win' if new_v < old_v else 'loss'
    return 'win' if new_v > old_v else 'loss'


def summarize(vals):
    xs = [v for v in vals if v is not None]
    return {'n': len(xs), 'mean': None if not xs else float(np.mean(xs)), 'median': None if not xs else float(np.median(xs))}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', type=pathlib.Path, required=True)
    ap.add_argument('--device', default='cuda:3')
    ap.add_argument('--output', type=pathlib.Path, default=EXP / 'eval/heldout25')
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    device = torch.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    preds = {
        'B0': {r['cad_id']: existing_pred(B0_DEC, r['cad_id']) for r in rows},
        'OLD_M2': {r['cad_id']: existing_pred(M2_DEC, r['cad_id']) for r in rows},
        'M2_PLACEMENT': decode_placement(rows, a.checkpoint, device, a.output / 'M2_PLACEMENT'),
    }
    mod = audit.dsl_module()
    case_rows = []
    work_root = a.output / 'tmp_exec'
    work_root.mkdir(exist_ok=True)
    for row in rows:
        cad_id = row['cad_id']
        gt_text = pathlib.Path(row['target_dsl']).read_text()
        gt_work = pathlib.Path(tempfile.mkdtemp(dir=work_root))
        gt_exec = execute_dsl(mod, gt_text, gt_work)
        item = {'cad_id': cad_id}
        for arm, pmap in preds.items():
            pred = pmap[cad_id]
            pw = pathlib.Path(tempfile.mkdtemp(dir=work_root))
            ex = execute_dsl(mod, pred, pw)
            exact = pred.strip() == gt_text.strip()
            opf1 = util.f1(util.ops(gt_text), util.ops(pred))
            place = placement_error(mod, gt_text, pred)
            geom_gt = {'chamfer_rel': None, 'hausdorff95_rel': None, 'bbox_error_rel': None}
            geom_src = dict(geom_gt)
            if gt_exec.get('stl_path') and ex.get('stl_path'):
                geom_gt = geom_pair(gt_exec['stl_path'], ex['stl_path'])
            if ex.get('stl_path') and pathlib.Path(row['noisy_mesh']).exists():
                geom_src = geom_pair(row['noisy_mesh'], ex['stl_path'])
            item[arm] = {
                'exact_match': exact,
                'op_f1': opf1,
                'dsl_parse_success': bool(ex.get('dsl_parse_success')),
                'step_reload_success': bool(ex.get('step_reload_success')),
                'gt_dsl_vs_pred': geom_gt,
                'source_vs_pred': geom_src,
                'global_placement_error': bool(place['has_global_placement_error']),
                'placement': {k: place[k] for k in place if k != 'hits'},
                'pred_text': pred,
            }
        case_rows.append(item)
        print(f'[eval] {cad_id} place B0/M2/P={item["B0"]["global_placement_error"]}/{item["OLD_M2"]["global_placement_error"]}/{item["M2_PLACEMENT"]["global_placement_error"]}', flush=True)

    def arm_summary(name):
        recs = [c[name] for c in case_rows]
        ch = [r['gt_dsl_vs_pred']['chamfer_rel'] for r in recs]
        hh = [r['gt_dsl_vs_pred']['hausdorff95_rel'] for r in recs]
        bb = [r['gt_dsl_vs_pred']['bbox_error_rel'] for r in recs]
        return {
            'Exact': sum(r['exact_match'] for r in recs),
            'OpF1': float(np.mean([r['op_f1'] for r in recs])),
            'STEP': sum(r['step_reload_success'] for r in recs),
            'Chamfer_rel': summarize(ch),
            'Hausdorff95': summarize(hh),
            'BBox_error': summarize(bb),
            'Global_placement_error_cases': sum(r['global_placement_error'] for r in recs),
            'source_vs_pred_chamfer': summarize([r['source_vs_pred']['chamfer_rel'] for r in recs]),
        }

    counts = Counter()
    fixed = new = unchanged = 0
    for c in case_rows:
        old_p = c['OLD_M2']['global_placement_error']
        new_p = c['M2_PLACEMENT']['global_placement_error']
        if old_p and not new_p:
            fixed += 1
            c['placement_delta'] = 'fixed'
        elif (not old_p) and new_p:
            new += 1
            c['placement_delta'] = 'new'
        else:
            unchanged += 1
            c['placement_delta'] = 'unchanged'
        for metric, key in [('Chamfer', 'chamfer_rel'), ('Hausdorff', 'hausdorff95_rel'), ('BBox', 'bbox_error_rel')]:
            counts[f'{metric}_{wtl(c["OLD_M2"]["gt_dsl_vs_pred"][key], c["M2_PLACEMENT"]["gt_dsl_vs_pred"][key])}'] += 1

    def wtl_str(metric):
        return f"{counts[f'{metric}_win']}/{counts[f'{metric}_tie']}/{counts[f'{metric}_loss']}"

    b0s, m2s, ps = arm_summary('B0'), arm_summary('OLD_M2'), arm_summary('M2_PLACEMENT')
    # Reproduce frozen diagnostic counts as a sanity check on B0/M2 tags.
    sanity = {'B0_place': b0s['Global_placement_error_cases'], 'OLD_M2_place': m2s['Global_placement_error_cases'], 'frozen_B0': 19, 'frozen_M2': 21}

    promising = (
        ps['Global_placement_error_cases'] < m2s['Global_placement_error_cases']
        and counts['Chamfer_loss'] <= counts['Chamfer_win']
        and (ps['Chamfer_rel']['mean'] is not None and m2s['Chamfer_rel']['mean'] is not None)
        and ps['Chamfer_rel']['mean'] <= m2s['Chamfer_rel']['mean'] + 1e-6
        and ps['STEP'] >= m2s['STEP']
        and ps['OpF1'] >= m2s['OpF1'] - 1e-6
    )
    if promising:
        final = 'M2_PLACEMENT_CADFS_V1_PROMISING'
    elif ps['Global_placement_error_cases'] < m2s['Global_placement_error_cases'] and counts['Chamfer_loss'] > counts['Chamfer_win']:
        final = 'SIGNAL_PRESENT_BUT_RESIDUAL_TOO_AGGRESSIVE'
    elif abs(ps['Global_placement_error_cases'] - m2s['Global_placement_error_cases']) == 0 and counts['Chamfer_tie'] >= 20:
        final = 'DESCRIPTOR_NOT_EFFECTIVELY_USED'
    else:
        final = 'M2_PLACEMENT_CADFS_V1_FAIL'

    report = {
        'EXPERIMENT': 'M2_PLACEMENT_CADFS_V1',
        'n': 25,
        'geometry_reference': 'gt_dsl_vs_pred (CAD reconstruction); source_vs_pred also stored',
        'B0': b0s,
        'OLD_M2': m2s,
        'M2_PLACEMENT': ps,
        'PLACEMENT_ERROR_FIXED': fixed,
        'PLACEMENT_ERROR_NEW': new,
        'PLACEMENT_ERROR_UNCHANGED': unchanged,
        'Chamfer_win_tie_loss': wtl_str('Chamfer'),
        'Hausdorff_win_tie_loss': wtl_str('Hausdorff'),
        'BBox_win_tie_loss': wtl_str('BBox'),
        'placement_tag_sanity': sanity,
        'FINAL_GATE': final,
        'NOTE': 'CADFS frozen train100+heldout25 pilot only; not a large-scale claim.',
        'OLD_M2_CHECKPOINT': str(M2_CKPT),
        'M2_PLACEMENT_CHECKPOINT': str(a.checkpoint),
        'B0_CHECKPOINT': str(B0_CKPT),
        'decode_reused': {'B0': str(B0_DEC), 'OLD_M2': str(M2_DEC), 'M2_PLACEMENT': 'new greedy 4096'},
    }
    dump(a.output / 'HELDOUT25_SUMMARY.json', report)
    dump(a.output / 'HELDOUT25_CASEWISE_COMPARISON.json', case_rows)
    lines = ['cad_id,old_m2_chamfer,m2p_chamfer,chamfer_wtl,old_m2_h95,m2p_h95,h95_wtl,old_m2_bbox,m2p_bbox,bbox_wtl,old_m2_place,m2p_place,place_delta,old_m2_opf1,m2p_opf1']
    for c in case_rows:
        o, n = c['OLD_M2'], c['M2_PLACEMENT']
        lines.append(','.join(map(str, [
            c['cad_id'],
            o['gt_dsl_vs_pred']['chamfer_rel'], n['gt_dsl_vs_pred']['chamfer_rel'],
            wtl(o['gt_dsl_vs_pred']['chamfer_rel'], n['gt_dsl_vs_pred']['chamfer_rel']),
            o['gt_dsl_vs_pred']['hausdorff95_rel'], n['gt_dsl_vs_pred']['hausdorff95_rel'],
            wtl(o['gt_dsl_vs_pred']['hausdorff95_rel'], n['gt_dsl_vs_pred']['hausdorff95_rel']),
            o['gt_dsl_vs_pred']['bbox_error_rel'], n['gt_dsl_vs_pred']['bbox_error_rel'],
            wtl(o['gt_dsl_vs_pred']['bbox_error_rel'], n['gt_dsl_vs_pred']['bbox_error_rel']),
            int(o['global_placement_error']), int(n['global_placement_error']), c['placement_delta'],
            o['op_f1'], n['op_f1'],
        ])))
    (a.output / 'HELDOUT25_CASEWISE_COMPARISON.csv').write_text('\n'.join(lines) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
