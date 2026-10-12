#!/usr/bin/env python3
"""DeepCAD program complexity audit (GT + optional pred under-generation check).

Reports per-sample and aggregate:
  - GT operation count (Extrude + ExtrudePolygon + Box [+ Cylinder/Revolve])
  - Cut / Union / ExtrudePolygon counts
  - profile vertex count (ExtrudePolygon points; Rectangle=4)
  - DSL token length (SpatialLM tokenizer)
  - 1-op / 2-op / 3-op / 4+-op proportions

Always-on under-generation metric when predictions are available:
  predicted_op_count / gt_op_count
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

SOLID_OPS = frozenset({"Extrude", "ExtrudePolygon", "Box", "Cylinder", "Revolve"})
BOOL_OPS = frozenset({"Cut", "Union"})
PROFILE_OPS = frozenset({"Circle", "Rectangle", "Sketch"})
V1_OPS = SOLID_OPS | BOOL_OPS | PROFILE_OPS

DEFAULT_TOKENIZER = ROOT / "SpatialLM/models/SpatialLM1.1-Llama-1B"


def _pct(n: int, total: int) -> float:
    return 100.0 * n / total if total else 0.0


def _mean(xs: list[float]) -> float | None:
    return float(np.mean(xs)) if xs else None


def _median(xs: list[float]) -> float | None:
    return float(np.median(xs)) if xs else None


def _percentile(xs: list[float], q: float) -> float | None:
    return float(np.percentile(xs, q)) if xs else None


def _literal_list_len(node: ast.AST) -> int:
    if isinstance(node, ast.List):
        return len(node.elts)
    if isinstance(node, (ast.Tuple,)):
        return len(node.elts)
    return 0


def analyze_dsl(dsl_text: str) -> dict[str, Any]:
    """Parse DSL and extract complexity features."""
    try:
        from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code

        code = extract_dsl_code(dsl_text)
    except Exception:
        code = dsl_text

    # Drop comment-only lines for char/line stats; keep full code for tokens.
    body_lines = [
        ln for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#")
    ]
    body = "\n".join(body_lines).strip()

    ops: Counter = Counter()
    profile_vertex_count = 0
    parse_ok = True
    try:
        tree = ast.parse(body if body else code, mode="exec")
    except SyntaxError as exc:
        return {
            "parse_ok": False,
            "parse_error": str(exc),
            "ops": {},
            "op_count": 0,
            "cut_count": 0,
            "union_count": 0,
            "extrude_polygon_count": 0,
            "profile_vertex_count": 0,
            "n_lines": len(body_lines),
            "n_chars": len(body),
            "dsl": body,
        }

    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        name = node.func.id
        if name in V1_OPS:
            ops[name] += 1

        if name == "ExtrudePolygon":
            pts = None
            for kw in node.keywords:
                if kw.arg == "points":
                    pts = kw.value
                    break
            if pts is None and node.args:
                pts = node.args[0]
            if pts is not None:
                profile_vertex_count += _literal_list_len(pts)
        elif name == "Box":
            profile_vertex_count += 4
        elif name == "Rectangle":
            profile_vertex_count += 4
        elif name == "Extrude" and node.args:
            arg0 = node.args[0]
            if isinstance(arg0, ast.Call) and isinstance(arg0.func, ast.Name):
                inner = arg0.func.id
                if inner == "Rectangle":
                    profile_vertex_count += 4
                elif inner == "ExtrudePolygon":
                    # uncommon nesting; still count points if present
                    for kw in arg0.keywords:
                        if kw.arg == "points":
                            profile_vertex_count += _literal_list_len(kw.value)

    op_count = sum(ops[k] for k in SOLID_OPS)
    return {
        "parse_ok": parse_ok,
        "ops": dict(ops),
        "op_count": int(op_count),
        "cut_count": int(ops.get("Cut", 0)),
        "union_count": int(ops.get("Union", 0)),
        "extrude_polygon_count": int(ops.get("ExtrudePolygon", 0)),
        "profile_vertex_count": int(profile_vertex_count),
        "n_lines": len(body_lines),
        "n_chars": len(body),
        "dsl": body,
    }


def _bucket(op_count: int) -> str:
    if op_count <= 0:
        return "0-op"
    if op_count == 1:
        return "1-op"
    if op_count == 2:
        return "2-op"
    if op_count == 3:
        return "3-op"
    return "4+-op"


def _iter_qa_passed(train_dir: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(train_dir.iterdir()):
        if not p.is_dir():
            continue
        qa_path = p / "qa.json"
        if not qa_path.exists():
            continue
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if qa.get("passed"):
            out.append(p)
    return out


def _iter_manifest(train_dir: Path, manifest: Path) -> list[Path]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    ids = data.get("sample_ids") or data.get("passed_ids") or []
    dirs: list[Path] = []
    for sid in ids:
        sid_s = str(sid).replace("/", "_")
        d = train_dir / sid_s
        if d.is_dir():
            dirs.append(d)
    return dirs


def _load_dsl(sample_dir: Path, prefer_canonical: bool) -> tuple[str | None, str | None]:
    candidates = (
        ["program_canonical.dsl", "program.dsl"]
        if prefer_canonical
        else ["program.dsl", "program_canonical.dsl"]
    )
    for name in candidates:
        path = sample_dir / name
        if path.exists():
            return path.read_text(encoding="utf-8"), name
    return None, None


def _load_tokenizer(tokenizer_path: Path | None):
    if tokenizer_path is None:
        return None
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(tokenizer_path), trust_remote_code=True)


def _token_len(tokenizer, text: str) -> int | None:
    if tokenizer is None:
        return None
    return int(len(tokenizer.encode(text, add_special_tokens=False)))


def _summarize_numeric(values: list[float]) -> dict[str, float | None]:
    return {
        "mean": _mean(values),
        "median": _median(values),
        "p25": _percentile(values, 25),
        "p75": _percentile(values, 75),
        "p95": _percentile(values, 95),
        "min": float(min(values)) if values else None,
        "max": float(max(values)) if values else None,
        "sum": float(sum(values)) if values else None,
    }


def audit_gt_samples(
    sample_dirs: list[Path],
    prefer_canonical: bool,
    tokenizer,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    bucket_counts: Counter = Counter()
    missing_dsl = 0

    for sample_dir in sample_dirs:
        dsl_text, dsl_name = _load_dsl(sample_dir, prefer_canonical)
        if dsl_text is None:
            missing_dsl += 1
            records.append({"sample_id": sample_dir.name, "error": "missing_dsl"})
            continue
        feat = analyze_dsl(dsl_text)
        tok_len = _token_len(tokenizer, feat.get("dsl") or "")
        bucket = _bucket(feat["op_count"])
        bucket_counts[bucket] += 1
        rec = {
            "sample_id": sample_dir.name,
            "dsl_file": dsl_name,
            "parse_ok": feat["parse_ok"],
            "op_count": feat["op_count"],
            "cut_count": feat["cut_count"],
            "union_count": feat["union_count"],
            "extrude_polygon_count": feat["extrude_polygon_count"],
            "profile_vertex_count": feat["profile_vertex_count"],
            "dsl_token_length": tok_len,
            "n_lines": feat["n_lines"],
            "n_chars": feat["n_chars"],
            "op_bucket": bucket,
            "ops": feat["ops"],
        }
        if not feat["parse_ok"]:
            rec["parse_error"] = feat.get("parse_error")
        records.append(rec)

    ok = [r for r in records if "op_count" in r and r.get("parse_ok", True)]
    n = len(ok)

    def col(key: str) -> list[float]:
        return [float(r[key]) for r in ok if r.get(key) is not None]

    summary = {
        "n_samples": len(sample_dirs),
        "n_audited": n,
        "missing_dsl": missing_dsl,
        "parse_fail": sum(1 for r in records if r.get("parse_ok") is False),
        "gt_operation_count": _summarize_numeric(col("op_count")),
        "cut_count": _summarize_numeric(col("cut_count")),
        "union_count": _summarize_numeric(col("union_count")),
        "extrude_polygon_count": _summarize_numeric(col("extrude_polygon_count")),
        "profile_vertex_count": _summarize_numeric(col("profile_vertex_count")),
        "dsl_token_length": _summarize_numeric(col("dsl_token_length")),
        "op_bucket_counts": dict(bucket_counts),
        "op_bucket_proportions": {
            k: {"count": bucket_counts[k], "pct": round(_pct(bucket_counts[k], n), 2)}
            for k in ("1-op", "2-op", "3-op", "4+-op", "0-op")
            if bucket_counts[k] or k != "0-op"
        },
        "samples_with_cut": {
            "count": sum(1 for r in ok if r["cut_count"] > 0),
            "pct": round(_pct(sum(1 for r in ok if r["cut_count"] > 0), n), 2),
        },
        "samples_with_union": {
            "count": sum(1 for r in ok if r["union_count"] > 0),
            "pct": round(_pct(sum(1 for r in ok if r["union_count"] > 0), n), 2),
        },
        "samples_with_extrude_polygon": {
            "count": sum(1 for r in ok if r["extrude_polygon_count"] > 0),
            "pct": round(_pct(sum(1 for r in ok if r["extrude_polygon_count"] > 0), n), 2),
        },
    }
    return records, summary


def audit_pred_dirs(
    pred_dirs: list[Path],
    gt_by_id: dict[str, dict[str, Any]] | None = None,
    prefer_gt_from_pred: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compute predicted_op_count / gt_op_count from decode output folders.

    Expects each sample dir to contain gt.dsl (or gt from gt_by_id) and
    pred.txt / pred_canonical.dsl / pred.dsl.
    """
    rows: list[dict[str, Any]] = []
    ratios: list[float] = []
    under_gen = 0
    exact_op = 0
    over_gen = 0

    for pred_root in pred_dirs:
        for sample_dir in sorted(p for p in pred_root.iterdir() if p.is_dir()):
            sid = sample_dir.name
            gt_text = None
            if prefer_gt_from_pred and (sample_dir / "gt.dsl").exists():
                gt_text = (sample_dir / "gt.dsl").read_text(encoding="utf-8")
            elif gt_by_id and sid in gt_by_id:
                gt_text = gt_by_id[sid].get("dsl")

            pred_text = None
            for name in ("pred_canonical.dsl", "pred.dsl", "pred.txt"):
                path = sample_dir / name
                if path.exists():
                    pred_text = path.read_text(encoding="utf-8")
                    break

            if gt_text is None or pred_text is None:
                rows.append(
                    {
                        "sample_id": sid,
                        "pred_root": str(pred_root),
                        "error": "missing_gt_or_pred",
                    }
                )
                continue

            gt = analyze_dsl(gt_text)
            pred = analyze_dsl(pred_text)
            gt_op = int(gt["op_count"])
            pred_op = int(pred["op_count"]) if pred["parse_ok"] else 0
            ratio = pred_op / gt_op if gt_op > 0 else (1.0 if pred_op == 0 else float("inf"))
            if gt_op > 0 and np.isfinite(ratio):
                ratios.append(float(ratio))
            if pred_op < gt_op:
                under_gen += 1
            elif pred_op == gt_op:
                exact_op += 1
            else:
                over_gen += 1

            rows.append(
                {
                    "sample_id": sid,
                    "pred_root": str(pred_root),
                    "gt_op_count": gt_op,
                    "predicted_op_count": pred_op,
                    "predicted_op_count_over_gt_op_count": float(ratio)
                    if np.isfinite(ratio)
                    else None,
                    "gt_cut_count": gt["cut_count"],
                    "pred_cut_count": pred["cut_count"] if pred["parse_ok"] else 0,
                    "gt_union_count": gt["union_count"],
                    "pred_union_count": pred["union_count"] if pred["parse_ok"] else 0,
                    "pred_parse_ok": pred["parse_ok"],
                    "under_generation": pred_op < gt_op,
                }
            )

    n = len([r for r in rows if "gt_op_count" in r])
    summary = {
        "n_paired": n,
        "predicted_op_count_over_gt_op_count": _summarize_numeric(ratios),
        "under_generation_rate": round(_pct(under_gen, n), 2) if n else None,
        "exact_op_count_rate": round(_pct(exact_op, n), 2) if n else None,
        "over_generation_rate": round(_pct(over_gen, n), 2) if n else None,
        "mean_gt_op_count": _mean([float(r["gt_op_count"]) for r in rows if "gt_op_count" in r]),
        "mean_predicted_op_count": _mean(
            [float(r["predicted_op_count"]) for r in rows if "predicted_op_count" in r]
        ),
        "verdict": None,
    }
    mean_ratio = summary["predicted_op_count_over_gt_op_count"]["mean"]
    if mean_ratio is not None:
        if mean_ratio < 0.67:
            summary["verdict"] = (
                f"program under-generation: mean pred/gt op_count={mean_ratio:.3f} "
                f"(gt_mean={summary['mean_gt_op_count']:.2f}, "
                f"pred_mean={summary['mean_predicted_op_count']:.2f})"
            )
        elif mean_ratio > 1.5:
            summary["verdict"] = (
                f"program over-generation: mean pred/gt op_count={mean_ratio:.3f}"
            )
        else:
            summary["verdict"] = (
                f"op-count roughly matched: mean pred/gt op_count={mean_ratio:.3f}"
            )
    return rows, summary


