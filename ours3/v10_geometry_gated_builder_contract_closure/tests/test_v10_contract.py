#!/usr/bin/env python3
"""V10 contract tests: eligibility, plan validator, fail-fast OCC, counterfactuals A–F."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest
import trimesh
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from builders import occ_api
from routing import builder_registry as registry
from builders.control_net_guard import audit_control_net
from builders.preflight import grid_preflight, loft_preflight
from builders.profiles import extract_profiles
from design_intent.plan_validator import validate_plan
from routing.builder_eligibility import compute_eligibility


@pytest.fixture
def guard_cfg():
    return yaml.safe_load((ROOT / "config/builder_guards.yaml").read_text())


@pytest.fixture
def box():
    return trimesh.creation.box(extents=[1.0, 0.4, 0.3])


@pytest.fixture
def spec(box):
    return {
        "area": float(box.area),
        "bbox": [box.bounds[0].tolist(), box.bounds[1].tolist()],
        "centroid": box.centroid.tolist(),
        "extents": box.extents.tolist(),
        "longitudinal_axis_index": 0,
        "profiles": [],
    }


def test_yaml_has_no_case_ids():
    text = (ROOT / "config/builder_guards.yaml").read_text()
    assert "CASE_" not in text


def test_occ_apis_only_in_occ_api():
    banned = ("BRepOffsetAPI_" + "ThruSections", "GeomAPI_" + "PointsToBSplineSurface")
    for path in ROOT.rglob("*.py"):
        if path.name == "occ_api.py" or "tests" in path.parts:
            continue
        text = path.read_text()
        for token in banned:
            assert token not in text, f"{token} in {path}"


def test_qwen_cannot_override_invalid_loft(box, spec, guard_cfg):
    elig = compute_eligibility(box, spec, None, None, guard_cfg)
    elig["BUILDER_ELIGIBILITY"]["LOFT"] = {"valid": False, "reason": "PROFILE_CORRESPONDENCE_INVALID", "score": 0.0}
    elig["ALLOWED_BUILDERS"] = [b for b in elig["ALLOWED_BUILDERS"] if b != "LOFT"] or ["EXTRUSION"]
    occ_api.reset_stats()
    out = registry.execute({"builder": "GLOBAL_LOFT", "CANDIDATE_SOURCE": "QWEN_PLAN"}, box, elig, spec, guard_cfg, {})
    assert out["validation"]["PLAN_EXECUTABLE"] is False
    assert out["executed"] is False
    assert occ_api.STATS["thru_sections_calls"] == 0


def test_valid_construction_can_execute(box, spec, guard_cfg):
    elig = compute_eligibility(box, spec, None, None, guard_cfg)
    occ_api.reset_stats()
    family = "LOFT" if "LOFT" in elig["ALLOWED_BUILDERS"] else "EXTRUSION"
    out = registry.execute({"builder": family, "CANDIDATE_SOURCE": "QWEN_PLAN", "sections": 8, "profile_count": 8}, box, elig, spec, guard_cfg, {})
    assert out.get("executed") is True
    assert out.get("shape") is not None


def test_corrupt_correspondence_blocks_preflight(box, spec, guard_cfg):
    extracted = extract_profiles(box, 8, 8)
    extracted["profiles_uv"][2] = extracted["profiles_uv"][2][::-1]
    pre = loft_preflight(extracted, float(np.linalg.norm(box.extents)), guard_cfg)
    assert pre["LOFT_PREFLIGHT_PASS"] is False
    occ_api.reset_stats()
    before = occ_api.STATS["thru_sections_calls"]
    from builders.loft_builder import execute as loft_execute
    counters = {}
    part_bbox = {
        "bbox_min": box.bounds[0].tolist(),
        "bbox_max": box.bounds[1].tolist(),
        "bbox_diag": float(np.linalg.norm(box.extents)),
    }
    out = loft_execute(box, {"sections": 8, "profile_count": 8}, part_bbox, guard_cfg, counters, extracted=extracted)
    assert out["executed"] is False
    assert occ_api.STATS["thru_sections_calls"] == before


def test_control_net_rejects_before_face(box, spec, guard_cfg):
    elig = compute_eligibility(box, spec, None, None, guard_cfg)
    poles = np.zeros((5, 5, 3))
    poles[0, 0] = [90, 90, 90]
    cnet = audit_control_net(poles, elig["part_bbox"], elig["part_bbox"], guard_cfg)
    assert cnet["BSPLINE_CONTROL_NET_REJECTED"] is True
    occ_api.reset_stats()
    with pytest.raises(RuntimeError, match="CONTROL_NET_GUARD_REJECTED_BUT_FACE_CREATED"):
        occ_api.make_face_from_surface(None, control_net_passed=False)
    assert occ_api.STATS["make_face_after_bspline"] == 0


def test_unmeasured_qwen_depth_not_consumed(box, spec, guard_cfg):
    elig = compute_eligibility(box, spec, None, None, guard_cfg)
    out = registry.execute({"builder": "EXTRUSION", "depth": 99999, "CANDIDATE_SOURCE": "QWEN_PLAN"}, box, elig, spec, guard_cfg, {})
    assert out["validation"]["PLAN_EXECUTABLE"] is False
    assert out["validation"]["UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT"] == 0
    assert out["executed"] is False


def test_geometry_alternative_is_independent(box, spec, guard_cfg):
    elig = compute_eligibility(box, spec, None, None, guard_cfg)
    elig_block = dict(elig)
    elig_block["BUILDER_ELIGIBILITY"] = dict(elig["BUILDER_ELIGIBILITY"])
    elig_block["BUILDER_ELIGIBILITY"]["LOFT"] = {"valid": False, "reason": "PROFILE_CORRESPONDENCE_INVALID", "score": 0.0}
    elig_block["ALLOWED_BUILDERS"] = [b for b in elig["ALLOWED_BUILDERS"] if b != "LOFT"] or ["EXTRUSION"]
    qwen = registry.execute({"builder": "GLOBAL_LOFT", "CANDIDATE_SOURCE": "QWEN_PLAN"}, box, elig_block, spec, guard_cfg, {})
    assert "EXTRUSION" in elig["ALLOWED_BUILDERS"]
    alt = registry.execute({"builder": "EXTRUSION", "CANDIDATE_SOURCE": "GEOMETRY_ALTERNATIVE"}, box, elig, spec, guard_cfg, {})
    assert qwen["executed"] is False
    assert qwen["CANDIDATE_SOURCE"] == "QWEN_PLAN"
    assert alt["CANDIDATE_SOURCE"] == "GEOMETRY_ALTERNATIVE"
    assert alt.get("shape") is not None


def test_thru_sections_requires_preflight():
    occ_api.reset_stats()
    with pytest.raises(RuntimeError, match="LOFT_PREFLIGHT_REJECTED_BUT_EXECUTED"):
        occ_api.thru_sections([], preflight_passed=False)
    assert occ_api.STATS["thru_sections_calls"] == 0


def test_direct_occ_bypass_detected():
    occ_api.reset_stats()
    with pytest.raises(RuntimeError,match="DIRECT_OCC_BUILDER_BYPASS_DETECTED"):
        occ_api.thru_sections([],preflight_passed=True)
    assert occ_api.STATS["direct_bypass_attempts"]==1


def test_pathological_grid_fails_preflight(guard_cfg):
    grid=np.zeros((6,6,3),float)
    for i in range(6):
        for j in range(6): grid[i,j]=[i*.1,j*.1,0]
    grid[2,3]=[80,80,80]
    assert grid_preflight(grid,guard_cfg,1.2)["BSPLINE_GRID_PREFLIGHT_PASS"] is False
