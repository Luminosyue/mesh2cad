#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/fusion360_reconstruction_expansion_v1")
BUILD = OUT / "canary/build/Fusion360/train"
RESULTS = OUT / "canary/FUSION360_CANARY100_EXECUTION.jsonl"
FAILURES = OUT / "FUSION360_EXPANSION_FAILURES.jsonl"
NONTERM = OUT / "FUSION360_OCC_NATIVE_NONTERMINATION.jsonl"

TAXONOMY = [
    "SOURCE_PARSE_FAIL",
    "UNSUPPORTED_PROGRAM",
    "DSL_CONVERSION_FAIL",
    "DSL_EXEC_FAIL",
    "STEP_WRITE_FAIL",
    "STEP_RELOAD_FAIL",
    "BREP_INVALID",
    "OCC_NATIVE_NONTERMINATION",
    "SURFACE_FAIL",
    "CURVE_EXTRACTION_FAIL",
    "C2_FAIL",
    "CONTEXT_OVERFLOW",
    "TARGET_TRUNCATION",
    "EOS_SUPERVISION_FAIL",
    "RESULT_SUPERVISION_FAIL",
    "LABEL_MASK_FAIL",
    "OTHER",
]


def read_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


rows = read_jsonl(RESULTS)
fixed = []
failures = []
nonterms = []
for row in rows:
    sid = row["source_id"]
    meta = read_json(BUILD / sid / "meta.json")
    qa = meta.get("qa") or {}
    conversion_pass = bool(meta.get("conversion"))
    dsl_exec_pass = bool(meta.get("occ_qa", {}).get("ok"))
    step_pass = bool(meta.get("model_step")) or bool(meta.get("occ_qa", {}).get("step"))
    final_geometry_pass = row.get("returncode") == 0 and bool(qa.get("passed", True))
    surface_pass = final_geometry_pass and meta.get("spatial", {}).get("num_points") == 8192
    stage = None
    if row.get("timeout"):
        stage = "OCC_NATIVE_NONTERMINATION"
    elif row.get("returncode") == 2:
        stage = "UNSUPPORTED_PROGRAM"
    elif row.get("returncode") == 1:
        stage = "DSL_EXEC_FAIL"
    elif row.get("returncode") == 3:
        stage = "DSL_CONVERSION_FAIL"
    elif row.get("returncode") != 0:
        stage = "OTHER"
    reason = None
    if stage:
        reason = qa.get("reject_reason") or row.get("failure_reason")
    row.update(
        {
            "PROGRAM_PASS": conversion_pass,
            "DSL_EXEC_PASS": dsl_exec_pass,
            "STEP_PASS": step_pass,
            "BREP_PASS": final_geometry_pass,
            "SURFACE_PASS": surface_pass,
            "CURVE_PASS": False,
            "C2_PASS": False,
            "RUNTIME_PASS": False,
            "FINAL_READY": False,
            "failure_stage": stage,
            "failure_reason": reason,
        }
    )
    fixed.append(row)
    if stage:
        failures.append(
            {
                "cad_id": row["cad_id"],
                "source_id": sid,
                "stage": stage,
                "failure_reason": reason,
                "timeout": bool(row.get("timeout")),
                "artifact_refs": {"artifact_dir": row.get("artifact_dir")},
            }
        )
    if row.get("timeout"):
        nonterms.append(
            {
                "cad_id": row["cad_id"],
                "source_id": sid,
                "timeout": 600,
                "stage": "OCC_NATIVE_NONTERMINATION",
                "retry_count": 0,
                "worker_status": "subprocess_timeout_killed",
            }
        )

write_jsonl(RESULTS, fixed)
write_jsonl(FAILURES, failures)
write_jsonl(NONTERM, nonterms)

counts = {
    field: sum(1 for row in fixed if row.get(field))
    for field in [
        "PROGRAM_PASS",
        "DSL_EXEC_PASS",
        "STEP_PASS",
        "BREP_PASS",
        "SURFACE_PASS",
        "CURVE_PASS",
        "C2_PASS",
        "RUNTIME_PASS",
        "FINAL_READY",
    ]
}
matrix = dict(Counter(row.get("failure_stage") or "PASS_GEOMETRY_ONLY_CURVE_C2_RUNTIME_PENDING" for row in fixed))
report = {
    "CURRENT_STAGE": "CANARY100",
    "CANARY_N": len(fixed),
    **counts,
    "READY_YIELD": 0.0,
    "FAILURE_MATRIX": matrix,
    "OCC_NATIVE_NONTERMINATION": matrix.get("OCC_NATIVE_NONTERMINATION", 0),
    "UNRESOLVED_INFRA_FAILURE": matrix.get("OTHER", 0),
    "PROTOCOL_DRIFT": "NO",
    "CURRENT_GATE": "FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW",
    "NEXT_STEP": "Review canonical Fusion360 conversion coverage before Pilot1000; do not change DSL/C2/tokenizer/context to lift yield.",
    "notes": [
        "Canary execution used the existing Fusion360 canonical DSL/official geometry/spatial QA builder in per-case subprocess isolation.",
        "CURVE/C2/RUNTIME/FINAL_READY remain false because the canary failed before official expansion C2/runtime eligibility could launch.",
    ],
}
write_json(OUT / "FUSION360_CANARY100_REPORT.json", report)

