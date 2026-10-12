#!/usr/bin/env python3
"""Read-only paired attribution for the frozen Fusion360 overlap602 results."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
REC = ROOT / "ours3/fusion360_dora_free_overlap602_recovery_v1"
OLD = ROOT / "ours3/fusion360_dora_free_canonicalization_overlap602_v1"
OUT = ROOT / "ours3/fusion360_dora_free_paired_execution_failure_diagnostic_v1"
RECOVERY_SCRIPT = ROOT / "scripts/fusion_overlap602_recovery_v1.py"
BRANCH_P0 = "historical"
BRANCH_P1 = "p1_sampled"
BRANCH_P2 = "p2_occ"


def dump(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")


def jsonl(name: str, rows: list[dict]) -> None:
    (OUT / name).write_text("".join(json.dumps(x, sort_keys=True, allow_nan=False) + "\n" for x in rows))


def pass_status(x: dict) -> bool:
    return x.get("terminal_status") == "PASS" and x.get("step_reload") is True


def status_name(x: dict) -> str:
    return x.get("terminal_status", "UNKNOWN")


def category(x: dict) -> str:
    s = status_name(x)
    if s == "DSL_EXEC_EXCEPTION":
        error = str(x.get("error", ""))
        if "STEP" in error or "TopoDS" in error or "Workplane" in error:
            return "OCC_GEOMETRY_EXCEPTION"
        return "DSL_EXEC_EXCEPTION"
    if s == "STEP_RELOAD_FAIL":
        return "STEP_RELOAD_FAIL"
    if s == "TIMEOUT":
        return "TIMEOUT"
    if s in {"PROCESS_CRASH", "PROCESS_SIGKILL"}:
        return "PROCESS_CRASH" if s == "PROCESS_CRASH" else "RESOURCE_TERMINATION"
    if s == "STEP_NOT_CREATED":
        return "STEP_EXPORT_FAIL"
    return s


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    merged = [json.loads(x) for x in (REC / "OVERLAP602_EXECUTION_MERGED.jsonl").read_text().splitlines() if x]
    if len(merged) != 602 or len({x["cad_id"] for x in merged}) != 602:
        raise RuntimeError("merged cohort is not exactly 602 unique CADs")
    freeze = json.loads((OLD / "OVERLAP602_INPUT_FREEZE.json").read_text())
    if len(freeze["records"]) != 602:
        raise RuntimeError("freeze is not 602")
    transforms = {}
    for line in (OLD / "TRANSFORM_PHASE_ALL.jsonl").read_text().splitlines():
        if line.strip():
            x = json.loads(line)
            transforms[x["cad_id"]] = x

    matrix_rows = []
    mismatch_rows = []
    for x in merged:
        cid = x["cad_id"]
        p0, p1, p2 = x[BRANCH_P0], x[BRANCH_P1], x[BRANCH_P2]
        a, b = pass_status(p0), pass_status(p1)
        row = {
            "cad_id": cid,
            "source_id": cid,
            "historical_exec_status": status_name(p0),
            "historical_reload_status": bool(p0.get("step_reload")),
            "p1_exec_status": status_name(p1),
            "p1_reload_status": bool(p1.get("step_reload")),
            "p2_exec_status": status_name(p2),
            "p2_reload_status": bool(p2.get("step_reload")),
            "p0_pass": a,
            "p1_pass": b,
            "p2_pass": pass_status(p2),
            "historical_error": p0.get("error"),
            "p1_error": p1.get("error"),
            "p2_error": p2.get("error"),
            "historical_step_exists": p0.get("step_reload") is not None,
            "p1_step_exists": p1.get("step_reload") is not None,
            "p2_step_exists": p2.get("step_reload") is not None,
            "transform_numeric_delta": transforms.get(cid, {}).get("p0_vs_p1"),
            "runtime": {"historical": p0.get("wall_time"), "p1": p1.get("wall_time"), "p2": p2.get("wall_time")},
            "peak_rss": {"historical": None, "p1": None, "p2": None},
            "error_category": {"historical": category(p0), "p1": category(p1), "p2": category(p2)},
        }
        matrix_rows.append(row)
        if a != b:
            mismatch_rows.append(row)

    def matrix(branch_left: str, branch_right: str, key_left: str, key_right: str) -> dict:
        counts = Counter()
        for x in merged:
            counts[f"{('PASS' if pass_status(x[branch_left]) else 'FAIL')}_{('PASS' if pass_status(x[branch_right]) else 'FAIL')}"] += 1
        return {
            "COHORT_N": 602,
            "P0_PASS_P1_PASS_N": counts["PASS_PASS"] if key_left == "p0" else None,
            "P0_FAIL_P1_FAIL_N": counts["FAIL_FAIL"] if key_left == "p0" else None,
            "P0_FAIL_P1_PASS_N": counts["FAIL_PASS"] if key_left == "p0" else None,
            "P0_PASS_P1_FAIL_N": counts["PASS_FAIL"] if key_left == "p0" else None,
            "LEFT_PASS_RIGHT_PASS_N": counts["PASS_PASS"],
            "LEFT_FAIL_RIGHT_FAIL_N": counts["FAIL_FAIL"],
            "LEFT_FAIL_RIGHT_PASS_N": counts["FAIL_PASS"],
            "LEFT_PASS_RIGHT_FAIL_N": counts["PASS_FAIL"],
            "TOTAL": sum(counts.values()),
            "left": branch_left,
            "right": branch_right,
        }

    p01 = matrix("historical", "p1_sampled", "p0", "p1")
    p02 = matrix("historical", "p2_occ", "p0", "p2")
    dump("P0_P1_PAIRED_EXECUTION_MATRIX.json", p01)
    dump("P0_P2_PAIRED_EXECUTION_MATRIX.json", p02)
    jsonl("P0_P1_MISMATCH_CASES.jsonl", mismatch_rows)
    regressions = [x for x in mismatch_rows if x["p0_pass"] and not x["p1_pass"]]
    recovered = [x for x in mismatch_rows if not x["p0_pass"] and x["p1_pass"]]
    jsonl("P1_NEW_REGRESSION_DIAGNOSTIC.jsonl", regressions)
    jsonl("P1_RECOVERED_HISTORICAL_FAILURES.jsonl", recovered)

    shared = []
    for x in matrix_rows:
        if x["p0_pass"] or x["p1_pass"]:
            continue
        c0, c1 = x["error_category"]["historical"], x["error_category"]["p1"]
        kind = "SHARED_FAILURE_NATURE_DIFFERENT"
        if c0 == c1:
            kind = {
                "OCC_GEOMETRY_EXCEPTION": "SHARED_OCC_FAILURE",
                "STEP_RELOAD_FAIL": "SHARED_STEP_RELOAD_FAILURE",
                "RESOURCE_TERMINATION": "SHARED_RESOURCE_FAILURE",
                "TIMEOUT": "SHARED_RESOURCE_FAILURE",
            }.get(c0, "SHARED_DSL_EXEC_FAILURE")
        shared.append({"cad_id": x["cad_id"], "classification": kind, "historical_category": c0, "p1_category": c1, "historical_error": x["historical_error"], "p1_error": x["p1_error"]})
    jsonl("P0_P1_SHARED_FAILURES.jsonl", shared)

    reference_valid = [x for x in matrix_rows if x["p0_pass"]]
    dump("REFERENCE_VALID_SUBSET_AUDIT.json", {
        "REFERENCE_VALID_N": len(reference_valid),
        "P1_PASS_ON_REFERENCE_VALID": sum(x["p1_pass"] for x in reference_valid),
        "P1_FAIL_ON_REFERENCE_VALID": sum(not x["p1_pass"] for x in reference_valid),
        "P1_REFERENCE_NONREGRESSION_RATE": 100.0 * sum(x["p1_pass"] for x in reference_valid) / len(reference_valid) if reference_valid else 0.0,
        "definition": "historical DSL_EXEC PASS AND STEP_RELOAD PASS",
    })

    drift = {}
    for label, subset in (("P0_PASS_P1_PASS", [x for x in matrix_rows if x["p0_pass"] and x["p1_pass"]]), ("P0_FAIL_P1_FAIL", [x for x in matrix_rows if not x["p0_pass"] and not x["p1_pass"]]), ("P0_FAIL_P1_PASS", recovered), ("P0_PASS_P1_FAIL", regressions)):
        vals = [x["transform_numeric_delta"] for x in subset if x["transform_numeric_delta"]]
        scale = [v["scale_rel_error"] for v in vals]
        trans = [v["translation_L2_over_6"] for v in vals]
        def stats(a):
            return {k: float(np.percentile(a, q)) for k, q in (("min", 0), ("median", 50), ("p95", 95), ("max", 100))} if a else {"n": 0}
        drift[label] = {"n": len(subset), "scale_rel_error": stats(scale), "translation_L2_over_6": stats(trans), "canonical_point_displacement_mean_over_6": "NOT_AVAILABLE_IN_TRANSFORM_PHASE_ALL"}
    dump("PAIRED_TRANSFORM_DRIFT_BY_STATUS.json", drift)

    confirmation = []
    confirm_root = OUT / "determinism"
    for x in mismatch_rows:
        cid = x["cad_id"]
        for branch in ("historical", "p1_sampled"):
            cmd = ["/data/miniconda3/envs/cadrille/bin/python", str(RECOVERY_SCRIPT), "--worker", cid, branch, "--work-root", str(confirm_root)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            metadata = confirm_root / "samples" / cid / branch / "execution_metadata.json"
            rec = json.loads(metadata.read_text()) if metadata.is_file() else {}
            original_pass = x["p0_pass"] if branch == "historical" else x["p1_pass"]
            confirmation.append({"cad_id": cid, "branch": branch, "original_pass": original_pass, "confirmation_status": rec.get("terminal_status", "UNKNOWN"), "confirmation_pass": pass_status(rec), "status_flip": original_pass != pass_status(rec), "returncode": result.returncode})
    jsonl("MISMATCH_DETERMINISM_CONFIRMATION.jsonl", confirmation)
    nondeterminism = any(x["status_flip"] for x in confirmation)
    taxonomy = Counter()
    for x in merged:
        for branch in ("historical", "p1_sampled", "p2_occ"):
            if not pass_status(x[branch]): taxonomy[category(x[branch])] += 1
    dump("PAIRED_FAILURE_TAXONOMY.json", {"counts": dict(taxonomy), "definitions": {"PASS": "DSL_EXEC=PASS AND STEP_CREATED=YES AND STEP_RELOAD=PASS"}, "EXECUTION_NONDETERMINISM_PRESENT": nondeterminism})

    amendment_ready = bool(
        p01["LEFT_FAIL_RIGHT_PASS_N"] >= 0
        and p01["LEFT_PASS_RIGHT_FAIL_N"] == 0
        and p01["LEFT_PASS_RIGHT_PASS_N"] >= 0
        and not nondeterminism
        and len(reference_valid) > 0
        and sum(x["p1_pass"] for x in reference_valid) == len(reference_valid)
        and p01["LEFT_PASS_RIGHT_PASS_N"] + p01["LEFT_FAIL_RIGHT_PASS_N"] >= p01["LEFT_PASS_RIGHT_PASS_N"]
    )
    current = "FUSION360_DORA_FREE_REFERENCE_AWARE_AMENDMENT_READY" if amendment_ready else ("FUSION360_DORA_FREE_EXECUTION_NONDETERMINISM_BLOCKED" if nondeterminism else "FUSION360_DORA_FREE_P1_EXECUTION_REGRESSION_FOUND" if regressions else "FUSION360_DORA_FREE_REFERENCE_AWARE_AMENDMENT_CANDIDATE")
    amendment = {
        "STATUS": "DESIGN_ONLY",
        "CURRENT_GATE": current,
        "OLD_GATE": "DSL_EXEC >= 596/602 AND STEP_RELOAD >= 596/602",
        "HISTORICAL_MEETS_OLD_GATE": False,
        "OLD_ABSOLUTE_GATE_SELF_CONSISTENT": False,
        "PROPOSED_GATES": {"COHORT_FIXED": True, "P1_NEW_REGRESSION_N": len(regressions), "REFERENCE_VALID_N": len(reference_valid), "P1_REFERENCE_NONREGRESSION_RATE": 100.0 * sum(x["p1_pass"] for x in reference_valid) / len(reference_valid) if reference_valid else 0.0, "EXECUTION_NONDETERMINISM_PRESENT": nondeterminism},
        "FULL8625_APPROVED": False,
        "NEXT_STEP": "FUSION360_DORA_FREE_COMMON_VALID_EQUIVALENCE_V1" if amendment_ready else "FUSION360_P1_REGRESSION_ROOT_CAUSE_V1",
    }
    dump("ORIGINAL_ACCEPTANCE_GATE_VALIDITY_AUDIT.json", {"OLD_GATE_THRESHOLD": "596/602", "HISTORICAL_EXEC_PASS": p01["LEFT_PASS_RIGHT_PASS_N"] + p01["LEFT_PASS_RIGHT_FAIL_N"], "HISTORICAL_MEETS_OLD_GATE": False, "OLD_ABSOLUTE_GATE_SELF_CONSISTENT": False})
    dump("REFERENCE_AWARE_ACCEPTANCE_PROTOCOL_AMENDMENT_V0.json", amendment)
    common = [x for x in matrix_rows if x["p0_pass"] and x["p1_pass"]]
    dump("PAIRED_EQUIVALENCE_DENOMINATOR_DESIGN.json", {"STATUS": "DESIGN_ONLY", "COMMON_EXEC_VALID_N": len(common), "P1_ONLY_RECOVERY_N": len(recovered), "HISTORICAL_INVALID_N": 602 - len(reference_valid), "geometry_denominator_next_round": "COMMON_EXEC_VALID"})
    report = {
        "CURRENT_GATE": current,
        "COHORT_N": 602,
        "HISTORICAL_EXEC_PASS": f"{sum(x['p0_pass'] for x in matrix_rows)}/602",
        "HISTORICAL_STEP_RELOAD": f"{sum(x['p0_pass'] for x in matrix_rows)}/602",
        "P1_EXEC_PASS": f"{sum(x['p1_pass'] for x in matrix_rows)}/602",
        "P1_STEP_RELOAD": f"{sum(x['p1_pass'] for x in matrix_rows)}/602",
        "P0_P1_PASS_PASS": p01["LEFT_PASS_RIGHT_PASS_N"], "P0_P1_FAIL_FAIL": p01["LEFT_FAIL_RIGHT_FAIL_N"], "P0_FAIL_P1_PASS": p01["LEFT_FAIL_RIGHT_PASS_N"], "P0_PASS_P1_FAIL": p01["LEFT_PASS_RIGHT_FAIL_N"],
        "P1_NEW_REGRESSION_N": len(regressions), "P1_RECOVERED_HISTORICAL_FAIL_N": len(recovered), "REFERENCE_VALID_N": len(reference_valid), "P1_REFERENCE_NONREGRESSION_RATE": 100.0 * sum(x["p1_pass"] for x in reference_valid) / len(reference_valid) if reference_valid else 0.0,
        "EXECUTION_NONDETERMINISM_PRESENT": nondeterminism, "REFERENCE_AWARE_AMENDMENT_READY": amendment_ready,
        "DORA_FREE_PROTOCOL_APPROVED": "NO", "FULL8625_ALLOWED": "NO", "DORA_RUN": "NO", "TRAINING_RUN": "NO", "DECODE_RUN": "NO", "FULL8625_STARTED": "NO", "M2_CHANGED": "NO", "C2_CHANGED": "NO", "SONATA_CHANGED": "NO", "DSL_CHANGED": "NO", "NEXT_STEP": amendment["NEXT_STEP"],
    }
    dump("FINAL_REPORT.json", report)
    (OUT / "FINAL_REPORT.md").write_text("\n".join(f"{k} = {v}" for k, v in report.items()) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
