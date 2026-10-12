"""Fragment ↔ OCC branch matching and gap support audit."""
from __future__ import annotations

from typing import Any

import numpy as np
import trimesh

from .occ_branches import project_point_to_branch


def poly_len(pts: np.ndarray) -> float:
    if len(pts) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def dist_stats(dists: np.ndarray) -> dict:
    d = np.asarray(dists, float)
    if len(d) == 0:
        return {"mean": None, "median": None, "p95": None, "max": None}
    return {
        "mean": float(np.mean(d)),
        "median": float(np.median(d)),
        "p95": float(np.percentile(d, 95)),
        "max": float(np.max(d)),
    }


def sample_curve_segment(crv, t0: float, t1: float, n: int = 200) -> tuple[np.ndarray, np.ndarray]:
    from OCP.GeomAdaptor import GeomAdaptor_Curve

    if t1 < t0:
        t0, t1 = t1, t0
    ad = GeomAdaptor_Curve(crv)
    ts = np.linspace(t0, t1, max(n, 2))
    pts = []
    for t in ts:
        p = ad.Value(float(t))
        pts.append([p.X(), p.Y(), p.Z()])
    return np.asarray(pts, float), ts


def match_fragment_to_branch(frag: dict, branches: list[dict]) -> dict:
    pts = np.asarray(frag["points"], dtype=float)
    best = None
    for b in branches:
        crv = b.get("occ_curve")
        if crv is None:
            continue
        dists = []
        ts = []
        for p in pts[np.linspace(0, len(pts) - 1, min(32, len(pts)), dtype=int)]:
            t, d = project_point_to_branch(crv, p)
            if np.isfinite(d):
                dists.append(d)
                ts.append(t)
        if not dists:
            continue
        ds = np.asarray(dists, float)
        mean_d = float(np.mean(ds))
        # tangent alignment at midpoint
        mid = pts[len(pts) // 2]
        t_mid, _ = project_point_to_branch(crv, mid)
        tan_frag = frag.get("start_tangent")
        tan_align = 0.0
        try:
            from OCP.GeomAdaptor import GeomAdaptor_Curve

            ad = GeomAdaptor_Curve(crv)
            pnt, tan = ad.D1(float(t_mid))
            ct = np.array([tan.X(), tan.Y(), tan.Z()], float)
            ft = np.asarray(tan_frag, float)
            ct = ct / (np.linalg.norm(ct) + 1e-12)
            ft = ft / (np.linalg.norm(ft) + 1e-12)
            tan_align = float(abs(np.dot(ct, ft)))
        except Exception:
            pass
        overlap = float(np.percentile(ds, 50))
        score = mean_d + 0.1 * (1.0 - tan_align)
        if best is None or score < best["score"]:
            conf = "HIGH" if mean_d < 0.005 else ("MEDIUM" if mean_d < 0.02 else "LOW")
            if mean_d > 0.05:
                conf = "NONE"
            best = {
                "fragment_id": frag["fragment_id"],
                "surface_pair": list(frag["surface_pair"]),
                "matched_occ_branch": b["branch_id"],
                "mean_distance": mean_d,
                "median_distance": float(np.median(ds)),
                "p95_distance": float(np.percentile(ds, 95)),
                "max_distance": float(np.max(ds)),
                "tangent_alignment": tan_align,
                "overlap_length": overlap,
                "confidence": conf,
                "t_range": [float(min(ts)), float(max(ts))],
                "score": score,
            }
    if best is None:
        return {
            "fragment_id": frag["fragment_id"],
            "surface_pair": list(frag["surface_pair"]),
            "matched_occ_branch": None,
            "mean_distance": None,
            "p95_distance": None,
            "tangent_alignment": None,
            "confidence": "NONE",
        }
    return best


def build_boundary_evidence(xpart: trimesh.Trimesh, clipped_surfaces: list[trimesh.Trimesh], diag: float) -> dict:
    from scipy.spatial import cKDTree

    xv = np.asarray(xpart.vertices, float)
    xtree = cKDTree(xv)
    # sharp edges on xpart
    sharp_pts = []
    try:
        adj = xpart.edges_unique
        v = xv
        for e in adj[: min(len(adj), 50000)]:
            n1 = xpart.vertex_normals[e[0]]
            n2 = xpart.vertex_normals[e[1]]
            if float(np.dot(n1, n2)) < 0.5:
                sharp_pts.append(0.5 * (v[e[0]] + v[e[1]]))
    except Exception:
        pass
    sharp = np.asarray(sharp_pts, float) if sharp_pts else xv[np.linspace(0, len(xv) - 1, min(500, len(xv)), dtype=int)]
    sharp_tree = cKDTree(sharp) if len(sharp) else xtree
    # patch color boundaries from clipped meshes
    patch_boundary = []
    for sm in clipped_surfaces:
        pts = np.asarray(sm.vertices, float)
        if len(pts):
            patch_boundary.append(pts[np.linspace(0, len(pts) - 1, min(200, len(pts)), dtype=int)])
    pb = np.vstack(patch_boundary) if patch_boundary else xv
    pb_tree = cKDTree(pb)
    return {
        "BOUNDARY_SUPPORT_AVAILABLE": True,
        "surface_tree": xtree,
        "boundary_tree": pb_tree,
        "sharp_tree": sharp_tree,
        "surface_thr": 0.03 * diag,
        "boundary_thr": 0.04 * diag,
    }


def audit_segment_support(
    crv,
    t0: float,
    t1: float,
    evidence: dict,
    diag: float,
    n: int = 200,
) -> dict:
    pts, ts = sample_curve_segment(crv, t0, t1, n=max(n, 200))
    if len(pts) < 2:
        return {"segment_length": 0.0, "support_frac_surface": 0.0, "support_frac_boundary": 0.0}
    seg_len = poly_len(pts)
    ds = evidence["surface_tree"].query(pts)[0]
    db = evidence["boundary_tree"].query(pts)[0]
    st = evidence["surface_thr"]
    bt = evidence["boundary_thr"]
    return {
        "segment_length": seg_len,
        "segment_length_norm": seg_len / max(diag, 1e-12),
        "n_samples": len(pts),
        "surface_distance_mean": float(np.mean(ds)),
        "surface_distance_p50": float(np.median(ds)),
        "surface_distance_p95": float(np.percentile(ds, 95)),
        "surface_distance_max": float(np.max(ds)),
        "boundary_distance_mean": float(np.mean(db)),
        "boundary_distance_p95": float(np.percentile(db, 95)),
        "support_frac_surface": float(np.mean(ds < st)),
        "support_frac_boundary": float(np.mean(db < bt)),
        "surface_distance_mean_norm": float(np.mean(ds) / max(diag, 1e-12)),
        "boundary_distance_p95_norm": float(np.percentile(db, 95) / max(diag, 1e-12)),
    }


def classify_gap(
    frag_i: dict,
    frag_j: dict,
    match_i: dict,
    match_j: dict,
    support: dict,
    endpoint_gap: float,
    diag: float,
) -> str:
    same = (
        match_i.get("matched_occ_branch")
        and match_j.get("matched_occ_branch")
        and match_i["matched_occ_branch"] == match_j["matched_occ_branch"]
        and match_i.get("confidence") in ("HIGH", "MEDIUM")
        and match_j.get("confidence") in ("HIGH", "MEDIUM")
    )
    if not same:
        if match_i.get("confidence") == "NONE" or match_j.get("confidence") == "NONE":
            return "FIT_TOPOLOGY_INCONSISTENT"
        if match_i.get("matched_occ_branch") != match_j.get("matched_occ_branch"):
            return "AMBIGUOUS" if endpoint_gap / max(diag, 1e-12) < 0.01 else "FIT_TOPOLOGY_INCONSISTENT"
        return "AMBIGUOUS"
    bs = support.get("support_frac_boundary") or 0.0
    ss = support.get("support_frac_surface") or 0.0
    if bs >= 0.5 and ss >= 0.5:
        return "TRUE_INTERSECTION_FRAGMENTATION"
    if ss >= 0.5 and bs < 0.25:
        return "TRUE_TRIM_SEPARATION"
    if ss < 0.25 and bs < 0.25:
        return "FIT_TOPOLOGY_INCONSISTENT"
    return "AMBIGUOUS"


def enumerate_gaps(
    frags: list[dict],
    matches: dict,
    branches: list[dict],
    evidence: dict,
    diag: float,
    accepted_pairs: set[tuple[str, str]] | None = None,
) -> list[dict]:
    by_branch: dict[str, list[dict]] = {}
    for f in frags:
        m = matches[f["fragment_id"]]
        bid = m.get("matched_occ_branch")
        if bid:
            by_branch.setdefault(bid, []).append({**f, "match": m})
    branch_map = {b["branch_id"]: b for b in branches}
    gaps = []
    for bid, group in by_branch.items():
        if len(group) < 2:
            continue
        b = branch_map.get(bid)
        if not b:
            continue
        crv = b.get("occ_curve")
        # sort by parameter at start
        tagged = []
        for f in group:
            t_s, d_s = project_point_to_branch(crv, np.asarray(f["start_xyz"], float))
            t_e, d_e = project_point_to_branch(crv, np.asarray(f["end_xyz"], float))
            tagged.append({**f, "t_start": t_s, "t_end": t_e})
        tagged.sort(key=lambda x: min(x["t_start"], x["t_end"]))
        for a, bfrag in zip(tagged, tagged[1:]):
            # endpoints closest along branch
            ends_a = [("s", a["t_start"], a["start_xyz"]), ("e", a["t_end"], a["end_xyz"])]
            ends_b = [("s", bfrag["t_start"], bfrag["start_xyz"]), ("e", bfrag["t_end"], bfrag["end_xyz"])]
            best = None
            for _, ta, pa in ends_a:
                for _, tb, pb in ends_b:
                    g = float(np.linalg.norm(np.asarray(pa, float) - np.asarray(pb, float)))
                    if best is None or g < best["gap"]:
                        t_i, t_j = float(ta), float(tb)
                        best = {"gap": g, "t_i": t_i, "t_j": t_j, "pa": pa, "pb": pb}
            if best is None:
                continue
            t0, t1 = sorted([best["t_i"], best["t_j"]])
            if abs(t1 - t0) < 1e-9:
                continue
            support = audit_segment_support(crv, t0, t1, evidence, diag)
            cls = classify_gap(a, bfrag, a["match"], bfrag["match"], support, best["gap"], diag)
            key = tuple(sorted([a["fragment_id"], bfrag["fragment_id"]]))
            gaps.append(
                {
                    "fragment_i": a["fragment_id"],
                    "fragment_j": bfrag["fragment_id"],
                    "surface_pair": list(a["surface_pair"]),
                    "occ_branch": bid,
                    "same_occ_branch": True,
                    "endpoint_xyz_gap": best["gap"],
                    "normalized_xyz_gap": best["gap"] / max(diag, 1e-12),
                    "t_start": t0,
                    "t_end": t1,
                    "analytic_gap_segment_length": support["segment_length"],
                    **support,
                    "classification": cls,
                    "v6a_accepted": key in (accepted_pairs or set()),
                }
            )
    return gaps
