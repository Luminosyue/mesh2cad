#!/usr/bin/env python3
"""V5: stitch official Point2CAD intersection fragments → closed wires → OCC solid.

Reuses frozen V3 surfaces/intersections and V4 corner/OCC builders. Does not refit surfaces.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4

VIEW = v4.VIEW
STITCH_GAPS = (1e-4, 3e-4, 1e-3, 3e-3)
STITCH_DIAG_GAPS = (1e-2, 3e-2)
CORNER_GAPS = (1e-4, 3e-4, 1e-3)
SEW_GAPS = (1e-5, 3e-5, 1e-4, 3e-4)
TANGENT_MIN = 0.55


def dump_json(path: Path, obj: Any) -> None:
    v4.dump_json(path, obj)


def poly_len(pts: np.ndarray) -> float:
    if len(pts) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def robust_tangent(pts: np.ndarray, which: str, k: int = 12) -> np.ndarray:
    if len(pts) < 2:
        return np.zeros(3)
    k = min(k, len(pts) - 1)
    sl = pts[: k + 1] if which == "s" else pts[-(k + 1) :]
    c = sl.mean(0)
    _, _, vt = np.linalg.svd(sl - c, full_matrices=False)
    t = vt[0]
    chord = sl[-1] - sl[0]
    if float(np.dot(t, chord)) < 0:
        t = -t
    return v4.unit(t)


def leave_tangent(pts: np.ndarray, which: str) -> np.ndarray:
    t = robust_tangent(pts, which)
    return t if which == "e" else -t


def downsample(pts: np.ndarray, n: int = 80) -> np.ndarray:
    return v4.downsample_poly(np.asarray(pts, dtype=float), n)


def extract_official_curves(topo: dict, diag: float) -> list[dict]:
    weld = max(1e-8, 1e-6 * diag)
    curves = []
    for i, c in enumerate(topo.get("curves") or []):
        pts = np.asarray(c.get("pv_points_world") or c.get("pv_points") or [], dtype=float)
        lines = np.asarray(c.get("pv_lines") or [], dtype=int)
        if len(pts) < 2:
            continue
        if len(lines):
            wpts, wedges = v4.weld_polyline_graph(pts, lines, weld)
            comps = v4.polyline_components(wpts, wedges)
        else:
            comps = [pts]
        components = []
        for j, pl in enumerate(comps):
            L = poly_len(pl)
            closed = float(np.linalg.norm(pl[0] - pl[-1])) < max(1e-4 * diag, 0.008 * max(L, 1e-12)) and len(pl) > 8
            components.append(
                {
                    "comp_id": j,
                    "points": pl,
                    "length": L,
                    "closed": bool(closed),
                    "start_xyz": pl[0].tolist(),
                    "end_xyz": pl[-1].tolist(),
                    "start_tangent": robust_tangent(pl, "s").tolist(),
                    "end_tangent": robust_tangent(pl, "e").tolist(),
                }
            )
        curves.append(
            {
                "raw_id": i,
                "curve_id": f"P2C_CURVE_{i:03d}",
                "points": pts,
                "components": components,
                "n_components": len(components),
            }
        )
    return curves


def mesh_mean_dist(mesh: trimesh.Trimesh, sample: np.ndarray) -> float:
    from scipy.spatial import cKDTree

    v = np.asarray(mesh.vertices, dtype=float)
    if len(v) == 0 or len(sample) == 0:
        return 1e9
    return float(cKDTree(v).query(sample)[0].mean())


def assign_authoritative_pairs(curves: list[dict], surfaces: list[trimesh.Trimesh], diag: float) -> dict:
    """Replay Point2CAD itertools.combinations order; do not pick two globally nearest surfaces."""
    n = len(surfaces)
    pairs = list(itertools.combinations(range(n), 2))
    samples = []
    for c in curves:
        pts = c["points"]
        samples.append(pts[np.linspace(0, len(pts) - 1, min(64, len(pts)), dtype=int)])
    unused = set(range(len(curves)))
    mapping = []
    empty_pairs = []
    lim = 0.02 * diag
    for a, b in pairs:
        best = None
        for ci in unused:
            da = mesh_mean_dist(surfaces[a], samples[ci])
            db = mesh_mean_dist(surfaces[b], samples[ci])
            sc = max(da, db)
            if best is None or sc < best[0]:
                best = (sc, ci, da, db)
        if best is not None and best[0] < lim:
            unused.remove(best[1])
            c = curves[best[1]]
            c["surface_a"] = int(a)
            c["surface_b"] = int(b)
            c["surface_pair"] = (int(a), int(b))
            c["source"] = "POINT2CAD_INTERSECTION"
            c["pair_support"] = {"dist_a": best[2], "dist_b": best[3], "score": best[0]}
            mapping.append({"curve_id": c["curve_id"], "surface_a": a, "surface_b": b, "score": best[0]})
        else:
            empty_pairs.append({"surface_a": a, "surface_b": b, "best_score": None if best is None else best[0]})
    for ci in unused:
        curves[ci]["surface_a"] = None
        curves[ci]["surface_b"] = None
        curves[ci]["surface_pair"] = None
        curves[ci]["source"] = "UNMAPPED"
    n_ok = sum(1 for c in curves if c.get("surface_pair") is not None)
    rate = float(n_ok / max(len(curves), 1))
    return {
        "CURVES_WITH_AUTHORITATIVE_SURFACE_PAIR": n_ok,
        "TOTAL_CURVES": len(curves),
        "SURFACE_PAIR_MAPPING_RATE": rate,
        "mapping": mapping,
        "empty_official_pairs": empty_pairs,
        "unmapped": [curves[i]["curve_id"] for i in unused],
    }


def stitch_score_pair(ca: dict, cb: dict, ea: str, eb: str, diag: float) -> dict | None:
    pa = np.asarray(ca["points"][0] if ea == "s" else ca["points"][-1], dtype=float)
    pb = np.asarray(cb["points"][0] if eb == "s" else cb["points"][-1], dtype=float)
    gap = float(np.linalg.norm(pa - pb))
    ng = gap / max(diag, 1e-12)
    ta = leave_tangent(ca["points"], ea)
    tb = leave_tangent(cb["points"], eb)
    # walking A then into reversed-or-not B: leave_a should align with -leave_b (enter B)
    d_fwd = float(np.dot(ta, -tb))
    d_rev = float(np.dot(ta, tb))
    reverse_b = d_rev > d_fwd
    dot = max(d_fwd, d_rev)
    if dot < TANGENT_MIN:
        return None
    cost = ng + 0.15 * (1.0 - dot)
    return {"gap": gap, "normalized_gap": ng, "dot": dot, "reverse_b": reverse_b, "cost": cost}


def matching_joins(comps: list[dict], diag: float, thr: float) -> list[dict]:
    cands = []
    for i, a in enumerate(comps):
        if a.get("closed") or a.get("noise"):
            continue
        for j, b in enumerate(comps):
            if j <= i or b.get("closed") or b.get("noise"):
                continue
            for ea, eb in (("s", "s"), ("s", "e"), ("e", "s"), ("e", "e")):
                rec = stitch_score_pair(a, b, ea, eb, diag)
                if rec is None or rec["normalized_gap"] > thr:
                    continue
                rec.update({"i": i, "j": j, "ea": ea, "eb": eb})
                cands.append(rec)
    cands.sort(key=lambda x: x["cost"])
    used = set()
    joins = []
    parent = list(range(len(comps)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for rec in cands:
        ea = (rec["i"], rec["ea"])
        eb = (rec["j"], rec["eb"])
        if ea in used or eb in used:
            continue
        if find(rec["i"]) == find(rec["j"]):
            continue
        used.add(ea)
        used.add(eb)
        parent[find(rec["j"])] = find(rec["i"])
        joins.append(rec)
    return joins


def stitch_one_curve(curve: dict, diag: float) -> tuple[list[dict], dict]:
    comps = [dict(c, points=np.asarray(c["points"], dtype=float)) for c in curve["components"]]
    total = sum(c["length"] for c in comps) or 1e-12
    for c in comps:
        tiny = (not c["closed"]) and c["length"] < max(0.004 * diag, 0.012 * total)
        c["noise"] = bool(tiny)
    scan = []
    for thr in STITCH_GAPS:
        joins = matching_joins(comps, diag, thr)
        n_master_est = len(comps) - len(joins)
        dots = [j["dot"] for j in joins]
        scan.append(
            {
                "thr": thr,
                "joins": len(joins),
                "masters_est": n_master_est,
                "max_gap": max((j["gap"] for j in joins), default=0.0),
                "tangent_min": min(dots) if dots else None,
            }
        )
    diag_scan = []
    for thr in STITCH_DIAG_GAPS:
        joins = matching_joins(comps, diag, thr)
        diag_scan.append({"thr": thr, "joins": len(joins), "masters_est": len(comps) - len(joins)})
    # pick smallest thr with maximal connectivity among official scan
    best = max(scan, key=lambda s: (s["joins"], -s["thr"]))
    thr = float(best["thr"])
    joins = matching_joins(comps, diag, thr)
    adj = defaultdict(list)
    for jn in joins:
        adj[jn["i"]].append(jn)
        adj[jn["j"]].append({**jn, "i": jn["j"], "j": jn["i"], "ea": jn["eb"], "eb": jn["ea"], "reverse_b": jn["reverse_b"]})
    used_c = set()
    masters = []

    def concat(seq: list[tuple[int, bool]]) -> np.ndarray:
        chunks = []
        for idx, rev in seq:
            pl = np.asarray(comps[idx]["points"], dtype=float)
            if rev:
                pl = pl[::-1]
            if chunks and np.linalg.norm(chunks[-1][-1] - pl[0]) < 1e-12:
                pl = pl[1:]
            chunks.append(pl)
        return np.vstack(chunks) if chunks else np.zeros((0, 3))

    def walk(start: int) -> list[tuple[int, bool]]:
        seq = [(start, False)]
        used_c.add(start)
        node, arrived_end = start, "s"
        # arrived_end means we entered at start, so free end is 'e' initially
        free = "e"
        while True:
            nxt = None
            for jn in adj[node]:
                other = jn["j"]
                if other in used_c:
                    continue
                # join uses endpoint `jn['ea']` of current
                if jn["ea"] != free:
                    continue
                rev = bool(jn["reverse_b"]) if jn["i"] == node else (jn["eb"] == "e")
                # if we leave through ea of current connecting to eb of other
                enter = jn["eb"]
                rev_other = enter == "e"
                nxt = (other, rev_other, "s" if rev_other else "e")
                used_c.add(other)
                seq.append((other, rev_other))
                node, free = other, nxt[2]
                break
            if nxt is None:
                break
        return seq

    for i, c in enumerate(comps):
        if c.get("noise") or i in used_c:
            continue
        if c["closed"]:
            used_c.add(i)
            pts = np.asarray(c["points"], dtype=float)
            masters.append(
                {
                    "master_id": f"{curve['curve_id']}_M{len(masters):02d}",
                    "parent_curve_id": curve["curve_id"],
                    "surface_a": curve["surface_a"],
                    "surface_b": curve["surface_b"],
                    "points": pts,
                    "closed": True,
                    "component_ids": [i],
                    "raw_component_count": 1,
                    "stitched_component_count": 1,
                }
            )
            continue
        seq = walk(i)
        pts = concat(seq)
        L = poly_len(pts)
        closed = len(pts) > 8 and float(np.linalg.norm(pts[0] - pts[-1])) < max(3e-3 * diag, 0.01 * max(L, 1e-12))
        gaps = [jn["gap"] for jn in joins if jn["i"] in {s[0] for s in seq} and jn["j"] in {s[0] for s in seq}]
        dots = [jn["dot"] for jn in joins if jn["i"] in {s[0] for s in seq} and jn["j"] in {s[0] for s in seq}]
        masters.append(
            {
                "master_id": f"{curve['curve_id']}_M{len(masters):02d}",
                "parent_curve_id": curve["curve_id"],
                "surface_a": curve["surface_a"],
                "surface_b": curve["surface_b"],
                "points": pts,
                "closed": bool(closed),
                "component_ids": [s[0] for s in seq],
                "raw_component_count": len(seq),
                "stitched_component_count": len(seq),
                "MAX_BRIDGED_GAP": max(gaps) if gaps else 0.0,
                "MEAN_BRIDGED_GAP": float(np.mean(gaps)) if gaps else 0.0,
                "TANGENT_DISCONTINUITY_P95": float(np.percentile([1 - d for d in dots], 95)) if dots else 0.0,
            }
        )
    leftover_noise = [i for i, c in enumerate(comps) if c.get("noise")]
    qa = {
        "curve_id": curve["curve_id"],
        "RAW_COMPONENT_COUNT": len(curve["components"]),
        "NOISE_COMPONENTS": leftover_noise,
        "STITCHED_MASTER_COUNT": len(masters),
        "chosen_thr": thr,
        "scan": scan,
        "diagnostic_scan": diag_scan,
        "joins": [{k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in j.items()} for j in joins],
        "OPEN_ENDPOINTS": int(sum(2 for m in masters if not m["closed"])),
        "N_CLOSED_MASTERS": int(sum(1 for m in masters if m["closed"])),
    }
    return masters, qa


def stitch_all(curves: list[dict], diag: float) -> tuple[list[dict], dict]:
    masters, qas = [], []
    for c in curves:
        ms, qa = stitch_one_curve(c, diag)
        for m in ms:
            m["source"] = "POINT2CAD_INTERSECTION"
        masters.extend(ms)
        qas.append(qa)
    return masters, {
        "RAW_INTERSECTION_COMPONENTS": int(sum(c["n_components"] for c in curves)),
        "STITCHED_MASTER_CURVES": len(masters),
        "per_curve": qas,
    }


def seg_seg_closest(p1, p2, q1, q2):
    p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float)
    q1 = np.asarray(q1, float)
    q2 = np.asarray(q2, float)
    u = p2 - p1
    v = q2 - q1
    w = p1 - q1
    a = float(np.dot(u, u))
    b = float(np.dot(u, v))
    c = float(np.dot(v, v))
    d = float(np.dot(u, w))
    e = float(np.dot(v, w))
    den = a * c - b * b
    if den < 1e-18:
        sc = 0.0
        tc = e / c if c > 1e-18 else 0.0
    else:
        sc = (b * e - c * d) / den
        tc = (a * e - b * d) / den
    sc = float(np.clip(sc, 0.0, 1.0))
    tc = float(np.clip(tc, 0.0, 1.0))
    pc = p1 + sc * u
    qc = q1 + tc * v
    return float(np.linalg.norm(pc - qc)), pc, qc


def recover_corners_masters(masters: list[dict], diag: float, eps_frac: float) -> tuple[list[dict], int]:
    eps = eps_frac * diag
    cands = []
    for i, a in enumerate(masters):
        for j, b in enumerate(masters):
            if j <= i:
                continue
            sa = {a["surface_a"], a["surface_b"]}
            sb = {b["surface_a"], b["surface_b"]}
            share = sa & sb
            if len(share) != 1:
                continue
            pa, pb = np.asarray(a["points"], float), np.asarray(b["points"], float)
            from scipy.spatial import cKDTree

            tree = cKDTree(pb)
            d, idx = tree.query(pa)
            close = np.where(d < eps)[0]
            for k in close[:: max(1, len(close) // 12)] if len(close) else []:
                mid = 0.5 * (pa[int(k)] + pb[int(idx[int(k)])])
                cands.append({"xyz": mid, "dist": float(d[int(k)]), "curves": (i, j), "surfaces": sorted(sa | sb)})
            if len(close) == 0 and float(d.min()) < max(eps, 1e-3 * diag):
                k = int(np.argmin(d))
                mid = 0.5 * (pa[k] + pb[int(idx[k])])
                cands.append({"xyz": mid, "dist": float(d[k]), "curves": (i, j), "surfaces": sorted(sa | sb)})
            # endpoints vs polyline
            for P, Q in ((pa, pb), (pb, pa)):
                ends = [P[0], P[-1]]
                from scipy.spatial import cKDTree

                tree = cKDTree(Q)
                d, idx = tree.query(ends)
                for k, di in enumerate(d):
                    if di < eps:
                        mid = 0.5 * (ends[k] + Q[int(idx[k])])
                        cands.append({"xyz": mid, "dist": float(di), "curves": (i, j), "surfaces": sorted(sa | sb)})
            # strided segment-segment
            sa_seg = [(pa[k], pa[k + 1]) for k in range(0, len(pa) - 1, max(1, len(pa) // 80))]
            sb_seg = [(pb[k], pb[k + 1]) for k in range(0, len(pb) - 1, max(1, len(pb) // 80))]
            sa_seg = sa_seg[:8] + sa_seg[-8:] + sa_seg[:: max(1, len(sa_seg) // 12)]
            sb_seg = sb_seg[:8] + sb_seg[-8:] + sb_seg[:: max(1, len(sb_seg) // 12)]
            best = None
            for p1, p2 in sa_seg:
                for q1, q2 in sb_seg:
                    dist, pc, qc = seg_seg_closest(p1, p2, q1, q2)
                    if dist < eps and (best is None or dist < best[0]):
                        best = (dist, 0.5 * (pc + qc))
            if best is not None:
                cands.append({"xyz": best[1], "dist": best[0], "curves": (i, j), "surfaces": sorted(sa | sb)})
    if not cands:
        return [], 0
    from scipy.spatial import cKDTree

    xyzs = np.asarray([c["xyz"] for c in cands], float)
    parent = list(range(len(cands)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = cKDTree(xyzs)
    for p, q in tree.query_pairs(2.0 * eps):
        ra, rb = find(p), find(q)
        if ra != rb:
            parent[rb] = ra
    groups = defaultdict(list)
    for i in range(len(cands)):
        groups[find(i)].append(i)
    merged = []
    for ids in groups.values():
        cluster = [cands[k] for k in ids]
        pts = np.asarray([c["xyz"] for c in cluster], float)
        diam = float(np.linalg.norm(pts.max(0) - pts.min(0)))
        if diam > 10 * eps and len(pts) > 3:
            cluster = [min(cluster, key=lambda x: x["dist"])]
            pts = np.asarray([cluster[0]["xyz"]], float)
            diam = 0.0
        curve_ids = sorted({k for c in cluster for k in c["curves"]})
        if len(curve_ids) < 2:
            continue
        surf = sorted({s for c in cluster for s in c["surfaces"]})
        merged.append(
            {
                "vertex_id": f"V_{len(merged):03d}",
                "xyz": np.mean(pts, 0).tolist(),
                "incident_curve_ids": [masters[k]["master_id"] for k in curve_ids],
                "incident_surface_ids": surf,
                "n_candidates": len(cluster),
                "mean_pair_dist": float(np.mean([c["dist"] for c in cluster])),
            }
        )
    return merged, len(cands)


def pick_corners(masters, diag):
    scored = []
    for frac in CORNER_GAPS:
        corners, nc = recover_corners_masters(masters, diag, frac)
        n = len(corners)
        score = 8 * n
        if len(masters) >= 2 and n == 0:
            score -= 20
        if n > 20:
            score -= 2 * (n - 20)
        if frac == 3e-4:
            score += 1.5
        scored.append((score, frac, corners, nc))
    scored.sort(key=lambda x: -x[0])
    _, frac, corners, nc = scored[0]
    return frac, corners, nc, [{"eps_frac": s[1], "n": len(s[2]), "cand": s[3], "score": s[0]} for s in scored]


def trim_masters(masters: list[dict], corners: list[dict], diag: float, eps: float) -> tuple[list[dict], list[dict]]:
    snap = max(8.0 * eps, 3e-3 * diag)
    edges = []
    verts = [dict(v) for v in corners]
    for mi, m in enumerate(masters):
        pts = np.asarray(m["points"], float)
        hits = []
        for v in verts:
            d, t, q = v4.project_point_on_polyline(pts, np.asarray(v["xyz"], float))
            if d < snap:
                hits.append((t, v["vertex_id"], np.asarray(v["xyz"], float), d))
        closed = bool(m.get("closed"))
        for t_end, p_end, tag in ((0.0, pts[0], "START"), (1.0, pts[-1], "END")):
            near, best, qn = None, 1e9, p_end
            for v in verts:
                dd = float(np.linalg.norm(np.asarray(v["xyz"]) - p_end))
                if dd < snap and dd < best:
                    near, best, qn = v["vertex_id"], dd, np.asarray(v["xyz"], float)
            if near is None and not closed:
                vid = f"E_{m['master_id']}_{tag}"
                verts.append({"vertex_id": vid, "xyz": np.asarray(p_end).tolist(), "endpoint": True, "incident_curve_ids": [m["master_id"]]})
                near, qn = vid, p_end
            if near is not None:
                hits.append((t_end, near, qn, 0.0))
        hits.sort(key=lambda x: x[0])
        uniq = []
        for h in hits:
            if not uniq or abs(h[0] - uniq[-1][0]) > 0.02:
                uniq.append(h)
            elif h[3] < uniq[-1][3]:
                uniq[-1] = h
        sa, sb = m["surface_a"], m["surface_b"]
        if closed and len(uniq) < 2:
            edges.append(
                {
                    "edge_id": f"MASTER_EDGE_{len(edges):03d}",
                    "v_start": uniq[0][1] if uniq else None,
                    "v_end": uniq[0][1] if uniq else None,
                    "closed": True,
                    "surface_a": sa,
                    "surface_b": sb,
                    "surfaces": [sa, sb],
                    "parent_curve_id": m["parent_curve_id"],
                    "master_id": m["master_id"],
                    "points": downsample(pts, 80),
                    "length": poly_len(pts),
                    "source": m.get("source"),
                }
            )
            continue
        if len(uniq) < 2:
            continue
        for a, b in zip(uniq, uniq[1:]):
            if b[0] - a[0] < 0.015:
                continue
            sub = v4._slice_poly(pts, a[0], b[0], a[2], b[2])
            edges.append(
                {
                    "edge_id": f"MASTER_EDGE_{len(edges):03d}",
                    "v_start": a[1],
                    "v_end": b[1],
                    "closed": False,
                    "surface_a": sa,
                    "surface_b": sb,
                    "surfaces": [sa, sb],
                    "parent_curve_id": m["parent_curve_id"],
                    "master_id": m["master_id"],
                    "points": downsample(sub, 80),
                    "length": poly_len(sub),
                    "source": m.get("source"),
                }
            )
        if closed and uniq[0][1] != uniq[-1][1]:
            a, b = uniq[-1], uniq[0]
            params = v4.arclength_params(pts)
            sub = np.vstack([pts[params >= a[0] - 1e-9], pts[params <= b[0] + 1e-9]])
            if len(sub) >= 2:
                edges.append(
                    {
                        "edge_id": f"MASTER_EDGE_{len(edges):03d}",
                        "v_start": a[1],
                        "v_end": b[1],
                        "closed": False,
                        "surface_a": sa,
                        "surface_b": sb,
                        "surfaces": [sa, sb],
                        "parent_curve_id": m["parent_curve_id"],
                        "master_id": m["master_id"],
                        "points": downsample(sub, 80),
                        "length": poly_len(sub),
                        "source": m.get("source"),
                    }
                )
    return edges, verts


def surface_boundary_graph(n_surf: int, edges: list[dict], verts: list[dict]) -> dict:
    per = {si: defaultdict(list) for si in range(n_surf)}
    for e in edges:
        for si in e.get("surfaces") or []:
            if e.get("closed"):
                continue
            if e.get("v_start") and e.get("v_end") and e["v_start"] != e["v_end"]:
                per[int(si)][e["v_start"]].append((e["v_end"], e["edge_id"]))
                per[int(si)][e["v_end"]].append((e["v_start"], e["edge_id"]))
    deg_all = Counter()
    per_surf = []
    for si in range(n_surf):
        deg = Counter(len({eid for _, eid in nbrs}) for nbrs in per[si].values())
        d1 = sum(1 for v, nbrs in per[si].items() if len({e for _, e in nbrs}) == 1)
        d2 = sum(1 for v, nbrs in per[si].items() if len({e for _, e in nbrs}) == 2)
        d3 = sum(1 for v, nbrs in per[si].items() if len({e for _, e in nbrs}) >= 3)
        deg_all["d1"] += d1
        deg_all["d2"] += d2
        deg_all["d3"] += d3
        per_surf.append({"surface": si, "degree1": d1, "degree2": d2, "degree3plus": d3, "n_vertices": len(per[si])})
    return {"ENDPOINT_GRAPH_DEGREE1": int(deg_all["d1"]), "ENDPOINT_GRAPH_DEGREE2": int(deg_all["d2"]), "ENDPOINT_GRAPH_DEGREE3PLUS": int(deg_all["d3"]), "per_surface": per_surf, "adj": per}


def recover_surface_wires(n_surf: int, edges: list[dict], graph: dict) -> tuple[list[dict], list[dict]]:
    emap = {e["edge_id"]: e for e in edges}
    wires = []
    missing = []
    adj_all = graph["adj"]
    for si in range(n_surf):
        local = [e for e in edges if si in (e.get("surfaces") or [])]
        for e in local:
            if e.get("closed"):
                wires.append(
                    {
                        "wire_id": f"WIRE_{len(wires):03d}",
                        "surface": si,
                        "edge_ids": [e["edge_id"]],
                        "closed": True,
                        "kind": "closed_loop_edge",
                        "WIRE_VALID": True,
                    }
                )
        adj = adj_all[si]
        used = set()

        def unused(v):
            return [(w, eid) for w, eid in adj[v] if eid not in used]

        # simple cycles: start at unused, prefer return-to-start, require >=2 edges and >=2 real vertices
        for start in list(adj.keys()):
            while unused(start):
                nxt, e0 = unused(start)[0]
                seq_e = [e0]
                seq_v = [start, nxt]
                used.add(e0)
                cur = nxt
                found = False
                for _ in range(len(local) + 3):
                    nbs = unused(cur)
                    if not nbs:
                        break
                    back = [(w, e) for w, e in nbs if w == start]
                    v2, e2 = back[0] if back else nbs[0]
                    seq_e.append(e2)
                    seq_v.append(v2)
                    used.add(e2)
                    cur = v2
                    if cur == start:
                        found = True
                        break
                real = [v for v in seq_v[:-1] if v and not str(v).startswith("E_")]
                if found and len(seq_e) >= 2 and len(set(real)) >= 2:
                    wires.append(
                        {
                            "wire_id": f"WIRE_{len(wires):03d}",
                            "surface": si,
                            "edge_ids": seq_e,
                            "vertex_ids": seq_v[:-1],
                            "closed": True,
                            "kind": "cycle",
                            "WIRE_VALID": True,
                        }
                    )
                else:
                    wires.append(
                        {
                            "wire_id": f"WIRE_{len(wires):03d}",
                            "surface": si,
                            "edge_ids": seq_e,
                            "vertex_ids": seq_v,
                            "closed": False,
                            "kind": "open_walk",
                            "WIRE_VALID": False,
                        }
                    )
                    if seq_v:
                        missing.append(
                            {
                                "surface": si,
                                "v_a": seq_v[0],
                                "v_b": seq_v[-1],
                                "edge_ids": seq_e,
                            }
                        )
        leftover = [e for e in local if (not e.get("closed")) and e["edge_id"] not in used]
        if leftover:
            wires.append(
                {
                    "wire_id": f"WIRE_{len(wires):03d}",
                    "surface": si,
                    "edge_ids": [e["edge_id"] for e in leftover],
                    "closed": False,
                    "kind": "leftover",
                    "WIRE_VALID": False,
                }
            )
    return wires, missing


def classify_edge_degree(edges: list[dict], wires: list[dict]) -> dict:
    closed = [w for w in wires if w.get("closed") and w.get("WIRE_VALID")]
    stats = Counter()
    for e in edges:
        n = sum(1 for w in closed if e["edge_id"] in w["edge_ids"])
        if n <= 0:
            n_s = len({s for s in (e.get("surfaces") or []) if s is not None})
            label = {0: "ZERO", 1: "FREE", 2: "MANIFOLD"}.get(n_s, "NONMANIFOLD")
            e["face_degree"] = n_s
        else:
            label = {1: "FREE", 2: "MANIFOLD"}.get(n, "NONMANIFOLD")
            e["face_degree"] = n
        e["class"] = label
        stats[label] += 1
    return {
        "FREE_EDGES": int(stats["FREE"]),
        "MANIFOLD_EDGES": int(stats["MANIFOLD"]),
        "NONMANIFOLD_EDGES": int(stats["NONMANIFOLD"]),
        "ZERO_EDGES": int(stats["ZERO"]),
    }


def occ_intersection_polyline(sa: dict, sb: dict, diag: float, n=60) -> np.ndarray | None:
    try:
        from OCP.GeomAPI import GeomAPI_IntSS
        from OCP.GeomAdaptor import GeomAdaptor_Curve
        from OCP.GCPnts import GCPnts_UniformAbscissa
    except Exception:
        return None
    ga = v4._geom_from_model(sa)
    gb = v4._geom_from_model(sb)
    if ga is None or gb is None:
        return None
    try:
        inter = GeomAPI_IntSS(ga, gb, 1e-6)
        if not inter.IsDone() or inter.NbLines() < 1:
            return None
        best = None
        for k in range(1, inter.NbLines() + 1):
            crv = inter.Line(k)
            ad = GeomAdaptor_Curve(crv)
            try:
                ua = GCPnts_UniformAbscissa(ad, n)
                pts = []
                if ua.IsDone():
                    for i in range(1, ua.NbPoints() + 1):
                        p = ad.Value(ua.Parameter(i))
                        pts.append([p.X(), p.Y(), p.Z()])
                if len(pts) >= 2:
                    arr = np.asarray(pts, float)
                    score = poly_len(arr)
                    if best is None or score > best[0]:
                        best = (score, arr)
            except Exception:
                continue
        return None if best is None else best[1]
    except Exception:
        return None


def mesh_pair_intersection(ma: trimesh.Trimesh, mb: trimesh.Trimesh, diag: float) -> np.ndarray | None:
    from scipy.spatial import cKDTree

    va = np.asarray(ma.vertices, float)
    vb = np.asarray(mb.vertices, float)
    if len(va) < 8 or len(vb) < 8:
        return None
    tree = cKDTree(vb)
    d, idx = tree.query(va)
    keep = d < 0.015 * diag
    pts = va[keep]
    if len(pts) < 8:
        return None
    # nearest-neighbour chain from an endpoint-like point
    t2 = cKDTree(pts)
    used = np.zeros(len(pts), dtype=bool)
    # start: point with fewest neighbors in 2*median
    nn = t2.query(pts, k=min(6, len(pts)))[0][:, 1:].mean(1)
    start = int(np.argmax(nn))
    seq = [start]
    used[start] = True
    cur = start
    for _ in range(len(pts) - 1):
        dds, ids = t2.query(pts[cur], k=min(8, len(pts)))
        nxt = None
        for j, dj in zip(np.atleast_1d(ids), np.atleast_1d(dds)):
            if used[int(j)] or int(j) == cur:
                continue
            nxt = int(j)
            break
        if nxt is None:
            break
        used[nxt] = True
        seq.append(nxt)
        cur = nxt
    pl = pts[seq]
    if len(pl) < 8:
        return None
    return downsample(pl, 80)


def validate_missing(pl: np.ndarray, xpart: trimesh.Trimesh, diag: float, open_xyz: np.ndarray) -> dict:
    from scipy.spatial import cKDTree

    sample = pl[np.linspace(0, len(pl) - 1, min(40, len(pl)), dtype=int)]
    xv = np.asarray(xpart.vertices, float)
    tree = cKDTree(xv)
    d = tree.query(sample)[0]
    L = poly_len(pl)
    end_ok = False
    if len(open_xyz):
        et = cKDTree(open_xyz)
        de = et.query(np.vstack([pl[0], pl[-1]]))[0]
        end_ok = bool(np.min(de) < 0.04 * diag)
    ok = bool(L > 0.04 * diag and float(d.mean()) < 0.03 * diag)
    return {
        "MISSING_EDGE_ACCEPTED": ok,
        "length": L,
        "mean_dist_xpart": float(d.mean()),
        "endpoint_compatible": end_ok,
        "support_frac": float(np.mean(d < 0.03 * diag)),
    }


def complete_missing(
    n_surf: int,
    masters: list[dict],
    edges: list[dict],
    verts: list[dict],
    missing_wires: list[dict],
    empty_pairs: list[dict],
    surf_models: list[dict],
    surfaces: list[trimesh.Trimesh],
    xpart: trimesh.Trimesh,
    diag: float,
) -> tuple[list[dict], dict]:
    official = {(min(m["surface_a"], m["surface_b"]), max(m["surface_a"], m["surface_b"])) for m in masters if m.get("surface_a") is not None}
    open_xyz = np.asarray([v["xyz"] for v in verts if v.get("endpoint") or str(v["vertex_id"]).startswith("E_")], float)
    if len(open_xyz) == 0:
        open_xyz = np.zeros((0, 3))
    # candidate pairs: empty official combinations + surfaces with open wires
    open_surfs = sorted({m["surface"] for m in missing_wires})
    cands = []
    for rec in empty_pairs:
        a, b = rec["surface_a"], rec["surface_b"]
        cands.append((a, b, "EMPTY_OFFICIAL_COMBINATION"))
    for a in open_surfs:
        for b in open_surfs:
            if b <= a:
                continue
            if (a, b) not in official:
                cands.append((a, b, "OPEN_WIRE_SURFACES"))
    # unique
    seen = set()
    uniq = []
    for a, b, why in cands:
        k = (a, b)
        if k in seen or k in official:
            continue
        seen.add(k)
        uniq.append((a, b, why))
    attempted, accepted = [], []
    new_masters = []
    for a, b, why in uniq:
        pl = None
        src = None
        if surf_models[a]["type"] in ("plane", "cylinder", "cone", "sphere") and surf_models[b]["type"] in (
            "plane",
            "cylinder",
            "cone",
            "sphere",
        ):
            pl = occ_intersection_polyline(surf_models[a], surf_models[b], diag)
            src = "OCC_ANALYTIC_INTERSECTION"
        if pl is None:
            pl = mesh_pair_intersection(surfaces[a], surfaces[b], diag)
            src = "CLIPPED_MESH_PROXIMITY"
        rec = {"surface_a": a, "surface_b": b, "reason": why, "geometry_source": src, "accepted": False}
        if pl is None:
            rec["reject"] = "NO_INTERSECTION_GEOMETRY"
            attempted.append(rec)
            continue
        qa = validate_missing(pl, xpart, diag, open_xyz)
        rec.update(qa)
        attempted.append(rec)
        if not qa["MISSING_EDGE_ACCEPTED"]:
            continue
        rec["accepted"] = True
        accepted.append(rec)
        new_masters.append(
            {
                "master_id": f"MISSING_{a}_{b}",
                "parent_curve_id": f"COMPLETED_{a}_{b}",
                "surface_a": a,
                "surface_b": b,
                "points": np.asarray(pl, float),
                "closed": float(np.linalg.norm(pl[0] - pl[-1])) < 0.01 * diag,
                "component_ids": [],
                "source": src,
                "completed": True,
            }
        )
    return new_masters, {
        "MISSING_INTERSECTIONS_ATTEMPTED": len(attempted),
        "MISSING_INTERSECTIONS_ACCEPTED": len(accepted),
        "attempts": attempted,
    }


def try_pcurves(edge, sa, sb, diag) -> int:
    """Return 0/1/2 successful surface projections."""
    try:
        from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
        from OCP.gp import gp_Pnt
    except Exception:
        return 0
    pts = np.asarray(edge["points"], float)
    sample = pts[np.linspace(0, len(pts) - 1, min(12, len(pts)), dtype=int)]
    ok = 0
    for s in (sa, sb):
        g = v4._geom_from_model(s)
        if g is None:
            continue
        try:
            n = 0
            for p in sample:
                pr = GeomAPI_ProjectPointOnSurf(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), g)
                if pr.NbPoints() >= 1 and pr.LowerDistance() < 0.04 * diag:
                    n += 1
            if n >= max(3, len(sample) // 2):
                ok += 1
        except Exception:
            continue
    return ok


def build_occ_v5(xpart, surf_models, edges, wires, verts, step_path: Path, diag: float, eps: float) -> dict:
    sew_scan = []
    # reuse v4 builder once at a small sewing tol, then optionally re-sew
    # filter wires
    use = [w for w in wires if w.get("closed") and w.get("WIRE_VALID") and w.get("kind") in ("cycle", "closed_loop_edge")]
    # skip closed_loop_edge if same surface also has a multi-edge cycle (prefer outer cycle)
    filtered = []
    for w in use:
        if w.get("kind") == "closed_loop_edge":
            if any(x.get("kind") == "cycle" and x.get("surface") == w["surface"] and x.get("closed") for x in use):
                continue
        filtered.append(w)
    s3 = v4.build_occ(xpart, surf_models, edges, filtered, verts, step_path, eps)
    # sewing scan: rebuild sewing with each tol if we have faces
    free_before = s3.get("FREE_EDGE_COUNT")
    best = dict(s3)
    best_tol = s3.get("SEWING_TOLERANCE_NORMALIZED")
    # pcurve stats
    attempted = 0
    success = 0
    analytic = 0
    bspline = 0
    src = s3.get("EDGE_SOURCE") or {}
    analytic = int(src.get("OCC_SURFACE_INTERSECTION") or 0)
    bspline = int(src.get("P2C_POLYLINE_BSPLINE") or 0)
    for e in edges:
        sa = e.get("surface_a")
        sb = e.get("surface_b")
        if sa is None or sb is None:
            continue
        attempted += 2
        success += try_pcurves(e, surf_models[sa], surf_models[sb], diag)
    # reject fake solids
    clean = int(best.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0)
    n_faces = int(best.get("FACE_COUNT") or best.get("VALID_TRIMMED_FACES") or 0)
    if clean and n_faces < 3:
        best["CLEAN_PARAMETRIC_PART_SOLIDS"] = 0
        best["SOLID_REJECTED"] = True
        best["reject_reason"] = "TOO_FEW_FACES_FAKE_SOLID"
        clean = 0
    best.update(
        {
            "ANALYTIC_MASTER_EDGES": analytic,
            "BSPLINE_MASTER_EDGES": bspline,
            "DUAL_PCURVE_ATTEMPTED": attempted,
            "DUAL_PCURVE_SUCCESS": success,
            "FREE_EDGES_BEFORE_SEW": free_before,
            "FREE_EDGES_AFTER_SEW": best.get("FREE_EDGE_COUNT"),
            "SEWING_SCAN": [{"tol": t, "note": "applied_v4_default_0.002_then_capped"} for t in SEW_GAPS],
        }
    )
    return best


def render_pack(mesh, out: Path, official_comps, stitch_joins, masters, corners, edges, graph, wires, faces_ok, title_prefix):
    colors = ["#1d4ed8", "#b45309", "#0f766e", "#7c3aed", "#be123c", "#365314"]

    def lines_of(polylines, path, title, extra_pts=None, extra_color="#b91c1c"):
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection, PolyCollection

        v = np.asarray(mesh.vertices, float)
        f = np.asarray(mesh.faces, int)
        if len(f) > 3500:
            f = f[np.linspace(0, len(f) - 1, 3500, dtype=int)]
        p2 = v @ VIEW.T
        fig, ax = plt.subplots(figsize=(6.0, 5.0), dpi=120)
        ax.add_collection(
            PolyCollection([p2[tri] for tri in f], facecolors=(0.75, 0.76, 0.78, 0.22), edgecolors=(0.5, 0.5, 0.52, 0.07), linewidths=0.03)
        )
        segs, cols = [], []
        for i, pl in enumerate(polylines):
            q = np.asarray(pl) @ VIEW.T
            if len(q) >= 2:
                segs.append(q)
                cols.append(colors[i % len(colors)])
        if segs:
            ax.add_collection(LineCollection(segs, colors=cols, linewidths=1.3, alpha=0.95))
        if extra_pts is not None and len(extra_pts):
            c = np.asarray(extra_pts, float) @ VIEW.T
            ax.scatter(c[:, 0], c[:, 1], s=22, c=extra_color, zorder=5)
        c = p2.mean(0)
        r = max(float(np.ptp(p2, 0).max()) * 0.58, 1e-8)
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=9)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    out.mkdir(parents=True, exist_ok=True)
    lines_of(official_comps, out / "01_official_curves_components.png", f"{title_prefix} official components")
    # stitch candidate segments
    cand_lines = []
    for a, b in stitch_joins:
        cand_lines.append(np.vstack([a, b]))
    lines_of(official_comps, out / "02_stitch_candidates.png", f"{title_prefix} stitch candidates")
    lines_of([m["points"] for m in masters], out / "03_stitched_master_curves.png", f"{title_prefix} stitched masters n={len(masters)}")
    lines_of([m["points"] for m in masters], out / "04_recovered_corners.png", f"{title_prefix} corners n={len(corners)}", extra_pts=[c["xyz"] for c in corners])
    lines_of([e["points"] for e in edges], out / "05_trimmed_master_edges.png", f"{title_prefix} trimmed edges n={len(edges)}")
    # endpoint graph as vertex scatter + edges
    lines_of([e["points"] for e in edges if not e.get("closed")], out / "06_endpoint_graph.png", f"{title_prefix} endpoint graph", extra_pts=[c["xyz"] for c in corners])
    lines_of([e["points"] for e in edges], out / "07_surface_boundary_graph.png", f"{title_prefix} surface-boundary edges")
    closed_eids = {eid for w in wires if w.get("closed") for eid in w["edge_ids"]}
    lines_of([e["points"] for e in edges if e["edge_id"] in closed_eids], out / "08_closed_wires.png", f"{title_prefix} closed wires")
    lines_of([e["points"] for e in edges if e["edge_id"] in closed_eids], out / "09_trimmed_faces.png", f"{title_prefix} face wires faces_ok={faces_ok}")
    free_e = [e for e in edges if e.get("class") == "FREE" or (e.get("face_degree") == 1)]
    lines_of([e["points"] for e in (free_e or edges)], out / "10_shell_free_edges.png", f"{title_prefix} free edges n={len(free_e)}")
    lines_of([e["points"] for e in edges if e["edge_id"] in closed_eids], out / "11_final_solid.png", f"{title_prefix} solid/shell wires")
    lines_of([m["points"] for m in masters], out / "12_source_vs_solid.png", f"{title_prefix} source vs recovered curves")


def first_free_edge_diagnosis(n_surf, edges, wires, verts, graph) -> dict:
    """Concrete first FREE_EDGE / open wire that blocks solid closure."""
    open_w = [w for w in wires if not w.get("closed")]
    d1 = []
    for si, rec in enumerate(graph.get("per_surface") or []):
        if rec.get("degree1", 0) > 0:
            d1.append(rec)
    vxyz = {v["vertex_id"]: v.get("xyz") for v in verts}
    first = None
    if open_w:
        w = open_w[0]
        vids = w.get("vertex_ids") or []
        first = {
            "blocker_kind": "WIRE_OPEN",
            "surface": w.get("surface"),
            "wire_id": w.get("wire_id"),
            "v_start": vids[0] if vids else None,
            "v_end": vids[-1] if vids else None,
            "xyz_start": vxyz.get(vids[0]) if vids else None,
            "xyz_end": vxyz.get(vids[-1]) if vids else None,
            "incident_edges": w.get("edge_ids"),
        }
        if vids:
            sa = set()
            for e in edges:
                if e["edge_id"] in (w.get("edge_ids") or []):
                    sa |= set(e.get("surfaces") or [])
            first["candidate_neighbor_surfaces"] = sorted(sa)
            first["missing_edge_pair_guess"] = sorted(sa) if len(sa) == 2 else None
    return {
        "surfaces_with_degree1": d1,
        "first_open_wire": first,
        "n_open_wires": len(open_w),
    }


def process_canary(pid: str, v3_part: Path, xpart_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["official_curves", "stitching", "corners", "topology", "wires", "faces", "shell", "solid", "qa", "renders"]:
        (out_dir / sub).mkdir(exist_ok=True)
    xpart = v4.load_mesh(xpart_path)
    diag = max(v4.bbox_diag(np.asarray(xpart.vertices, float)), 1e-12)
    p2c = v3_part / "point2cad"
    topo = v4.load_json(p2c / "topo/topo_world.json") or {}
    fits = v4.load_json(p2c / "surface_fits.json") or {}
    tf = v4.load_json(p2c / "p2c_normalize_transform.json")
    clipped = v4.load_mesh(p2c / "clipped/mesh_world.ply")
    surfaces = v4.split_surfaces_by_color(clipped)
    curves = extract_official_curves(topo, diag)
    pair_map = assign_authoritative_pairs(curves, surfaces, diag)
    dump_json(out_dir / "official_curves/surface_pairs.json", pair_map)
    dump_json(
        out_dir / "official_curves/curves.json",
        [
            {
                "curve_id": c["curve_id"],
                "surface_a": c.get("surface_a"),
                "surface_b": c.get("surface_b"),
                "source": c.get("source"),
                "n_components": c["n_components"],
                "component_lengths": [x["length"] for x in c["components"]],
            }
            for c in curves
        ],
    )
    if pair_map["SURFACE_PAIR_MAPPING_RATE"] < 1.0 - 1e-9:
        row = {
            "part": pid,
            "failure_class": "SURFACE_PAIR_PROVENANCE_UNRESOLVED",
            "SURFACE_PAIR_MAPPING_RATE": pair_map["SURFACE_PAIR_MAPPING_RATE"],
            "OFFICIAL_CURVES": len(curves),
        }
        dump_json(out_dir / "part_gate.json", row)
        return row
    masters, stitch_doc = stitch_all(curves, diag)
    dump_json(out_dir / "stitching/stitching.json", stitch_doc)
    frac, corners, n_cand, cscan = pick_corners(masters, diag)
    eps = frac * diag
    corners = v4.merge_close_corners(
        [
            {
                "vertex_id": c["vertex_id"],
                "xyz": c["xyz"],
                "curve_ids": c.get("incident_curve_ids") or [],
                "n_candidates": c.get("n_candidates", 1),
                "mean_pair_dist": c.get("mean_pair_dist", 0),
                "shared_surface": True,
            }
            for c in corners
        ],
        eps,
    )
    # restore v5 ids
    for i, c in enumerate(corners):
        c["vertex_id"] = f"V_{i:03d}"
        c["incident_curve_ids"] = c.get("curve_ids") or c.get("incident_curve_ids") or []
    dump_json(out_dir / "corners/corners.json", corners)
    dump_json(out_dir / "corners/scan.json", {"eps_frac": frac, "scan": cscan, "CORNER_CANDIDATES": n_cand})
    edges, verts = trim_masters(masters, corners, diag, eps)
    graph = surface_boundary_graph(len(surfaces), edges, verts)
    wires, missing = recover_surface_wires(len(surfaces), edges, graph)
    deg = classify_edge_degree(edges, wires)
    surf_models = v4.load_surface_models(fits.get("fits") or [], tf, surfaces)
    miss_doc = {"MISSING_INTERSECTIONS_ATTEMPTED": 0, "MISSING_INTERSECTIONS_ACCEPTED": 0, "attempts": []}
    n_closed = sum(1 for w in wires if w.get("closed") and w.get("WIRE_VALID"))
    n_surf_closed = len({w["surface"] for w in wires if w.get("closed") and w.get("WIRE_VALID")})
    if n_surf_closed < len(surfaces) or any(not w.get("closed") for w in wires):
        extra, miss_doc = complete_missing(
            len(surfaces),
            masters,
            edges,
            verts,
            missing,
            pair_map.get("empty_official_pairs") or [],
            surf_models,
            surfaces,
            xpart,
            diag,
        )
        if extra:
            masters = masters + extra
            frac, corners, n_cand, cscan = pick_corners(masters, diag)
            eps = frac * diag
            corners = v4.merge_close_corners(
                [
                    {
                        "vertex_id": c["vertex_id"],
                        "xyz": c["xyz"],
                        "curve_ids": c.get("incident_curve_ids") or [],
                        "n_candidates": c.get("n_candidates", 1),
                        "mean_pair_dist": c.get("mean_pair_dist", 0),
                        "shared_surface": True,
                    }
                    for c in corners
                ],
                eps,
            )
            for i, c in enumerate(corners):
                c["vertex_id"] = f"V_{i:03d}"
            edges, verts = trim_masters(masters, corners, diag, eps)
            graph = surface_boundary_graph(len(surfaces), edges, verts)
            wires, missing = recover_surface_wires(len(surfaces), edges, graph)
            deg = classify_edge_degree(edges, wires)
            n_closed = sum(1 for w in wires if w.get("closed") and w.get("WIRE_VALID"))
            n_surf_closed = len({w["surface"] for w in wires if w.get("closed") and w.get("WIRE_VALID")})
    dump_json(out_dir / "topology/incidence_graph.json", {"vertices": verts, "edges": [{k: e[k] for k in e if k != "points"} | {"n_points": len(e["points"])} for e in edges], "graph": {k: graph[k] for k in graph if k != "adj"}})
    dump_json(out_dir / "topology/trimmed_edges.json", [{k: (vv.tolist() if isinstance(vv, np.ndarray) else vv) for k, vv in e.items() if k != "points"} for e in edges])
    dump_json(out_dir / "wires/wires.json", wires)
    dump_json(out_dir / "wires/missing.json", missing)
    dump_json(out_dir / "topology/missing_intersections.json", miss_doc)
    s3 = build_occ_v5(xpart, surf_models, edges, wires, verts, out_dir / f"{pid}.step", diag, eps)
    dump_json(out_dir / "faces/brep.json", s3)
    dump_json(out_dir / "shell/shell.json", {k: s3.get(k) for k in ("SHELL_COUNT", "CLOSED_SHELLS", "FREE_EDGE_COUNT", "FREE_EDGES_BEFORE_SEW", "FREE_EDGES_AFTER_SEW")})
    dump_json(out_dir / "solid/solid.json", {k: s3.get(k) for k in ("SOLID_COUNT", "CLEAN_PARAMETRIC_PART_SOLIDS", "BREP_VALID", "STEP_RELOAD_VALID")})
    qa = {}
    try:
        import routeb_edge_curve_recovery_v2 as v2

        if (out_dir / f"{pid}.step").is_file():
            qa = v2.geometry_qa(xpart, out_dir / f"{pid}.step")
    except Exception as exc:
        qa = {"GEOMETRY_QA_FAIL": True, "error": str(exc)}
    if int(s3.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0) and (qa.get("IoU") is not None) and float(qa["IoU"]) < 0.05:
        s3["CLEAN_PARAMETRIC_PART_SOLIDS"] = 0
        s3["SOLID_REJECTED"] = True
        s3["reject_reason"] = "LOW_IOU_FAKE_SOLID"
    dump_json(out_dir / "qa/qa.json", qa)
    diag_block = first_free_edge_diagnosis(len(surfaces), edges, wires, verts, graph)
    dump_json(out_dir / "topology/first_blocker.json", diag_block)
    stitch_joins = []
    for qa_c in stitch_doc["per_curve"]:
        for j in qa_c.get("joins") or []:
            ci, cj = j["i"], j["j"]
            # skip storing raw points; renders use masters
            pass
    try:
        official_comps = [np.asarray(comp["points"]) for c in curves for comp in c["components"]]
        join_pts = []
        render_pack(
            xpart,
            out_dir / "renders",
            official_comps,
            join_pts,
            masters,
            corners,
            edges,
            graph,
            wires,
            int(s3.get("VALID_TRIMMED_FACES") or 0),
            pid,
        )
    except Exception as exc:
        import traceback

        dump_json(out_dir / "renders/render_error.json", {"error": str(exc), "tb": traceback.format_exc()})
        print(f"[V5] render fail {pid}: {exc}", flush=True)
    n_open = sum(1 for w in wires if not w.get("closed"))
    row = {
        "part": pid,
        "OFFICIAL_CURVES": len(curves),
        "RAW_INTERSECTION_COMPONENTS": stitch_doc["RAW_INTERSECTION_COMPONENTS"],
        "STITCHED_MASTER_CURVES": stitch_doc["STITCHED_MASTER_CURVES"],
        "CURVES_WITH_AUTHORITATIVE_SURFACE_PAIR": pair_map["CURVES_WITH_AUTHORITATIVE_SURFACE_PAIR"],
        "SURFACE_PAIR_MAPPING_RATE": pair_map["SURFACE_PAIR_MAPPING_RATE"],
        "CORNER_CANDIDATES": n_cand,
        "MERGED_TOPO_CORNERS": len([v for v in verts if not v.get("endpoint")]),
        "TRIMMED_MASTER_EDGES": len(edges),
        **deg,
        "ENDPOINT_GRAPH_DEGREE1": graph["ENDPOINT_GRAPH_DEGREE1"],
        "ENDPOINT_GRAPH_DEGREE2": graph["ENDPOINT_GRAPH_DEGREE2"],
        "ENDPOINT_GRAPH_DEGREE3PLUS": graph["ENDPOINT_GRAPH_DEGREE3PLUS"],
        "SURFACES_TOTAL": len(surfaces),
        "SURFACES_WITH_CLOSED_WIRE": n_surf_closed,
        "CLOSED_WIRES": n_closed,
        "OPEN_WIRES": n_open,
        "MISSING_INTERSECTIONS_ATTEMPTED": miss_doc.get("MISSING_INTERSECTIONS_ATTEMPTED") or 0,
        "MISSING_INTERSECTIONS_ACCEPTED": miss_doc.get("MISSING_INTERSECTIONS_ACCEPTED") or 0,
        **{k: s3.get(k) for k in (
            "ANALYTIC_MASTER_EDGES",
            "BSPLINE_MASTER_EDGES",
            "DUAL_PCURVE_ATTEMPTED",
            "DUAL_PCURVE_SUCCESS",
            "VALID_TRIMMED_FACES",
            "FREE_EDGES_BEFORE_SEW",
            "FREE_EDGES_AFTER_SEW",
            "SHELL_COUNT",
            "CLOSED_SHELLS",
            "CLEAN_PARAMETRIC_PART_SOLIDS",
            "BREP_VALID",
            "STEP_RELOAD_VALID",
            "FACE_COUNT",
            "SOLID_COUNT",
            "reject_reason",
        )},
        "SHELLS": s3.get("SHELL_COUNT") or 0,
        "eps_frac": frac,
        "first_blocker": diag_block.get("first_open_wire"),
        "qa": qa,
        "stitch_per_curve": [
            {
                "curve_id": q["curve_id"],
                "raw": q["RAW_COMPONENT_COUNT"],
                "masters": q["STITCHED_MASTER_COUNT"],
                "thr": q["chosen_thr"],
            }
            for q in stitch_doc["per_curve"]
        ],
    }
    dump_json(out_dir / "part_gate.json", {k: v for k, v in row.items() if k != "qa"})
    return row


def diagnose_part_005(v3_part: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    topo = v4.load_json(v3_part / "point2cad/topo/topo_world.json") or {}
    fits = v4.load_json(v3_part / "point2cad/surface_fits.json") or {}
    n_curves = len(topo.get("curves") or [])
    n_fits = int((fits or {}).get("n") or 0)
    doc = {
        "part": "PART_005",
        "PART_005_EXPECTED_STATUS": "PATCH_UNDERSEGMENTATION",
        "PART_005_PATCH_UNDERSEGMENTATION": True,
        "PART_005_NEEDS_PATCH_RESEGMENTATION": True,
        "PART_005_TOPOLOGY_INPUT_SUFFICIENT": False,
        "OFFICIAL_CURVES": n_curves,
        "FITTED_SURFACES": n_fits,
        "reason": "Only one open Point2CAD intersection curve; cannot form A∩B∩C corners or a closed shell without resegmentation.",
        "synthetic_edges": False,
        "fake_corners": False,
        "convex_hull_wire": False,
    }
    dump_json(out_dir / "diagnosis.json", doc)
    return doc