summary = {"TOTAL_FAIL": len(failures), **{k: 0 for k in TAXONOMY}}
for item in failures:
    summary[item["stage"] if item["stage"] in TAXONOMY else "OTHER"] += 1
write_json(OUT / "FUSION360_EXPANSION_FAILURE_SUMMARY.json", summary)

stats = read_json(OUT / "FUSION360_EXPANSION_DATASET_STATS.json")
stats.update(
    {
        "PROGRAM_PASS": counts["PROGRAM_PASS"],
        "GEOMETRY_PASS": counts["BREP_PASS"],
        "SURFACE_PASS": counts["SURFACE_PASS"],
        "CURVE_PASS": 0,
        "C2_PASS": 0,
        "RUNTIME_PASS": 0,
        "FINAL_READY": 0,
        "READY_YIELD": 0,
        "failure_matrix": matrix,
    }
)
write_json(OUT / "FUSION360_EXPANSION_DATASET_STATS.json", stats)

final = read_json(OUT / "FINAL_REPORT.json")
final.update(
    {
        "CURRENT_STAGE": "CANARY100",
        "COMPLETED": len(fixed),
        "GEOMETRY_C2_CLEAN": 0,
        "RUNTIME_AUDITED": 0,
        "FINAL_READY": 0,
        "READY_YIELD": 0,
        "FAILURES": summary,
        "CURRENT_GATE": "FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW",
        "FUSION360_EXPANSION_READY": "NO",
    }
)
write_json(OUT / "FINAL_REPORT.json", final)

md = f"""# FUSION360_RECONSTRUCTION_EXPANSION_V1

CURRENT_STAGE = CANARY100

RAW_TOTAL = {final['RAW_TOTAL']}
EXISTING_EXCLUDED = {final['EXISTING_EXCLUDED']}
NEW_RAW_CANDIDATES = {final['NEW_RAW_CANDIDATES']}
CANARY_N = {final['CANARY_N']}
PILOT_N = {final['PILOT_N']}
FULL_COHORT = {final['FULL_COHORT']}
COMPLETED = {final['COMPLETED']}

PROGRAM_PASS = {counts['PROGRAM_PASS']}
DSL_EXEC_PASS = {counts['DSL_EXEC_PASS']}
STEP_PASS = {counts['STEP_PASS']}
BREP_PASS = {counts['BREP_PASS']}
SURFACE_PASS = {counts['SURFACE_PASS']}
CURVE_PASS = 0
C2_PASS = 0
RUNTIME_PASS = 0
FINAL_READY = 0
READY_YIELD = 0

FAILURES:
- DSL_CONVERSION_FAIL = {summary['DSL_CONVERSION_FAIL']}
- DSL_EXEC_FAIL = {summary['DSL_EXEC_FAIL']}
- UNSUPPORTED_PROGRAM = {summary['UNSUPPORTED_PROGRAM']}
- OCC_NATIVE_NONTERMINATION = {summary['OCC_NATIVE_NONTERMINATION']}
- OTHER = {summary['OTHER']}

CONTRACT:
- TARGET = CANONICAL_DSL
- SURFACE = SAME_AS_EXACT10K_V1
- CURVE_SOURCE = GT_BREP
- C2 = FROZEN
- VARIABLE_K = YES
- CAP = 128
- CONTEXT = 8192
- K8 = NO
- PROTOCOL_DRIFT = NO

LEAKAGE:
- EXACT10K_OVERLAP = 0
- EXISTING_READY_DUPLICATE = 0
- PROTECTED_CONFLICT = 0

SAFETY:
- EXACT10K_V1_CHANGED = NO
- TRAINING_RUN = NO
- OPTIMIZER_STEP = NO
- DECODE_RUN = NO
- TARGET_CHANGED = NO
- TOKENIZER_CHANGED = NO
- CONTEXT_CHANGED = NO
- C2_CHANGED = NO

CURRENT_GATE = FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW
FUSION360_EXPANSION_READY = NO

NEXT_STEP = Review canonical Fusion360 conversion coverage before Pilot1000.
"""
(OUT / "FINAL_REPORT.md").write_text(md, encoding="utf-8")
print(json.dumps(report, indent=2, sort_keys=True))
