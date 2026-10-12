from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
STAGE = ROOT / "next_stage_parallel_v1"
A = json.loads((STAGE / "track_a" / "artifacts" / "track_a_summary.json").read_text())
B = json.loads((STAGE / "track_b" / "artifacts" / "track_b_summary.json").read_text())
C = json.loads((STAGE / "track_c" / "artifacts" / "track_c_summary.json").read_text())
STATE = json.loads((STAGE / "artifacts" / "next_stage_parallel_v1_state.json").read_text())


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_tracks_are_independent():
    assert A["TRACK_A_STATUS"] == "PASS"
    assert B["TRACK_B_STATUS"] == "BLOCKED"
    assert C["TRACK_C_STATUS"] == "PASS"
    assert all((STAGE / f"track_{name}" / "artifacts" / f"track_{name}_summary.json").is_file() for name in "abc")


def test_no_step_gt():
    assert not A["STEP_GT_USED"] and not C["STEP_GT_USED"] and not STATE["STEP_GT_USED"]
    assert all(not item["qa"].get("step_gt_used", False) for item in C["CASES"])


def test_no_abc_gt():
    assert not A["ABC_DATA_USED"] and not C["ABC_DATA_USED"] and not STATE["ABC_DATA_USED"]


def test_p3_not_rerun():
    assert A["P3_REUSED_EXISTING_OUTPUT"] is True
    assert A["P3_INFERENCE_RERUN"] is False
    provenance = A["provenance"]
    assert sha256(Path(provenance["triangle_part_id"])) == provenance["triangle_part_id_sha256"]


def test_p3_triangle_mapping():
    labels = np.load(A["provenance"]["triangle_part_id"], allow_pickle=False)
    assert labels.shape == (385828,)
    assert labels.min() == 0 and labels.max() == 25
    assert len(np.unique(labels)) == 26
    assert A["TRIANGLE_MAPPING_VALID"] is True


def test_all_26_parts_audited():
    rows = read_csv(STAGE / "track_a" / "artifacts" / "p3_gate1_part_inventory.csv")
    assert len(rows) == A["PARTS_AUDITED"] == 26
    assert {int(row["PART_ID"]) for row in rows} == set(range(26))


def test_segment_status_enum():
    allowed = {"GOOD_CAD_PART_CANDIDATE", "OVERSEGMENTATION_SUSPECT", "UNDERSEGMENTATION_SUSPECT", "TINY_FRAGMENT", "FREEFORM_PART", "UNCERTAIN_PART"}
    rows = read_csv(STAGE / "track_a" / "artifacts" / "p3_gate1_part_inventory.csv")
    assert {row["PART_SEGMENT_STATUS"] for row in rows} <= allowed
    assert len(rows) == A["SEGMENT_STATUS_ASSIGNED"]


def test_merge_score_range():
    rows = read_csv(STAGE / "track_a" / "artifacts" / "p3_gate1_merge_hypotheses.csv")
    assert rows
    assert all(0.0 <= float(row["MERGE_SCORE"]) <= 1.0 for row in rows)
    assert {row["MERGE_HYPOTHESIS"] for row in rows} <= {"STRONG_MERGE_HYPOTHESIS", "WEAK_MERGE_HYPOTHESIS", "KEEP_SEPARATE"}


def test_undersegmentation_detection():
    rows = read_csv(STAGE / "track_a" / "artifacts" / "p3_gate1_part_inventory.csv")
    flagged = [row for row in rows if row["UNDERSEGMENTATION_SUSPECTED"] == "True"]
    assert len(flagged) == A["UNDERSEGMENTATION_SUSPECTS"] >= 1


def test_p3_pilot_selection_max_5():
    payload = json.loads((STAGE / "track_a" / "artifacts" / "p3_gate1_mac_pilot_candidates.json").read_text())
    assert 1 <= len(payload["candidates"]) <= 5
    assert len(payload["candidates"]) == A["P3_MAC_PILOT_CANDIDATES"]
    assert all(item["PART_SEGMENT_STATUS"] == "GOOD_CAD_PART_CANDIDATE" for item in payload["candidates"])
    assert payload["MAC_RUNS"] == 0


def test_physx_checkpoint_not_faked():
    assert B["TRACK_B_STATUS"] == "BLOCKED"
    assert B["PHYSX_CHECKPOINT_READY"] is False
    assert B["PHYSX_CHECKPOINT_PATH"] is None
    assert B["PHYSX_CHECKPOINT_LOAD_SUCCESS"] is False


def test_physx_smoke_before_batch():
    assert B["PHYSX_SMOKE_SUCCESS"] is False
    assert B["PHYSX_CASES_ATTEMPTED"] == 0
    gate = json.loads((STAGE / "track_b" / "artifacts" / "physx_batch_gate.json").read_text())
    assert gate["run_permitted"] is False


def test_physx_raw_output_preserved():
    assert B["PHYSX_RAW_OUTPUTS"] == 0
    assert B["PHYSX_UNDERSTANDING_OUTPUTS"] == 0
    assert B["PHYSX_SMOKE_ATTEMPTED"] is False
    assert not list((STAGE / "track_b").rglob("physx_raw_output.txt"))


