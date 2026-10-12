#!/usr/bin/env python3
"""Convert DeepCAD JSON (sketch + extrude sequence) to project program.dsl."""

from __future__ import annotations

import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-deepcad")

import argparse
import json
import sys
from copy import copy
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEEPCAD_ROOT = ROOT / "DeepCAD"
sys.path.insert(0, str(DEEPCAD_ROOT))

from cadlib.curves import Arc, Circle, Line  # noqa: E402
from cadlib.extrude import CADSequence, Extrude  # noqa: E402
from cadlib.macro import EXTRUDE_OPERATIONS, EXTENT_TYPE  # noqa: E402


def _fmt_float(x: float) -> str:
    return f"{float(x):.6f}".rstrip("0").rstrip(".")


def _fmt_vec3(v: np.ndarray | tuple[float, float, float]) -> str:
    arr = np.asarray(v, dtype=float)
    return f"({_fmt_float(arr[0])}, {_fmt_float(arr[1])}, {_fmt_float(arr[2])})"


def _fmt_points(points: list[tuple[float, float]]) -> str:
    inner = ", ".join(f"({_fmt_float(x)}, {_fmt_float(y)})" for x, y in points)
    return f"[{inner}]"


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


def _sample_loop_points(loop, n_per_curve: int = 16) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for curve in loop.children:
        if isinstance(curve, Line):
            if not pts or not np.allclose(pts[-1], curve.start_point):
                pts.append((float(curve.start_point[0]), float(curve.start_point[1])))
            pts.append((float(curve.end_point[0]), float(curve.end_point[1])))
        elif isinstance(curve, Circle):
            angles = np.linspace(0.0, 2.0 * np.pi, num=max(n_per_curve, 8), endpoint=False)
            ring = curve.center[np.newaxis] + np.stack([np.cos(angles), np.sin(angles)], axis=1) * curve.radius
            for p in ring:
                pts.append((float(p[0]), float(p[1])))
        elif isinstance(curve, Arc):
            samples = curve.sample_points(max(n_per_curve, 8))
            for i, p in enumerate(samples):
                if i == 0 and pts and np.allclose(pts[-1], p):
                    continue
                pts.append((float(p[0]), float(p[1])))
        else:
            raise NotImplementedError(f"unsupported curve type: {type(curve).__name__}")
    if len(pts) >= 2 and np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    return _clean_polygon(pts)


def _is_circle_loop(loop) -> tuple[bool, float | None]:
    if len(loop.children) != 1 or not isinstance(loop.children[0], Circle):
        return False, None
    return True, float(loop.children[0].radius)


def _is_rect_loop(loop, tol: float = 1e-4) -> tuple[bool, tuple[float, float] | None]:
    if len(loop.children) != 4 or not all(isinstance(c, Line) for c in loop.children):
        return False, None
    pts = _sample_loop_points(loop)
    if len(pts) != 4:
        return False, None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if max(xs) - min(xs) < tol or max(ys) - min(ys) < tol:
        return False, None
    return True, (float(max(xs) - min(xs)), float(max(ys) - min(ys)))


def _extrude_params(ext: Extrude) -> dict[str, Any]:
    axis = tuple(float(x) for x in ext.sketch_plane.normal)
    origin = tuple(float(x) for x in ext.sketch_pos)
    x_axis = tuple(float(x) for x in ext.sketch_plane.x_axis)
    extent_type = EXTENT_TYPE[ext.extent_type]
    height = float(abs(ext.extent_one))
    height_two = float(abs(ext.extent_two))
    return {
        "axis": axis,
        "origin": origin,
        "x_axis": x_axis,
        "extent_type": extent_type,
        "height": height,
        "height_two": height_two,
        "symmetric": extent_type == "SymmetricFeatureExtentType",
        "operation": EXTRUDE_OPERATIONS[ext.operation],
    }


def _emit_extrude_body(name: str, ext: Extrude, profile) -> tuple[str, dict[str, Any]]:
    params = _extrude_params(ext)
    loops = profile.children
    meta: dict[str, Any] = {
        "op_index": name,
        "operation": params["operation"],
        "extent_type": params["extent_type"],
        "profile_kind": "unknown",
        "n_loops": len(loops),
    }

    if len(loops) == 1:
        outer = loops[0]
        is_circle, radius = _is_circle_loop(outer)
        if is_circle and radius is not None:
            meta["profile_kind"] = "circle"
            line = (
                f"{name} = Extrude(Circle(radius={_fmt_float(radius)}), "
                f"height={_fmt_float(params['height'])}, axis={_fmt_vec3(params['axis'])}, "
                f"origin={_fmt_vec3(params['origin'])})"
            )
            return line, meta

        is_rect, size = _is_rect_loop(outer)
        if is_rect and size is not None:
            meta["profile_kind"] = "rectangle"
            line = (
                f"{name} = Box(width={_fmt_float(size[0])}, depth={_fmt_float(size[1])}, "
                f"height={_fmt_float(params['height'])}, axis={_fmt_vec3(params['axis'])}, "
                f"origin={_fmt_vec3(params['origin'])}, x_axis={_fmt_vec3(params['x_axis'])})"
            )
            return line, meta

        points = _sample_loop_points(outer)
        meta["profile_kind"] = "polygon"
    else:
        # Use outer loop only; inner loops become separate cut bodies upstream.
        points = _sample_loop_points(loops[0])
        meta["profile_kind"] = "polygon_outer_only"

    kw = [
        f"points={_fmt_points(points)}",
        f"height={_fmt_float(params['height'])}",
        f"axis={_fmt_vec3(params['axis'])}",
        f"origin={_fmt_vec3(params['origin'])}",
        f"x_axis={_fmt_vec3(params['x_axis'])}",
    ]
    if params["symmetric"]:
        kw.append("symmetric=True")
    elif params["height_two"] > 0:
        kw.append(f"height_two={_fmt_float(params['height_two'])}")
    line = f"{name} = ExtrudePolygon({', '.join(kw)})"
    return line, meta


