from __future__ import annotations

import ast
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

from common import EXECUTOR, EXECUTOR_SHA256, sha256


SUPPORTED_FIELDS = {
    'Circle': {'radius'},
    'Extrude': {'origin', 'axis', 'height', 'height_two'},
    'Box': {'origin', 'width', 'depth', 'height'},
}


def expr(value):
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, list):
        value = tuple(value)
    return ast.parse(repr(value), mode='eval').body


def set_kw(call: ast.Call, name: str, value) -> None:
    for keyword in call.keywords:
        if keyword.arg == name:
            keyword.value = expr(value)
            return
    call.keywords.append(ast.keyword(arg=name, value=expr(value)))


def set_pos_or_kw(call: ast.Call, position: int, name: str, value) -> None:
    if len(call.args) > position:
        call.args[position] = expr(value)
    else:
        set_kw(call, name, value)


def structure_signature(text: str) -> dict:
    tree = ast.parse(text)
    assignments = []
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        calls, refs = [], []
        for node in ast.walk(stmt.value):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node, ast.Name):
                refs.append(node.id)
        assignments.append({'name': stmt.targets[0].id, 'calls': calls, 'refs': sorted(refs)})
    return {'assignments': assignments}


def compose(gt_text: str, replacements: dict[str, dict]) -> tuple[str, list[dict]]:
    before = structure_signature(gt_text)
    tree = ast.parse(gt_text)
    audit = []
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        name = stmt.targets[0].id
        values = replacements.get(name)
        if not values or not isinstance(stmt.value, ast.Call) or not isinstance(stmt.value.func, ast.Name):
            continue
        call = stmt.value
        op = call.func.id
        if op == 'Extrude':
            if 'circle_radius' in values and call.args and isinstance(call.args[0], ast.Call):
                circle = call.args[0]
                if isinstance(circle.func, ast.Name) and circle.func.id in {'Circle', 'Sketch'}:
                    set_pos_or_kw(circle, 0, 'radius', values['circle_radius'])
                    audit.append({'assignment': name, 'operation': 'Circle', 'field': 'radius', 'value': values['circle_radius']})
            set_pos_or_kw(call, 1, 'height', values['depth'])
            set_kw(call, 'origin', tuple(values['origin']))
            set_kw(call, 'axis', tuple(values['direction']))
            audit.extend([
                {'assignment': name, 'operation': 'Extrude', 'field': 'height', 'value': values['depth']},
                {'assignment': name, 'operation': 'Extrude', 'field': 'origin', 'value': values['origin']},
                {'assignment': name, 'operation': 'Extrude', 'field': 'axis', 'value': values['direction']},
            ])
            if any(keyword.arg == 'height_two' for keyword in call.keywords):
                set_kw(call, 'height_two', values['height_two'])
                audit.append({'assignment': name, 'operation': 'Extrude', 'field': 'height_two', 'value': values['height_two']})
        elif op == 'Box':
            set_pos_or_kw(call, 0, 'width', values['extent'][0])
            set_pos_or_kw(call, 1, 'depth', values['extent'][1])
            set_pos_or_kw(call, 2, 'height', values['extent'][2])
            set_kw(call, 'origin', tuple(values['origin']))
            for field, value in zip(('width', 'depth', 'height'), values['extent']):
                audit.append({'assignment': name, 'operation': 'Box', 'field': field, 'value': value})
            audit.append({'assignment': name, 'operation': 'Box', 'field': 'origin', 'value': values['origin']})
    text = ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    after = structure_signature(text)
    if before != after:
        raise RuntimeError('Operation skeleton changed during parameter replacement')
    return text, audit


