"""Deterministic structured plans from eligibility + catalog. Not Qwen, not fallback-as-success."""
from __future__ import annotations

from typing import Any

from design_plan.schema import BUILDER_REQUIRED_REFS, PLAN_VERSION


def _plan(part_id: str, builder: str, refs: dict[str, Any], source: str, summary: str) -> dict[str, Any]:
    return {
        "plan_version": PLAN_VERSION,
        "part_id": part_id,
        "construction_family": builder,
        "builder": builder,
        "builder_eligibility_ref": f"BUILDER_ELIGIBILITY.{builder}",
        "geometry_refs": refs,
        "topology_refs": {},
        "feature_refs": {},
        "execution_options": {"occ_tolerance": 1e-6},
        "reasoning_summary": summary,
        "confidence": 0.7,
        "CANDIDATE_SOURCE": source,
    }


def _has(catalog, *refs) -> bool:
    entries = catalog["entries"]
    return all(r in entries for r in refs)


def geometry_alternative_plans(part_id: str, eligibility: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    allowed = eligibility.get("ALLOWED_BUILDERS") or []
    plans = []
    if "EXTRUSION" in allowed and _has(catalog, "MEASURED_SPEC.PROFILES.CLOSED_LOOP_EXTRUSION", "MEASURED_SPEC.AXES.AXIS_001.direction", "MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION.depth"):
        plans.append(_plan(part_id, "EXTRUSION", {
            "profile_ref": "MEASURED_SPEC.PROFILES.CLOSED_LOOP_EXTRUSION",
            "direction_ref": "MEASURED_SPEC.AXES.AXIS_001.direction",
            "depth_ref": "MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION.depth",
        }, "GEOMETRY_ALTERNATIVE", "Approximately constant section supports extrusion from measured hull and depth."))
    if "LOFT" in allowed:
        prefs = sorted(r for r in catalog["entries"] if r.startswith("MEASURED_SPEC.PROFILES.PROFILE_") and r.split("_")[-1].isdigit())
        srefs = sorted(r for r in catalog["entries"] if r.startswith("MEASURED_SPEC.STATIONS.STATION_"))
        if len(prefs) >= 4 and len(srefs) >= 4 and "MEASURED_SPEC.CORRESPONDENCE.ALIGNED_CYCLIC" in catalog["entries"]:
            plans.append(_plan(part_id, "LOFT", {
                "profile_refs": prefs,
                "station_refs": srefs,
                "correspondence_ref": "MEASURED_SPEC.CORRESPONDENCE.ALIGNED_CYCLIC",
            }, "GEOMETRY_ALTERNATIVE", "Ordered measured stations support a loft."))
    if "CYLINDER" in allowed and _has(catalog, "MEASURED_SPEC.AXES.AXIS_CYLINDER", "MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.radius", "MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.height"):
        plans.append(_plan(part_id, "CYLINDER", {
            "axis_ref": "MEASURED_SPEC.AXES.AXIS_CYLINDER",
            "radius_ref": "MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.radius",
            "height_ref": "MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.height",
        }, "PRIMITIVE_BANK", "Radial consistency supports a measured cylinder."))
    if "PLANE" in allowed and _has(catalog, "MEASURED_SPEC.AXES.PLANE_ORIGIN", "MEASURED_SPEC.AXES.PLANE_NORMAL", "MEASURED_SPEC.SUPPORT.PART_BBOX"):
        plans.append(_plan(part_id, "PLANE", {
            "origin_ref": "MEASURED_SPEC.AXES.PLANE_ORIGIN",
            "normal_ref": "MEASURED_SPEC.AXES.PLANE_NORMAL",
            "support_ref": "MEASURED_SPEC.SUPPORT.PART_BBOX",
        }, "PRIMITIVE_BANK", "Planar support from measured bbox."))
    if "GENERAL_BSPLINE" in allowed and _has(catalog, "MEASURED_SPEC.SURFACE_PRIMITIVES.GRID_FROM_PROFILES", "MEASURED_SPEC.SUPPORT.PART_BBOX", "MEASURED_SPEC.PARAMETERIZATION.UNIFORM_UV"):
        plans.append(_plan(part_id, "GENERAL_BSPLINE", {
            "surface_grid_ref": "MEASURED_SPEC.SURFACE_PRIMITIVES.GRID_FROM_PROFILES",
            "support_ref": "MEASURED_SPEC.SUPPORT.PART_BBOX",
            "parameterization_ref": "MEASURED_SPEC.PARAMETERIZATION.UNIFORM_UV",
        }, "GEOMETRY_ALTERNATIVE", "Ordered profile grid supports a bounded BSpline."))
    return plans


def open_shell_plan(part_id: str) -> dict[str, Any]:
    return _plan(part_id, "OPEN_SHELL", {
        "surface_refs": ["MEASURED_SPEC.SURFACE_PRIMITIVES.TAIL_OPEN_SHELL"],
        "master_boundary_refs": ["MEASURED_SPEC.MASTER_BOUNDARIES.BOUNDARY_000"],
        "wireframe_refs": ["MEASURED_SPEC.WIREFRAME.TAIL_MASTER"],
    }, "PRIMITIVE_BANK", "V7D3 master-boundary topology should not be rebuilt as a generic BSpline.")


def invalid_loft_probe(part_id: str) -> dict[str, Any]:
    return _plan(part_id, "LOFT", {
        "profile_refs": ["MEASURED_SPEC.PROFILES.PROFILE_000", "MEASURED_SPEC.PROFILES.PROFILE_001"],
        "station_refs": ["MEASURED_SPEC.STATIONS.STATION_000", "MEASURED_SPEC.STATIONS.STATION_001"],
        "correspondence_ref": "MEASURED_SPEC.CORRESPONDENCE.ALIGNED_CYCLIC",
    }, "QWEN_PLAN", "Qwen requested loft despite invalid geometry family.")


__all__ = ["geometry_alternative_plans", "open_shell_plan", "invalid_loft_probe", "BUILDER_REQUIRED_REFS"]
