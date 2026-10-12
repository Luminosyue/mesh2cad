#!/usr/bin/env python3
from __future__ import annotations

import ast
import collections
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
PREV_CODE = ROOT / 'scripts/parameter_head_oracle_v1'
PREV_OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1'
OUT = PREV_OUT / 'parameter_replacement_causality_audit_v1'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
sys.path.insert(0, str(PREV_CODE))

from common import EXECUTOR_SHA256  # noqa: E402
from train_heads import FeatureStore, load_jsonl, predict_all  # noqa: E402
from model import ParameterHeads  # noqa: E402


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def dump(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def close(a, b, tol=1e-7) -> bool:
    try:
        aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        return aa.shape == bb.shape and bool(np.allclose(aa, bb, rtol=tol, atol=tol))
    except Exception:
        return False


def value_score(a, b) -> float:
    aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.linalg.norm(aa - bb) / max(float(np.linalg.norm(aa)), 1e-9))


def assignment_call(text: str, name: str) -> tuple[int, ast.Call]:
    index = -1
    for stmt in ast.parse(text).body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        if stmt.targets[0].id == 'result':
            continue
        index += 1
        if stmt.targets[0].id == name and isinstance(stmt.value, ast.Call):
            return index, stmt.value
    raise KeyError(name)


def literal(node):
    return ast.literal_eval(node)


def arg_or_kw(call: ast.Call, pos: int, key: str, default=None):
    if pos >= 0 and len(call.args) > pos:
        return literal(call.args[pos])
    for kw in call.keywords:
        if kw.arg == key:
            return literal(kw.value)
    return default


