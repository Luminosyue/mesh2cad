import csv
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "batch_10_step_audit_sanity_fix_v2"
V1 = ROOT / "batch_10_step_quality_audit_v1"


def summary():
    return json.load((OUT / "artifacts/summary.json").open(encoding="utf-8"))


def rows():
    with (OUT / "metrics/provenance_and_geometry_qa.csv").open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_gate():
    assert summary()["CURRENT_GATE"] == "BATCH_10_STEP_AUDIT_SANITY_FIX_V2_PASS"


def test_case00_provenance_fixed():
    s = summary(); r = rows()[0]
    assert s["CASE00_PROVENANCE_BUG_CONFIRMED"]
    assert r["SOURCE_OBJ_PATH"].endswith("/meshes/30_CONSTRUCTION_SET.obj")
    assert r["STEP_PATH"].endswith("/batch_real_mesh2cad_v1/cases/CASE_00/assembly/REAL_03_partial_assembly.step")
    assert not r["STEP_PATH"].endswith("/negative_feature_topology_recovery_v1/assembly/REAL_03_full_cad_assembly_feature_fixed.step")


def test_only_case00_provenance_changed():
    assert summary()["CASES_WITH_PROVENANCE_CHANGE"] == ["CASE_00"]


def test_only_case00_topology_reaudited():
    s = summary(); assert s["TOPOLOGY_REAUDIT_CASES"] == ["CASE_00"] and s["TESSELLATIONS_RUN"] == 1


def test_exact_mapping_fields():
    required = ("CASE_ID", "SOURCE_OBJ_PATH", "SOURCE_OBJ_SHA256", "STEP_PATH", "STEP_SHA256", "STEP_PROVENANCE_FILE", "RECOVERY_BACKEND", "QUALITY_METRICS_SOURCE")
    for row in rows():
        assert all(row[key] for key in required if not (row["CASE_ID"] == "CASE_06" and key in ("STEP_PATH", "STEP_SHA256")))


def test_no_duplicate_steps():
    assert summary()["DUPLICATE_STEP_CASE_GROUPS"] == []


def test_equal_counts_are_different_geometry():
    data = json.load((OUT / "artifacts/duplicate_step_analysis.json").open(encoding="utf-8"))
    assert data["TARGET_RELATION"] == "SAME_TOPOLOGY_DIFFERENT_GEOMETRY"
    sigs = data["SIGNATURES"]
    assert len({x["STEP_SHA256"] for x in sigs.values()}) == 4
    assert len({x["VERTEX_COORDINATE_HASH"] for x in sigs.values()}) == 4
    assert len({(x["FACE_COUNT"], x["EDGE_COUNT"]) for x in sigs.values()}) == 1


def test_transform_bug_confirmed():
    s = summary(); assert s["GEOMETRY_QA_TRANSFORM_BUG"]
    assert s["GEOMETRY_QA_TRANSFORM_BUG_CASES"] == ["CASE_01", "CASE_02", "CASE_03", "CASE_04", "CASE_08", "CASE_09"]


def test_corrected_whole_object_quality_matches_batch():
    by_case = {r["CASE_ID"]: r for r in rows()}
    for cid in ("CASE_02", "CASE_03", "CASE_04", "CASE_08", "CASE_09"):
        r = by_case[cid]
        assert r["BATCH_GEOM_Q"] == r["V2_CORRECTED_GEOM_Q"] == "Q1"
        assert abs(float(r["BATCH_CHAMFER"]) - float(r["V2_CORRECTED_CHAMFER"])) < 0.00003


def test_v1_q3_not_formal_for_transform_cases():
    by_case = {r["CASE_ID"]: r for r in rows()}
    for cid in ("CASE_02", "CASE_03", "CASE_04", "CASE_08", "CASE_09"):
        assert by_case[cid]["V1_AUDIT_GEOM_Q"] == "Q3" and by_case[cid]["V2_CORRECTED_GEOM_Q"] == "Q1"


def test_case00_correct_scope_is_partial_vs_full():
    r = rows()[0]
    assert r["V2_CORRECTED_GEOM_Q"] == "Q3" and float(r["V2_CORRECTED_COVERAGE02"]) < 0.10
    assert "PARTIAL_ASSEMBLY" in r["QA_SCOPE_NEW"] and "FULL_SOURCE_OBJ" in r["QA_SCOPE_NEW"]


def test_representation_and_fidelity_separate():
    by_case = {r["CASE_ID"]: r for r in rows()}
    assert by_case["CASE_03"]["BREP_AUTHENTICITY"] == "COMPACT_TRUE_BREP"
    assert by_case["CASE_05"]["BREP_AUTHENTICITY"] == "FRAGMENTED_TRUE_BREP" and by_case["CASE_05"]["V2_CORRECTED_GEOM_Q"] == "Q1"


def test_no_icp():
    assert not summary()["UNRESTRICTED_ICP_USED"]
    assert all(r["UNRESTRICTED_ICP_USED"] == "False" and r["BATCH_ICP_USED"] == "False" for r in rows())


def test_report_and_artifacts():
    assert (OUT / "report.md").stat().st_size > 500
    assert (OUT / "manifest/exact_case_mapping.json").stat().st_size > 1000
    assert (OUT / "artifacts/duplicate_step_analysis.json").stat().st_size > 1000


def test_no_blockers():
    assert summary()["BLOCKERS"] == []
