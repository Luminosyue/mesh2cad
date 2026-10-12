#!/usr/bin/env python3
from __future__ import annotations

import ast
import collections
import hashlib
import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OLD_CODE = ROOT / 'scripts/parameter_head_oracle_v1'
CODE_ROOT = ROOT / 'scripts/parameter_composition_routing_v2'
OLD_OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1'
AUDIT_V1 = OLD_OUT / 'parameter_replacement_causality_audit_v1'
OUT = OLD_OUT / 'parameter_composition_routing_v2'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
HEAD_CHECKPOINT = OLD_OUT / 'train800/checkpoint_final.pt'
HEAD_SHA256 = '2ac24248215aea415be16e3fdca7ca344e24ae25bc2d285809dc6b13f4e6c12e'
SERIALIZATION_TOLERANCE = 1e-7
sys.path.insert(0, str(CODE_ROOT))
sys.path.insert(0, str(OLD_CODE))

from typed_composition import TypedProgram, structure_signature  # noqa: E402
from common import DEV_MANIFEST, EXECUTOR_SHA256, load_manifest  # noqa: E402
from train_heads import FeatureStore, load_jsonl, predict_all  # noqa: E402
from model import ParameterHeads  # noqa: E402
from evaluate_dev50 import parameter_errors  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write_json(name: str, value) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def same(a, b, tol=SERIALIZATION_TOLERANCE) -> bool:
    try:
        aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        return aa.shape == bb.shape and bool(np.allclose(aa, bb, atol=tol, rtol=tol))
    except Exception:
        return False


def summarize(values: list[float]) -> dict:
    a = np.asarray(values, dtype=float)
    return {'n': len(a), 'mean': float(a.mean()) if len(a) else None, 'median': float(np.median(a)) if len(a) else None,
            'P25': float(np.percentile(a, 25)) if len(a) else None, 'P75': float(np.percentile(a, 75)) if len(a) else None,
            'P90': float(np.percentile(a, 90)) if len(a) else None}


