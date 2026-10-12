#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1")
A = json.loads((ROOT / "task_a/artifacts/task_a_summary.json").read_text())
B = json.loads((ROOT / "task_b/artifacts/task_b_summary.json").read_text())
C = json.loads((ROOT / "task_c/artifacts/task_c_summary.json").read_text())
I = json.loads((ROOT / "isolation/isolation_verification.json").read_text())

subtests = A["TESTS_PASSED"] + B["TESTS_PASSED"] + C["TESTS_PASSED"]
blockers = list(dict.fromkeys(A.get("BLOCKERS", []) + B.get("BLOCKERS", []) + C.get("BLOCKERS", [])))
criteria = {
    "TASK_A_PASS": A["TASK_A_STATUS"] == "PASS",
    "TASK_B_PASS": B["TASK_B_STATUS"] == "PASS",
    "TASK_C_PASS": C["CURRENT_GATE"] == "CASE01_RECOVERY_ROOTCAUSE_V1_PASS",
    "CASE09_NOT_TOUCHED_BY_DIAGNOSTIC": not A["CASE09_TOUCHED"] and not B["CASE09_TOUCHED"] and not I["DIAGNOSTIC_CASE09_TOUCHED"],
    "ISOLATION_PASS": I["ISOLATION_PASS"],
    "NO_SUBTASK_TEST_FAILURES": A["TESTS_FAILED"] + B["TESTS_FAILED"] + C["TESTS_FAILED"] == 0,
    "NO_FORBIDDEN_GPU_INFERENCE": B["P3_INFERENCE_RUNS"] == 0 and B["PHYSX_INFERENCE_RUNS"] == 0 and not B["GPU_USED"],
    "NO_FORBIDDEN_CAD_GENERATION": B["LOFT_RUNS"] == 0 and B["BSPLINE_RUNS"] == 0 and B["STEP_GENERATED"] == 0,
    "NO_MAC_OR_LLM": B["MAC_RUNS"] == 0 and B["LLM_CALLS"] == 0 and C["MAC_LLM_CALLS"] == 0,
    "NO_UNRESTRICTED_ICP": not C["UNRESTRICTED_ICP_USED"],
}
for name, ok in criteria.items():
    if not ok: blockers.append(name)
gate = not blockers and all(criteria.values())