def _print_gt_summary(summary: dict[str, Any]) -> None:
    print("=== DeepCAD Program Complexity Audit (GT) ===")
    print(f"Samples audited: {summary['n_audited']} / {summary['n_samples']}")
    print()
    for title, key in [
        ("GT operation count", "gt_operation_count"),
        ("Cut count", "cut_count"),
        ("Union count", "union_count"),
        ("ExtrudePolygon count", "extrude_polygon_count"),
        ("Profile vertex count", "profile_vertex_count"),
        ("DSL token length", "dsl_token_length"),
    ]:
        s = summary[key]
        print(f"--- {title} ---")
        print(
            f"  mean={s['mean']:.3f}  median={s['median']:.3f}  "
            f"p25={s['p25']:.3f}  p75={s['p75']:.3f}  p95={s['p95']:.3f}  "
            f"min={s['min']:.0f}  max={s['max']:.0f}"
            if s["mean"] is not None
            else "  (empty)"
        )
    print()
    print("--- Op-count buckets ---")
    for k in ("1-op", "2-op", "3-op", "4+-op"):
        info = summary["op_bucket_proportions"].get(k, {"count": 0, "pct": 0.0})
        print(f"  {k:5s}: {info['count']:4d}  ({info['pct']:.1f}%)")
    print()
    print(
        f"Samples with Cut:             {summary['samples_with_cut']['count']} "
        f"({summary['samples_with_cut']['pct']:.1f}%)"
    )
    print(
        f"Samples with Union:           {summary['samples_with_union']['count']} "
        f"({summary['samples_with_union']['pct']:.1f}%)"
    )
    print(
        f"Samples with ExtrudePolygon:  {summary['samples_with_extrude_polygon']['count']} "
        f"({summary['samples_with_extrude_polygon']['pct']:.1f}%)"
    )


