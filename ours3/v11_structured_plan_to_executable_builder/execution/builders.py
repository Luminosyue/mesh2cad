"""V11 builders consume resolved references only. OCC ThruSections/BSpline via V10 occ_api."""
from __future__ import annotations

from typing import Any

import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol
from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Vec

from builders import occ_api
from builders.control_net_guard import audit_control_net
from builders.post_build_guard import post_build_guard
from builders.preflight import grid_preflight, loft_preflight


def _val(resolved, key):
    return resolved["resolved"][key]["value"]


def _consumed(resolved, keys):
    rows = []
    for item in resolved.get("provenance") or []:
        if item["PARAMETER_NAME"] in keys:
            rows.append(item)
    return rows


def extrusion(resolved, part_bbox, guard_cfg, counters):
    counters["EXTRUSION_REQUEST"] = counters.get("EXTRUSION_REQUEST", 0) + 1
    profile = np.asarray(_val(resolved, "profile_ref"), float)
    direction = np.asarray(_val(resolved, "direction_ref"), float)
    depth = float(_val(resolved, "depth_ref"))
    direction = direction / max(np.linalg.norm(direction), 1e-12)
    face = BRepBuilderAPI_MakeFace(occ_api.polygon_wire(profile), True)
    shape = BRepPrimAPI_MakePrism(face.Face(), gp_Vec(*(direction * depth)), True).Shape()
    return _finish(shape, part_bbox, guard_cfg, counters, resolved, ["profile_ref", "direction_ref", "depth_ref"])


def loft(resolved, part_bbox, guard_cfg, counters):
    counters["LOFT_REQUEST"] = counters.get("LOFT_REQUEST", 0) + 1
    profiles = [np.asarray(p, float) for p in _val(resolved, "profile_refs")]
    stations = [float(s) for s in _val(resolved, "station_refs")]
    stacked = np.vstack(profiles)
    ai = int(np.argmax(stacked.max(0) - stacked.min(0)))
    plane = [i for i in range(3) if i != ai]
    uv = [row[:, plane] for row in profiles]
    extracted = {
        "profiles_uv": uv,
        "stations": stations,
        "cyclic_shifts": (_val(resolved, "correspondence_ref") or {}).get("cyclic_shifts"),
        "PROFILE_SUPPORT_BBOX": part_bbox,
    }
    pre = loft_preflight(extracted, part_bbox["bbox_diag"], guard_cfg)
    if not pre["LOFT_PREFLIGHT_PASS"]:
        counters["LOFT_PREFLIGHT_FAIL"] = counters.get("LOFT_PREFLIGHT_FAIL", 0) + 1
        return {"BUILDER_EXECUTED": False, "PLAN_STATUS": "PLAN_PREFLIGHT_REJECTED", "shape": None, "preflight": pre, "consumed": []}
    wires = [occ_api.polygon_wire(p) for p in profiles]
    shape = occ_api.thru_sections(wires, preflight_passed=True)
    return _finish(shape, part_bbox, guard_cfg, counters, resolved, ["profile_refs", "station_refs", "correspondence_ref"], extra={"preflight": pre})


def cylinder(resolved, part_bbox, guard_cfg, counters):
    counters["CYLINDER_REQUEST"] = counters.get("CYLINDER_REQUEST", 0) + 1
    axis = _val(resolved, "axis_ref")
    origin = np.asarray(axis["origin"], float)
    direction = np.asarray(axis["direction"], float)
    direction = direction / max(np.linalg.norm(direction), 1e-12)
    radius = float(_val(resolved, "radius_ref"))
    height = float(_val(resolved, "height_ref"))
    ax = gp_Ax2(gp_Pnt(*map(float, origin - 0.5 * direction * height)), gp_Dir(*map(float, direction)))
    shape = BRepPrimAPI_MakeCylinder(ax, abs(radius), abs(height)).Shape()
    return _finish(shape, part_bbox, guard_cfg, counters, resolved, ["axis_ref", "radius_ref", "height_ref"])


def revolution(resolved, part_bbox, guard_cfg, counters):
    counters["REVOLUTION_REQUEST"] = counters.get("REVOLUTION_REQUEST", 0) + 1
    profile = np.asarray(_val(resolved, "profile_ref"), float)
    origin = np.asarray(_val(resolved, "axis_origin_ref"), float)
    direction = np.asarray(_val(resolved, "axis_direction_ref"), float)
    angle = float(_val(resolved, "angle_ref"))
    direction = direction / max(np.linalg.norm(direction), 1e-12)
    face = BRepBuilderAPI_MakeFace(occ_api.polygon_wire(profile), True)
    ax = gp_Ax1(gp_Pnt(*map(float, origin)), gp_Dir(*map(float, direction)))
    shape = BRepPrimAPI_MakeRevol(face.Face(), ax, angle).Shape()
    return _finish(shape, part_bbox, guard_cfg, counters, resolved, ["profile_ref", "axis_origin_ref", "axis_direction_ref", "angle_ref"])


