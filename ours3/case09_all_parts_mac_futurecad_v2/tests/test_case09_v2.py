import json
import re
from pathlib import Path

import pytest
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2')
SUMMARY = json.loads((ROOT/'metrics/summary.json').read_text())
MAC = json.loads((ROOT/'metrics/mac_aggregate.json').read_text())
PARTS = [f'CADPART_{i:03d}' for i in range(8)]


def test_v1_inputs_frozen():
    assert SUMMARY['V1_FROZEN'] is True


def test_source_sha_provenance():
    assert SUMMARY['SOURCE_SHA256'] == 'ec3b6fb83ce405bd4c6cd41bb506ef9e5a8995919fb32ab9c40411f400e823cd'


def test_p3_not_rerun():
    assert SUMMARY['P3_RERUN'] is False


def test_physx_not_rerun():
    assert SUMMARY['PHYSX_RERUN'] is False


def test_all_8_parts_mac_attempted():
    assert MAC['MAC_PARTS_ATTEMPTED'] == 8


def test_all_8_parts_mac_success():
    assert MAC['MAC_PARTS_SUCCESS'] == 8 and MAC['MAC_PART_RATIO'] == 1.0


def test_each_part_llm_calls_positive():
    assert all(p['LLM_CALLS'] > 0 for p in MAC['parts'])


def test_each_part_mac_run_positive():
    assert all(p['MAC_RUNS'] >= 1 for p in MAC['parts'])


def test_required_mac_artifacts_exist():
    required = ['cad_brief.json','architect_plan.json','generated_code.py','mac_prompt.txt','mac_response.json','execution_log.txt','token_usage.json']
    assert all((ROOT/'02_mac_runs'/part/name).is_file() for part in PARTS for name in required)


def test_mac_receives_measured_spec():
    for part in PARTS:
        spec = json.loads((ROOT/'01_part_specs'/part/'measured_cad_spec.json').read_text())
        assert spec['operations'] and spec['raw_obj_read_by_mac'] is False and spec['old_step_read_by_mac'] is False


def test_no_raw_mesh_dimension_guess():
    source = SUMMARY['SOURCE_OBJ']
    for part in PARTS:
        prompt = (ROOT/'02_mac_runs'/part/'mac_prompt.txt').read_text(errors='ignore')
        assert source not in prompt


def test_futurecad_repo_audit():
    assert SUMMARY['FUTURECAD_REPO_FOUND'] is True


def test_no_fake_futurecad_usage():
    assert SUMMARY['FUTURECAD_OFFICIAL_USED'] is False
    assert SUMMARY['GROUNDING_MODE'] == 'FUTURECAD_COMPATIBLE_GROUNDING_PROXY'


def test_transient_brep_graph():
    for part in PARTS:
        graph = json.loads((ROOT/'03_grounding'/part/'transient_brep_graph.json').read_text())
        assert graph['fresh_reload'] and graph['brep_valid'] and graph['face_count'] > 0 and graph['edge_count'] > 0


def test_transient_graph_face_schema():
    required = {'surface_type','area','centroid','normal','bbox','inner_wires','adjacent_edges','adjacent_faces'}
    for part in PARTS:
        graph = json.loads((ROOT/'03_grounding'/part/'transient_brep_graph.json').read_text())
        assert all(required <= set(face) for face in graph['faces'])


def test_transient_graph_edge_schema():
    required = {'curve_type','length','centroid','tangent','adjacent_faces','dihedral_degrees','closed','bbox'}
    for part in PARTS:
        graph = json.loads((ROOT/'03_grounding'/part/'transient_brep_graph.json').read_text())
        assert all(required <= set(edge) for edge in graph['edges'])


def test_grounding_query_schema():
    assert SUMMARY['GROUNDING_REQUIRED_PARTS'] == [] and SUMMARY['GROUNDING_QUERIES'] == 0


def test_grounding_entity_valid():
    assert SUMMARY['GROUNDING_FAILURES'] == 0


def test_no_fixed_topology_index_dependency():
    pattern = re.compile(r'(?:faces|edges)\s*\(\s*\)\s*\[\s*\d+')
    assert all(not pattern.search((ROOT/'04_program_execution'/p/'final_generated_code.py').read_text()) for p in PARTS)


def test_mac_candidate_generation():
    assert all(p['MAC_CANDIDATES'] >= 3 and len(p['candidates']) >= 3 for p in MAC['parts'])


def test_mac_feedback_loop_recorded():
    assert all((ROOT/'02_mac_runs'/p['part_id']/f"candidate_{c['candidate']:02d}"/'execution_log.txt').is_file() for p in MAC['parts'] for c in p['candidates'])


def test_max_repair_rounds():
    assert all(c['repair_rounds'] <= 3 for p in MAC['parts'] for c in p['candidates'])


def test_part_brep_valid():
    assert all(p['BREP_VALID'] and p['FINAL_STEP_RELOAD'] for p in SUMMARY['part_qa'])


def test_geometry_thresholds_frozen():
    assert SUMMARY['CHAMFER'] <= .01 and SUMMARY['P95'] <= .02 and SUMMARY['COVERAGE02'] >= .95


def test_final_geometry_q1():
    assert SUMMARY['GEOM_Q'] == 'Q1'


def test_sharp_edge_metric():
    assert SUMMARY['V2_SHARP_EDGE_RECALL'] >= .90


def test_feature_boundary_metric():
    assert SUMMARY['V2_FEATURE_BOUNDARY_RECALL'] >= .98


def test_structure_qa():
    assert SUMMARY['CAD_STRUCTURE_Q'] == 'PASS' and SUMMARY['V2_STRIP_EDGE_RATIO'] < .05


def test_part_transform_preserved():
    assert all(p['transform_preserved'] for p in SUMMARY['part_qa'])


def test_xcaf_assembly():
    manifest = json.loads((ROOT/'06_assembly/assembly_manifest.json').read_text())
    assert manifest['XCAF_ASSEMBLY_PRESENT'] and manifest['FINAL_COMPONENT_COUNT'] == 8


def test_final_step_reload():
    reader = STEPControl_Reader(); status = reader.ReadFile(SUMMARY['FINAL_STEP'])
    assert status == IFSelect_RetDone and reader.TransferRoots() > 0
    assert BRepCheck_Analyzer(reader.OneShape()).IsValid()


def test_all_final_programs_exist():
    assert all((ROOT/'04_program_execution'/p/'final_generated_code.py').is_file() for p in PARTS)


def test_wing_tail_feature_semantics():
    for p in ['CADPART_001','CADPART_002','CADPART_003','CADPART_004','CADPART_005']:
        text = (ROOT/'04_program_execution'/p/'final_generated_code.py').read_text()
        assert 'build_profile_loft_part' in text


def test_propeller_pattern_semantics():
    text = (ROOT/'04_program_execution/CADPART_006/final_generated_code.py').read_text()
    assert 'build_patterned_blade_part' in text and 'MEASURED_INSTANCE_PATTERN' in text and 'forced_symmetry' in text


def test_no_debug_fallback_selected():
    assert all(p['DEBUG_FALLBACK_RESULT'] == 'NOT_RUN' for p in SUMMARY['part_qa'])


def test_visual_artifacts_exist():
    assert all(Path(SUMMARY[k]).is_file() for k in ['COMPARISON_FIGURE','TRUE_EDGE_FIGURE','GROUNDING_FIGURE'])
