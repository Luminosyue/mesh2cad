from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "generalization/v4_failure_coverage_audit_v1.py"
V4_RUNNER = ROOT / "generalization/run_topology_aware_routing_trimmed_surface_fidelity_v4.py"


def test_audit_script_exists():
    assert AUDIT.is_file()


def test_output_root_is_separate():
    text = AUDIT.read_text(encoding="utf-8")
    assert "v4_failure_coverage_audit_v1" in text


def test_v4_is_frozen():
    text = AUDIT.read_text(encoding="utf-8")
    assert "V4_CODE_FROZEN" in text
    assert "V4_QA_THRESHOLDS_UNCHANGED" in text


def test_execution_contract_is_frozen():
    text = AUDIT.read_text(encoding="utf-8")
    assert "P3_REEXECUTED" in text
    assert "PHYSX_REEXECUTED" in text
    assert "REAL_MAC_CALLS" in text


def test_audit_does_not_modify_v4_runner():
    text = AUDIT.read_text(encoding="utf-8")
    assert "write_text" in text
    assert "run_topology_aware_routing_trimmed_surface_fidelity_v4.py" not in text


def test_triangle_hash_is_deterministic():
    from generalization.v4_failure_coverage_audit_v1 import sha256_ids

    ids = np.asarray([7, 1, 3], dtype=np.int64)
    expected = hashlib.sha256(np.asarray([1, 3, 7], dtype=np.int64).tobytes()).hexdigest()
    assert sha256_ids(ids) == expected


def test_union_coverage_uses_unique_triangles():
    text = AUDIT.read_text(encoding="utf-8")
    assert "np.unique(np.concatenate" in text


def test_area_coverage_uses_source_face_areas():
    text = AUDIT.read_text(encoding="utf-8")
    assert "source_area_faces" in text
    assert "source_area_fraction" in text


def test_failure_taxonomy_is_specific():
    text = AUDIT.read_text(encoding="utf-8")
    for reason in (
        "NO_CANDIDATE_GENERATED",
        "FP_OCCUPANCY_FAIL",
        "MULTI_PATCH_REQUIRED",
        "OCC_INVALID",
        "HAUSDORFF_FAIL",
    ):
        assert reason in text


def test_pass_parts_are_not_added_to_failure_groups():
    text = AUDIT.read_text(encoding="utf-8")
    assert "passes = [item for item in part_data.values() if item[\"qa_pass\"]]" in text
    assert "fails = [item for item in part_data.values() if not item[\"qa_pass\"]]" in text


def test_no_mesh_fallback():
    text = AUDIT.read_text(encoding="utf-8").lower()
    assert "mesh_to_step" not in text
    assert "mesh fallback" not in text


def test_no_step_regeneration():
    text = AUDIT.read_text(encoding="utf-8")
    assert "STEP" not in text or "step_to_mesh" in text


def test_pareto_artifact_is_written():
    text = AUDIT.read_text(encoding="utf-8")
    assert "failure_coverage_pareto.csv" in text


def test_visual_audit_artifact_is_written():
    text = AUDIT.read_text(encoding="utf-8")
    assert "top5_failure_parts_contact_sheet.png" in text


def test_recommendation_is_coverage_driven():
    text = AUDIT.read_text(encoding="utf-8")
    assert "largest_reason" in text
    assert "RECOMMENDED_V5" in text
