#!/usr/bin/env python3
"""DORA_BREP_GRANULARITY_CANARY_V1 — visualization / analysis only.

Answers whether rare fitted ELLIPSE / BSPLINE UNMATCHED is mainly
Dora-chain granularity != single GT BRep-edge granularity.

Does not rerun Dora, chain extraction, curve fitting, correspondence,
thresholds, C2 training, or write back into the frozen V1 dataset.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.interpolate import splev
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT / "scripts")]

from curve_token_v1.config import GEOMABS_TO_NAME
from curve_token_v1.extract_brep_curves import extract_curves_from_step
from curve_token_v1.occ_curve_v1 import (
    arclength_params,
    eval_point,
    load_step_shape,
    make_adaptor,
)
from dora_fitted_curve_dataset_v1 import extract_chains, graph_from_dora, objverts
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_IndexedMapOfShape

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_dora_brep_granularity_canary_v1")

SOURCE = ROOT / "ours3/dora_fitted_curve_v1_rare_type_failure_audit_v4/VISUAL_CASE_MANIFEST.json"
COHORT = ROOT / "ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl"
V1_CAD = ROOT / "ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad"
OUT = ROOT / "ours3/dora_brep_granularity_canary_v1"

N_SAMPLE = 256
COVER_GOOD = 0.85
COVER_WEAK = 0.50
DIST_REL = 0.008  # analysis-only; frozen correspondence is not rewritten
IMPROVE = 0.20
OTHER_GT_COLORS = [
    "#ff7f0e",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#c49c94",
    "#f7b6d2",
    "#c7c7c7",
    "#dbdb8d",
    "#9edae5",
    "#98df8a",
    "#ff9896",
    "#c5b0d5",
]
LABELS = (
    "SINGLE_GT_EDGE_COMPATIBLE",
    "MULTI_GT_SAME_PRIMITIVE",
    "MULTI_GT_HETEROGENEOUS_PRIMITIVES",
    "FITTED_TYPE_FALSE_POSITIVE",
    "NO_REASONABLE_GT_GEOMETRY",
    "AMBIGUOUS",
)


def _f(x):
    if isinstance(x, (np.floating, float)):
        return float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    return x


def _dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def _as(x) -> np.ndarray:
    return np.asarray(x, dtype=np.float64)


def polyline_length(pts: np.ndarray) -> float:
    if len(pts) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def densify_polyline(pts: np.ndarray, n: int = N_SAMPLE, closed: bool = False) -> np.ndarray:
    pts = np.asarray(pts, dtype=np.float64)
    if len(pts) == 0:
        return pts.reshape(0, 3)
    if closed and np.linalg.norm(pts[0] - pts[-1]) > 1e-12:
        pts = np.vstack([pts, pts[0]])
    if len(pts) == 1:
        return np.repeat(pts, n, axis=0)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cum[-1])
    if total <= 1e-15:
        return np.repeat(pts[:1], n, axis=0)
    t = np.linspace(0.0, total, n)
    out = np.empty((n, 3), dtype=np.float64)
    for k in range(3):
        out[:, k] = np.interp(t, cum, pts[:, k])
    return out


def sample_fitted(fit: dict, n: int = N_SAMPLE) -> np.ndarray:
    t = fit["type"]
    a = lambda k: _as(fit[k])
    u0, u1 = float(fit.get("u0", 0.0)), float(fit.get("u1", 1.0))
    u = np.linspace(u0, u1, n)
    if t == "LINE":
        return a("origin")[None] + np.linspace(0.0, 1.0, n)[:, None] * float(fit["length"]) * a("direction")[None]
    if t in ("CIRCLE", "ARC"):
        return a("center")[None] + float(fit["radius"]) * (
            np.cos(u)[:, None] * a("x_axis")[None] + np.sin(u)[:, None] * a("y_axis")[None]
        )
    if t == "ELLIPSE":
        return (
            a("center")[None]
            + float(fit["major_radius"]) * np.cos(u)[:, None] * a("major_axis")[None]
            + float(fit["minor_radius"]) * np.sin(u)[:, None] * a("minor_axis")[None]
        )
    tck = fit["tck"]
    uu = np.linspace(0.0, 1.0, n)
    return np.asarray(splev(uu, (np.asarray(tck[0]), np.asarray(tck[1]), int(tck[2])))).T


def viz_type(curve_type: str, is_closed: bool) -> str:
    if curve_type == "CIRCLE":
        return "CIRCLE" if is_closed else "ARC"
    if curve_type in ("BEZIER",):
        return "BSPLINE"
    if curve_type in ("LINE", "ELLIPSE", "BSPLINE"):
        return curve_type
    return "OTHER"


def load_obj(path: Path):
    verts, faces = [], []
    for line in Path(path).read_text(errors="ignore").splitlines():
        if line.startswith("v "):
            verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith("f "):
            ids = []
            for tok in line.split()[1:]:
                ids.append(int(tok.split("/")[0]) - 1)
            if len(ids) >= 3:
                faces.append(ids)
    return np.asarray(verts, dtype=np.float64), faces


def extract_gt_edges(step_path: Path, n: int = N_SAMPLE):
    extracted = extract_curves_from_step(Path(step_path))
    by = {int(c["edge_id"]): c for c in extracted["curves"]}
    shape = load_step_shape(Path(step_path))
    mp = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, mp)
    edges = []
    for i in range(1, mp.Size() + 1):
        eid = i - 1
        rec = by.get(eid)
        edge = TopoDS.Edge_s(mp.FindKey(i))
        try:
            adaptor = make_adaptor(edge)
            u0 = float(adaptor.FirstParameter()) if rec is None else float(rec["u_start"])
            u1 = float(adaptor.LastParameter()) if rec is None else float(rec["u_end"])
            us, _ = arclength_params(adaptor, n, u0, u1)
            pts = np.asarray([eval_point(adaptor, float(u)) for u in us], dtype=np.float64)
        except Exception:
            continue
        if rec is None:
            ctype, closed, length, verts, params = "OTHER", False, polyline_length(pts), [], {}
            start, end = pts[0], pts[-1]
        else:
            ctype = rec["curve_type"]
            closed = bool(rec.get("is_closed", False))
            length = float(rec.get("length") or polyline_length(pts))
            verts = [int(v) for v in rec.get("vertex_ids") or []]
            params = rec.get("world_parameters") or {}
            start, end = _as(rec["start_point"]), _as(rec["end_point"])
        vtype = viz_type(ctype, closed)
        edges.append(
            {
                "edge_id": eid,
                "occ_type": ctype,
                "viz_type": vtype,
                "is_closed": closed,
                "points": pts,
                "length": length,
                "bbox_min": pts.min(0),
                "bbox_max": pts.max(0),
                "start": start,
                "end": end,
                "vertex_ids": verts,
                "params": params,
            }
        )
    vertex_to_edges = {}
    for e in edges:
        for v in e["vertex_ids"]:
            if v < 0:
                continue
            vertex_to_edges.setdefault(v, []).append(e["edge_id"])
    adj = {e["edge_id"]: set() for e in edges}
    for ids in vertex_to_edges.values():
        for a in ids:
            for b in ids:
                if a != b:
                    adj[a].add(b)
    return edges, adj, extracted


def bbox_overlap(a_min, a_max, b_min, b_max, pad=0.0):
    return bool(
        np.all(a_min - pad <= b_max)
        and np.all(b_min - pad <= a_max)
    )


def metrics_pair(src: np.ndarray, tgt: np.ndarray, diag: float) -> dict:
    if len(src) == 0 or len(tgt) == 0:
        empty = {
            "dora_to_gt_mean": None,
            "gt_to_dora_mean": None,
            "dora_to_gt_mean_rel": None,
            "gt_to_dora_mean_rel": None,
            "dora_to_gt_coverage": 0.0,
            "gt_to_dora_coverage": 0.0,
        }
        return empty
    d2g = cKDTree(tgt).query(src)[0]
    g2d = cKDTree(src).query(tgt)[0]
    tol = DIST_REL * diag
    return {
        "dora_to_gt_mean": float(d2g.mean()),
        "gt_to_dora_mean": float(g2d.mean()),
        "dora_to_gt_mean_rel": float(d2g.mean() / diag),
        "gt_to_dora_mean_rel": float(g2d.mean() / diag),
        "dora_to_gt_coverage": float((d2g <= tol).mean()),
        "gt_to_dora_coverage": float((g2d <= tol).mean()),
    }


def score(m: dict) -> float:
    if m is None:
        return -1.0
    return float(m["dora_to_gt_coverage"] + m["gt_to_dora_coverage"]) - 0.25 * (
        (m["dora_to_gt_mean_rel"] or 1.0) + (m["gt_to_dora_mean_rel"] or 1.0)
    )


def good(m: dict, cover=COVER_GOOD) -> bool:
    return (
        m is not None
        and m["dora_to_gt_coverage"] >= cover
        and m["gt_to_dora_coverage"] >= cover
    )


def same_analytic(a: dict, b: dict, diag: float) -> bool:
    ta, tb = a["viz_type"], b["viz_type"]
    pa, pb = a.get("params") or {}, b.get("params") or {}
    pos = 3e-3 * diag
    rel = 3e-3 * diag

    def nrm(v):
        v = _as(v)
        n = np.linalg.norm(v)
        return v / n if n > 1e-15 else v

    if ta in ("CIRCLE", "ARC") and tb in ("CIRCLE", "ARC"):
        if "center" not in pa or "center" not in pb:
            return False
        return (
            np.linalg.norm(_as(pa["center"]) - _as(pb["center"])) <= pos
            and abs(float(pa["radius"]) - float(pb["radius"])) <= rel
            and abs(float(np.dot(nrm(pa["normal"]), nrm(pb["normal"])))) >= 0.99
        )
    if ta == "ELLIPSE" and tb == "ELLIPSE":
        if "center" not in pa or "center" not in pb:
            return False
        return (
            np.linalg.norm(_as(pa["center"]) - _as(pb["center"])) <= pos
            and abs(float(pa["major_radius"]) - float(pb["major_radius"])) <= rel
            and abs(float(pa["minor_radius"]) - float(pb["minor_radius"])) <= rel
            and abs(float(np.dot(nrm(pa["normal"]), nrm(pb["normal"])))) >= 0.99
        )
    if ta == "LINE" and tb == "LINE":
        if "direction" not in pa or "direction" not in pb:
            return False
        da, db = nrm(pa["direction"]), nrm(pb["direction"])
        if abs(float(np.dot(da, db))) < 0.99:
            return False
        origin = _as(pa.get("origin", a["start"]))
        pt = _as(pb.get("origin", b["start"]))
        return float(np.linalg.norm(np.cross(pt - origin, da))) <= pos
    if ta == "BSPLINE" and tb == "BSPLINE":
        return True
    return False


def set_same_primitive(edges_by_id: dict, ids: list, diag: float) -> bool:
    if len(ids) <= 1:
        return True
    types = {edges_by_id[i]["viz_type"] for i in ids}
    analytic = {("CIRCLE" if t == "ARC" else t) for t in types}
    if len(analytic) != 1:
        return False
    base = edges_by_id[ids[0]]
    return all(same_analytic(base, edges_by_id[i], diag) for i in ids[1:])


def connected_components(ids, adj):
    remain = set(ids)
    comps = []
    while remain:
        start = min(remain)
        stack = [start]
        comp = set()
        while stack:
            x = stack.pop()
            if x in comp or x not in remain:
                continue
            comp.add(x)
            stack.extend(adj.get(x, set()) & remain)
        remain -= comp
        comps.append(sorted(comp))
    return comps


def greedy_grow(chain: np.ndarray, nearby: list, edges_by_id: dict, adj: dict, diag: float):
    if not nearby:
        return [], {"dora_to_gt_coverage": 0.0, "gt_to_dora_coverage": 0.0,
                    "dora_to_gt_mean_rel": None, "gt_to_dora_mean_rel": None,
                    "dora_to_gt_mean": None, "gt_to_dora_mean": None}
    singles = []
    for eid in nearby:
        m = metrics_pair(chain, edges_by_id[eid]["points"], diag)
        singles.append((score(m), eid, m))
    singles.sort(reverse=True)
    chosen = [singles[0][1]]
    chosen_pts = edges_by_id[chosen[0]]["points"]
    best_m = singles[0][2]
    unused = set(nearby) - set(chosen)
    improved = True
    while unused and improved:
        improved = False
        border = set()
        for eid in chosen:
            border |= adj.get(eid, set())
        cands = [i for i in unused if i in border] or list(unused)
        ranked = []
        for eid in cands:
            pts = np.vstack([chosen_pts, edges_by_id[eid]["points"]])
            m = metrics_pair(chain, pts, diag)
            ranked.append((score(m), eid, m, pts))
        ranked.sort(reverse=True)
        if ranked and ranked[0][0] > score(best_m) + 1e-6:
            _, eid, m, pts = ranked[0]
            chosen.append(eid)
            chosen_pts = pts
            best_m = m
            unused.remove(eid)
            improved = True
    return chosen, best_m


def best_connected_set(chain, grow_ids, nearby, edges_by_id, adj, diag):
    pool = list(grow_ids) if grow_ids else list(nearby)
    greedy_ids, greedy_m = greedy_grow(chain, pool, edges_by_id, adj, diag)
    scored = [(score(greedy_m), greedy_ids, greedy_m, "greedy_adjacent_growth")]
    for comp in connected_components(pool, adj):
        pts = np.vstack([edges_by_id[i]["points"] for i in comp])
        m = metrics_pair(chain, pts, diag)
        scored.append((score(m), comp, m, "nearby_connected_component"))
    scored.sort(key=lambda x: x[0], reverse=True)
    _, ids, m, how = scored[0]
    return list(ids), m, how


def select_nearby(chain: np.ndarray, edges: list, adj: dict, diag: float, frozen_id):
    """Geometric on-chain edges + 1-ring BRep adjacency. Frozen id is recorded even if far."""
    chain_len = max(polyline_length(chain), 1e-12)
    geom_tol = max(3.0 * DIST_REL * diag, 0.02 * chain_len)
    box_pad = max(2.0 * DIST_REL * diag, 0.02 * chain_len)
    cmin, cmax = chain.min(0), chain.max(0)
    tree = cKDTree(chain)
    primary = []
    dmin = {}
    for e in edges:
        d = float(tree.query(e["points"])[0].min())
        dmin[e["edge_id"]] = d
        g2d = float((tree.query(e["points"])[0] <= 3.0 * DIST_REL * diag).mean())
        geom_close = d <= geom_tol or g2d >= 0.5
        box_close = bbox_overlap(cmin, cmax, e["bbox_min"], e["bbox_max"], pad=box_pad) and d <= 4.0 * geom_tol
        if geom_close or box_close:
            primary.append(e["edge_id"])
    nearby = set(primary)
    for eid in list(primary):
        nearby |= adj.get(eid, set())
    if frozen_id is not None and int(frozen_id) in dmin:
        nearby.add(int(frozen_id))
    nearby = sorted(i for i in nearby if i in dmin)
    return nearby, dmin, geom_tol, sorted(primary)


def reconstruct_chain(salient_path: Path, chain_id: int, meta: dict) -> np.ndarray:
    xyz, adj, edges = graph_from_dora(np.load(salient_path))
    chains = extract_chains(xyz, adj, edges)
    ch = chains[int(chain_id)]
    pts = np.asarray(ch["points"], dtype=np.float64)
    expect_n = int(meta["vertex_count"])
    expect_l = float(meta["polyline_length"])
    if len(pts) != expect_n:
        raise RuntimeError(f"chain {chain_id} vertex_count {len(pts)} != frozen {expect_n}")
    if abs(polyline_length(pts) - expect_l) > 1e-6:
        raise RuntimeError(f"chain {chain_id} length mismatch vs frozen chains_meta")
    return pts


def label_case(fitted_type, nearby, nearby_types, single_m, set_ids, set_m, same_prim):
    if not nearby:
        return "NO_REASONABLE_GT_GEOMETRY"
    if good(single_m):
        return "SINGLE_GT_EDGE_COMPATIBLE"
    multi_ok = len(set_ids) > 1 and (
        good(set_m)
        or (
            set_m["dora_to_gt_coverage"] >= COVER_WEAK
            and set_m["gt_to_dora_coverage"] >= COVER_WEAK
            and (
                set_m["dora_to_gt_coverage"] - single_m["dora_to_gt_coverage"] >= IMPROVE
                or set_m["gt_to_dora_coverage"] - single_m["gt_to_dora_coverage"] >= IMPROVE
            )
        )
    )
    if multi_ok:
        return "MULTI_GT_SAME_PRIMITIVE" if same_prim else "MULTI_GT_HETEROGENEOUS_PRIMITIVES"
    fitted_family = fitted_type
    gt_families = set()
    for t in nearby_types:
        if t in ("CIRCLE", "ARC"):
            gt_families.add("CIRCLE")
        else:
            gt_families.add(t)
    if fitted_family not in gt_families and not good(set_m, COVER_WEAK):
        return "FITTED_TYPE_FALSE_POSITIVE"
    return "AMBIGUOUS"


def _setup_mpl():
    import matplotlib
    import mpl_toolkits

    sibling = Path(matplotlib.__file__).resolve().parents[1] / "mpl_toolkits"
    if sibling.is_dir() and str(sibling) not in mpl_toolkits.__path__:
        mpl_toolkits.__path__.insert(0, str(sibling))
    matplotlib.use("Agg")
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import matplotlib.pyplot as plt

    return plt, Poly3DCollection


def equal_aspect(ax, pts: np.ndarray, pad_frac=0.08):
    pts = np.asarray(pts, dtype=np.float64)
    if pts.size == 0:
        return
    mn, mx = pts.min(0), pts.max(0)
    c = 0.5 * (mn + mx)
    r = 0.5 * float(np.max(mx - mn))
    r = max(r * (1.0 + pad_frac), 1e-6)
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))


def plot_mesh(ax, mesh, faces, mask=None, max_v=8000, max_f=4000):
    pts = mesh if mask is None else mesh[mask]
    if len(pts) == 0:
        pts = mesh
    stride = max(1, len(pts) // max_v)
    ax.scatter(
        pts[::stride, 0],
        pts[::stride, 1],
        pts[::stride, 2],
        s=2,
        c="#d0d0d0",
        alpha=0.18,
        linewidths=0,
        label="Mesh",
    )


def plot_poly(ax, pts, color, lw, label, zs=None):
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color=color, lw=lw, label=label)


def _local_union(chain, fitted, edges_by_id, ids, dmin, diag):
    chunks = [chain, fitted]
    far = []
    for eid in ids:
        e = edges_by_id.get(eid)
        if e is None:
            continue
        if dmin.get(eid, 0.0) > 0.12 * diag:
            far.append(eid)
            continue
        chunks.append(e["points"])
    return np.vstack(chunks), far


def render_case(case, mesh, faces, chain, fitted, edges_by_id, nearby, frozen_id,
                set_ids, best_single, single_m, set_m, label, dmin, diag, outdir: Path):
    plt, _ = _setup_mpl()
    frozen = edges_by_id.get(frozen_id)
    plot_ids = list(dict.fromkeys(list(set_ids) + [i for i in nearby if dmin.get(i, 1e9) <= 0.12 * diag]))
    if frozen_id is not None and frozen_id in edges_by_id and dmin.get(frozen_id, 1e9) <= 0.12 * diag:
        if frozen_id not in plot_ids:
            plot_ids = [frozen_id] + plot_ids
    nearby_edges = [edges_by_id[i] for i in plot_ids if i in edges_by_id]

    def crop_mask(pts_union):
        lo, hi = pts_union.min(0), pts_union.max(0)
        pad = 0.18 * max(float(np.max(hi - lo)), 1e-6)
        return np.all((mesh >= lo - pad) & (mesh <= hi + pad), axis=1)

    fig = plt.figure(figsize=(10.5, 8.2))
    ax = fig.add_subplot(111, projection="3d")
    plot_mesh(ax, mesh, faces)
    if frozen is not None:
        plot_poly(ax, frozen["points"], "#2ca02c", 2.6, f"current GT edge_{frozen_id} {frozen['viz_type']}")
    ci = 0
    for e in nearby_edges:
        if e["edge_id"] == frozen_id:
            continue
        plot_poly(
            ax, e["points"], OTHER_GT_COLORS[ci % len(OTHER_GT_COLORS)], 1.7,
            f"nearby edge_{e['edge_id']} {e['viz_type']}",
        )
        ci += 1
    plot_poly(ax, fitted, "blue", 3, "Fitted curve")
    plot_poly(ax, chain, "red", 4, "Dora chain")
    equal_aspect(ax, np.vstack([mesh, chain, fitted]))
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.view_init(elev=22, azim=-60)
    ax.legend(loc="upper left", fontsize=7, ncol=2, framealpha=0.9)
    ax.set_title(f"{case['cad_id']}  |  {case['fitted_type']}  |  {case['match_class']}")
    fig.savefig(outdir / "global_overlay.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    union, far_ids = _local_union(chain, fitted, edges_by_id, plot_ids, dmin, diag)
    mask = crop_mask(union)
    fig = plt.figure(figsize=(14.8, 8.2))
    ax = fig.add_subplot(121, projection="3d")
    plot_mesh(ax, mesh, faces, mask=mask)
    palette = ["#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#17becf",
               "#bcbd22", "#7f7f7f", "#98df8a", "#c49c94", "#dbdb8d", "#9edae5",
               "#ff9896", "#c5b0d5"]
    local_edges = [e for e in nearby_edges if e["edge_id"] not in far_ids]
    legend_set = set(set_ids[:16])
    for i, e in enumerate(local_edges):
        name = f"edge_{e['edge_id']} {e['viz_type']}"
        if len(local_edges) > 16 and e["edge_id"] not in legend_set and e["edge_id"] != frozen_id:
            name = None
        plot_poly(ax, e["points"], palette[i % len(palette)], 2.1, name)
    plot_poly(ax, fitted, "blue", 3, "Fitted curve")
    plot_poly(ax, chain, "red", 4, "Dora ordered chain")
    equal_aspect(ax, union, pad_frac=0.14)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.view_init(elev=22, azim=-60)
    ax.legend(loc="upper left", fontsize=7, framealpha=0.92)
    ax.set_title("local overlay")
    tx = fig.add_subplot(122)
    tx.axis("off")
    seq = " -> ".join(f"{eid}:{edges_by_id[eid]['viz_type']}" for eid in set_ids[:12])
    if len(set_ids) > 12:
        seq += f" ... (+{len(set_ids) - 12})"
    rel = single_m["dora_to_gt_mean_rel"]
    rel_s = "None" if rel is None else ("%.4f" % rel)
    lines = [
        f"CAD_ID: {case['cad_id']}",
        f"chain_id: {case['dora_chain_id']}",
        f"fitted_curve_id: {case['fitted_curve_id']}",
        f"Fitted type: {case['fitted_type']}",
        f"Current MATCH_CLASS: {case['match_class']}",
        f"analysis label: {label}",
        "",
        f"best single GT edge: {best_single}",
        f"best single type: {edges_by_id[best_single]['viz_type'] if best_single is not None else None}",
        f"best single distance (rel): {rel_s}",
        f"Dora->single GT coverage: {single_m['dora_to_gt_coverage']:.4f}",
        f"single GT->Dora coverage: {single_m['gt_to_dora_coverage']:.4f}",
        "",
        f"frozen GT candidate: {frozen_id}",
        f"connected GT edge-set: {set_ids}",
        f"set sequence: {seq}",
        f"Dora->GT-set coverage: {set_m['dora_to_gt_coverage']:.4f}",
        f"GT-set->Dora coverage: {set_m['gt_to_dora_coverage']:.4f}",
    ]
    tx.text(0.02, 0.98, "\n".join(lines), va="top", family="monospace", fontsize=9)
    fig.suptitle(f"{case['cad_id']}  chain {case['dora_chain_id']}  {case['fitted_type']}  {case['match_class']}")
    fig.savefig(outdir / "local_overlay.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig = plt.figure(figsize=(10.5, 8.2))
    ax = fig.add_subplot(111, projection="3d")
    plot_mesh(ax, mesh, faces, mask=mask)
    if set_ids:
        union_pts = np.vstack([edges_by_id[i]["points"] for i in set_ids])
        for k, eid in enumerate(set_ids):
            e = edges_by_id[eid]
            plot_poly(ax, e["points"], "#2ca02c", 2.6, "connected GT edge-set" if k == 0 else None)
            ax.scatter(
                [e["start"][0], e["end"][0]], [e["start"][1], e["end"][1]], [e["start"][2], e["end"][2]],
                s=42, c="#1a5c1a", marker="o", depthshade=False,
                label="GT edge boundary" if k == 0 else None,
            )
        focus = np.vstack([chain, fitted, union_pts])
    else:
        focus = np.vstack([chain, fitted])
    plot_poly(ax, fitted, "blue", 3, "Fitted curve")
    plot_poly(ax, chain, "red", 4, "Dora chain")
    equal_aspect(ax, focus, pad_frac=0.14)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.view_init(elev=22, azim=-60)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.92)
    ax.set_title(f"{case['cad_id']}  chain {case['dora_chain_id']}\nconnected GT set {set_ids}  |  {label}")
    fig.savefig(outdir / "gt_edge_set_overlay.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def compact_metrics(m: dict) -> dict:
    return {k: _f(v) if v is not None else None for k, v in m.items()}


def main():
    src_cases = json.loads(SOURCE.read_text())["cases"]
    ellipse = [c for c in src_cases if c["fitted_type"] == "ELLIPSE"][:5]
    bspline = [c for c in src_cases if c["fitted_type"] == "BSPLINE"][:5]
    if len(ellipse) != 5 or len(bspline) != 5:
        raise RuntimeError(f"expected 5+5 visual cases, got {len(ellipse)} ELLIPSE / {len(bspline)} BSPLINE")
    cohort = {}
    for line in COHORT.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            cohort[row["cad_id"]] = row

    if OUT.exists():
        for p in OUT.iterdir():
            if p.name in {"visual_cases", "CASE_MANIFEST.json", "GRANULARITY_CASES.jsonl",
                          "GRANULARITY_SUMMARY.md", "FINAL_GATE.json"}:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "visual_cases" / "ellipse").mkdir(parents=True)
    (OUT / "visual_cases" / "bspline").mkdir(parents=True)

    records = []
    manifest_cases = []
    for family, pool in (("ellipse", ellipse), ("bspline", bspline)):
        for case in pool:
            cad = case["cad_id"]
            chain_id = int(case["dora_chain_id"])
            fitted_id = int(case["fitted_curve_id"])
            frozen_gt = case.get("gt_brep_edge_id")
            frozen_gt = int(frozen_gt) if frozen_gt is not None else None
            assets = cohort[cad]["assets"]
            cdir = V1_CAD / cad
            fits = json.loads((cdir / "dora/fitted_curves.json").read_text())["curves"]
            fit = fits[fitted_id]
            if int(fit["chain_id"]) != chain_id:
                raise RuntimeError(f"{cad}: fitted_curve_id {fitted_id} chain {fit['chain_id']} != {chain_id}")
            meta = json.loads((cdir / "dora/chains_meta.json").read_text())
            chain_meta = meta["chains"][chain_id]
            chain_raw = reconstruct_chain(Path(assets["dora_salient_edges"]["path"]), chain_id, chain_meta)
            chain_dense = densify_polyline(chain_raw, N_SAMPLE, closed=bool(chain_meta.get("closed_loop")))
            fitted_pts = sample_fitted(fit, N_SAMPLE)
            mesh, faces = load_obj(Path(assets["model_obj"]["path"]))
            diag = float(np.linalg.norm(mesh.max(0) - mesh.min(0)))
            edges, adj, _extracted = extract_gt_edges(Path(assets["model_step"]["path"]), N_SAMPLE)
            edges_by_id = {e["edge_id"]: e for e in edges}
            nearby, dmin, radius, primary = select_nearby(chain_dense, edges, adj, diag, frozen_gt)

            single_rank = []
            for eid in nearby:
                m = metrics_pair(chain_dense, edges_by_id[eid]["points"], diag)
                single_rank.append((score(m), eid, m))
            single_rank.sort(reverse=True)
            best_single = single_rank[0][1] if single_rank else None
            single_m = single_rank[0][2] if single_rank else {
                "dora_to_gt_mean": None, "gt_to_dora_mean": None,
                "dora_to_gt_mean_rel": None, "gt_to_dora_mean_rel": None,
                "dora_to_gt_coverage": 0.0, "gt_to_dora_coverage": 0.0,
            }
            set_ids, set_m, how = best_connected_set(chain_dense, primary, nearby, edges_by_id, adj, diag)
            same_prim = set_same_primitive(edges_by_id, set_ids, diag) if set_ids else False
            nearby_types = [edges_by_id[i]["viz_type"] for i in nearby]
            set_types = [edges_by_id[i]["viz_type"] for i in set_ids]
            label = label_case(case["fitted_type"], nearby, nearby_types, single_m, set_ids, set_m, same_prim)

            folder = OUT / "visual_cases" / family / f"{cad}__chain_{chain_id}__curve_{fitted_id}"
            folder.mkdir(parents=True, exist_ok=True)
            render_case(
                case, mesh, faces, chain_raw, fitted_pts, edges_by_id, nearby,
                frozen_gt, set_ids, best_single, single_m, set_m, label, dmin, diag, folder,
            )

            metrics = {
                "cad_id": cad,
                "dora_chain_id": chain_id,
                "fitted_curve_id": fitted_id,
                "fitted_type": case["fitted_type"],
                "formal_match_class_unchanged": case["match_class"],
                "frozen_gt_brep_edge_id": frozen_gt,
                "frozen_gt_candidate_type": case.get("gt_candidate_type"),
                "analysis_neighborhood_radius": _f(radius),
                "primary_on_chain_edge_ids": [int(x) for x in primary],
                "object_bbox_diagonal": _f(diag),
                "nearby_gt_edges": [
                    {
                        "edge_id": int(eid),
                        "viz_type": edges_by_id[eid]["viz_type"],
                        "occ_type": edges_by_id[eid]["occ_type"],
                        "length": _f(edges_by_id[eid]["length"]),
                        "min_distance_to_chain": _f(dmin[eid]),
                        "vertex_ids": edges_by_id[eid]["vertex_ids"],
                        "adjacent_in_nearby": sorted(int(x) for x in adj.get(eid, set()) if x in set(nearby)),
                    }
                    for eid in nearby
                ],
                "A_dora_vs_best_single_gt_edge": {
                    "best_single_gt_edge_id": best_single,
                    "best_single_gt_type": None if best_single is None else edges_by_id[best_single]["viz_type"],
                    **compact_metrics(single_m),
                },
                "B_dora_vs_best_connected_gt_edge_set": {
                    "connected_gt_edge_ids": [int(x) for x in set_ids],
                    "connected_gt_types": set_types,
                    "selection": how,
                    "same_analytic_primitive": bool(same_prim),
                    "primitive_sequence": " -> ".join(set_types),
                    **compact_metrics(set_m),
                },
                "granularity_label": label,
                "formal_match_class_modified": False,
            }
            _dump(folder / "metrics.json", metrics)

            rec = {
                "cad_id": cad,
                "dora_chain_id": chain_id,
                "fitted_curve_id": fitted_id,
                "fitted_type": case["fitted_type"],
                "match_class": case["match_class"],
                "granularity_label": label,
                "best_single_gt_edge_id": best_single,
                "connected_gt_edge_ids": [int(x) for x in set_ids],
                "primitive_sequence": " -> ".join(set_types),
                "single_dora_to_gt_coverage": _f(single_m["dora_to_gt_coverage"]),
                "single_gt_to_dora_coverage": _f(single_m["gt_to_dora_coverage"]),
                "single_dora_to_gt_mean_rel": _f(single_m["dora_to_gt_mean_rel"]) if single_m["dora_to_gt_mean_rel"] is not None else None,
                "set_dora_to_gt_coverage": _f(set_m["dora_to_gt_coverage"]),
                "set_gt_to_dora_coverage": _f(set_m["gt_to_dora_coverage"]),
                "set_dora_to_gt_mean_rel": _f(set_m["dora_to_gt_mean_rel"]) if set_m["dora_to_gt_mean_rel"] is not None else None,
                "visual_folder": str(folder.relative_to(OUT)),
            }
            records.append(rec)
            manifest_cases.append(
                {
                    "cad_id": cad,
                    "dora_chain_id": chain_id,
                    "fitted_curve_id": fitted_id,
                    "fitted_type": case["fitted_type"],
                    "match_class": case["match_class"],
                    "folder": str(folder.relative_to(OUT)),
                    "granularity_label": label,
                    "source_visual_case": case.get("folder"),
                }
            )
            print(f"[ok] {cad} chain={chain_id} {case['fitted_type']} -> {label}", flush=True)

    counts = {k: sum(r["granularity_label"] == k for r in records) for k in LABELS}
    (OUT / "GRANULARITY_CASES.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in records))
    _dump(
        OUT / "CASE_MANIFEST.json",
        {
            "gate": "DORA_BREP_GRANULARITY_CANARY_V1",
            "selection": "5 ELLIPSE + 5 BSPLINE from rare-type VISUAL_CASE_MANIFEST.json; CAD_ID / chain_id / fitted_curve_id unchanged",
            "n_cases": len(records),
            "formal_match_class_modified": False,
            "correspondence_threshold_modified": False,
            "dora_rerun": False,
            "chain_extraction_rerun": False,
            "curve_fitting_rerun": False,
            "c2_training": False,
            "counts": counts,
            "cases": manifest_cases,
        },
    )
    lines = [
        "# Dora / BRep granularity canary V1",
        "",
        "Question: is rare fitted ELLIPSE / BSPLINE UNMATCHED mainly from Dora-chain granularity != single GT BRep edge granularity?",
        "",
        f"- TOTAL_CASES: {len(records)}",
    ]
    for k in LABELS:
        lines.append(f"- {k}: {counts[k]}")
    lines += [
        "",
        "Formal MATCH_CLASS, correspondence, thresholds, Dora, chain extraction, fitting, and C2 were not modified.",
        "",
        "| CAD_ID | type | MATCH_CLASS | label | single d2g/g2d | set d2g/g2d | GT set |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in records:
        lines.append(
            f"| {r['cad_id']} | {r['fitted_type']} | {r['match_class']} | {r['granularity_label']} | "
            f"{r['single_dora_to_gt_coverage']:.3f}/{r['single_gt_to_dora_coverage']:.3f} | "
            f"{r['set_dora_to_gt_coverage']:.3f}/{r['set_gt_to_dora_coverage']:.3f} | "
            f"{r['primitive_sequence']} |"
        )
    (OUT / "GRANULARITY_SUMMARY.md").write_text("\n".join(lines) + "\n")

    print()
    print("CURRENT_GATE=")
    print("DORA_BREP_GRANULARITY_CANARY_V1_COMPLETE")
    print()
    print(f"TOTAL_CASES={len(records)}")
    print()
    for k in LABELS:
        print(f"{k}={counts[k]}")


if __name__ == "__main__":
    main()
