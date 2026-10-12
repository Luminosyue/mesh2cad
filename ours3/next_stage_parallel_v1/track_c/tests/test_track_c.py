from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
TRACK = OURS3 / "next_stage_parallel_v1" / "track_c"
GATE1 = OURS3 / "mac_pipeline"


@pytest.fixture(scope="module")
def manifest():
    return json.loads((TRACK / "artifacts" / "track_c_manifest.json").read_text())


@pytest.fixture(scope="module")
def summary():
    return json.loads((TRACK / "artifacts" / "track_c_summary.json").read_text())


def test_mac_only_original_ab_cases(manifest):
    assert len(manifest["cases"]) == 4
    assert all(c["cadability_class"].startswith(("A_", "B_")) for c in manifest["cases"])


def test_exactly_one_a_pilot(manifest):
    assert sum(c["cadability_class"].startswith("A_") for c in manifest["cases"]) == 1
    assert manifest["cases"][0]["cadability_class"].startswith("A_")


def test_no_p3_parts_selected(manifest):
    assert manifest["whole_object_only"] is True
    assert all("part_" not in c["source_obj"] for c in manifest["cases"])


def test_geometry_baseline_no_physx(manifest, summary):
    assert manifest["prohibitions"]["physx_used"] is False
    assert summary["PHYSX_USED_IN_MAC_BASELINE"] is False


def test_geometry_baseline_no_p3(manifest, summary):
    assert manifest["prohibitions"]["p3_used"] is False
    assert summary["P3_INFERENCE_RERUN"] is False


def test_no_step_gt(manifest, summary):
    assert manifest["prohibitions"]["step_gt_used"] is False
    assert summary["STEP_GT_USED"] is False


def test_no_abc_gt(manifest, summary):
    assert manifest["prohibitions"]["abc_data_used"] is False
    assert summary["ABC_DATA_USED"] is False


def test_no_assembly(summary):
    assert summary["ASSEMBLY_STARTED"] is False


def test_gate1_spec_and_prompt_preserved(manifest):
    for c in manifest["cases"]:
        d = Path(c["case_dir"])
        assert (d / "cad_spec_v0_gate1_unchanged.json").read_bytes() == (GATE1 / "cases" / c["case_id"] / "cad_spec" / "cad_spec_v0.json").read_bytes()
        assert (d / "cad_prompt_v0_gate1_unchanged.txt").read_bytes() == (GATE1 / "cases" / c["case_id"] / "cad_spec" / "cad_prompt_v0.txt").read_bytes()


def test_geometry_analyzer_not_rerun(manifest):
    assert manifest["prohibitions"]["geometry_analyzer_rerun"] is False
    for c in manifest["cases"]:
        prov = json.loads((Path(c["case_dir"]) / "provenance.json").read_text())
        assert prov["geometry_analyzer"] == "GATE1_V0"


def test_canonical_bbox_diagonal(manifest):
    assert manifest["canonical_bbox_diagonal_mm"] == 100.0
    for c in manifest["cases"]:
        spec = json.loads((Path(c["case_dir"]) / "cad_spec_geometry_only_mac.json").read_text())
        ext = spec["object_geometry"]["bbox"]["extents"]
        assert sum(x * x for x in ext) ** 0.5 == pytest.approx(100.0)


def test_canonical_scale_roundtrip(manifest):
    for c in manifest["cases"]:
        assert c["mesh_to_cad_scale"] * c["cad_to_mesh_scale"] == pytest.approx(1.0)


def test_direction_vectors_not_scaled(manifest):
    for c in manifest["cases"]:
        d = Path(c["case_dir"])
        original = json.loads((d / "cad_spec_v0_gate1_unchanged.json").read_text())
        scaled = json.loads((d / "cad_spec_geometry_only_mac.json").read_text())
        assert scaled["base_feature"]["parameters"]["axis"] == original["base_feature"]["parameters"]["axis"]
        assert scaled["object_geometry"]["principal_axes"] == original["object_geometry"]["principal_axes"]


def test_prompt_variant_geometry_only(manifest):
    for c in manifest["cases"]:
        p = Path(c["mac_output_dir"]) / "input_prompt.txt"
        text = p.read_text()
        assert "PROMPT_VARIANT=GEOMETRY_ONLY" in text
        assert "PHYSX_USED=false" in text
        assert "P3_USED=false" in text


def test_provider_key_not_logged():
    audit = json.loads((TRACK / "artifacts" / "mac_repo_audit.json").read_text())
    assert audit["provider_secret_logged"] is False
    smoke = json.loads((TRACK / "artifacts" / "provider_smoke.json").read_text())
    assert "api_key" not in smoke


def test_provider_smoke_precedes_mac(manifest):
    smoke = TRACK / "artifacts" / "provider_smoke.json"
    assert smoke.exists()
    for c in manifest["cases"]:
        run = Path(c["mac_output_dir"]) / "mac_run_result.json"
        if run.exists():
            assert smoke.stat().st_mtime <= run.stat().st_mtime


def test_brep_validation_independent(summary):
    for c in summary["CASES"]:
        qa = c["qa"]
        if qa.get("step_reload_success"):
            assert "solid_count" in qa and "face_count" in qa


def test_step_retessellation_from_step(summary):
    for c in summary["CASES"]:
        if c["qa"].get("geometry_metrics_computed"):
            assert (TRACK / "cases" / c["case_id"] / "mac_output_geometry_only" / "generated_from_step.obj").exists()


def test_geometry_sample_budget(summary):
    for c in summary["CASES"]:
        if c["qa"].get("geometry_metrics_computed"):
            assert c["qa"]["sample_count_per_surface"] >= 50_000
            assert c["qa"]["sample_seed"] == 20260810


def test_no_icp_main_metric(manifest, summary):
    assert manifest["prohibitions"]["icp_used_for_main_metric"] is False
    assert all(not c["qa"].get("icp_used", False) for c in summary["CASES"])


def test_quality_thresholds_fixed(manifest):
    q = manifest["quality_thresholds"]
    assert q["Q1_STRONG_PAIR"] == {"chamfer_max": 0.01, "p95_max": 0.02, "coverage_02_min": 0.95}
    assert q["Q2_USABLE_PAIR"] == {"chamfer_max": 0.02, "p95_max": 0.05, "coverage_02_min": 0.85}


def test_quality_class_enum(summary):
    assert all(c["qa"]["quality_class"] in {"Q1_STRONG_PAIR", "Q2_USABLE_PAIR", "Q3_REJECT"} for c in summary["CASES"])


def test_summary_has_required_track_c_fields(summary):
    required = {
        "TRACK_C_STATUS", "MAC_INPUT_CASES", "LLM_PROVIDER_READY", "MAC_ATTEMPTED",
        "MAC_RUN_SUCCESS", "MAC_STEP_SUCCESS", "STEP_RELOAD_SUCCESS", "BREP_VALID_COUNT",
        "GEOMETRY_METRICS_COMPUTED", "Q1_STRONG_PAIR", "Q2_USABLE_PAIR", "Q3_REJECT",
        "GEOMETRY_ONLY_PSEUDO_PAIR_FEASIBLE", "LLM_CALLS", "TOTAL_TOKENS", "BLOCKERS",
    }
    assert required <= set(summary)


def test_track_c_status_criterion(summary):
    if summary["TRACK_C_STATUS"] == "PASS":
        assert summary["MAC_ATTEMPTED"] >= 1
        assert summary["MAC_STEP_SUCCESS"] >= 1
        assert summary["STEP_RELOAD_SUCCESS"] >= 1
        assert summary["GEOMETRY_METRICS_COMPUTED"] >= 1
