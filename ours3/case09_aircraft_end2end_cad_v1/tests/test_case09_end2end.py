import hashlib
import json
from pathlib import Path

import pytest

from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'case09_aircraft_end2end_cad_v1'
SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
FINAL=OUT/'07_assembly/CASE09_aircraft_final.step'


def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


@pytest.fixture(scope='module')
def summary(): return load(OUT/'metrics/summary.json')


@pytest.fixture(scope='module')
def graph(): return load(OUT/'02_cad_part_graph/cad_part_graph.json')


def test_source_frozen():
    audit=load(OUT/'00_source/source_audit.json');manifest=load(OUT/'00_source/provenance_manifest.json')
    assert audit['SOURCE_SHA256']==manifest['source_sha256']==digest(SOURCE)
    assert not audit['geometry_modified']


def test_no_old_step_used_for_reconstruction():
    manifest=load(OUT/'00_source/provenance_manifest.json')
    assert manifest['old_baseline_role']=='FINAL_EVALUATION_ONLY'
    assert manifest['old_step_used_for_reconstruction'] is False
    for spec in (OUT/'05_backend_recovery').glob('*/measured_cad_spec.json'):
        assert load(spec)['old_step_read_by_builder'] is False


def test_p3_real_inference():
    meta=load(OUT/'01_part_discovery/p3/part_metadata.json')
    assert meta['method']=='P3-SAM' and meta['adapter']=='P3SAMAdapter'
    assert meta['connected_components_used_as_p3'] is False
    assert meta['num_parts']==10 and (OUT/'01_part_discovery/p3/triangle_part_id.npy').is_file()


def test_physx_real_inference_or_explicit_skip():
    p=load(OUT/'01_part_discovery/physx/provenance.json')
    assert p['PHYSX_RAN'] is True and p['success'] is True
    assert p['semantic_prior_is_soft'] is True and p['geometry_modified'] is False


def test_cad_part_graph(graph):
    assert graph['cad_part_count']==8 and len(graph['nodes'])==8
    assert graph['fusion_applied'] is True and graph['direct_segment_to_part_mapping'] is False


