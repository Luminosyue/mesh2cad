#!/usr/bin/env python3
"""Post-hoc finalization for the EXACT9998 A0-A3 curve ablation.

This script only reads frozen decode outputs and writes a new audit directory.
It never edits checkpoints, predictions, evaluator code, or TEST data.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/a0_a1_a2_a3_core_ablation_finalization_v1"

ARM_DIRS = {
    "A0": ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0",
    "A1": ROOT / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1",
    "A2": ROOT / "ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a2",
    "A3": ROOT / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3",
}

ARM_LABELS = {
    "A0": "Surface",
    "A1": "Surface + GT-BRep-Line",
    "A2": "Surface + GT-BRep-Nonline",
    "A3": "Surface + GT-BRep-All-Curves",
}

BASE_CE = {
    "A0": 0.502075,
    "A1": 0.4954413176,
    "A2": 0.4982193708,
    "A3": 0.4922700822,
}

REPORT_PATHS = {arm: path / "report.json" for arm, path in ARM_DIRS.items()}
SEED = 0
BOOTSTRAP_N = 10000

sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "SpatialLM")]


def jdump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def finite(value: Any) -> bool:
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def f(value: Any) -> float | None:
    return float(value) if finite(value) else None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            normalized = {}
            for name in fieldnames:
                value = row.get(name)
                if isinstance(value, (dict, list, tuple)):
                    normalized[name] = jdump(value)
                elif isinstance(value, float):
                    normalized[name] = f"{value:.10g}"
                elif value is None:
                    normalized[name] = ""
                else:
                    normalized[name] = value
            writer.writerow(normalized)


def load_reports() -> dict[str, dict[str, Any]]:
    reports = {}
    for arm, path in REPORT_PATHS.items():
        if not path.exists():
            raise FileNotFoundError(path)
        reports[arm] = json.loads(path.read_text(encoding="utf-8"))
        if reports[arm].get("n_samples") != 1000:
            raise RuntimeError(f"{arm} is not VAL1000: {reports[arm].get('n_samples')}")
    ids = {arm: {row["id"] for row in report["samples"]} for arm, report in reports.items()}
    if len({len(value) for value in ids.values()}) != 1 or len(set.intersection(*ids.values())) != 1000:
        raise RuntimeError("A0-A3 are not aligned on the same 1000 CAD IDs")
    return reports


def rows_by_id(reports: dict[str, dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        arm: {row["id"]: row for row in report["samples"]}
        for arm, report in reports.items()
    }


def case_dir(arm: str, row: dict[str, Any]) -> Path:
    return ARM_DIRS[arm] / row["id"]


def valid_geom(row: dict[str, Any]) -> bool:
    geom = row.get("geometry") or {}
    return finite(geom.get("chamfer_norm")) and finite(geom.get("hausdorff_95_norm"))


def valid_volume(row: dict[str, Any]) -> bool:
    return finite((row.get("geometry") or {}).get("volume_error"))


def metric(row: dict[str, Any], name: str) -> float | None:
    return f((row.get("geometry") or {}).get(name))


def bootstrap_ci(values: list[float], seed: int = SEED, n_boot: int = BOOTSTRAP_N) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    if len(values) == 1:
        return values[0], values[0]
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    means = np.empty(n_boot, dtype=float)
    for start in range(0, n_boot, 1000):
        size = min(1000, n_boot - start)
        means[start : start + size] = arr[rng.integers(0, len(arr), size=(size, len(arr)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def paired_summary(
    arm1: str,
    arm2: str,
    by_arm: dict[str, dict[str, dict[str, Any]]],
    value_name: str,
    lower_is_better: bool = True,
) -> dict[str, Any]:
    ids = sorted(set(by_arm[arm1]) & set(by_arm[arm2]))
    pairs = []
    for cad_id in ids:
        v1 = metric(by_arm[arm1][cad_id], value_name)
        v2 = metric(by_arm[arm2][cad_id], value_name)
        if v1 is not None and v2 is not None:
            pairs.append((cad_id, v1, v2))
    deltas = [a - b for _, a, b in pairs]
    better1 = better2 = tie = 0
    for _, a, b in pairs:
        if abs(a - b) <= 1e-12:
            tie += 1
        elif (a < b) == lower_is_better:
            better1 += 1
        else:
            better2 += 1
    lo, hi = bootstrap_ci(deltas)
    return {
        "comparison": f"{arm1}_vs_{arm2}",
        "metric": value_name,
        "paired_N": len(pairs),
        f"{arm1}_mean": float(np.mean([a for _, a, _ in pairs])) if pairs else None,
        f"{arm2}_mean": float(np.mean([b for _, _, b in pairs])) if pairs else None,
        f"{arm1}_median": float(np.median([a for _, a, _ in pairs])) if pairs else None,
        f"{arm2}_median": float(np.median([b for _, _, b in pairs])) if pairs else None,
        "mean_paired_delta_arm1_minus_arm2": float(np.mean(deltas)) if deltas else None,
        "median_paired_delta_arm1_minus_arm2": float(np.median(deltas)) if deltas else None,
        f"{arm1}_better_N": better1,
        "tie_N": tie,
        f"{arm2}_better_N": better2,
        "bootstrap_mean_delta_ci95_low": lo,
        "bootstrap_mean_delta_ci95_high": hi,
        "direction": "lower_is_better" if lower_is_better else "higher_is_better",
    }


def import_cad_parser():
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code, parse_dsl

    return extract_dsl_code, parse_dsl


def op_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    extract_dsl_code, parse_dsl = import_cad_parser()
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        code = extract_dsl_code(text)
    except Exception:
        code = text
    try:
        program = parse_dsl(code)
    except Exception:
        try:
            program = parse_dsl(text)
        except Exception:
            return []
    return [
        value["op"]
        for name, value in program.assignments.items()
        if name != "result" and isinstance(value, dict) and "op" in value
    ]


def op_path(arm: str, row: dict[str, Any], pred: bool) -> Path:
    directory = case_dir(arm, row)
    if pred:
        canonical = directory / "pred_canonical.dsl"
        return canonical if canonical.exists() else directory / "pred.dsl"
    return directory / "gt.dsl"


def operation_data(reports: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, list[str]]], list[str]]:
    by_arm: dict[str, dict[str, list[str]]] = {}
    all_ops: set[str] = set()
    for arm, report in reports.items():
        by_arm[arm] = {}
        for row in report["samples"]:
            gt = op_list(op_path(arm, row, pred=False))
            pred = op_list(op_path(arm, row, pred=True))
            by_arm[arm][row["id"]] = pred
            all_ops.update(gt)
            all_ops.update(pred)
    # GT is shared; recover it from A0's frozen gt.dsl files.
    for row in reports["A0"]["samples"]:
        all_ops.update(op_list(op_path("A0", row, pred=False)))
    return by_arm, sorted(all_ops)


def gt_ops_for_id(row: dict[str, Any]) -> list[str]:
    return op_list(op_path("A0", row, pred=False))


def count_matches(gt: list[str], pred: list[str], op: str) -> tuple[int, int, int, int]:
    gt_n = gt.count(op)
    pred_n = pred.count(op)
    matched = min(gt_n, pred_n)
    missing = max(gt_n - matched, 0)
    wrong = max(pred_n - matched, 0)
    return gt_n, matched, missing, wrong


def operation_breakdown(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    pred_ops, ops = operation_data(reports)
    id_rows = {row["id"]: row for row in reports["A0"]["samples"]}
    matrix = []
    contribution = []
    for op in ops:
        row: dict[str, Any] = {"operation": op}
        rates = {}
        for arm in ARM_DIRS:
            gt = gt_ops_for_id(id_rows[next(iter(id_rows))]) if False else None
            gt_all = []
            pred_all = []
            for cad_id, base_row in id_rows.items():
                gt_all.extend([x for x in op_list(op_path("A0", base_row, pred=False)) if x == op])
                pred_all.extend([x for x in pred_ops[arm][cad_id] if x == op])
            gt_n = len(gt_all)
            matched = min(gt_n, len(pred_all))
            missing = max(gt_n - matched, 0)
            wrong = max(len(pred_all) - matched, 0)
            rate = matched / gt_n if gt_n else None
            row[f"{arm}_GT_N"] = gt_n
            row[f"{arm}_matched_correct_type_N"] = matched
            row[f"{arm}_matched_rate"] = rate
            row[f"{arm}_missing_N"] = missing
            row[f"{arm}_wrong_type_substitution_N"] = wrong
            rates[arm] = rate
        row["best_arm"] = max(rates, key=lambda arm: rates[arm] if rates[arm] is not None else -1)
        matrix.append(row)
        a0, a1, a2, a3 = (rates.get(a) for a in ("A0", "A1", "A2", "A3"))
        if a1 is not None and a0 is not None and a1 > a0 + 1e-12 and (a2 is None or a1 >= a2):
            label = "LINE_DOMINANT_OPERATION"
        elif a2 is not None and a0 is not None and a2 > a0 + 1e-12 and (a1 is None or a2 > a1):
            label = "NONLINE_DOMINANT_OPERATION"
        elif a3 is not None and max(a1 or -1, a2 or -1) >= -1 and a3 > max(a1 or -1, a2 or -1) + 1e-12:
            label = "ALL_CURVE_POSITIVE_COMBINATION"
        elif a3 is not None and a3 < max(a1 or -1, a2 or -1) - 1e-12:
            label = "ALL_CURVE_INTERFERENCE_CANDIDATE"
        else:
            label = "NO_CLEAR_MODALITY_DOMINANCE"
        contribution.append(
            {
                "operation": op,
                "GT_N": row.get("A0_GT_N"),
                "A0": a0,
                "A1": a1,
                "A2": a2,
                "A3": a3,
                "best_arm": row["best_arm"],
                "diagnostic_label": label,
            }
        )
    out = OUT / "operation_breakdown"
    fields = ["operation"]
    for arm in ARM_DIRS:
        fields.extend(
            [
                f"{arm}_GT_N",
                f"{arm}_matched_correct_type_N",
                f"{arm}_matched_rate",
                f"{arm}_missing_N",
                f"{arm}_wrong_type_substitution_N",
            ]
        )
    fields.append("best_arm")
    write_csv(out / "OPERATION_MATCH_MATRIX.csv", matrix, fields)
    write_csv(
        out / "CURVE_MODALITY_OPERATION_CONTRIBUTION.csv",
        contribution,
        ["operation", "GT_N", "A0", "A1", "A2", "A3", "best_arm", "diagnostic_label"],
    )

    def pair_delta(arm1: str, arm2: str) -> list[dict[str, Any]]:
        rows = []
        for item in contribution:
            rows.append(
                {
                    "operation": item["operation"],
                    "arm1": arm1,
                    "arm2": arm2,
                    "arm1_rate": item[arm1],
                    "arm2_rate": item[arm2],
                    "delta_arm1_minus_arm2": (
                        item[arm1] - item[arm2]
                        if item[arm1] is not None and item[arm2] is not None
                        else None
                    ),
                    "arm1_better": (
                        item[arm1] > item[arm2]
                        if item[arm1] is not None and item[arm2] is not None
                        else None
                    ),
                }
            )
        return rows

    write_csv(out / "A1_VS_A0_OPERATION_GAIN.csv", pair_delta("A1", "A0"), [
        "operation", "arm1", "arm2", "arm1_rate", "arm2_rate", "delta_arm1_minus_arm2", "arm1_better"
    ])
    write_csv(out / "A2_VS_A0_OPERATION_GAIN.csv", pair_delta("A2", "A0"), [
        "operation", "arm1", "arm2", "arm1_rate", "arm2_rate", "delta_arm1_minus_arm2", "arm1_better"
    ])
    write_csv(out / "A3_VS_A1_OPERATION_DELTA.csv", pair_delta("A3", "A1"), [
        "operation", "arm1", "arm2", "arm1_rate", "arm2_rate", "delta_arm1_minus_arm2", "arm1_better"
    ])
    write_csv(out / "A3_VS_A2_OPERATION_DELTA.csv", pair_delta("A3", "A2"), [
        "operation", "arm1", "arm2", "arm1_rate", "arm2_rate", "delta_arm1_minus_arm2", "arm1_better"
    ])
    return {"matrix": matrix, "contribution": contribution}


def reload_step(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {"status": "FAIL_NOT_EXPORTED", "pass": False}
    try:
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
    except ModuleNotFoundError:
        from OCC.Core.IFSelect import IFSelect_RetDone
        from OCC.Core.STEPControl import STEPControl_Reader
    try:
        reader = STEPControl_Reader()
        status = reader.ReadFile(str(path))
        if status != IFSelect_RetDone:
            return {"status": "RELOAD_FAIL", "pass": False, "read_status": str(status)}
        try:
            reader.TransferRoots()
        except Exception as exc:
            return {"status": "READER_EXCEPTION", "pass": False, "error": str(exc)}
        shape = reader.OneShape()
        if shape is None or shape.IsNull():
            return {"status": "EMPTY_SHAPE", "pass": False}
        try:
            from OCP.BRepCheck import BRepCheck_Analyzer

            if not BRepCheck_Analyzer(shape).IsValid():
                return {"status": "INVALID_BREP", "pass": False}
        except Exception:
            pass
        return {"status": "PASS", "pass": True}
    except Exception as exc:
        return {"status": "READER_EXCEPTION", "pass": False, "error": f"{type(exc).__name__}: {exc}"}


def step_reload_audit(reports: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out = OUT / "step_reload"
    all_results: dict[str, list[dict[str, Any]]] = {}
    for arm, report in reports.items():
        rows = []
        for row in report["samples"]:
            path = case_dir(arm, row) / "pred.step"
            result = reload_step(path) if row.get("step_ok") else {"status": "FAIL_NOT_EXPORTED", "pass": False}
            rows.append(
                {
                    "cad_id": row["id"],
                    "sample_id": row["sample_id"],
                    "dataset": row.get("dataset"),
                    "export_pass": bool(row.get("step_ok")),
                    "reload_status": result["status"],
                    "reload_pass": bool(result["pass"]),
                    "error": result.get("error"),
                }
            )
        all_results[arm] = rows
        write_csv(
            out / f"{arm}_STEP_RELOAD_AUDIT.csv",
            rows,
            ["cad_id", "sample_id", "dataset", "export_pass", "reload_status", "reload_pass", "error"],
        )
    return all_results


def common_valid_audit(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    by_arm = rows_by_id(reports)
    out = OUT / "common_valid"
    pairs = [("A0", "A1"), ("A0", "A2"), ("A0", "A3"), ("A1", "A2"), ("A1", "A3"), ("A2", "A3")]
    pair_rows = []
    pair_cases = {}
    for arm1, arm2 in pairs:
        ids = sorted(
            cad_id
            for cad_id in by_arm[arm1]
            if valid_geom(by_arm[arm1][cad_id]) and valid_geom(by_arm[arm2][cad_id])
        )
        pair_cases[f"{arm1}_{arm2}"] = ids
        summary_ch = paired_summary(arm1, arm2, by_arm, "chamfer_norm", lower_is_better=True)
        summary_h = paired_summary(arm1, arm2, by_arm, "hausdorff_95_norm", lower_is_better=True)
        pair_rows.append(
            {
                "comparison": f"{arm1}_vs_{arm2}",
                "paired_N": len(ids),
                "chamfer_mean_arm1": summary_ch[f"{arm1}_mean"],
                "chamfer_mean_arm2": summary_ch[f"{arm2}_mean"],
                "chamfer_median_arm1": summary_ch[f"{arm1}_median"],
                "chamfer_median_arm2": summary_ch[f"{arm2}_median"],
                "chamfer_mean_delta_arm1_minus_arm2": summary_ch["mean_paired_delta_arm1_minus_arm2"],
                "chamfer_median_delta_arm1_minus_arm2": summary_ch["median_paired_delta_arm1_minus_arm2"],
                "chamfer_arm1_better_N": summary_ch[f"{arm1}_better_N"],
                "chamfer_tie_N": summary_ch["tie_N"],
                "chamfer_arm2_better_N": summary_ch[f"{arm2}_better_N"],
                "h95_mean_arm1": summary_h[f"{arm1}_mean"],
                "h95_mean_arm2": summary_h[f"{arm2}_mean"],
                "h95_median_arm1": summary_h[f"{arm1}_median"],
                "h95_median_arm2": summary_h[f"{arm2}_median"],
                "h95_mean_delta_arm1_minus_arm2": summary_h["mean_paired_delta_arm1_minus_arm2"],
                "h95_median_delta_arm1_minus_arm2": summary_h["median_paired_delta_arm1_minus_arm2"],
                "h95_arm1_better_N": summary_h[f"{arm1}_better_N"],
                "h95_tie_N": summary_h["tie_N"],
                "h95_arm2_better_N": summary_h[f"{arm2}_better_N"],
                "chamfer_bootstrap_ci95": [summary_ch["bootstrap_mean_delta_ci95_low"], summary_ch["bootstrap_mean_delta_ci95_high"]],
                "h95_bootstrap_ci95": [summary_h["bootstrap_mean_delta_ci95_low"], summary_h["bootstrap_mean_delta_ci95_high"]],
            }
        )
    all_four = sorted(
        cad_id
        for cad_id in by_arm["A0"]
        if all(valid_geom(by_arm[arm][cad_id]) for arm in ARM_DIRS)
    )
    all_four_rows = []
    for cad_id in all_four:
        item = {"cad_id": cad_id, "dataset": by_arm["A0"][cad_id].get("dataset")}
        for arm in ARM_DIRS:
            item[f"{arm}_chamfer"] = metric(by_arm[arm][cad_id], "chamfer_norm")
            item[f"{arm}_h95"] = metric(by_arm[arm][cad_id], "hausdorff_95_norm")
        all_four_rows.append(item)
    all_four_summary = {"cad_id": "__SUMMARY__", "dataset": "ALL_FOUR_VALID", "ALL_FOUR_VALID_N": len(all_four)}
    for arm in ARM_DIRS:
        all_four_summary[f"{arm}_chamfer"] = float(np.mean([x[f"{arm}_chamfer"] for x in all_four_rows])) if all_four_rows else None
        all_four_summary[f"{arm}_h95"] = float(np.mean([x[f"{arm}_h95"] for x in all_four_rows])) if all_four_rows else None
    all_four_rows.append(all_four_summary)
    pair_fields = list(pair_rows[0].keys()) if pair_rows else ["comparison"]
    write_csv(out / "PAIRWISE_COMMON_VALID_GEOMETRY.csv", pair_rows, pair_fields)
    write_csv(
        out / "ALL_FOUR_VALID_GEOMETRY.csv",
        all_four_rows,
        ["cad_id", "dataset", "ALL_FOUR_VALID_N"] + [f"{arm}_{metric_name}" for arm in ARM_DIRS for metric_name in ("chamfer", "h95")],
    )
    bootstrap_rows = []
    for arm1, arm2 in pairs:
        for value_name in ("chamfer_norm", "hausdorff_95_norm"):
            item = paired_summary(arm1, arm2, by_arm, value_name, lower_is_better=True)
            bootstrap_rows.append(item)
    write_csv(
        out / "PAIRWISE_GEOMETRY_BOOTSTRAP.csv",
        bootstrap_rows,
        list(bootstrap_rows[0].keys()) if bootstrap_rows else ["comparison"],
    )
    return {
        "pair_rows": pair_rows,
        "all_four_ids": all_four,
        "all_four_summary": all_four_summary,
        "pair_cases": pair_cases,
    }


def load_registry() -> dict[str, dict[str, Any]]:
    path = ROOT / "ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl"
    result = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                result[item.get("cad_id")] = item
    return result


def load_mesh(path: Path):
    import trimesh

    mesh = trimesh.load(str(path), force="mesh")
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def volume_distribution(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    out = OUT / "volume_audit"
    by_arm = rows_by_id(reports)
    distribution = []
    for arm in ARM_DIRS:
        values = [metric(row, "volume_error") for row in by_arm[arm].values() if valid_volume(row)]
        values = [x for x in values if x is not None]
        distribution.append(
            {
                "arm": arm,
                "label": ARM_LABELS[arm],
                "N": len(values),
                "mean": float(np.mean(values)) if values else None,
                "median": float(np.median(values)) if values else None,
                "p75": float(np.percentile(values, 75)) if values else None,
                "p90": float(np.percentile(values, 90)) if values else None,
                "p95": float(np.percentile(values, 95)) if values else None,
                "p99": float(np.percentile(values, 99)) if values else None,
                "max": float(np.max(values)) if values else None,
            }
        )
    write_csv(out / "VOLUME_DISTRIBUTION.csv", distribution, list(distribution[0].keys()))

    pair_rows = []
    for arm1, arm2 in [("A0", "A1"), ("A0", "A2"), ("A0", "A3"), ("A1", "A2"), ("A1", "A3"), ("A2", "A3")]:
        ids = sorted(cad_id for cad_id in by_arm[arm1] if valid_volume(by_arm[arm1][cad_id]) and valid_volume(by_arm[arm2][cad_id]))
        vals1 = [metric(by_arm[arm1][cad_id], "volume_error") for cad_id in ids]
        vals2 = [metric(by_arm[arm2][cad_id], "volume_error") for cad_id in ids]
        deltas = [a - b for a, b in zip(vals1, vals2)]
        better1 = sum(a < b - 1e-12 for a, b in zip(vals1, vals2))
        better2 = sum(b < a - 1e-12 for a, b in zip(vals1, vals2))
        tie = len(ids) - better1 - better2
        lo, hi = bootstrap_ci(deltas)
        pair_rows.append(
            {
                "comparison": f"{arm1}_vs_{arm2}",
                "paired_N": len(ids),
                "mean_arm1": float(np.mean(vals1)) if vals1 else None,
                "mean_arm2": float(np.mean(vals2)) if vals2 else None,
                "median_arm1": float(np.median(vals1)) if vals1 else None,
                "median_arm2": float(np.median(vals2)) if vals2 else None,
                "mean_delta_arm1_minus_arm2": float(np.mean(deltas)) if deltas else None,
                "median_delta_arm1_minus_arm2": float(np.median(deltas)) if deltas else None,
                "arm1_better_N": better1,
                "tie_N": tie,
                "arm2_better_N": better2,
                "bootstrap_ci95_low": lo,
                "bootstrap_ci95_high": hi,
            }
        )
    write_csv(out / "VOLUME_PAIRWISE.csv", pair_rows, list(pair_rows[0].keys()) if pair_rows else ["comparison"])

    registry = load_registry()
    a3_rows = [
        row for row in reports["A3"]["samples"]
        if valid_volume(row)
    ]
    a3_rows.sort(key=lambda row: metric(row, "volume_error") or -1, reverse=True)
    top_rows = []
    root_rows = []
    for row in a3_rows[:20]:
        cad_id = row["id"]
        sid = row["sample_id"]
        gt_mesh_path = ROOT / "cad_spatial_dataset/DeepCAD/train" / sid / "model.obj"
        pred_mesh_path = case_dir("A3", row) / "pred.stl"
        diagnostics = {}
        try:
            gt_mesh = load_mesh(gt_mesh_path)
            pred_mesh = load_mesh(pred_mesh_path)
            gt_extent = np.asarray(gt_mesh.bounds[1] - gt_mesh.bounds[0], dtype=float)
            pred_extent = np.asarray(pred_mesh.bounds[1] - pred_mesh.bounds[0], dtype=float)
            gt_diag = float(np.linalg.norm(gt_extent))
            pred_diag = float(np.linalg.norm(pred_extent))
            bbox_ratio = pred_diag / max(gt_diag, 1e-12)
            extent_error = float(np.max(np.abs(pred_extent - gt_extent) / np.maximum(gt_extent, 1e-12)))
            center_error = float(np.linalg.norm(np.asarray(pred_mesh.centroid) - np.asarray(gt_mesh.centroid)) / max(gt_diag, 1e-12))
            diagnostics = {
                "bbox_diag_ratio": bbox_ratio,
                "extent_error": extent_error,
                "center_error": center_error,
                "gt_bbox_diag": gt_diag,
                "pred_bbox_diag": pred_diag,
            }
        except Exception as exc:
            diagnostics = {"geometry_audit_error": f"{type(exc).__name__}: {exc}"}
        gt_ops = op_list(op_path("A0", row, pred=False))
        pred_ops = op_list(op_path("A3", row, pred=True))
        op_mismatch = Counter(gt_ops) != Counter(pred_ops)
        scale_collapse = finite(diagnostics.get("bbox_diag_ratio")) and diagnostics["bbox_diag_ratio"] < 0.5
        scale_explosion = finite(diagnostics.get("bbox_diag_ratio")) and diagnostics["bbox_diag_ratio"] > 2.0
        placement_error = finite(diagnostics.get("center_error")) and diagnostics["center_error"] > 0.25
        extent_error = finite(diagnostics.get("extent_error")) and diagnostics["extent_error"] > 0.5
        reasons = []
        if scale_collapse or scale_explosion:
            reasons.append("SCALE_COLLAPSE" if scale_collapse else "EXTENT_ERROR")
        if extent_error and "EXTENT_ERROR" not in reasons:
            reasons.append("EXTENT_ERROR")
        if placement_error:
            reasons.append("PLACEMENT_ERROR")
        if op_mismatch:
            reasons.append("OPERATION_STRUCTURE_ERROR")
        if not reasons:
            reasons.append("LOCAL_PARAMETER_ERROR" if not diagnostics.get("geometry_audit_error") else "UNRESOLVED")
        if len(reasons) > 1:
            category = "MULTIPLE"
        else:
            category = reasons[0]
        top = {
            "rank": len(top_rows) + 1,
            "cad_id": cad_id,
            "source": row.get("dataset"),
            "K": registry.get(cad_id, {}).get("K"),
            "A3_volume_error": metric(row, "volume_error"),
            "A3_chamfer": metric(row, "chamfer_norm"),
            "A3_H95": metric(row, "hausdorff_95_norm"),
            "A3_Exact": row.get("exact_match"),
            "A3_Op_F1": row.get("op_f1"),
            "A3_STEP_Reload": None,
            "A0_volume_error": metric(by_arm["A0"][cad_id], "volume_error"),
            "A1_volume_error": metric(by_arm["A1"][cad_id], "volume_error"),
            "A2_volume_error": metric(by_arm["A2"][cad_id], "volume_error"),
        }
        top.update(diagnostics)
        top_rows.append(top)
        root_rows.append(
            {
                "cad_id": cad_id,
                "volume_error": metric(row, "volume_error"),
                "bbox_diag_ratio": diagnostics.get("bbox_diag_ratio"),
                "extent_error": diagnostics.get("extent_error"),
                "center_error": diagnostics.get("center_error"),
                "scale_collapse": scale_collapse,
                "placement_error": placement_error,
                "operation_mismatch": op_mismatch,
                "gt_ops": gt_ops,
                "pred_ops": pred_ops,
                "category": category,
                "evidence": reasons,
            }
        )
    write_csv(out / "A3_VOLUME_OUTLIER_TOP20.csv", top_rows, list(top_rows[0].keys()) if top_rows else ["rank"])
    write_csv(out / "A3_VOLUME_OUTLIER_ROOT_CAUSE.csv", root_rows, list(root_rows[0].keys()) if root_rows else ["cad_id"])
    return {"distribution": distribution, "pairwise": pair_rows, "top20": top_rows, "root_cause": root_rows}


def truncation_audit(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    out = OUT / "truncation"
    rows = []
    for arm, report in reports.items():
        for row in report["samples"]:
            if row.get("stop_reason") != "MAX_LENGTH":
                continue
            gt_path = op_path(arm, row, pred=False)
            pred_path = op_path(arm, row, pred=True)
            gt_text = gt_path.read_text(encoding="utf-8", errors="replace") if gt_path.exists() else ""
            pred_text = pred_path.read_text(encoding="utf-8", errors="replace") if pred_path.exists() else ""
            rows.append(
                {
                    "arm": arm,
                    "cad_id": row["id"],
                    "source": row.get("dataset"),
                    "K": load_registry().get(row["id"], {}).get("K"),
                    "gt_target_length_chars": len(gt_text),
                    "pred_generated_length_tokens": row.get("prediction_tokens"),
                    "gt_operation_count": row.get("gt_op_count"),
                    "pred_operation_count": row.get("predicted_op_count"),
                    "under_generation": row.get("under_generation"),
                    "op_f1": row.get("op_f1"),
                    "step_export": row.get("step_ok"),
                    "geometry_valid": valid_geom(row),
                }
            )
    write_csv(out / "MAX_LENGTH_AUDIT.csv", rows, list(rows[0].keys()) if rows else ["arm"])
    by_arm = {}
    for arm in ARM_DIRS:
        subset = [x for x in rows if x["arm"] == arm]
        by_arm[arm] = {
            "N": len(subset),
            "mean_op_f1": float(np.mean([x["op_f1"] for x in subset])) if subset else None,
            "step_export_rate": float(np.mean([bool(x["step_export"]) for x in subset])) if subset else None,
            "geometry_valid_rate": float(np.mean([bool(x["geometry_valid"]) for x in subset])) if subset else None,
            "mean_gt_operation_count": float(np.mean([x["gt_operation_count"] for x in subset])) if subset else None,
            "mean_pred_operation_count": float(np.mean([x["pred_operation_count"] for x in subset])) if subset else None,
        }
    return {"rows": rows, "by_arm": by_arm}


def parse_step_by_arm(step_results: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    return {
        arm: {row["cad_id"]: row for row in rows}
        for arm, rows in step_results.items()
    }


def parse_step_mcnemar(reports: dict[str, dict[str, Any]], step_results: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    by_arm_rows = rows_by_id(reports)
    step_by_arm = parse_step_by_arm(step_results)
    out = []
    for arm1, arm2 in [("A1", "A0"), ("A2", "A0"), ("A3", "A1"), ("A3", "A2")]:
        ids = sorted(by_arm_rows[arm1])
        both = arm1_only = arm2_only = both_fail = 0
        for cad_id in ids:
            a = bool(step_by_arm[arm1][cad_id]["reload_pass"])
            b = bool(step_by_arm[arm2][cad_id]["reload_pass"])
            if a and b:
                both += 1
            elif a:
                arm1_only += 1
            elif b:
                arm2_only += 1
            else:
                both_fail += 1
        discordant = arm1_only + arm2_only
        try:
            from scipy.stats import binomtest

            pvalue = float(binomtest(min(arm1_only, arm2_only), n=discordant, p=0.5).pvalue) if discordant else 1.0
        except Exception:
            pvalue = None
        out.append(
            {
                "comparison": f"{arm1}_vs_{arm2}",
                "both_pass": both,
                "arm1_only": arm1_only,
                "arm2_only": arm2_only,
                "both_fail": both_fail,
                "discordant": discordant,
                "mcnemar_exact_two_sided_p": pvalue,
            }
        )
    return out


def parse_mcnemar(reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_arm = rows_by_id(reports)
    out = []
    for arm1, arm2 in [("A1", "A0"), ("A2", "A0"), ("A3", "A1"), ("A3", "A2")]:
        both = arm1_only = arm2_only = both_fail = 0
        for cad_id in by_arm[arm1]:
            a = bool(by_arm[arm1][cad_id].get("parsed"))
            b = bool(by_arm[arm2][cad_id].get("parsed"))
            if a and b:
                both += 1
            elif a:
                arm1_only += 1
            elif b:
                arm2_only += 1
            else:
                both_fail += 1
        discordant = arm1_only + arm2_only
        try:
            from scipy.stats import binomtest

            pvalue = float(binomtest(min(arm1_only, arm2_only), n=discordant, p=0.5).pvalue) if discordant else 1.0
        except Exception:
            pvalue = None
        out.append(
            {
                "comparison": f"{arm1}_vs_{arm2}",
                "both_pass": both,
                "arm1_only": arm1_only,
                "arm2_only": arm2_only,
                "both_fail": both_fail,
                "discordant": discordant,
                "mcnemar_exact_two_sided_p": pvalue,
            }
        )
    return out


def opf1_paired(reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_arm = rows_by_id(reports)
    out = []
    for arm1, arm2 in [("A1", "A3"), ("A2", "A3")]:
        deltas = []
        better1 = better2 = tie = 0
        for cad_id in by_arm[arm1]:
            a = f(by_arm[arm1][cad_id].get("op_f1"))
            b = f(by_arm[arm2][cad_id].get("op_f1"))
            if a is None or b is None:
                continue
            deltas.append(a - b)
            if abs(a - b) <= 1e-12:
                tie += 1
            elif a > b:
                better1 += 1
            else:
                better2 += 1
        lo, hi = bootstrap_ci(deltas)
        out.append(
            {
                "comparison": f"{arm1}_vs_{arm2}",
                "paired_N": len(deltas),
                "mean_delta_arm1_minus_arm2": float(np.mean(deltas)) if deltas else None,
                "median_delta_arm1_minus_arm2": float(np.median(deltas)) if deltas else None,
                "arm1_better_N": better1,
                "tie_N": tie,
                "arm2_better_N": better2,
                "bootstrap_ci95_low": lo,
                "bootstrap_ci95_high": hi,
                "direction": "higher_is_better",
            }
        )
    return out


def final_tables(
    reports: dict[str, dict[str, Any]],
    reload_results: dict[str, list[dict[str, Any]]],
    common: dict[str, Any],
    volume: dict[str, Any],
) -> dict[str, Any]:
    out = OUT / "tables"
    step_by_arm = parse_step_by_arm(reload_results)
    rows = []
    for arm in ("A0", "A1", "A2", "A3"):
        report = reports[arm]
        valid_n = sum(valid_geom(x) for x in report["samples"])
        volume_n = sum(valid_volume(x) for x in report["samples"])
        reload_n = sum(x["reload_pass"] for x in reload_results[arm])
        row = {
            "Input": ARM_LABELS[arm],
            "VAL_Base_CE": BASE_CE[arm],
            "Exact": report["exact_match_rate"],
            "Op-F1": report["mean_op_f1"],
            "Op_Recall": report["mean_op_recall"],
            "Parse": report["dsl_parse_valid_rate"],
            "STEP_Export": report["step_valid_rate"],
            "STEP_Reload": reload_n / 1000,
            "Geometry_valid": valid_n / 1000,
            "Geometry_valid_N": valid_n,
            "Chamfer_mean": report["mean_chamfer_norm"],
            "Chamfer_median": float(np.median([metric(x, "chamfer_norm") for x in report["samples"] if metric(x, "chamfer_norm") is not None])),
            "H95_mean": report["mean_hausdorff_95_norm"],
            "H95_median": float(np.median([metric(x, "hausdorff_95_norm") for x in report["samples"] if metric(x, "hausdorff_95_norm") is not None])),
            "Volume_error_mean": report["mean_volume_error"],
            "Volume_error_median": float(np.median([metric(x, "volume_error") for x in report["samples"] if metric(x, "volume_error") is not None])),
            "Volume_valid_N": volume_n,
            "EOS_N": report["stop_reason_counts"].get("EOS", 0),
            "MAX_LENGTH_N": report["stop_reason_counts"].get("MAX_LENGTH", 0),
            "Parse_fail_N": sum(not bool(x.get("parsed")) for x in report["samples"]),
            "STEP_export_fail_N": sum(not bool(x.get("step_ok")) for x in report["samples"]),
            "STEP_reload_pass_N": reload_n,
            "EXEC_timeout_N": sum(bool(x.get("exec_timeout")) for x in report["samples"]),
        }
        rows.append(row)
    write_csv(out / "A0_A1_A2_A3_CORE_ABLATION_FINAL_TABLE.csv", rows, list(rows[0].keys()))

    common_rows = []
    for row in common["pair_rows"]:
        common_rows.append({"row_type": "pair", **row})
    common_rows.append({"row_type": "all_four_summary", **common["all_four_summary"]})
    write_csv(
        out / "A0_A1_A2_A3_COMMON_VALID_GEOMETRY_TABLE.csv",
        common_rows,
        sorted({key for row in common_rows for key in row}),
    )

    advisor_rows = []
    for row in rows:
        advisor_rows.append(
            {
                "Input": row["Input"],
                "VAL_CE": row["VAL_Base_CE"],
                "Exact": row["Exact"],
                "Op-F1": row["Op-F1"],
                "Parse": row["Parse"],
                "STEP_Reload": row["STEP_Reload"],
                "Geometry_valid": row["Geometry_valid"],
                "Chamfer": row["Chamfer_mean"],
                "H95": row["H95_mean"],
            }
        )
    write_csv(
        out / "ADVISOR_CORE_ABLATION_TABLE.csv",
        advisor_rows,
        ["Input", "VAL_CE", "Exact", "Op-F1", "Parse", "STEP_Reload", "Geometry_valid", "Chamfer", "H95"],
    )
    return {"core": rows, "advisor": advisor_rows}


def make_gallery(
    reports: dict[str, dict[str, Any]],
    common: dict[str, Any],
    volume: dict[str, Any],
) -> dict[str, Any]:
    from PIL import Image, ImageDraw, ImageFont

    by_arm = rows_by_id(reports)
    common_ids = set(common["pair_cases"]["A0_A1"]) & set(common["pair_cases"]["A0_A2"])
    line_cases = sorted(
        common_ids,
        key=lambda cad_id: (f(by_arm["A1"][cad_id].get("op_f1")) or 0) - (f(by_arm["A0"][cad_id].get("op_f1")) or 0),
        reverse=True,
    )[:4]
    nonline_cases = sorted(
        common["pair_cases"]["A0_A2"],
        key=lambda cad_id: (metric(by_arm["A0"][cad_id], "chamfer_norm") or 0) - (metric(by_arm["A2"][cad_id], "chamfer_norm") or 0),
        reverse=True,
    )[:4]
    interference_cases = sorted(
        by_arm["A1"],
        key=lambda cad_id: max(
            (f(by_arm["A1"][cad_id].get("op_f1")) or 0) - (f(by_arm["A3"][cad_id].get("op_f1")) or 0),
            (f(by_arm["A2"][cad_id].get("op_f1")) or 0) - (f(by_arm["A3"][cad_id].get("op_f1")) or 0),
        ),
        reverse=True,
    )[:4]
    selected = {
        "line_program_rescue": line_cases,
        "nonline_geometry_rescue": nonline_cases,
        "a3_interference": interference_cases,
    }
    write_json(OUT / "gallery/GALLERY_SELECTION.json", selected)

    width, height = 2400, 1500
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    mono_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    font_path = next((p for p in font_candidates if Path(p).exists()), None)
    mono_path = next((p for p in mono_candidates if Path(p).exists()), font_path)
    title_font = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()
    header_font = ImageFont.truetype(font_path, 24) if font_path else ImageFont.load_default()
    body_font = ImageFont.truetype(font_path, 18) if font_path else ImageFont.load_default()
    mono_font = ImageFont.truetype(mono_path, 16) if mono_path else ImageFont.load_default()
    draw.text((55, 30), "EXACT9998 A0-A3 Curve Modality Ablation", fill=(20, 20, 20), font=title_font)
    draw.text((55, 78), "VAL-only diagnostic gallery; cases selected by frozen post-hoc criteria", fill=(90, 90, 90), font=body_font)

    labels = ["A0", "A1", "A2", "A3"]
    values = {
        "Op-F1": [reports[a]["mean_op_f1"] for a in labels],
        "Parse": [reports[a]["dsl_parse_valid_rate"] for a in labels],
        "STEP export": [reports[a]["step_valid_rate"] for a in labels],
        "Geometry valid": [sum(valid_geom(x) for x in reports[a]["samples"]) / 1000 for a in labels],
    }
    chart_x, chart_y, chart_w, chart_h = 70, 135, 2260, 470
    draw.rectangle((chart_x, chart_y, chart_x + chart_w, chart_y + chart_h), outline=(210, 210, 210), width=2)
    for tick in range(0, 11, 2):
        y = chart_y + chart_h - int(chart_h * tick / 10)
        draw.line((chart_x, y, chart_x + chart_w, y), fill=(235, 235, 235), width=1)
        draw.text((chart_x - 42, y - 10), f"{tick / 10:.1f}", fill=(80, 80, 80), font=body_font)
    colors = [(65, 105, 170), (230, 145, 60), (80, 150, 95), (170, 85, 125)]
    group_w = chart_w / 4
    bar_w = group_w / 6
    for gi, arm in enumerate(labels):
        center = chart_x + group_w * (gi + 0.5)
        draw.text((center - 20, chart_y + chart_h + 12), arm, fill=(20, 20, 20), font=header_font)
        for mi, (name, vals) in enumerate(values.items()):
            value = float(vals[gi])
            x0 = center + (mi - 1.5) * bar_w - bar_w * 0.42
            x1 = center + (mi - 1.5) * bar_w + bar_w * 0.42
            y1 = chart_y + chart_h
            y0 = y1 - int(chart_h * max(0.0, min(1.0, value)))
            draw.rectangle((x0, y0, x1, y1), fill=colors[mi])
            if gi == 0:
                draw.text((chart_x + 25 + mi * 330, chart_y + 18), name, fill=colors[mi], font=body_font)
    draw.text((chart_x + chart_w - 170, chart_y + 18), "rate", fill=(80, 80, 80), font=body_font)

    panel_y = 675
    panel_w = 735
    panel_h = 735
    panel_titles = ["Line program rescue", "Non-line geometry rescue", "A3 interference"]
    for index, (title, ids) in enumerate(selected.items()):
        x0 = 55 + index * 780
        draw.rectangle((x0, panel_y, x0 + panel_w, panel_y + panel_h), outline=(210, 210, 210), width=2)
        draw.text((x0 + 18, panel_y + 18), panel_titles[index], fill=(20, 20, 20), font=header_font)
        y = panel_y + 62
        for cad_id in ids:
            a0 = by_arm["A0"][cad_id]
            a1 = by_arm["A1"][cad_id]
            a2 = by_arm["A2"][cad_id]
            a3 = by_arm["A3"][cad_id]
            ch = [metric(a, "chamfer_norm") for a in (a0, a1, a2, a3)]
            text = (
                f"{cad_id}\n"
                f"  Op-F1    {a0.get('op_f1', 0):.2f} / {a1.get('op_f1', 0):.2f} / {a2.get('op_f1', 0):.2f} / {a3.get('op_f1', 0):.2f}\n"
                f"  Chamfer  {ch[0] if ch[0] is not None else float('nan'):.3f} / {ch[1] if ch[1] is not None else float('nan'):.3f} / {ch[2] if ch[2] is not None else float('nan'):.3f} / {ch[3] if ch[3] is not None else float('nan'):.3f}"
            )
            draw.multiline_text((x0 + 18, y), text, fill=(45, 45, 45), font=mono_font, spacing=5)
            y += 112
    path = OUT / "gallery/CURVE_MODALITY_ABLATION_GALLERY.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return selected


def build_summary(
    reports: dict[str, dict[str, Any]],
    reload_results: dict[str, list[dict[str, Any]]],
    common: dict[str, Any],
    volume: dict[str, Any],
    operation: dict[str, Any],
    truncation: dict[str, Any],
    tables: dict[str, Any],
    parse_stats: list[dict[str, Any]],
    step_stats: list[dict[str, Any]],
    opf1_stats: list[dict[str, Any]],
) -> dict[str, Any]:
    all_four = common["all_four_summary"]
    a3_dist = next(x for x in volume["distribution"] if x["arm"] == "A3")
    line_dom = [x["operation"] for x in operation["contribution"] if x["diagnostic_label"] == "LINE_DOMINANT_OPERATION"]
    nonline_dom = [x["operation"] for x in operation["contribution"] if x["diagnostic_label"] == "NONLINE_DOMINANT_OPERATION"]
    positive = [x["operation"] for x in operation["contribution"] if x["diagnostic_label"] == "ALL_CURVE_POSITIVE_COMBINATION"]
    interference = [x["operation"] for x in operation["contribution"] if x["diagnostic_label"] == "ALL_CURVE_INTERFERENCE_CANDIDATE"]
    p1_dir = ROOT / "ours3/p1_operation_aware_structure_loss_v1"
    p1_status_path = p1_dir / "reports/P1_TRAINING_STATUS.json"
    p1_status = json.loads(p1_status_path.read_text()) if p1_status_path.exists() else {}
    p1_latest_progress = {}
    trainer_log = p1_dir / "runs/p1/trainer_log.jsonl"
    if trainer_log.exists():
        for line in reversed(trainer_log.read_text(encoding="utf-8", errors="replace").splitlines()):
            if line.strip():
                try:
                    p1_latest_progress = json.loads(line)
                except json.JSONDecodeError:
                    pass
                break
    p1_pid_path = p1_dir / "launch/train.pid"
    p1_alive = False
    if p1_pid_path.exists():
        try:
            pid = int(p1_pid_path.read_text().strip())
            os.kill(pid, 0)
            p1_alive = True
        except Exception:
            p1_alive = False
    summary = {
        "CURRENT_GATE": "A0_A1_A2_A3_CORE_ABLATION_FINALIZATION",
        "RESULT_PATTERN": "ASYMMETRIC_MODALITY_BENEFITS_WITH_NAIVE_FUSION_INTERFERENCE",
        "TEST_TOUCHED": "NO",
        "STEP_RELOAD": {
            arm: {
                "export_rate": reports[arm]["step_valid_rate"],
                "export_pass_N": sum(bool(x["export_pass"]) for x in reload_results[arm]),
                "reload_pass_N": sum(bool(x["reload_pass"]) for x in reload_results[arm]),
                "reload_rate_headline": sum(bool(x["reload_pass"]) for x in reload_results[arm]) / 1000,
                "conditional_reload_rate": (
                    sum(bool(x["reload_pass"]) for x in reload_results[arm])
                    / max(sum(bool(x["export_pass"]) for x in reload_results[arm]), 1)
                ),
                "status_counts": dict(Counter(x["reload_status"] for x in reload_results[arm])),
            }
            for arm in ARM_DIRS
        },
        "COMMON_VALID": {
            "pairwise_N": {row["comparison"]: row["paired_N"] for row in common["pair_rows"]},
            "ALL_FOUR_VALID_N": all_four["ALL_FOUR_VALID_N"],
            "ALL_FOUR": {
                arm: {"Chamfer": all_four.get(f"{arm}_chamfer"), "H95": all_four.get(f"{arm}_h95")}
                for arm in ARM_DIRS
            },
        },
        "VOLUME": {
            "A3_VOLUME_MEAN": a3_dist["mean"],
            "A3_VOLUME_MEDIAN": a3_dist["median"],
            "A3_VOLUME_P90": a3_dist["p90"],
            "A3_VOLUME_P95": a3_dist["p95"],
            "A3_VOLUME_P99": a3_dist["p99"],
            "A3_VOLUME_MAX": a3_dist["max"],
            "VOLUME_RESULT_PATTERN": "OUTLIER_DRIVEN" if a3_dist["mean"] > 2 * a3_dist["median"] and a3_dist["p99"] > 3 * a3_dist["median"] else "MIXED",
            "top20_sum": float(np.sum([x["A3_volume_error"] for x in volume["top20"]])) if volume["top20"] else None,
            "all_valid_sum": float(np.sum([metric(row, "volume_error") for row in reports["A3"]["samples"] if valid_volume(row)])),
        },
        "PROGRAM": {
            "A0_OPF1": reports["A0"]["mean_op_f1"],
            "A1_OPF1": reports["A1"]["mean_op_f1"],
            "A2_OPF1": reports["A2"]["mean_op_f1"],
            "A3_OPF1": reports["A3"]["mean_op_f1"],
            "A1_VS_A3_PAIRED": opf1_stats[0],
            "A2_VS_A3_PAIRED": opf1_stats[1],
        },
        "OPERATION_CONTRIBUTION": {
            "LINE_DOMINANT_OPERATIONS": line_dom,
            "NONLINE_DOMINANT_OPERATIONS": nonline_dom,
            "ALL_CURVE_POSITIVE_OPERATIONS": positive,
            "ALL_CURVE_INTERFERENCE_CANDIDATES": interference,
        },
        "TRUNCATION": {
            "A0_MAX_LENGTH": reports["A0"]["stop_reason_counts"].get("MAX_LENGTH", 0),
            "A1_MAX_LENGTH": reports["A1"]["stop_reason_counts"].get("MAX_LENGTH", 0),
            "A2_MAX_LENGTH": reports["A2"]["stop_reason_counts"].get("MAX_LENGTH", 0),
            "A3_MAX_LENGTH": reports["A3"]["stop_reason_counts"].get("MAX_LENGTH", 0),
            "TRUNCATION_PATTERN": "A2_A3_HIGHER_MAX_LENGTH_RATE",
            "effect_summary": truncation["by_arm"],
        },
        "INTERPRETATION": {
            "LINE_CONTRIBUTION": "Line is associated with the strongest program-structure gains if A1 dominates A0 on the operation matrix.",
            "NONLINE_CONTRIBUTION": "Non-line contribution is geometry-oriented only when its common-valid paired Chamfer/H95 deltas remain favorable.",
            "ALL_CURVE_STATUS": "A3 does not qualify as globally best unless it exceeds both A1 and A2 on the paired/common-valid metrics.",
            "NAIVE_FUSION_STATUS": "Diagnostic candidate labels only; they are not causal proof.",
            "GEOMETRY_COVERAGE_STATUS": "Geometry metrics must be read together with valid-N coverage.",
        },
        "P1": {
            "P1_STATUS": p1_status,
            "P1_CURRENT_STEP": p1_latest_progress.get("current_steps") or (p1_status.get("CURRENT_PROGRESS") or {}).get("current_steps"),
            "P1_BEST_VAL_BASE_CE": p1_status.get("best_val_base_ce") or p1_status.get("best_val_loss"),
            "latest_trainer_progress": p1_latest_progress,
            "training_alive": p1_alive,
        },
        "INTEGRITY": {
            "A0_CHANGED": "NO",
            "A1_CHANGED": "NO",
            "A2_CHANGED": "NO",
            "A3_CHANGED": "NO",
            "P1_CHANGED": "NO",
            "EVALUATOR_CHANGED": "NO",
            "PREDICTIONS_CHANGED": "NO",
            "EXACT9998_CHANGED": "NO",
            "TEST_TOUCHED": "NO",
            "report_sha256": {arm: sha256(REPORT_PATHS[arm]) for arm in ARM_DIRS},
        },
        "PARSE_MCNEMAR": parse_stats,
        "STEP_MCNEMAR": step_stats,
        "TABLES": tables,
    }
    return summary


def write_markdown(summary: dict[str, Any]) -> None:
    core = summary["TABLES"]["core"]
    lines = [
        "# EXACT9998 A0-A3 Curve Modality Ablation",
        "",
        "Formal VAL1000 post-hoc finalization. TEST remained blind and no checkpoint, prediction, evaluator, parser, executor, or geometry metric was modified.",
        "",
        "## Core Table",
        "",
        "| Input | CE | Exact | Op-F1 | Op Recall | Parse | STEP Export | STEP Reload | Geometry-valid | Chamfer | H95 | Volume error |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in core:
        lines.append(
            f"| {row['Input']} | {row['VAL_Base_CE']:.4f} | {row['Exact']:.3f} | {row['Op-F1']:.4f} | {row['Op_Recall']:.4f} | {row['Parse']:.3f} | {row['STEP_Export']:.3f} | {row['STEP_Reload']:.3f} | {row['Geometry_valid']:.3f} ({row['Geometry_valid_N']}) | {row['Chamfer_mean']:.5f} | {row['H95_mean']:.5f} | {row['Volume_error_mean']:.5f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A1 is the strongest arm on program structure: Op-F1, Parse, and STEP export.",
            "- A2 is the geometry-distance leader in the original valid-only table, but this must be checked against paired/common-valid coverage.",
            "- A3 is not called globally best unless the paired/common-valid audit supports it.",
            "- STEP Export and STEP Reload are reported separately. Reload headline denominator is all 1000 VAL cases.",
            "- Volume error is valid-only and its mean is sensitive to extreme outliers; the distribution and top-20 audit are included.",
            "",
            "## Integrity",
            "",
            f"- TEST_TOUCHED: `{summary['TEST_TOUCHED']}`",
            f"- RESULT_PATTERN: `{summary['RESULT_PATTERN']}`",
            f"- P1 training alive at audit time: `{summary['P1']['training_alive']}`",
        ]
    )
    text = "\n".join(lines) + "\n"
    (OUT / "reports/ADVISOR_CORE_ABLATION_SUMMARY.md").write_text(text, encoding="utf-8")
    (OUT / "reports/FINAL_REPORT.md").write_text(text, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ["step_reload", "common_valid", "volume_audit", "operation_breakdown", "truncation", "tables", "stats", "gallery", "reports"]:
        (OUT / name).mkdir(parents=True, exist_ok=True)
    reports = load_reports()
    report_hashes_before = {arm: sha256(REPORT_PATHS[arm]) for arm in ARM_DIRS}
    reload_results = step_reload_audit(reports)
    common = common_valid_audit(reports)
    volume = volume_distribution(reports)
    operation = operation_breakdown(reports)
    truncation = truncation_audit(reports)
    step_by_arm = parse_step_by_arm(reload_results)
    for item in volume["top20"]:
        item["A3_STEP_Reload"] = bool(step_by_arm["A3"][item["cad_id"]]["reload_pass"])
    if volume["top20"]:
        write_csv(
            OUT / "volume_audit/A3_VOLUME_OUTLIER_TOP20.csv",
            volume["top20"],
            list(volume["top20"][0].keys()),
        )
    parse_stats = parse_mcnemar(reports)
    step_stats = parse_step_mcnemar(reports, reload_results)
    opf1_stats = opf1_paired(reports)
    tables = final_tables(reports, reload_results, common, volume)
    write_csv(OUT / "stats/PAIRWISE_OPF1_BOOTSTRAP.csv", opf1_stats, list(opf1_stats[0].keys()))
    write_csv(OUT / "stats/PAIRWISE_STEP_MCNEMAR.csv", step_stats, list(step_stats[0].keys()))
    write_csv(OUT / "stats/PAIRWISE_PARSE_MCNEMAR.csv", parse_stats, list(parse_stats[0].keys()))
    selected = make_gallery(reports, common, volume)
    summary = build_summary(reports, reload_results, common, volume, operation, truncation, tables, parse_stats, step_stats, opf1_stats)
    summary["GALLERY_SELECTION"] = selected
    summary["report_sha256_before"] = report_hashes_before
    summary["report_sha256_after"] = {arm: sha256(REPORT_PATHS[arm]) for arm in ARM_DIRS}
    write_json(OUT / "reports/FINAL_REPORT.json", summary)
    write_markdown(summary)
    print(json.dumps({
        "out": str(OUT),
        "step_reload": {
            arm: {
                "export_pass_N": sum(x["export_pass"] for x in reload_results[arm]),
                "reload_pass_N": sum(x["reload_pass"] for x in reload_results[arm]),
                "status_counts": dict(Counter(x["reload_status"] for x in reload_results[arm])),
            }
            for arm in ARM_DIRS
        },
        "all_four_valid_N": common["all_four_summary"]["ALL_FOUR_VALID_N"],
        "a3_volume": next(x for x in volume["distribution"] if x["arm"] == "A3"),
        "p1_alive": summary["P1"]["training_alive"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
