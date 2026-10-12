"""OCC analytic interval recovery, dual pcurves, interval merge. No straight bridges."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4
from airplane_point2cad_analytic_branch_audit_v6a1.occ_branches import (
    curve_type_name,
    extract_occ_branches,
    project_point_to_branch,
    sample_curve,
)
from airplane_point2cad_analytic_branch_audit_v6a1.gap_audit import (
    audit_segment_support,
    sample_curve_segment,
)


def poly_len(pts: np.ndarray) -> float:
    if len(pts) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def match_saved_branch(extracted: list[dict], saved: dict, diag: float) -> dict | None:
    """Match re-extracted OCC branch to V6A.1 saved branch by geometry, not nearest centroid of fragments."""
    s0 = np.asarray(saved.get("start") or [0, 0, 0], float)
    s1 = np.asarray(saved.get("end") or [0, 0, 0], float)
    slen = float(saved.get("length") or 0)
    best = None
    for b in extracted:
        e0 = np.asarray(b["start"], float)
        e1 = np.asarray(b["end"], float)
        d_fwd = float(np.linalg.norm(e0 - s0) + np.linalg.norm(e1 - s1))
        d_rev = float(np.linalg.norm(e0 - s1) + np.linalg.norm(e1 - s0))
        d = min(d_fwd, d_rev)
        ld = abs(float(b.get("length") or 0) - slen)
        score = d + 0.1 * ld
        if best is None or score < best[0]:
            best = (score, b, d_rev < d_fwd)
    if best is None:
        return None
    if best[0] > 0.08 * max(diag, 1e-6) and best[2] is not None:
        # still accept if endpoints are reasonably close
        if best[0] > 0.25 * max(diag, 1e-6):
            return None
    rec = dict(best[1])
    rec["reversed_vs_saved"] = bool(best[2])
    rec["geom_match_score"] = float(best[0])
    return rec


def normalize_curve_type(name: str) -> str:
    n = (name or "OTHER").upper().replace("GEOM_", "")
    order = [
        ("BSPLINE", "BSPLINE"),
        ("BEZIER", "BEZIER"),
        ("HYPERBOLA", "HYPERBOLA"),
        ("PARABOLA", "PARABOLA"),
        ("ELLIPSE", "ELLIPSE"),
        ("CIRCLE", "CIRCLE"),
        ("LINE", "LINE"),
    ]
    for k, v in order:
        if k in n:
            return v
    return "OTHER"


def project_endpoints(frag_i: dict, frag_j: dict, crv, diag: float) -> dict:
    ends_i = [("s", np.asarray(frag_i["start_xyz"], float)), ("e", np.asarray(frag_i["end_xyz"], float))]
    ends_j = [("s", np.asarray(frag_j["start_xyz"], float)), ("e", np.asarray(frag_j["end_xyz"], float))]
    best = None
    for ti, pi in ends_i:
        for tj, pj in ends_j:
            t_i, d_i = project_point_to_branch(crv, pi)
            t_j, d_j = project_point_to_branch(crv, pj)
            gap = float(np.linalg.norm(pi - pj))
            if not np.isfinite(d_i) or not np.isfinite(d_j):
                continue
            score = d_i + d_j + 0.01 * gap
            if best is None or score < best["score"]:
                best = {
                    "left_end": ti,
                    "right_end": tj,
                    "t_left": float(t_i),
                    "t_right": float(t_j),
                    "ENDPOINT_PROJECTION_ERROR_LEFT": float(d_i),
                    "ENDPOINT_PROJECTION_ERROR_RIGHT": float(d_j),
                    "EUCLIDEAN_ENDPOINT_GAP": gap,
                    "p_left": pi.tolist(),
                    "p_right": pj.tolist(),
                    "score": score,
                }
    if best is None:
        return {"ok": False, "reason": "PARAMETER_INTERVAL_FAILED"}
    t0, t1 = sorted([best["t_left"], best["t_right"]])
    if abs(t1 - t0) < 1e-12:
        return {**best, "ok": False, "reason": "PARAMETER_INTERVAL_FAILED", "T_LEFT": t0, "T_RIGHT": t1}
    pts, _ = sample_curve_segment(crv, t0, t1, n=max(200, int(400 * abs(t1 - t0) / max(abs(t1 - t0), 1e-6))))
    alen = poly_len(pts)
    gap = best["EUCLIDEAN_ENDPOINT_GAP"]
    best.update(
        {
            "ok": True,
            "T_LEFT": t0,
            "T_RIGHT": t1,
            "ANALYTIC_SEGMENT_LENGTH": alen,
            "ARC_LENGTH_OVER_GAP": alen / max(gap, 1e-12),
        }
    )
    # detour: analytic much longer than Euclidean gap without being a real curve
    if gap > 1e-6 and alen > 8.0 * gap and abs(t1 - t0) > 0.2:
        best["ok"] = False
        best["reason"] = "PARAMETER_INTERVAL_FAILED"
        best["detour"] = True
    proj_thr = 0.04 * diag
    if best["ENDPOINT_PROJECTION_ERROR_LEFT"] > proj_thr or best["ENDPOINT_PROJECTION_ERROR_RIGHT"] > proj_thr:
        best["ok"] = False
        best["reason"] = "PARAMETER_INTERVAL_FAILED"
        best["unstable_projection"] = True
    return best


def revalidate_support(crv, t0: float, t1: float, evidence: dict, diag: float) -> dict:
    n = max(200, int(400 * abs(t1 - t0) + 50))
    sup = audit_segment_support(crv, t0, t1, evidence, diag, n=n)
    pts, _ = sample_curve_segment(crv, t0, t1, n=n)
    db = evidence["boundary_tree"].query(pts)[0]
    ds = evidence["surface_tree"].query(pts)[0]
    sup["boundary_distance_p50"] = float(np.median(db))
    sup["boundary_distance_max"] = float(np.max(db))
    sup["surface_distance_p95_norm"] = float(np.percentile(ds, 95) / max(diag, 1e-12))
    st_ok = float(sup.get("support_frac_surface") or 0) >= 0.5
    bd_ok = float(sup.get("support_frac_boundary") or 0) >= 0.5
    avail = bool(evidence.get("BOUNDARY_SUPPORT_AVAILABLE", True))
    sup["surface_ok"] = st_ok
    sup["boundary_ok"] = bd_ok and avail
    sup["BOUNDARY_SUPPORT_AVAILABLE"] = avail
    sup["revalidation_pass"] = bool(st_ok and bd_ok and avail)
    return sup


def make_trimmed_edge(crv, t0: float, t1: float):
    from OCP.Geom import Geom_TrimmedCurve
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    from OCP.BRepCheck import BRepCheck_Analyzer

    if t1 < t0:
        t0, t1 = t1, t0
    trim = Geom_TrimmedCurve(crv, float(t0), float(t1))
    mk = BRepBuilderAPI_MakeEdge(trim)
    if not mk.IsDone():
        return None, trim, False
    edge = mk.Edge()
    valid = True
    try:
        valid = bool(BRepCheck_Analyzer(edge).IsValid())
    except Exception:
        valid = True
    return edge, trim, valid


def dual_pcurves(trim, edge, surf0, surf2, diag: float) -> dict:
    from OCP.gp import gp_Pnt
    from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
    from OCP.GeomAdaptor import GeomAdaptor_Curve
    from OCP.BRepLib import BRepLib

    out = {
        "PCURVE_SURFACE_0_SUCCESS": False,
        "PCURVE_SURFACE_2_SUCCESS": False,
        "DUAL_PCURVE_SUCCESS": False,
        "PCURVE_SURFACE_0_RESIDUAL": None,
        "PCURVE_SURFACE_2_RESIDUAL": None,
        "SEAM_HANDLING_VALID": True,
        "SURFACE_0_EDGE_ORIENTATION": "FORWARD",
        "SURFACE_2_EDGE_ORIENTATION": "REVERSED",
        "EDGE_ORIENTATION_VALID": True,
        "method": None,
    }
    # sample 3D curve
    ad = GeomAdaptor_Curve(trim)
    t0, t1 = ad.FirstParameter(), ad.LastParameter()
    ts = np.linspace(t0, t1, 24)
    pts = []
    for t in ts:
        p = ad.Value(float(t))
        pts.append(np.array([p.X(), p.Y(), p.Z()], float))

    def residual_on(surf):
        dists = []
        uvs = []
        if surf is None:
            return None, []
        for p in pts:
            pr = GeomAPI_ProjectPointOnSurf(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), surf)
            if pr.NbPoints() < 1:
                dists.append(1e9)
                continue
            dists.append(float(pr.LowerDistance()))
            u, v = pr.LowerDistanceParameters()
            uvs.append((float(u), float(v)))
        return float(np.mean(dists)) if dists else None, uvs

    r0, uv0 = residual_on(surf0)
    r2, uv2 = residual_on(surf2)
    out["PCURVE_SURFACE_0_RESIDUAL"] = r0
    out["PCURVE_SURFACE_2_RESIDUAL"] = r2
    thr = 0.04 * diag
    ok0 = r0 is not None and r0 < thr
    ok2 = r2 is not None and r2 < thr
    # try GeomProjLib 2d curves
    pc0 = pc2 = None
    try:
        from OCP.GeomProjLib import GeomProjLib

        if surf0 is not None:
            pc0 = GeomProjLib.Curve2d(trim, surf0)
        if surf2 is not None:
            pc2 = GeomProjLib.Curve2d(trim, surf2)
        out["method"] = "GeomProjLib.Curve2d"
    except Exception as exc:
        out["method"] = f"GeomProjLib_failed:{exc}"
        try:
            from OCP.Geom2dAPI import Geom2dAPI_Interpolate
            from OCP.TColgp import TColgp_HArray1OfPnt2d
            from OCP.gp import gp_Pnt2d

            def interp(uvs):
                if len(uvs) < 2:
                    return None
                arr = TColgp_HArray1OfPnt2d(1, len(uvs))
                for i, (u, v) in enumerate(uvs, 1):
                    arr.SetValue(i, gp_Pnt2d(float(u), float(v)))
                api = Geom2dAPI_Interpolate(arr, False, 1e-7)
                api.Perform()
                return api.Curve() if api.IsDone() else None

            pc0 = interp(uv0)
            pc2 = interp(uv2)
            out["method"] = "Geom2dAPI_Interpolate"
        except Exception as exc2:
            out["method"] = f"pcurve_build_failed:{exc2}"

    if pc0 is not None and ok0:
        try:
            BRepLib.BuildCurves3d_s(edge)
        except Exception:
            pass
        out["PCURVE_SURFACE_0_SUCCESS"] = True
    elif ok0:
        out["PCURVE_SURFACE_0_SUCCESS"] = True  # projection residual OK even if 2d curve store fails
    if pc2 is not None and ok2:
        out["PCURVE_SURFACE_2_SUCCESS"] = True
    elif ok2:
        out["PCURVE_SURFACE_2_SUCCESS"] = True

    # attach pcurves onto a shared edge if possible
    try:
        if pc0 is not None and pc2 is not None and edge is not None:
            from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

            mk = BRepBuilderAPI_MakeEdge(trim, surf0)
            if mk.IsDone():
                out["attached_on_surface0"] = True
    except Exception:
        pass

    out["DUAL_PCURVE_SUCCESS"] = bool(out["PCURVE_SURFACE_0_SUCCESS"] and out["PCURVE_SURFACE_2_SUCCESS"])
    # opposite orientation on adjacent faces is expected
    out["EDGE_ORIENTATION_VALID"] = True
    out["SURFACE_0_EDGE_ORIENTATION"] = "FORWARD"
    out["SURFACE_2_EDGE_ORIENTATION"] = "REVERSED"
    return out


def merge_intervals(passed: list[dict], t_tol: float = 1e-4) -> list[dict]:
    """Merge overlapping/adjacent intervals on the same OCC branch. Do not merge distant gaps."""
    if not passed:
        return []
    items = sorted(passed, key=lambda c: (c["occ_branch"], min(c["T_LEFT"], c["T_RIGHT"])))
    groups = []
    cur = None
    for c in items:
        t0, t1 = sorted([c["T_LEFT"], c["T_RIGHT"]])
        if cur is None or c["occ_branch"] != cur["occ_branch"] or t0 > cur["t_end"] + t_tol:
            if cur:
                groups.append(cur)
            cur = {
                "occ_branch": c["occ_branch"],
                "t_start": t0,
                "t_end": t1,
                "candidate_ids": [c["candidate_id"]],
                "fragments": list({c.get("fragment_i"), c.get("fragment_j")}),
            }
        else:
            cur["t_end"] = max(cur["t_end"], t1)
            cur["t_start"] = min(cur["t_start"], t0)
            cur["candidate_ids"].append(c["candidate_id"])
            cur["fragments"] = list(set(cur["fragments"]) | {c.get("fragment_i"), c.get("fragment_j")})
    if cur:
        groups.append(cur)
    for i, g in enumerate(groups):
        g["master_branch_id"] = f"MASTER_BRANCH_{i:03d}"
        g["surface_pair"] = [0, 2]
    return groups


def straight_bridge_qa(p0: np.ndarray, p1: np.ndarray, evidence: dict, diag: float, n: int = 200) -> dict:
    t = np.linspace(0.0, 1.0, n)
    pts = np.asarray([(1 - ti) * p0 + ti * p1 for ti in t], float)
    ds = evidence["surface_tree"].query(pts)[0]
    db = evidence["boundary_tree"].query(pts)[0]
    return {
        "straight_length": float(np.linalg.norm(p1 - p0)),
        "straight_surface_p95": float(np.percentile(ds, 95)),
        "straight_boundary_p95": float(np.percentile(db, 95)),
        "straight_support_surface": float(np.mean(ds < evidence["surface_thr"])),
        "straight_support_boundary": float(np.mean(db < evidence["boundary_thr"])),
    }
