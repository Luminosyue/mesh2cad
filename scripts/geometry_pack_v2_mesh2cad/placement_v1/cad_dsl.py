"""Minimal CAD DSL: Cylinder / Extrude(circle) / Revolve(profile) / Cut → OCC/CadQuery STEP."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ALLOWED_FUNCS = {
    "Cylinder",
    "Extrude",
    "ExtrudePolygon",
    "Box",
    "Revolve",
    "Cut",
    "Sketch",
    "Circle",
    "Union",
}


@dataclass
class DSLProgram:
    raw: str
    assignments: dict[str, Any]
    result_name: str


def _as_vec3(val: Any, default: tuple[float, float, float] | None = None) -> tuple[float, float, float]:
    if val is None:
        if default is None:
            raise ValueError("missing vector")
        return default
    if isinstance(val, (list, tuple)) and len(val) == 3:
        return (float(val[0]), float(val[1]), float(val[2]))
    raise ValueError(f"expected vec3, got {val!r}")


def _eval_node(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        raise ValueError(f"undefined name: {node.id}")
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(elt, env) for elt in node.elts)
    if isinstance(node, ast.List):
        return [_eval_node(elt, env) for elt in node.elts]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -float(_eval_node(node.operand, env))
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, env)
        right = _eval_node(node.right, env)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        raise ValueError("unsupported binary op")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("only simple calls allowed")
        fname = node.func.id
        if fname not in ALLOWED_FUNCS:
            raise ValueError(f"disallowed function: {fname}")
        args = [_eval_node(a, env) for a in node.args]
        kwargs = {kw.arg: _eval_node(kw.value, env) for kw in node.keywords if kw.arg}
        return {"op": fname, "args": args, "kwargs": kwargs}
    raise ValueError(f"unsupported AST node: {type(node).__name__}")


def extract_dsl_code(text: str) -> str:
    """Pull DSL from LLM output (fenced or raw)."""
    text = text.strip()
    fence = re.search(r"```(?:python|cad|dsl)?\s*(.*?)```", text, flags=re.S | re.I)
    if fence:
        text = fence.group(1).strip()
    # drop leading commentary lines until first assignment / result
    lines = []
    started = False
    for line in text.splitlines():
        s = line.strip()
        if not started:
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", s) or s.startswith("result"):
                started = True
            else:
                continue
        if s.startswith("#") and "result" not in s:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def parse_dsl(code: str) -> DSLProgram:
    code = extract_dsl_code(code)
    if not code:
        raise ValueError("empty DSL")
    tree = ast.parse(code, mode="exec")
    env: dict[str, Any] = {}
    result_name = "result"
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            name = stmt.targets[0].id
            env[name] = _eval_node(stmt.value, env)
            if name == "result":
                result_name = "result"
        elif isinstance(stmt, ast.Expr):
            # allow bare result expression
            env["result"] = _eval_node(stmt.value, env)
            result_name = "result"
        else:
            raise ValueError(f"unsupported statement: {ast.dump(stmt)}")
    if "result" not in env:
        # last assignment becomes result
        if not env:
            raise ValueError("DSL has no assignments")
        result_name = list(env.keys())[-1]
        env["result"] = env[result_name]
    return DSLProgram(raw=code, assignments=env, result_name="result")


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else np.array([0.0, 0.0, 1.0])


def _clean_polygon(points: list[tuple[float, float]], tol: float = 1e-6) -> list[tuple[float, float]]:
    if not points:
        return points
    cleaned: list[tuple[float, float]] = [points[0]]
    for p in points[1:]:
        if float(np.linalg.norm(np.asarray(p) - np.asarray(cleaned[-1]))) > tol:
            cleaned.append(p)
    if len(cleaned) >= 2 and float(np.linalg.norm(np.asarray(cleaned[0]) - np.asarray(cleaned[-1]))) <= tol:
        cleaned = cleaned[:-1]
    return cleaned


def _cq_on_plane(
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    x_axis: tuple[float, float, float] | None = None,
):
    import cadquery as cq

    axis_v = _unit(np.asarray(axis, dtype=float))
    origin_v = np.asarray(origin, dtype=float)
    if x_axis is None:
        ref = np.array([0.0, 0.0, 1.0])
        if abs(float(ref @ axis_v)) > 0.95:
            ref = np.array([1.0, 0.0, 0.0])
        x_axis_v = _unit(np.cross(ref, axis_v))
    else:
        x_axis_v = _unit(np.asarray(x_axis, dtype=float))
    return cq.Workplane(cq.Plane(origin=tuple(origin_v.tolist()), xDir=tuple(x_axis_v.tolist()), normal=tuple(axis_v.tolist())))


def _extrude_with_extent(make_solid, height: float, height_two: float = 0.0, symmetric: bool = False):
    """Build a one-side solid, then optionally union the opposite extent.

    `make_solid(h)` must extrude by signed height `h` along the local +normal.
    Negative `height` is reverse one-side. Two-side uses `height_two` opposite
    the profile normal, matching Fusion AgainstDistance.
    """
    h = float(height)
    h2 = float(height_two)
    solid = make_solid(h)
    if symmetric:
        if abs(h) > 1e-12:
            solid = solid.union(make_solid(-h))
    elif abs(h2) > 1e-12:
        solid = solid.union(make_solid(-h2))
    return solid


def _cq_cylinder(
    radius: float,
    height: float,
    axis=(0.0, 0.0, 1.0),
    origin=(0.0, 0.0, 0.0),
    height_two: float = 0.0,
    symmetric: bool = False,
):
    import cadquery as cq

    axis = _unit(np.asarray(axis, dtype=float))
    origin = np.asarray(origin, dtype=float)

    def make(h: float):
        return cq.Workplane("XY").circle(radius).extrude(h)

    # CadQuery extrudes along +Z locally; build then transform
    solid = _extrude_with_extent(make, height, height_two, symmetric)
    # map local Z to desired axis; bottom at origin along axis
    z = np.array([0.0, 0.0, 1.0])
    if abs(float(z @ axis)) > 0.999:
        # parallel: maybe flip
        if float(z @ axis) < 0:
            # rotate 180 around X
            solid = solid.rotate((0, 0, 0), (1, 0, 0), 180)
    else:
        rot_axis = np.cross(z, axis)
        rot_axis = _unit(rot_axis)
        ang = float(np.degrees(np.arccos(np.clip(z @ axis, -1.0, 1.0))))
        solid = solid.rotate((0, 0, 0), tuple(rot_axis.tolist()), ang)
    solid = solid.translate(tuple(origin.tolist()))
    return solid


def _cq_box(
    width: float,
    depth: float,
    height: float,
    axis=(0.0, 0.0, 1.0),
    origin=(0.0, 0.0, 0.0),
    x_axis: tuple[float, float, float] | None = None,
    height_two: float = 0.0,
    symmetric: bool = False,
):
    wp = _cq_on_plane(_as_vec3(axis, (0, 0, 1)), _as_vec3(origin, (0, 0, 0)), x_axis)
    return _extrude_with_extent(lambda h: wp.rect(width, depth).extrude(h), height, height_two, symmetric)


def _cq_extrude_polygon(
    points: list[tuple[float, float]],
    height: float,
    axis=(0.0, 0.0, 1.0),
    origin=(0.0, 0.0, 0.0),
    x_axis: tuple[float, float, float] | None = None,
    height_two: float = 0.0,
    symmetric: bool = False,
):
    if len(points) < 3:
        raise ValueError("ExtrudePolygon needs >= 3 points")
    points = _clean_polygon([(float(p[0]), float(p[1])) for p in points])
    if len(points) < 3:
        raise ValueError("ExtrudePolygon collapsed to < 3 unique points")
    wp = _cq_on_plane(_as_vec3(axis, (0, 0, 1)), _as_vec3(origin, (0, 0, 0)), x_axis)
    return _extrude_with_extent(
        lambda h: wp.polyline(points).close().extrude(h),
        height,
        height_two,
        symmetric,
    )


def _build_shape(node: Any, shapes: dict[str, Any]) -> Any:
    """Recursively build CadQuery Workplane/Shape from parsed DSL node."""
    if isinstance(node, str) and node in shapes:
        return shapes[node]
    if not isinstance(node, dict) or "op" not in node:
        raise ValueError(f"not a CAD op node: {node!r}")
    op = node["op"]
    args = node.get("args") or []
    kw = node.get("kwargs") or {}

    if op == "Cylinder":
        if args:
            # Cylinder(r, h) or Cylinder(r, h, axis, origin)
            radius = float(args[0])
            height = float(args[1]) if len(args) > 1 else float(kw.get("height", 1.0))
            axis = args[2] if len(args) > 2 else kw.get("axis", (0, 0, 1))
            origin = args[3] if len(args) > 3 else kw.get("origin", (0, 0, 0))
        else:
            radius = float(kw["radius"])
            height = float(kw["height"])
            axis = kw.get("axis", (0, 0, 1))
            origin = kw.get("origin", (0, 0, 0))
        return _cq_cylinder(radius, height, _as_vec3(axis, (0, 0, 1)), _as_vec3(origin, (0, 0, 0)))

    if op == "Circle":
        # Sketch helper: Circle(radius) → dict for Extrude/Revolve
        r = float(args[0] if args else kw["radius"])
        return {"sketch": "circle", "radius": r}

    if op == "Sketch":
        # Sketch(Circle(...)) or Sketch(radius=...)
        if args and isinstance(args[0], dict):
            return args[0]
        return {"sketch": "circle", "radius": float(kw.get("radius", args[0] if args else 1.0))}

    if op == "Extrude":
        # Extrude(sketch, height, axis=..., origin=...)
        sketch = args[0] if args else kw.get("sketch")
        height = float(args[1] if len(args) > 1 else kw["height"])
        axis = _as_vec3(kw.get("axis", (0, 0, 1)), (0, 0, 1))
        origin = _as_vec3(kw.get("origin", (0, 0, 0)), (0, 0, 0))
        if isinstance(sketch, dict) and sketch.get("op") in {"Circle", "Sketch"}:
            sketch = _build_shape(sketch, shapes)
        if not isinstance(sketch, dict) or sketch.get("sketch") != "circle":
            # allow Extrude(radius, height) shorthand
            if isinstance(sketch, (int, float)):
                radius = float(sketch)
            else:
                raise ValueError("Extrude expects Circle/Sketch or radius")
        else:
            radius = float(sketch["radius"])
        height_two = float(kw.get("height_two", 0.0))
        symmetric = bool(kw.get("symmetric", False))
        return _cq_cylinder(
            radius,
            height,
            axis,
            origin,
            height_two=height_two,
            symmetric=symmetric,
        )

    if op == "Revolve":
        # Revolve(outer_r, height, axis, origin) — rectangle profile → cylinder equivalent
        # or Revolve(profile_outer, profile_inner=None, ...)
        outer = float(args[0] if args else kw.get("radius", kw.get("outer_radius")))
        height = float(args[1] if len(args) > 1 else kw["height"])
        axis = _as_vec3(args[2] if len(args) > 2 else kw.get("axis", (0, 0, 1)), (0, 0, 1))
        origin = _as_vec3(args[3] if len(args) > 3 else kw.get("origin", (0, 0, 0)), (0, 0, 0))
        return _cq_cylinder(outer, height, axis, origin)

    if op == "Box":
        if args:
            width = float(args[0])
            depth = float(args[1]) if len(args) > 1 else float(kw.get("depth", 1.0))
            height = float(args[2]) if len(args) > 2 else float(kw.get("height", 1.0))
            axis = args[3] if len(args) > 3 else kw.get("axis", (0, 0, 1))
            origin = args[4] if len(args) > 4 else kw.get("origin", (0, 0, 0))
            x_axis = args[5] if len(args) > 5 else kw.get("x_axis")
        else:
            width = float(kw["width"])
            depth = float(kw["depth"])
            height = float(kw["height"])
            axis = kw.get("axis", (0, 0, 1))
            origin = kw.get("origin", (0, 0, 0))
            x_axis = kw.get("x_axis")
        height_two = float(kw.get("height_two", 0.0))
        symmetric = bool(kw.get("symmetric", False))
        return _cq_box(
            width,
            depth,
            height,
            _as_vec3(axis, (0, 0, 1)),
            _as_vec3(origin, (0, 0, 0)),
            _as_vec3(x_axis) if x_axis is not None else None,
            height_two=height_two,
            symmetric=symmetric,
        )

    if op == "ExtrudePolygon":
        points = args[0] if args else kw["points"]
        height = float(args[1] if len(args) > 1 else kw["height"])
        axis = _as_vec3(kw.get("axis", (0, 0, 1)), (0, 0, 1))
        origin = _as_vec3(kw.get("origin", (0, 0, 0)), (0, 0, 0))
        x_axis = kw.get("x_axis")
        height_two = float(kw.get("height_two", 0.0))
        symmetric = bool(kw.get("symmetric", False))
        pts = [(float(p[0]), float(p[1])) for p in points]
        return _cq_extrude_polygon(
            pts,
            height,
            axis,
            origin,
            _as_vec3(x_axis) if x_axis is not None else None,
            height_two=height_two,
            symmetric=symmetric,
        )

    if op == "Cut":
        # Cut(a, b)
        a = args[0] if len(args) > 0 else kw.get("a")
        b = args[1] if len(args) > 1 else kw.get("b")
        sa = _resolve(a, shapes)
        sb = _resolve(b, shapes)
        return sa.cut(sb)

    if op == "Union":
        a = args[0]
        b = args[1]
        return _resolve(a, shapes).union(_resolve(b, shapes))

    raise ValueError(f"unhandled op: {op}")


def _resolve(node: Any, shapes: dict[str, Any]) -> Any:
    if isinstance(node, str):
        if node not in shapes:
            raise ValueError(f"unknown shape ref: {node}")
        return shapes[node]
    if isinstance(node, dict) and "op" in node:
        return _build_shape(node, shapes)
    return node


def execute_dsl(program: DSLProgram | str, step_path: Path | str, stl_path: Path | str | None = None) -> dict:
    """Execute DSL and write STEP (and optional STL)."""
    import cadquery as cq
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.IFSelect import IFSelect_RetDone

    if isinstance(program, str):
        program = parse_dsl(program)

    shapes: dict[str, Any] = {}
    # build in assignment order
    for name, node in program.assignments.items():
        if name == "result":
            continue
        if isinstance(node, dict) and "op" in node:
            shapes[name] = _build_shape(node, shapes)
        else:
            shapes[name] = node

    result_node = program.assignments["result"]
    if isinstance(result_node, str):
        result = shapes[result_node]
    elif isinstance(result_node, dict) and "op" in result_node:
        result = _build_shape(result_node, shapes)
    else:
        result = result_node

    step_path = Path(step_path)
    step_path.parent.mkdir(parents=True, exist_ok=True)

    # CadQuery compound → OCP shape
    ocp_shape = result.val().wrapped if hasattr(result, "val") else result
    writer = STEPControl_Writer()
    writer.Transfer(ocp_shape, STEPControl_AsIs)
    status = writer.Write(str(step_path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: status={status}")

    out = {"step": str(step_path), "ok": True}
    if stl_path is not None:
        stl_path = Path(stl_path)
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(result, str(stl_path))
        out["stl"] = str(stl_path)
    return out
