from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
DATA_ROOT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
TRAIN_MANIFEST = DATA_ROOT / 'v3_1k_train.json'
DEV_MANIFEST = DATA_ROOT / 'v3_decode_dev_50.json'
CHECKPOINT = Path('/var/tmp/cuiyuehan_mesh2cad/m2_spatial_anchor_q_ablation_formal_train800_v1/A3_ANCHOR_Q32/checkpoint_epoch_07')
CHECKPOINT_SHA256 = '9dcb175c2667a6403604939d7d0de6321c26f2e6dc86a7a310e06179529c1704'
C2_SHA256 = '553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
EXECUTOR_SHA256 = '53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'
OUTPUT_ROOT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1'
CODE_ROOT = ROOT / 'scripts/parameter_head_oracle_v1'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if data.get('official_test_read') is not False:
        raise RuntimeError(f'Forbidden split flag is not false: {path}')
    return data['records']


def literal(node: ast.AST) -> Any:
    return ast.literal_eval(node)


def parse_assignments(text: str) -> list[dict]:
    tree = ast.parse(text)
    out = []
    for order, stmt in enumerate(tree.body):
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        if not isinstance(stmt.value, ast.Call) or not isinstance(stmt.value.func, ast.Name):
            continue
        name = stmt.targets[0].id
        if name == 'result':
            continue
        call = stmt.value
        kwargs = {kw.arg: literal(kw.value) for kw in call.keywords if kw.arg}
        args = []
        for value in call.args:
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
                nested_kwargs = {kw.arg: literal(kw.value) for kw in value.keywords if kw.arg}
                nested_args = [literal(v) for v in value.args]
                args.append({'op': value.func.id, 'args': nested_args, 'kwargs': nested_kwargs})
            else:
                args.append(literal(value))
        out.append({'name': name, 'order': order, 'op': call.func.id, 'args': args, 'kwargs': kwargs})
    return out


def vec3(value: Any, default=(0.0, 0.0, 0.0)) -> np.ndarray:
    if value is None:
        value = default
    arr = np.asarray(value, dtype=np.float64)
    if arr.shape != (3,) or not np.all(np.isfinite(arr)):
        raise ValueError(f'invalid vec3: {value!r}')
    return arr


def unit(value: Any) -> np.ndarray:
    arr = vec3(value)
    norm = float(np.linalg.norm(arr))
    if norm <= 1e-12:
        raise ValueError('zero direction')
    return arr / norm


def operation_parameters(op: dict) -> dict | None:
    args, kw = op['args'], op['kwargs']
    if op['op'] == 'Extrude':
        sketch = args[0] if args else kw.get('sketch')
        if not isinstance(sketch, dict) or sketch.get('op') not in {'Circle', 'Sketch'}:
            return None
        sk_args, sk_kw = sketch.get('args') or [], sketch.get('kwargs') or {}
        radius = float(sk_args[0] if sk_args else sk_kw['radius'])
        height = float(args[1] if len(args) > 1 else kw['height'])
        return {
            'origin': vec3(kw.get('origin', (0, 0, 0))),
            'direction': unit(kw.get('axis', (0, 0, 1))),
            'depth': height,
            'height_two': float(kw.get('height_two', 0.0)),
            'symmetric': bool(kw.get('symmetric', False)),
            'circle_radius': radius,
        }
    if op['op'] == 'Box':
        if args:
            width = float(args[0])
            depth = float(args[1] if len(args) > 1 else kw.get('depth', 1.0))
            height = float(args[2] if len(args) > 2 else kw.get('height', 1.0))
            axis = args[3] if len(args) > 3 else kw.get('axis', (0, 0, 1))
            origin = args[4] if len(args) > 4 else kw.get('origin', (0, 0, 0))
            x_axis = args[5] if len(args) > 5 else kw.get('x_axis')
        else:
            width, depth, height = float(kw['width']), float(kw['depth']), float(kw['height'])
            axis, origin, x_axis = kw.get('axis', (0, 0, 1)), kw.get('origin', (0, 0, 0)), kw.get('x_axis')
        axis_v = unit(axis)
        if x_axis is None:
            ref = np.array([0.0, 0.0, 1.0])
            if abs(float(ref @ axis_v)) > 0.95:
                ref = np.array([1.0, 0.0, 0.0])
            x_v = unit(np.cross(ref, axis_v))
        else:
            x_v = unit(x_axis)
        y_v = unit(np.cross(axis_v, x_v))
        return {
            'origin': vec3(origin), 'axis': axis_v, 'x_axis': x_v, 'y_axis': y_v,
            'width': width, 'depth': depth, 'height': height,
            'height_two': float(kw.get('height_two', 0.0)),
            'symmetric': bool(kw.get('symmetric', False)),
        }
    return None


