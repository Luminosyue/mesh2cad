from __future__ import annotations

import numpy as np
import pytest
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

from futurecad_grounding.deterministic_grounder import DeterministicBRepGrounder
from futurecad_grounding.feature_execution_loop import FeatureExecutionLoop
from futurecad_grounding.futurecad_adapter import FutureCADToV11Adapter
from futurecad_grounding.geometric_descriptor import shape_bbox
from futurecad_grounding.grounding_resolver import GroundingResolver, StaleRuntimePrimitiveError
from futurecad_grounding.grounding_validator import validate_parameter_refs
from futurecad_grounding.primitive_inventory import PartLocalFrame, PrimitiveInventoryBuilder
from futurecad_grounding.schema import FeatureOperationPlan, FutureCADProgramProposal, PrimitiveGroundingQuery


CATALOG = {
    'MEASURED_SPEC.FEATURES.FILLET_RADIUS_001': {'value': 0.20, 'authority': 'MEASURED_SPEC'},
    'MEASURED_SPEC.FEATURES.CHAMFER_DISTANCE_001': {'value': 0.25, 'authority': 'MEASURED_SPEC'},
}


def box_shape():
    return BRepPrimAPI_MakeBox(10.0, 8.0, 6.0).Shape()


def frame_for(shape):
    bounds = np.asarray(shape_bbox(shape), dtype=float)
    center = (bounds[0] + bounds[1]) * 0.5
    return PartLocalFrame.from_axes(center, [1, 0, 0], [0, 1, 0], [0, 0, 1], 'TEST_FRAME')


def box_edge_query():
    return PrimitiveGroundingQuery(
        'EDGE',
        'the four vertical outer edges',
        {'orientation': 'VERTICAL', 'boundary_role': 'OUTER'},
        4,
    )


def resolver():
    return GroundingResolver(DeterministicBRepGrounder())


def test_inventory_has_state_local_face_edge_and_vertex_ids():
    shape = box_shape()
    inventory = PrimitiveInventoryBuilder().build(shape, frame_for(shape), 'STATE_007')
    assert len(inventory.faces) == 6
    assert len(inventory.edges) == 12
    assert len(inventory.vertices) == 8
    for target in ('faces', 'edges', 'vertices'):
        assert all(row['runtime_id'].startswith('STATE_007:') for row in getattr(inventory, target))


def test_structured_box_query_grounds_exact_edges():
    shape = box_shape()
    inventory = PrimitiveInventoryBuilder().build(shape, frame_for(shape), 'STATE_000')
    result = resolver().ground(box_edge_query(), inventory)
    assert result.valid
    assert len(result.selected_runtime_ids) == 4
    selected = [next(row for row in inventory.edges if row['runtime_id'] == runtime_id) for runtime_id in result.selected_runtime_ids]
    assert all('VERTICAL' in row['orientation'] and row['outer_boundary'] for row in selected)


def test_ambiguous_query_is_rejected():
    shape = box_shape()
    inventory = PrimitiveInventoryBuilder().build(shape, frame_for(shape), 'STATE_000')
    query = PrimitiveGroundingQuery('EDGE', 'one outer edge', {'boundary_role': 'OUTER'}, 1, confidence_requirement=0.5)
    result = resolver().ground(query, inventory)
    assert result.status == 'GROUNDING_AMBIGUOUS'
    assert not result.selected_runtime_ids


def test_stale_runtime_id_is_rejected():
    shape = box_shape()
    builder = PrimitiveInventoryBuilder()
    inventory_0 = builder.build(shape, frame_for(shape), 'STATE_000')
    inventory_1 = builder.build(shape, frame_for(shape), 'STATE_001')
    with pytest.raises(StaleRuntimePrimitiveError, match='STALE_RUNTIME_ID'):
        resolver().validate_runtime_ids([inventory_0.edges[0]['runtime_id']], inventory_1)


