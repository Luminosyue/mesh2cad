"""Geometry-gated builders. OCC ThruSections / BSpline surface only via occ_api."""
from __future__ import annotations

from typing import Any

import numpy as np
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Vec
from scipy.spatial import ConvexHull

from builders import occ_api
from builders.control_net_guard import audit_control_net
from builders.post_build_guard import post_build_guard
from builders.preflight import grid_preflight, loft_preflight
from builders.profiles import extract_profiles, polygon_wire_points


def polygon_wire_points(points):
    return occ_api.polygon_wire(points)


def _part_bbox(mesh) -> dict:
    lo, hi = np.asarray(mesh.bounds[0], float), np.asarray(mesh.bounds[1], float)
    return {"bbox_min": lo.tolist(), "bbox_max": hi.tolist(), "bbox_diag": float(np.linalg.norm(hi - lo))}


class BuilderRejected(Exception):
    def __init__(self, stage: str, payload: dict[str, Any]):
        super().__init__(stage)
        self.stage = stage
        self.payload = payload


def loft_builder(mesh, guards: dict[str, Any], counters: dict[str, int], extracted=None):
    part = _part_bbox(mesh)
    extracted = extracted or extract_profiles(mesh, 10, 10)
    pre = loft_preflight(extracted, part["bbox_diag"], guards)
    if not pre["LOFT_PREFLIGHT_PASS"]:
        counters["LOFT_PREFLIGHT_FAIL_COUNT"] += 1
        raise BuilderRejected("LOFT_PREFLIGHT", pre)
    ai = extracted["axis_index"]
    plane = [i for i in range(3) if i != ai]
    wires = []
    for coordinate, uv in zip(extracted["stations"], extracted["profiles_uv"]):
        pts = np.zeros((len(uv), 3))
        pts[:, ai] = coordinate
        pts[:, plane] = uv
        wires.append(occ_api.polygon_wire(pts))
    shape = occ_api.thru_sections(wires, preflight_passed=True)
    post = post_build_guard(shape, part, extracted["PROFILE_SUPPORT_BBOX"], guards)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT_COUNT"] += 1
        raise BuilderRejected("POST_BUILD", post)
    return shape, {"preflight": pre, "post": post, "extracted": extracted}


def _skin_grids(extracted) -> tuple[np.ndarray, np.ndarray]:
    grid = np.asarray(extracted["profiles_xyz"], float)
    count = grid.shape[1]
    if count % 2:
        count -= 1
        grid = grid[:, :count]
    half = count // 2
    upper = grid[:, : half + 1]
    lower = np.concatenate([grid[:, half:], grid[:, :1]], axis=1)
    return upper, lower


def bspline_skin_builder(mesh, guards: dict[str, Any], counters: dict[str, int], extracted=None, tolerance=0.001):
    part = _part_bbox(mesh)
    extracted = extracted or extract_profiles(mesh, 10, 10)
    pre = loft_preflight(extracted, part["bbox_diag"], guards)
    if not pre["LOFT_PREFLIGHT_PASS"]:
        counters["LOFT_PREFLIGHT_FAIL_COUNT"] += 1
        counters["BSPLINE_GRID_PREFLIGHT_FAIL_COUNT"] += 1
        raise BuilderRejected("LOFT_PREFLIGHT", pre)
    upper, lower = _skin_grids(extracted)
    faces = []
    for grid in (upper, lower):
        gpre = grid_preflight(grid, guards, part["bbox_diag"])
        if not gpre["BSPLINE_GRID_PREFLIGHT_PASS"]:
            counters["BSPLINE_GRID_PREFLIGHT_FAIL_COUNT"] += 1
            raise BuilderRejected("BSPLINE_GRID_PREFLIGHT", gpre)
        surface = occ_api.points_to_bspline_surface(grid, tolerance, grid_preflight_passed=True)
        poles = occ_api.poles_of(surface)
        cnet = audit_control_net(poles, part, extracted["PROFILE_SUPPORT_BBOX"], guards)
        if cnet["BSPLINE_CONTROL_NET_REJECTED"]:
            counters["CONTROL_NET_GUARD_FAIL_COUNT"] += 1
            raise BuilderRejected("CONTROL_NET", cnet)
        faces.append(occ_api.make_face_from_surface(surface, control_net_passed=True))
    sew = BRepBuilderAPI_Sewing(1e-5)
    for face in faces:
        sew.Add(face)
    sew.Perform()
    shape = sew.SewedShape()
    post = post_build_guard(shape, part, extracted["PROFILE_SUPPORT_BBOX"], guards)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT_COUNT"] += 1
        raise BuilderRejected("POST_BUILD", post)
    return shape, {"preflight": pre, "post": post, "extracted": extracted}


def extrusion_builder(mesh, guards: dict[str, Any], counters: dict[str, int], max_vertices=16):
    part = _part_bbox(mesh)
    ai = int(np.argmax(mesh.extents))
    plane = [i for i in range(3) if i != ai]
    vertices = np.asarray(mesh.vertices, float)
    uv = np.unique(np.round(vertices[:, plane], 9), axis=0)
    hull = uv[ConvexHull(uv).vertices]
    while len(hull) > max_vertices:
        costs = [abs(np.cross(hull[i] - hull[i - 1], hull[(i + 1) % len(hull)] - hull[i - 1])) for i in range(len(hull))]
        hull = np.delete(hull, int(np.argmin(costs)), axis=0)
    lo, hi = mesh.bounds[:, ai]
    pts = np.zeros((len(hull), 3))
    pts[:, ai] = lo
    pts[:, plane] = hull
    face = BRepBuilderAPI_MakeFace(occ_api.polygon_wire(pts), True)
    vec = np.zeros(3)
    vec[ai] = hi - lo
    shape = BRepPrimAPI_MakePrism(face.Face(), gp_Vec(*map(float, vec)), True).Shape()
    post = post_build_guard(shape, part, part, guards)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT_COUNT"] += 1
        raise BuilderRejected("POST_BUILD", post)
    return shape, {"post": post}
