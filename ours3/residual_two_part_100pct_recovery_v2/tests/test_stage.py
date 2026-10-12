import csv
import hashlib
import json
from pathlib import Path

import numpy as np

OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
ROOT = OURS3 / "residual_two_part_100pct_recovery_v2"
V1 = OURS3 / "full_object_cad_recovery_v1"
TARGETS = ("CADPART_008", "CADPART_010")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def summary():
    return load(ROOT / "artifacts/summary.json")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def reports():
    return {cid: load(ROOT / cid / "final_recovery_report.json") for cid in TARGETS}


def test_only_failed_parts_processed():
    assert {p.name for p in ROOT.glob("CADPART_*") if p.is_dir()} == set(TARGETS)


def test_25_old_components_frozen():
    manifest = load(ROOT / "audit/frozen_v1_manifest.json")
    assert manifest["frozen_component_count"] == 25
    for component in manifest["components"]:
        for record in component["files"]:
            assert sha(record["path"]) == record["sha256"]


def test_failed_part_source_accounting():
    for cid in TARGETS:
        source = np.load(V1 / "parts" / cid / "source_triangle_ids.npy")
        final = np.load(ROOT / cid / "source_triangle_ids.npy")
        assert np.array_equal(source, final)


def test_failure_audit_exists():
    required = {"PREVIOUS_BACKENDS_ATTEMPTED", "BEST_PREVIOUS_CHAMFER", "BEST_PREVIOUS_P95", "BEST_PREVIOUS_COVERAGE02", "BREP_VALID", "FAILURE_STAGE", "FAILURE_REASON"}
    for cid in TARGETS:
        assert required <= set(load(ROOT / "audit" / cid / "failure_audit.json"))


def test_diagnostic_visualizations():
    names = ("source_part.png", "surface_curvature.png", "sharp_edges.png", "cross_sections.png", "previous_best_overlay.png", "failure_diagnostic_contact_sheet.png")
    for cid in TARGETS:
        assert all((ROOT / "audit" / cid / name).is_file() for name in names)


def test_local_decomposition_only():
    assert summary()["LOCAL_DECOMPOSITION_USED"] is False and summary()["NEW_SUBPART_COUNT"] == 0


def test_sweep_backend():
    for cid in TARGETS:
        names = {x["candidate"] for x in load(ROOT / "audit" / cid / "failure_audit.json")["preflight_candidates"]}
        assert "SWEEP_PIPE" in names


def test_mixed_feature_backend():
    for cid in TARGETS:
        names = {x["candidate"] for x in load(ROOT / "audit" / cid / "failure_audit.json")["preflight_candidates"]}
        assert "MIXED_FEATURE_PARAMETRIC" in names


def test_surface_brep_v2():
    assert all(x["final_backend"] == "ANALYTIC_SURFACE_BREP_ADAPTIVE_PATCH_V2" for x in reports().values())


def test_analytic_priority():
    for cid in TARGETS:
        audit = load(ROOT / "audit" / cid / "failure_audit.json")
        assert audit["analytic_first"] is True and audit["nurbs_used"] is False


def test_boundary_constrained_nurbs():
    for cid in TARGETS:
        candidates = load(ROOT / "audit" / cid / "failure_audit.json")["preflight_candidates"]
        record = next(x for x in candidates if x["candidate"] == "BOUNDARY_CONSTRAINED_NURBS")
        assert record["status"] == "FALLBACK_NOT_NEEDED"


def test_no_unsafe_surface_shift():
    assert all(x["surface_shift_applied"] is False for x in reports().values())


def test_open_shell_handling():
    assert all(x["expected_topology_type"] == "COMPOUND" for x in reports().values())


def test_q_thresholds_unchanged():
    assert summary()["CADPART_008_FINAL_QUALITY"] == "S1_SURFACE_BREP_ACCEPTED"
    assert summary()["CADPART_010_FINAL_QUALITY"] == "S1_SURFACE_BREP_ACCEPTED"


