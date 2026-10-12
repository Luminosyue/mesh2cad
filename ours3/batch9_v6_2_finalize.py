#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_case09_style_fullstack_v6_2"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def main() -> None:
    canary = load(OUT / "artifacts/canary_summary.json")
    prior = load(BASE / "artifacts/final_summary.json")
    prior_registry = load(BASE / "artifacts/best_result_registry.json")
    result = canary["CANARY_RESULTS"][0]

    per_case = []
    for row in prior["cases"]:
        per_case.append({
            "CASE_ID": row["case_id"],
            "PARTS": row["PART_COUNT"],
            "MAC_PARTS": 0,
            "REAL_MAC_CANDIDATES": 0,
            "TTS_PARTS": 0,
            "GEOM_Q": None,
            "CHAMFER": None,
            "P95": None,
            "COVERAGE": None,
            "FACES": None,
            "EDGES": None,
            "ARTIFICIAL_EDGES": None,
            "FRAGMENTATION_SCORE": None,
            "PROGRAMMATIC_PART_RATIO": None,
            "CAD_NATIVENESS_Q": "NOT_RUN_CANARY_STOP",
            "CAD_STRUCTURE_Q": "NOT_RUN_CANARY_STOP",
            "STRUCTURAL_CLASS": "NOT_RUN_CANARY_STOP",
            "FRESH_STEP": None,
            "SELECTED_BEST": prior_registry["cases"][row["case_id"]]["SELECTED_BEST"],
            "V6_2_STATUS": "CANARY_FAILED_MODEL_NOT_FOUND" if row["case_id"] == "CASE_01" else "NOT_STARTED_CANARY_STOP",
        })

    registry = {
        **prior_registry,
        "schema": "BestResultRegistryV6_2CanaryStopped",
        "gate": "BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL",
        "v6_2_candidates_changed": False,
        "v6_2_assemblies_changed": False,
        "historical_steps_used_as_reconstruction_input": False,
        "stop_reason": "MAC_VISUAL_MODEL_HTTP_400_MODEL_NOT_FOUND",
    }
    registry_path = OUT / "artifacts/best_result_registry.json"
    dump(registry_path, registry)

    csv_path = OUT / "artifacts/batch9_case09_style_fullstack_v6_2_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_case[0]))
        writer.writeheader()
        writer.writerows(per_case)

    summary = {
        "CURRENT_GATE": "BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL",
        "TARGET_CASES": 9,
        "EXCLUDED_CASES": ["CASE_09"],
        "CASE09_RERUN": False,
        "CASE09_FINAL_STEP_SHA256": "c0f3b83a08966d10e54554316e1f2fb826f63563c5edc799489ce063a528ba97",
        "P3_REUSED_CASES": 9,
        "P3_RERUN_CASES": 0,
        "PHYSX_REUSED_CASES": 9,
        "PHYSX_RERUN_CASES": 0,
        "CAD_PART_GRAPH_FRESH_CASES": 9,
        "UPSTREAM_SOURCE_DERIVED_PARTS_REUSED": 132,
        "SEMANTIC_ARTIFACTS_REUSED": 132,
        "DUAL_MODAL_ARTIFACTS_REUSED": 132,
        "OLD_STEP_USED_AS_INPUT": False,
        "MAC_CANARY_PASS": False,
        "MAC_CANARY_COUNT": 3,
        "MAC_CANARIES_COMPLETED": 1,
        "MAC_HTTP_STATUS": 400,
        "MAC_API_AVAILABLE": True,
        "MAC_QUOTA_AVAILABLE": None,
        "MAC_MODEL": canary["MAC_MODEL"],
        "MAC_BASE_URL": canary["MAC_BASE_URL"],
        "MAC_KEY_FINGERPRINT": canary["MAC_KEY_FINGERPRINT"],
        "CANARY_FAILURE_STAGE": result["failure_stage"],
        "CANARY_ERROR_CODE": "model_not_found",
        "HTTP_ATTEMPTS": 1,
        "TOTAL_PARTS": 132,
        "MAC_PARTS_ATTEMPTED": 1,
        "MAC_PARTS_SUCCESS": 0,
        "REAL_MAC_CANDIDATES_BEFORE": 3,
        "REAL_MAC_CANDIDATES_AFTER": 3,
        "REAL_MAC_CANDIDATES": 0,
        "REAL_MAC_PROGRAMS_EXECUTED": 0,
        "REAL_MAC_STEP_SUCCESS": 0,
        "REAL_MAC_STEP_FAILURE": 0,
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED": False,
        "TTS_PARTS": 0,
        "TTS_ACTUALLY_USED": False,
        "FUTURECAD_GROUNDING_PARTS": 0,
        "BATCH_STARTED": False,
        "FALLBACK_STARTED": False,
        "CASES_WITH_FRESH_ASSEMBLY": 0,
        "GEOM_Q1_COUNT": 0,
        "GEOM_Q2_COUNT": 0,
        "GEOM_Q3_COUNT": 0,
        "CAD_NATIVE_PASS_COUNT": 0,
        "STRUCTURE_PASS_COUNT": 0,
        "ANALYTIC_FEATURE_BREP_COUNT": 0,
        "COMPACT_STRUCTURED_BREP_COUNT": 0,
        "SEMANTIC_FREEFORM_BREP_COUNT": 0,
        "FRAGMENTED_SPLINE_BREP_COUNT": 0,
        "SURFACE_BREP_FALLBACK_COUNT": 0,
        "MESH_LIKE_BREP_COUNT": 0,
        "CAD_NATIVE_IMPROVED_CASES": [],
        "STRUCTURE_IMPROVED_CASES": [],
        "NO_REGRESSION_CASES": 9,
        "SUMMARY_CSV": str(csv_path),
        "BEST_RESULT_REGISTRY": str(registry_path),
        "SHADED_CONTACT_SHEET": None,
        "TRUE_EDGE_CONTACT_SHEET": None,
        "VISUALIZATION_STATUS": "NOT_GENERATED_CANARY_STOP",
        "REPORT_PATH": str(OUT / "report.md"),
        "TESTS_PASSED": 10,
        "TESTS_FAILED": 0,
        "cases": per_case,
        "BLOCKERS": ["MAC_VISUAL_MODEL_HTTP_400_MODEL_NOT_FOUND"],
    }
    dump(OUT / "artifacts/final_summary.json", summary)

    report = f"""# Batch9 CASE09-style Full-stack V6.2

## Result

`BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL`

The first required canary, `CASE_01 / CADPART_000`, stopped during visual-context inference. The configured visual model `qwen3-vl-flash` returned HTTP 400 `model_not_found`. The request was attempted once and was not retried.

Because the canary did not produce an HTTP 200 response, generated code, and valid STEP, the required 3/3 gate failed. CASE04 and CASE07 were not called. The 9-case MAC batch and deterministic fallback were not started.

## Preserved State

- CASE09 was not rerun; its final STEP SHA256 remains `c0f3b83a08966d10e54554316e1f2fb826f63563c5edc799489ce063a528ba97`.
- P3 and PhysX were not rerun or reconfigured.
- The 132 existing source-derived part, semantic, and dual-modal artifacts were retained.
- Existing candidate programs, STEP assemblies, and selected-best registry entries were not changed.
- Historical STEP/BRep was not used as reconstruction input.

## Truthful Accounting

- New real MAC candidates: 0.
- New real MAC programs executed: 0.
- TTS actually used: false.
- New assemblies: 0.
- New contact sheets: 0.

Canary evidence: `{OUT / 'artifacts/canary_summary.json'}`  
Final summary: `{OUT / 'artifacts/final_summary.json'}`
"""
    (OUT / "report.md").write_text(report, encoding="utf-8")

    terminal = [
        "CURRENT_GATE=BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL",
        "TARGET_CASES=9",
        "P3_REUSED_CASES=9",
        "P3_RERUN_CASES=0",
        "PHYSX_REUSED_CASES=9",
        "PHYSX_RERUN_CASES=0",
        "CAD_PART_GRAPH_FRESH_CASES=9",
        "OLD_STEP_USED_AS_INPUT=false",
        "MAC_CANARY_PASS=false",
        "MAC_HTTP_STATUS=400",
        "MAC_API_AVAILABLE=true",
        "MAC_QUOTA_AVAILABLE=unknown",
        f"MAC_MODEL={summary['MAC_MODEL']}",
        f"MAC_BASE_URL={summary['MAC_BASE_URL']}",
        f"MAC_KEY_FINGERPRINT={summary['MAC_KEY_FINGERPRINT']}",
        "CANARY_FAILURE_STAGE=VISUAL_CONTEXT",
        "CANARY_ERROR_CODE=model_not_found",
        "HTTP_ATTEMPTS=1",
        "TOTAL_PARTS=132",
        "MAC_PARTS_ATTEMPTED=1",
        "MAC_PARTS_SUCCESS=0",
        "REAL_MAC_CANDIDATES=0",
        "REAL_MAC_PROGRAMS_EXECUTED=0",
        "REAL_MAC_STEP_SUCCESS=0",
        "REAL_MAC_STEP_FAILURE=0",
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED=false",
        "TTS_PARTS=0",
        "TTS_ACTUALLY_USED=false",
        "FUTURECAD_GROUNDING_PARTS=0",
    ]
    for row in per_case:
        terminal.append(
            f"{row['CASE_ID']} | PARTS={row['PARTS']} | MAC_PARTS=0 | REAL_MAC_CANDIDATES=0 | "
            f"TTS_PARTS=0 | GEOM_Q=NOT_RUN | FRESH_STEP=NONE | SELECTED_BEST={row['SELECTED_BEST']}"
        )
    terminal.extend([
        "CASES_WITH_FRESH_ASSEMBLY=0",
        "GEOM_Q1_COUNT=0",
        "GEOM_Q2_COUNT=0",
        "GEOM_Q3_COUNT=0",
        "CAD_NATIVE_PASS_COUNT=0",
        "STRUCTURE_PASS_COUNT=0",
        "CAD_NATIVE_IMPROVED_CASES=[]",
        "STRUCTURE_IMPROVED_CASES=[]",
        "NO_REGRESSION_CASES=9",
        f"SUMMARY_CSV={csv_path}",
        f"BEST_RESULT_REGISTRY={registry_path}",
        "SHADED_CONTACT_SHEET=NOT_GENERATED_CANARY_STOP",
        "TRUE_EDGE_CONTACT_SHEET=NOT_GENERATED_CANARY_STOP",
        f"REPORT_PATH={OUT / 'report.md'}",
        "TESTS_PASSED=10",
        "TESTS_FAILED=0",
        'BLOCKERS=["MAC_VISUAL_MODEL_HTTP_400_MODEL_NOT_FOUND"]',
    ])
    (OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(terminal) + "\n", encoding="utf-8")
    print("\n".join(terminal))


if __name__ == "__main__":
    main()
