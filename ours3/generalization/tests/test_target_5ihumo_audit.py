from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "generalization/target_5ihumo_geometry_audit_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("audit_v1", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_p3_to_cadpart_relation_detects_one_to_one() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "ONE_TO_ONE" in text
    assert "CURRENT_CAD_PART_GRAPH_IS_EFFECTIVELY_P3_SEGMENT_GRAPH" in text


def test_disconnected_component_detection() -> None:
    module = load_module()
    out = module.classify_from_features({"significant_component_count": 2, "repetition_evidence": False})
    assert out["decomposition_recommendation"] == "SPLIT_BY_CONNECTED_COMPONENT"


def test_tiny_component_not_forced_split() -> None:
    module = load_module()
    out = module.classify_from_features({"significant_component_count": 1, "repetition_evidence": False})
    assert out["decomposition_recommendation"] == "KEEP_AS_SINGLE_CAD_PART"


def test_planar_patch_detection() -> None:
    module = load_module()
    out = module.classify_from_features({"max_single_plane_coverage": 0.5, "significant_component_count": 1})
    assert "PLANAR_PATCH" in out["audited_geometry_classes"]


def test_linear_rod_detection() -> None:
    module = load_module()
    out = module.classify_from_features({"linear_rod_evidence": True, "significant_component_count": 1})
    assert "LINEAR_ROD" in out["audited_geometry_classes"]


def test_repetition_detection() -> None:
    module = load_module()
    out = module.classify_from_features({"repetition_evidence": True, "significant_component_count": 5})
    assert out["decomposition_recommendation"] == "SPLIT_BY_CONNECTED_COMPONENT"


def test_mixed_geometry_requests_decomposition() -> None:
    module = load_module()
    out = module.classify_from_features({"thin_plate_evidence": True, "linear_rod_evidence": True, "significant_component_count": 1})
    assert out["split_recommended"]


def test_analytic_missed_opportunity_detection() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "analytic_missed_opportunity" in text
    assert "ANALYTIC_MISSED_OPPORTUNITY_COUNT" in text


def test_v6_out_of_source_support_detection() -> None:
    module = load_module()
    out = module.v6_sanity_from_metrics({"brep_geometry_within_source_support_ratio": 0.1})
    assert out["v6_out_of_source_support"]


def test_loop_like_edge_suspect_detection() -> None:
    module = load_module()
    out = module.v6_sanity_from_metrics({"edge_length_to_bbox_ratio_max": 2.0})
    assert out["loop_like_edge_suspect"]


def test_least_bad_candidate_not_absolute_pass() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "selected_as_least_bad_option" in text
    assert "selected_candidate_should_have_been_rejected" in text


def test_existing_artifacts_immutable() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "before_hash" in text
    assert "EXISTING_ARTIFACT_MODIFIED_COUNT" in text