def object_frame(row: dict) -> tuple[np.ndarray, float, np.ndarray, np.ndarray]:
    vertices = []
    for line in (Path(row['target_dsl']).parent / 'mesh.obj').read_text().splitlines():
        if line.startswith('v '):
            vertices.append([float(v) for v in line.split()[1:4]])
    points = np.asarray(vertices, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 3 or not np.all(np.isfinite(points)):
        raise ValueError('invalid mesh vertices')
    lo, hi = points.min(0), points.max(0)
    scale = float(np.max(hi - lo))
    if not math.isfinite(scale) or scale <= 1e-8:
        raise ValueError('non-invertible object scale')
    return (lo + hi) / 2, scale, lo, hi


def token_contract(row: dict) -> tuple[np.ndarray, np.ndarray, dict[int, int], list[dict]]:
    tokens = np.load(row['m2_full_c2_tokens']).astype(np.float32)
    meta = json.loads(Path(row['m2_full_c2_tokens']).with_name('curve_tokens_meta.json').read_text())
    if len(tokens) != len(meta['curves']):
        raise ValueError('token/meta length mismatch')
    chosen = [int(i) for i in row['selected_m2_indices']]
    if len(chosen) != int(row['k_valid']):
        raise ValueError('selected_m2/k_valid mismatch')
    selected_tokens = tokens[chosen]
    # Exact frozen BEST_ARM anchor recipe. It indexes curve_xyz by token index;
    # preserving this behavior is required for representation identity.
    curves = np.load(row['m2_full_curves'], allow_pickle=True)
    xyz = curves['curve_xyz'][np.asarray(chosen, dtype=np.int64)]
    center, scale, _, _ = object_frame(row)
    anchors = np.concatenate(
        [(xyz.mean(1) - center) / scale, (xyz.max(1) - xyz.min(1)) / scale], axis=1
    ).astype(np.float32)
    edge_to_selected = {int(meta['curves'][token_i]['edge_id']): selected_i for selected_i, token_i in enumerate(chosen)}
    return selected_tokens, anchors, edge_to_selected, meta['curves']


def normalized_curves(row: dict) -> dict[int, dict]:
    data = json.loads(Path(row['m2_full_curves']).with_name('curves.json').read_text())
    return {int(curve['edge_id']): curve for curve in data['curves']}


def circle_edge_match(row: dict, params: dict, tolerance: float = 2e-5) -> tuple[int | None, str]:
    _, _, edge_to_selected, _ = token_contract(row)
    curves = normalized_curves(row)
    target_center = params['origin']
    target_radius = float(params['circle_radius'])
    target_normal = params['direction']
    matches = []
    for edge_id, selected_i in edge_to_selected.items():
        curve = curves.get(edge_id)
        if not curve or curve.get('curve_type') != 'CIRCLE':
            continue
        p = curve.get('normalized_parameters') or {}
        center = vec3(p.get('center'))
        radius = float(p.get('radius'))
        normal = unit(p.get('normal'))
        if (
            np.linalg.norm(center - target_center) <= tolerance
            and abs(radius - target_radius) <= tolerance
            and abs(float(normal @ target_normal)) >= 1.0 - tolerance
        ):
            matches.append(selected_i)
    if len(matches) == 1:
        return matches[0], 'STRICT_ANALYTIC_IDENTITY_UNIQUE'
    return None, 'NO_EXACT_TOKEN_IDENTITY' if not matches else 'AMBIGUOUS_EXACT_TOKEN_IDENTITY'


def _segment_key(a: np.ndarray, b: np.ndarray, decimals: int = 5) -> tuple:
    aa = tuple(np.round(a, decimals).tolist())
    bb = tuple(np.round(b, decimals).tolist())
    return tuple(sorted((aa, bb)))


def box_expected_segments(params: dict) -> set[tuple]:
    origin, axis, x, y = params['origin'], params['axis'], params['x_axis'], params['y_axis']
    w, d, h = params['width'], params['depth'], params['height']
    offsets = [0.0, h]
    if params['symmetric']:
        offsets.append(-h)
    elif abs(params['height_two']) > 1e-12:
        offsets.append(-params['height_two'])
    z0, z1 = min(offsets), max(offsets)
    layers = []
    for z in (z0, z1):
        layers.append([
            origin + sx * w * 0.5 * x + sy * d * 0.5 * y + z * axis
            for sx, sy in ((-1, -1), (-1, 1), (1, 1), (1, -1))
        ])
    segments = set()
    for layer in layers:
        for i in range(4):
            segments.add(_segment_key(layer[i], layer[(i + 1) % 4]))
    for i in range(4):
        segments.add(_segment_key(layers[0][i], layers[1][i]))
    return segments


def box_edge_match(row: dict, params: dict) -> tuple[list[int] | None, str]:
    _, _, edge_to_selected, _ = token_contract(row)
    curves = normalized_curves(row)
    signature_to_indices: dict[tuple, list[int]] = {}
    for edge_id, selected_i in edge_to_selected.items():
        curve = curves.get(edge_id)
        if not curve or curve.get('curve_type') != 'LINE':
            continue
        normalized = curve.get('normalized') or {}
        key = _segment_key(vec3(normalized.get('start_point')), vec3(normalized.get('end_point')))
        signature_to_indices.setdefault(key, []).append(selected_i)
    expected = box_expected_segments(params)
    matched = []
    for key in expected:
        indices = signature_to_indices.get(key, [])
        if len(indices) != 1:
            return None, 'NO_COMPLETE_EXACT_BOX_EDGE_IDENTITY' if not indices else 'AMBIGUOUS_BOX_EDGE_IDENTITY'
        matched.append(indices[0])
    if len(set(matched)) != 12:
        return None, 'NON_UNIQUE_BOX_EDGE_SET'
    return sorted(matched), 'STRICT_ANALYTIC_12_EDGE_IDENTITY'


def finite_array(value: Any) -> bool:
    if isinstance(value, dict):
        return all(finite_array(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_array(item) for item in value)
    try:
        return bool(math.isfinite(float(value)))
    except Exception:
        return False
