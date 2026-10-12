"""Canonical V4 record schema; every source is normalized to this exact key set."""
from __future__ import annotations
from copy import deepcopy

_TEMPLATE = {
    'cad_id': '', 'source': '', 'source_id': '', 'source_path': '',
    'canonical_program_path': None, 'canonical_step_path': None, 'canonical_mesh_path': None,
    'operations': [], 'num_operations': 0,
    'has_extrude': False, 'has_cut': False, 'has_join': False, 'has_revolve': False,
    'has_loft': False, 'has_sweep': False, 'has_fillet': False, 'has_chamfer': False,
    'has_shell': False, 'has_mirror': False, 'has_pattern': False,
    'num_line': 0, 'num_arc': 0, 'num_circle': 0, 'num_ellipse': 0, 'num_bspline': 0,
    'num_faces': 0, 'num_edges': 0, 'num_solids': 0,
    'bbox_extent': None, 'volume': None, 'surface_area': None,
    'complexity': None, 'aircraft_relevance': 0,
    'dsl_parse': None, 'dsl_execute': None, 'occ_non_null': None, 'brep_valid': None,
    'step_write': None, 'step_reload': None, 'geometry_gate': None,
    'surface_valid': None, 'edge_valid': None, 'curve_valid': None, 'c2_valid': None,
    'source_sha256': None, 'canonical_dsl_sha256': None, 'geometry_fingerprint': None,
    'duplicate_group': None, 'family_id': None, 'split': None,
    'status': 'candidate', 'failure_reason': None,
}

def new_record(**values):
    record = deepcopy(_TEMPLATE)
    unknown = set(values) - set(record)
    if unknown:
        raise KeyError(f'unknown canonical schema fields: {sorted(unknown)}')
    record.update(values)
    return record

def validate_record(record):
    if set(record) != set(_TEMPLATE):
        raise ValueError('record keyset differs from canonical V4 schema')
    if not record['cad_id'] or not record['source'] or not record['source_id']:
        raise ValueError('cad_id/source/source_id are required')
