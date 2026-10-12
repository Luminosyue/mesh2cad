#!/usr/bin/env python3
"""Read-only staged CAD executor audit for frozen V3 decode-dev candidates."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import pathlib
import re
import sys
import tempfile
from collections import Counter

import torch

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
from geometry_prefix_adapter import GeometryPrefixAdapter

DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
EOS_IDS = (128001, 128008, 128009)


def dsl_module():
    spec = importlib.util.spec_from_file_location('audit_cad_dsl', ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py')
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Dataclasses resolve postponed annotations through sys.modules during
    # module execution; register this isolated executor before loading it.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def taxonomy(exc: Exception) -> str:
    text = f'{type(exc).__name__}: {exc}'.lower()
    if 'unknown shape ref' in text or 'undefined' in text or 'not defined' in text:
        return 'UNDEFINED_REFERENCE'
    if 'polygon' in text:
        return 'INVALID_POLYGON'
    if 'extrude' in text:
        return 'INVALID_EXTRUSION'
    if 'boolean' in text or 'cut' in text or 'union' in text or 'intersect' in text:
        return 'BOOLEAN_FAILURE'
    if any(x in text for x in ('radius', 'height', 'width', 'depth', 'zero', 'negative', 'nan', 'inf')):
        return 'INVALID_PARAMETER'
    return 'UNKNOWN_EXCEPTION'


def staged_execute(text: str, work_root: pathlib.Path) -> dict:
    rec = {
        'dsl_parse_success': False, 'dsl_execute_success': False,
        'occ_shape_non_null': False, 'brep_valid': False,
        'occ_shape_valid': False, 'step_write_success': False,
        'step_reload_success': False, 'failure_reason': None,
        'error': None, 'shape_type': None,
    }
    mod = dsl_module()
    try:
        code = mod.extract_dsl_code(text)
        ast.parse(code)
        program = mod.parse_dsl(code)
        rec['dsl_parse_success'] = True
    except Exception as exc:
        rec['failure_reason'] = 'PARSE_ERROR'
        rec['error'] = f'{type(exc).__name__}: {exc}'[-600:]
        return rec
    try:
        shapes = {}
        for name, node in program.assignments.items():
            if name != 'result':
                shapes[name] = mod._build_shape(node, shapes) if isinstance(node, dict) and 'op' in node else node
        node = program.assignments['result']
        if isinstance(node, str):
            result = shapes[node]
        elif isinstance(node, dict) and 'op' in node:
            result = mod._build_shape(node, shapes)
        else:
            result = node
        rec['dsl_execute_success'] = True
    except Exception as exc:
        rec['failure_reason'] = taxonomy(exc)
        rec['error'] = f'{type(exc).__name__}: {exc}'[-600:]
        return rec
    try:
        shape = result.val().wrapped if hasattr(result, 'val') else result
        rec['shape_type'] = int(shape.ShapeType())
        if shape.IsNull():
            rec['failure_reason'] = 'NULL_SHAPE'
            return rec
        rec['occ_shape_non_null'] = True
        from OCP.BRepCheck import BRepCheck_Analyzer
        if not BRepCheck_Analyzer(shape).IsValid():
            rec['failure_reason'] = 'BREP_INVALID'
            return rec
        rec['brep_valid'] = True
        rec['occ_shape_valid'] = True
    except Exception as exc:
        rec['failure_reason'] = 'NULL_SHAPE'
        rec['error'] = f'{type(exc).__name__}: {exc}'[-600:]
        return rec
    try:
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
        from OCP.IFSelect import IFSelect_RetDone
        path = work_root / 'pred.step'
        writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
        if writer.Write(str(path)) != IFSelect_RetDone or not path.exists() or path.stat().st_size == 0:
            rec['failure_reason'] = 'STEP_WRITE_FAILURE'
            return rec
        rec['step_write_success'] = True
    except Exception as exc:
        rec['failure_reason'] = 'STEP_WRITE_FAILURE'
        rec['error'] = f'{type(exc).__name__}: {exc}'[-600:]
        return rec
    try:
        import cadquery as cq
        cq.importers.importStep(str(path))
        rec['step_reload_success'] = True
    except Exception as exc:
        rec['failure_reason'] = 'STEP_RELOAD_FAILURE'
        rec['error'] = f'{type(exc).__name__}: {exc}'[-600:]
        return rec
    rec['failure_reason'] = 'SUCCESS'
    return rec


def load_rows():
    return json.loads((DATA / 'v3_decode_dev_50.json').read_text())['records']


def target_text(value: str) -> str:
    """Saved audit records retain DSL text; manifests retain a filesystem path."""
    if '\n' not in value and len(value) < 1024:
        path = pathlib.Path(value)
        if path.exists():
            return path.read_text()
    return value


def generate_rows(arm: str, checkpoint: pathlib.Path, device: torch.device, target_norm: float):
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tok = core.AutoTokenizer.from_pretrained(checkpoint, local_files_only=True, use_fast=False)
    model = core.module.SpatialLMLlamaForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    if arm == 'b1':
        model.edge_proj = GeometryPrefixAdapter(model.config.hidden_size, model.config.hidden_size, target_norm=target_norm).to(device=device, dtype=torch.bfloat16)
    elif arm == 'm2':
        model.edge_proj = GeometryPrefixAdapter(256, model.config.hidden_size, target_norm=target_norm).to(device=device, dtype=torch.bfloat16)
    if arm != 'b0':
        model.edge_proj.load_state_dict(torch.load(checkpoint / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
        model.config.separate_edge_tokens = True; model.separate_edge_tokens = True
    else:
        model.edge_proj = None
    model.eval(); state = {}; original = core.install_precomputed_second(model, arm, state)
    try:
        for row in load_rows():
            ids, labels, _, _ = core.encode(tok, row, arm)
            prompt = int((labels[0] == -100).sum())
            surface, _ = plugin._load_cad_separate_edge(row['surface_input'])
            surface = torch.tensor(surface, device=device).unsqueeze(0)
            second, mask = core.second_input(row, arm); state['raw_mask'] = mask
            edge = None if second is None else second.to(device).unsqueeze(0)
            with torch.no_grad():
                gen = model.generate(input_ids=ids[:, :prompt].to(device), attention_mask=torch.ones((1, prompt), dtype=torch.long, device=device), point_clouds=surface, edge_clouds=edge, max_new_tokens=4096, do_sample=False, use_cache=True, eos_token_id=list(EOS_IDS), pad_token_id=128001)
            new = gen[0, prompt:].cpu()
            yield row, tok.decode(new, skip_special_tokens=True), {'generated_token_length': int(new.numel()), 'eos_emitted': bool(new.numel() and int(new[-1]) in EOS_IDS)}
    finally:
        core.module._splice_geometry = original


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['gt', 'pred', 'replay', 'saved'], required=True)
    ap.add_argument('--arm', choices=['b0', 'b1', 'm2'])
    ap.add_argument('--checkpoint')
    ap.add_argument('--output', required=True)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--target-norm', type=float, default=1.9414176940917969)
    ap.add_argument('--replay-file')
    ap.add_argument('--saved-file')
    ap.add_argument('--limit', type=int, default=20)
    a = ap.parse_args(); out = pathlib.Path(a.output); out.mkdir(parents=True, exist_ok=False)
    if a.mode == 'pred' and (not a.arm or not a.checkpoint): ap.error('pred requires arm and checkpoint')
    if a.mode == 'replay' and not a.replay_file: ap.error('replay requires --replay-file')
    if a.mode == 'saved' and not a.saved_file: ap.error('saved requires --saved-file')
    if a.mode == 'gt':
        iterable = ((r, pathlib.Path(r['target_dsl']).read_text(), {}) for r in load_rows())
    elif a.mode == 'replay':
        replay = [json.loads(x) for x in pathlib.Path(a.replay_file).read_text().splitlines()][:a.limit]
        iterable = (({'cad_id': r['cad_id'], 'target_dsl': r['target_dsl']}, r['prediction'], {}) for r in replay)
    elif a.mode == 'saved':
        saved = [json.loads(x) for x in pathlib.Path(a.saved_file).read_text().splitlines()]
        iterable = (({'cad_id': r['cad_id'], 'target_dsl': r['target_dsl']}, r['generated_dsl'], {}) for r in saved)
    else:
        iterable = generate_rows(a.arm, pathlib.Path(a.checkpoint), torch.device(a.device), a.target_norm)
    per = []; work = out / 'tmp'; work.mkdir()
    for i, (row, text, gen) in enumerate(iterable, 1):
        with tempfile.TemporaryDirectory(dir=work) as d:
            audit = staged_execute(text, pathlib.Path(d))
        target = target_text(row['target_dsl'])
        rec = {'cad_id': row['cad_id'], 'target_dsl': target, 'generated_dsl': text, **gen, **audit}
        per.append(rec)
        if i % 10 == 0: print(f'{a.mode} {a.arm or "gt"} {i}/50', flush=True)
    keys = ('dsl_parse_success', 'dsl_execute_success', 'occ_shape_non_null', 'brep_valid', 'occ_shape_valid', 'step_write_success', 'step_reload_success')
    summary = {'mode': a.mode, 'arm': a.arm, 'checkpoint': a.checkpoint, 'n': len(per), **{k: sum(bool(x[k]) for x in per) for k in keys}, 'failure_taxonomy': dict(sorted(Counter(x['failure_reason'] for x in per).items()))}
    (out / 'per_cad.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in per))
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__':
    main()