def _emit_inner_cuts(ext: Extrude, profile, prefix: str) -> tuple[list[str], list[dict[str, Any]]]:
    lines: list[str] = []
    metas: list[dict[str, Any]] = []
    if len(profile.children) <= 1:
        return lines, metas
    params = _extrude_params(ext)
    for i, loop in enumerate(profile.children[1:], start=1):
        points = _sample_loop_points(loop)
        name = f"{prefix}_hole_{i}"
        kw = [
            f"points={_fmt_points(points)}",
            f"height={_fmt_float(params['height'])}",
            f"axis={_fmt_vec3(params['axis'])}",
            f"origin={_fmt_vec3(params['origin'])}",
            f"x_axis={_fmt_vec3(params['x_axis'])}",
        ]
        if params["symmetric"]:
            kw.append("symmetric=True")
        elif params["height_two"] > 0:
            kw.append(f"height_two={_fmt_float(params['height_two'])}")
        lines.append(f"{name} = ExtrudePolygon({', '.join(kw)})")
        metas.append({"op_index": name, "profile_kind": "hole", "n_points": len(points)})
    return lines, metas


def deepcad_json_to_dsl(data: dict) -> tuple[str, dict[str, Any]]:
    cad = CADSequence.from_dict(data)
    cad.normalize()
    lines: list[str] = ["# DeepCAD → project CAD DSL"]
    op_meta: list[dict[str, Any]] = []
    body_names: list[str] = []
    result_expr: str | None = None

    for i, ext in enumerate(cad.seq):
        profile = copy(ext.profile)
        profile.denormalize(ext.sketch_size)
        body_name = f"body_{i}"
        body_line, meta = _emit_extrude_body(body_name, ext, profile)
        lines.append(body_line)
        op_meta.append(meta)

        hole_lines, hole_meta = _emit_inner_cuts(ext, profile, body_name)
        lines.extend(hole_lines)
        op_meta.extend(hole_meta)
        hole_names = [m["op_index"] for m in hole_meta]

        op = EXTRUDE_OPERATIONS[ext.operation]
        piece_names = [body_name] + hole_names
        if op == "NewBodyFeatureOperation":
            if result_expr is None:
                result_expr = body_name
            else:
                result_expr = f"Union({result_expr}, {body_name})"
            for hole in hole_names:
                result_expr = f"Cut({result_expr}, {hole})"
        elif op == "JoinFeatureOperation":
            result_expr = body_name if result_expr is None else f"Union({result_expr}, {body_name})"
            for hole in hole_names:
                result_expr = f"Cut({result_expr}, {hole})"
        elif op == "CutFeatureOperation":
            if result_expr is None:
                result_expr = body_name
            else:
                result_expr = f"Cut({result_expr}, {body_name})"
            for hole in hole_names:
                result_expr = f"Cut({result_expr}, {hole})"
        elif op == "IntersectFeatureOperation":
            result_expr = body_name if result_expr is None else f"Cut({result_expr}, {body_name})"
        body_names.append(body_name)

    if result_expr is None:
        raise ValueError("empty DeepCAD sequence")
    lines.append(f"result = {result_expr}")

    report = {
        "n_extrude": len(cad.seq),
        "operations": op_meta,
        "bbox": np.asarray(cad.bbox).tolist() if cad.bbox is not None else None,
    }
    return "\n".join(lines) + "\n", report


def convert_file(json_path: Path, dsl_path: Path | None = None) -> dict[str, Any]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    dsl_text, report = deepcad_json_to_dsl(data)
    if dsl_path is not None:
        dsl_path.parent.mkdir(parents=True, exist_ok=True)
        dsl_path.write_text(dsl_text, encoding="utf-8")
    report["json"] = str(json_path)
    report["dsl"] = str(dsl_path) if dsl_path else None
    report["dsl_lines"] = len(dsl_text.splitlines())
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepCAD JSON → program.dsl")
    parser.add_argument("--json", type=Path, required=True, help="DeepCAD source JSON")
    parser.add_argument("--out", type=Path, default=None, help="Output program.dsl path")
    parser.add_argument("--report", type=Path, default=None, help="Optional conversion report JSON")
    args = parser.parse_args()

    out = args.out or args.json.with_name("program.dsl")
    report = convert_file(args.json, out)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