def test_no_physx_mac_fusion_yet():
    assert B["FUSION_RUNS"] == 0 and B["MAC_RUNS"] == 0
    assert C["PHYSX_USED_IN_MAC_BASELINE"] is False


def test_mac_only_original_ab_cases():
    ids = {item["case_id"] for item in C["CASES"]}
    assert ids == {"REAL_02", "REAL_05", "REAL_06", "REAL_08"}
    assert all(item["cadability_class"].startswith(("A_", "B_")) for item in C["CASES"])
    assert C["MAC_INPUT_CASES"] == 4


def test_geometry_baseline_no_physx():
    for item in C["CASES"]:
        provenance = json.loads((STAGE / "track_c" / "cases" / item["case_id"] / "provenance.json").read_text())
        assert provenance["physx_used"] is False and provenance["prompt_variant"] == "GEOMETRY_ONLY"


def test_geometry_baseline_no_p3():
    assert C["P3_INFERENCE_RERUN"] is False
    for item in C["CASES"]:
        provenance = json.loads((STAGE / "track_c" / "cases" / item["case_id"] / "provenance.json").read_text())
        assert provenance["p3_used"] is False


def test_canonical_scale_roundtrip():
    for item in C["CASES"]:
        spec = json.loads((STAGE / "track_c" / "cases" / item["case_id"] / "cad_spec_geometry_only_mac.json").read_text())
        scale = spec["canonicalization"]
        assert math.isclose(scale["mesh_to_cad_scale"] * scale["cad_to_mesh_scale"], 1.0, rel_tol=1e-12)
        assert math.isclose(scale["source_bbox_diagonal_mesh_units"] * scale["mesh_to_cad_scale"], 100.0, rel_tol=1e-12)
        assert scale["physical_unit_inferred"] is False and scale["directions_scaled"] is False


def test_brep_validation_independent():
    script = (STAGE / "track_c" / "scripts" / "track_c_pipeline.py").read_text()
    assert "STEPControl_Reader" in script and "BRepCheck_Analyzer" in script
    for item in C["CASES"]:
        assert item["qa"]["step_reload_success"] is True
        assert item["qa"]["brep_valid"] is True


def test_no_icp_main_metric():
    assert all(item["qa"]["icp_used"] is False for item in C["CASES"])
    manifest = json.loads((STAGE / "track_c" / "artifacts" / "track_c_manifest.json").read_text())
    assert manifest["prohibitions"]["icp_used_for_main_metric"] is False


def test_quality_thresholds_fixed():
    script = (STAGE / "track_c" / "scripts" / "track_c_pipeline.py").read_text()
    assert 'metrics["symmetric_chamfer_normalized"] <= 0.01' in script
    assert 'metrics["p95_symmetric"] <= 0.02' in script
    assert 'metrics["coverage_02"] >= 0.95' in script
    assert 'metrics["symmetric_chamfer_normalized"] <= 0.02' in script
    assert 'metrics["p95_symmetric"] <= 0.05' in script
    assert 'metrics["coverage_02"] >= 0.85' in script


def test_geometry_metrics_sample_50000():
    assert C["GEOMETRY_METRICS_COMPUTED"] == 4
    assert all(item["qa"]["sample_count_per_surface"] >= 50000 for item in C["CASES"])
    assert len({item["qa"]["sample_seed"] for item in C["CASES"]}) == 1


def test_quality_counts_complete():
    assert C["Q1_STRONG_PAIR"] + C["Q2_USABLE_PAIR"] + C["Q3_REJECT"] == C["GEOMETRY_METRICS_COMPUTED"]
    assert C["GEOMETRY_ONLY_PSEUDO_PAIR_FEASIBLE"] is (C["Q1_STRONG_PAIR"] + C["Q2_USABLE_PAIR"] >= 1)


def test_provider_secret_not_logged():
    smoke = json.loads((STAGE / "track_c" / "artifacts" / "provider_smoke.json").read_text())
    assert smoke["api_key_present"] is True and smoke["connectivity_smoke_success"] is True
    assert "api_key" not in smoke and "token" not in smoke


def test_no_assembly_started():
    assert C["ASSEMBLY_STARTED"] is False and STATE["ASSEMBLY_STARTED"] is False


def test_no_second_p3_level_or_part_mac():
    assert not list((STAGE / "track_a").rglob("triangle_part_id.npy"))
    assert A["MULTI_AGENT_CAD_RUNS"] == 0


def test_frozen_source_hashes_unchanged():
    manifest = json.loads((ROOT / "mac_pipeline" / "artifacts" / "frozen_10_case_manifest.json").read_text())
    for entry in manifest["cases"].values():
        assert sha256(Path(entry["absolute_path"])) == entry["SHA256"]


def test_stage_state_matches_track_statuses():
    assert STATE["CURRENT_STAGE"] == "NEXT_STAGE_PARALLEL_V1_COMPLETE"
    assert STATE["TRACK_A_STATUS"] == A["TRACK_A_STATUS"]
    assert STATE["TRACK_B_STATUS"] == B["TRACK_B_STATUS"]
    assert STATE["TRACK_C_STATUS"] == C["TRACK_C_STATUS"]
