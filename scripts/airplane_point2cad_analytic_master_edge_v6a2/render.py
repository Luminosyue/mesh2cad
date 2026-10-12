"""V6A2 visualization."""
from __future__ import annotations

from pathlib import Path

import numpy as np

VIEW = np.array([[0.72, -0.36, 0.59], [0.68, 0.42, -0.60], [-0.15, 0.83, 0.53]])
PAL = ["#1d4ed8", "#b45309", "#0f766e", "#7c3aed", "#be123c", "#0891b2", "#ca8a04", "#365314"]


def _plot(mesh, polylines, colors, path: Path, title: str, pts=None, pt_c="#dc2626"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection

    v = np.asarray(mesh.vertices, float)
    f = np.asarray(mesh.faces, int)
    if len(f) > 3500:
        f = f[np.linspace(0, len(f) - 1, 3500, dtype=int)]
    p2 = (v @ VIEW.T)[:, :2]
    fig, ax = plt.subplots(figsize=(6.4, 5.1), dpi=110)
    ax.add_collection(
        PolyCollection(
            [p2[tri] for tri in f],
            facecolors=(0.78, 0.78, 0.8, 0.18),
            edgecolors=(0.5, 0.5, 0.52, 0.05),
            linewidths=0.03,
        )
    )
    segs, cols = [], []
    for i, pl in enumerate(polylines):
        a = np.asarray(pl, float)
        if a.ndim != 2 or len(a) < 2:
            continue
        q = (a @ VIEW.T)[:, :2]
        segs.append(q)
        cols.append(colors[i % len(colors)] if isinstance(colors, list) else colors)
    if segs:
        ax.add_collection(LineCollection(segs, colors=cols, linewidths=1.6, alpha=0.95))
    if pts is not None and len(pts):
        c = (np.asarray(pts, float) @ VIEW.T)[:, :2]
        ax.scatter(c[:, 0], c[:, 1], s=26, c=pt_c, zorder=6)
    ctr = p2.mean(0)
    r = max(float(np.ptp(p2, 0).max()) * 0.58, 1e-8)
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_v6a2(mesh, out: Path, pair_frags, extracted, results, master_branches, before, after, title: str):
    out.mkdir(parents=True, exist_ok=True)
    _plot(mesh, [f["points"] for f in pair_frags], PAL, out / "01_pair02_raw_fragments.png", f"{title} (0,2) raw fragments")
    gap_pts = []
    gap_lines = []
    for r in results:
        if r.get("p_left") and r.get("p_right"):
            gap_lines.append(np.vstack([r["p_left"], r["p_right"]]))
            gap_pts.extend([r["p_left"], r["p_right"]])
        if r.get("points") is not None:
            gap_lines.append(r["points"])
    _plot(mesh, gap_lines or [np.zeros((2, 3))], ["#dc2626"] * 8, out / "02_four_eligible_gaps.png", f"{title} 4 eligible gaps", pts=gap_pts)
    occ_lines = [b["points"] for b in extracted]
    _plot(mesh, occ_lines, ["#111827"] * len(occ_lines), out / "03_all_occ_branches_0_2.png", f"{title} all OCC (0,2) branches n={len(occ_lines)}")
    matched = [r.get("points") for r in results if r.get("points") is not None]
    _plot(mesh, matched or occ_lines[:1], PAL, out / "04_candidate_matched_branch.png", f"{title} candidates on OCC_BRANCH_000")
    _plot(mesh, matched or [np.zeros((2, 3))], ["#7c3aed"] * 8, out / "05_analytic_missing_intervals.png", f"{title} analytic missing intervals")
    _plot(mesh, [mb["points"] for mb in master_branches], ["#16a34a"] * 8, out / "06_recovered_master_branches.png", f"{title} master branches n={len(master_branches)}")
    _plot(
        mesh,
        [f["points"] for f in pair_frags] + [mb["points"] for mb in master_branches],
        ["#94a3b8"] * len(pair_frags) + ["#16a34a"] * len(master_branches),
        out / "07_fragments_vs_masters.png",
        f"{title} fragments vs recovered masters",
    )
    _plot(mesh, matched or [np.zeros((2, 3))], "#0f766e", out / "08_xpart_support_intervals.png", f"{title} X-Part support intervals")
    straight = []
    analytic = []
    for r in results:
        if r.get("p_left") and r.get("p_right"):
            straight.append(np.vstack([r["p_left"], r["p_right"]]))
        if r.get("points") is not None:
            analytic.append(r["points"])
    _plot(mesh, straight + analytic, ["#dc2626"] * len(straight) + ["#16a34a"] * len(analytic), out / "09_straight_vs_analytic.png", f"{title} red=straight QA-only  green=analytic")
    _plot(mesh, [mb["points"] for mb in master_branches], "#1d4ed8", out / "10_surface0_plus_masters.png", f"{title} surface 0 + masters")
    _plot(mesh, [mb["points"] for mb in master_branches], "#b45309", out / "11_surface2_plus_masters.png", f"{title} surface 2 + masters")
    _plot(mesh, [mb["points"] for mb in master_branches], "#7c3aed", out / "12_shared_master_edges.png", f"{title} shared (0,2) master edges")
    _plot(mesh, [f["points"] for f in pair_frags], PAL, out / "13_pair_topology_before.png", f"{title} pair topology before d1={before.get('degree1')}")
    after_lines = [mb["points"] for mb in master_branches]
    _plot(mesh, after_lines or [np.zeros((2, 3))], "#16a34a", out / "14_pair_topology_after.png", f"{title} pair topology after d1={after.get('degree1')}")
    _plot(
        mesh,
        [f["points"] for f in pair_frags] + [mb["points"] for mb in master_branches],
        PAL,
        out / "15_whole_part_diagnostic.png",
        f"{title} whole-part diagnostic (0,2 replaced only)",
    )
    for r in results:
        if r.get("points") is not None:
            _plot(mesh, [r["points"]], "#7c3aed", out / f"cand_{r['candidate_id']}.png", f"{title} {r['candidate_id']} {r['status']}")
