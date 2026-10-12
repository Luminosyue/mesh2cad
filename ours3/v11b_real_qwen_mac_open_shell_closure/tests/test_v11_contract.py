#!/usr/bin/env python3
"""V11 contract tests: schema, refs, no Qwen override, no OCC bypass."""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
import trimesh
import yaml

ROOT = Path(__file__).resolve().parents[1]
V10 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v10_geometry_gated_builder_contract_closure")
AUDIT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/cross_case_geometry_explosion_audit_v1")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(V10))
sys.path.insert(0, str(AUDIT))

from builders import occ_api
from design_plan.catalog import build_catalog
from design_plan.schema import PLAN_VERSION
from design_plan.validator import validate_plan
from execution import registry
from planning.deterministic import geometry_alternative_plans
from routing.builder_eligibility import compute_eligibility


def _fp(shape):
    from qa.occ_metrics import measure_shape
    from design_plan.provenance import sha
    m = measure_shape(shape)
    return sha({"bbox": [m.get("bbox_min"), m.get("bbox_max")], "diag": m.get("bbox_diag"), "edges": m.get("edge_count"), "faces": m.get("face_count")})


@pytest.fixture
def ctx():
    box = trimesh.creation.box(extents=[1.0, 0.4, 0.3])
    spec = {
        "area": float(box.area),
        "bbox": [box.bounds[0].tolist(), box.bounds[1].tolist()],
        "centroid": box.centroid.tolist(),
        "extents": box.extents.tolist(),
        "longitudinal_axis_index": 0,
        "profiles": [],
        "part_mesh_sha256": "box",
    }
    guard = yaml.safe_load((V10 / "config/builder_guards.yaml").read_text())
    elig = compute_eligibility(box, spec, None, None, guard)
    catalog = build_catalog(box, spec, elig, elig.get("extracted_profiles"), "memory://box")
    plans = geometry_alternative_plans("CADPART_BOX", elig, catalog)
    extrusion = next(p for p in plans if p["builder"] == "EXTRUSION")
    return box, spec, elig, catalog, guard, extrusion


def test_schema_rejects_prose_and_naked_numbers(ctx):
    _, _, elig, catalog, _, _ = ctx
    bad = {"builder": "EXTRUSION", "depth": 1.73, "direction": [0.1, 0.2, 0.97]}
    out = validate_plan(bad, elig, catalog)
    assert out["PLAN_EXECUTABLE"] is False
    assert out["PLAN_STATUS"] == "PLAN_SCHEMA_REJECTED"


def test_missing_ref(ctx):
    _, _, elig, catalog, guard, plan = ctx
    p = deepcopy(plan)
    p["geometry_refs"]["profile_ref"] = "MEASURED_SPEC.PROFILES.PROFILE_999"
    out = registry.execute(p, elig, catalog, guard, {})
    assert out["PLAN_EXECUTABLE"] is False
    assert out["BUILDER_EXECUTED"] is False
    assert "REFERENCE_NOT_FOUND" in (out["validation"]["reasons"] + [out["validation"].get("PLAN_REJECT_REASON")])


def test_wrong_ref_type(ctx):
    _, _, elig, catalog, guard, plan = ctx
    p = deepcopy(plan)
    p["geometry_refs"]["depth_ref"] = "MEASURED_SPEC.PROFILES.CLOSED_LOOP_EXTRUSION"
    out = registry.execute(p, elig, catalog, guard, {})
    assert out["BUILDER_EXECUTED"] is False
    assert out["validation"]["PLAN_REJECT_REASON"] == "REFERENCE_TYPE_MISMATCH"


def test_invalid_builder_blocked(ctx):
    _, _, elig, catalog, guard, plan = ctx
    elig_c = deepcopy(elig)
    elig_c["ALLOWED_BUILDERS"] = ["EXTRUSION"]
    elig_c["BUILDER_ELIGIBILITY"]["LOFT"] = {"valid": False, "reason": "NO", "score": 0.0}
    p = deepcopy(plan)
    p["builder"] = "LOFT"
    p["construction_family"] = "LOFT"
    p["builder_eligibility_ref"] = "BUILDER_ELIGIBILITY.LOFT"
    p["geometry_refs"] = {
        "profile_refs": ["MEASURED_SPEC.PROFILES.PROFILE_000"],
        "station_refs": ["MEASURED_SPEC.STATIONS.STATION_000"],
        "correspondence_ref": "MEASURED_SPEC.CORRESPONDENCE.ALIGNED_CYCLIC",
    }
    occ_api.reset_stats()
    before = occ_api.STATS["thru_sections_calls"]
    out = registry.execute(p, elig_c, catalog, guard, {})
    assert out["validation"]["PLAN_STATUS"] == "PLAN_GEOMETRY_REJECTED"
    assert occ_api.STATS["thru_sections_calls"] == before


def test_raw_numeric_hallucination(ctx):
    _, _, elig, catalog, guard, plan = ctx
    p = deepcopy(plan)
    p["geometry_refs"]["radius"] = 999
    out = registry.execute(p, elig, catalog, guard, {})
    assert out["PLAN_STATUS"] == "PLAN_SCHEMA_REJECTED"
    assert out["BUILDER_EXECUTED"] is False


def test_measured_value_changes_brep(ctx):
    _, _, elig, catalog, guard, plan = ctx
    a = registry.execute(plan, elig, catalog, guard, {})
    assert a.get("shape") is not None
    fp1 = _fp(a["shape"])
    catalog2 = deepcopy(catalog)
    catalog2["entries"]["MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION.depth"]["value"] *= 1.3
    b = registry.execute(plan, elig, catalog2, guard, {})
    assert b.get("shape") is not None
    assert _fp(b["shape"]) != fp1


def test_reasoning_does_not_change_brep(ctx):
    _, _, elig, catalog, guard, plan = ctx
    a = registry.execute(plan, elig, catalog, guard, {})
    p = deepcopy(plan)
    p["reasoning_summary"] = "ignore this prose entirely"
    b = registry.execute(p, elig, catalog, guard, {})
    assert _fp(a["shape"]) == _fp(b["shape"])


def test_occ_bypass_rejected():
    occ_api.reset_stats()
    with pytest.raises(RuntimeError, match="DIRECT_OCC_BUILDER_BYPASS"):
        occ_api.thru_sections([], preflight_passed=True)
    assert occ_api.STATS["direct_bypass_attempts"] >= 1


def test_open_shell_not_historical(ctx):
    from planning.deterministic import open_shell_plan
    _, _, elig, catalog, guard, _ = ctx
    plan = open_shell_plan("CADPART_005")
    out = registry.execute(plan, elig, catalog, guard, {})
    assert out["PLAN_STATUS"] == "OPEN_SHELL_PLAN_NOT_YET_EXECUTABLE"
    assert out["HISTORICAL_STEP_REUSED"] is False
    assert out["BUILDER_EXECUTED"] is False