def plane(resolved, part_bbox, guard_cfg, counters):
    counters["PLANE_REQUEST"] = counters.get("PLANE_REQUEST", 0) + 1
    origin = np.asarray(_val(resolved, "origin_ref"), float)
    normal = np.asarray(_val(resolved, "normal_ref"), float)
    support = _val(resolved, "support_ref")
    normal = normal / max(np.linalg.norm(normal), 1e-12)
    lo = np.asarray(support["bbox_min"], float)
    hi = np.asarray(support["bbox_max"], float)
    tmp = np.array([1.0, 0.0, 0.0]) if abs(normal[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(normal, tmp)
    u = u / max(np.linalg.norm(u), 1e-12)
    v = np.cross(normal, u)
    corners3 = np.array([
        [lo[0], lo[1], lo[2]], [hi[0], lo[1], lo[2]], [lo[0], hi[1], lo[2]], [hi[0], hi[1], lo[2]],
        [lo[0], lo[1], hi[2]], [hi[0], lo[1], hi[2]], [lo[0], hi[1], hi[2]], [hi[0], hi[1], hi[2]],
    ], float)
    rel = corners3 - origin
    uu = rel @ u
    vv = rel @ v
    corners = [
        origin + float(uu.min()) * u + float(vv.min()) * v,
        origin + float(uu.max()) * u + float(vv.min()) * v,
        origin + float(uu.max()) * u + float(vv.max()) * v,
        origin + float(uu.min()) * u + float(vv.max()) * v,
    ]
    face = BRepBuilderAPI_MakeFace(occ_api.polygon_wire(corners), True)
    return _finish(face.Face(), part_bbox, guard_cfg, counters, resolved, ["origin_ref", "normal_ref", "support_ref"])


def bspline(resolved, part_bbox, guard_cfg, counters):
    counters["BSPLINE_REQUEST"] = counters.get("BSPLINE_REQUEST", 0) + 1
    grid = np.asarray(_val(resolved, "surface_grid_ref"), float)
    support = _val(resolved, "support_ref")
    gpre = grid_preflight(grid, guard_cfg, part_bbox["bbox_diag"])
    if not gpre["BSPLINE_GRID_PREFLIGHT_PASS"]:
        counters["BSPLINE_GRID_PREFLIGHT_FAIL"] = counters.get("BSPLINE_GRID_PREFLIGHT_FAIL", 0) + 1
        return {"BUILDER_EXECUTED": False, "PLAN_STATUS": "PLAN_PREFLIGHT_REJECTED", "shape": None, "grid": gpre, "consumed": []}
    surf = occ_api.points_to_bspline_surface(grid, 0.001, grid_preflight_passed=True)
    poles = occ_api.poles_of(surf)
    cnet = audit_control_net(poles, part_bbox, support, guard_cfg)
    if cnet["BSPLINE_CONTROL_NET_REJECTED"]:
        counters["CONTROL_NET_GUARD_FAIL"] = counters.get("CONTROL_NET_GUARD_FAIL", 0) + 1
        return {"BUILDER_EXECUTED": False, "PLAN_STATUS": "PLAN_PREFLIGHT_REJECTED", "shape": None, "control_net": cnet, "consumed": []}
    face = occ_api.make_face_from_surface(surf, control_net_passed=True)
    return _finish(face, part_bbox, guard_cfg, counters, resolved, ["surface_grid_ref", "support_ref", "parameterization_ref"])


def _finish(shape, part_bbox, guard_cfg, counters, resolved, keys, extra=None):
    support = part_bbox
    post = post_build_guard(shape, part_bbox, support, guard_cfg)
    consumed = _consumed(resolved, keys)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT"] = counters.get("POST_BUILD_REJECT", 0) + 1
        out = {"BUILDER_EXECUTED": True, "PLAN_STATUS": "PLAN_EXECUTION_FAILED", "shape": None, "post": post, "consumed": consumed, "BUILDER_OUTPUT_REJECTED": True}
        if extra:
            out.update(extra)
        return out
    out = {"BUILDER_EXECUTED": True, "PLAN_STATUS": "PLAN_EXECUTION_SUCCESS", "shape": shape, "post": post, "consumed": consumed, "FRESH_BREP": True}
    if extra:
        out.update(extra)
    return out


DISPATCH = {
    "EXTRUSION": extrusion,
    "LOFT": loft,
    "CYLINDER": cylinder,
    "REVOLUTION": revolution,
    "PLANE": plane,
    "GENERAL_BSPLINE": bspline,
}
