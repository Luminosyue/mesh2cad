from __future__ import annotations

from copy import deepcopy
from typing import Any


def _refs(entries: dict[str, Any], prefix: str) -> list[str]:
    return sorted(key for key in entries if key.startswith(prefix))


def _first(entries: dict[str, Any], prefixes: list[str]) -> str | None:
    for prefix in prefixes:
        values = _refs(entries, prefix)
        if values:
            return values[0]
    return None


def _base(part_id: str, family: str, candidate_id: str, rationale: str) -> dict[str, Any]:
    return {
        "plan_version": "V11",
        "part_id": part_id,
        "construction_family": family,
        "builder": family,
        "builder_eligibility_ref": f"BUILDER_ELIGIBILITY.{family}",
        "geometry_refs": {},
        "topology_refs": {},
        "feature_refs": {},
        "execution_options": {"occ_tolerance": 1e-6, "max_degree": 5},
        "reasoning_summary": rationale,
        "confidence": 0.7,
        "CANDIDATE_SOURCE": "MESH2CAD_STYLE",
        "hypothesis_id": candidate_id,
    }


def adapt_to_v11(intermediate: dict[str, Any], part_id: str, eligibility: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    family = str(intermediate["construction_family"]).upper()
    allowed = set(eligibility.get("ALLOWED_BUILDERS") or [])
    if family not in allowed:
        raise ValueError(f"MESH2CAD_FAMILY_NOT_ELIGIBLE:{family}")
    entries = catalog["entries"]
    plan = _base(part_id, family, intermediate["candidate_id"], intermediate.get("rationale", ""))
    geometry = plan["geometry_refs"]
    if family == "LOFT":
        profiles = _refs(entries, "MEASURED_SPEC.PROFILES.PROFILE_")
        stations = _refs(entries, "MEASURED_SPEC.STATIONS.STATION_")
        correspondence = _first(entries, ["MEASURED_SPEC.CORRESPONDENCE."])
        if len(profiles) < 2 or len(stations) < 2 or not correspondence:
            raise ValueError("MESH2CAD_LOFT_REFS_UNAVAILABLE")
        geometry.update(profile_refs=profiles, station_refs=stations, correspondence_ref=correspondence)
    elif family == "EXTRUSION":
        profile = _first(entries, ["MEASURED_SPEC.PROFILES.CLOSED_LOOP_EXTRUSION", "MEASURED_SPEC.PROFILES.PROFILE_"])
        direction = _first(entries, ["MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.direction", "MEASURED_SPEC.AXES."])
        depth = _first(entries, ["MEASURED_SPEC.FEATURE_PARAMETERS.EXTRUSION.depth", "MEASURED_SPEC.DIMENSIONS."])
        if not all((profile, direction, depth)):
            raise ValueError("MESH2CAD_EXTRUSION_REFS_UNAVAILABLE")
        geometry.update(profile_ref=profile, direction_ref=direction, depth_ref=depth)
    elif family == "CYLINDER":
        axis = _first(entries, ["MEASURED_SPEC.AXES.AXIS_LONGITUDINAL", "MEASURED_SPEC.AXES."])
        radius = _first(entries, ["MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.radius", "MEASURED_SPEC.DIMENSIONS.radius"])
        height = _first(entries, ["MEASURED_SPEC.FEATURE_PARAMETERS.CYLINDER.height", "MEASURED_SPEC.DIMENSIONS."])
        if not all((axis, radius, height)):
            raise ValueError("MESH2CAD_CYLINDER_REFS_UNAVAILABLE")
        geometry.update(axis_ref=axis, radius_ref=radius, height_ref=height)
    elif family == "REVOLUTION":
        profile = _first(entries, ["MEASURED_SPEC.PROFILES.REVOLUTION", "MEASURED_SPEC.PROFILES.PROFILE_"])
        origin = _first(entries, ["MEASURED_SPEC.AXES.REVOLUTION.origin", "MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.origin"])
        direction = _first(entries, ["MEASURED_SPEC.AXES.REVOLUTION.direction", "MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.direction"])
        angle = _first(entries, ["MEASURED_SPEC.FEATURE_PARAMETERS.REVOLUTION.angle"])
        if not all((profile, origin, direction, angle)):
            raise ValueError("MESH2CAD_REVOLUTION_REFS_UNAVAILABLE")
        geometry.update(profile_ref=profile, axis_origin_ref=origin, axis_direction_ref=direction, angle_ref=angle)
    elif family == "GENERAL_BSPLINE":
        grid = _first(entries, ["MEASURED_SPEC.SURFACE_GRIDS.", "MEASURED_SPEC.CONTROL_NETS."])
        support = _first(entries, ["MEASURED_SPEC.SUPPORT.", "MEASURED_SPEC.SURFACE_PRIMITIVES."])
        parameterization = _first(entries, ["MEASURED_SPEC.PARAMETERIZATION.", "MEASURED_SPEC.CORRESPONDENCE."])
        if not all((grid, support, parameterization)):
            raise ValueError("MESH2CAD_BSPLINE_REFS_UNAVAILABLE")
        geometry.update(surface_grid_ref=grid, support_ref=support, parameterization_ref=parameterization)
    elif family == "PERIODIC_BSPLINE":
        grid = _first(entries, ["MEASURED_SPEC.PERIODIC_SURFACE_GRIDS.", "MEASURED_SPEC.SURFACE_GRIDS."])
        direction = _first(entries, ["MEASURED_SPEC.PERIODIC_DIRECTION.", "MEASURED_SPEC.AXES.AXIS_LONGITUDINAL.direction"])
        support = _first(entries, ["MEASURED_SPEC.SUPPORT.", "MEASURED_SPEC.SURFACE_PRIMITIVES."])
        if not all((grid, direction, support)):
            raise ValueError("MESH2CAD_PERIODIC_BSPLINE_REFS_UNAVAILABLE")
        geometry.update(periodic_surface_grid_ref=grid, periodic_direction_ref=direction, support_ref=support)
    elif family == "OPEN_SHELL":
        surfaces = _refs(entries, "MEASURED_SPEC.SURFACE_PRIMITIVES.")
        boundaries = _refs(entries, "MEASURED_SPEC.MASTER_BOUNDARIES.")
        wireframes = _refs(entries, "MEASURED_SPEC.WIREFRAME.")
        topology = _refs(entries, "MEASURED_SPEC.TOPOLOGY.")
        if not all((surfaces, boundaries, wireframes, topology)):
            raise ValueError("MESH2CAD_OPEN_SHELL_REFS_UNAVAILABLE")
        geometry.update(surface_refs=surfaces, master_boundary_refs=boundaries, wireframe_refs=wireframes)
        plan["topology_refs"] = {"topology_refs": topology}
    else:
        raise ValueError(f"MESH2CAD_ADAPTER_UNSUPPORTED:{family}")
    plan["reasoning_summary"] = (
        f"Mesh2CAD-style structure proposal grounded to authoritative V11 refs. "
        f"Operations={deepcopy(intermediate.get('operation_sequence') or [])}; "
        f"raw numeric parameters are diagnostic-only and were not consumed. "
        f"{plan['reasoning_summary']}"
    )
    return plan
