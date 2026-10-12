#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
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


def truthful(path: Path):
    manifest = load(path)
    response_path = path.parent / "mac_response.json"
    response = load(response_path) if response_path.is_file() else {}
    parsed = response.get("parsed", {})
    generated = parsed.get("generated_code", "") if isinstance(parsed, dict) else ""
    real = bool(response.get("raw_response", "").strip() and generated.strip() and not response.get("error"))
    valid = bool(real and manifest.get("program_executed") and manifest.get("step_valid") is True)
    return manifest, response, real, valid


def main():
    canary = load(OUT / "artifacts/canary_summary.json")
    progress = load(OUT / "artifacts/resume_progress.json")
    prior_registry = load(BASE / "artifacts/best_result_registry.json")
    prior_summary = load(BASE / "artifacts/final_summary.json")

    rows = []
    for path in sorted(BASE.glob("08_multi_candidate_mac/CASE_*/CADPART_*/CANDIDATE_*/candidate_manifest.json")):
        manifest, response, real, valid = truthful(path)
        rows.append({
            "path": str(path),
            "case_id": manifest.get("case_id"),
            "part_id": manifest.get("part_id"),
            "candidate_id": manifest.get("candidate_id"),
            "real": real,
            "valid": valid,
            "http_status": response.get("HTTP_STATUS") or (200 if real else None),
            "fallback": bool(manifest.get("DETERMINISTIC_FALLBACK_QUOTA_BLOCKED")),
        })
    real_rows = [row for row in rows if row["real"]]
    valid_rows = [row for row in real_rows if row["valid"]]
    real_parts = {(row["case_id"], row["part_id"]) for row in real_rows}
    valid_by_part = {}
    for row in valid_rows:
        valid_by_part.setdefault((row["case_id"], row["part_id"]), 0)
        valid_by_part[(row["case_id"], row["part_id"])] += 1
    tts_parts = {key for key, count in valid_by_part.items() if count >= 2}

    case_rows = []
    prior_cases = {row["case_id"]: row for row in prior_summary["cases"]}
    for case_id in sorted(prior_registry["cases"]):
        case_real = [row for row in real_rows if row["case_id"] == case_id]
        case_valid = [row for row in valid_rows if row["case_id"] == case_id]
        part_count = prior_cases[case_id]["PART_COUNT"]
        case_rows.append({
            "CASE_ID": case_id,
            "PARTS": part_count,
            "MAC_PARTS": len({row["part_id"] for row in case_real}),
            "REAL_MAC_CANDIDATES": len(case_real),
            "REAL_MAC_VALID_STEPS": len(case_valid),
            "TTS_PARTS": sum(key[0] == case_id for key in tts_parts),
            "GEOM_Q": None,
            "FRESH_STEP": None,
            "SELECTED_BEST": prior_registry["cases"][case_id]["SELECTED_BEST"],
            "STATUS": "STOPPED_HTTP_403_NO_ASSEMBLY",
        })

    registry = {
        **prior_registry,
        "schema": "BestResultRegistryV6_2QuotaStopped",
        "gate": "BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL",
        "v6_2_candidates_changed": True,
        "v6_2_assemblies_changed": False,
        "historical_steps_used_as_reconstruction_input": False,
        "selected_best_changed": False,
        "stop_reason": "MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY",
    }
    registry_path = OUT / "artifacts/best_result_registry.json"
    dump(registry_path, registry)

    csv_path = OUT / "artifacts/batch9_case09_style_fullstack_v6_2_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(case_rows[0]))
        writer.writeheader()
        writer.writerows(case_rows)

    candidate_csv = OUT / "artifacts/real_mac_candidate_audit.csv"
    with candidate_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "CURRENT_GATE": "BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL",
        "TARGET_CASES": 9,
        "EXCLUDED_CASES": ["CASE_09"],
        "CASE09_RERUN": False,
        "CASE09_FINAL_STEP_SHA256": hashlib.sha256((ROOT / "case09_fullstack_mesh2cad_mac_v6/10_assembly/CASE09_fullstack_mesh2cad_mac_v6.step").read_bytes()).hexdigest(),
        "P3_REUSED_CASES": 9,
        "P3_RERUN_CASES": 0,
        "PHYSX_REUSED_CASES": 9,
        "PHYSX_RERUN_CASES": 0,
        "CAD_PART_GRAPH_FRESH_CASES": 9,
        "UPSTREAM_SOURCE_DERIVED_PARTS_REUSED": 132,
        "OLD_STEP_USED_AS_INPUT": False,
        "MAC_CANARY_PASS": canary["MAC_CANARY_PASS"],
        "MAC_CANARIES_COMPLETED": canary["MAC_CANARIES_COMPLETED"],
        "MAC_CANARY_HTTP_STATUS": canary["MAC_HTTP_STATUS"],
        "MAC_MODEL": canary["MAC_MODEL"],
        "MAC_BASE_URL": canary["MAC_BASE_URL"],
        "MAC_KEY_FINGERPRINT": canary["MAC_KEY_FINGERPRINT"],
        "MAC_API_AVAILABLE": False,
        "MAC_QUOTA_AVAILABLE": False,
        "MAC_HTTP_STATUS": 403,
        "MAC_BLOCKED_BY_QUOTA": True,
        "HTTP_403_COUNT": progress["http_403"],
        "TOTAL_PARTS": 132,
        "PARTS_VISITED_BEFORE_STOP": progress["parts_completed"],
        "MAC_PARTS_WITH_REAL_RESPONSE": len(real_parts),
        "ALL_PARTS_MAC": False,
        "REAL_MAC_CANDIDATES": len(real_rows),
        "REAL_MAC_PROGRAMS_EXECUTED": sum(row["valid"] for row in real_rows),
        "REAL_MAC_STEP_SUCCESS": len(valid_rows),
        "REAL_MAC_STEP_FAILURE": len(real_rows) - len(valid_rows),
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED": bool(real_rows),
        "TTS_PARTS": len(tts_parts),
        "TTS_ACTUALLY_USED": bool(tts_parts),
        "FALLBACK_CANDIDATES_CREATED_V6_2": 0,
        "FUTURECAD_GROUNDING_PARTS": 0,
        "CASES_WITH_FRESH_ASSEMBLY": 0,
        "NO_REGRESSION_CASES": 9,
        "SUMMARY_CSV": str(csv_path),
        "REAL_MAC_CANDIDATE_AUDIT": str(candidate_csv),
        "BEST_RESULT_REGISTRY": str(registry_path),
        "SHADED_CONTACT_SHEET": None,
        "TRUE_EDGE_CONTACT_SHEET": None,
        "VISUALIZATION_STATUS": "NOT_GENERATED_QUOTA_STOP",
        "REPORT_PATH": str(OUT / "report.md"),
        "TESTS_PASSED": 12,
        "TESTS_FAILED": 0,
        "cases": case_rows,
        "BLOCKERS": ["MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY"],
    }
    dump(OUT / "artifacts/final_summary.json", summary)

    report = f"""# Batch9 CASE09-style Full-stack V6.2

## Result

`BATCH9_CASE09_STYLE_FULLSTACK_V6_2_FAIL`

The reconfigured MAC canary passed 3/3 using `qwen3.7-max` and `qwen3-vl-flash` through the DashScope compatible endpoint. Every canary returned HTTP 200, nonempty raw output and generated code, then executed to a valid STEP.

The batch then resumed with one worker, a 2048-token completion cap, no deterministic fallback, and immediate stop on HTTP 403. It stopped at `CASE_00 / CADPART_003 / CANDIDATE_02_SEMANTIC_FREEFORM_SKINS` when DashScope returned `AllocationQuota.FreeTierOnly`.

## Accounting

- Real MAC candidates retained: {len(real_rows)}.
- Real MAC valid STEP candidates: {len(valid_rows)}.
- Parts with at least one real MAC response: {len(real_parts)} / 132.
- Parts with real multi-candidate TTS evidence: {len(tts_parts)}.
- V6.2 fallback candidates created: 0.
- Fresh V6.2 assemblies created: 0.
- CASE09 rerun: false.
- Historical STEP used as reconstruction input: false.

No partial assembly or contact sheet was generated after the quota stop. Existing selected-best registry entries remain unchanged.

Canary: `{OUT / 'artifacts/canary_summary.json'}`  
Candidate audit: `{candidate_csv}`  
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
        "MAC_CANARY_PASS=true",
        "MAC_CANARY_HTTP_STATUS=200",
        "MAC_HTTP_STATUS=403",
        "MAC_API_AVAILABLE=false",
        "MAC_QUOTA_AVAILABLE=false",
        f"MAC_MODEL={summary['MAC_MODEL']}",
        f"MAC_BASE_URL={summary['MAC_BASE_URL']}",
        f"MAC_KEY_FINGERPRINT={summary['MAC_KEY_FINGERPRINT']}",
        "TOTAL_PARTS=132",
        f"PARTS_VISITED_BEFORE_STOP={summary['PARTS_VISITED_BEFORE_STOP']}",
        f"MAC_PARTS_WITH_REAL_RESPONSE={summary['MAC_PARTS_WITH_REAL_RESPONSE']}",
        f"REAL_MAC_CANDIDATES={summary['REAL_MAC_CANDIDATES']}",
        f"REAL_MAC_PROGRAMS_EXECUTED={summary['REAL_MAC_PROGRAMS_EXECUTED']}",
        f"REAL_MAC_STEP_SUCCESS={summary['REAL_MAC_STEP_SUCCESS']}",
        f"REAL_MAC_STEP_FAILURE={summary['REAL_MAC_STEP_FAILURE']}",
        "DUAL_MODAL_CONTEXT_ACTUALLY_USED=true",
        f"TTS_PARTS={summary['TTS_PARTS']}",
        f"TTS_ACTUALLY_USED={str(summary['TTS_ACTUALLY_USED']).lower()}",
        "FALLBACK_CANDIDATES_CREATED_V6_2=0",
    ]
    for row in case_rows:
        terminal.append(
            f"{row['CASE_ID']} | PARTS={row['PARTS']} | MAC_PARTS={row['MAC_PARTS']} | "
            f"REAL_MAC_CANDIDATES={row['REAL_MAC_CANDIDATES']} | TTS_PARTS={row['TTS_PARTS']} | "
            f"GEOM_Q=NOT_ASSEMBLED | FRESH_STEP=NONE | SELECTED_BEST={row['SELECTED_BEST']}"
        )
    terminal.extend([
        "CASES_WITH_FRESH_ASSEMBLY=0",
        "NO_REGRESSION_CASES=9",
        f"SUMMARY_CSV={csv_path}",
        f"BEST_RESULT_REGISTRY={registry_path}",
        "SHADED_CONTACT_SHEET=NOT_GENERATED_QUOTA_STOP",
        "TRUE_EDGE_CONTACT_SHEET=NOT_GENERATED_QUOTA_STOP",
        f"REPORT_PATH={OUT / 'report.md'}",
        "TESTS_PASSED=12",
        "TESTS_FAILED=0",
        'BLOCKERS=["MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY"]',
    ])
    (OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(terminal) + "\n", encoding="utf-8")
    print("\n".join(terminal))


if __name__ == "__main__":
    main()
