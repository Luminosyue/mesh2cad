from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any


def _expr(value: Any) -> ast.expr:
    if hasattr(value, 'tolist'):
        value = value.tolist()
    if isinstance(value, list):
        value = tuple(value)
    return ast.parse(repr(value), mode='eval').body


def _literal(node: ast.AST) -> Any:
    return ast.literal_eval(node)


def _get(call: ast.Call, position: int, keyword: str, default=None):
    if position >= 0 and len(call.args) > position:
        return _literal(call.args[position])
    for item in call.keywords:
        if item.arg == keyword:
            return _literal(item.value)
    return default


def _has_kw(call: ast.Call, keyword: str) -> bool:
    return any(item.arg == keyword for item in call.keywords)


def _set(call: ast.Call, position: int, keyword: str, value: Any) -> None:
    if position >= 0 and len(call.args) > position:
        call.args[position] = _expr(value)
        return
    for item in call.keywords:
        if item.arg == keyword:
            item.value = _expr(value)
            return
    call.keywords.append(ast.keyword(arg=keyword, value=_expr(value)))


def structure_signature(tree: ast.Module) -> list[dict]:
    result = []
    for stmt in tree.body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
            continue
        calls, refs = [], []
        for node in ast.walk(stmt.value):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node, ast.Name):
                refs.append(node.id)
        result.append({'name': stmt.targets[0].id, 'calls': calls, 'refs': sorted(refs)})
    return result


@dataclass
class TypedOperation:
    index: int
    assignment: str
    op_type: str
    call: ast.Call

    def circle_call(self) -> ast.Call | None:
        if self.op_type != 'Extrude' or not self.call.args or not isinstance(self.call.args[0], ast.Call):
            return None
        nested = self.call.args[0]
        if isinstance(nested.func, ast.Name) and nested.func.id in {'Circle', 'Sketch'}:
            return nested
        return None

    def active_mask(self) -> list[dict]:
        if self.op_type == 'Extrude' and self.circle_call() is not None:
            symmetric = bool(_get(self.call, -1, 'symmetric', False))
            explicit_h2 = _has_kw(self.call, 'height_two')
            h2 = float(_get(self.call, -1, 'height_two', 0.0))
            h2_active = explicit_h2 and not symmetric and abs(h2) > 1e-12
            return [
                {'parameter': 'circle.radius', 'active': True, 'owner': 'CircleParameterHead.radius'},
                {'parameter': 'circle.center', 'active': True, 'owner': 'CircleParameterHead.center', 'effective_slot': 'Extrude.origin'},
                {'parameter': 'circle.normal', 'active': True, 'owner': 'CircleParameterHead.normal', 'effective_slot': 'Extrude.axis'},
                {'parameter': 'extrude.origin', 'active': False, 'owner': 'ExtrudeParameterHead.origin', 'skipped_reason': 'COALESCED_WITH_PROFILE_CENTER_SINGLE_ORIGIN_EXECUTOR'},
                {'parameter': 'extrude.direction', 'active': False, 'owner': 'ExtrudeParameterHead.direction', 'skipped_reason': 'COALESCED_WITH_PROFILE_NORMAL_SINGLE_AXIS_EXECUTOR'},
                {'parameter': 'extrude.depth', 'active': True, 'owner': 'ExtrudeParameterHead.depth', 'effective_slot': 'Extrude.height'},
                {'parameter': 'extrude.height_two', 'active': h2_active, 'owner': 'ExtrudeParameterHead.height_two', 'effective_slot': 'Extrude.height_two', 'skipped_reason': None if h2_active else 'INACTIVE_IN_GT_SKELETON'},
            ]
        if self.op_type == 'Box':
            return [
                {'parameter': 'box.origin', 'active': True, 'owner': 'BoxParameterHead.origin'},
                {'parameter': 'box.extent.width', 'active': True, 'owner': 'BoxParameterHead.extent[0]'},
                {'parameter': 'box.extent.depth', 'active': True, 'owner': 'BoxParameterHead.extent[1]'},
                {'parameter': 'box.extent.height', 'active': True, 'owner': 'BoxParameterHead.extent[2]'},
            ]
        return []

    def get(self, parameter: str):
        circle = self.circle_call()
        if parameter == 'circle.radius' and circle is not None:
            return _get(circle, 0, 'radius')
        mapping = {
            'circle.center': (-1, 'origin', (0.0, 0.0, 0.0)),
            'circle.normal': (-1, 'axis', (0.0, 0.0, 1.0)),
            'extrude.depth': (1, 'height', None),
            'extrude.height_two': (-1, 'height_two', 0.0),
            'box.origin': (-1, 'origin', (0.0, 0.0, 0.0)),
            'box.extent.width': (0, 'width', None),
            'box.extent.depth': (1, 'depth', None),
            'box.extent.height': (2, 'height', None),
        }
        if parameter not in mapping:
            raise KeyError(parameter)
        pos, keyword, default = mapping[parameter]
        return _get(self.call, pos, keyword, default)

    def set(self, parameter: str, value: Any) -> None:
        circle = self.circle_call()
        if parameter == 'circle.radius' and circle is not None:
            _set(circle, 0, 'radius', value); return
        mapping = {
            'circle.center': (-1, 'origin'), 'circle.normal': (-1, 'axis'),
            'extrude.depth': (1, 'height'), 'extrude.height_two': (-1, 'height_two'),
            'box.origin': (-1, 'origin'), 'box.extent.width': (0, 'width'),
            'box.extent.depth': (1, 'depth'), 'box.extent.height': (2, 'height'),
        }
        pos, keyword = mapping[parameter]
        _set(self.call, pos, keyword, value)


class TypedProgram:
    def __init__(self, text: str):
        self.tree = ast.parse(text)
        self.original_signature = structure_signature(self.tree)
        self.operations: dict[str, TypedOperation] = {}
        index = -1
        for stmt in self.tree.body:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                continue
            name = stmt.targets[0].id
            if name == 'result':
                continue
            index += 1
            if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                self.operations[name] = TypedOperation(index, name, stmt.value.func.id, stmt.value)

    def serialize(self) -> str:
        if structure_signature(self.tree) != self.original_signature:
            raise RuntimeError('typed AST operation skeleton changed')
        return ast.unparse(ast.fix_missing_locations(self.tree)) + '\n'

    def bind(self, assignment: str, values: dict[str, Any]) -> list[dict]:
        operation = self.operations[assignment]
        mask = {row['parameter']: row for row in operation.active_mask()}
        applied = []
        for parameter, value in values.items():
            slot = mask[parameter]
            if not slot['active']:
                applied.append({**slot, 'parameter_applied': False, 'head_world_value': value})
                continue
            operation.set(parameter, value)
            applied.append({**slot, 'parameter_applied': True, 'head_world_value': value, 'ast_value': operation.get(parameter)})
        return applied