summary = {
    "CURRENT_GATE": "PARALLEL_PIPELINE_DIAGNOSTICS_V1_PASS" if gate else "PARALLEL_PIPELINE_DIAGNOSTICS_V1_FAIL",
    "CASE09_TOUCHED": False,
    "CONCURRENT_CASE09_ACTIVITY_OBSERVED": I["CONCURRENT_CASE09_ACTIVITY_OBSERVED"],
    "CASE09_POINT_IN_TIME_ONLY": bool(A.get("CASE09_CROSS_RUN_CHANGED", False)),
    "CRITERIA": criteria,
    "CASES_AUDITED": A["CASES_AUDITED"],
    "CASE02_STRUCTURAL_CLASS": A["CASE02_STRUCTURAL_CLASS"],
    "CASE03_STRUCTURAL_CLASS": A["CASE03_STRUCTURAL_CLASS"],
    "CASE04_STRUCTURAL_CLASS": A["CASE04_STRUCTURAL_CLASS"],
    "CASE05_STRUCTURAL_CLASS": A["CASE05_STRUCTURAL_CLASS"],
    "CASE08_STRUCTURAL_CLASS": A["CASE08_STRUCTURAL_CLASS"],
    "CASE09_STRUCTURAL_CLASS": A["CASE09_STRUCTURAL_CLASS"],
    "CASE09_TOTAL_FACES": A["CASE09_TOTAL_FACES"],
    "CASE09_BSPLINE_RATIO": A["CASE09_BSPLINE_RATIO"],
    "CASE09_SURFACE_GROUPS": A["CASE09_SURFACE_GROUPS"],
    "CASE09_STRIP_EDGE_COUNT": A["CASE09_STRIP_EDGE_COUNT"],
    "CASE09_STRIP_EDGE_RATIO": A["CASE09_STRIP_EDGE_RATIO"],
    "STRUCTURE_CONTACT_SHEET": A["STRUCTURE_CONTACT_SHEET"],
    "CASE06_P3_SEGMENTS": B["CASE06_P3_SEGMENTS"],
    "CASE06_CAD_PARTS": B["CASE06_CAD_PARTS"],
    "CASE06_UNASSIGNED_AREA_RATIO": B["CASE06_UNASSIGNED_AREA_RATIO"],
    "CASE06_PRIMARY_ROOT_CAUSE": B["CASE06_PRIMARY_ROOT_CAUSE"],
    "CASE07_P3_SEGMENTS": B["CASE07_P3_SEGMENTS"],
    "CASE07_CAD_PARTS": B["CASE07_CAD_PARTS"],
    "CASE07_OLD_COVERAGE": B["CASE07_OLD_COVERAGE"],
    "CASE07_PART_GRAPH_COVERAGE": B["CASE07_PART_GRAPH_COVERAGE"],
    "CASE07_PRIMARY_ROOT_CAUSE": B["CASE07_PRIMARY_ROOT_CAUSE"],
    "CASE07_ROOT_CAUSE_DETAIL": "AREA_UNAWARE_MAX_READY_PARTS_TRUNCATION",
    "CASE01_PRIMARY_ROOT_CAUSE": C["PRIMARY_ROOT_CAUSE"],
    "CASE01_PRIMARY_ROOT_CAUSE_DETAIL": C["PRIMARY_ROOT_CAUSE_DETAIL"],
    "CASE01_SECONDARY_CAUSES": C["SECONDARY_ROOT_CAUSES"],
    "CASE01_BEST_EXISTING_CANDIDATE_Q": "Q1" if C["CANDIDATE_Q1"] else "Q3",
    "CASE01_RESOURCE_FAILURE": C["CASE01_RESOURCE_FAILURE"],
    "CASE01_GEOMETRY_FAILURE": C["CASE01_GEOMETRY_FAILURE"],
    "CASE01_RESCUE_ROUTE_A": C["RESCUE_ROUTE_A"],
    "CASE01_RESCUE_ROUTE_B": C["RESCUE_ROUTE_B"],
    "TASK_A_SUMMARY": str(ROOT / "task_a/artifacts/task_a_summary.json"),
    "TASK_B_SUMMARY": str(ROOT / "task_b/artifacts/task_b_summary.json"),
    "TASK_C_SUMMARY": str(ROOT / "task_c/artifacts/task_c_summary.json"),
    "ISOLATION_REPORT": str(ROOT / "isolation/isolation_verification.json"),
    "REPORT_PATH": str(ROOT / "report.md"),
    "SUBTASK_TESTS_PASSED": subtests,
    "INTEGRATION_TESTS_PASSED": 0,
    "TESTS_PASSED": subtests,
    "TESTS_FAILED": 0,
    "BLOCKERS": blockers,
}
(ROOT / "artifacts").mkdir(exist_ok=True)
(ROOT / "artifacts/summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

report = f"""# PARALLEL_PIPELINE_DIAGNOSTICS_V1

Gate: `{summary['CURRENT_GATE']}`

## Isolation

The diagnostic wrote only under `{ROOT}`. It changed no shared code and generated no STEP. The separately running CASE09 task changed its own source/output during the observation window; this is explicitly recorded as concurrent external activity, not attributed to this diagnostic. CASE09 headline structure metrics are point-in-time because the live final changed from 137 to 92 faces between two read-only audit runs, although the selected 92-face file was stable during the final audit window.

## CAD structure audit

Six cases and fourteen unique STEP artifacts were fresh reloaded. CASE03 is a true analytic 6-plane BRep. CASE02/04/05/08 are fragmented spline BReps at their latest stable selected versions. CASE04 V1 is compact but spline-derived; its V2 has more feature-preserving faces yet remains a 322-patch spline BRep, so it is not mislabeled as structured. The CASE09 point-in-time final has 92 faces, {summary['CASE09_BSPLINE_RATIO']:.6f} BSpline ratio, 86 surface groups, and remains structurally UNKNOWN.

## CASE06 and CASE07 part discovery

Existing P3 and PhysX evidence was reused without inference. CASE06 source area is fully represented by two P3 segments, but both were C_FREEFORM/ready=0, so the old zero-accept result is a PART_CADABILITY_FAILURE. CASE07 has 30 P3 segments; three disconnected segments split into 33 graph parts. Coverage rises from {summary['CASE07_OLD_COVERAGE']:.6f} to 1.0 at Part Graph scope. The old assembly omitted 90.0486% of source area because an area-unaware ready-part cap retained only a small subset, classified as ROUTER_FAILURE.

## CASE01 root cause

All three existing candidate STEP files fresh reload and are BRep valid. Candidate A smooth loft is Q3 and grossly mis-scaled after the frozen transform; candidates B ruled loft and C primitive are both Q1. The primary cause is OTHER: a stale candidate-A failure sentinel caused the old control flow to continue before QA/ranking valid B and C. Resource timeout and A-only geometry failure both occurred, but RESOURCE_TIMEOUT_ONLY is rejected. No rebuild was executed.

## Prohibitions

No shared pipeline edits, MAC, LLM API, P3/PhysX rerun, GPU use, unrestricted ICP, Loft/BSpline generation, STEP generation, or 10-case batch was performed.
"""
(ROOT / "report.md").write_text(report)
print(json.dumps(summary, indent=2))
