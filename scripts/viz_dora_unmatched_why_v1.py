#!/usr/bin/env python3
"""Why fitted ELLIPSE/BSPLINE never 1-to-1 match, and why FRAGMENTED=77 is LINE-only.

Read-only on train800_build_v1. Isolated output dir.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_dora_unmatched_why_v1")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT / "scripts")]
from viz_dora_fitted_overlay_v1 import (  # noqa: E402
    BASE,
    COHORT,
    load_cad_geom,
    render_case,
    gt_family,
)

OUT = ROOT / "ours3/dora_unmatched_why_v1"
DIST, COV, TAN = 0.008, 0.85, 0.75
FITTED = ("LINE", "CIRCLE", "ARC", "ELLIPSE", "BSPLINE")
GTF = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")


def fail_gates(m):
    if not m:
        return {"no_metrics": True, "strong": False, "fail_distance": True, "fail_coverage": True, "fail_tangent": True}
    d_ok = m.get("d2g_mean_rel", 9) <= DIST and m.get("g2d_mean_rel", 9) <= DIST
    c_ok = min(m.get("coverage_d2g", 0), m.get("coverage_g2d", 0)) >= COV
    t_ok = m.get("tangent_compatibility", 0) >= TAN
    return {
        "strong": bool(d_ok and c_ok and t_ok),
        "fail_distance": not d_ok,
        "fail_coverage": not c_ok,
        "fail_tangent": not t_ok,
        "fail_distance_only": (not d_ok) and c_ok and t_ok,
        "fail_coverage_only": d_ok and (not c_ok) and t_ok,
    }


def scan():
    nearest = {t: Counter() for t in ("ELLIPSE", "BSPLINE")}
    gates = {t: Counter() for t in ("ELLIPSE", "BSPLINE")}
    residual = {t: [] for t in ("ELLIPSE", "BSPLINE")}
    frag_by_type = Counter()
    frag_groups = defaultdict(list)
    ell_cases, bs_unmatched, bs_partial, line_frag = [], [], [], []
    for cdir in sorted((BASE / "cad").iterdir()):
        cad = cdir.name
        fits = json.loads((cdir / "dora/fitted_curves.json").read_text())["curves"]
        corr = json.loads((cdir / "correspondence.json").read_text())["records"]
        gts = {int(g["edge_id"]): g for g in json.loads((cdir / "gt_brep_curves.json").read_text())["curves"]}
        for rec, f in zip(corr, fits):
            gt = gts.get(rec.get("gt_curve_id"))
            gtyp = None if gt is None else gt_family(gt["curve_type"])
            cls = rec["classification"]
            m = rec.get("metrics") or {}
            row = {
                "cad_id": cad,
                "dora_curve_index": int(rec["dora_curve_index"]),
                "chain_id": int(f["chain_id"]),
                "fitted_type": f["type"],
                "gt_type": gtyp,
                "gt_curve_id": rec.get("gt_curve_id"),
                "classification": cls,
                "metrics": m,
                "normalized_residual": float(f.get("normalized_residual") or 0),
                "curve_length": f.get("curve_length"),
            }
            if f["type"] in ("ELLIPSE", "BSPLINE"):
                nearest[f["type"]][gtyp or "NONE"] += 1
                g = fail_gates(m)
                if g["strong"]:
                    gates[f["type"]]["would_be_strong_but_not_1to1"] += 1
                else:
                    if g["fail_coverage"]:
                        gates[f["type"]]["fail_coverage"] += 1
                    if g["fail_distance"]:
                        gates[f["type"]]["fail_distance"] += 1
                    if g["fail_tangent"]:
                        gates[f["type"]]["fail_tangent"] += 1
                    if g["fail_coverage"] and g["fail_distance"]:
                        gates[f["type"]]["fail_both_dist_and_cov"] += 1
                residual[f["type"]].append(row["normalized_residual"])
            if f["type"] == "ELLIPSE":
                ell_cases.append(row)
            if f["type"] == "BSPLINE" and cls == "UNMATCHED":
                bs_unmatched.append(row)
            if f["type"] == "BSPLINE" and cls == "PARTIAL":
                bs_partial.append(row)
            if cls == "FRAGMENTED":
                frag_by_type[f["type"]] += 1
                frag_groups[(cad, rec.get("gt_curve_id"))].append(row)
                if f["type"] == "LINE":
                    line_frag.append(row)
    return {
        "nearest": {k: dict(v) for k, v in nearest.items()},
        "gates": {k: dict(v) for k, v in gates.items()},
        "residual_p50": {k: float(np.median(v)) if v else None for k, v in residual.items()},
        "residual_lt_005": {k: int(sum(x <= 0.005 for x in v)) for k, v in residual.items()},
        "n": {k: len(v) for k, v in residual.items()},
        "frag_by_type": dict(frag_by_type),
        "ell_cases": ell_cases,
        "bs_unmatched": bs_unmatched,
        "bs_partial": bs_partial,
        "line_frag": line_frag,
        "frag_groups": frag_groups,
    }


def draw_explainer(stats, path: Path):
    fig, ax = plt.subplots(figsize=(12.4, 7.6), dpi=140)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Why ELLIPSE/BSPLINE never enter FRAGMENTED=77", fontsize=14, pad=10, fontweight="bold")

    def box(x, y, w, h, fc, title, body, tc="#0f172a"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012", fc=fc, ec="#94a3b8", lw=0.8))
        ax.text(x + 0.018, y + h - 0.028, title, fontsize=10, fontweight="bold", color=tc, va="top")
        ax.text(x + 0.018, y + h - 0.055, body, fontsize=8.6, color="#334155", va="top", wrap=True)

    box(0.04, 0.72, 0.92, 0.22, "#f1f5f9",
        "1-to-1 classifier  (must pass STRONG first)",
        "STRONG = dist≤0.008  AND  coverage≥0.85 both ways  AND  tangent≥0.75\n"
        "then: unique both ways → MATCHED   |   1 GT ← many Dora → FRAGMENTED   |   1 Dora → many GT → MERGED\n"
        "if not STRONG: partial cover → PARTIAL, else UNMATCHED.   Ellipse/BSpline almost never become STRONG.")

    box(0.04, 0.38, 0.44, 0.30, "#fef3c7",
        "110 fitted ELLIPSE  →  0 MATCHED, 0 FRAGMENTED",
        "Nearest GT type:\n"
        f"  LINE {stats['nearest']['ELLIPSE'].get('LINE', 0)}   CIRCLE {stats['nearest']['ELLIPSE'].get('CIRCLE', 0)}\n"
        f"  BSPLINE {stats['nearest']['ELLIPSE'].get('BSPLINE', 0)}   ELLIPSE {stats['nearest']['ELLIPSE'].get('ELLIPSE', 0)}\n"
        "They are a different population: Dora chains that the fitter\n"
        "called ELLIPSE. They do not sit on GT ellipses.\n"
        f"Fit residual median {stats['residual_p50']['ELLIPSE']:.4f}  "
        f"({stats['residual_lt_005']['ELLIPSE']}/{stats['n']['ELLIPSE']} ≤0.005)\n"
        "→ fitting to the chain often OK; correspondence fails.")

    box(0.52, 0.38, 0.44, 0.30, "#fee2e2",
        "True GT ELLIPSE  (chopped by Dora)",
        "GT ellipse is covered by LINE / ARC / CIRCLE pieces.\n"
        "Those pieces fail STRONG (coverage/distance),\n"
        "so they are UNMATCHED, not FRAGMENTED.\n"
        "Program FRAGMENTED requires STRONG first.\n"
        "That is why the 77 FRAGMENTED are LINE-only.")

    box(0.04, 0.06, 0.44, 0.28, "#e0f2fe",
        "355 fitted BSPLINE  →  0 MATCHED, 7 PARTIAL",
        f"Nearest GT: LINE {stats['nearest']['BSPLINE'].get('LINE', 0)}  "
        f"CIRCLE {stats['nearest']['BSPLINE'].get('CIRCLE', 0)}\n"
        f"  ELLIPSE {stats['nearest']['BSPLINE'].get('ELLIPSE', 0)}  "
        f"BSPLINE {stats['nearest']['BSPLINE'].get('BSPLINE', 0)}\n"
        "Only 4 even point at a GT BSPLINE; none pass 1-to-1.\n"
        "Typical fail: chain is a LINE/loop, fitter falls back to spline.")

    nfrag = stats["frag_by_type"]
    box(0.52, 0.06, 0.44, 0.28, "#dcfce7",
        "Program FRAGMENTED = 77, all LINE",
        f"LINE {nfrag.get('LINE', 0)}  CIRCLE {nfrag.get('CIRCLE', 0)}  "
        f"ARC {nfrag.get('ARC', 0)}\n"
        f"ELLIPSE {nfrag.get('ELLIPSE', 0)}  BSPLINE {nfrag.get('BSPLINE', 0)}\n"
        "These Dora LINEs DID pass STRONG against one GT LINE,\n"
        "but that GT LINE also matched other Dora LINEs.\n"
        "That is a different bug from ellipse chopping.")

    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.12)
    plt.close(fig)


def draw_bars(stats, path: Path):
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.4), dpi=140)
    colors = {"LINE": "#64748b", "CIRCLE": "#38bdf8", "ELLIPSE": "#f59e0b", "BSPLINE": "#a78bfa", "NONE": "#ef4444"}
    for ax, key, title in (
        (axes[0], "ELLIPSE", "110 fitted ELLIPSE\nnearest GT type"),
        (axes[1], "BSPLINE", "355 fitted BSPLINE\nnearest GT type"),
    ):
        labels = ["LINE", "CIRCLE", "ELLIPSE", "BSPLINE"]
        vals = [stats["nearest"][key].get(k, 0) for k in labels]
        ax.bar(labels, vals, color=[colors[k] for k in labels])
        ax.set_title(title, fontsize=11)
        ax.set_ylabel("count")
        for i, v in enumerate(vals):
            ax.text(i, v + max(vals) * 0.02, str(v), ha="center", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax = axes[2]
    labs = ["coverage\n<0.85", "distance\n>0.008", "tangent\n<0.75", "both dist\n+ coverage"]
    e = stats["gates"]["ELLIPSE"]
    b = stats["gates"]["BSPLINE"]
    x = np.arange(len(labs))
    ax.bar(x - 0.18, [e.get("fail_coverage", 0), e.get("fail_distance", 0), e.get("fail_tangent", 0), e.get("fail_both_dist_and_cov", 0)],
           0.36, label="ELLIPSE", color="#f59e0b")
    ax.bar(x + 0.18, [b.get("fail_coverage", 0), b.get("fail_distance", 0), b.get("fail_tangent", 0), b.get("fail_both_dist_and_cov", 0)],
           0.36, label="BSPLINE", color="#a78bfa")
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=8)
    ax.set_title("Why STRONG fails\n(vs nearest GT, not vs true ellipse)", fontsize=11)
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.12)
    plt.close(fig)


def overlay_one(cohort, row, title, extra_lines, outp, geom=None, dora=None, fit=None, gt=None, others=None):
    if geom is None:
        geom = load_cad_geom(row["cad_id"], cohort[row["cad_id"]]["assets"])
    i = row["dora_curve_index"]
    f = geom["fits"][i]
    if dora is None:
        dora = [geom["chain_pts"][int(f["chain_id"])]]
    if fit is None:
        fit = [geom["fit_xyz"][i]]
    if gt is None and row.get("gt_curve_id") is not None:
        gidx = next((j for j, g in enumerate(geom["gts"]) if int(g["edge_id"]) == int(row["gt_curve_id"])), None)
        gt = None if gidx is None else geom["gt_xyz"][gidx]
    if others:
        dora = dora + others[0]
        fit = fit + others[1]
    m = row.get("metrics") or {}
    lines = [
        f"GT type:        {row.get('gt_type')}",
        f"Fitted type:    {f['type']}",
        f"classification: {row['classification']}",
        f"Dora → GT cov:  {m.get('coverage_d2g', 0):.1%}",
        f"GT → Dora cov:  {m.get('coverage_g2d', 0):.1%}",
        f"distance d2g:   {m.get('d2g_mean_rel', 0):.4f}",
        f"distance g2d:   {m.get('g2d_mean_rel', 0):.4f}",
        f"tangent:        {m.get('tangent_compatibility', 0):.3f}",
        f"fit residual:   {row.get('normalized_residual', f.get('normalized_residual', 0)):.4f}",
        *extra_lines,
    ]
    sub = f"{row['cad_id']}  dora[{i}]  GT {row.get('gt_curve_id')}"
    render_case(outp, geom, title, sub, lines, dora, fit, gt)
    return geom


def pick_line_frag(stats):
    best = None
    for (cad, gid), rows in stats["frag_groups"].items():
        if gid is None or len(rows) < 2:
            continue
        if any(r["fitted_type"] != "LINE" for r in rows):
            continue
        if best is None or (2 <= len(rows) <= 4 and len(rows) > len(best[1])):
            best = ((cad, gid), rows)
            if 2 <= len(rows) <= 4:
                return rows
    return best[1] if best else []


def main():
    if OUT.exists() and (OUT / "WHY.json").exists():
        for p in (OUT / "figures").glob("*.png"):
            p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    cohort = {}
    for line in COHORT.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            cohort[r["cad_id"]] = r
    print("scanning", flush=True)
    stats = scan()
    dump(OUT / "WHY.json", {k: stats[k] for k in ("nearest", "gates", "residual_p50", "residual_lt_005", "n", "frag_by_type")})
    draw_explainer(stats, OUT / "figures" / "00_explainer.png")
    draw_bars(stats, OUT / "figures" / "01_nearest_gt_and_gates.png")

    # A. fitted ellipse around a LINE (known-readable canary)
    ell_a = next(
        (r for r in stats["ell_cases"] if r["cad_id"] == "deepcad__0028_00283333" and r["dora_curve_index"] == 3),
        None,
    ) or next((r for r in stats["ell_cases"] if r["gt_type"] == "LINE" and 0.001 < r["normalized_residual"] <= 0.005), None)
    if ell_a:
        overlay_one(
            cohort, ell_a,
            "A  Fitted ELLIPSE vs nearest GT LINE",
            ["fit residual small → chain fit OK", "nearest GT is a LINE, coverage ~0", "this is why 110 never MATCH"],
            OUT / "figures" / f"A_fitted_ellipse_vs_LINE_{ell_a['cad_id']}.png",
        )

    # B. reuse GT-side ellipse chop from known good CAD
    geom = load_cad_geom("deepcad__0091_00919064", cohort["deepcad__0091_00919064"]["assets"])
    gidx = next(j for j, g in enumerate(geom["gts"]) if int(g["edge_id"]) == 242)
    gp = geom["gt_xyz"][gidx]
    from viz_dora_fitted_overlay_v1 import pair_pts, near, frames_aligned
    attached = []
    for i, fp in enumerate(geom["fit_xyz"]):
        if gp is None:
            break
        m = pair_pts(fp, gp, geom["diag"])
        if near(m):
            attached.append(i)
    dora = [geom["chain_pts"][int(geom["fits"][i]["chain_id"])] for i in attached]
    fit = [geom["fit_xyz"][i] for i in attached]
    types = [geom["fits"][i]["type"] for i in attached]
    row_b = {
        "cad_id": "deepcad__0091_00919064",
        "dora_curve_index": attached[0] if attached else 0,
        "gt_curve_id": 242,
        "gt_type": "ELLIPSE",
        "classification": "UNMATCHED (GT-side chopped)",
        "metrics": pair_pts(np.vstack(fit), gp, geom["diag"]) if fit else {},
        "normalized_residual": 0,
    }
    overlay_one(
        cohort, row_b,
        "B  GT ELLIPSE chopped  —  not in the 77",
        [f"Dora pieces: {', '.join(types)}", "fitted types are ARC/CIRCLE, not ELLIPSE",
         "pieces fail STRONG → UNMATCHED", "never counted as FRAGMENTED"],
        OUT / "figures" / "B_gt_ellipse_chopped_0091.png",
        geom=geom, dora=dora, fit=fit, gt=gp,
    )

    # C. LINE FRAGMENTED (the actual 77)
    fr = pick_line_frag(stats)
    if fr:
        geom = load_cad_geom(fr[0]["cad_id"], cohort[fr[0]["cad_id"]]["assets"])
        gid = fr[0]["gt_curve_id"]
        gidx = next(j for j, g in enumerate(geom["gts"]) if int(g["edge_id"]) == int(gid))
        dora = [geom["chain_pts"][int(geom["fits"][r["dora_curve_index"]]["chain_id"])] for r in fr]
        fit = [geom["fit_xyz"][r["dora_curve_index"]] for r in fr]
        overlay_one(
            cohort, {**fr[0], "classification": "FRAGMENTED"},
            "C  Program FRAGMENTED  —  these ARE the 77",
            [f"{len(fr)} Dora LINEs all STRONG-match one GT LINE",
             "this class requires STRONG first",
             "ellipse fragments never get here"],
            OUT / "figures" / f"C_line_FRAGMENTED_{fr[0]['cad_id']}.png",
            geom=geom, dora=dora, fit=fit, gt=geom["gt_xyz"][gidx],
        )

    # D. BSPLINE unmatched vs LINE
    bs = next(
        (r for r in stats["bs_unmatched"] if r["cad_id"] == "deepcad__0084_00840479"),
        None,
    ) or next((r for r in stats["bs_unmatched"] if r["cad_id"].startswith("deepcad")), None)
    if bs:
        overlay_one(
            cohort, bs,
            "D  Fitted BSPLINE vs nearest GT LINE",
            ["fitter fell back to spline on a chain", "nearest GT is LINE, not BSPLINE",
             "0 of 355 fitted BSPLINE are MATCHED"],
            OUT / "figures" / f"D_fitted_bspline_vs_LINE_{bs['cad_id']}.png",
        )
    if stats["bs_partial"]:
        overlay_one(
            cohort, stats["bs_partial"][0],
            "E  Fitted BSPLINE PARTIAL  (7 cases)",
            ["only 7/355 are PARTIAL, rest UNMATCHED", "Dora chain covers only part of GT"],
            OUT / "figures" / f"E_bspline_PARTIAL_{stats['bs_partial'][0]['cad_id']}.png",
        )

    print(json.dumps({"out": str(OUT), "figures": sorted(p.name for p in (OUT / "figures").glob("*.png"))}, indent=2))


if __name__ == "__main__":
    main()
