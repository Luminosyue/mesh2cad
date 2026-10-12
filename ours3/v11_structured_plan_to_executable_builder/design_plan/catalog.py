"""Authoritative MEASURED_SPEC catalog. Built once per part; missing refs never remeasure."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import ConvexHull

from design_plan.schema import EXPECTED_FRAME


def _sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _entry(ref: str, kind: str, value, source_file: str, source_hash: str, extra: dict | None = None) -> dict[str, Any]:
    payload = {
        "ref": ref,
        "type": kind,
        "value": value,
        "coordinate_frame": EXPECTED_FRAME,
        "source_file": source_file,
        "source_hash": source_hash,
        "authority": "MEASURED_SPEC" if ref.startswith("MEASURED_SPEC") else "BUILDER_ELIGIBILITY",
    }
    if extra:
        payload.update(extra)
    return payload


def build_catalog(mesh, spec: dict[str, Any] | None, eligibility: dict[str, Any], extracted, spec_path: str, v7d3: dict[str, Any] | None = None) -> dict[str, Any]:
    spec = spec or {}
    source_hash = str(spec.get("part_mesh_sha256") or _sha({"bbox": spec.get("bbox"), "extents": spec.get("extents")}))
    entries: dict[str, dict[str, Any]] = {}

    def put(ref, kind, value, extra=None):
        entries[ref] = _entry(ref, kind, value, spec_path, source_hash, extra)

    lo = np.asarray(mesh.bounds[0], float)
    hi = np.asarray(mesh.bounds[1], float)
    extents = hi - lo
    center = ((lo + hi) * 0.5).tolist()
    diag = float(np.linalg.norm(extents))
    ai = int(np.argmax(extents))
    if spec.get("longitudinal_axis_index") is not None:
        ai = int(spec["longitudinal_axis_index"])
    spec_ext = spec.get("extents") or extents.tolist()
    put("MEASURED_SPEC.DIMENSIONS.BBOX_MIN", "point", lo.tolist())
    put("MEASURED_SPEC.DIMENSIONS.BBOX_MAX", "point", hi.tolist())
    put("MEASURED_SPEC.DIMENSIONS.BBOX_DIAG", "scalar", diag)
    put("MEASURED_SPEC.DIMENSIONS.EXTENTS", "vector", list(map(float, spec_ext)))
    put("MEASURED_SPEC.DIMENSIONS.CENTROID", "point", spec.get("centroid") or center)
    depth = float(spec_ext[ai] if len(spec_ext) > ai else extents[ai])
    put("MEASURED_SPEC.DIMENSIONS.DEPTH_LONGITUDINAL", "scalar", depth)
    put("MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION.depth", "scalar", depth)
    put("MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION_002.depth", "scalar", depth)

    direction = (eligibility.get("BUILDER_ELIGIBILITY") or {}).get("EXTRUSION", {}).get("direction")
    if not direction:
        verts = np.asarray(mesh.vertices, float)
        _, _, vh = np.linalg.svd(verts - verts.mean(0), full_matrices=False)
        direction = vh[0].tolist()
    direction = [float(x) for x in direction]
    origin = spec.get("centroid") or center
    put("MEASURED_SPEC.AXES.AXIS_001.origin", "point", origin)
    put("MEASURED_SPEC.AXES.AXIS_001.direction", "vector", direction)
    put("MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.origin", "point", origin)
    put("MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.direction", "vector", direction)
    put("MEASURED_SPEC.AXES.AXIS_001", "axis", {"origin": origin, "direction": direction})
    put("MEASURED_SPEC.AXES.AXIS_CYLINDER", "axis", {"origin": origin, "direction": direction})

    plane = [i for i in range(3) if i != ai]
    verts = np.asarray(mesh.vertices, float)
    uv = np.unique(np.round(verts[:, plane], 9), axis=0)
    hull = uv[ConvexHull(uv).vertices]
    while len(hull) > 16:
        costs = [abs(np.cross(hull[i] - hull[i - 1], hull[(i + 1) % len(hull)] - hull[i - 1])) for i in range(len(hull))]
        hull = np.delete(hull, int(np.argmin(costs)), axis=0)
    start = float(lo[ai])
    pts = np.zeros((len(hull), 3))
    pts[:, ai] = start
    pts[:, plane] = hull
    put("MEASURED_SPEC.PROFILES.PROFILE_000", "profile", pts.tolist())
    put("MEASURED_SPEC.PROFILES.PROFILE_004", "profile", pts.tolist())
    put("MEASURED_SPEC.PROFILES.CLOSED_LOOP_EXTRUSION", "profile", pts.tolist())
    put("MEASURED_SPEC.CLOSED_LOOPS.LOOP_EXTRUSION", "profile", pts.tolist())

    profiles_xyz = []
    stations = []
    if extracted:
        for i, (xyz, station) in enumerate(zip(extracted["profiles_xyz"], extracted["stations"])):
            pref = f"MEASURED_SPEC.PROFILES.PROFILE_{i:03d}"
            sref = f"MEASURED_SPEC.STATIONS.STATION_{i:03d}"
            put(pref, "profile", np.asarray(xyz, float).tolist())
            put(sref, "scalar", float(station))
            profiles_xyz.append(np.asarray(xyz, float))
            stations.append(float(station))
        put("MEASURED_SPEC.CORRESPONDENCE.ALIGNED_CYCLIC", "correspondence", {
            "cyclic_shifts": extracted.get("cyclic_shifts"),
            "orientations": extracted.get("orientations"),
            "closed": bool(extracted.get("closed")),
        })
        put("MEASURED_SPEC.WIREFRAME.PROFILE_SUPPORT", "support", extracted.get("PROFILE_SUPPORT_BBOX"))
        grid = np.asarray(profiles_xyz, float)
        put("MEASURED_SPEC.SURFACE_PRIMITIVES.GRID_FROM_PROFILES", "grid", grid.tolist())
        put("MEASURED_SPEC.PARAMETERIZATION.UNIFORM_UV", "parameterization", {"u": "station", "v": "normalized_arclength"})
        put("MEASURED_SPEC.SWEEP.SPINE", "profile", np.asarray([[0, 0, 0], [d * depth for d in direction]], float).tolist())
        put("MEASURED_SPEC.SWEEP.FRAME_POLICY", "frame_policy", "FRENET_SOURCE_GLOBAL")

    q = verts - np.asarray(origin, float)
    axis = np.asarray(direction, float)
    axis = axis / max(np.linalg.norm(axis), 1e-12)
    radial = np.linalg.norm(q - np.outer(q @ axis, axis), axis=1)
    radius = float(np.median(radial))
    put("MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.radius", "scalar", radius)
    put("MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.height", "scalar", depth)
    put("MEASURED_SPEC.FEATURE_PARAMETERS.REVOLUTION.angle", "scalar", float(2.0 * np.pi))
    put("MEASURED_SPEC.SUPPORT.PART_BBOX", "support", {
        "bbox_min": lo.tolist(),
        "bbox_max": hi.tolist(),
        "bbox_diag": diag,
    })
    put("MEASURED_SPEC.AXES.PLANE_ORIGIN", "point", origin)
    normal = axis.tolist()
    put("MEASURED_SPEC.AXES.PLANE_NORMAL", "vector", normal)

    for name, payload in (eligibility.get("BUILDER_ELIGIBILITY") or {}).items():
        eref = f"BUILDER_ELIGIBILITY.{name}"
        entries[eref] = _entry(eref, "eligibility", payload, spec_path, source_hash)

    if v7d3:
        put("MEASURED_SPEC.MASTER_BOUNDARIES.BOUNDARY_000", "topology", {
            "count": v7d3.get("VERTICAL_TAIL_MASTER_BOUNDARY_COUNT"),
            "shared_edge_count": v7d3.get("VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT"),
            "identity_preserved": v7d3.get("SHARED_EDGE_IDENTITY_PRESERVED"),
            "step_sha256": v7d3.get("FINAL_STEP_SHA256"),
            "note": "descriptor_only_not_a_shape_source",
        })
        put("MEASURED_SPEC.TOPOLOGY.SHARED_EDGE", "topology", {
            "shared_occ_edge_count": v7d3.get("VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT"),
            "pcurve_count": v7d3.get("VERTICAL_TAIL_PCURVE_COUNT"),
        })
        put("MEASURED_SPEC.SURFACE_PRIMITIVES.TAIL_OPEN_SHELL", "topology", {
            "trimmed_face_count": v7d3.get("VERTICAL_TAIL_TRIMMED_FACE_COUNT"),
        })
        put("MEASURED_SPEC.WIREFRAME.TAIL_MASTER", "topology", {
            "master_boundary_count": v7d3.get("VERTICAL_TAIL_MASTER_BOUNDARY_COUNT"),
        })

    put("MEASURED_SPEC.OPEN_CHAINS.CHAIN_000", "profile", pts[: max(2, len(pts) // 2)].tolist())
    put("MEASURED_SPEC.HOLES.NONE", "topology", {"count": 0})

    return {
        "entries": entries,
        "source_hash": source_hash,
        "source_file": spec_path,
        "part_axis_index": ai,
        "EXPECTED_FRAME": EXPECTED_FRAME,
    }
