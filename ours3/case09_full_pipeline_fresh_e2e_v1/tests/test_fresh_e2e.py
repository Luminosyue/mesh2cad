from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

OUT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_full_pipeline_fresh_e2e_v1')
ROOT = OUT.parent
SOURCE = ROOT / 'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
sys.path.insert(0, str(ROOT / 'v6_backend_mainline_integration'))
sys.path.insert(0, str(ROOT / 'v6_geometry_backend_restore'))
sys.path.insert(0, str(ROOT / 'v13_transform_restore_and_xcaf_assembly'))


def test_fresh_source_and_p3():
    summary = json.loads((OUT / 'artifacts/final_summary.json').read_text())
    assert summary['SOURCE_AUDIT_FRESH'] is True
    assert summary['P3_FRESH_RUN'] is True
    assert summary['P3_TRIANGLE_COVERAGE'] == 1.0
    labels = np.load(OUT / '01_p3/triangle_part_id.npy', allow_pickle=False)
    assert len(labels) == summary['SOURCE_AUDIT_FRESH'] * 140164
    assert (OUT / '01_p3/part_metadata.json').is_file()


def test_fresh_graph_and_measurements():
    graph = json.loads((OUT / '02_cad_part_graph/cad_part_graph.json').read_text())
    assert graph['CAD_PART_GRAPH_FRESH'] is True
    assert graph['source_obj_sha256'] == json.loads((OUT / 'artifacts/case09_full_e2e_provenance.json').read_text())['source_obj_sha256']
    assert len(graph['nodes']) == 8
    for node in graph['nodes']:
        assert Path(node['source_part_mesh']).is_file()
        measured = OUT / '03_geometry' / node['part_id'] / 'measured_cad_spec.json'
        assert json.loads(measured.read_text())['part_mesh_sha256'] == node['source_part_mesh_sha256']


def test_physx_and_contexts_are_fresh():
    status = json.loads((OUT / '04_physx_semantics/fresh_run_status.json').read_text())
    assert status['PHYSX_FRESH_RUN'] is True
    for part_id in [f'CADPART_{i:03d}' for i in range(8)]:
        root = OUT / '04_physx_semantics' / part_id
        assert (root / 'semantic_surface_graph.json').is_file()
        assert (root / 'cad_feature_graph.json').is_file()
        assert (root / 'design_intent_hypotheses.json').is_file()
        assert (OUT / '05_candidate_generation' / part_id / 'dual_modal_context/canonical_obj_tokens.txt').is_file()


def test_selected_steps_reload_independently():
    from fresh_e2e_runner import reload_shape
    selection = list(csv.DictReader((OUT / 'artifacts/case09_full_e2e_selection_summary.csv').open()))
    assert len(selection) == 8
    for row in selection:
        shape = reload_shape(Path(row['selected_step']))
        assert not shape.IsNull()


def test_vertical_hybrid_topology():
    from backends.v6_backend_safety_wrapper import topology_metrics
    path = OUT / '05_candidate_generation/CADPART_005/V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID_FRESH/candidate.step'
    metrics = topology_metrics(__import__('fresh_e2e_runner').reload_shape(path), 1.0)
    assert metrics['shared_edge_count'] >= 1
    assert metrics['pcurve_count'] >= 2
    assert metrics['trimmed_face_count'] >= 2
    selected = json.loads((OUT / 'artifacts/final_summary.json').read_text())
    assert selected['VERTICAL_TAIL_TOPOLOGY_PRESERVED_AFTER_ASSEMBLY'] is True


def test_final_xcaf_reload():
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    final = OUT / 'final/CASE09_full_e2e_assembly.step'
    doc, shapes, info = reload_xcaf(final)
    metrics = validate_reloaded_components(doc)
    assert info['file_readable'] is True
    assert metrics['component_count'] == 8
    assert metrics['reloaded_component_invalid_count'] == 0


def test_freshness_counters_and_artifacts():
    rows = list(csv.DictReader((OUT / 'artifacts/case09_full_e2e_freshness_audit.csv').open()))
    assert rows and all(float(row['value']) == 0 for row in rows)
    for name in ['case09_full_e2e_stage_summary.csv', 'case09_full_e2e_part_summary.csv', 'case09_full_e2e_candidate_summary.csv', 'case09_full_e2e_selection_summary.csv', 'case09_full_e2e_provenance.json', 'CASE09_FULL_E2E_PART_COMPARISON_SHADED.png', 'CASE09_FULL_E2E_PART_COMPARISON_TRUE_EDGES.png', 'CASE09_FULL_E2E_SOURCE_VS_FINAL.png', 'CASE09_FULL_PIPELINE_FRESH_END_TO_END_REPORT.md']:
        assert (OUT / 'artifacts' / name).is_file()


def test_gate_and_no_batch9():
    summary = json.loads((OUT / 'artifacts/final_summary.json').read_text())
    assert summary['CURRENT_GATE'] == 'CASE09_FULL_PIPELINE_FRESH_END_TO_END_PASS'
    assert summary['CASE09_E2E_PASS'] is True
    assert not any('batch9' in str(p).lower() for p in (OUT / 'artifacts').rglob('*') if p.is_file() and p.suffix in {'.step', '.obj'})