def load_executor():
    if sha256(EXECUTOR) != EXECUTOR_SHA256:
        raise RuntimeError('frozen executor hash mismatch')
    spec = importlib.util.spec_from_file_location('routing_v2_executor', EXECUTOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def shape_properties(shape_obj) -> dict:
    q = lambda value: round(float(value), 9)
    bbox = shape_obj.BoundingBox()
    center = [q((bbox.xmin + bbox.xmax) / 2), q((bbox.ymin + bbox.ymax) / 2), q((bbox.zmin + bbox.zmax) / 2)]
    extent = [q(bbox.xmax - bbox.xmin), q(bbox.ymax - bbox.ymin), q(bbox.zmax - bbox.zmin)]
    vertices = sorted([[q(x) for x in v.Center().toTuple()] for v in shape_obj.Vertices()])
    edge_lengths = sorted(q(edge.Length()) for edge in shape_obj.Edges())
    face_areas = sorted(q(face.Area()) for face in shape_obj.Faces())
    payload = {
        'solid_count': len(shape_obj.Solids()), 'face_count': len(shape_obj.Faces()),
        'edge_count': len(shape_obj.Edges()), 'vertex_count': len(shape_obj.Vertices()),
        'bbox_center': center, 'bbox_extent': extent,
        'volume': q(shape_obj.Volume()), 'surface_area': q(shape_obj.Area()),
        'vertices': vertices, 'edge_lengths': edge_lengths, 'face_areas': face_areas,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False)
    result = {k: v for k, v in payload.items() if k not in {'vertices', 'edge_lengths', 'face_areas'}}
    result['geometry_fingerprint'] = hashlib.sha256(canonical.encode()).hexdigest()
    result['fingerprint_contract'] = 'SHA256(sorted topology counts, bbox, volume, area, vertices, edge lengths, face areas; values quantized to 1e-9)'
    return result


def fresh_execute(text: str, mesh_path: Path, run_dir: Path, executor) -> dict:
    run_dir.mkdir(parents=True, exist_ok=False)
    dsl_path = run_dir / 'input.dsl'; dsl_path.write_text(text)
    record = {
        'dsl_path': str(dsl_path), 'dsl_sha256': sha256(dsl_path),
        'step_path': str(run_dir / 'result.step'), 'mesh_path': str(run_dir / 'result.stl'),
        'metric_cache_path': None, 'fingerprint_cache_path': None,
        'parse': False, 'execute': False, 'IsNull': None, 'brep_valid': False, 'step_reload': False,
        'failure': None, 'shape': None, 'metrics': None,
    }
    try:
        clean = executor.extract_dsl_code(text)
        ast.parse(clean); program = executor.parse_dsl(clean); record['parse'] = True
        shapes = {}
        for name, node in program.assignments.items():
            if name != 'result':
                shapes[name] = executor._build_shape(node, shapes) if isinstance(node, dict) and 'op' in node else node
        result_node = program.assignments['result']
        result = shapes[result_node] if isinstance(result_node, str) else executor._build_shape(result_node, shapes)
        record['execute'] = True
        shape_obj = result.val() if hasattr(result, 'val') else result
        wrapped = shape_obj.wrapped
        record['IsNull'] = bool(wrapped.IsNull())
        if record['IsNull']:
            record['failure'] = 'NULL_SHAPE'; return record
        from OCP.BRepCheck import BRepCheck_Analyzer
        record['brep_valid'] = bool(BRepCheck_Analyzer(wrapped).IsValid())
        if not record['brep_valid']:
            record['failure'] = 'BREP_INVALID'; return record
        record['shape'] = shape_properties(shape_obj)
        import cadquery as cq
        cq.exporters.export(shape_obj, record['step_path'])
        loaded = cq.importers.importStep(record['step_path']); record['step_reload'] = True
        cq.exporters.export(loaded, record['mesh_path'])
        record['step_sha256'] = sha256(Path(record['step_path']))
        record['mesh_sha256'] = sha256(Path(record['mesh_path']))
        import trimesh
        from scipy.spatial import cKDTree
        gt = trimesh.load(str(mesh_path), force='mesh'); pred = trimesh.load(record['mesh_path'], force='mesh')
        if isinstance(gt, trimesh.Scene): gt = gt.dump(concatenate=True)
        if isinstance(pred, trimesh.Scene): pred = pred.dump(concatenate=True)
        ge, pe = gt.bounds[1] - gt.bounds[0], pred.bounds[1] - pred.bounds[0]
        gc, pc = gt.bounds.mean(0), pred.bounds.mean(0)
        diagonal = max(float(np.linalg.norm(ge)), 1e-12)
        a, _ = trimesh.sample.sample_surface(gt, 3000, seed=42)
        b, _ = trimesh.sample.sample_surface(pred, 3000, seed=43)
        da = cKDTree(b).query(a, k=1)[0]; db = cKDTree(a).query(b, k=1)[0]
        record['metrics'] = {
            'Chamfer': float((da.mean() + db.mean()) / 2 / diagonal),
            'H95': float(np.percentile(np.concatenate([da, db]), 95) / diagonal),
            'bbox_center': float(np.linalg.norm(pc - gc) / diagonal),
            'bbox_extent': float(np.linalg.norm(pe - ge) / diagonal),
        }
        record['failure'] = 'SUCCESS'
    except Exception as exc:
        record['failure'] = f'{type(exc).__name__}: {exc}'[-1000:]
    return record


def build_head_values(labels: list[dict], predictions: list[dict]):
    values = collections.defaultdict(lambda: collections.defaultdict(dict))
    raw = collections.defaultdict(lambda: collections.defaultdict(dict))
    for label, pred in zip(labels, predictions):
        cad, assignment, kind = label['cad_id'], label['assignment'], label['head_type']
        scale, center = float(label['object_scale']), np.asarray(label['object_center'], dtype=float)
        if kind == 'circle':
            values[cad][assignment].update({
                'circle.radius': float(pred['radius']) * scale,
                'circle.center': (np.asarray(pred['center']) * scale + center).tolist(),
                'circle.normal': pred['normal'],
            })
            raw[cad][assignment].update({'circle.radius': pred['radius'], 'circle.center': pred['center'], 'circle.normal': pred['normal']})
        elif kind == 'extrude':
            values[cad][assignment].update({
                'extrude.origin': (np.asarray(pred['origin']) * scale + center).tolist(),
                'extrude.direction': pred['direction'], 'extrude.depth': float(pred['depth']) * scale,
                'extrude.height_two': float(pred['height_two']) * scale,
            })
            raw[cad][assignment].update({'extrude.origin': pred['origin'], 'extrude.direction': pred['direction'], 'extrude.depth': pred['depth'], 'extrude.height_two': pred['height_two']})
        else:
            extent = (np.asarray(pred['extent']) * scale).tolist()
            values[cad][assignment].update({'box.origin': (np.asarray(pred['origin']) * scale + center).tolist(), 'box.extent.width': extent[0], 'box.extent.depth': extent[1], 'box.extent.height': extent[2]})
            raw[cad][assignment].update({'box.origin': pred['origin'], 'box.extent.width': pred['extent'][0], 'box.extent.depth': pred['extent'][1], 'box.extent.height': pred['extent'][2]})
    return values, raw


def compose_system(gt_text: str, assignments: list[str], values_by_assignment: dict, raw_by_assignment: dict | None = None):
    program = TypedProgram(gt_text)
    records = []
    for assignment in assignments:
        if assignment not in values_by_assignment:
            continue
        for row in program.bind(assignment, values_by_assignment[assignment]):
            row.update({'assignment': assignment, 'operation_index': program.operations[assignment].index})
            if raw_by_assignment is not None:
                row['head_raw_pred'] = raw_by_assignment[assignment][row['parameter']]
            records.append(row)
    text = program.serialize()
    reparsed = TypedProgram(text)
    for row in records:
        if row['parameter_applied']:
            value = reparsed.operations[row['assignment']].get(row['parameter'])
            row['serialized_value'] = value; row['reparsed_effective_value'] = value
            row['applied_parameter_match'] = same(row['head_world_value'], value)
        else:
            row['ast_value'] = None; row['serialized_value'] = None; row['reparsed_effective_value'] = None
            row['applied_parameter_match'] = None
    return text, records


def llm_values_from_old_dsl(text: str, assignments: list[str]) -> dict:
    program = TypedProgram(text); result = {}
    for assignment in assignments:
        op = program.operations[assignment]
        result[assignment] = {slot['parameter']: op.get(slot['parameter']) for slot in op.active_mask() if slot['active']}
    return result


def aggregate_occ(rows: list[dict], system: str, common_ids: set[str] | None = None) -> dict:
    chosen = [r[system] for r in rows if common_ids is None or r['cad_id'] in common_ids]
    metrics = lambda key: summarize([r['metrics'][key] for r in chosen if r['metrics'] is not None])
    return {
        'CAD_COUNT': len(chosen), 'PARSE': sum(r['parse'] for r in chosen), 'EXECUTE': sum(r['execute'] for r in chosen),
        'BREP_VALID': sum(r['brep_valid'] for r in chosen), 'STEP_RELOAD': sum(r['step_reload'] for r in chosen),
        'Chamfer': metrics('Chamfer'), 'H95': metrics('H95'), 'BBox_center': metrics('bbox_center'), 'BBox_extent': metrics('bbox_extent'),
    }


def rotate_direction(direction, degrees: float):
    v = np.asarray(direction, dtype=float); v /= np.linalg.norm(v)
    ref = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    axis = np.cross(v, ref); axis /= np.linalg.norm(axis)
    theta = math.radians(degrees)
    rotated = v * math.cos(theta) + np.cross(axis, v) * math.sin(theta) + axis * np.dot(axis, v) * (1 - math.cos(theta))
    return rotated.tolist()


def main() -> None:
    if sha256(HEAD_CHECKPOINT) != HEAD_SHA256:
        raise RuntimeError('Parameter Head checkpoint hash mismatch')
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    frozen10 = json.loads((AUDIT_V1 / 'DSL_REPLACEMENT_AUDIT.json').read_text())['SELECTED_CAD_IDS']
    records = load_manifest(DEV_MANIFEST)
    record_by_cad = {r['cad_id']: r for r in records}
    if len(record_by_cad) != 50: raise RuntimeError('dev manifest not 50')
    old_occ = json.loads((OLD_OUT / 'DEV50_OCC_REPLAY.json').read_text())
    assignments_by_cad = {r['cad_id']: r['replacement_assignments'] for r in old_occ['PER_CAD']}
    labels = load_jsonl(OLD_OUT / 'oracle_labels_dev.jsonl')
    checkpoint = torch.load(HEAD_CHECKPOINT, map_location='cpu', weights_only=True)
    model = ParameterHeads(); model.load_state_dict(checkpoint['model']); model.eval()
    predictions = predict_all(model, labels, FeatureStore(labels), torch.device('cpu'))
    head_values, head_raw = build_head_values(labels, predictions)

    ownership = {
        'VERSION': 'PARAMETER_COMPOSITION_ROUTING_V2', 'TYPED_AST_REQUIRED': True,
        'SERIALIZATION_TOLERANCE': SERIALIZATION_TOLERANCE,
        'PARAMETER_HEAD_CHECKPOINT': str(HEAD_CHECKPOINT), 'PARAMETER_HEAD_CHECKPOINT_SHA256': HEAD_SHA256,
        'PARAMETER_HEAD_ORACLE_V1_SCIENTIFIC_RESULT_VALID': False,
        'INVALIDATION_REASON': 'PARAMETER_COMPOSITION_ROUTING_BUG', 'OLD_HEAD_GEOMETRY_RESULT_INVALID': True,
        'OWNERSHIP': {
            'circle.radius': 'CircleParameterHead.radius -> Circle.radius',
            'circle.center': 'CircleParameterHead.center -> Extrude.origin -> _cq_cylinder translate',
            'circle.normal': 'CircleParameterHead.normal -> Extrude.axis -> _cq_cylinder rotation/extrusion axis',
            'extrude.origin': 'ExtrudeParameterHead.origin inactive: placement_v3 has one origin, owned by profile center',
            'extrude.direction': 'ExtrudeParameterHead.direction inactive: placement_v3 has one axis shared with profile normal; signed depth selects motion sense',
            'extrude.depth': 'ExtrudeParameterHead.depth -> Extrude.height -> _extrude_with_extent',
            'extrude.height_two': 'Applied only for explicit, nonzero, nonsymmetric two-sided GT slot',
            'box.origin': 'BoxParameterHead.origin -> Box.origin -> _cq_on_plane',
            'box.extent': 'BoxParameterHead.extent -> Box width/depth/height -> rect/extrude',
        },
        'EXTRUDE_AXIS_SEMANTICS': 'Single placement_v3 axis simultaneously defines sketch/profile normal and actual extrusion axis; no independent direction slot exists.',
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    write_json('PARAMETER_OWNERSHIP_CONTRACT_V2.json', ownership)

    routing_root = OUT / 'routing10'; routing_root.mkdir()
    mask_rows, assertions, routing_dsl = [], [], []
    for cad_id in frozen10:
        gt_text = Path(record_by_cad[cad_id]['target_dsl']).read_text()
        assignments = assignments_by_cad[cad_id]
        old_llm_text = (OLD_OUT / 'dev50' / cad_id / 'LLM_PARAMETER_DSL.dsl').read_text()
        llm_values = llm_values_from_old_dsl(old_llm_text, assignments)
        llm_text, _ = compose_system(gt_text, assignments, llm_values)
        head_text, rows = compose_system(gt_text, assignments, head_values[cad_id], head_raw[cad_id])
        cad_dir = routing_root / cad_id; cad_dir.mkdir()
        for system, text in [('GT', gt_text), ('LLM', llm_text), ('HEAD_V2', head_text)]:
            path = cad_dir / f'{system}_PARAMETER_DSL.dsl'; path.write_text(text)
            routing_dsl.append({'cad_id': cad_id, 'system': system, 'path': str(path), 'sha256': sha256(path)})
        for assignment in assignments:
            op = TypedProgram(gt_text).operations[assignment]
            for slot in op.active_mask():
                mask_rows.append({'cad_id': cad_id, 'operation_index': op.index, 'assignment': assignment, **slot,
                                  'HEAD_VALUE_MAY_EXIST': slot['parameter'] in head_values[cad_id][assignment],
                                  'PARAMETER_APPLIED': slot['active'], 'PARAMETER_SKIPPED_REASON': slot.get('skipped_reason')})
        for row in rows:
            row['cad_id'] = cad_id
            row.update({'PARAMETER_APPLIED': row.pop('parameter_applied'),
                        'PARAMETER_SKIPPED_REASON': row.pop('skipped_reason', None),
                        'HEAD_RAW_PRED': row.pop('head_raw_pred'), 'HEAD_WORLD_VALUE': row.pop('head_world_value'),
                        'AST_VALUE': row.pop('ast_value'), 'SERIALIZED_VALUE': row.pop('serialized_value'),
                        'REPARSED_EFFECTIVE_VALUE': row.pop('reparsed_effective_value'),
                        'APPLIED_PARAMETER_MATCH': row.pop('applied_parameter_match')})
            assertions.append(row)
    with (OUT / 'ACTIVE_PARAMETER_MASK_AUDIT.jsonl').open('w') as f:
        for r in mask_rows: f.write(json.dumps(r) + '\n')
    with (OUT / 'ROUNDTRIP_PARAMETER_ASSERTIONS.jsonl').open('w') as f:
        for r in assertions: f.write(json.dumps(r) + '\n')
    active = [r for r in assertions if r['PARAMETER_APPLIED']]
    mismatches = [r for r in active if not r['APPLIED_PARAMETER_MATCH']]
    relevant = lambda prefix: [r for r in active if r['parameter'].startswith(prefix)]
    routing_report = {
        'FROZEN_CAD_IDS': frozen10, 'ACTIVE_REPLACEMENTS': len(active), 'ROUTING_MISMATCH': len(mismatches),
        'CIRCLE_CENTER_ROUTING_PASS': all(r['APPLIED_PARAMETER_MATCH'] for r in active if r['parameter'] == 'circle.center'),
        'CIRCLE_NORMAL_ROUTING_PASS': all(r['APPLIED_PARAMETER_MATCH'] for r in active if r['parameter'] == 'circle.normal'),
        'CIRCLE_RADIUS_ROUTING_PASS': all(r['APPLIED_PARAMETER_MATCH'] for r in active if r['parameter'] == 'circle.radius'),
        'EXTRUDE_DIRECTION_ROUTING_PASS': all(r['PARAMETER_SKIPPED_REASON'] == 'COALESCED_WITH_PROFILE_NORMAL_SINGLE_AXIS_EXECUTOR' for r in assertions if r['parameter'] == 'extrude.direction'),
        'EXTRUDE_DEPTH_ROUTING_PASS': all(r['APPLIED_PARAMETER_MATCH'] for r in active if r['parameter'] == 'extrude.depth'),
        'BOX_ORIGIN_ROUTING_PASS': all(r['APPLIED_PARAMETER_MATCH'] for r in active if r['parameter'] == 'box.origin'),
        'BOX_EXTENT_ROUTING_PASS': all(r['APPLIED_PARAMETER_MATCH'] for r in active if r['parameter'].startswith('box.extent')),
        'SERIALIZATION_TOLERANCE': SERIALIZATION_TOLERANCE, 'DSL_FILES': routing_dsl,
        'PARAMETER_HEAD_CHECKPOINT_SHA256': sha256(HEAD_CHECKPOINT),
    }
    routing_pass = routing_report['ACTIVE_REPLACEMENTS'] > 0 and routing_report['ROUTING_MISMATCH'] == 0 and all(v is True for k, v in routing_report.items() if k.endswith('_ROUTING_PASS'))
    routing_report['ROUTING_PASS'] = routing_pass
    write_json('PARAMETER_ROUTING_10CAD.json', routing_report)
    if not routing_pass:
        finalize('PARAMETER_COMPOSITION_ROUTING_V2_FAIL', routing_report, None, None); return

    executor = load_executor()
    perturb_root = OUT / 'fresh_perturbation'; perturb_root.mkdir()
    extrude_cads = [cad for cad in frozen10 if any(TypedProgram(Path(record_by_cad[cad]['target_dsl']).read_text()).operations[a].op_type == 'Extrude' for a in assignments_by_cad[cad])]
    box_cads = [cad for cad in frozen10 if any(TypedProgram(Path(record_by_cad[cad]['target_dsl']).read_text()).operations[a].op_type == 'Box' for a in assignments_by_cad[cad])]
    experiments = [
        ('circle_radius', extrude_cads[0], 'circle.radius'), ('circle_center', extrude_cads[1], 'circle.center'),
        ('extrude_depth', extrude_cads[2], 'extrude.depth'), ('extrude_direction', extrude_cads[3], 'circle.normal'),
        ('box_extent', box_cads[0], 'box.extent.width'),
    ]
    perturb_rows = []
    for label_name, cad_id, parameter in experiments:
        gt_text = Path(record_by_cad[cad_id]['target_dsl']).read_text(); assignments = assignments_by_cad[cad_id]
        original_text, _ = compose_system(gt_text, assignments, head_values[cad_id], head_raw[cad_id])
        original_program = TypedProgram(original_text)
        assignment = next(a for a in assignments if parameter in {s['parameter'] for s in original_program.operations[a].active_mask() if s['active']})
        original_value = original_program.operations[assignment].get(parameter)
        if parameter == 'circle.normal':
            minus_value, plus_value = rotate_direction(original_value, -20.0), rotate_direction(original_value, 20.0)
            perturb_contract = 'unit direction rotated by fixed -20/+20 degrees'
        else:
            arr = np.asarray(original_value, dtype=float)
            minus_value = (arr * 0.8).tolist() if arr.ndim else float(arr * 0.8)
            plus_value = (arr * 1.2).tolist() if arr.ndim else float(arr * 1.2)
            perturb_contract = 'effective parameter multiplied by fixed 0.8/1.2'
        texts = {'ORIGINAL': original_text}
        for variant, value in [('PARAM_MINUS_20PCT', minus_value), ('PARAM_PLUS_20PCT', plus_value)]:
            program = TypedProgram(original_text); program.operations[assignment].set(parameter, value); texts[variant] = program.serialize()
        mesh_path = Path(record_by_cad[cad_id]['target_dsl']).parent / 'mesh.obj'
        results = {variant: fresh_execute(text, mesh_path, perturb_root / cad_id / label_name / variant, executor) for variant, text in texts.items()}
        fingerprints = [results[v]['shape']['geometry_fingerprint'] if results[v]['shape'] else None for v in texts]
        changed = fingerprints[0] is not None and any(fp is not None and fp != fingerprints[0] for fp in fingerprints[1:])
        perturb_rows.append({'cad_id': cad_id, 'assignment': assignment, 'experiment': label_name, 'effective_parameter': parameter,
                             'perturbation_contract': perturb_contract, 'original_value': original_value, 'minus_value': minus_value, 'plus_value': plus_value,
                             'RESULTS': results, 'PARAMETER_EFFECTIVE_IN_EXECUTOR': changed})
    perturb_pass = len(perturb_rows) >= 5 and all(r['PARAMETER_EFFECTIVE_IN_EXECUTOR'] for r in perturb_rows)
    perturb_report = {'PERTURBATION_PASS': perturb_pass, 'EXPERIMENT_COUNT': len(perturb_rows), 'EXPERIMENTS': perturb_rows,
                      'FRESH_EXECUTION': True, 'METRIC_CACHE_USED': False}
    write_json('SINGLE_PARAMETER_CAUSALITY_V2.json', perturb_report)
    if not perturb_pass:
        finalize('PARAMETER_COMPOSITION_ROUTING_V2_FAIL_CAUSALITY', routing_report, perturb_report, None); return

    fresh_root = OUT / 'fresh_dev50'; fresh_root.mkdir()
    occ_rows, common_parameter_labels, llm_parameter_values, head_parameter_values = [], [], [], []
    label_by_cad = collections.defaultdict(list)
    for label in labels: label_by_cad[label['cad_id']].append(label)
    for cad_id in sorted(record_by_cad):
        gt_path = Path(record_by_cad[cad_id]['target_dsl']); gt_text = gt_path.read_text(); assignments = assignments_by_cad.get(cad_id, [])
        old_llm_text = (OLD_OUT / 'dev50' / cad_id / 'LLM_PARAMETER_DSL.dsl').read_text()
        llm_values = llm_values_from_old_dsl(old_llm_text, assignments) if assignments else {}
        llm_text, _ = compose_system(gt_text, assignments, llm_values)
        head_text, _ = compose_system(gt_text, assignments, head_values.get(cad_id, {}), head_raw.get(cad_id, {}))
        mesh_path = gt_path.parent / 'mesh.obj'; cad_root = fresh_root / cad_id
        results = {system: fresh_execute(text, mesh_path, cad_root / system, executor) for system, text in [('GT', gt_text), ('LLM', llm_text), ('HEAD_V2', head_text)]}
        occ_rows.append({'cad_id': cad_id, **results, 'replacement_assignments': assignments})
        for label in label_by_cad.get(cad_id, []):
            assignment, kind = label['assignment'], label['head_type']
            if assignment not in assignments: continue
            lv, hv = llm_values[assignment], head_values[cad_id][assignment]
            if kind == 'circle':
                lpred = {'center': lv['circle.center'], 'radius': lv['circle.radius'], 'normal': lv['circle.normal']}
                hpred = {'center': hv['circle.center'], 'radius': hv['circle.radius'], 'normal': hv['circle.normal']}
            elif kind == 'extrude':
                lpred = {'origin': lv['circle.center'], 'direction': lv['circle.normal'], 'depth': lv['extrude.depth']}
                hpred = {'origin': hv['circle.center'], 'direction': hv['circle.normal'], 'depth': hv['extrude.depth']}
            else:
                lpred = {'origin': lv['box.origin'], 'extent': [lv['box.extent.width'], lv['box.extent.depth'], lv['box.extent.height']]}
                hpred = {'origin': hv['box.origin'], 'extent': [hv['box.extent.width'], hv['box.extent.depth'], hv['box.extent.height']]}
            common_parameter_labels.append(label); llm_parameter_values.append(lpred); head_parameter_values.append(hpred)

    metric_values = {'LLM': collections.defaultdict(list), 'HEAD_V2': collections.defaultdict(list)}
    for label, lv, hv in zip(common_parameter_labels, llm_parameter_values, head_parameter_values):
        for system, pred in [('LLM', lv), ('HEAD_V2', hv)]:
            for metric, value in parameter_errors(label, pred).items(): metric_values[system][metric].append(value)
    parameter_report = {'COMMON_PARAMETER_INSTANCE_COUNT': len(common_parameter_labels),
                        'COMMON_COUNTS': dict(collections.Counter(l['head_type'] for l in common_parameter_labels)),
                        'METRICS': {s: {m: summarize(v) for m, v in values.items()} for s, values in metric_values.items()},
                        'HEAD_V2_EFFECTIVE_OWNERSHIP': 'circle center/normal own Extrude origin/axis',
                        'FRESH_RECOMPUTATION': True, 'OLD_HEAD_GEOMETRY_RESULT_INVALID': True}
    write_json('DEV50_HEAD_V2_PARAMETER_METRICS.json', parameter_report)
    occ_report = {'CAD_COUNT': len(occ_rows), 'PER_CAD': occ_rows, 'FRESH_EXECUTION': True, 'EXECUTOR_SHA256': sha256(EXECUTOR)}
    write_json('DEV50_HEAD_V2_OCC_REPLAY.json', occ_report)
    common_valid = {r['cad_id'] for r in occ_rows if all(r[s]['step_reload'] and r[s]['metrics'] is not None for s in ('GT', 'LLM', 'HEAD_V2'))}
    geometry = {'ALL_VALID': {s: aggregate_occ(occ_rows, s) for s in ('GT', 'LLM', 'HEAD_V2')},
                'COMMON_VALID_COUNT': len(common_valid), 'COMMON_VALID_CAD_IDS': sorted(common_valid),
                'COMMON_VALID': {s: aggregate_occ(occ_rows, s, common_valid) for s in ('GT', 'LLM', 'HEAD_V2')},
                'FRESH_RECOMPUTATION': True, 'OLD_HEAD_GEOMETRY_RESULT_INVALID': True}
    write_json('DEV50_HEAD_V2_GEOMETRY_METRICS.json', geometry)
    llm_ch = geometry['COMMON_VALID']['LLM']['Chamfer']['median']; head_ch = geometry['COMMON_VALID']['HEAD_V2']['Chamfer']['median']
    comparison = {
        'CURRENT_GATE': 'PARAMETER_HEAD_ORACLE_V1_REEVALUATED_WITH_ROUTING_V2',
        'PARAMETER_HEAD_ORACLE_V1_SCIENTIFIC_RESULT_VALID': False, 'INVALIDATION_REASON': 'PARAMETER_COMPOSITION_ROUTING_BUG',
        'OLD_HEAD_RESULT_INVALID': True, 'OLD_HEAD_GEOMETRY_RESULT_INVALID': True,
        'V2_IS_AUTHORITATIVE': True, 'ROUTING_PASS': True, 'PERTURBATION_PASS': True,
        'ACTIVE_REPLACEMENTS': routing_report['ACTIVE_REPLACEMENTS'], 'ROUTING_MISMATCH': routing_report['ROUTING_MISMATCH'],
        'LLM_CIRCLE_RADIUS_MEDIAN': parameter_report['METRICS']['LLM']['circle_radius_abs']['median'],
        'HEAD_V2_CIRCLE_RADIUS_MEDIAN': parameter_report['METRICS']['HEAD_V2']['circle_radius_abs']['median'],
        'LLM_EXTRUDE_ORIGIN_MEDIAN': parameter_report['METRICS']['LLM']['extrude_origin']['median'],
        'HEAD_V2_EXTRUDE_ORIGIN_MEDIAN': parameter_report['METRICS']['HEAD_V2']['extrude_origin']['median'],
        'LLM_EXTRUDE_DEPTH_MEDIAN': parameter_report['METRICS']['LLM']['extrude_depth_abs']['median'],
        'HEAD_V2_EXTRUDE_DEPTH_MEDIAN': parameter_report['METRICS']['HEAD_V2']['extrude_depth_abs']['median'],
        'LLM_BOX_ORIGIN_MEDIAN': parameter_report['METRICS']['LLM']['box_origin']['median'],
        'HEAD_V2_BOX_ORIGIN_MEDIAN': parameter_report['METRICS']['HEAD_V2']['box_origin']['median'],
        'LLM_STEP': geometry['ALL_VALID']['LLM']['STEP_RELOAD'], 'HEAD_V2_STEP': geometry['ALL_VALID']['HEAD_V2']['STEP_RELOAD'],
        'LLM_COMMON_VALID_CHAMFER': llm_ch, 'HEAD_V2_COMMON_VALID_CHAMFER': head_ch,
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    write_json('LLM_VS_HEAD_V2_COMMON_VALID.json', comparison)
    finalize(comparison['CURRENT_GATE'], routing_report, perturb_report, comparison, occ_rows)


def finalize(gate: str, routing: dict, perturb: dict | None, comparison: dict | None, occ_rows: list[dict] | None = None):
    if not (OUT / 'SINGLE_PARAMETER_CAUSALITY_V2.json').exists():
        write_json('SINGLE_PARAMETER_CAUSALITY_V2.json', {'STATUS': 'NOT_RUN_DUE_GATE', 'CURRENT_GATE': gate})
    for name in ['DEV50_HEAD_V2_PARAMETER_METRICS.json', 'DEV50_HEAD_V2_OCC_REPLAY.json', 'DEV50_HEAD_V2_GEOMETRY_METRICS.json', 'LLM_VS_HEAD_V2_COMMON_VALID.json']:
        if not (OUT / name).exists(): write_json(name, {'STATUS': 'NOT_RUN_DUE_GATE', 'CURRENT_GATE': gate})
    paths = []
    if occ_rows:
        for row in occ_rows:
            for system in ('GT', 'LLM', 'HEAD_V2'):
                paths.append({k: row[system][k] for k in ('dsl_path', 'step_path', 'mesh_path', 'metric_cache_path', 'fingerprint_cache_path')})
    perturb_paths = []
    if perturb and perturb.get('EXPERIMENTS'):
        for exp in perturb['EXPERIMENTS']:
            for result in exp['RESULTS'].values():
                perturb_paths.append({k: result[k] for k in ('dsl_path', 'step_path', 'mesh_path', 'metric_cache_path', 'fingerprint_cache_path')})
    all_paths = paths + perturb_paths
    cache = {
        'CURRENT_GATE': gate, 'FRESH_EXECUTION': bool(occ_rows),
        'GT_LLM_HEAD_V2_RUN_PATH_COUNT': len(paths), 'PERTURBATION_RUN_PATH_COUNT': len(perturb_paths),
        'DSL_PATHS_UNIQUE': len({p['dsl_path'] for p in all_paths}) == len(all_paths),
        'STEP_PATHS_UNIQUE': len({p['step_path'] for p in all_paths}) == len(all_paths),
        'MESH_PATHS_UNIQUE': len({p['mesh_path'] for p in all_paths}) == len(all_paths),
        'METRIC_CACHE_USED': False, 'FINGERPRINT_CACHE_USED': False,
        'PATHS': all_paths,
    }
    write_json('CACHE_ISOLATION_V2.json', cache)
    manifest_targets = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'FILE_SHA256_MANIFEST.json')
    manifest_targets += [EXECUTOR, HEAD_CHECKPOINT, CODE_ROOT / 'run_v2.py', CODE_ROOT / 'typed_composition.py']
    files = [{'path': str(p), 'sha256': sha256(p), 'bytes': p.stat().st_size} for p in manifest_targets]
    write_json('FILE_SHA256_MANIFEST.json', {'HASH_ALGORITHM': 'SHA256', 'MANIFEST_SELF_EXCLUDED': True, 'FILE_COUNT': len(files), 'FILES': files,
                                             'CURRENT_GATE': gate, 'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False})
    final = {'CURRENT_GATE': gate, 'ACTIVE_REPLACEMENTS': routing['ACTIVE_REPLACEMENTS'], 'ROUTING_MISMATCH': routing['ROUTING_MISMATCH'],
             'ROUTING_PASS': routing.get('ROUTING_PASS'), 'PERTURBATION_PASS': perturb.get('PERTURBATION_PASS') if perturb else None,
             'OLD_HEAD_RESULT_INVALID': True, 'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False}
    if comparison: final.update(comparison)
    print(json.dumps(final, indent=2))


if __name__ == '__main__':
    main()