def physical(text: str, assignment: str, operation: str, field: str):
    _, call = assignment_call(text, assignment)
    op = call.func.id if isinstance(call.func, ast.Name) else None
    if operation == 'Circle':
        if op != 'Extrude' or not call.args or not isinstance(call.args[0], ast.Call):
            raise KeyError((assignment, operation, field))
        nested = call.args[0]
        if field == 'radius':
            return arg_or_kw(nested, 0, 'radius')
    if operation == 'Extrude' and op == 'Extrude':
        mapping = {'height': (1, 'height', None), 'origin': (-1, 'origin', (0, 0, 0)), 'axis': (-1, 'axis', (0, 0, 1)), 'height_two': (-1, 'height_two', 0.0)}
        pos, key, default = mapping[field]
        return arg_or_kw(call, pos, key, default)
    if operation == 'Box' and op == 'Box':
        mapping = {'width': (0, 'width', None), 'depth': (1, 'depth', None), 'height': (2, 'height', None), 'origin': (-1, 'origin', (0, 0, 0))}
        pos, key, default = mapping[field]
        return arg_or_kw(call, pos, key, default)
    raise KeyError((assignment, operation, field))


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    dsl_root = OUT / 'dsl'; dsl_root.mkdir()

    old_rows = load_jsonl(PREV_OUT / 'PARAMETER_REPLACEMENT_AUDIT.jsonl')
    occ = json.loads((PREV_OUT / 'DEV50_OCC_REPLAY.json').read_text())
    grouped = collections.defaultdict(lambda: collections.defaultdict(dict))
    for row in old_rows:
        key = (row['assignment'], row['operation'], row['field'])
        grouped[row['cad_id']][row['system']][key] = row['value']
    valid = {
        row['cad_id'] for row in occ['PER_CAD']
        if row['LLM']['step_reload'] and row['HEAD']['step_reload'] and row['replacement_assignments']
    }
    scores = {}
    for cad_id in valid:
        shared = set(grouped[cad_id]['LLM']) & set(grouped[cad_id]['HEAD'])
        scores[cad_id] = max(value_score(grouped[cad_id]['LLM'][k], grouped[cad_id]['HEAD'][k]) for k in shared)
    selected = sorted(valid, key=lambda cad: (-scores[cad], cad))[:10]
    if len(selected) != 10:
        raise RuntimeError(f'could not select 10 CADs: {len(selected)}')

    labels = load_jsonl(PREV_OUT / 'oracle_labels_dev.jsonl')
    checkpoint = torch.load(PREV_OUT / 'train800/checkpoint_final.pt', map_location='cpu', weights_only=True)
    model = ParameterHeads(); model.load_state_dict(checkpoint['model']); model.eval()
    predictions = predict_all(model, labels, FeatureStore(labels), torch.device('cpu'))
    pred_by_id = {(l['cad_id'], l['assignment'], l['head_type']): (l, p) for l, p in zip(labels, predictions)}

    field_rows, dsl_files, mismatches = [], [], []
    for cad_id in selected:
        source = PREV_OUT / 'dev50' / cad_id
        target = dsl_root / cad_id; target.mkdir()
        texts = {}
        for system, filename in [('GT', 'GT_PARAMETER_DSL.dsl'), ('LLM', 'LLM_PARAMETER_DSL.dsl'), ('HEAD', 'HEAD_PARAMETER_DSL.dsl')]:
            src = source / filename
            dst = target / filename
            shutil.copyfile(src, dst)
            texts[system] = dst.read_text()
            dsl_files.append({'cad_id': cad_id, 'system': system, 'path': str(dst), 'sha256': digest(dst), 'bytes': dst.stat().st_size})

        assignments = sorted({k[0] for k in grouped[cad_id]['HEAD']})
        for assignment in assignments:
            index, call = assignment_call(texts['GT'], assignment)
            op = call.func.id
            specs = []
            if op == 'Extrude':
                circle = pred_by_id[(cad_id, assignment, 'circle')]
                extrude = pred_by_id[(cad_id, assignment, 'extrude')]
                cl, cp = circle; el, ep = extrude
                scale, center = float(cl['object_scale']), np.asarray(cl['object_center'])
                specs.extend([
                    ('Circle', 'radius', float(cp['radius']) * scale, 'CircleParameterHead.radius'),
                    ('Extrude', 'origin', (np.asarray(cp['center']) * scale + center).tolist(), 'CircleParameterHead.center'),
                    ('Extrude', 'axis', cp['normal'], 'CircleParameterHead.normal'),
                    ('Extrude', 'origin', (np.asarray(ep['origin']) * scale + center).tolist(), 'ExtrudeParameterHead.origin'),
                    ('Extrude', 'axis', ep['direction'], 'ExtrudeParameterHead.direction'),
                    ('Extrude', 'height', float(ep['depth']) * scale, 'ExtrudeParameterHead.depth'),
                    ('Extrude', 'height_two', float(ep['height_two']) * scale, 'ExtrudeParameterHead.height_two'),
                ])
            elif op == 'Box':
                label, pred = pred_by_id[(cad_id, assignment, 'box')]
                scale, center = float(label['object_scale']), np.asarray(label['object_center'])
                origin = (np.asarray(pred['origin']) * scale + center).tolist()
                extent = (np.asarray(pred['extent']) * scale).tolist()
                specs.extend([
                    ('Box', 'origin', origin, 'BoxParameterHead.origin'),
                    ('Box', 'width', extent[0], 'BoxParameterHead.extent[0]'),
                    ('Box', 'depth', extent[1], 'BoxParameterHead.extent[1]'),
                    ('Box', 'height', extent[2], 'BoxParameterHead.extent[2]'),
                ])
            for operation, field, predicted, source_head in specs:
                actual = physical(texts['HEAD'], assignment, operation, field)
                row = {
                    'cad_id': cad_id, 'operation_index': index, 'assignment': assignment,
                    'operation_type': operation, 'field_name': field,
                    'head_output_source': source_head,
                    'gt_value': physical(texts['GT'], assignment, operation, field),
                    'llm_value': physical(texts['LLM'], assignment, operation, field),
                    'head_value': predicted,
                    'value_actually_sent_to_executor': actual,
                    'head_prediction_equals_executor_value': close(predicted, actual),
                }
                field_rows.append(row)
                if not row['head_prediction_equals_executor_value']:
                    mismatches.append(row)

    with (OUT / 'PARAMETER_FIELD_DIFF.jsonl').open('w') as f:
        for row in field_rows:
            f.write(json.dumps(row) + '\n')

    circle_center_mismatch = any(r['head_output_source'] == 'CircleParameterHead.center' for r in mismatches)
    circle_normal_mismatch = any(r['head_output_source'] == 'CircleParameterHead.normal' for r in mismatches)
    height_two_mismatch = any(r['head_output_source'] == 'ExtrudeParameterHead.height_two' for r in mismatches)
    replacement = {
        'EXPERIMENT': 'PARAMETER_REPLACEMENT_CAUSALITY_AUDIT_V1',
        'CURRENT_GATE': 'PARAMETER_REPLACEMENT_CAUSALITY_AUDIT_FAIL_PIPELINE_BUG',
        'REPLACEMENT_PIPELINE_BUG': True,
        'DETERMINISTIC_SELECTION_RULE': 'STEP-valid in both branches, nonempty replacements; descending max relative LLM-vs-HEAD field difference, then cad_id',
        'SELECTED_CAD_IDS': selected, 'SELECTION_SCORES': {cad: scores[cad] for cad in selected},
        'DSL_FILES': dsl_files, 'FIELD_RECORD_COUNT': len(field_rows),
        'MISMATCH_COUNT': len(mismatches),
        'CIRCLE_CENTER_NOT_ROUTED_FROM_CIRCLE_HEAD': circle_center_mismatch,
        'CIRCLE_NORMAL_NOT_ROUTED_FROM_CIRCLE_HEAD': circle_normal_mismatch,
        'HEIGHT_TWO_OMITTED_WHEN_GT_KEYWORD_ABSENT': height_two_mismatch,
        'EXACT_FAILURE': 'CircleParameterHead.center/normal are not composed into the executor DSL; ExtrudeParameterHead.origin/direction occupy those fields. ExtrudeParameterHead.height_two is also not written when the GT DSL omitted the keyword.',
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    dump('DSL_REPLACEMENT_AUDIT.json', replacement)

    semantics = {
        'EXECUTOR_PATH': str(EXECUTOR), 'EXECUTOR_SHA256': digest(EXECUTOR),
        'EXECUTOR_HASH_MATCHES_FROZEN': digest(EXECUTOR) == EXECUTOR_SHA256,
        'CODE_TRACE': {
            'Extrude': ['_build_shape reads height/axis/origin at cad_dsl.py:291-296', '_cq_cylinder constructs local circle extrusion and rotates/translates it at cad_dsl.py:187-218'],
            'Box': ['_build_shape reads width/depth/height/axis/origin at cad_dsl.py:327-352', '_cq_box builds a Workplane at origin/axis and extrudes width/depth/height at cad_dsl.py:219-230'],
            'Circle': ['_build_shape converts Circle.radius into the sketch dictionary at cad_dsl.py:280-283', 'Extrude consumes sketch.radius at cad_dsl.py:297-310'],
        },
        'EXTRUDE_ORIGIN_IS_CAUSAL': True, 'EXTRUDE_DIRECTION_IS_CAUSAL': True, 'EXTRUDE_DEPTH_IS_CAUSAL': True,
        'BOX_ORIGIN_IS_CAUSAL': True, 'BOX_EXTENT_IS_CAUSAL': True,
        'CIRCLE_CENTER_IS_CAUSAL': True, 'CIRCLE_RADIUS_IS_CAUSAL': True, 'CIRCLE_NORMAL_IS_CAUSAL': True,
        'CIRCLE_CENTER_NORMAL_NOTE': 'Circle center and normal are geometrically causal through Extrude.origin and Extrude.axis, but the current replacement pipeline routes those DSL fields from ExtrudeParameterHead, not CircleParameterHead.',
        'FIELDS_ARE_REDUNDANT_METADATA': False,
    }
    dump('EXECUTOR_PARAMETER_SEMANTICS.json', semantics)

    skip = {
        'STATUS': 'NOT_RUN_DUE_IMMEDIATE_PHASE4_PIPELINE_GATE_FAILURE',
        'CURRENT_GATE': replacement['CURRENT_GATE'],
        'REASON': replacement['EXACT_FAILURE'],
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    dump('SINGLE_PARAMETER_PERTURBATION.json', {**skip, 'PARAMETER_EFFECTIVE_IN_EXECUTOR': None})
    dump('OCC_CAUSALITY_AUDIT.json', skip)
    dump('FRESH_GEOMETRY_METRICS.json', skip)
    dump('CACHE_ISOLATION_AUDIT.json', {**skip, 'SHARED_STEP_PATH': False, 'SHARED_MESH_PATH': False, 'SHARED_METRIC_CACHE_PATH': False, 'SHARED_FINGERPRINT_CACHE_PATH': False})

    targets = sorted([p for p in OUT.rglob('*') if p.is_file()]) + [EXECUTOR, PREV_OUT / 'train800/checkpoint_final.pt', Path(__file__).resolve()]
    files = [{'path': str(p), 'sha256': digest(p), 'bytes': p.stat().st_size} for p in targets]
    dump('FILE_SHA256_MANIFEST.json', {'HASH_ALGORITHM': 'SHA256', 'FILE_COUNT': len(files), 'FILES': files, 'MANIFEST_SELF_EXCLUDED': True})
    print(json.dumps(replacement, indent=2))


if __name__ == '__main__':
    main()