def test_numeric_parameter_refs_are_authoritative():
    valid = validate_parameter_refs({'radius_ref': 'MEASURED_SPEC.FEATURES.FILLET_RADIUS_001'}, CATALOG)
    bad_literal = validate_parameter_refs({'radius_ref': '0.2'}, CATALOG)
    missing = validate_parameter_refs({'radius_ref': 'MEASURED_SPEC.FEATURES.UNKNOWN'}, CATALOG)
    assert valid['PARAMETER_REFS_VALID']
    assert not bad_literal['PARAMETER_REFS_VALID']
    assert not missing['PARAMETER_REFS_VALID']


def test_futurecad_adapter_emits_grounded_v11_plan_without_runtime_ids():
    proposal = FutureCADProgramProposal(
        'FIXTURE',
        [
            {'operation': 'CREATE_BASE_BOX', 'operation_id': 'BASE'},
            {
                'operation': 'FILLET',
                'operation_id': 'F1',
                'grounding_query_id': 'Q1',
                'numeric_parameter_placeholders': {'radius_ref': 'RADIUS'},
            },
        ],
        [
            {
                'query_id': 'Q1',
                'target_type': 'EDGE',
                'natural_language_query': 'the four vertical outer edges',
                'structured_constraints': {'orientation': 'VERTICAL', 'boundary_role': 'OUTER'},
                'expected_count': 4,
            }
        ],
        {'RADIUS': 'MEASURED_SPEC.FEATURES.FILLET_RADIUS_001'},
    )
    plans = FutureCADToV11Adapter().adapt(proposal)
    assert len(plans) == 1
    assert plans[0].operation == 'FILLET'
    assert plans[0].parameter_refs['radius_ref'] in CATALOG
    assert 'RT_' not in str(plans[0].to_dict())


def test_grounded_fillet_executes_and_returns_valid_new_brep():
    shape = box_shape()
    plan = FeatureOperationPlan(
        'FILLET',
        box_edge_query(),
        {'radius_ref': 'MEASURED_SPEC.FEATURES.FILLET_RADIUS_001'},
        'FILLET_TEST',
    )
    result = FeatureExecutionLoop(resolver(), CATALOG).run(shape, frame_for(shape), [plan])
    assert result['operations'][0]['accepted']
    assert result['counters']['FILLET_GROUNDING_EXECUTED_COUNT'] == 1
    assert BRepCheck_Analyzer(result['shape']).IsValid()
    assert result['states'][0].shape_signature != result['final_inventory'].shape_signature


def test_grounded_chamfer_reinventories_and_invalidates_old_ids():
    shape = box_shape()
    local_frame = frame_for(shape)
    plan = FeatureOperationPlan(
        'CHAMFER',
        box_edge_query(),
        {'distance_ref': 'MEASURED_SPEC.FEATURES.CHAMFER_DISTANCE_001'},
        'CHAMFER_TEST',
    )
    result = FeatureExecutionLoop(resolver(), CATALOG).run(shape, local_frame, [plan])
    assert result['operations'][0]['accepted']
    assert result['final_inventory'].inventory_version == 'STATE_001'
    assert result['states'][0].inventory_hash != result['final_inventory'].inventory_hash
    stale_id = result['states'][0].edges[0]['runtime_id']
    with pytest.raises(StaleRuntimePrimitiveError, match='STALE_RUNTIME_ID'):
        resolver().validate_runtime_ids([stale_id], result['final_inventory'])


def test_invalid_parameter_ref_rolls_back_without_execution():
    shape = box_shape()
    plan = FeatureOperationPlan('FILLET', box_edge_query(), {'radius_ref': '0.2'}, 'BAD_REF')
    result = FeatureExecutionLoop(resolver(), CATALOG).run(shape, frame_for(shape), [plan])
    assert result['operations'][0]['rollback']
    assert not result['operations'][0]['accepted']
    assert result['counters']['FILLET_GROUNDING_EXECUTED_COUNT'] == 0
    assert result['final_inventory'].shape_signature == result['states'][0].shape_signature