def _print_pred_summary(summary: dict[str, Any]) -> None:
    print()
    print("=== predicted_op_count / gt_op_count ===")
    print(f"Paired samples: {summary['n_paired']}")
    s = summary["predicted_op_count_over_gt_op_count"]
    if s["mean"] is None:
        print("  (no ratios)")
        return
    print(
        f"  mean={s['mean']:.3f}  median={s['median']:.3f}  "
        f"p25={s['p25']:.3f}  p75={s['p75']:.3f}  p95={s['p95']:.3f}"
    )
    print(f"  mean GT op_count:   {summary['mean_gt_op_count']:.3f}")
    print(f"  mean pred op_count: {summary['mean_predicted_op_count']:.3f}")
    print(f"  under-generation:   {summary['under_generation_rate']}%")
    print(f"  exact op count:     {summary['exact_op_count_rate']}%")
    print(f"  over-generation:    {summary['over_generation_rate']}%")
    if summary.get("verdict"):
        print(f"  VERDICT: {summary['verdict']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="DeepCAD program complexity audit")
    ap.add_argument(
        "--train-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/train",
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional sample_ids JSON; default = all qa.passed (DeepCAD-1K cohort)",
    )
    ap.add_argument(
        "--qa-passed-only",
        action="store_true",
        default=True,
        help="Use qa.json passed=True samples (default)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap after sorting (e.g. 1000 for exact 1K)",
    )
    ap.add_argument(
        "--prefer-canonical",
        action="store_true",
        default=True,
        help="Prefer program_canonical.dsl (training target)",
    )
    ap.add_argument(
        "--tokenizer",
        type=Path,
        default=DEFAULT_TOKENIZER,
        help="HF tokenizer path for DSL token length (empty to skip)",
    )
    ap.add_argument(
        "--no-tokenizer",
        action="store_true",
        help="Skip DSL token length",
    )
    ap.add_argument(
        "--pred-dir",
        type=Path,
        action="append",
        default=None,
        help="Decode output dir(s) with per-sample gt.dsl + pred*.dsl (repeatable)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/program_complexity_audit_1k.json",
    )
    args = ap.parse_args()

    if args.manifest is not None:
        sample_dirs = _iter_manifest(args.train_dir, args.manifest)
    else:
        sample_dirs = _iter_qa_passed(args.train_dir)

    if args.limit is not None:
        sample_dirs = sample_dirs[: args.limit]

    tokenizer = None
    if not args.no_tokenizer and args.tokenizer is not None and args.tokenizer.exists():
        print(f"Loading tokenizer from {args.tokenizer} ...")
        tokenizer = _load_tokenizer(args.tokenizer)
    elif not args.no_tokenizer:
        print(f"WARNING: tokenizer not found at {args.tokenizer}; skipping token length")

    records, gt_summary = audit_gt_samples(
        sample_dirs, prefer_canonical=args.prefer_canonical, tokenizer=tokenizer
    )
    _print_gt_summary(gt_summary)

    pred_rows: list[dict[str, Any]] = []
    pred_summary: dict[str, Any] | None = None
    if args.pred_dir:
        pred_rows, pred_summary = audit_pred_dirs(args.pred_dir)
        _print_pred_summary(pred_summary)

    report = {
        "cohort": "DeepCAD-1K" if args.manifest is None else str(args.manifest),
        "train_dir": str(args.train_dir),
        "prefer_canonical": args.prefer_canonical,
        "tokenizer": None if tokenizer is None else str(args.tokenizer),
        "gt_summary": gt_summary,
        "pred_summary": pred_summary,
        "samples": records,
        "pred_samples": pred_rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nReport written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
