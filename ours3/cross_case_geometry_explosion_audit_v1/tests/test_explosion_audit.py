#!/usr/bin/env python3
"""Unit tests for CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))

from failure_localization.first_explosion_locator import locate
from qa.geometry_explosion_guard import classify, evaluate_candidate, load_config
from qa.primitive_applicability import score_part


def test_yaml_has_no_case_ids():
    text = (ROOT / "config/geometry_explosion_guard.yaml").read_text(encoding="utf-8")
    for token in ("CASE_5IHUMO", "CASE_YC4XCA", "CASE09", "5iHumo", "yC4xca"):
        assert token not in text


def test_manifest_has_three_cases():
    manifest = json.loads((ROOT / "config/case_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["cases"]) >= 3
    roles = {c["role"] for c in manifest["cases"]}
    assert "audit_target" in roles and "reference" in roles


def test_guard_rejects_exploded_bbox():
    cfg = load_config(ROOT / "config/geometry_explosion_guard.yaml")
    source = {
        "SOURCE_BBOX_MIN": [-1, -1, -1],
        "SOURCE_BBOX_MAX": [1, 1, 1],
        "SOURCE_BBOX_DIAG": 3.464,
        "SOURCE_BBOX_VOLUME": 8.0,
    }
    occ = {
        "bbox_min": [-20, -20, -20],
        "bbox_max": [20, 20, 20],
        "bbox_diag": 69.28,
        "centroid": [0, 0, 0],
        "volume": 64000.0,
        "edge_lengths": [40.0, 0.1],
        "max_edge_length": 40.0,
        "edge_bboxes": [([-20, -20, -20], [20, 20, 20], 40.0)],
        "face_bboxes": [([-20, -20, -20], [20, 20, 20], 69.28, 80.0, 1.0)],
        "face_aspects": [80.0],
        "face_areas": [1.0],
        "max_face_bbox_diag": 69.28,
        "vertices": [[20, 20, 20], [-20, -20, -20]],
        "control_points": [[100, 0, 0]],
        "control_point_count": 1,
        "control_point_bbox": {"bbox_min": [-100, 0, 0], "bbox_max": [100, 0, 0], "bbox_diag": 200.0},
        "control_net_step_p95": 10.0,
        "control_net_step_max": 50.0,
        "pcurve_domain_error_count": 0,
        "entity_count": 4,
        "edge_count": 2,
        "face_count": 1,
    }
    result = evaluate_candidate(occ, source, cfg, part_bbox={"bbox_min": [-0.2, -0.2, -0.2], "bbox_max": [0.2, 0.2, 0.2], "bbox_diag": 0.69})
    assert result["GEOMETRY_EXPLOSION_STATUS"] == "REJECT"
    assert result["ELIGIBLE_FOR_BEST_AVAILABLE"] is False
    assert result["ELIGIBLE_FOR_TTS"] is False


def test_guard_passes_source_scale():
    cfg = load_config(ROOT / "config/geometry_explosion_guard.yaml")
    source = {
        "SOURCE_BBOX_MIN": [-1, -1, -0.2],
        "SOURCE_BBOX_MAX": [1, 1, 0.2],
        "SOURCE_BBOX_DIAG": 2.83,
        "SOURCE_BBOX_VOLUME": 0.8,
    }
    occ = {
        "bbox_min": [-1, -1, -0.2],
        "bbox_max": [1, 1, 0.2],
        "bbox_diag": 2.83,
        "centroid": [0, 0, 0],
        "volume": 0.8,
        "edge_lengths": [1.7, 0.4, 0.3],
        "max_edge_length": 1.7,
        "edge_bboxes": [([-1, -1, -0.2], [1, 0, 0], 1.7)],
        "face_bboxes": [([-1, -1, -0.2], [1, 1, 0.2], 2.83, 5.0, 0.5)],
        "face_aspects": [5.0],
        "face_areas": [0.5],
        "max_face_bbox_diag": 2.83,
        "vertices": [[1, 1, 0.2], [-1, -1, -0.2]],
        "control_points": [[0, 0, 0], [0.2, 0, 0]],
        "control_point_count": 2,
        "control_point_bbox": {"bbox_min": [-1, -1, -0.2], "bbox_max": [1, 1, 0.2], "bbox_diag": 2.83},
        "control_net_step_p95": 0.2,
        "control_net_step_max": 0.3,
        "pcurve_domain_error_count": 0,
        "entity_count": 6,
        "edge_count": 3,
        "face_count": 1,
    }
    result = evaluate_candidate(occ, source, cfg, part_bbox={"bbox_min": [-1, -1, -0.2], "bbox_max": [1, 1, 0.2], "bbox_diag": 2.83})
    assert result["GEOMETRY_EXPLOSION_STATUS"] in ("PASS", "WARNING")
    assert result["ELIGIBLE_FOR_BEST_AVAILABLE"] is True


def test_locator_finds_builder_stage():
    stages = {
        "STAGE_0_P3_SEGMENT": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_1_CAD_PART_AFTER_MERGE": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_2_GEOMETRY_ANALYZER": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_3_MEASURED_CAD_SPEC": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_4_SELECTED_PRIMITIVE": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_5_SEMANTIC_WIREFRAME": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_6_DESIGN_INTENT": {"GEOMETRY_EXPLOSION_STATUS": "PASS"},
        "STAGE_7_BUILDER_RAW_OUTPUT": {
            "GEOMETRY_EXPLOSION_STATUS": "REJECT",
            "CAD_BBOX_DIAG_RATIO": 12.0,
            "MAX_EDGE_LENGTH_RATIO": 8.0,
            "MAX_FACE_EXTENT_RATIO": 9.0,
            "GEOMETRY_EXPLOSION_REASONS": ["LONG_EDGE", "LOFT_DOMAIN_ERROR"],
            "COORDINATE_FRAME_DECLARATION": "SOURCE_GLOBAL",
            "SURFACE_DOMAIN_EXPLOSION": True,
        },
        "STAGE_8_TRIMMED_BREP": {"GEOMETRY_EXPLOSION_STATUS": "REJECT"},
        "STAGE_9_PARAMETER_OPTIMIZED": {"GEOMETRY_EXPLOSION_STATUS": "REJECT"},
        "STAGE_10_ASSEMBLY_PLACEMENT": {"GEOMETRY_EXPLOSION_STATUS": "REJECT"},
    }
    result = locate(stages, {"builder": "GLOBAL_LOFT", "profile_correspondence": {"LOFT_PREFLIGHT_PASS": False, "PROFILE_PAIR_CROSSING_COUNT": 9}})
    assert result["FIRST_EXPLOSION_STAGE"] == "STAGE_7_BUILDER_RAW_OUTPUT"
    assert result["PRIMARY_FAILURE_CLASS"] in ("LOFT_DOMAIN_ERROR", "PROFILE_CORRESPONDENCE_ERROR", "BSPLINE_CONTROL_NET_ERROR")


def test_no_silent_bspline_fallback():
    rng = np.random.default_rng(0)
    plane = np.column_stack([rng.normal(0, 1, 200), rng.normal(0, 1, 200), rng.normal(0, 0.001, 200)])
    scored = score_part(plane)
    assert scored["silent_general_bspline_fallback"] is False
    assert scored["selected"] != "GENERAL_BSPLINE" or scored["GENERAL_BSPLINE_SELECTED_BY_SCORE"]


def test_python_has_no_case_id_control_flow():
    for path in ROOT.rglob("*.py"):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        assert not re.search(r'if .*(CASE_5IHUMO|CASE_YC4XCA|CASE09)', text)


def test_reject_never_best_available():
    cfg = load_config(ROOT / "config/geometry_explosion_guard.yaml")
    metrics = {
        "CAD_BBOX_DIAG": 50.0,
        "CAD_BBOX_DIAG_RATIO": 20.0,
        "CAD_BBOX_VOLUME_RATIO": 80.0,
        "MAX_EDGE_LENGTH_RATIO": 12.0,
        "LONG_EDGE_COUNT": 10,
        "MAX_FACE_EXTENT_RATIO": 15.0,
        "HUGE_FACE_COUNT": 8,
        "EXTREME_ASPECT_RATIO_FACE_RATE": 0.5,
        "EXTREME_ASPECT_RATIO_FACE_COUNT": 8,
        "OUTSIDE_SOURCE_BBOX_FACE_RATE": 0.9,
        "OUTSIDE_SOURCE_BBOX_VERTEX_RATE": 0.9,
        "CONTROL_POINT_BBOX_DIAG_RATIO": 30.0,
        "CONTROL_NET_OUTLIER": True,
    }
    result = classify(metrics, cfg, part_diag=0.2)
    assert result["GEOMETRY_EXPLOSION_STATUS"] == "REJECT"
    assert result["ELIGIBLE_FOR_BEST_AVAILABLE"] is False