def inverse_predictions(labels: list[dict], predictions: list[dict]) -> dict[str, dict]:
    output = {}
    for label, pred in zip(labels, predictions):
        scale = float(label['object_scale'])
        center = np.asarray(label['object_center'], dtype=float)
        assignment = label['assignment']
        item = output.setdefault(assignment, {})
        if label['head_type'] == 'circle':
            item['circle_center'] = (np.asarray(pred['center']) * scale + center).tolist()
            item['circle_radius'] = float(pred['radius']) * scale
            item['circle_normal'] = pred['normal']
        elif label['head_type'] == 'extrude':
            item['origin'] = (np.asarray(pred['origin']) * scale + center).tolist()
            item['direction'] = pred['direction']
            item['depth'] = float(pred['depth']) * scale
            item['height_two'] = float(pred['height_two']) * scale
        elif label['head_type'] == 'box':
            item['origin'] = (np.asarray(pred['origin']) * scale + center).tolist()
            item['extent'] = (np.asarray(pred['extent']) * scale).tolist()
    # Composition uses Extrude head for origin/direction/depth and Circle head for radius.
    return {name: values for name, values in output.items() if ('extent' in values or {'circle_radius', 'origin', 'direction', 'depth', 'height_two'} <= set(values))}


def load_executor():
    if sha256(EXECUTOR) != EXECUTOR_SHA256:
        raise RuntimeError('executor sha256 mismatch')
    spec = importlib.util.spec_from_file_location('parameter_head_executor', EXECUTOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def replay(text: str, mesh_path: Path, output_dir: Path, executor) -> dict:
    output_dir.mkdir(parents=True, exist_ok=False)
    record = {'parse': False, 'execute': False, 'non_null': False, 'brep_valid': False, 'step_write': False, 'step_reload': False, 'chamfer': None, 'H95': None, 'bbox_center': None, 'bbox_extent': None, 'failure': None}
    try:
        clean = executor.extract_dsl_code(text)
        ast.parse(clean)
        program = executor.parse_dsl(clean)
        record['parse'] = True
        shapes = {}
        for name, node in program.assignments.items():
            if name != 'result':
                shapes[name] = executor._build_shape(node, shapes) if isinstance(node, dict) and 'op' in node else node
        node = program.assignments['result']
        result = shapes[node] if isinstance(node, str) else executor._build_shape(node, shapes)
        record['execute'] = True
        shape = result.val().wrapped if hasattr(result, 'val') else result
        if shape.IsNull():
            record['failure'] = 'NULL_SHAPE'; return record
        record['non_null'] = True
        from OCP.BRepCheck import BRepCheck_Analyzer
        if not BRepCheck_Analyzer(shape).IsValid():
            record['failure'] = 'BREP_INVALID'; return record
        record['brep_valid'] = True
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
        step = output_dir / 'result.step'
        writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
        if writer.Write(str(step)) != IFSelect_RetDone:
            record['failure'] = 'STEP_WRITE'; return record
        record['step_write'] = True
        import cadquery as cq
        loaded = cq.importers.importStep(str(step)); record['step_reload'] = True
        stl = output_dir / 'result.stl'; cq.exporters.export(loaded, str(stl))
        import trimesh
        from scipy.spatial import cKDTree
        gt = trimesh.load(str(mesh_path), force='mesh'); pred = trimesh.load(str(stl), force='mesh')
        if isinstance(gt, trimesh.Scene): gt = gt.dump(concatenate=True)
        if isinstance(pred, trimesh.Scene): pred = pred.dump(concatenate=True)
        ge, pe = gt.bounds[1] - gt.bounds[0], pred.bounds[1] - pred.bounds[0]
        gc, pc = gt.bounds.mean(0), pred.bounds.mean(0)
        diagonal = max(float(np.linalg.norm(ge)), 1e-12)
        a, _ = trimesh.sample.sample_surface(gt, 3000, seed=42)
        b, _ = trimesh.sample.sample_surface(pred, 3000, seed=43)
        da = cKDTree(b).query(a, k=1)[0]; db = cKDTree(a).query(b, k=1)[0]
        record['chamfer'] = float((da.mean() + db.mean()) / 2 / diagonal)
        record['H95'] = float(np.percentile(np.concatenate([da, db]), 95) / diagonal)
        record['bbox_center'] = float(np.linalg.norm(pc - gc) / diagonal)
        record['bbox_extent'] = float(np.linalg.norm(pe - ge) / diagonal)
        record['failure'] = 'SUCCESS'
    except Exception as error:
        record['failure'] = f'{type(error).__name__}: {error}'[-800:]
    return record
