#!/usr/bin/env python3
"""Convert Fusion360 Reconstruction JSON to project program.dsl (CAD DSL v1)."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


class Fusion360FilterError(Exception):
    """Sample should be excluded (unsupported op, Intersect, etc.)."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def _fmt_float(x: float) -> str:
    return f"{float(x):.6f}".rstrip("0").rstrip(".")


def _fmt_vec3(v: tuple[float, float, float] | np.ndarray) -> str:
    arr = np.asarray(v, dtype=float)
    return f"({_fmt_float(arr[0])}, {_fmt_float(arr[1])}, {_fmt_float(arr[2])})"


def _fmt_points(points: list[tuple[float, float]]) -> str:
    inner = ", ".join(f"({_fmt_float(x)}, {_fmt_float(y)})" for x, y in points)
    return f"[{inner}]"


def _pt2d(obj: dict) -> tuple[float, float]:
    return float(obj["x"]), float(obj["y"])


def _vec3(obj: dict) -> tuple[float, float, float]:
    return float(obj["x"]), float(obj["y"]), float(obj["z"])


def _normalize(v: tuple[float, float, float], eps: float = 1e-12) -> tuple[float, float, float]:
    arr = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(arr))
    if n < eps:
        return (0.0, 0.0, 1.0)
    arr = arr / n
    return float(arr[0]), float(arr[1]), float(arr[2])


def _clean_polygon(points: list[tuple[float, float]], tol: float = 1e-6) -> list[tuple[float, float]]:
    if not points:
        return points
    cleaned: list[tuple[float, float]] = [points[0]]
    for p in points[1:]:
        if float(np.linalg.norm(np.asarray(p) - np.asarray(cleaned[-1]))) > tol:
            cleaned.append(p)
    if len(cleaned) >= 2 and float(np.linalg.norm(np.asarray(cleaned[0]) - np.asarray(cleaned[-1]))) <= tol:
        cleaned = cleaned[:-1]
    if len(cleaned) < 3:
        return cleaned
    final: list[tuple[float, float]] = [cleaned[0]]
    for i in range(1, len(cleaned) - 1):
        a = np.asarray(final[-1])
        b = np.asarray(cleaned[i])
        c = np.asarray(cleaned[i + 1])
        cross = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        if cross > tol:
            final.append(cleaned[i])
    final.append(cleaned[-1])
    return final


def _sample_arc(curve: dict, n: int = 16) -> list[tuple[float, float]]:
    center = _pt2d(curve["center_point"])
    radius = float(curve["radius"])
    start_angle = float(curve.get("start_angle", 0.0))
    end_angle = float(curve.get("end_angle", 0.0))
    ref = curve.get("reference_vector") or {"x": 1.0, "y": 0.0, "z": 0.0}
    ref_xy = np.array([float(ref["x"]), float(ref["y"])], dtype=float)
    ref_norm = float(np.linalg.norm(ref_xy))
    if ref_norm < 1e-12:
        ref_xy = np.array([1.0, 0.0])
    else:
        ref_xy /= ref_norm
    base_angle = math.atan2(ref_xy[1], ref_xy[0])
    if end_angle < start_angle:
        end_angle += 2.0 * math.pi
    angles = np.linspace(start_angle, end_angle, num=max(n, 4))
    pts: list[tuple[float, float]] = []
    for ang in angles:
        theta = base_angle + float(ang)
        pts.append((center[0] + radius * math.cos(theta), center[1] + radius * math.sin(theta)))
    return pts


def _sample_nurbs(curve: dict, n_per_seg: int = 8) -> list[tuple[float, float]]:
    cps = curve.get("control_points") or []
    if not cps:
        return []
    pts = [_pt2d(p) for p in cps]
    dense: list[tuple[float, float]] = []
    for i in range(len(pts) - 1):
        a = np.asarray(pts[i])
        b = np.asarray(pts[i + 1])
        for t in np.linspace(0.0, 1.0, num=n_per_seg, endpoint=(i == len(pts) - 2)):
            p = a * (1.0 - t) + b * t
            dense.append((float(p[0]), float(p[1])))
    return dense


