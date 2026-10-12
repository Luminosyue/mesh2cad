"""Small reference-aware profile/axis geometry backend.

It consumes explicit canonical entity geometry. It never infers geometry from
a bounding box and never falls back to a global axis. Incomplete source-query
resolution is rejected before the kernel call.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


class GeometryBackendError(ValueError):
    pass


@dataclass(frozen=True)
class LineGeometry:
    entity_id: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]


@dataclass(frozen=True)
class CircleGeometry:
    entity_id: str
    center: tuple[float, float, float]
    radius: float
    normal: tuple[float, float, float]


@dataclass(frozen=True)
class AxisGeometry:
    axis_id: str
    source_ref: str
    origin: tuple[float, float, float]
    direction: tuple[float, float, float]


def _vec(value, name):
    arr = np.asarray(value, dtype=float)
    if arr.shape != (3,) or not np.isfinite(arr).all():
        raise GeometryBackendError(f"{name}_GEOMETRY_FAIL")
    return arr


def validate_axis(axis: AxisGeometry) -> AxisGeometry:
    origin = _vec(axis.origin, "AXIS")
    direction = _vec(axis.direction, "AXIS")
    norm = float(np.linalg.norm(direction))
    if norm <= 1e-12:
        raise GeometryBackendError("AXIS_GEOMETRY_FAIL:zero_direction")
    return AxisGeometry(axis.axis_id, axis.source_ref, tuple(origin), tuple(direction / norm))


def validate_entities(entities: Iterable[LineGeometry | CircleGeometry]) -> None:
    seen = set()
    for entity in entities:
        if entity.entity_id in seen:
            raise GeometryBackendError("ENTITY_GEOMETRY_FAIL:duplicate_id")
        seen.add(entity.entity_id)
        if isinstance(entity, LineGeometry):
            a, b = _vec(entity.start, "ENTITY"), _vec(entity.end, "ENTITY")
            if np.linalg.norm(a - b) <= 1e-12:
                raise GeometryBackendError("ENTITY_GEOMETRY_FAIL:zero_line")
        elif isinstance(entity, CircleGeometry):
            _vec(entity.center, "ENTITY"); n = _vec(entity.normal, "ENTITY")
            if entity.radius <= 0 or np.linalg.norm(n) <= 1e-12:
                raise GeometryBackendError("ENTITY_GEOMETRY_FAIL:invalid_circle")
        else:
            raise GeometryBackendError("ENTITY_GEOMETRY_FAIL:unsupported_type")


def order_closed_line_loop(lines: list[LineGeometry], tolerance: float = 1e-6) -> list[LineGeometry]:
    if not lines:
        raise GeometryBackendError("PROFILE_WIRE_OPEN:empty")
    validate_entities(lines)
    remaining = list(lines)
    ordered = [remaining.pop(0)]
    while remaining:
        end = np.asarray(ordered[-1].end, dtype=float)
        match = None
        reverse = False
        for i, line in enumerate(remaining):
            if np.linalg.norm(end - np.asarray(line.start)) <= tolerance:
                match = i; break
            if np.linalg.norm(end - np.asarray(line.end)) <= tolerance:
                match = i; reverse = True; break
        if match is None:
            raise GeometryBackendError("PROFILE_ENTITY_ORDER_FAIL")
        line = remaining.pop(match)
        ordered.append(LineGeometry(line.entity_id, line.end, line.start) if reverse else line)
    if np.linalg.norm(np.asarray(ordered[-1].end) - np.asarray(ordered[0].start)) > tolerance:
        raise GeometryBackendError("PROFILE_WIRE_OPEN")
    return ordered


def build_revolve_shape(ordered_lines: list[LineGeometry], axis: AxisGeometry, angle_degrees: float):
    """Create a true CadQuery revolve from an explicit closed 3-D wire."""
    if not np.isfinite(angle_degrees) or not (0 < angle_degrees <= 360):
        raise GeometryBackendError("REVOLVE_KERNEL_FAIL:invalid_angle")
    axis = validate_axis(axis)
    ordered_lines = order_closed_line_loop(ordered_lines)
    import cadquery as cq
    edges = [cq.Edge.makeLine(cq.Vector(*line.start), cq.Vector(*line.end)) for line in ordered_lines]
    wire = cq.Wire.assembleEdges(edges)
    face = cq.Face.makeFromWires(wire)
    a = cq.Vector(*axis.origin)
    d = cq.Vector(*(np.asarray(axis.origin) + np.asarray(axis.direction)))
    return cq.Workplane(obj=face).revolve(angle_degrees, tuple(a.toTuple()), tuple(d.toTuple()))
