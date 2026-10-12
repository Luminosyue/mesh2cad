#!/usr/bin/env python3
"""LINE→CIRCLE false-positive diagnostics (no training / no P2 changes).

Compares geometric stats across:
  A. LINE → LINE
  B. LINE → CIRCLE
  C. CIRCLE → CIRCLE
plus short CIRCLE → LINE, and counts LINE→CIRCLE across P0–T2.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_encoder_baseline_v1.config import (  # noqa: E402
    EXPERIMENTS,
    ID_TO_TYPE,
    PRIMARY_TYPES,
    RUNS_DIR,
    TYPE_TO_ID,
)
from curve_encoder_baseline_v1.dataset import (  # noqa: E402
    CACHE_DIR,
    CurveEncoderDataset,
    collate_curves,
)
from curve_encoder_baseline_v1.models import build_model  # noqa: E402

EXPS = ["P0", "P1", "P2", "T0", "T1", "T2"]


def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-12)
    b = b / (np.linalg.norm(b) + 1e-12)
    c = float(np.clip(np.dot(a, b), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def geom_features(xyz: np.ndarray, tangent: np.ndarray, length: float) -> dict:
    """Chord height / turn angles / orientation from sampled curve."""
    xyz = np.asarray(xyz, dtype=np.float64)
    tan = np.asarray(tangent, dtype=np.float64)
    n = xyz.shape[0]
    # chord through endpoints
    p0, p1 = xyz[0], xyz[-1]
    chord = p1 - p0
    chord_len = float(np.linalg.norm(chord))
    if chord_len < 1e-12:
        # closed or degenerate: use PCA major axis as reference line through centroid
        c = xyz.mean(0)
        _, _, vt = np.linalg.svd(xyz - c, full_matrices=False)
        direction = vt[0]
        # distance to axis through centroid
        d = xyz - c
        proj = (d @ direction)[:, None] * direction
        perp = d - proj
        max_dev = float(np.linalg.norm(perp, axis=1).max())
        closed_like = True
    else:
        direction = chord / chord_len
        t = ((xyz - p0) @ direction)[:, None] * direction
        perp = xyz - p0 - t
        max_dev = float(np.linalg.norm(perp, axis=1).max())
        closed_like = False

    curve_len = float(length) if length > 1e-12 else float(
        np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()
    )
    if curve_len < 1e-12:
        curve_len = 1e-12
    norm_chord_height = max_dev / curve_len

    # turn angles from consecutive tangents
    turns = []
    for i in range(n - 1):
        turns.append(_angle_deg(tan[i], tan[i + 1]))
    turns = np.asarray(turns, dtype=np.float64)
    mean_turn = float(turns.mean()) if turns.size else 0.0
    max_turn = float(turns.max()) if turns.size else 0.0
    total_turn = float(turns.sum()) if turns.size else 0.0

    # endpoint direction (orientation): unit vector of chord or mean tangent
    if chord_len >= 1e-12:
        orient = direction
    else:
        mt = tan.mean(0)
        nrm = float(np.linalg.norm(mt))
        orient = mt / nrm if nrm > 1e-12 else np.array([1.0, 0.0, 0.0])

    # axis-aligned ratio: |max_abs_component| / ||orient|| (=1 for unit) → how axis-aligned
    abs_o = np.abs(orient)
    axis_aligned_ratio = float(abs_o.max())  # 1 = axis-aligned, ~0.577 = diagonal
    dominant_axis = int(abs_o.argmax())  # 0=x,1=y,2=z

    bbox = xyz.max(0) - xyz.min(0)
    center = xyz.mean(0)

    return {
        "max_chord_deviation": max_dev,
        "normalized_chord_height": norm_chord_height,
        "chord_len": chord_len,
        "curve_length": curve_len,
        "mean_turn_angle": mean_turn,
        "max_turn_angle": max_turn,
        "total_turn_angle": total_turn,
        "closed_like_endpoints": closed_like,
        "orient_x": float(orient[0]),
        "orient_y": float(orient[1]),
        "orient_z": float(orient[2]),
        "axis_aligned_ratio": axis_aligned_ratio,
        "dominant_axis": dominant_axis,
        "center_x": float(center[0]),
        "center_y": float(center[1]),
        "center_z": float(center[2]),
        "bbox_diag": float(np.linalg.norm(bbox)),
    }


def _stat(xs: list[float] | np.ndarray) -> dict:
    if xs is None or len(xs) == 0:
        return {"n": 0, "median": None, "p90": None, "p95": None, "mean": None}
    a = np.asarray(xs, dtype=np.float64)
    return {
        "n": int(a.size),
        "median": float(np.median(a)),
        "p90": float(np.percentile(a, 90)),
        "p95": float(np.percentile(a, 95)),
        "mean": float(a.mean()),
    }


@torch.no_grad()
def predict_exp(exp: str, device: torch.device) -> np.ndarray:
    spec = EXPERIMENTS[exp]
    # feature set differs; always load matching dataset
    ds = CurveEncoderDataset("test", spec["features"], force_rebuild=False)
    model = build_model(spec["encoder"], tuple(spec["features"])).to(device)
    ckpt = torch.load(RUNS_DIR / f"{exp}_frozen_v1" / "best.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model"])
    model.eval()
    loader = DataLoader(
        ds, batch_size=512, shuffle=False, num_workers=4, collate_fn=collate_curves,
        pin_memory=device.type == "cuda",
    )
    preds = []
    for batch in loader:
        logits = model(batch["feats"].to(device))["type_logits"]
        preds.append(logits.argmax(-1).cpu().numpy())
    return np.concatenate(preds)


def length_bucket(length: float, edges: np.ndarray) -> str:
    # edges = [p10,p25,p50,p75,p90] of LINE lengths
    p10, p25, p50, p75, p90 = edges
    if length < p10:
        return "<P10"
    if length < p25:
        return "P10–P25"
    if length < p50:
        return "P25–P50"
    if length < p75:
        return "P50–P75"
    if length < p90:
        return "P75–P90"
    return ">P90"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--exps", nargs="+", default=EXPS)
    args = ap.parse_args()
    device = torch.device(args.device)

    out_dir = RUNS_DIR / "P2_frozen_v1" / "diagnostics" / "line_to_circle"
    out_dir.mkdir(parents=True, exist_ok=True)

    # geometry from P2 feature cache (xyz+tan+s) — geometry independent of exp
    base_ds = CurveEncoderDataset("test", ("xyz", "tangent", "s"), force_rebuild=False)
    meta = json.loads((CACHE_DIR / "frozen_v1_test_meta.json").read_text(encoding="utf-8"))
    refs = meta["refs"]
    y_true = base_ds.type_id.copy()
    n = len(y_true)
    assert len(refs) == n

    print("[geom] computing features for all test curves…")
    feats = []
    for i in range(n):
        poly_len = float(np.linalg.norm(np.diff(base_ds.xyz[i], axis=0), axis=1).sum())
        f = geom_features(base_ds.xyz[i], base_ds.tangent[i], poly_len)
        f["type_id"] = int(y_true[i])
        feats.append(f)

    lengths_line = np.array(
        [feats[i]["curve_length"] for i in range(n) if y_true[i] == TYPE_TO_ID["LINE"]],
        dtype=np.float64,
    )
    len_edges = np.percentile(lengths_line, [10, 25, 50, 75, 90])

    print("[pred] running P0–T2 on test…")
    preds = {}
    for exp in args.exps:
        print(f"  {exp}")
        preds[exp] = predict_exp(exp, device)
        assert preds[exp].shape[0] == n

    # --- cross-exp LINE→CIRCLE counts ---
    line_id = TYPE_TO_ID["LINE"]
    circ_id = TYPE_TO_ID["CIRCLE"]
    cross = {}
    for exp, yp in preds.items():
        mask = (y_true == line_id) & (yp == circ_id)
        cross[exp] = {
            "LINE→CIRCLE": int(mask.sum()),
            "LINE→LINE": int(((y_true == line_id) & (yp == line_id)).sum()),
            "n_LINE": int((y_true == line_id).sum()),
            "frac_of_LINE": float(mask.mean()) if (y_true == line_id).any() else 0.0,
            # also CIRCLE precision killer share among CIRCLE predictions
            "n_pred_CIRCLE": int((yp == circ_id).sum()),
            "LINE_share_of_pred_CIRCLE": float(
                mask.sum() / max((yp == circ_id).sum(), 1)
            ),
        }

    # --- detailed groups on P2 ---
    yp = preds["P2"]
    groups = {
        "LINE→LINE": (y_true == line_id) & (yp == line_id),
        "LINE→CIRCLE": (y_true == line_id) & (yp == circ_id),
        "CIRCLE→CIRCLE": (y_true == circ_id) & (yp == circ_id),
        "short_CIRCLE→LINE": None,  # filled below
    }
    # short circle: span would need curves.json; approximate by polyline chord_len tiny OR use existing diag
    # Use closed_like OR curve_length in bottom 20% of CIRCLE lengths AND pred LINE
    circ_lens = np.array(
        [feats[i]["curve_length"] for i in range(n) if y_true[i] == circ_id],
        dtype=np.float64,
    )
    circ_p20 = float(np.percentile(circ_lens, 20)) if circ_lens.size else 0.0
    groups["short_CIRCLE→LINE"] = (
        (y_true == circ_id)
        & (yp == line_id)
        & np.array([feats[i]["curve_length"] <= circ_p20 for i in range(n)])
    )
    # also all CIRCLE→LINE
    groups["CIRCLE→LINE"] = (y_true == circ_id) & (yp == line_id)

    keys = [
        "normalized_chord_height",
        "max_chord_deviation",
        "total_turn_angle",
        "mean_turn_angle",
        "max_turn_angle",
        "curve_length",
        "axis_aligned_ratio",
    ]
    group_table = {}
    for gname, mask in groups.items():
        idx = np.where(mask)[0]
        group_table[gname] = {
            "n": int(idx.size),
            **{k: _stat([feats[i][k] for i in idx]) for k in keys},
            "dominant_axis_counts": {
                ax: int(sum(1 for i in idx if feats[i]["dominant_axis"] == ax))
                for ax in (0, 1, 2)
            },
            "closed_like_frac": float(
                np.mean([feats[i]["closed_like_endpoints"] for i in idx])
            )
            if idx.size
            else None,
        }

    # chord-height near-zero among LINE→CIRCLE
    b_idx = np.where(groups["LINE→CIRCLE"])[0]
    nh = np.array([feats[i]["normalized_chord_height"] for i in b_idx])
    chord_bins = {
        "≈0 (<1e-4)": int((nh < 1e-4).sum()),
        "tiny [1e-4,1e-3)": int(((nh >= 1e-4) & (nh < 1e-3)).sum()),
        "small [1e-3,1e-2)": int(((nh >= 1e-3) & (nh < 1e-2)).sum()),
        "bent [1e-2,1e-1)": int(((nh >= 1e-2) & (nh < 1e-1)).sum()),
        "very_bent ≥1e-1": int((nh >= 1e-1).sum()),
    }

    # length buckets for LINE→CIRCLE vs all LINE
    len_bucket_rows = []
    for bname in ["<P10", "P10–P25", "P25–P50", "P50–P75", "P75–P90", ">P90"]:
        line_in_b = [
            i
            for i in range(n)
            if y_true[i] == line_id
            and length_bucket(feats[i]["curve_length"], len_edges) == bname
        ]
        fp_in_b = [i for i in line_in_b if yp[i] == circ_id]
        len_bucket_rows.append(
            {
                "bucket": bname,
                "n_LINE": len(line_in_b),
                "n_LINE→CIRCLE": len(fp_in_b),
                "frac": (len(fp_in_b) / len(line_in_b)) if line_in_b else 0.0,
                "chord_height_median_fp": _stat(
                    [feats[i]["normalized_chord_height"] for i in fp_in_b]
                )["median"],
                "total_turn_median_fp": _stat(
                    [feats[i]["total_turn_angle"] for i in fp_in_b]
                )["median"],
            }
        )

    # orientation bias: dominant axis among A vs B
    orient = {}
    for gname in ("LINE→LINE", "LINE→CIRCLE"):
        idx = np.where(groups[gname])[0]
        orient[gname] = {
            "dominant_axis": {
                "X": group_table[gname]["dominant_axis_counts"][0],
                "Y": group_table[gname]["dominant_axis_counts"][1],
                "Z": group_table[gname]["dominant_axis_counts"][2],
            },
            "axis_aligned_ratio": group_table[gname]["axis_aligned_ratio"],
            "center": {
                ax: _stat([feats[i][f"center_{ax}"] for i in idx])
                for ax in ("x", "y", "z")
            },
        }

    payload = {
        "exp_detailed": "P2",
        "n_test": n,
        "line_length_percentiles": {
            "P10": float(len_edges[0]),
            "P25": float(len_edges[1]),
            "P50": float(len_edges[2]),
            "P75": float(len_edges[3]),
            "P90": float(len_edges[4]),
        },
        "cross_exp_LINE_to_CIRCLE": cross,
        "group_table": group_table,
        "LINE_to_CIRCLE_chord_height_bins": chord_bins,
        "LINE_to_CIRCLE_by_length_bucket": len_bucket_rows,
        "orientation": orient,
        "definitions": {
            "normalized_chord_height": "max distance to endpoint-chord / polyline length",
            "total_turn_angle": "sum of angle(t_i, t_{i+1}) in degrees",
            "short_CIRCLE": f"CIRCLE with curve_length <= P20 of CIRCLE lengths ({circ_p20:.6g})",
        },
    }
    (out_dir / "line_to_circle_diagnostics.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    # ---- histograms ----
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, key, title, xlim in [
        (axes[0, 0], "normalized_chord_height", "normalized chord height", (0, 0.05)),
        (axes[0, 1], "total_turn_angle", "total turn angle (°)", (0, 60)),
        (axes[1, 0], "curve_length", "curve length (normalized frame)", None),
        (axes[1, 1], "mean_turn_angle", "mean turn angle (°)", (0, 5)),
    ]:
        for gname, color in [
            ("LINE→LINE", "C0"),
            ("LINE→CIRCLE", "C3"),
            ("CIRCLE→CIRCLE", "C2"),
        ]:
            idx = np.where(groups[gname])[0]
            vals = np.array([feats[i][key] for i in idx], dtype=np.float64)
            if vals.size == 0:
                continue
            # subsample LINE→LINE for plot readability
            if gname == "LINE→LINE" and vals.size > 5000:
                rng = np.random.default_rng(0)
                vals = rng.choice(vals, 5000, replace=False)
            ax.hist(vals, bins=60, density=True, alpha=0.45, label=f"{gname} (n={groups[gname].sum()})", color=color)
        ax.set_title(title)
        if xlim:
            ax.set_xlim(*xlim)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.suptitle("P2 test: LINE→CIRCLE geometry vs controls")
    fig.tight_layout()
    fig.savefig(out_dir / "geom_histograms.png", dpi=140)
    plt.close(fig)

    # length-bucket bar
    fig, ax = plt.subplots(figsize=(8, 4))
    xs = [r["bucket"] for r in len_bucket_rows]
    ys = [r["frac"] for r in len_bucket_rows]
    ns = [r["n_LINE→CIRCLE"] for r in len_bucket_rows]
    ax.bar(xs, ys, color="C3", alpha=0.8)
    for i, (y, c) in enumerate(zip(ys, ns)):
        ax.text(i, y, f"n={c}", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("P(pred=CIRCLE | GT=LINE)")
    ax.set_title("LINE→CIRCLE rate by LINE length percentile bucket")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "length_bucket_rates.png", dpi=140)
    plt.close(fig)

    # ---- markdown ----
    def fmt_stat(s: dict) -> str:
        if not s or s.get("n", 0) == 0:
            return "—"
        return f"{s['median']:.4g} / {s['p90']:.4g} / {s['p95']:.4g}"

    md = []
    md.append("# LINE→CIRCLE diagnostics (P2 detailed, P0–T2 counts)\n")
    md.append("No model changes. Metrics: median / P90 / P95.\n")

    md.append("## 0. Cross-exp LINE→CIRCLE counts (test)\n")
    md.append("| Exp | LINE→CIRCLE | / n_LINE | frac | share of pred CIRCLE |")
    md.append("| --- | ---: | ---: | ---: | ---: |")
    for exp in args.exps:
        c = cross[exp]
        md.append(
            f"| {exp} | {c['LINE→CIRCLE']} | {c['n_LINE']} | {c['frac_of_LINE']:.3%} | "
            f"{c['LINE_share_of_pred_CIRCLE']:.1%} |"
        )
    md.append("")

    md.append("## 1–2. Group geometry table (P2)\n")
    md.append(
        "| Group | n | chord height (med/P90/P95) | total turn° | mean turn° | length | axis-align |"
    )
    md.append("| --- | ---: | --- | --- | --- | --- | --- |")
    for gname in (
        "LINE→LINE",
        "LINE→CIRCLE",
        "CIRCLE→CIRCLE",
        "CIRCLE→LINE",
        "short_CIRCLE→LINE",
    ):
        g = group_table[gname]
        md.append(
            f"| {gname} | {g['n']} | {fmt_stat(g['normalized_chord_height'])} | "
            f"{fmt_stat(g['total_turn_angle'])} | {fmt_stat(g['mean_turn_angle'])} | "
            f"{fmt_stat(g['curve_length'])} | {fmt_stat(g['axis_aligned_ratio'])} |"
        )
    md.append("")
    md.append("### LINE→CIRCLE chord-height bins\n")
    for k, v in chord_bins.items():
        md.append(f"- **{k}**: {v} / {len(b_idx)} ({v/max(len(b_idx),1):.1%})")
    md.append("")

    md.append("## 4. LINE→CIRCLE rate by length bucket\n")
    md.append("| bucket | n_LINE | n_FP | rate | FP chordH med | FP totalTurn med |")
    md.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for r in len_bucket_rows:
        md.append(
            f"| {r['bucket']} | {r['n_LINE']} | {r['n_LINE→CIRCLE']} | {r['frac']:.3%} | "
            f"{r['chord_height_median_fp']} | {r['total_turn_median_fp']} |"
        )
    md.append("")

    md.append("## 5. Orientation / frame (P2)\n")
    for gname in ("LINE→LINE", "LINE→CIRCLE"):
        o = orient[gname]
        dom = o["dominant_axis"]
        tot = sum(dom.values()) or 1
        md.append(
            f"- **{gname}** dominant axis: "
            f"X={dom['X']} ({dom['X']/tot:.1%}), "
            f"Y={dom['Y']} ({dom['Y']/tot:.1%}), "
            f"Z={dom['Z']} ({dom['Z']/tot:.1%}); "
            f"axis_aligned_ratio med={o['axis_aligned_ratio']['median']:.3f}"
        )
    md.append("")
    md.append("## Figures\n")
    md.append("- `geom_histograms.png`")
    md.append("- `length_bucket_rates.png`")
    md.append("")

    # auto reads
    med_a = group_table["LINE→LINE"]["normalized_chord_height"]["median"]
    med_b = group_table["LINE→CIRCLE"]["normalized_chord_height"]["median"]
    med_c = group_table["CIRCLE→CIRCLE"]["normalized_chord_height"]["median"]
    turn_a = group_table["LINE→LINE"]["total_turn_angle"]["median"]
    turn_b = group_table["LINE→CIRCLE"]["total_turn_angle"]["median"]
    turn_c = group_table["CIRCLE→CIRCLE"]["total_turn_angle"]["median"]
    p2_fp = cross["P2"]["LINE→CIRCLE"]
    p1_fp = cross.get("P1", {}).get("LINE→CIRCLE")
    md.append("## Auto reads\n")
    md.append(
        f"- Chord height medians: A={med_a:.4g}, B={med_b:.4g}, C={med_c:.4g}. "
        f"{'B≈A (true straight LINEs misclassified)' if med_b is not None and med_a is not None and abs(med_b-med_a)<1e-3 else 'see numbers'}."
    )
    md.append(
        f"- Total turn° medians: A={turn_a:.4g}, B={turn_b:.4g}, C={turn_c:.4g}."
    )
    if p1_fp is not None:
        md.append(
            f"- LINE→CIRCLE counts: P1={p1_fp}, P2={p2_fp} "
            f"(Δ={p2_fp-p1_fp:+d}, {(p2_fp-p1_fp)/max(p1_fp,1):+.1%} vs P1)."
        )
    short = max(len_bucket_rows, key=lambda r: r["frac"])
    md.append(
        f"- Highest LINE→CIRCLE rate length bucket: **{short['bucket']}** "
        f"({short['frac']:.2%}, n_FP={short['n_LINE→CIRCLE']})."
    )

    (out_dir / "line_to_circle_diagnostics.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nwrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
