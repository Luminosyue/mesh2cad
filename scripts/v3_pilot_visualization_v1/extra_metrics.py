#!/usr/bin/env python3
"""Extra quantitative metrics for frozen V3 pilot-eval 150.

Reads frozen per_cad.jsonl + split metadata only. No retrain, no redecode,
no official test, does not modify original result files.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_v3_extra_metrics")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EVAL = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "pilot_eval_150_frozen_v1"
)
SPLIT = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "data/v3_pilot_eval_150.json"
)
OUT = EVAL / "extra_metrics_v1"
ARMS = ("b0", "b1", "m2")
ARM_DIR = {"b0": "b0_epoch09", "b1": "b1_epoch09", "m2": "m2_epoch10"}
ARM_LABEL = {"b0": "B0", "b1": "B1", "m2": "M2"}
COLORS = {"b0": "#3870b2", "b1": "#e68623", "m2": "#38984f"}
OPS = (
    "Box",
    "Cylinder",
    "ExtrudePolygon",
    "Extrude",
    "Revolve",
    "Union",
    "Cut",
    "Intersect",
    "Circle",
    "Rectangle",
    "Polygon",
)
OP_RE = re.compile(r"\b(" + "|".join(OPS) + r")\s*\(")
BODY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", re.M)
FOCUS_OPS = ("Cut", "Union", "Circle", "Extrude", "ExtrudePolygon", "Box")
CH_THRESH = (0.25, 0.5, 1.0, 2.0)


def load_jsonl(path: Path) -> dict[str, dict]:
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["cad_id"]] = rec
    return out


def ops_list(text: str) -> list[str]:
    return OP_RE.findall(text or "")


def prf(gt: list[str], pred: list[str]) -> dict:
    a, b = Counter(gt), Counter(pred)
    tp = sum((a & b).values())
    ng, np_ = sum(a.values()), sum(b.values())
    if ng == 0 and np_ == 0:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "n_gt": 0, "n_pred": 0}
    p = tp / np_ if np_ else 0.0
    r = tp / ng if ng else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return {"precision": p, "recall": r, "f1": f1, "tp": tp, "n_gt": ng, "n_pred": np_}


def presence(ops: list[str], name: str) -> bool:
    return name in ops


def mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and np.isnan(x))]
    return float(np.mean(xs)) if xs else None


def median(xs):
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else None


def pctl(xs, q):
    xs = [x for x in xs if x is not None]
    return float(np.quantile(xs, q)) if xs else None


def rate(xs):
    xs = list(xs)
    return float(np.mean(xs)) if xs else None


def binary_prf(gt_flags, pred_flags):
    gt = np.array(gt_flags, dtype=bool)
    pr = np.array(pred_flags, dtype=bool)
    tp = int(np.sum(gt & pr))
    fp = int(np.sum(~gt & pr))
    fn = int(np.sum(gt & ~pr))
    p = tp / (tp + fp) if (tp + fp) else (1.0 if (tp + fn) == 0 else 0.0)
    r = tp / (tp + fn) if (tp + fn) else (1.0 if (tp + fp) == 0 else 0.0)
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    support = int(np.sum(gt))
    return {"precision": p, "recall": r, "f1": f1, "support_gt": support, "tp": tp, "fp": fp, "fn": fn}


def pairwise(a, b):
    better = tie = worse = 0
    for x, y in zip(a, b):
        if x is None or y is None:
            continue
        if x < y:
            better += 1
        elif x > y:
            worse += 1
        else:
            tie += 1
    return [better, tie, worse]


def pairwise_higher_better(a, b):
    better = tie = worse = 0
    for x, y in zip(a, b):
        if x is None or y is None:
            continue
        if x > y:
            better += 1
        elif x < y:
            worse += 1
        else:
            tie += 1
    return [better, tie, worse]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {r["cad_id"]: r for r in json.loads(SPLIT.read_text())["records"]}
    arms = {k: load_jsonl(EVAL / ARM_DIR[k] / "per_cad.jsonl") for k in ARMS}
    ids = list(arms["b0"])
    if len(ids) != 150:
        raise RuntimeError("expected 150")

    rows = []
    for i in ids:
        m = meta[i]
        gt_text = Path(m["target_dsl"]).read_text()
        gt_ops = ops_list(gt_text)
        rec = {
            "cad_id": i,
            "source_dataset": m.get("source_dataset"),
            "difficulty_bin": m.get("difficulty_bin"),
            "operation_count": int(m.get("operation_count") or len(gt_ops)),
            "has_cut": bool(m.get("has_cut")),
            "has_circle": bool(m.get("has_circle")),
            "has_join": bool(m.get("has_join")),
            "has_hole": bool(m.get("has_hole")),
            "gt_ops": gt_ops,
            "gt_n_ops": len(gt_ops),
            "gt_n_assign": len(BODY_RE.findall(gt_text)),
            "gt_has_cut": presence(gt_ops, "Cut") or bool(m.get("has_cut")),
            "gt_has_union": presence(gt_ops, "Union") or bool(m.get("has_join")),
            "gt_has_circle": presence(gt_ops, "Circle") or bool(m.get("has_circle")),
        }
        for k in ARMS:
            r = arms[k][i]
            pred_ops = ops_list(r.get("generated_dsl") or "")
            scores = prf(gt_ops, pred_ops)
            n_assign = len(BODY_RE.findall(r.get("generated_dsl") or ""))
            rec[k] = {
                **scores,
                "step": bool(r.get("step_reload_success")),
                "parse": bool(r.get("dsl_parse_success")),
                "execute": bool(r.get("dsl_execute_success")),
                "brep": bool(r.get("brep_valid")),
                "runaway": bool(r.get("unexpected_runaway")),
                "eos": bool(r.get("eos_emitted")),
                "failure_reason": r.get("failure_reason"),
                "op_f1_saved": r.get("op_f1"),
                "chamfer": r.get("chamfer_norm"),
                "h95": r.get("hausdorff95_norm"),
                "coverage": r.get("coverage_at_0p01"),
                "bbox_err": r.get("bbox_error_norm"),
                "vol_err": r.get("volume_relative_error"),
                "len_ratio": r.get("generated_target_ratio"),
                "gen_len": r.get("generated_token_length"),
                "tgt_len": r.get("target_token_length"),
                "n_assign": n_assign,
                "has_cut": presence(pred_ops, "Cut"),
                "has_union": presence(pred_ops, "Union"),
                "has_circle": presence(pred_ops, "Circle"),
                "n_pred_ops": len(pred_ops),
                "op_count_abs_err": abs(len(pred_ops) - len(gt_ops)),
                "overgen_ratio": len(pred_ops) / max(len(gt_ops), 1),
            }
            type_prf = {}
            for op in FOCUS_OPS:
                type_prf[op] = prf([x for x in gt_ops if x == op], [x for x in pred_ops if x == op])
            rec[k]["type_prf"] = type_prf
        rows.append(rec)

    common = [r for r in rows if r["b0"]["step"] and r["b1"]["step"] and r["m2"]["step"]]
    subsets = {
        "150_overall": rows,
        "91_common_valid": common,
        "deepcad": [r for r in rows if r["source_dataset"] == "deepcad"],
        "fusion360": [r for r in rows if r["source_dataset"] == "fusion360"],
        "has_cut": [r for r in rows if r["gt_has_cut"]],
        "no_cut": [r for r in rows if not r["gt_has_cut"]],
        "has_circle": [r for r in rows if r["gt_has_circle"]],
        "no_circle": [r for r in rows if not r["gt_has_circle"]],
        "ops_1to3": [r for r in rows if r["gt_n_ops"] <= 3],
        "ops_4to8": [r for r in rows if 4 <= r["gt_n_ops"] <= 8],
        "ops_9plus": [r for r in rows if r["gt_n_ops"] >= 9],
    }
    for bin_name in sorted({r["difficulty_bin"] for r in rows if r["difficulty_bin"]}):
        subsets[f"diff_{bin_name}"] = [r for r in rows if r["difficulty_bin"] == bin_name]

    def arm_block(subset, k):
        recs = [r[k] for r in subset]
        ch = [x["chamfer"] for x in recs if x["chamfer"] is not None]
        h95 = [x["h95"] for x in recs if x["h95"] is not None]
        bbox = [x["bbox_err"] for x in recs if x["bbox_err"] is not None]
        vol = [x["vol_err"] for x in recs if x["vol_err"] is not None]
        block = {
            "n": len(subset),
            "runaway": sum(x["runaway"] for x in recs),
            "parse": sum(x["parse"] for x in recs),
            "execute": sum(x["execute"] for x in recs),
            "brep": sum(x["brep"] for x in recs),
            "step": sum(x["step"] for x in recs),
            "mean_op_f1": mean([x["f1"] for x in recs]),
            "mean_op_precision": mean([x["precision"] for x in recs]),
            "mean_op_recall": mean([x["recall"] for x in recs]),
            "mean_op_f1_step_success": mean([x["f1"] for x in recs if x["step"]]),
            "mean_n_pred_ops": mean([x["n_pred_ops"] for x in recs]),
            "mean_op_count_abs_err": mean([x["op_count_abs_err"] for x in recs]),
            "mean_overgen_ratio": mean([x["overgen_ratio"] for x in recs]),
            "mean_assign_abs_err": mean([abs(x["n_assign"] - r["gt_n_assign"]) for r, x in zip(subset, recs)]),
            "mean_len_ratio": mean([x["len_ratio"] for x in recs]),
            "median_len_ratio": median([x["len_ratio"] for x in recs]),
            "failure_taxonomy": dict(sorted(Counter(x["failure_reason"] for x in recs).items())),
            "chamfer": {
                "n": len(ch),
                "mean": mean(ch),
                "median": median(ch),
                "p25": pctl(ch, 0.25),
                "p75": pctl(ch, 0.75),
                "frac_lt": {str(t): rate(v < t for v in ch) for t in CH_THRESH} if ch else {},
            },
            "hausdorff95": {"n": len(h95), "mean": mean(h95), "median": median(h95)},
            "bbox_err": {"n": len(bbox), "mean": mean(bbox), "median": median(bbox)},
            "volume_rel_err": {"n": len(vol), "mean": mean(vol), "median": median(vol)},
            "feature_recovery": {
                "cut": binary_prf([r["gt_has_cut"] for r in subset], [x["has_cut"] for x in recs]),
                "union": binary_prf([r["gt_has_union"] for r in subset], [x["has_union"] for x in recs]),
                "circle": binary_prf([r["gt_has_circle"] for r in subset], [x["has_circle"] for x in recs]),
            },
            "type_mean_f1": {
                op: mean([x["type_prf"][op]["f1"] for x in recs]) for op in FOCUS_OPS
            },
            "type_mean_recall": {
                op: mean([x["type_prf"][op]["recall"] for x in recs]) for op in FOCUS_OPS
            },
        }
        return block

    summary = {
        "evaluation": "V3 frozen pilot-eval 150 extra metrics v1",
        "official_test_read": False,
        "retrain": False,
        "redecode": False,
        "original_results_modified": False,
        "note": "Op precision/recall/F1 over all samples. Chamfer stats over STEP-success only unless noted.",
        "subsets": {},
    }
    for name, subset in subsets.items():
        if not subset:
            continue
        summary["subsets"][name] = {
            "n": len(subset),
            "arms": {k: arm_block(subset, k) for k in ARMS},
        }

    # pairwise on 91
    cv = common
    summary["pairwise_91"] = {
        "chamfer_m2_vs_b0_better_tie_worse": pairwise(
            [r["m2"]["chamfer"] for r in cv], [r["b0"]["chamfer"] for r in cv]
        ),
        "chamfer_m2_vs_b1_better_tie_worse": pairwise(
            [r["m2"]["chamfer"] for r in cv], [r["b1"]["chamfer"] for r in cv]
        ),
        "opf1_m2_vs_b0_better_tie_worse": pairwise_higher_better(
            [r["m2"]["f1"] for r in cv], [r["b0"]["f1"] for r in cv]
        ),
        "opf1_m2_vs_b1_better_tie_worse": pairwise_higher_better(
            [r["m2"]["f1"] for r in cv], [r["b1"]["f1"] for r in cv]
        ),
        "both_better_than_b0": sum(
            1
            for r in cv
            if r["m2"]["f1"] > r["b0"]["f1"]
            and r["m2"]["chamfer"] is not None
            and r["b0"]["chamfer"] is not None
            and r["m2"]["chamfer"] < r["b0"]["chamfer"]
        ),
    }

    # length bins vs step / f1
    bins = [0, 0.5, 1.0, 1.5, 2.0, 4.0, 99]
    length = {}
    for k in ARMS:
        recs = [r[k] for r in rows]
        length[k] = []
        ratios = np.array([float(x["len_ratio"] or 0) for x in recs])
        for a, b in zip(bins[:-1], bins[1:]):
            msk = (ratios >= a) & (ratios < b)
            sel = [x for x, ok in zip(recs, msk) if ok]
            length[k].append(
                {
                    "bin": f"[{a},{b})",
                    "n": int(msk.sum()),
                    "step_rate": rate(x["step"] for x in sel),
                    "mean_op_f1": mean(x["f1"] for x in sel),
                    "runaway_rate": rate(x["runaway"] for x in sel),
                }
            )
    summary["length_bins"] = length

    (OUT / "EXTRA_METRICS_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "per_cad_extra.jsonl").write_text(
        "".join(
            json.dumps(
                {
                    "cad_id": r["cad_id"],
                    "source_dataset": r["source_dataset"],
                    "difficulty_bin": r["difficulty_bin"],
                    "gt_n_ops": r["gt_n_ops"],
                    "gt_has_cut": r["gt_has_cut"],
                    "gt_has_circle": r["gt_has_circle"],
                    "gt_has_union": r["gt_has_union"],
                    **{
                        k: {
                            "f1": r[k]["f1"],
                            "precision": r[k]["precision"],
                            "recall": r[k]["recall"],
                            "step": r[k]["step"],
                            "chamfer": r[k]["chamfer"],
                            "has_cut": r[k]["has_cut"],
                            "has_circle": r[k]["has_circle"],
                            "n_pred_ops": r[k]["n_pred_ops"],
                            "len_ratio": r[k]["len_ratio"],
                            "failure_reason": r[k]["failure_reason"],
                        }
                        for k in ARMS
                    },
                }
            )
            + "\n"
            for r in rows
        )
    )
    make_figures(summary, subsets)
    write_readme(summary)
    print(f"[done] {OUT}")
    return 0


def bar_group(ax, labels, series, ylabel, title, ylim=None):
    x = np.arange(len(labels))
    w = 0.24
    for i, k in enumerate(ARMS):
        ax.bar(x + (i - 1) * w, series[k], width=w, label=ARM_LABEL[k], color=COLORS[k])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=15)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_facecolor("white")


def make_figures(summary, subsets):
    fig_dir = OUT / "figures"
    fig_dir.mkdir(exist_ok=True)

    def grab(subset_name, field, inner=None):
        out = {}
        for k in ARMS:
            blk = summary["subsets"][subset_name]["arms"][k]
            if inner:
                out[k] = blk[field][inner]
            else:
                out[k] = blk[field]
        return out

    # 1) precision / recall / f1 overall + common
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), dpi=140, facecolor="white")
    for ax, name, title in (
        (axes[0], "150_overall", "150 overall"),
        (axes[1], "91_common_valid", "91 common-valid"),
    ):
        labels = ["Op P", "Op R", "Op F1"]
        series = {k: [] for k in ARMS}
        for k in ARMS:
            blk = summary["subsets"][name]["arms"][k]
            series[k] = [blk["mean_op_precision"], blk["mean_op_recall"], blk["mean_op_f1"]]
        bar_group(ax, labels, series, "score", title, (0, 1.05))
    fig.suptitle("Operation precision / recall / F1", fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "op_precision_recall_f1.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # 2) feature recovery recall
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), dpi=140, facecolor="white")
    for ax, name, title in (
        (axes[0], "150_overall", "150 overall"),
        (axes[1], "91_common_valid", "91 common-valid"),
    ):
        labels = ["Cut R", "Union R", "Circle R", "Cut P", "Union P", "Circle P"]
        series = {k: [] for k in ARMS}
        for k in ARMS:
            fr = summary["subsets"][name]["arms"][k]["feature_recovery"]
            series[k] = [
                fr["cut"]["recall"],
                fr["union"]["recall"],
                fr["circle"]["recall"],
                fr["cut"]["precision"],
                fr["union"]["precision"],
                fr["circle"]["precision"],
            ]
        bar_group(ax, labels, series, "score", title, (0, 1.05))
    fig.suptitle("Feature recovery: Cut / Union / Circle  (R=recall, P=precision)", fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "feature_recovery.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # 3) type F1
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 4.8), dpi=140, facecolor="white")
    labels = list(FOCUS_OPS)
    for ax, name, title in (
        (axes[0], "150_overall", "150 overall type F1"),
        (axes[1], "91_common_valid", "91 common-valid type F1"),
    ):
        series = {k: [summary["subsets"][name]["arms"][k]["type_mean_f1"][op] or 0 for op in labels] for k in ARMS}
        bar_group(ax, labels, series, "mean F1", title, (0, 1.05))
    fig.suptitle("Per-operation-type F1", fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "type_op_f1.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # 4) chamfer distribution stats
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6), dpi=140, facecolor="white")
    for ax, name, title in (
        (axes[0], "150_overall", "150 STEP-success Chamfer"),
        (axes[1], "91_common_valid", "91 common-valid Chamfer"),
    ):
        labels = ["mean", "median", "p25", "p75"]
        series = {k: [] for k in ARMS}
        for k in ARMS:
            ch = summary["subsets"][name]["arms"][k]["chamfer"]
            series[k] = [ch["mean"], ch["median"], ch["p25"], ch["p75"]]
        bar_group(ax, labels, series, "Chamfer (norm)", title)
    fig.suptitle("Chamfer is mean-skewed; median is the fairer number", fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "chamfer_percentiles.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # 5) stratified op f1
    keys = [
        ("deepcad", "DeepCAD"),
        ("fusion360", "Fusion"),
        ("has_cut", "has Cut"),
        ("no_cut", "no Cut"),
        ("has_circle", "has Circle"),
        ("no_circle", "no Circle"),
        ("ops_1to3", "ops 1-3"),
        ("ops_4to8", "ops 4-8"),
        ("ops_9plus", "ops 9+"),
    ]
    keys = [(a, b) for a, b in keys if a in summary["subsets"]]
    fig, ax = plt.subplots(figsize=(12.8, 4.8), dpi=140, facecolor="white")
    labels = [f"{b}\n n={summary['subsets'][a]['n']}" for a, b in keys]
    series = {k: [summary["subsets"][a]["arms"][k]["mean_op_f1"] for a, _ in keys] for k in ARMS}
    bar_group(ax, labels, series, "mean Op F1", "Stratified Op F1 (150)", (0, 1.05))
    fig.tight_layout()
    fig.savefig(fig_dir / "stratified_op_f1.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12.8, 4.8), dpi=140, facecolor="white")
    series = {
        k: [
            (summary["subsets"][a]["arms"][k]["chamfer"]["median"] or np.nan)
            for a, _ in keys
        ]
        for k in ARMS
    }
    bar_group(ax, labels, series, "median Chamfer", "Stratified median Chamfer (STEP-success)")
    fig.tight_layout()
    fig.savefig(fig_dir / "stratified_chamfer_median.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # 6) length bins
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.6), dpi=140, facecolor="white")
    bins = [x["bin"] for x in summary["length_bins"]["m2"]]
    for ax, field, title, ylim in (
        (axes[0], "step_rate", "STEP success vs length ratio", (0, 1.05)),
        (axes[1], "mean_op_f1", "Op F1 vs length ratio", (0, 1.05)),
    ):
        for k in ARMS:
            ys = [x[field] if x[field] is not None else np.nan for x in summary["length_bins"][k]]
            ns = [x["n"] for x in summary["length_bins"][k]]
            ax.plot(range(len(bins)), ys, marker="o", color=COLORS[k], label=ARM_LABEL[k])
        ax.set_xticks(range(len(bins)))
        ax.set_xticklabels(bins, fontsize=8)
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_xlabel("generated / target length")
    fig.suptitle("Length ratio bins (n annotated in JSON)", fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "length_bins.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # 7) compact numeric table image for 150 + 91
    fig, ax = plt.subplots(figsize=(14.2, 5.4), dpi=140, facecolor="white")
    ax.axis("off")
    header = [
        "set/arm",
        "STEP",
        "OpP",
        "OpR",
        "OpF1",
        "CutR",
        "CircR",
        "Ch med",
        "Ch mean",
        "Ch<0.5",
        "|Δops|",
    ]
    cells = []
    for sname, slabel in (("150_overall", "150"), ("91_common_valid", "91")):
        for k in ARMS:
            blk = summary["subsets"][sname]["arms"][k]
            ch = blk["chamfer"]
            cells.append(
                [
                    f"{slabel}/{ARM_LABEL[k]}",
                    f"{blk['step']}/{blk['n']}",
                    f"{blk['mean_op_precision']:.3f}",
                    f"{blk['mean_op_recall']:.3f}",
                    f"{blk['mean_op_f1']:.3f}",
                    f"{blk['feature_recovery']['cut']['recall']:.3f}",
                    f"{blk['feature_recovery']['circle']['recall']:.3f}",
                    f"{ch['median']:.3f}" if ch["median"] is not None else "—",
                    f"{ch['mean']:.3f}" if ch["mean"] is not None else "—",
                    f"{ch['frac_lt'].get('0.5', 0):.3f}" if ch["frac_lt"] else "—",
                    f"{blk['mean_op_count_abs_err']:.2f}",
                ]
            )
    table = ax.table(cellText=cells, colLabels=header, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.45)
    ax.set_title("Extra metrics (frozen 150; no redecode)", fontsize=12)
    fig.tight_layout()
    fig.savefig(fig_dir / "extra_metrics_table.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_readme(summary):
    p91 = summary["pairwise_91"]
    lines = [
        "# Extra metrics v1",
        "",
        "Computed from frozen `per_cad.jsonl` + target DSL. No retrain / redecode / official test.",
        "",
        "## What was added beyond the original summary",
        "- Op precision / recall (not just F1)",
        "- Cut / Union / Circle presence recovery",
        "- Per-type operation F1 (Cut, Union, Circle, Extrude, ExtrudePolygon, Box)",
        "- Chamfer median / p25 / p75 / fraction below thresholds",
        "- Stratify: DeepCAD vs Fusion, has_cut, has_circle, op-count bins",
        "- Length-ratio bins vs STEP and Op F1",
        "- Pairwise Op F1 wins on the 91 common-valid set",
        "",
        "## 91 pairwise",
        f"- Chamfer M2 vs B0 better/tie/worse: {p91['chamfer_m2_vs_b0_better_tie_worse']}",
        f"- Chamfer M2 vs B1: {p91['chamfer_m2_vs_b1_better_tie_worse']}",
        f"- Op F1 M2 vs B0: {p91['opf1_m2_vs_b0_better_tie_worse']}",
        f"- Op F1 M2 vs B1: {p91['opf1_m2_vs_b1_better_tie_worse']}",
        f"- both F1↑ and Chamfer↓ vs B0: {p91['both_better_than_b0']}/91",
        "",
        "Figures in `figures/`.",
    ]
    (OUT / "README.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
