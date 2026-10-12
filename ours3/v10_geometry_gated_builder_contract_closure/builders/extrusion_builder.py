"""ExtrusionBuilder from measured extents. Depth must come from spec refs, not Qwen literals."""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial import ConvexHull

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec

from builders import occ_api
from builders.post_build_guard import post_build_guard


def execute(mesh, plan: dict[str, Any], part_bbox: dict[str, Any], guard_cfg: dict[str, Any], counters: dict[str, int], spec: dict[str, Any] | None = None) -> dict[str, Any]:
    counters["EXTRUSION_REQUEST"] = counters.get("EXTRUSION_REQUEST", 0) + 1
    ai = int(np.argmax(mesh.extents))
    if spec and spec.get("longitudinal_axis_index") is not None:
        ai = int(spec["longitudinal_axis_index"])
    plane = [i for i in range(3) if i != ai]
    vertices = np.asarray(mesh.vertices, float)
    uv = np.unique(np.round(vertices[:, plane], 9), axis=0)
    hull = uv[ConvexHull(uv).vertices]
    while len(hull) > 16:
        costs = [abs(np.cross(hull[i] - hull[i - 1], hull[(i + 1) % len(hull)] - hull[i - 1])) for i in range(len(hull))]
        hull = np.delete(hull, int(np.argmin(costs)), axis=0)
    lo, hi = mesh.bounds[:, ai]
    if spec and spec.get("extents"):
        depth = float(spec["extents"][ai])
        mid = 0.5 * (lo + hi)
        lo, hi = mid - 0.5 * depth, mid + 0.5 * depth
    pts = np.zeros((len(hull), 3))
    pts[:, ai] = lo
    pts[:, plane] = hull
    face = BRepBuilderAPI_MakeFace(occ_api.polygon_wire(pts), True)
    vec = np.zeros(3)
    vec[ai] = hi - lo
    shape = BRepPrimAPI_MakePrism(face.Face(), gp_Vec(*map(float, vec)), True).Shape()
    support = {"bbox_min": np.asarray(mesh.bounds[0]).tolist(), "bbox_max": np.asarray(mesh.bounds[1]).tolist(), "bbox_diag": float(np.linalg.norm(mesh.extents))}
    post = post_build_guard(shape, part_bbox, support, guard_cfg)
    if post["BUILDER_OUTPUT_REJECTED"]:
        counters["POST_BUILD_REJECT"] = counters.get("POST_BUILD_REJECT", 0) + 1
        return {"executed": True, "rejected_stage": "POST_BUILD", "BUILDER_OUTPUT_REJECTED": True, "post": post, "shape": None}
    return {"executed": True, "rejected_stage": None, "shape": shape, "post": post}
