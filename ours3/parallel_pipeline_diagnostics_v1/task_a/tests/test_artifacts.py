import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1/task_a")
ART = ROOT / "artifacts"


def load_summary(): return json.loads((ART / "task_a_summary.json").read_text())
def load_manifest(): return json.loads((ART / "input_manifest.json").read_text())


def test_gate_and_case_count():
    s = load_summary(); assert s["TASK_A_STATUS"] == "PASS"; assert s["CASES_AUDITED"] == 6


def test_latest_classes_are_present_and_semantic():
    s = load_summary()
    for case in ("02", "03", "04", "05", "08", "09"):
        assert s[f"CASE{case}_STRUCTURAL_CLASS"] in {
            "COMPACT_STRUCTURED", "COMPACT_BUT_SPLINE_DERIVED", "FRAGMENTED_SPLINE_BREP",
            "ANALYTIC_FEATURE_BREP", "UNKNOWN"}
    assert s["CASE03_STRUCTURAL_CLASS"] == "ANALYTIC_FEATURE_BREP"
    assert s["CASE04_STRUCTURAL_CLASS"] == "FRAGMENTED_SPLINE_BREP"


def test_exact_version_matrix():
    slots = load_manifest()["VERSION_SLOTS"]
    expected_missing = {("CASE_02","v1_compact"), ("CASE_02","v2_feature_preserving"),
                        ("CASE_03","v1_compact"), ("CASE_08","v1_compact"),
                        ("CASE_08","v2_feature_preserving")}
    for case, versions in slots.items():
        for version in ("baseline", "v1_compact", "v2_feature_preserving"):
            assert (versions[version]["status"] == "NOT_AVAILABLE") == ((case, version) in expected_missing)


def test_every_artifact_has_five_nonempty_pngs():
    s = load_summary(); assert s["ARTIFACTS_AUDITED"] == 14
    for item in s["ALL_ARTIFACT_RESULTS"]:
        d = Path(item["OUTPUT_DIR"])
        for name in ("smooth_shaded.png", "true_brep_edges.png", "surface_type_colored.png",
                     "surface_group_colored.png", "strip_edge_overlay.png"):
            assert (d / name).stat().st_size > 1000


def test_surface_histograms_and_fresh_reload():
    s = load_summary()
    names = ("PLANE", "CYLINDER", "CONE", "SPHERE", "TORUS", "SURFACE_OF_REVOLUTION",
             "SURFACE_OF_EXTRUSION", "BSPLINE", "BEZIER", "OTHER")
    for item in s["ALL_ARTIFACT_RESULTS"]:
        m = json.loads((Path(item["OUTPUT_DIR"]) / "cad_structure_metrics.json").read_text())
        assert m["FRESH_RELOAD"] is True
        assert sum(m[f"{n}_FACES"] for n in names) == m["TOTAL_FACES"]
        assert m["TOTAL_FACES"] > 0 and m["TOTAL_EDGES"] > 0


def test_real_strip_detector_outputs():
    s = load_summary()
    for item in s["ALL_ARTIFACT_RESULTS"]:
        m = json.loads((Path(item["OUTPUT_DIR"]) / "cad_structure_metrics.json").read_text())
        assert "TopoDS_Edge" in m["STRIP_DETECTOR"]
        assert 0 <= m["STRIP_EDGE_RATIO"] <= 1
        assert m["STRIP_REGION_COUNT"] >= 0


def test_read_only_fingerprints_and_no_model_calls():
    s = load_summary(); assert s["CASE09_TOUCHED"] is False
    assert s["MAC_CALLS"] == 0 and s["LLM_CALLS"] == 0
    for item in s["ALL_ARTIFACT_RESULTS"]:
        m = json.loads((Path(item["OUTPUT_DIR"]) / "cad_structure_metrics.json").read_text())
        assert m["INPUT_UNCHANGED"] is True
        assert m["INPUT_FINGERPRINT_BEFORE"] == m["INPUT_FINGERPRINT_AFTER"]


def test_contact_sheet_and_report():
    s = load_summary()
    assert Path(s["STRUCTURE_CONTACT_SHEET"]).stat().st_size > 10000
    assert Path(s["REPORT_PATH"]).stat().st_size > 500
