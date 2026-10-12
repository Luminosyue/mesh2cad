from __future__ import annotations

import numpy as np
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepFilletAPI import BRepFilletAPI_MakeChamfer, BRepFilletAPI_MakeFillet

from .grounding_validator import validate_grounding_result, validate_parameter_refs
from .primitive_inventory import PrimitiveInventoryBuilder
from .provenance import GroundingProvenanceLog


class FeatureExecutionLoop:
    def __init__(self, resolver, parameter_catalog: dict[str, dict], *, explosion_ratio=2.5):
        self.resolver = resolver
        self.parameter_catalog = parameter_catalog
        self.inventory_builder = PrimitiveInventoryBuilder()
        self.explosion_ratio = explosion_ratio
        self.provenance = GroundingProvenanceLog()
        self.counters = {
            'FILLET_GROUNDING_EXECUTED_COUNT': 0, 'CHAMFER_GROUNDING_EXECUTED_COUNT': 0,
            'SHELL_GROUNDING_EXECUTED_COUNT': 0, 'EXECUTED_FEATURE_WITHOUT_GROUNDING_COUNT': 0,
            'EXECUTED_FEATURE_WITH_AMBIGUOUS_GROUNDING_COUNT': 0,
            'EXECUTED_PARAMETER_WITHOUT_REF_COUNT': 0, 'STALE_RUNTIME_PRIMITIVE_USED_COUNT': 0,
            'INVALID_FEATURE_BREP_ACCEPTED_COUNT': 0, 'DIRECT_TEXT_TO_OCC_BYPASS_COUNT': 0,
            'GEOMETRY_EXPLOSION_COUNT': 0,
        }

    def run(self, base_shape, frame, plans):
        current = base_shape; states = []; operations = []
        for index, plan in enumerate(plans):
            state_id = f'STATE_{index:03d}'
            inventory = self.inventory_builder.build(current, frame, state_id)
            result = self.resolver.ground(plan.target_grounding_query, inventory, {'operation': plan.operation})
            grounding_check = validate_grounding_result(plan.target_grounding_query, result, inventory)
            refs_check = validate_parameter_refs(plan.parameter_refs, self.parameter_catalog)
            row = {'operation_id': plan.operation_id, 'operation': plan.operation, 'input_state': state_id, 'input_shape_signature': inventory.shape_signature, 'inventory_hash': inventory.inventory_hash, 'grounding_status': result.status, 'grounding_confidence': result.confidence, 'selected_runtime_ids': result.selected_runtime_ids, 'parameter_refs': plan.parameter_refs, 'accepted': False, 'rollback': False}
            if not grounding_check['GROUNDING_VALID']:
                if result.status == 'GROUNDING_AMBIGUOUS': self.counters['EXECUTED_FEATURE_WITH_AMBIGUOUS_GROUNDING_COUNT'] += 0
                row['reject_reason'] = grounding_check['reasons']; row['rollback'] = True
                self.provenance.append(inventory=inventory, query=plan.target_grounding_query, result=result, feature_operation=plan.operation)
                operations.append(row); states.append(inventory); break
            if not refs_check['PARAMETER_REFS_VALID']:
                self.counters['EXECUTED_PARAMETER_WITHOUT_REF_COUNT'] += 0
                row['reject_reason'] = refs_check['reasons']; row['rollback'] = True
                operations.append(row); states.append(inventory); break
            if plan.diagnostic_only:
                row['diagnostic_only'] = True; operations.append(row); states.append(inventory); continue
            targets = self.resolver.resolve_shapes(result, inventory)
            try:
                candidate = self._execute(current, plan.operation, targets, plan.parameter_refs)
            except Exception as exc:
                row['reject_reason'] = f'{type(exc).__name__}:{exc}'; row['rollback'] = True
                operations.append(row); states.append(inventory); break
            if candidate is None or candidate.IsNull() or not BRepCheck_Analyzer(candidate).IsValid():
                row['reject_reason'] = 'INVALID_TOPOLOGY'; row['rollback'] = True
                operations.append(row); states.append(inventory); break
            next_inventory = self.inventory_builder.build(candidate, frame, f'STATE_{index+1:03d}')
            before = np.asarray(inventory.shape_bbox); after = np.asarray(next_inventory.shape_bbox)
            before_diag = max(float(np.linalg.norm(before[1] - before[0])), 1e-9)
            after_diag = float(np.linalg.norm(after[1] - after[0]))
            if after_diag / before_diag > self.explosion_ratio:
                self.counters['GEOMETRY_EXPLOSION_COUNT'] += 1; row['reject_reason'] = 'GEOMETRY_EXPLOSION'; row['rollback'] = True
                operations.append(row); states.append(inventory); break
            current = candidate; row['accepted'] = True; row['output_state'] = next_inventory.inventory_version; row['result_shape_signature'] = next_inventory.shape_signature
            self.counters[f'{plan.operation}_GROUNDING_EXECUTED_COUNT'] += 1
            self.provenance.append(inventory=inventory, query=plan.target_grounding_query, result=result, feature_operation=plan.operation, result_shape_signature=next_inventory.shape_signature)
            operations.append(row); states.append(inventory)
        final_state = f'STATE_{len([row for row in operations if row.get("accepted")]):03d}'
        final_inventory = self.inventory_builder.build(current, frame, final_state)
        return {'shape': current, 'states': states, 'final_inventory': final_inventory, 'operations': operations, 'counters': dict(self.counters), 'provenance': self.provenance.to_dict()}

    def _value(self, refs, name):
        ref = refs[name]
        entry = self.parameter_catalog[ref]
        return float(entry['value'] if isinstance(entry, dict) else entry)

    def _execute(self, shape, operation, targets, refs):
        if operation == 'FILLET':
            radius = self._value(refs, 'radius_ref')
            if radius <= 0: raise ValueError('INVALID_RADIUS')
            maker = BRepFilletAPI_MakeFillet(shape)
            for edge in targets: maker.Add(radius, edge)
            maker.Build()
            if not maker.IsDone(): raise RuntimeError('FILLET_FAILED')
            return maker.Shape()
        if operation == 'CHAMFER':
            distance = self._value(refs, 'distance_ref')
            if distance <= 0: raise ValueError('INVALID_CHAMFER_DISTANCE')
            maker = BRepFilletAPI_MakeChamfer(shape)
            for edge in targets: maker.Add(distance, edge)
            maker.Build()
            if not maker.IsDone(): raise RuntimeError('CHAMFER_FAILED')
            return maker.Shape()
        if operation == 'SHELL':
            raise RuntimeError('SHELL_DIAGNOSTIC_ONLY_V1')
        raise ValueError(f'UNSUPPORTED_OPERATION:{operation}')
