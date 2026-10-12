"""V6A.1 audit renders."""
from __future__ import annotations

from pathlib import Path

import numpy as np

VIEW = np.array([[0.72, -0.36, 0.59], [0.68, 0.42, -0.60], [-0.15, 0.83, 0.53]])


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
    fig, ax = plt.subplots(figsize=(6.5, 5.2), dpi=120)
    ax.add_collection(
        PolyCollection([p2[tri] for tri in f], facecolors=(0.78, 0.78, 0.8, 0.18), edgecolors=(0.5, 0.5, 0.52, 0.05), linewidths=0.03)
    )
    segs, cols = [], []
    for i, pl in enumerate(polylines):
        q = (np.asarray(pl, float) @ VIEW.T)[:, :2]
        if len(q) >= 2:
            segs.append(q)
            cols.append(colors[i % len(colors)] if isinstance(colors, list) else colors)
    if segs:
        ax.add_collection(LineCollection(segs, colors=cols, linewidths=1.5, alpha=0.95))
    if pts is not None and len(pts):
        c = (np.asarray(pts, float) @ VIEW.T)[:, :2]
        ax.scatter(c[:, 0], c[:, 1], s=28, c=pt_c, zorder=6)
    ctr = p2.mean(0)
    r = max(float(np.ptp(p2, 0).max()) * 0.58, 1e-8)
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_audit(mesh, out: Path, frags, branches_by_pair, gaps, fb_audit, evidence, title):
    out.mkdir(parents=True, exist_ok=True)
    pal = ["#1d4ed8", "#b45309", "#0f766e", "#7c3aed", "#be123c", "#0891b2"]
    frag_lines = [f["points"] for f in frags]
    occ_lines = []
    for branches in branches_by_pair.values():
        occ_lines.extend([b["points"] for b in branches])
    _plot(
        mesh,
        frag_lines + occ_lines,
        [pal[i % len(pal)] for i in range(len(frag_lines))] + ["#111827"] * len(occ_lines),
        out / "01_fragments_and_occ_branches.png",
        f"{title} fragments + OCC branches",
    )
    for label, branches in branches_by_pair.items():
        pair = tuple(int(x) for x in label.split("_")[1:])
        pf = [f for f in frags if tuple(f["surface_pair"]) == pair]
        lines = [f["points"] for f in pf] + [b["points"] for b in branches]
        cols = [pal[i % len(pal)] for i in range(len(pf))] + ["#111827"] * len(branches)
        _plot(mesh, lines, cols, out / f"02_{label.lower()}_audit.png", f"{title} {label}")
    # pair 1,2 positive
    pair = (1, 2)
    pf = [f for f in frags if tuple(f["surface_pair"]) == pair]
    lines = [f["points"] for f in pf] + [b["points"] for b in branches_by_pair["PAIR_1_2"]]
    _plot(mesh, lines, pal, out / "04_pair_1_2_positive_control.png", f"{title} pair (1,2) positive control")
    # support samples along gaps
    sup_pts, sup_c = [], []
    for g in gaps:
        if g.get("classification") != "TRUE_INTERSECTION_FRAGMENTATION":
            continue
        # placeholder: show gap endpoints
        pass
    _plot(mesh, [f["points"] for f in frags], "#64748b", out / "05_xpart_support_samples.png", f"{title} gap support audit")
    ws = fb_audit.get("wire_start")
    we = fb_audit.get("wire_end")
    pf01 = [f for f in frags if tuple(f["surface_pair"]) == (0, 1)]
    lines = [f["points"] for f in pf01] + [b["points"] for b in branches_by_pair.get("PAIR_0_1", [])]
    _plot(
        mesh,
        lines,
        pal,
        out / "06_first_blocker_wire_001.png",
        f"{title} WIRE_001 {fb_audit.get('classification')}",
        pts=[ws, we] if ws and we else None,
    )