def test_transform_preserved(graph):
    identity=[[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[0.0,0.0,0.0,1.0]]
    assert all(n['local_to_global_transform']==identity and n['global_to_local_transform']==identity for n in graph['nodes'])


def test_geometry_analyzer(graph):
    for node in graph['nodes']:
        d=load(OUT/'03_geometry_analyzer'/node['part_id']/'geometry_analysis.json')
        assert d['source_triangle_count']>0 and len(d['cross_sections'])==64


def test_feature_graph(graph):
    for node in graph['nodes']:
        d=load(OUT/'04_feature_graph'/node['part_id']/'cad_feature_graph.json')
        assert d['FINAL_FEATURE_COUNT']>=1 and d['STRIP_LOFT_FAILURE'] is False


def test_wing_feature_hypothesis():
    for part in ('CADPART_001','CADPART_002'):
        d=load(OUT/'04_feature_graph'/part/'cad_feature_graph.json')
        assert any(n['type']=='LOFT' and n.get('global_surface') for n in d['nodes'])


def test_fuselage_feature_hypothesis():
    d=load(OUT/'04_feature_graph/CADPART_000/cad_feature_graph.json')
    assert any(n['type']=='LOFT' and n.get('global_surface') for n in d['nodes'])


def test_strip_pattern_detector(summary):
    assert summary['OLD_COMPACT']['STRIP_EDGE_COUNT']==64
    assert summary['NEW_STRIP']['STRIP_EDGE_COUNT']==8
    assert summary['STRIP_EDGE_REDUCTION']>=.70


def test_feature_builder(graph):
    for node in graph['nodes']:
        p=OUT/'05_backend_recovery'/node['part_id']
        spec=load(p/'measured_cad_spec.json')
        assert spec['source']=='GEOMETRY_ANALYZER_ONLY' and spec['operations']
        assert (p/'deterministic_cad_program.py').is_file() and (p/'reconstructed.step').is_file()


def test_mac_api_audit(summary):
    audit=load(OUT/'05_backend_recovery/CADPART_000/mac/mac_audit.json')
    assert summary['MAC_API_AVAILABLE'] is True
    assert summary['MAC_USED'] is True and summary['MAC_RUNS']==1 and summary['LLM_CALLS']==4
    assert audit['success'] is True and audit['provider_request_sent'] and audit['provider_response_received']
    assert audit['MAC_PARTS']==['CADPART_000'] and audit['raw_obj_received'] is False and audit['old_step_received'] is False


def test_mac_only_receives_measured_spec(graph):
    for node in graph['nodes']:
        d=load(OUT/'05_backend_recovery'/node['part_id']/'measured_cad_spec.json')
        assert d['raw_obj_read_by_builder'] is False
        if node['part_id']=='CADPART_000':
            assert d['MAC_USED'] is True and d['MAC_SKIPPED_REASON'] is None
            assert Path(d['MAC_OUTPUT_STEP']).is_file()
        else:
            assert d['MAC_USED'] is False


def test_freeform_global_fit():
    d=load(OUT/'05_backend_recovery/CADPART_000/measured_cad_spec.json')
    assert d['operations'][0]['operation']=='GLOBAL_LOFT'
    assert d['operations'][0]['SECTION_COUNT_USED']==14


def test_no_faceted_step(summary):
    assert summary['NEW_FACES']==92
    assert summary['NEW_FACES']<1000 and summary['BSPLINE_FACES']>0
    assert summary['NEW_FACES']/140164<.01


def test_part_brep_valid(summary):
    assert len(summary['part_qa'])==8
    assert all(row['BREP_VALID'] for row in summary['part_qa'])


def test_geometry_qa(summary):
    assert summary['GEOM_Q']=='Q1'
    assert summary['CHAMFER']<=.01 and summary['P95']<=.02 and summary['COVERAGE02']>=.95


def test_structural_qa(summary):
    assert summary['CAD_STRUCTURE_Q']=='PASS'
    assert summary['FEATURE_COUNT']>=2 and summary['SURFACE_GROUP_COUNT']>=3


def test_xcaf_assembly(summary):
    d=load(OUT/'07_assembly/assembly_manifest.json')
    assert d['XCAF_ASSEMBLY_PRESENT'] is True
    assert d['FINAL_COMPONENT_COUNT']==summary['FINAL_COMPONENT_COUNT']==8


def test_final_step_reload(summary):
    reader=STEPControl_Reader();assert reader.ReadFile(str(FINAL))==IFSelect_RetDone
    roots=reader.TransferRoots();shape=reader.OneShape()
    assert roots>=1 and not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid()
    assert summary['FINAL_STEP_RELOAD'] is True and summary['FINAL_BREP_VALID'] is True


def test_true_edge_render():
    for name in ('new_smooth_shaded.png','new_true_edges.png','source_vs_old_vs_new.png'):
        path=OUT/'artifacts'/name;assert path.is_file() and path.stat().st_size>10000


def test_part_graph_figure():
    path=OUT/'02_cad_part_graph/cad_part_graph.png';assert path.is_file() and path.stat().st_size>10000


def test_source_coverage(summary): assert summary['COVERAGE02']>=.98


def test_meaningful_part_count(summary): assert summary['CAD_PART_COUNT']>=4 and len(summary['CAD_PART_LABELS'])==8


def test_feature_boundary_recall(summary): assert summary['FEATURE_BOUNDARY_RECALL']>=.95


def test_sharp_edge_recall(summary): assert summary['SHARP_EDGE_RECALL']>=.80


def test_final_output_paths():
    assert FINAL.is_file() and (OUT/'07_assembly/CASE09_aircraft_final.glb').is_file()
    assert (OUT/'report.md').is_file()