def _sample_profile_curve(curve: dict, n: int = 16) -> list[tuple[float, float]]:
    ctype = curve.get("type")
    if ctype == "Line3D":
        return [_pt2d(curve["start_point"]), _pt2d(curve["end_point"])]
    if ctype == "Circle3D":
        center = _pt2d(curve["center_point"])
        radius = float(curve["radius"])
        angles = np.linspace(0.0, 2.0 * math.pi, num=max(n, 8), endpoint=False)
        return [
            (center[0] + radius * math.cos(a), center[1] + radius * math.sin(a))
            for a in angles
        ]
    if ctype == "Arc3D":
        return _sample_arc(curve, n=n)
    if ctype in ("NurbsCurve3D", "EllipticalArc3D", "EllipticArc3D", "ConicCurve3D"):
        return _sample_nurbs(curve, n_per_seg=max(n // 2, 4))
    raise Fusion360FilterError(f"unsupported_profile_curve:{ctype}")


def _sample_loop(profile_curves: list[dict], n_per_curve: int = 16) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for curve in profile_curves:
        seg = _sample_profile_curve(curve, n=n_per_curve)
        for i, p in enumerate(seg):
            if i == 0 and pts and np.allclose(pts[-1], p):
                continue
            pts.append(p)
    if len(pts) >= 2 and np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    return _clean_polygon(pts)


def _is_circle_loop(profile_curves: list[dict]) -> tuple[bool, float | None]:
    if len(profile_curves) != 1:
        return False, None
    curve = profile_curves[0]
    if curve.get("type") != "Circle3D":
        return False, None
    return True, float(curve["radius"])


def _is_rect_loop(profile_curves: list[dict], tol: float = 1e-4) -> tuple[bool, tuple[float, float] | None]:
    if len(profile_curves) != 4:
        return False, None
    if not all(c.get("type") == "Line3D" for c in profile_curves):
        return False, None
    corners: list[tuple[float, float]] = []
    for curve in profile_curves:
        for key in ("start_point", "end_point"):
            p = _pt2d(curve[key])
            if not any(abs(p[0] - q[0]) <= tol and abs(p[1] - q[1]) <= tol for q in corners):
                corners.append(p)
    if len(corners) != 4:
        return False, None
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    if w < tol or h < tol:
        return False, None
    # Four line segments do not necessarily form an axis-aligned rectangle.
    # Keep rotated rectangles and general quadrilaterals as exact polygons.
    for c in profile_curves:
        a, b = _pt2d(c['start_point']), _pt2d(c['end_point'])
        if abs(a[0]-b[0]) > tol and abs(a[1]-b[1]) > tol:
            return False, None
    expected = [(x, y) for x in (min(xs), max(xs)) for y in (min(ys), max(ys))]
    if any(not any(np.allclose(p, q, atol=tol, rtol=0) for q in corners) for p in expected):
        return False, None
    return True, (float(w), float(h))


def _profile_point_to_world(point, frame):
    origin, normal, x_axis = (np.asarray(v, dtype=float) for v in frame)
    if not np.isclose(np.dot(normal, x_axis), 0., atol=1e-6):
        raise Fusion360FilterError('non_orthogonal_sketch_frame')
    y_axis = np.cross(normal, x_axis)
    x, y = point
    return tuple(origin + x*x_axis + y*y_axis)


def _sketch_frame(sketch: dict) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    transform = sketch.get("transform") or {}
    origin = _vec3(transform.get("origin") or {"x": 0, "y": 0, "z": 0})
    x_axis = _normalize(_vec3(transform.get("x_axis") or {"x": 1, "y": 0, "z": 0}))
    z_axis = _normalize(_vec3(transform.get("z_axis") or {"x": 0, "y": 0, "z": 1}))
    return origin, z_axis, x_axis


def _distance_value(extent_obj: dict | None) -> float:
    if not extent_obj:
        return 0.0
    return float((extent_obj.get("distance") or {}).get("value", 0.0))


def _parse_extent(extrude: dict) -> dict[str, Any]:
    extent_type = extrude.get("extent_type", "OneSideFeatureExtentType")
    start = extrude.get("start_extent") or {}
    if start.get("type") not in (None, "ProfilePlaneStartDefinition"):
        raise Fusion360FilterError(f"unsupported_start_extent:{start.get('type')}")

    extent_one = extrude.get("extent_one") or {}
    extent_two = extrude.get("extent_two") or {}
    # Keep signs: Fusion negative AlongDistance extrudes opposite the sketch normal.
    height = _distance_value(extent_one)
    height_two = _distance_value(extent_two) if extent_two else 0.0
    taper = float((extent_one.get("taper_angle") or {}).get("value", 0.0))
    if abs(taper) > 1e-6:
        raise Fusion360FilterError("unsupported_taper_angle")

    return {
        "extent_type": extent_type,
        "height": height,
        "height_two": height_two,
        "symmetric": extent_type == "SymmetricFeatureExtentType",
    }


def _extent_extra_kwargs(extent: dict[str, Any]) -> list[str]:
    extra: list[str] = []
    if extent["symmetric"]:
        extra.append("symmetric=True")
    elif abs(float(extent["height_two"])) > 1e-12:
        extra.append(f"height_two={_fmt_float(extent['height_two'])}")
    return extra


def _profile_loops(sketch: dict, profile_id: str) -> list[dict]:
    profile = (sketch.get("profiles") or {}).get(profile_id)
    if profile is None:
        raise Fusion360FilterError(f"missing_profile:{profile_id}")
    loops = profile.get("loops") or []
    if not loops:
        raise Fusion360FilterError(f"empty_profile:{profile_id}")
    outers = [lp for lp in loops if lp.get("is_outer", True)]
    inners = [lp for lp in loops if not lp.get("is_outer", True)]
    ordered = outers + inners
    return ordered


def _emit_extrude_body(
    name: str,
    outer_curves: list[dict],
    frame: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
    extent: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    origin, axis, x_axis = frame
    meta: dict[str, Any] = {"op_index": name, "profile_kind": "unknown"}

    is_circle, radius = _is_circle_loop(outer_curves)
    if is_circle and radius is not None:
        meta["profile_kind"] = "circle"
        center = _pt2d(outer_curves[0]['center_point'])
        origin = _profile_point_to_world(center, frame)
        meta['placement_fix'] = {'local_center': center, 'world_origin': origin}
        kw = [
            f"height={_fmt_float(extent['height'])}",
            f"axis={_fmt_vec3(axis)}",
            f"origin={_fmt_vec3(origin)}",
            *_extent_extra_kwargs(extent),
        ]
        line = f"{name} = Extrude(Circle(radius={_fmt_float(radius)}), {', '.join(kw)})"
        return line, meta

    is_rect, size = _is_rect_loop(outer_curves)
    if is_rect and size is not None:
        meta["profile_kind"] = "rectangle"
        corners = [_pt2d(c[k]) for c in outer_curves for k in ('start_point','end_point')]
        center = tuple((np.min(corners,axis=0)+np.max(corners,axis=0))/2)
        origin = _profile_point_to_world(center, frame)
        meta['placement_fix'] = {'local_center': center, 'world_origin': origin}
        kw = [
            f"width={_fmt_float(size[0])}",
            f"depth={_fmt_float(size[1])}",
            f"height={_fmt_float(extent['height'])}",
            f"axis={_fmt_vec3(axis)}",
            f"origin={_fmt_vec3(origin)}",
            f"x_axis={_fmt_vec3(x_axis)}",
            *_extent_extra_kwargs(extent),
        ]
        line = f"{name} = Box({', '.join(kw)})"
        return line, meta

    points = _sample_loop(outer_curves)
    if len(points) < 3:
        raise Fusion360FilterError("degenerate_outer_loop")
    meta["profile_kind"] = "polygon"
    meta["n_points"] = len(points)
    meta["has_arc_or_spline"] = any(
        c.get("type") in ("Arc3D", "NurbsCurve3D", "EllipticalArc3D", "EllipticArc3D", "ConicCurve3D")
        for c in outer_curves
    )

    kw = [
        f"points={_fmt_points(points)}",
        f"height={_fmt_float(extent['height'])}",
        f"axis={_fmt_vec3(axis)}",
        f"origin={_fmt_vec3(origin)}",
        f"x_axis={_fmt_vec3(x_axis)}",
        *_extent_extra_kwargs(extent),
    ]
    return f"{name} = ExtrudePolygon({', '.join(kw)})", meta


def _emit_hole_body(
    name: str,
    inner_curves: list[dict],
    frame: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]],
    extent: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    origin, axis, x_axis = frame
    points = _sample_loop(inner_curves)
    if len(points) < 3:
        raise Fusion360FilterError("degenerate_hole_loop")
    kw = [
        f"points={_fmt_points(points)}",
        f"height={_fmt_float(extent['height'])}",
        f"axis={_fmt_vec3(axis)}",
        f"origin={_fmt_vec3(origin)}",
        f"x_axis={_fmt_vec3(x_axis)}",
        *_extent_extra_kwargs(extent),
    ]
    line = f"{name} = ExtrudePolygon({', '.join(kw)})"
    meta = {"op_index": name, "profile_kind": "hole", "n_points": len(points)}
    return line, meta


def _combine_piece(result_expr: str | None, piece_expr: str, op: str, hole_names: list[str]) -> str:
    if op == "NewBodyFeatureOperation":
        if result_expr is None:
            result_expr = piece_expr
        else:
            result_expr = f"Union({result_expr}, {piece_expr})"
    elif op == "JoinFeatureOperation":
        result_expr = piece_expr if result_expr is None else f"Union({result_expr}, {piece_expr})"
    elif op == "CutFeatureOperation":
        result_expr = piece_expr if result_expr is None else f"Cut({result_expr}, {piece_expr})"
    else:
        raise Fusion360FilterError(f"unsupported_operation:{op}")
    for hole in hole_names:
        result_expr = f"Cut({result_expr}, {hole})"
    return result_expr


def fusion360_json_to_dsl(data: dict) -> tuple[str, dict[str, Any]]:
    entities = data.get("entities") or {}
    timeline = sorted(data.get("timeline") or [], key=lambda x: x.get("index", 0))

    lines: list[str] = ["# Fusion360 Reconstruction → project CAD DSL"]
    op_meta: list[dict[str, Any]] = []
    result_expr: str | None = None
    extrude_idx = 0
    filtered_intersect = 0

    for step in timeline:
        entity_id = step.get("entity")
        entity = entities.get(entity_id)
        if entity is None:
            raise Fusion360FilterError(f"missing_entity:{entity_id}")
        if entity.get("type") != "ExtrudeFeature":
            continue

        op = entity.get("operation", "NewBodyFeatureOperation")
        if op == "IntersectFeatureOperation":
            filtered_intersect += 1
            continue

        extent = _parse_extent(entity)
        profile_refs = entity.get("profiles") or []
        if not profile_refs:
            raise Fusion360FilterError("extrude_without_profiles")

        piece_names: list[str] = []
        piece_holes: dict[str, list[str]] = {}

        for pref_idx, pref in enumerate(profile_refs):
            sketch_id = pref.get("sketch")
            profile_id = pref.get("profile")
            sketch = entities.get(sketch_id)
            if sketch is None or sketch.get("type") != "Sketch":
                raise Fusion360FilterError(f"missing_sketch:{sketch_id}")

            loops = _profile_loops(sketch, profile_id)
            frame = _sketch_frame(sketch)
            body_name = f"body_{extrude_idx}" if len(profile_refs) == 1 else f"body_{extrude_idx}_{pref_idx}"
            outer_curves = loops[0].get("profile_curves") or []
            body_line, meta = _emit_extrude_body(body_name, outer_curves, frame, extent)
            meta["operation"] = op
            meta["extent_type"] = extent["extent_type"]
            lines.append(body_line)
            op_meta.append(meta)

            hole_names: list[str] = []
            for hole_i, inner_loop in enumerate(loops[1:], start=1):
                hole_name = f"{body_name}_hole_{hole_i}"
                hole_line, hole_meta = _emit_hole_body(
                    hole_name,
                    inner_loop.get("profile_curves") or [],
                    frame,
                    extent,
                )
                lines.append(hole_line)
                op_meta.append(hole_meta)
                hole_names.append(hole_name)

            piece_names.append(body_name)
            piece_holes[body_name] = hole_names

        if len(piece_names) == 1:
            piece_expr = piece_names[0]
            for h in piece_holes[piece_names[0]]:
                piece_expr = f"Cut({piece_expr}, {h})"
            result_expr = _combine_piece(result_expr, piece_expr, op, [])
        else:
            union_parts = []
            for pname in piece_names:
                expr = pname
                for h in piece_holes[pname]:
                    expr = f"Cut({expr}, {h})"
                union_parts.append(expr)
            multi_expr = union_parts[0]
            for part in union_parts[1:]:
                multi_expr = f"Union({multi_expr}, {part})"
            result_expr = _combine_piece(result_expr, multi_expr, op, [])

        extrude_idx += 1

    if result_expr is None:
        raise Fusion360FilterError("empty_extrude_sequence")

    lines.append(f"result = {result_expr}")
    report = {
        "n_extrude": extrude_idx,
        "filtered_intersect": filtered_intersect,
        "operations": op_meta,
    }
    return "\n".join(lines) + "\n", report


def convert_file(json_path: Path, dsl_path: Path | None = None) -> dict[str, Any]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    dsl_text, report = fusion360_json_to_dsl(data)
    if dsl_path is not None:
        dsl_path.parent.mkdir(parents=True, exist_ok=True)
        dsl_path.write_text(dsl_text, encoding="utf-8")
    report["json"] = str(json_path)
    report["dsl"] = str(dsl_path) if dsl_path else None
    report["dsl_lines"] = len(dsl_text.splitlines())
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Fusion360 JSON → program.dsl")
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    out = args.out or args.json.with_name("program.dsl")
    try:
        report = convert_file(args.json, out)
    except Fusion360FilterError as exc:
        report = {"ok": False, "filter_reason": exc.reason, "json": str(args.json)}
        if args.report:
            args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 2

    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