def test_s1_threshold_unchanged():
    for record in reports().values():
        metrics = record["metrics"]
        assert metrics["brep_valid"] and metrics["symmetric_chamfer_normalized"] <= 0.03 and metrics["p95_symmetric"] <= 0.07 and metrics["coverage_02"] >= 0.80


def test_no_mesh_fake_cad():
    for record in reports().values():
        assert record["faceted_triangle_brep"] is False and record["source_mesh_embedded"] is False and record["minimum_source_triangles_per_patch"] >= 30


def test_candidate_limit():
    assert all(x["candidate_configurations_attempted"] <= 12 for x in reports().values())


def test_subpart_union_coverage():
    for cid in TARGETS:
        meta = load(ROOT / cid / "final/surface_patch_segmentation.json")
        assert meta["assigned_source_triangle_count"] == meta["source_triangle_count"] == meta["unique_source_triangle_count"]


def test_transform_roundtrip():
    for cid in TARGETS:
        matrix = np.asarray(load(ROOT / cid / "final/transform.json")["CANONICAL_TO_SOURCE"])
        assert np.allclose(matrix @ np.linalg.inv(matrix), np.eye(4), atol=1e-12)


def test_xcaf_reload():
    s = summary()
    assert s["ASSEMBLY_STEP_GENERATED"] and s["ASSEMBLY_STEP_RELOAD_SUCCESS"] and Path(s["ASSEMBLY_STEP_PATH"]).is_file()


def test_all_components_preserved():
    manifest = load(ROOT / "assembly/assembly_manifest.json")
    assert manifest["representation"] == "XCAF_ASSEMBLY" and manifest["independent_components"] and manifest["component_count"] == 27


def test_whole_object_geometry_qa():
    metrics = load(ROOT / "metrics/whole_object_geometry_qa.json")
    assert metrics["source_frame_direct_comparison"] and metrics["icp_used"] is False and metrics["sample_count_per_surface"] == 100000


def test_exact100_strict():
    s = summary()
    assert s["NEW_TOTAL_CAD_AREA_COVERAGE"] == 1.0 and s["FAILED_AREA_COVERAGE"] == 0.0 and s["EXACT_100_PERCENT_CAD_COVERAGE"] is True


def test_source_accounting_strict():
    accounting = load(ROOT / "metrics/source_accounting.json")
    assert accounting["accounting"] == 1.0 and accounting["duplicate_count"] == 0 and accounting["missing_count"] == 0


def test_coverage_partition():
    s = summary()
    assert abs(s["Q1_AREA_COVERAGE"] + s["Q2_AREA_COVERAGE"] + s["S1_AREA_COVERAGE"] + s["FAILED_AREA_COVERAGE"] - 1.0) < 1e-12


def test_no_p3():
    assert summary()["NEW_P3_RUNS"] == 0


def test_no_physx():
    assert summary()["NEW_PHYSX_RUNS"] == 0


def test_no_mac():
    assert summary()["NEW_MAC_RUNS"] == 0


def test_no_llm():
    assert summary()["NEW_LLM_CAD_CALLS"] == 0


def test_no_step_gt_or_abc():
    assert summary()["STEP_GT_USED"] is False and summary()["ABC_DATA_USED"] is False


def test_final_visualizations():
    names = ("REAL_03_full_cad_v2_vs_source.png", "residual_008_010_before_after.png", "REAL_03_final_coverage_map.png")
    assert all((ROOT / "artifacts" / name).is_file() for name in names)


def test_glb_cad_only():
    manifest = load(ROOT / "assembly/glb_manifest.json")
    assert manifest["representation"] == "RECOVERED_CAD_TESSELLATION_ONLY" and manifest["source_residual_mesh_included"] is False and Path(manifest["path"]).is_file()


def test_gate_pass():
    assert summary()["CURRENT_GATE"] == "RESIDUAL_TWO_PART_100PCT_RECOVERY_V2_PASS"


def test_no_failed_parts():
    assert summary()["FAILED_PART_IDS"] == [] and summary()["BLOCKERS"] == []


def test_report_exists():
    assert (ROOT / "artifacts/residual_two_part_100pct_recovery_v2_report.md").is_file()
