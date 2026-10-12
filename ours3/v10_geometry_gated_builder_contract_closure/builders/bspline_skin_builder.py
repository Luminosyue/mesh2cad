"""Semantic skin / general / periodic BSpline builders share grid+control-net guards."""
from __future__ import annotations

from typing import Any

import numpy as np

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_Sewing
from OCP.GeomAPI import GeomAPI_PointsToBSpline
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.gp import gp_Pnt

from builders import occ_api
from builders.control_net_guard import audit_control_net
from builders.post_build_guard import post_build_guard
from builders.preflight import grid_preflight, loft_preflight
from builders.profiles import extract_profiles


def _curve(points):
    arr = TColgp_Array1OfPnt(1, len(points))
    for i, pnt in enumerate(points, 1):
        arr.SetValue(i, gp_Pnt(*map(float, pnt)))
    fit = GeomAPI_PointsToBSpline(arr)
    if not fit.IsDone():
        raise RuntimeError("curve fit failed")
    return fit.Curve()


def execute(mesh, plan: dict[str, Any], part_bbox: dict[str, Any], guard_cfg: dict[str, Any], counters: dict[str, int], extracted=None) -> dict[str, Any]:
    counters["BSPLINE_REQUEST"] = counters.get("BSPLINE_REQUEST", 0) + 1
    count = int(plan.get("profile_count") or 10)
    if count % 2:
        count += 1
    extracted = extracted or extract_profiles(mesh, int(plan.get("sections") or 10), count)
    pre = loft_preflight(extracted, part_bbox["bbox_diag"], guard_cfg)
    if not pre["LOFT_PREFLIGHT_PASS"]:
        counters["LOFT_PREFLIGHT_FAIL"] = counters.get("LOFT_PREFLIGHT_FAIL", 0) + 1
        counters["BSPLINE_GRID_PREFLIGHT_FAIL"] = counters.get("BSPLINE_GRID_PREFLIGHT_FAIL", 0) + 1
        return {"executed": False, "rejected_stage": "PREFLIGHT", "preflight": pre, "shape": None}
    ai = extracted["axis_index"]
    plane = [i for i in range(3) if i != ai]
    grid = []
    for coordinate, uv in zip(extracted["stations"], extracted["profiles_uv"]):
        pts = np.zeros((len(uv), 3))
        pts[:, ai] = coordinate
        pts[:, plane] = uv
        grid.append(pts)
    grid = np.asarray(grid)
    half = count // 2
    upper = grid[:, : half + 1]
    lower = np.concatenate([grid[:, half:], grid[:, :1]], axis=1)
    faces = []
    for patch in (upper, lower):
        gpre = grid_preflight(patch, guard_cfg, part_bbox["bbox_diag"])
        if not gpre["BSPLINE_GRID_PREFLIGHT_PASS"]:
            counters["BSPLINE_GRID_PREFLIGHT_FAIL"] = counters.get("BSPLINE_GRID_PREFLIGHT_FAIL", 0) + 1
            return {"executed": False, "rejected_stage": "GRID_PREFLIGHT", "grid": gpre, "shape": None}
        try:
            surf = occ_api.points_to_bspline_surface(patch, float(plan.get("tolerance") or 0.001), grid_preflight_passed=True)
        except Exception as exc:
            return {"executed": False, "rejected_stage": "OCC", "error": f"{type(exc).__name__}: {exc}", "shape": None}
        poles = occ_api.poles_of(surf)
        cnet = audit_control_net(poles, part_bbox, extracted["PROFILE_SUPPORT_BBOX"], guard_cfg)
        if cnet["BSPLINE_CONTROL_NET_REJECTED"]:
            counters["CONTROL_NET_GUARD_FAIL"] = counters.get("CONTROL_NET_GUARD_FAIL", 0) + 1
            return {"executed": False, "rejected_stage": "CONTROL_NET", "control_net": cnet, "shape": None, "BSPLINE_CONTROL_NET_REJECTED": True}
        try:
            faces.append(occ_api.make_face_from_surface(surf, control_net_passed=True))
        except Exception as exc:
            return {"executed": False, "rejected_stage": "FACE", "error": f"{type(exc).__name__}: {exc}", "shape": None}
    sew = BRepBuilderAPI_Sewing(1e-5)
    for face in faces:
        sew.Add(face)
    for k in (0, -1):
        wire = BRepBuilderAPI_MakeWire()
        wire.Add(BRepBuilderAPI_MakeEdge(_curve(upper[k])).Edge())
        wire.Add(BRepBuilderAPI_MakeEdge(_curve(lower[k])).Edge())
        if wire.IsDone():
            cap = BRepBuilderAPI_MakeFace(wire.Wire(), True)
            if cap.IsDone():
                sew.Add(cap.Face())
    sew.Perform()
    shape = sew.SewedShape()
    post = post_build_guard(shape, part_bbox, extracted["PROFILE_SUPPORT_BBOX"], guard_cfg)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT"] = counters.get("POST_BUILD_REJECT", 0) + 1
        return {"executed": True, "rejected_stage": "POST_BUILD", "BUILDER_OUTPUT_REJECTED": True, "post": post, "shape": None}
    return {"executed": True, "rejected_stage": None, "shape": shape, "post": post, "extracted": extracted}
