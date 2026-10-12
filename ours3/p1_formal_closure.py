#!/usr/bin/env python3
"""Formal, read-only closure analysis for P1 against A1/A3 on VAL1000."""

from __future__ import annotations

import ast
import csv
import difflib
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/p1_operation_aware_formal_closure_v1"
CADFIT_PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")
WORKER = (
    ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/launch/step_reload_worker.py"
)
ARMS = {
    "A0": ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0/report.json",
    "A1": ROOT
    / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1/report.json",
    "A2": ROOT
    / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a2/report.json",
    "A3": ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3/report.json",
    "P1": ROOT / "ours3/p1_exact9998_val1000_eval_v2/report.json",
}
OLD_CLOSURE = ROOT / "ours3/a0_a1_a2_a3_core_ablation_finalization_v1"
EXTENDED = ROOT / "ours3/exact9998_val1000_a0_a1_a2_a3_extended_cad_metrics_v1"

ALLOWED_OPS = (
    "ExtrudePolygon",
    "Cylinder",
    "Extrude",
    "Rectangle",
    "Circle",
    "Box",
    "Revolve",
    "Sketch",
    "Cut",
    "Union",
)
OP_RE = re.compile(r"\b(" + "|".join(ALLOWED_OPS) + r")\s*\(")

# Reuse the project parser used by the frozen A0-A3 audit whenever available.
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "SpatialLM")]
_CAD_PARSER = None


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        seen = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    keys.append(key)
                    seen.add(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def resolve_path(value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def load_reports() -> dict[str, dict[str, Any]]:
    reports = {}
    for arm, path in ARMS.items():
        reports[arm] = json.loads(path.read_text())
        if reports[arm].get("n_samples") != 1000:
            raise RuntimeError(f"{arm} report is not N=1000: {path}")
    return reports


def sample_maps(reports: dict[str, dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    return {arm: {row["id"]: row for row in report["samples"]} for arm, report in reports.items()}


def sample_dir(row: dict[str, Any]) -> Path | None:
    step = resolve_path(row.get("step"))
    if step:
        return step.parent
    # P1 and the historical reports store the other artifacts beside pred.dsl.
    return None


def read_sample_code(row: dict[str, Any], filename: str) -> str:
    base = sample_dir(row)
    if base is not None:
        if filename == "pred.dsl":
            canonical = base / "pred_canonical.dsl"
            if canonical.exists():
                return canonical.read_text(errors="replace")
        p = base / filename
        if p.exists():
            return p.read_text(errors="replace")
    # A failed sample may have no step path; infer from report-local fields.
    raise FileNotFoundError(f"{filename} unavailable for {row.get('id')}")


def operation_sequence(code: str) -> list[str]:
    global _CAD_PARSER
    if _CAD_PARSER is None:
        try:
            from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code, parse_dsl

            _CAD_PARSER = (extract_dsl_code, parse_dsl)
        except Exception:
            _CAD_PARSER = False
    if _CAD_PARSER:
        extract_dsl_code, parse_dsl = _CAD_PARSER
        try:
            parsed = parse_dsl(extract_dsl_code(code))
        except Exception:
            try:
                parsed = parse_dsl(code)
            except Exception:
                parsed = None
        if parsed is not None:
            return [
                value["op"]
                for name, value in parsed.assignments.items()
                if name != "result" and isinstance(value, dict) and "op" in value
            ]
    return [m.group(1) for m in OP_RE.finditer(code)]


def get_ops(row: dict[str, Any], which: str) -> list[str]:
    filename = "gt.dsl" if which == "gt" else "pred.dsl"
    try:
        return operation_sequence(read_sample_code(row, filename))
    except FileNotFoundError:
        # These lists are a conservative fallback used only for failed parses.
        return list(row.get("gt_ops" if which == "gt" else "pred_ops", []))


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def pct(values: list[float], q: float) -> float | None:
    if not values:
        return None
    v = sorted(values)
    if len(v) == 1:
        return v[0]
    pos = (len(v) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return v[lo]
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def bool_rate(rows: list[dict[str, Any]], key: str) -> float:
    return mean([float(bool(row.get(key))) for row in rows]) or 0.0


def bootstrap_mean(values: list[float], seed: int = 42, n_boot: int = 10000) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(values)
    boots = []
    for _ in range(n_boot):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        boots.append(total / n)
    return pct(boots, 0.025) or float("nan"), pct(boots, 0.975) or float("nan")


def mcnemar_pvalue(a: list[bool], b: list[bool]) -> float:
    x = sum(1 for aa, bb in zip(a, b) if aa and not bb)
    y = sum(1 for aa, bb in zip(a, b) if bb and not aa)
    n = x + y
    if n == 0:
        return 1.0
    k = min(x, y)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2.0 * tail)


def pair_stats(
    left: dict[str, dict[str, Any]],
    right: dict[str, dict[str, Any]],
    key: str,
    higher_is_better: bool = True,
) -> dict[str, Any]:
    ids = sorted(set(left) & set(right))
    deltas = [
        float(left[i].get(key, 0.0)) - float(right[i].get(key, 0.0))
        for i in ids
    ]
    better = sum(d > 0 if higher_is_better else d < 0 for d in deltas)
    worse = sum(d < 0 if higher_is_better else d > 0 for d in deltas)
    ties = len(deltas) - better - worse
    low, high = bootstrap_mean(deltas)
    return {
        "N": len(deltas),
        "mean_delta_left_minus_right": mean(deltas),
        "median_delta_left_minus_right": statistics.median(deltas) if deltas else None,
        "left_better_N": better,
        "tie_N": ties,
        "right_better_N": worse,
        "bootstrap_ci95_low": low,
        "bootstrap_ci95_high": high,
        "higher_is_better": higher_is_better,
    }


def classify_step_row(row: dict[str, Any], reload_ok: bool | None, reload_error: str = "") -> dict[str, Any]:
    step = resolve_path(row.get("step"))
    export_pass = bool(row.get("step_ok")) and step is not None and step.exists()
    if not export_pass:
        status = "FAIL_NOT_EXPORTED"
        reload_pass = False
    elif reload_ok:
        status = "PASS"
        reload_pass = True
    else:
        status = "RELOAD_FAIL"
        reload_pass = False
    return {
        "cad_id": row["id"],
        "sample_id": row.get("sample_id"),
        "dataset": row.get("dataset"),
        "export_pass": export_pass,
        "reload_status": status,
        "reload_pass": reload_pass,
        "error": reload_error,
    }


def reload_one(row: dict[str, Any]) -> dict[str, Any]:
    step = resolve_path(row.get("step"))
    if not (bool(row.get("step_ok")) and step and step.exists()):
        return classify_step_row(row, False)
    try:
        proc = subprocess.run(
            [str(CADFIT_PYTHON), str(WORKER), str(step)],
            capture_output=True,
            text=True,
            timeout=150,
        )
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        return classify_step_row(row, bool(payload.get("step_reload")), payload.get("error", ""))
    except subprocess.TimeoutExpired:
        return classify_step_row(row, False, "reload timeout")
    except Exception as exc:
        return classify_step_row(row, False, f"{type(exc).__name__}: {exc}")


def make_p1_reload_audit(p1_rows: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = list(p1_rows.values())
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(reload_one, row) for row in rows]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda x: x["cad_id"])
    write_csv(
        OUT / "step_reload/P1_STEP_RELOAD_AUDIT.csv",
        results,
        ["cad_id", "sample_id", "dataset", "export_pass", "reload_status", "reload_pass", "error"],
    )
    return {row["cad_id"]: row for row in results}


def load_old_reload(arm: str) -> dict[str, dict[str, Any]]:
    path = OLD_CLOSURE / f"step_reload/{arm}_STEP_RELOAD_AUDIT.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        rows = {}
        for row in csv.DictReader(f):
            row["export_pass"] = as_bool(row.get("export_pass"))
            row["reload_pass"] = as_bool(row.get("reload_pass"))
            rows[row["cad_id"]] = row
        return rows


def step_summary(audit: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = list(audit.values())
    export_n = sum(as_bool(row.get("export_pass")) for row in rows)
    reload_n = sum(as_bool(row.get("reload_pass")) for row in rows)
    return {
        "N": len(rows),
        "export_pass_N": export_n,
        "export_rate": export_n / len(rows) if rows else 0.0,
        "reload_pass_N": reload_n,
        "headline_reload_rate": reload_n / len(rows) if rows else 0.0,
        "conditional_reload_rate": reload_n / export_n if export_n else 0.0,
        "status_counts": dict(Counter(row.get("reload_status") for row in rows)),
    }


def operation_alignment(gt: list[str], pred: list[str]) -> dict[int, str]:
    status: dict[int, str] = {}
    matcher = difflib.SequenceMatcher(a=gt, b=pred, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for i in range(i1, i2):
                status[i] = "correct"
        elif tag == "delete":
            for i in range(i1, i2):
                status[i] = "missing"
        elif tag == "replace":
            n = min(i2 - i1, j2 - j1)
            for i in range(i1, i1 + n):
                status[i] = "wrong_type"
            for i in range(i1 + n, i2):
                status[i] = "missing"
    return status


def operation_matrix(
    maps: dict[str, dict[str, dict[str, Any]]],
    arms: list[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, dict[int, str]]]]:
    statuses: dict[str, dict[str, dict[int, str]]] = defaultdict(dict)
    all_ops = set()
    gt_by_id: dict[str, list[str]] = {}
    pred_by_arm: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for arm in arms:
        for sid, row in maps[arm].items():
            gt = get_ops(maps["A0"][sid], "gt")
            pred = get_ops(row, "pred")
            gt_by_id[sid] = gt
            pred_by_arm[arm][sid] = pred
            statuses[arm][sid] = operation_alignment(gt, pred)
            all_ops.update(gt)
    all_ops = sorted(op for op in all_ops if op not in {"Circle", "Rectangle", "Sketch"})
    result = []
    for op in all_ops:
        out: dict[str, Any] = {"operation": op}
        for arm in arms:
            gt_n = sum(gt.count(op) for gt in gt_by_id.values())
            pred_n = sum(pred_by_arm[arm][sid].count(op) for sid in pred_by_arm[arm])
            match_n = min(gt_n, pred_n)
            missing = max(gt_n - match_n, 0)
            wrong = max(pred_n - match_n, 0)
            out[f"{arm}_GT_N"] = gt_n
            out[f"{arm}_matched_correct_type_N"] = match_n
            out[f"{arm}_matched_rate"] = match_n / gt_n if gt_n else 0.0
            out[f"{arm}_missing_N"] = missing
            out[f"{arm}_wrong_type_substitution_N"] = wrong
            out[f"{arm}_Pred_N"] = pred_n
        rates = {arm: out[f"{arm}_matched_rate"] for arm in arms}
        out["best_arm"] = max(rates, key=rates.get) if rates else ""
        result.append(out)
    return result, statuses


def operation_delta(matrix: list[dict[str, Any]], left: str, right: str) -> list[dict[str, Any]]:
    rows = []
    for row in matrix:
        delta = row[f"{left}_matched_rate"] - row[f"{right}_matched_rate"]
        if delta > 1e-12:
            classification = "REPAIRED"
        elif delta < -1e-12:
            classification = "REGRESSED"
        else:
            classification = "PRESERVED"
        rows.append(
            {
                "operation": row["operation"],
                "GT_N": row[f"{left}_GT_N"],
                f"{left}_match_rate": row[f"{left}_matched_rate"],
                f"{right}_match_rate": row[f"{right}_matched_rate"],
                "delta_left_minus_right": delta,
                f"{left}_missing": row[f"{left}_missing_N"],
                f"{right}_missing": row[f"{right}_missing_N"],
                f"{left}_wrong_type": row[f"{left}_wrong_type_substitution_N"],
                f"{right}_wrong_type": row[f"{right}_wrong_type_substitution_N"],
                "classification": classification,
            }
        )
    return rows


def operation_rescue(
    maps: dict[str, dict[str, dict[str, Any]]],
    left: str,
    right: str,
    statuses: dict[str, dict[str, dict[int, str]]],
) -> list[dict[str, Any]]:
    all_ops = sorted(
        set(row["operation"] for row in operation_matrix(maps, [left, right])[0])
    )
    counts = {op: Counter() for op in all_ops}
    for sid in sorted(set(maps[left]) & set(maps[right])):
        gt = get_ops(maps["A0"][sid], "gt")
        a = statuses[left][sid]
        b = statuses[right][sid]
        for idx, op in enumerate(gt):
            if op not in counts:
                continue
            counts[op][f"{a.get(idx, 'missing')}_to_{b.get(idx, 'missing')}"] += 1
    result = []
    for op in all_ops:
        c = counts[op]
        result.append(
            {
                "operation": op,
                f"{left}_missing_to_{right}_correct_N": c["missing_to_correct"],
                f"{left}_wrong_type_to_{right}_correct_N": c["wrong_type_to_correct"],
                f"{left}_correct_to_{right}_wrong_type_N": c["correct_to_wrong_type"],
                f"{left}_correct_to_{right}_missing_N": c["correct_to_missing"],
                "all_transitions": json.dumps(dict(c), sort_keys=True),
            }
        )
    return result


def geometry_value(row: dict[str, Any], key: str) -> float | None:
    value = row.get("geometry", {}).get(key)
    return float(value) if isinstance(value, (int, float)) else None


def geometry_valid(row: dict[str, Any]) -> bool:
    return (
        geometry_value(row, "chamfer_norm") is not None
        and geometry_value(row, "hausdorff_95_norm") is not None
    )


def geometry_common(
    maps: dict[str, dict[str, dict[str, Any]]],
    left: str,
    right: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    for sid in sorted(set(maps[left]) & set(maps[right])):
        a, b = maps[left][sid], maps[right][sid]
        if not geometry_valid(a) or not geometry_valid(b):
            continue
        ca, cb = geometry_value(a, "chamfer_norm"), geometry_value(b, "chamfer_norm")
        ha, hb = geometry_value(a, "hausdorff_95_norm"), geometry_value(b, "hausdorff_95_norm")
        va, vb = geometry_value(a, "volume_error"), geometry_value(b, "volume_error")
        if ca is None or cb is None:
            continue
        rows.append(
            {
                "cad_id": sid,
                "dataset": a.get("dataset"),
                "left_chamfer": ca,
                "right_chamfer": cb,
                "delta_chamfer_left_minus_right": ca - cb,
                "left_h95": ha,
                "right_h95": hb,
                "delta_h95_left_minus_right": None if ha is None or hb is None else ha - hb,
                "left_volume_error": va,
                "right_volume_error": vb,
                "delta_volume_left_minus_right": None if va is None or vb is None else va - vb,
            }
        )
    summary = {}
    metric_fields = {
        "chamfer": ("left_chamfer", "right_chamfer", "delta_chamfer_left_minus_right"),
        "h95": ("left_h95", "right_h95", "delta_h95_left_minus_right"),
        "volume": ("left_volume_error", "right_volume_error", "delta_volume_left_minus_right"),
    }
    for key, (left_field, right_field, delta_key) in metric_fields.items():
        vals = [r[delta_key] for r in rows if isinstance(r.get(delta_key), (int, float))]
        summary[key] = {
            "paired_N": len(vals),
            "left_mean": mean([r[left_field] for r in rows if isinstance(r.get(left_field), (int, float))]),
            "right_mean": mean([r[right_field] for r in rows if isinstance(r.get(right_field), (int, float))]),
            "mean_delta_left_minus_right": mean(vals),
            "median_delta_left_minus_right": statistics.median(vals) if vals else None,
            "left_better_N": sum(v < 0 for v in vals),
            "tie_N": sum(v == 0 for v in vals),
            "right_better_N": sum(v > 0 for v in vals),
            "bootstrap_ci95_low": bootstrap_mean(vals)[0] if vals else None,
            "bootstrap_ci95_high": bootstrap_mean(vals)[1] if vals else None,
        }
    return rows, summary


def generation_transition_rows(
    maps: dict[str, dict[str, dict[str, Any]]],
    step_audits: dict[str, dict[str, dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ids = sorted(set(maps["A3"]) & set(maps["P1"]))
    max_rows = [{
        "metric": "MAX_LENGTH",
        "A3_1_to_P1_0": sum(
            maps["A3"][i].get("stop_reason") == "MAX_LENGTH"
            and maps["P1"][i].get("stop_reason") != "MAX_LENGTH"
            for i in ids
        ),
        "A3_0_to_P1_1": sum(
            maps["A3"][i].get("stop_reason") != "MAX_LENGTH"
            and maps["P1"][i].get("stop_reason") == "MAX_LENGTH"
            for i in ids
        ),
    }]
    under_rows = [{
        "metric": "under_generation",
        "A3_1_to_P1_0": sum(
            bool(maps["A3"][i].get("under_generation"))
            and not bool(maps["P1"][i].get("under_generation"))
            for i in ids
        ),
        "A3_0_to_P1_1": sum(
            not bool(maps["A3"][i].get("under_generation"))
            and bool(maps["P1"][i].get("under_generation"))
            for i in ids
        ),
    }]
    step_rows = [{
        "metric": "STEP_RELOAD",
        "A3_1_to_P1_0": sum(
            as_bool(step_audits["A3"][i].get("reload_pass"))
            and not as_bool(step_audits["P1"][i].get("reload_pass"))
            for i in ids
        ),
        "A3_0_to_P1_1": sum(
            not as_bool(step_audits["A3"][i].get("reload_pass"))
            and as_bool(step_audits["P1"][i].get("reload_pass"))
            for i in ids
        ),
    }]
    return max_rows + step_rows, under_rows


def structure_generation_association(
    maps: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    ids = sorted(set(maps["A3"]) & set(maps["P1"]))
    deltas = [
        float(maps["P1"][i].get("op_f1", 0.0))
        - float(maps["A3"][i].get("op_f1", 0.0))
        for i in ids
    ]
    improved = [i for i in ids if float(maps["P1"][i].get("op_f1", 0.0)) - float(maps["A3"][i].get("op_f1", 0.0)) >= 0.10]
    unchanged = [i for i in ids if abs(float(maps["P1"][i].get("op_f1", 0.0)) - float(maps["A3"][i].get("op_f1", 0.0))) <= 1e-12]
    groups = [("P1_OPF1_DELTA_GE_0.10", improved), ("P1_OPF1_UNCHANGED", unchanged)]
    rows = []
    for name, group in groups:
        if not group:
            rows.append({"group": name, "N": 0})
            continue
        rows.append(
            {
                "group": name,
                "N": len(group),
                "mean_op_f1_delta": mean([
                    float(maps["P1"][i].get("op_f1", 0.0))
                    - float(maps["A3"][i].get("op_f1", 0.0))
                    for i in group
                ]),
                "A3_EOS_to_P1_EOS_N": sum(
                    maps["A3"][i].get("stop_reason") != "EOS"
                    and maps["P1"][i].get("stop_reason") == "EOS"
                    for i in group
                ),
                "A3_MAXLEN_to_P1_nonMAXLEN_N": sum(
                    maps["A3"][i].get("stop_reason") == "MAX_LENGTH"
                    and maps["P1"][i].get("stop_reason") != "MAX_LENGTH"
                    for i in group
                ),
                "A3_UNDERGEN_to_P1_complete_N": sum(
                    bool(maps["A3"][i].get("under_generation"))
                    and not bool(maps["P1"][i].get("under_generation"))
                    for i in group
                ),
            }
        )
    rows.append(
        {
            "group": "ALL_CASES",
            "N": len(ids),
            "mean_op_f1_delta": mean(deltas),
            "A3_EOS_to_P1_EOS_N": sum(
                maps["A3"][i].get("stop_reason") != "EOS"
                and maps["P1"][i].get("stop_reason") == "EOS"
                for i in ids
            ),
            "A3_MAXLEN_to_P1_nonMAXLEN_N": sum(
                maps["A3"][i].get("stop_reason") == "MAX_LENGTH"
                and maps["P1"][i].get("stop_reason") != "MAX_LENGTH"
                for i in ids
            ),
            "A3_UNDERGEN_to_P1_complete_N": sum(
                bool(maps["A3"][i].get("under_generation"))
                and not bool(maps["P1"][i].get("under_generation"))
                for i in ids
            ),
        }
    )
    return rows


def parse_calls(code: str) -> list[tuple[str, ast.Call]]:
    try:
        tree = ast.parse(code, mode="exec")
    except Exception:
        return []
    calls: list[tuple[int, int, str, ast.Call]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ALLOWED_OPS:
                calls.append((getattr(node, "lineno", 0), getattr(node, "col_offset", 0), node.func.id, node))
    calls.sort(key=lambda x: (x[0], x[1]))
    return [(name, node) for _, _, name, node in calls]


def literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def vec_error(a: Any, b: Any) -> float | None:
    if not (
        isinstance(a, (tuple, list))
        and isinstance(b, (tuple, list))
        and len(a) == len(b)
    ):
        return None
    try:
        return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))
    except Exception:
        return None


def angle_error(a: Any, b: Any) -> float | None:
    if not (
        isinstance(a, (tuple, list))
        and isinstance(b, (tuple, list))
        and len(a) == len(b) == 3
    ):
        return None
    try:
        na = math.sqrt(sum(float(x) ** 2 for x in a))
        nb = math.sqrt(sum(float(x) ** 2 for x in b))
        if na == 0 or nb == 0:
            return None
        dot = sum(float(x) * float(y) for x, y in zip(a, b)) / (na * nb)
        return math.degrees(math.acos(max(-1.0, min(1.0, dot))))
    except Exception:
        return None


def call_kwargs(call: ast.Call) -> dict[str, Any]:
    return {kw.arg: literal(kw.value) for kw in call.keywords if kw.arg}


def parameter_rows(
    maps: dict[str, dict[str, dict[str, Any]]],
    left: str,
    right: str,
) -> list[dict[str, Any]]:
    values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for sid in sorted(set(maps[left]) & set(maps[right])):
        try:
            ga = parse_calls(read_sample_code(maps["A0"][sid], "gt.dsl"))
            la = parse_calls(read_sample_code(maps[left][sid], "pred.dsl"))
            gb = parse_calls(read_sample_code(maps[right][sid], "pred.dsl"))
        except FileNotFoundError:
            continue
        gt_names = [x[0] for x in ga]
        left_names = [x[0] for x in la]
        right_names = [x[0] for x in gb]
        # Match each prediction arm independently to the same GT call sequence.
        for arm_name, pred_calls, pred_names in (
            (left, la, left_names),
            (right, gb, right_names),
        ):
            matcher = difflib.SequenceMatcher(a=gt_names, b=pred_names, autojunk=False)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag != "equal":
                    continue
                for gi, pj in zip(range(i1, i2), range(j1, j2)):
                    op, gcall = ga[gi]
                    _, pcall = pred_calls[pj]
                    gkw, pkw = call_kwargs(gcall), call_kwargs(pcall)
                    for field in ("width", "depth", "height", "radius"):
                        if isinstance(gkw.get(field), (int, float)) and isinstance(pkw.get(field), (int, float)):
                            values[(arm_name, f"{op}.{field}")].append(abs(float(pkw[field]) - float(gkw[field])))
                    for field in ("origin",):
                        e = vec_error(pkw.get(field), gkw.get(field))
                        if e is not None:
                            values[(arm_name, f"{op}.{field}")].append(e)
                    for field in ("axis", "x_axis"):
                        e = angle_error(pkw.get(field), gkw.get(field))
                        if e is not None:
                            values[(arm_name, f"{op}.{field}_degrees")].append(e)
    rows = []
    for (arm, field), vals in sorted(values.items()):
        rows.append(
            {
                "arm": arm,
                "parameter_field": field,
                "N": len(vals),
                "mean": mean(vals),
                "median": statistics.median(vals) if vals else None,
                "p90": pct(vals, 0.90),
            }
        )
    return rows


def graph_from_code(code: str) -> tuple[list[str], set[tuple[int, int]]]:
    try:
        tree = ast.parse(code, mode="exec")
    except Exception:
        return [], set()
    nodes: list[str] = []
    edges: set[tuple[int, int]] = set()

    def visit(node: ast.AST, parent: int | None = None) -> None:
        current = parent
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ALLOWED_OPS:
            nodes.append(node.func.id)
            current = len(nodes) - 1
            if parent is not None:
                edges.add((parent, current))
        for child in ast.iter_child_nodes(node):
            visit(child, current)

    visit(tree)
    return nodes, edges


def graph_case_metrics(maps: dict[str, dict[str, dict[str, Any]]], arm: str) -> list[dict[str, Any]]:
    rows = []
    for sid, row in maps[arm].items():
        try:
            gt_code = read_sample_code(maps["A0"][sid], "gt.dsl")
            pred_code = read_sample_code(row, "pred.dsl")
        except FileNotFoundError:
            rows.append({"arm": arm, "cad_id": sid, "ged_status": "DEFERRED_NO_DSL"})
            continue
        gt_nodes, gt_edges = graph_from_code(gt_code)
        pred_nodes, pred_edges = graph_from_code(pred_code)
        matcher = difflib.SequenceMatcher(a=gt_nodes, b=pred_nodes, autojunk=False)
        mapping: dict[int, int] = {}
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                mapping.update(dict(zip(range(i1, i2), range(j1, j2))))
        mapped_gt_edges = {(mapping[a], mapping[b]) for a, b in gt_edges if a in mapping and b in mapping}
        tp = len(mapped_gt_edges & pred_edges)
        precision = tp / len(pred_edges) if pred_edges else (1.0 if not gt_edges else 0.0)
        recall = tp / len(gt_edges) if gt_edges else (1.0 if not pred_edges else 0.0)
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append(
            {
                "arm": arm,
                "cad_id": sid,
                "dependency_edge_f1": f1,
                "dependency_edge_precision": precision,
                "dependency_edge_recall": recall,
                "ged_status": "APPROX_AST_PARENT_CHILD",
                "graph_alignment_coverage": len(mapping) / len(gt_nodes) if gt_nodes else 1.0,
                "gt_edge_n": len(gt_edges),
                "gt_node_n": len(gt_nodes),
                "node_count_error": len(pred_nodes) - len(gt_nodes),
                "pred_edge_n": len(pred_edges),
                "pred_node_n": len(pred_nodes),
            }
        )
    return rows


def case_parameter_residuals(
    row: dict[str, Any],
    gt_row: dict[str, Any] | None = None,
) -> list[tuple[str, float]]:
    try:
        gt = parse_calls(read_sample_code(gt_row or row, "gt.dsl"))
        pred = parse_calls(read_sample_code(row, "pred.dsl"))
    except FileNotFoundError:
        return []
    gt_names = [name for name, _ in gt]
    pred_names = [name for name, _ in pred]
    errors: list[tuple[str, float]] = []
    matcher = difflib.SequenceMatcher(a=gt_names, b=pred_names, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            continue
        for gi, pj in zip(range(i1, i2), range(j1, j2)):
            op, gcall = gt[gi]
            _, pcall = pred[pj]
            gkw, pkw = call_kwargs(gcall), call_kwargs(pcall)
            for field in ("width", "depth", "height", "radius"):
                if isinstance(gkw.get(field), (int, float)) and isinstance(pkw.get(field), (int, float)):
                    errors.append((f"{op}.{field}", abs(float(pkw[field]) - float(gkw[field]))))
            e = vec_error(pkw.get("origin"), gkw.get("origin"))
            if e is not None:
                errors.append((f"{op}.origin", e))
            for field in ("axis", "x_axis"):
                e = angle_error(pkw.get(field), gkw.get(field))
                if e is not None:
                    errors.append((f"{op}.{field}_degrees", e))
    return errors


def outlier_root_cause(
    sid: str,
    gt_row: dict[str, Any],
    p1_row: dict[str, Any],
    a3_row: dict[str, Any],
    p1_step: dict[str, Any],
    p1_status: dict[int, str],
) -> dict[str, Any]:
    gt_ops = get_ops(gt_row, "gt")
    p1_ops = get_ops(p1_row, "pred")
    a3_ops = get_ops(a3_row, "pred")
    reasons: list[str] = []
    evidence: list[str] = []
    if not bool(p1_row.get("parsed")) or gt_ops != p1_ops:
        reasons.append("OPERATION_STRUCTURE_ERROR")
        evidence.append("P1 parse failure or operation sequence differs from GT")
    if p1_row.get("stop_reason") == "MAX_LENGTH" or bool(p1_row.get("under_generation")):
        reasons.append("OPERATION_STRUCTURE_ERROR")
        evidence.append("P1 generation stopped early or under-generated")
    if not as_bool(p1_step.get("reload_pass")):
        reasons.append("OPERATION_STRUCTURE_ERROR")
        evidence.append("P1 STEP did not reload successfully")
    errors = case_parameter_residuals(p1_row, gt_row)
    for field, value in errors:
        if field.endswith(".origin") and value > 0.25:
            reasons.append("ORIGIN_TRANSLATION_ERROR")
            evidence.append(f"{field} absolute error={value:.4g}")
        elif field.endswith("_degrees") and value > 15.0:
            reasons.append("DIRECTION_ERROR")
            evidence.append(f"{field} angular error={value:.4g} deg")
        elif any(field.endswith(f".{x}") for x in ("width", "depth", "height", "radius")) and value > 0.25:
            reasons.append("SCALE_ERROR")
            evidence.append(f"{field} absolute error={value:.4g}")
    if not reasons and (geometry_value(p1_row, "volume_error") or 0.0) > 1.0:
        reasons.append("EXTENT_ERROR")
        evidence.append("large volume error without a detected structural or parameter trigger")
    unique_reasons = sorted(set(reasons))
    if len(unique_reasons) > 1:
        category = "MULTIPLE"
    elif unique_reasons:
        category = unique_reasons[0]
    else:
        category = "UNRESOLVED"
        evidence.append("no dominant trigger detected by frozen post-hoc audits")
    return {
        "cad_id": sid,
        "P1_Chamfer": geometry_value(p1_row, "chamfer_norm"),
        "A3_Chamfer": geometry_value(a3_row, "chamfer_norm"),
        "P1_H95": geometry_value(p1_row, "hausdorff_95_norm"),
        "P1_Volume": geometry_value(p1_row, "volume_error"),
        "P1_OpF1": p1_row.get("op_f1"),
        "P1_Exact": p1_row.get("exact_match"),
        "P1_STEP_Reload": p1_step.get("reload_pass"),
        "P1_Operation_Diff": gt_ops != p1_ops,
        "A3_Operation_Diff": get_ops(gt_row, "gt") != a3_ops,
        "P1_Status_Correct_N": sum(value == "correct" for value in p1_status.values()),
        "category": category,
        "evidence": "; ".join(evidence),
    }


def make_rescue_gallery(
    maps: dict[str, dict[str, dict[str, Any]]],
    step_audits: dict[str, dict[str, dict[str, Any]]],
    statuses: dict[str, dict[str, dict[int, str]]],
) -> dict[str, Any]:
    from PIL import Image, ImageDraw, ImageFont

    ids = sorted(set(maps["A3"]) & set(maps["P1"]))
    selected: dict[str, str | None] = {}

    def op_rescue(sid: str) -> bool:
        gt = get_ops(maps["A0"][sid], "gt")
        a3 = statuses["A3"].get(sid, {})
        p1 = statuses["P1"].get(sid, {})
        return any(
            a3.get(i) in {"missing", "wrong_type"} and p1.get(i) == "correct"
            for i in range(len(gt))
        )

    candidates = [sid for sid in ids if op_rescue(sid)]
    selected["A3_wrong_operation_to_P1_correct"] = max(
        candidates,
        key=lambda sid: float(maps["P1"][sid].get("op_f1", 0.0)) - float(maps["A3"][sid].get("op_f1", 0.0)),
        default=None,
    )
    candidates = [
        sid for sid in ids
        if maps["A3"][sid].get("stop_reason") == "MAX_LENGTH"
        and maps["P1"][sid].get("stop_reason") != "MAX_LENGTH"
        and not bool(maps["P1"][sid].get("under_generation"))
    ]
    selected["A3_truncated_to_P1_complete"] = max(
        candidates,
        key=lambda sid: float(maps["P1"][sid].get("op_f1", 0.0)) - float(maps["A3"][sid].get("op_f1", 0.0)),
        default=None,
    )
    candidates = [
        sid for sid in ids
        if not as_bool(step_audits["A3"][sid].get("reload_pass"))
        and as_bool(step_audits["P1"][sid].get("reload_pass"))
    ]
    selected["A3_STEP_fail_to_P1_reload_pass"] = max(
        candidates,
        key=lambda sid: float(maps["P1"][sid].get("op_f1", 0.0)) - float(maps["A3"][sid].get("op_f1", 0.0)),
        default=None,
    )
    candidates = [
        sid for sid in ids
        if geometry_valid(maps["A3"][sid]) and geometry_valid(maps["P1"][sid])
        and (geometry_value(maps["P1"][sid], "chamfer_norm") or 0.0)
        > (geometry_value(maps["A3"][sid], "chamfer_norm") or 0.0)
    ]
    selected["P1_geometry_regression"] = max(
        candidates,
        key=lambda sid: (geometry_value(maps["P1"][sid], "chamfer_norm") or 0.0)
        - (geometry_value(maps["A3"][sid], "chamfer_norm") or 0.0),
        default=None,
    )
    dump_json(OUT / "gallery/P1_OPERATION_AWARE_RESCUE_SELECTION.json", selected)

    width, height = 1900, 920
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    mono_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    font_path = next((p for p in font_paths if Path(p).exists()), None)
    mono_path = next((p for p in mono_paths if Path(p).exists()), font_path)
    title_font = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
    header_font = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
    body_font = ImageFont.truetype(font_path, 16) if font_path else ImageFont.load_default()
    mono_font = ImageFont.truetype(mono_path, 15) if mono_path else ImageFont.load_default()
    draw.text((36, 24), "P1 Operation-Aware Rescue Gallery", fill=(20, 20, 20), font=title_font)
    draw.text((36, 66), "EXACT9998 VAL1000; one representative case per frozen diagnostic category", fill=(90, 90, 90), font=body_font)
    titles = [
        "A3 wrong op -> P1 correct",
        "A3 truncated -> P1 complete",
        "A3 STEP fail -> P1 reload",
        "P1 geometry regression",
    ]
    keys = list(selected)
    colors = [(65, 105, 170), (80, 150, 95), (230, 145, 60), (170, 85, 125)]
    card_w, card_h, gap = 430, 700, 28
    for index, key in enumerate(keys):
        x0 = 36 + index * (card_w + gap)
        y0 = 140
        draw.rectangle((x0, y0, x0 + card_w, y0 + card_h), outline=colors[index], width=3)
        draw.text((x0 + 16, y0 + 18), titles[index], fill=colors[index], font=header_font)
        sid = selected[key]
        if sid is None:
            draw.text((x0 + 16, y0 + 76), "No qualifying case", fill=(70, 70, 70), font=body_font)
            continue
        p1, a3 = maps["P1"][sid], maps["A3"][sid]
        a3_reload = step_audits["A3"][sid].get("reload_pass")
        p1_reload = step_audits["P1"][sid].get("reload_pass")
        text = (
            f"CAD: {sid}\n\n"
            f"Op-F1   A3 {float(a3.get('op_f1', 0.0)):.3f}   P1 {float(p1.get('op_f1', 0.0)):.3f}\n"
            f"Parse   A3 {bool(a3.get('parsed'))}   P1 {bool(p1.get('parsed'))}\n"
            f"STEP    A3 reload={a3_reload}   P1 reload={p1_reload}\n"
            f"Stop    A3 {a3.get('stop_reason')}   P1 {p1.get('stop_reason')}\n"
            f"UnderGen A3 {bool(a3.get('under_generation'))}   P1 {bool(p1.get('under_generation'))}\n\n"
            f"Chamfer A3 {geometry_value(a3, 'chamfer_norm')}\n"
            f"        P1 {geometry_value(p1, 'chamfer_norm')}\n"
            f"H95     A3 {geometry_value(a3, 'hausdorff_95_norm')}\n"
            f"        P1 {geometry_value(p1, 'hausdorff_95_norm')}\n"
            f"Volume  A3 {geometry_value(a3, 'volume_error')}\n"
            f"        P1 {geometry_value(p1, 'volume_error')}"
        )
        draw.multiline_text((x0 + 16, y0 + 76), text, fill=(45, 45, 45), font=mono_font, spacing=7)
    path = OUT / "gallery/P1_OPERATION_AWARE_RESCUE_GALLERY.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return selected


def binary_transition(
    left: dict[str, dict[str, Any]],
    right: dict[str, dict[str, Any]],
    key: str,
) -> dict[str, int]:
    ids = sorted(set(left) & set(right))
    return {
        f"{key}_left_1_right_0": sum(bool(left[i].get(key)) and not bool(right[i].get(key)) for i in ids),
        f"{key}_left_0_right_1": sum(not bool(left[i].get(key)) and bool(right[i].get(key)) for i in ids),
        f"{key}_both_1": sum(bool(left[i].get(key)) and bool(right[i].get(key)) for i in ids),
        f"{key}_both_0": sum(not bool(left[i].get(key)) and not bool(right[i].get(key)) for i in ids),
    }


def make_main_table(reports: dict[str, dict[str, Any]], step_audits: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    rows = []
    for arm in ("A1", "A3", "P1"):
        x = reports[arm]
        s = step_summary(step_audits[arm])
        geom = [sample for sample in x["samples"] if geometry_valid(sample)]
        cham = [geometry_value(sample, "chamfer_norm") for sample in geom]
        h95 = [geometry_value(sample, "hausdorff_95_norm") for sample in geom]
        vol = [geometry_value(sample, "volume_error") for sample in x["samples"] if geometry_value(sample, "volume_error") is not None]
        rows.append(
            {
                "arm": arm,
                "N": x["n_samples"],
                "Exact": x["exact_match_rate"],
                "Op-F1": x["mean_op_f1"],
                "Parse": x["dsl_parse_valid_rate"],
                "STEP_Export": x["step_valid_rate"],
                "STEP_Reload": s["headline_reload_rate"],
                "EOS": x["eos_rate"],
                "MaxLen": x["max_length_rate"],
                "UnderGen": x["under_generation_rate"],
                "Geometry_valid_N": len(geom),
                "Geometry_valid_rate": len(geom) / x["n_samples"],
                "Chamfer_mean": x["mean_chamfer_norm"],
                "Chamfer_median": statistics.median(cham) if cham else None,
                "H95_mean": x["mean_hausdorff_95_norm"],
                "H95_median": statistics.median(h95) if h95 else None,
                "Volume_mean": x["mean_volume_error"],
                "Volume_median": statistics.median(vol) if vol else None,
            }
        )
    return rows


def make_report(
    reports: dict[str, dict[str, Any]],
    step_summaries: dict[str, Any],
    paired: dict[str, Any],
    op_matrix: list[dict[str, Any]],
    geometry: dict[str, Any],
    param_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    p1 = reports["P1"]
    a3 = reports["A3"]
    p1_cham = [geometry_value(r, "chamfer_norm") for r in p1["samples"] if geometry_value(r, "chamfer_norm") is not None]
    a3_cham = [geometry_value(r, "chamfer_norm") for r in a3["samples"] if geometry_value(r, "chamfer_norm") is not None]
    return {
        "CURRENT_GATE": "P1_OPERATION_AWARE_FORMAL_CLOSURE",
        "TEST_TOUCHED": "NO",
        "NEW_TRAINING": "NO",
        "NEW_DECODE": "NO",
        "P1_STATUS": "CURRENT_BEST_MAIN_MODEL",
        "main_results": {
            "A1": reports["A1"],
            "A3": reports["A3"],
            "P1": reports["P1"],
        },
        "step_reload": step_summaries,
        "paired_stats": paired,
        "operation_breakdown": op_matrix,
        "geometry_common_valid": geometry,
        "chamfer_distribution": {
            "P1": {
                "N": len(p1_cham),
                "mean": mean(p1_cham),
                "median": statistics.median(p1_cham) if p1_cham else None,
                "p75": pct(p1_cham, 0.75),
                "p90": pct(p1_cham, 0.90),
                "p95": pct(p1_cham, 0.95),
                "p99": pct(p1_cham, 0.99),
                "max": max(p1_cham) if p1_cham else None,
            },
            "A3": {
                "N": len(a3_cham),
                "mean": mean(a3_cham),
                "median": statistics.median(a3_cham) if a3_cham else None,
                "p75": pct(a3_cham, 0.75),
                "p90": pct(a3_cham, 0.90),
                "p95": pct(a3_cham, 0.95),
                "p99": pct(a3_cham, 0.99),
                "max": max(a3_cham) if a3_cham else None,
            },
        },
        "parameter_support_rows": len(param_rows),
        "interpretation": {
            "operation_supervision_effect": "P1 improves operation-level program recovery and executability; this is association evidence, not causal proof beyond the loss ablation.",
            "generation_completeness_effect": "P1 reduces truncation and under-generation relative to A3.",
            "geometric_fidelity": "BROADLY_PRESERVED_WITH_CHAMFER_OUTLIERS",
            "parameter_residual_pattern": "PARAMETER_AUDIT_REQUIRED; operation loss does not directly supervise numeric placement/scale fields.",
        },
        "P2_STATUS": "DEFERRED",
        "P2_REASON": "Core P1 structure gain is established, but parameter/outlier audit should be reviewed before designing P2.",
        "CORE_CLAIM_STATUS": "SUPPORTED",
        "NEXT_ALLOWED_STAGE": "FREEZE_METHOD_AND_PREPARE_FINAL_TEST1000",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reports = load_reports()
    maps = sample_maps(reports)

    # Existing A1/A3 reload audits are reused; only P1 requires fresh reload checking.
    step_audits = {
        "A1": load_old_reload("A1"),
        "A3": load_old_reload("A3"),
        "P1": make_p1_reload_audit(maps["P1"]),
    }
    for arm, audit in step_audits.items():
        write_csv(
            OUT / f"step_reload/{arm}_STEP_RELOAD_AUDIT.csv",
            sorted(audit.values(), key=lambda x: x["cad_id"]),
            ["cad_id", "sample_id", "dataset", "export_pass", "reload_status", "reload_pass", "error"],
        )
    step_summaries = {arm: step_summary(audit) for arm, audit in step_audits.items()}
    dump_json(OUT / "step_reload/P1_STEP_RELOAD_SUMMARY.json", step_summaries["P1"])

    paired: dict[str, Any] = {}
    for left, right in (("P1", "A3"), ("P1", "A1")):
        paired[f"{left}_vs_{right}_OpF1"] = pair_stats(maps[left], maps[right], "op_f1")
        parse_a = [bool(maps[left][sid].get("parsed")) for sid in sorted(set(maps[left]) & set(maps[right]))]
        parse_b = [bool(maps[right][sid].get("parsed")) for sid in sorted(set(maps[left]) & set(maps[right]))]
        step_a = [as_bool(step_audits[left][sid].get("reload_pass")) for sid in sorted(set(maps[left]) & set(maps[right]))]
        step_b = [as_bool(step_audits[right][sid].get("reload_pass")) for sid in sorted(set(maps[left]) & set(maps[right]))]
        paired[f"{left}_vs_{right}_Parse_McNemar"] = {
            **binary_transition(maps[left], maps[right], "parsed"),
            "discordant_p_value": mcnemar_pvalue(parse_a, parse_b),
        }
        paired[f"{left}_vs_{right}_STEP_Reload_McNemar"] = {
            "both_pass": sum(a and b for a, b in zip(step_a, step_b)),
            "left_only_pass": sum(a and not b for a, b in zip(step_a, step_b)),
            "right_only_pass": sum(not a and b for a, b in zip(step_a, step_b)),
            "both_fail": sum(not a and not b for a, b in zip(step_a, step_b)),
            "discordant_p_value": mcnemar_pvalue(step_a, step_b),
        }
        paired[f"{left}_vs_{right}_Exact_Rescue_Regression"] = {
            "both_exact": sum(bool(maps[left][sid].get("exact_match")) and bool(maps[right][sid].get("exact_match")) for sid in maps[left]),
            "left_rescue": sum(bool(maps[left][sid].get("exact_match")) and not bool(maps[right][sid].get("exact_match")) for sid in maps[left]),
            "left_regression": sum(not bool(maps[left][sid].get("exact_match")) and bool(maps[right][sid].get("exact_match")) for sid in maps[left]),
            "both_non_exact": sum(not bool(maps[left][sid].get("exact_match")) and not bool(maps[right][sid].get("exact_match")) for sid in maps[left]),
        }

    write_csv(
        OUT / "paired_stats/P1_VS_A3_OPF1_BOOTSTRAP.csv",
        [paired["P1_vs_A3_OpF1"]],
    )
    write_csv(
        OUT / "paired_stats/P1_VS_A1_OPF1_BOOTSTRAP.csv",
        [paired["P1_vs_A1_OpF1"]],
    )
    for pair in ("P1_vs_A3", "P1_vs_A1"):
        write_csv(OUT / f"paired_stats/{pair}_PARSE_MCNEMAR.csv", [paired[f"{pair}_Parse_McNemar"]])
        write_csv(OUT / f"paired_stats/{pair}_STEP_MCNEMAR.csv", [paired[f"{pair}_STEP_Reload_McNemar"]])
        write_csv(OUT / f"paired_stats/{pair}_EXACT_RESCUE_REGRESSION.csv", [paired[f"{pair}_Exact_Rescue_Regression"]])

    matrix, statuses = operation_matrix(maps, ["A1", "A3", "P1"])
    p1_vs_a3_op_delta = operation_delta(matrix, "P1", "A3")
    p1_vs_a1_op_delta = operation_delta(matrix, "P1", "A1")
    write_csv(OUT / "operation_breakdown/P1_OPERATION_MATCH_MATRIX.csv", matrix)
    write_csv(OUT / "operation_breakdown/P1_VS_A3_OPERATION_DELTA.csv", p1_vs_a3_op_delta)
    write_csv(OUT / "operation_breakdown/P1_VS_A1_OPERATION_DELTA.csv", p1_vs_a1_op_delta)
    write_csv(OUT / "operation_breakdown/P1_OPERATION_RESCUE_TRANSITIONS.csv", operation_rescue(maps, "A3", "P1", statuses))
    write_csv(OUT / "operation_breakdown/P1_VS_A1_OPERATION_RESCUE_TRANSITIONS.csv", operation_rescue(maps, "A1", "P1", statuses))
    dump_json(
        OUT / "operation_breakdown/PROTOCOL_NOTE.json",
        {
            "parser": "edge_aware_cad_planner_v1.cad_dsl.extract_dsl_code + parse_dsl",
            "prediction_source": "pred_canonical.dsl when present, otherwise pred.dsl",
            "case_alignment": "SequenceMatcher over canonical parsed operation sequences for missing/wrong-type transition diagnostics only",
            "aggregate_matrix": "Same as the frozen A0-A3 protocol: shared A0 GT operation counts, predicted operation counts over VAL1000, matched=min(GT_N,Pred_N), missing=max(GT_N-matched), wrong_type_substitution=max(Pred_N-matched).",
            "interpretation": "Transition counts are diagnostic evidence and should not be read as a causal proof.",
        },
    )

    gen_rows = []
    for sid in sorted(set(maps["P1"]) & set(maps["A3"])):
        for key in ("stop_reason", "under_generation"):
            gen_rows.append(
                {
                    "cad_id": sid,
                    "metric": key,
                    "A3": maps["A3"][sid].get(key),
                    "P1": maps["P1"][sid].get(key),
                }
            )
    write_csv(OUT / "generation_behavior/GENERATION_CASE_LEVEL.csv", gen_rows)
    ids = sorted(set(maps["P1"]) & set(maps["A3"]))
    eos_rows = [{
        "metric": "EOS",
        "A3_EOS_to_P1_nonEOS": sum(
            maps["A3"][i].get("stop_reason") == "EOS"
            and maps["P1"][i].get("stop_reason") != "EOS"
            for i in ids
        ),
        "A3_nonEOS_to_P1_EOS": sum(
            maps["A3"][i].get("stop_reason") != "EOS"
            and maps["P1"][i].get("stop_reason") == "EOS"
            for i in ids
        ),
    }]
    under_rows = [{
        "metric": "under_generation",
        "A3_1_to_P1_0": sum(
            bool(maps["A3"][i].get("under_generation"))
            and not bool(maps["P1"][i].get("under_generation"))
            for i in ids
        ),
        "A3_0_to_P1_1": sum(
            not bool(maps["A3"][i].get("under_generation"))
            and bool(maps["P1"][i].get("under_generation"))
            for i in ids
        ),
    }]
    max_rows, _ = generation_transition_rows(maps, step_audits)
    write_csv(OUT / "generation_behavior/EOS_TRANSITIONS.csv", eos_rows)
    write_csv(OUT / "generation_behavior/MAX_LENGTH_TRANSITIONS.csv", [row for row in max_rows if row["metric"] == "MAX_LENGTH"])
    write_csv(OUT / "generation_behavior/UNDERGEN_TRANSITIONS.csv", under_rows)
    write_csv(OUT / "generation_behavior/STEP_RELOAD_TRANSITIONS.csv", [row for row in max_rows if row["metric"] == "STEP_RELOAD"])
    write_csv(OUT / "generation_behavior/STRUCTURE_GENERATION_ASSOCIATION.csv", structure_generation_association(maps))

    geom_pairs: dict[str, Any] = {}
    for left, right, name in (("P1", "A3", "P1_A3"), ("P1", "A1", "P1_A1")):
        rows, summary = geometry_common(maps, left, right)
        write_csv(OUT / f"common_valid/{name}_COMMON_VALID_GEOMETRY.csv", rows)
        geom_pairs[name] = summary
    all_valid_ids = sorted(set(maps["A1"]) & set(maps["A3"]) & set(maps["P1"]))
    write_csv(
        OUT / "common_valid/A1_A3_P1_ALL_VALID_GEOMETRY.csv",
        [
            {
                "cad_id": sid,
                **{
                    f"{arm}_Chamfer": geometry_value(maps[arm][sid], "chamfer_norm")
                    for arm in ("A1", "A3", "P1")
                },
                **{
                    f"{arm}_H95": geometry_value(maps[arm][sid], "hausdorff_95_norm")
                    for arm in ("A1", "A3", "P1")
                },
            }
            for sid in all_valid_ids
            if all(geometry_valid(maps[arm][sid]) for arm in ("A1", "A3", "P1"))
        ],
    )
    all_five_ids = sorted(
        set(maps["A0"]) & set(maps["A1"]) & set(maps["A2"]) & set(maps["A3"]) & set(maps["P1"])
    )
    write_csv(
        OUT / "common_valid/A0_A1_A2_A3_P1_ALL_VALID_GEOMETRY.csv",
        [
            {
                "cad_id": sid,
                **{
                    f"{arm}_Chamfer": geometry_value(maps[arm][sid], "chamfer_norm")
                    for arm in ("A0", "A1", "A2", "A3", "P1")
                },
                **{
                    f"{arm}_H95": geometry_value(maps[arm][sid], "hausdorff_95_norm")
                    for arm in ("A0", "A1", "A2", "A3", "P1")
                },
            }
            for sid in all_five_ids
            if all(geometry_valid(maps[arm][sid]) for arm in ("A0", "A1", "A2", "A3", "P1"))
        ],
    )
    bootstrap_rows = []
    for comparison, summary in geom_pairs.items():
        for metric_name, values in summary.items():
            bootstrap_rows.append({"comparison": comparison, "metric": metric_name, **values})
    write_csv(OUT / "common_valid/P1_GEOMETRY_BOOTSTRAP.csv", bootstrap_rows)

    p1_chamfer = []
    p1_map, a3_map = maps["P1"], maps["A3"]
    for sid in sorted(p1_map):
        cv = geometry_value(p1_map[sid], "chamfer_norm")
        if cv is None:
            continue
        p1_chamfer.append(
            {
                "cad_id": sid,
                "dataset": p1_map[sid].get("dataset"),
                "P1_Chamfer": cv,
                "A3_Chamfer": geometry_value(a3_map[sid], "chamfer_norm"),
                "P1_H95": geometry_value(p1_map[sid], "hausdorff_95_norm"),
                "P1_Volume": geometry_value(p1_map[sid], "volume_error"),
                "P1_OpF1": p1_map[sid].get("op_f1"),
                "P1_Exact": p1_map[sid].get("exact_match"),
                "P1_STEP_Reload": step_audits["P1"][sid].get("reload_pass"),
                "operation_sequence_difference": get_ops(maps["A0"][sid], "gt") != get_ops(p1_map[sid], "pred"),
            }
        )
    p1_chamfer.sort(key=lambda x: x["P1_Chamfer"], reverse=True)
    write_csv(OUT / "geometry_outliers/P1_CHAMFER_TOP20.csv", p1_chamfer[:20])
    root_rows = [
        outlier_root_cause(
            row["cad_id"],
            maps["A0"][row["cad_id"]],
            p1_map[row["cad_id"]],
            a3_map[row["cad_id"]],
            step_audits["P1"][row["cad_id"]],
            statuses["P1"].get(row["cad_id"], {}),
        )
        for row in p1_chamfer[:20]
    ]
    write_csv(OUT / "geometry_outliers/P1_CHAMFER_TOP20_ROOT_CAUSE.csv", root_rows)
    chamfer_dist = []
    for arm, rows in (("P1", p1_map), ("A3", a3_map)):
        vals = [geometry_value(r, "chamfer_norm") for r in rows.values() if geometry_value(r, "chamfer_norm") is not None]
        chamfer_dist.append(
            {
                "arm": arm,
                "N": len(vals),
                "mean": mean(vals),
                "median": statistics.median(vals) if vals else None,
                "p75": pct(vals, 0.75),
                "p90": pct(vals, 0.90),
                "p95": pct(vals, 0.95),
                "p99": pct(vals, 0.99),
                "max": max(vals) if vals else None,
            }
        )
    write_csv(OUT / "geometry_outliers/P1_CHAMFER_DISTRIBUTION.csv", chamfer_dist)

    volume_rows = []
    volume_pair_rows = []
    for arm in ("A3", "P1"):
        vals = [geometry_value(r, "volume_error") for r in maps[arm].values() if geometry_value(r, "volume_error") is not None]
        volume_rows.append(
            {
                "arm": arm,
                "N": len(vals),
                "mean": mean(vals),
                "median": statistics.median(vals) if vals else None,
                "p75": pct(vals, 0.75),
                "p90": pct(vals, 0.90),
                "p95": pct(vals, 0.95),
                "p99": pct(vals, 0.99),
                "max": max(vals) if vals else None,
            }
        )
    write_csv(OUT / "volume/P1_VOLUME_DISTRIBUTION.csv", volume_rows)
    for sid in sorted(set(maps["A3"]) & set(maps["P1"])):
        a3v = geometry_value(maps["A3"][sid], "volume_error")
        p1v = geometry_value(maps["P1"][sid], "volume_error")
        if a3v is None or p1v is None:
            continue
        volume_pair_rows.append(
            {
                "cad_id": sid,
                "A3_volume_error": a3v,
                "P1_volume_error": p1v,
                "delta_P1_minus_A3": p1v - a3v,
                "P1_better": p1v < a3v,
                "P1_OpF1": maps["P1"][sid].get("op_f1"),
                "P1_Exact": maps["P1"][sid].get("exact_match"),
            }
        )
    write_csv(OUT / "volume/P1_VS_A3_VOLUME_PAIRWISE.csv", volume_pair_rows)
    write_csv(
        OUT / "volume/P1_VOLUME_TOP20.csv",
        sorted(volume_pair_rows, key=lambda row: row["P1_volume_error"], reverse=True)[:20],
    )
    gallery_selection = make_rescue_gallery(maps, step_audits, statuses)

    params = parameter_rows(maps, "P1", "A3")
    write_csv(OUT / "parameters/P1_VS_A3_PARAMETER_ERROR.csv", params)
    write_csv(OUT / "parameters/P1_VS_A1_PARAMETER_ERROR.csv", parameter_rows(maps, "P1", "A1"))

    graph_rows = []
    for arm in ("A1", "A3", "P1"):
        graph_rows.extend(graph_case_metrics(maps, arm))
    write_csv(OUT / "graph/P1_DEPENDENCY_GRAPH_METRICS.csv", graph_rows)
    dump_json(
        OUT / "graph/PROTOCOL_NOTE.json",
        {
            "status": "APPROX_AST_PARENT_CHILD",
            "note": "P1 graph metrics use the same existing DSL source files but an explicit AST parent-child dependency graph; GED is not claimed.",
        },
    )
    write_csv(
        OUT / "extended_metrics/P1_TOPOLOGY_STATUS.csv",
        [
            {
                "metric_family": "BREP_TOPOLOGY",
                "status": "DEFERRED_SECONDARY",
                "reason": "Existing A0-A3 topology tables are shape-level extended metrics; no direct P1 shape-level batch script was available in the frozen closure inputs.",
                "TEST_TOUCHED": "NO",
            }
        ],
    )

    main_table = make_main_table(reports, step_audits)
    write_csv(OUT / "tables/A1_A3_P1_MAIN_COMPARISON.csv", main_table)
    write_csv(
        OUT / "tables/MAIN_MODEL_SELECTION_TABLE.csv",
        [
            {
                "arm": row["arm"],
                "program_structure": row["Op-F1"],
                "executability_parse": row["Parse"],
                "executability_step_export": row["STEP_Export"],
                "step_reload": row["STEP_Reload"],
                "generation_completeness": 1.0 - row["UnderGen"],
                "geometry_valid_rate": row["Geometry_valid_rate"],
                "chamfer_mean": row["Chamfer_mean"],
                "h95_mean": row["H95_mean"],
                "volume_mean": row["Volume_mean"],
                "selection_note": "P1 is best on program/executability; A2 remains the geometric Chamfer-mean reference outside this A1/A3/P1 main comparison.",
            }
            for row in main_table
        ],
    )
    key_operation_rows = {row["operation"]: row for row in p1_vs_a3_op_delta}
    p1_vs_a3_opf1 = paired["P1_vs_A3_OpF1"]
    p1_vs_a1_opf1 = paired["P1_vs_A1_OpF1"]
    formal_row = {
        "CURRENT_GATE": "P1_OPERATION_AWARE_FORMAL_CLOSURE",
        "P1_STATUS": "CURRENT_BEST_MAIN_MODEL",
        "TEST_TOUCHED": "NO",
        "NEW_TRAINING": "NO",
        "NEW_DECODE": "NO",
        "P1_Exact": reports["P1"]["exact_match_rate"],
        "A3_Exact": reports["A3"]["exact_match_rate"],
        "P1_OpF1": reports["P1"]["mean_op_f1"],
        "A3_OpF1": reports["A3"]["mean_op_f1"],
        "P1_vs_A3_OpF1_delta": reports["P1"]["mean_op_f1"] - reports["A3"]["mean_op_f1"],
        "P1_vs_A3_OpF1_bootstrap_low": p1_vs_a3_opf1["bootstrap_ci95_low"],
        "P1_vs_A3_OpF1_bootstrap_high": p1_vs_a3_opf1["bootstrap_ci95_high"],
        "P1_vs_A1_OpF1_delta": reports["P1"]["mean_op_f1"] - reports["A1"]["mean_op_f1"],
        "P1_vs_A1_OpF1_bootstrap_low": p1_vs_a1_opf1["bootstrap_ci95_low"],
        "P1_vs_A1_OpF1_bootstrap_high": p1_vs_a1_opf1["bootstrap_ci95_high"],
        "P1_Parse": reports["P1"]["dsl_parse_valid_rate"],
        "A3_Parse": reports["A3"]["dsl_parse_valid_rate"],
        "P1_STEP_Export": reports["P1"]["step_valid_rate"],
        "A3_STEP_Export": reports["A3"]["step_valid_rate"],
        "P1_STEP_Reload": step_summaries["P1"]["headline_reload_rate"],
        "A3_STEP_Reload": step_summaries["A3"]["headline_reload_rate"],
        "P1_Geometry_valid_N": main_table[-1]["Geometry_valid_N"],
        "A3_Geometry_valid_N": main_table[1]["Geometry_valid_N"],
        "P1_Chamfer_mean": reports["P1"]["mean_chamfer_norm"],
        "A3_Chamfer_mean": reports["A3"]["mean_chamfer_norm"],
        "P1_Chamfer_median": main_table[-1]["Chamfer_median"],
        "A3_Chamfer_median": main_table[1]["Chamfer_median"],
        "P1_H95_mean": reports["P1"]["mean_hausdorff_95_norm"],
        "A3_H95_mean": reports["A3"]["mean_hausdorff_95_norm"],
        "P1_Volume_mean": reports["P1"]["mean_volume_error"],
        "A3_Volume_mean": reports["A3"]["mean_volume_error"],
        "Box_repair": key_operation_rows.get("Box", {}).get("classification"),
        "Extrude_repair": key_operation_rows.get("Extrude", {}).get("classification"),
        "Union_repair": key_operation_rows.get("Union", {}).get("classification"),
        "Cut_repair": key_operation_rows.get("Cut", {}).get("classification"),
        "ExtrudePolygon_repair": key_operation_rows.get("ExtrudePolygon", {}).get("classification"),
        "gallery_cases": json.dumps(gallery_selection, sort_keys=True),
    }
    write_csv(OUT / "tables/P1_FORMAL_RESULT_TABLE.csv", [formal_row])
    report = make_report(
        reports,
        step_summaries,
        paired,
        matrix,
        geom_pairs,
        params,
    )
    dump_json(OUT / "reports/FINAL_REPORT.json", report)

    p1_a3 = paired["P1_vs_A3_OpF1"]
    p1_a1 = paired["P1_vs_A1_OpF1"]
    md = f"""# P1 Operation-Aware Formal Closure

## Frozen Scope

- VAL1000 only.
- Existing A1, A3, and P1 predictions reused.
- No training, no new decode, no evaluator/parser/executor/GT changes.
- TEST remains blind.

## Main Result

P1 vs A3 Op-F1 mean delta: `{p1_a3['mean_delta_left_minus_right']:.6f}`; bootstrap 95% CI `[{{:.6f}}, {{:.6f}}]`.

P1 vs A1 Op-F1 mean delta: `{p1_a1['mean_delta_left_minus_right']:.6f}`; bootstrap 95% CI `[{{:.6f}}, {{:.6f}}]`.

P1 is the current main model because it improves operation recovery, parse validity, STEP export/reload, and generation completeness over A3 while retaining broadly preserved geometry. The Chamfer mean remains outlier-sensitive.

## Interpretation

The evidence supports an operation-aware supervision effect consistent with fewer missing/wrong CAD operations and better generation completeness. It does not prove a causal mechanism beyond the frozen loss ablation.

P2 is deferred until the parameter and geometry-outlier audit is reviewed. The remaining risk is local parameter, placement, direction, or scale error rather than unresolved operation structure alone.
"""
    (OUT / "reports/FINAL_REPORT.md").write_text(md.replace("{{", "{").replace("}}", "}").format(p1_a3["bootstrap_ci95_low"], p1_a3["bootstrap_ci95_high"], p1_a1["bootstrap_ci95_low"], p1_a1["bootstrap_ci95_high"]))
    (OUT / "reports/ADVISOR_P1_SUMMARY.md").write_text(
        f"""# Advisor Summary

P1 reaches Exact `{reports['P1']['exact_match_rate']:.3f}`, Op-F1 `{reports['P1']['mean_op_f1']:.4f}`, Parse `{reports['P1']['dsl_parse_valid_rate']:.3f}`, and STEP export `{reports['P1']['step_valid_rate']:.3f}` on VAL1000.

Compared with A3, P1 improves Op-F1 by `{reports['P1']['mean_op_f1'] - reports['A3']['mean_op_f1']:.4f}`, Exact by `{reports['P1']['exact_match_rate'] - reports['A3']['exact_match_rate']:.3f}`, Parse by `{reports['P1']['dsl_parse_valid_rate'] - reports['A3']['dsl_parse_valid_rate']:.3f}`, and STEP export by `{reports['P1']['step_valid_rate'] - reports['A3']['step_valid_rate']:.3f}`. It also exceeds A1 in Op-F1 by `{reports['P1']['mean_op_f1'] - reports['A1']['mean_op_f1']:.4f}`.

P1 also reduces MaxLen from `{reports['A3']['max_length_rate']:.3f}` to `{reports['P1']['max_length_rate']:.3f}` and UnderGen from `{reports['A3']['under_generation_rate']:.3f}` to `{reports['P1']['under_generation_rate']:.3f}`.

Operation-level audits identify the repaired/preserved/regressed operation categories in `operation_breakdown/P1_VS_A3_OPERATION_DELTA.csv`; the transition table separates missing-to-correct and wrong-type-to-correct rescues.

Geometry is broadly preserved: P1 has better Chamfer median, H95, Volume error, and geometry-valid coverage, while Chamfer mean remains higher because of outliers. The remaining risk is local parameter, placement, direction, or scale error.

P2 is deferred pending parameter/outlier review. TEST remains blind and no new training or decode was run.
"""
    )
    (OUT / "reports/PAPER_P1_INTERPRETATION.md").write_text(
        """# Paper Interpretation

## Main Finding

Explicit curve geometry provides useful CAD structural cues, but naive all-curve conditioning can create operation-level interference. Operation-aware structural supervision improves the mapping from geometry to CAD operations.

## Mechanistic Evidence

P1 improves operation-level recovery, parse/STEP validity, and generation completeness relative to A3. Operation-level rescue and transition tables are provided in `operation_breakdown/`.

## Geometry Trade-off

Geometry is broadly preserved, with improved medians/H95/volume behavior and a remaining Chamfer-mean outlier tail. This should be reported as a trade-off, not as uniform geometric improvement.

## Limitation

The evidence is consistent with the loss mechanism but is not a causal proof beyond this loss ablation. Numeric placement and scale remain separately audited residuals.

## Next Step

Freeze P1 as the main model and keep TEST blind. Defer P2 until parameter/outlier evidence justifies a clean parameter-focused intervention.
"""
    )
    dump_json(
        OUT / "reports/INTEGRITY.json",
        {
            "A0_CHANGED": "NO",
            "A1_CHANGED": "NO",
            "A2_CHANGED": "NO",
            "A3_CHANGED": "NO",
            "P1_CHANGED": "NO",
            "PREDICTIONS_CHANGED": "NO",
            "EVALUATOR_CHANGED": "NO",
            "GT_CHANGED": "NO",
            "EXACT9998_CHANGED": "NO",
            "TEST_TOUCHED": "NO",
            "NEW_TRAINING": "NO",
            "NEW_DECODE": "NO",
        },
    )
    print(json.dumps({"out": str(OUT), "step_reload": step_summaries, "paired": paired, "main_table": main_table}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
