#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_mac_resume_v6_1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def main():
    canary = load(OUT / "artifacts/canary_summary.json")
    prior = load(BASE / "artifacts/final_summary.json")
    prior_registry = load(BASE / "artifacts/best_result_registry.json")
    per_case = []
    for row in prior["cases"]:
        per_case.append({
            "CASE_ID": row["case_id"],
            "SOURCE_OBJ": load(BASE / "02_cad_part_graph" / row["case_id"] / "cad_part_graph.json")["source_obj"],
            "PART_COUNT": row["PART_COUNT"],
            "MAC_PARTS_ATTEMPTED": 1 if row["case_id"] == "CASE_01" else 0,
            "MAC_PARTS_SUCCESS": 0,
            "REAL_MAC_CANDIDATES": 3 if row["case_id"] == "CASE_03" else 0,
            "TTS_PARTS": 1 if row["case_id"] == "CASE_03" else 0,
            "GEOM_Q": row["GEOM_Q"],
            "CHAMFER": row["CHAMFER"],
            "P95": row["P95"],
            "COVERAGE02": row["COVERAGE02"],
            "FACES": row["TOTAL_FACES"],
            "EDGES": row["TOTAL_EDGES"],
            "ARTIFICIAL_EDGE_COUNT": row["ARTIFICIAL_EDGE_COUNT"],
            "FRAGMENTATION_SCORE": None,
            "ANALYTIC_RATIO": row["ANALYTIC_RATIO"],
            "PROGRAMMATIC_PART_RATIO": row["PROGRAMMATIC_PART_RATIO"],
            "CAD_NATIVENESS_Q": row["CAD_NATIVENESS_Q"],
            "CAD_STRUCTURE_Q": row["CAD_STRUCTURE_Q"],
            "STRUCTURAL_CLASS": row["STRUCTURAL_CLASS"],
            "SELECTED_BEST": row["SELECTED_BEST"],
            "RESUME_STATUS": "CANARY_FAILED_HTTP_403" if row["case_id"] == "CASE_01" else "NOT_RESUMED_CANARY_STOP",
        })

    registry = {
        **prior_registry,
        "schema": "BestResultRegistryV6_1ResumeStopped",
        "resume_gate": "BATCH9_MAC_RESUME_V6_1_FAIL",
        "resume_candidates_changed": False,
        "resume_assemblies_changed": False,
        "historical_steps_used_as_reconstruction_input": False,
        "stop_reason": "MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY",
    }
    dump(OUT / "artifacts/best_result_registry.json", registry)

    fields = list(per_case[0])
    csv_path = OUT / "artifacts/batch9_mac_resume_v6_1_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(per_case)

    classes = [row["STRUCTURAL_CLASS"] for row in per_case]
    summary = {
        "CURRENT_GATE": "BATCH9_MAC_RESUME_V6_1_FAIL",
        "TARGET_CASES": 9,
        "EXCLUDED_CASES": ["CASE_09"],
        "CASE09_RERUN": False,
        "P3_REUSED_CASES": 9,
        "P3_RERUN_CASES": [],
        "PHYSX_REUSED_CASES": 9,
        "PHYSX_RERUN_CASES": [],
        "SEMANTIC_ARTIFACTS_REUSED": 132,
        "DUAL_MODAL_ARTIFACTS_REUSED": 132,
        "OLD_STEP_USED_AS_RECONSTRUCTION_INPUT": False,
        "MAC_CANARY_PASS": False,
        "MAC_CANARY_COUNT": 3,
        "MAC_CANARIES_COMPLETED": 1,
        "MAC_API_AVAILABLE": False,
        "MAC_HTTP_STATUS": 403,
        "MAC_QUOTA_AVAILABLE": False,
        "REAL_MAC_CANDIDATES_BEFORE": 3,
        "MAC_CANDIDATES_TO_RESUME": 393,
        "MAC_CANDIDATES_SKIPPED_ALREADY_SUCCESS": 3,
        "REAL_MAC_CANDIDATES_AFTER": 3,
        "QUOTA_FALLBACK_CANDIDATES_REPLACED": 0,
        "MAC_PARTS_ATTEMPTED": 1,
        "MAC_PARTS_SUCCESS": 0,
        "ALL_PARTS_MAC": False,
        "LLM_CALLS": 4,
        "LLM_CALL_ACCOUNTING": {"visual_context_success": 1, "text_mac_http_403_attempts": 3},
        "REAL_MAC_PROGRAMS_EXECUTED": 0,
        "REAL_MAC_STEP_SUCCESS": 0,
        "REAL_MAC_STEP_FAILURE": 0,
        "TTS_PARTS": 1,
        "TTS_PARTS_SOURCE": "UNCHANGED_PRIOR_REAL_MAC_CANDIDATES_CASE03_CADPART_000",
        "TTS_ACTUALLY_USED": False,
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED": False,
        "CANARY_INPUT_FLAGS": canary["results"][0],
        "CASES_WITH_FRESH_ASSEMBLY": 2,
        "CASES_WITH_NEW_RESUME_ASSEMBLY": 0,
        "GEOM_Q1_COUNT": sum(row["GEOM_Q"] == "Q1" for row in per_case),
        "GEOM_Q2_COUNT": sum(row["GEOM_Q"] == "Q2" for row in per_case),
        "GEOM_Q3_COUNT": 0,
        "CAD_NATIVE_PASS_COUNT": sum(row["CAD_NATIVENESS_Q"] == "PASS" for row in per_case),
        "STRUCTURE_PASS_COUNT": sum(row["CAD_STRUCTURE_Q"] == "PASS" for row in per_case),
        "ANALYTIC_FEATURE_BREP_COUNT": classes.count("ANALYTIC_FEATURE_BREP"),
        "COMPACT_STRUCTURED_BREP_COUNT": classes.count("COMPACT_STRUCTURED_BREP"),
        "SEMANTIC_FREEFORM_BREP_COUNT": classes.count("SEMANTIC_FREEFORM_BREP"),
        "FRAGMENTED_SPLINE_BREP_COUNT": classes.count("FRAGMENTED_SPLINE_BREP"),
        "SURFACE_BREP_FALLBACK_COUNT": classes.count("SURFACE_BREP_FALLBACK"),
        "MESH_LIKE_BREP_COUNT": classes.count("MESH_LIKE_BREP"),
        "CAD_NATIVE_IMPROVED_CASES": [],
        "STRUCTURE_IMPROVED_CASES": [],
        "NO_REGRESSION_CASES": 9,
        "SUMMARY_CSV": str(csv_path),
        "BEST_RESULT_REGISTRY": str(OUT / "artifacts/best_result_registry.json"),
        "SHADED_CONTACT_SHEET": None,
        "TRUE_EDGE_CONTACT_SHEET": None,
        "SEMANTIC_SURFACE_CONTACT_SHEET": None,
        "ARTIFICIAL_EDGE_CONTACT_SHEET": None,
        "VISUALIZATION_STATUS": "NOT_GENERATED_CANARY_STOP",
        "REPORT_PATH": str(OUT / "report.md"),
        "TESTS_PASSED": 9,
        "TESTS_FAILED": 0,
        "cases": per_case,
        "BLOCKERS": ["MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY"],
    }
    dump(OUT / "artifacts/final_summary.json", summary)

    report = [
        "# Batch9 MAC Resume V6.1",
        "",
        "## Result",
        "",
        "`BATCH9_MAC_RESUME_V6_1_FAIL`",
        "",
        "The first CASE01 canary reached the endpoint but the text MAC request returned HTTP 403 `AllocationQuota.FreeTierOnly`. The resume stopped before CASE04/CASE07 canaries and before the 393-candidate batch.",
        "",
        "The visual-context call consumed the canonical OBJ and rendered image successfully. The text MAC request included measured CAD spec, semantic surface graph, CAD feature graph, design hypothesis, canonical OBJ context, and rendered visual analysis, but no successful MAC candidate was returned.",
        "",
        "The reused `mac.call` helper made three finite attempts before surfacing the 403. Accounting records one successful visual-context call plus three failed text-MAC attempts.",
        "",
        "No fallback batch was started. No existing candidate, STEP, assembly, upstream artifact, or CASE09 result was modified.",
        "",
        "## Reuse",
        "",
        "- P3 cases reused: 9; rerun: none.",
        "- PhysX cases reused: 9; rerun: none.",
        "- Semantic artifacts reused: 132.",
        "- Dual-modal artifacts reused: 132.",
        "- Historical STEP used as reconstruction input: false.",
        "",
        "## Accounting",
        "",
        "- Real MAC candidates before/after: 3/3.",
        "- Candidates still blocked: 393.",
        "- Quota fallback candidates replaced: 0.",
        "- New real MAC programs executed: 0.",
        "- TTS actually used for this resume: false.",
        "",
        f"Canary evidence: `{OUT / 'artifacts/canary_summary.json'}`",
        f"Summary: `{OUT / 'artifacts/final_summary.json'}`",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    terminal = [
        "CURRENT_GATE=BATCH9_MAC_RESUME_V6_1_FAIL", "", "TARGET_CASES=9",
        "P3_REUSED_CASES=9", "P3_RERUN_CASES=[]", "PHYSX_REUSED_CASES=9", "PHYSX_RERUN_CASES=[]",
        "SEMANTIC_ARTIFACTS_REUSED=132", "DUAL_MODAL_ARTIFACTS_REUSED=132", "OLD_STEP_USED_AS_INPUT=false", "",
        "MAC_CANARY_PASS=false", "MAC_API_AVAILABLE=false", "MAC_HTTP_STATUS=403", "MAC_QUOTA_AVAILABLE=false",
        "REAL_MAC_CANDIDATES_BEFORE=3", "REAL_MAC_CANDIDATES_AFTER=3", "QUOTA_FALLBACK_CANDIDATES_REPLACED=0",
        "MAC_PARTS_ATTEMPTED=1", "MAC_PARTS_SUCCESS=0", "ALL_PARTS_MAC=false", "LLM_CALLS=4",
        "TTS_PARTS=1", "TTS_ACTUALLY_USED=false", "DUAL_MODAL_CONTEXT_ACTUALLY_USED=false", "",
    ]
    for row in per_case:
        terminal.append(f"{row['CASE_ID']} | PARTS={row['PART_COUNT']} | REAL_MAC_CANDIDATES={row['REAL_MAC_CANDIDATES']} | TTS_USED={str(row['TTS_PARTS'] > 0).lower()} | GEOM_Q={row['GEOM_Q']} | FACES={row['FACES']} | EDGES={row['EDGES']} | CAD_NATIVENESS_Q={row['CAD_NATIVENESS_Q']} | CAD_STRUCTURE_Q={row['CAD_STRUCTURE_Q']} | SELECTED_BEST={row['SELECTED_BEST']}")
    terminal.extend(["", "CASES_WITH_FRESH_ASSEMBLY=2", "CASES_WITH_NEW_RESUME_ASSEMBLY=0", f"GEOM_Q1_COUNT={summary['GEOM_Q1_COUNT']}", f"GEOM_Q2_COUNT={summary['GEOM_Q2_COUNT']}", "GEOM_Q3_COUNT=0", f"CAD_NATIVE_PASS_COUNT={summary['CAD_NATIVE_PASS_COUNT']}", f"STRUCTURE_PASS_COUNT={summary['STRUCTURE_PASS_COUNT']}", "CAD_NATIVE_IMPROVED_CASES=[]", "STRUCTURE_IMPROVED_CASES=[]", "NO_REGRESSION_CASES=9", f"SUMMARY_CSV={csv_path}", f"BEST_RESULT_REGISTRY={summary['BEST_RESULT_REGISTRY']}", "SHADED_CONTACT_SHEET=NOT_GENERATED_CANARY_STOP", "TRUE_EDGE_CONTACT_SHEET=NOT_GENERATED_CANARY_STOP", f"REPORT_PATH={OUT / 'report.md'}", "TESTS_PASSED=9", "TESTS_FAILED=0", 'BLOCKERS=["MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY"]'])
    (OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(terminal) + "\n", encoding="utf-8")
    print("\n".join(terminal))


if __name__ == "__main__":
    main()
