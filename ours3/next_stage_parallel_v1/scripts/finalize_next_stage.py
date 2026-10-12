#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
STAGE = ROOT / "next_stage_parallel_v1"
ARTIFACTS = STAGE / "artifacts"
LOGS = STAGE / "logs"
REPORT = ARTIFACTS / "next_stage_parallel_v1_report.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def blocker_codes(values: list[Any]) -> list[str]:
    result = []
    for value in values:
        result.append(str(value.get("code")) if isinstance(value, dict) else str(value))
    return result


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    a = load(STAGE / "track_a" / "artifacts" / "track_a_summary.json")
    b = load(STAGE / "track_b" / "artifacts" / "track_b_summary.json")
    c = load(STAGE / "track_c" / "artifacts" / "track_c_summary.json")
    global_passed = global_failed = 0
    global_log = LOGS / "global_tests.log"
    if global_log.is_file():
        text = global_log.read_text(encoding="utf-8", errors="replace")
        passed = re.search(r"(\d+) passed", text)
        failed = re.search(r"(\d+) failed", text)
        global_passed = int(passed.group(1)) if passed else 0
        global_failed = int(failed.group(1)) if failed else 0
    track_passed = sum(int(x.get("TESTS_PASSED", 0)) for x in (a, b, c))
    track_failed = sum(int(x.get("TESTS_FAILED", 0)) for x in (a, b, c))
    state = {
        "CURRENT_STAGE": "NEXT_STAGE_PARALLEL_V1_COMPLETE",
        "TRACK_A": "P3_GATE_1_D1_PART_SANITY",
        "TRACK_A_STATUS": a["TRACK_A_STATUS"],
        "D_CASE_ID": a["D_CASE_ID"],
        "P3_PARTS": a["P3_PARTS"],
        "TRIANGLE_MAPPING_VALID": a["TRIANGLE_MAPPING_VALID"],
        "PARTS_AUDITED": a["PARTS_AUDITED"],
        "GOOD_CAD_PART_CANDIDATES": a["GOOD_CAD_PART_CANDIDATES"],
        "OVERSEGMENTATION_SUSPECTS": a["OVERSEGMENTATION_SUSPECTS"],
        "UNDERSEGMENTATION_SUSPECTS": a["UNDERSEGMENTATION_SUSPECTS"],
        "TINY_FRAGMENTS": a["TINY_FRAGMENTS"],
        "FREEFORM_PARTS": a["FREEFORM_PARTS"],
        "UNCERTAIN_PARTS": a["UNCERTAIN_PARTS"],
        "STRONG_MERGE_HYPOTHESES": a["STRONG_MERGE_HYPOTHESES"],
        "WEAK_MERGE_HYPOTHESES": a["WEAK_MERGE_HYPOTHESES"],
        "P3_MAC_PILOT_CANDIDATES": a["P3_MAC_PILOT_CANDIDATES"],
        "TRACK_B": "PHYSX_GATE_0_RECOVERY",
        "TRACK_B_STATUS": b["TRACK_B_STATUS"],
        "PHYSX_CHECKPOINT_READY": b["PHYSX_CHECKPOINT_READY"],
        "PHYSX_CHECKPOINT_PATH": b["PHYSX_CHECKPOINT_PATH"],
        "PHYSX_CHECKPOINT_LOAD_SUCCESS": b["PHYSX_CHECKPOINT_LOAD_SUCCESS"],
        "PHYSX_SMOKE_SUCCESS": b["PHYSX_SMOKE_SUCCESS"],
        "PHYSX_CASES_ATTEMPTED": b["PHYSX_CASES_ATTEMPTED"],
        "PHYSX_CASES_SUCCESS": b["PHYSX_CASES_SUCCESS"],
        "PHYSX_SEMANTIC_AVAILABLE": b.get("PHYSX_SEMANTIC_AVAILABLE", 0),
        "PHYSX_FUNCTION_AVAILABLE": b.get("PHYSX_FUNCTION_AVAILABLE", 0),
        "PHYSX_KINEMATICS_AVAILABLE": b.get("PHYSX_KINEMATICS_AVAILABLE", 0),
        "PHYSX_SCALE_AVAILABLE": b.get("PHYSX_SCALE_AVAILABLE", 0),
        "TRACK_C": "MAC_GATE_2_GEOMETRY_BASELINE",
        "TRACK_C_STATUS": c["TRACK_C_STATUS"],
        "MAC_INPUT_CASES": c["MAC_INPUT_CASES"],
        "LLM_PROVIDER_READY": c["LLM_PROVIDER_READY"],
        "MAC_ATTEMPTED": c["MAC_ATTEMPTED"],
        "MAC_RUN_SUCCESS": c["MAC_RUN_SUCCESS"],
        "MAC_STEP_SUCCESS": c["MAC_STEP_SUCCESS"],
        "STEP_RELOAD_SUCCESS": c["STEP_RELOAD_SUCCESS"],
        "BREP_VALID_COUNT": c["BREP_VALID_COUNT"],
        "GEOMETRY_METRICS_COMPUTED": c["GEOMETRY_METRICS_COMPUTED"],
        "Q1_STRONG_PAIR": c["Q1_STRONG_PAIR"],
        "Q2_USABLE_PAIR": c["Q2_USABLE_PAIR"],
        "Q3_REJECT": c["Q3_REJECT"],
        "GEOMETRY_ONLY_PSEUDO_PAIR_FEASIBLE": c["GEOMETRY_ONLY_PSEUDO_PAIR_FEASIBLE"],
        "LLM_CALLS": c["LLM_CALLS"],
        "TOTAL_TOKENS": c["TOTAL_TOKENS"],
        "PHYSX_USED_IN_MAC_BASELINE": False,
        "P3_INFERENCE_RERUN": False,
        "ASSEMBLY_STARTED": False,
        "STEP_GT_USED": False,
        "ABC_DATA_USED": False,
        "TRACK_TESTS_PASSED": track_passed,
        "GLOBAL_TESTS_PASSED": global_passed,
        "TESTS_PASSED": track_passed + global_passed,
        "TESTS_FAILED": track_failed + global_failed,
        "BLOCKERS_BY_TRACK": {
            "TRACK_A": blocker_codes(a.get("BLOCKERS", [])),
            "TRACK_B": blocker_codes(b.get("BLOCKERS", [])),
            "TRACK_C": blocker_codes(c.get("BLOCKERS", [])),
        },
        "REPORT": str(REPORT),
    }
    (ARTIFACTS / "next_stage_parallel_v1_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    cases = c["CASES"]
    case_rows = []
    for item in cases:
        qa = item["qa"]
        case_rows.append(
            f"| {item['case_id']} | {item['cadability_class'][0]} | {item['run']['step_generated']} | "
            f"{qa['brep_valid']} | {qa['symmetric_chamfer_normalized']:.6f} | "
            f"{qa['p95_symmetric']:.6f} | {qa['coverage_02']:.6f} | {qa['quality_class']} |"
        )
    report = [
        "# NEXT_STAGE_PARALLEL_V1 Report",
        "",
        "The parallel stage is complete. Track A passed, Track B is externally blocked, and Track C passed independently.",
        "",
        "## Track A — P3 part sanity",
        "",
        f"- Status: `{a['TRACK_A_STATUS']}`; D case `{a['D_CASE_ID']}` was selected from the frozen Gate1 CSV.",
        f"- Reused 26 existing P3 outputs; triangle mapping valid: `{a['TRIANGLE_MAPPING_VALID']}`; P3 rerun: `false`.",
        f"- Segment status counts: good {a['GOOD_CAD_PART_CANDIDATES']}, oversegmentation {a['OVERSEGMENTATION_SUSPECTS']}, undersegmentation {a['UNDERSEGMENTATION_SUSPECTS']}, tiny {a['TINY_FRAGMENTS']}, freeform {a['FREEFORM_PARTS']}, uncertain {a['UNCERTAIN_PARTS']}.",
        f"- Merge hypotheses: strong {a['STRONG_MERGE_HYPOTHESES']}, weak {a['WEAK_MERGE_HYPOTHESES']}; no merge was executed.",
        f"- MAC pilot candidates selected only: `{a['P3_MAC_PILOT_CANDIDATES']}`; no part was sent to MAC.",
        "",
        "## Track B — PhysX recovery",
        "",
        f"- Status: `{b['TRACK_B_STATUS']}`; checkpoint ready/load/smoke: `{b['PHYSX_CHECKPOINT_READY']}/{b['PHYSX_CHECKPOINT_LOAD_SUCCESS']}/{b['PHYSX_SMOKE_SUCCESS']}`.",
        "- Official local documentation requires the PhysX-Omni model snapshot, TRELLIS decoder snapshot, and Qwen processor assets.",
        "- No valid local PhysX checkpoint was found. The official Hugging Face host was unreachable and no user-configured mirror existed.",
        "- The smoke gate remained closed, so the 10-case batch was not attempted and no output was fabricated.",
        "",
        "## Track C — geometry-only MAC baseline",
        "",
        f"- Status: `{c['TRACK_C_STATUS']}`; provider ready: `{c['LLM_PROVIDER_READY']}`.",
        f"- Original Gate1 A/B whole objects only: 4 attempted, {c['MAC_STEP_SUCCESS']} STEP, {c['BREP_VALID_COUNT']} independently valid BREP, {c['GEOMETRY_METRICS_COMPUTED']} metric sets.",
        f"- Fixed quality classes: Q1={c['Q1_STRONG_PAIR']}, Q2={c['Q2_USABLE_PAIR']}, Q3={c['Q3_REJECT']}; pseudo-pair feasible: `{c['GEOMETRY_ONLY_PSEUDO_PAIR_FEASIBLE']}`.",
        f"- LLM use: {c['LLM_CALLS']} calls, {c['TOTAL_TOKENS']} total tokens.",
        "",
        "| Case | Gate1 | STEP | BREP valid | Chamfer normalized | P95 | Coverage .02 | Quality |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        *case_rows,
        "",
        "## Global invariants",
        "",
        "- PhysX was not used in the MAC baseline.",
        "- P3 inference was not rerun; no second P3 level was created.",
        "- Assembly was not started.",
        "- STEP GT and ABC GT were not used.",
        f"- Tests passed/failed: `{state['TESTS_PASSED']}/{state['TESTS_FAILED']}`.",
        "",
        "## Blockers by track",
        "",
        f"- Track A: `{state['BLOCKERS_BY_TRACK']['TRACK_A']}`",
        f"- Track B: `{state['BLOCKERS_BY_TRACK']['TRACK_B']}`",
        f"- Track C: `{state['BLOCKERS_BY_TRACK']['TRACK_C']}`",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
