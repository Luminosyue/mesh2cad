#!/usr/bin/env python3
"""CAD canonical coordinate contract.

Unique per-sample transform T (matches former SpatialLM mm_plugin behavior):

    p_canonical = s * p_source + t
    s = target_diagonal / bbox_diagonal
    t = -s * bbox_min

DSL rules (NOT blind x*s+t on every number):
  - world positions (origin, center):     p' = s*p + t
  - lengths (radius, height, width, ...): l' = s*l
  - local 2D sketch points:               (x',y') = s*(x,y)
  - directions (axis, x_axis, normal):    unchanged
  - booleans / topology:                  unchanged

Inverse: p_source = (p_canonical - t) / s
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_TARGET_DIAGONAL = 6.0

_LENGTH_KEYS = frozenset(
    {"radius", "height", "width", "depth", "height_two", "outer_radius"}
)
_WORLD_KEYS = frozenset({"origin", "center"})
_DIR_KEYS = frozenset({"axis", "x_axis", "y_axis", "normal"})
_LOCAL2D_KEYS = frozenset({"points"})


@dataclass
class CoordinateTransform:
    source_bbox_min: list[float]
    source_bbox_max: list[float]
    source_diagonal: float
    target_diagonal: float
    scale: float
    translation: list[float]

    def to_json(self) -> dict:
        return asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "CoordinateTransform":
        return cls(
            source_bbox_min=[float(x) for x in data["source_bbox_min"]],
            source_bbox_max=[float(x) for x in data["source_bbox_max"]],
            source_diagonal=float(data["source_diagonal"]),
            target_diagonal=float(data["target_diagonal"]),
            scale=float(data["scale"]),
            translation=[float(x) for x in data["translation"]],
        )

    @property
    def s(self) -> float:
        return self.scale

    @property
    def t(self) -> np.ndarray:
        return np.asarray(self.translation, dtype=np.float64)

    def inverse_params(self) -> tuple[float, np.ndarray]:
        """Return (s_inv, t_inv) so p_source = s_inv * p_canonical + t_inv."""
        s_inv = 1.0 / self.scale
        t_inv = -self.t / self.scale
        return s_inv, t_inv


def compute_transform(
    points: np.ndarray,
    target_diagonal: float = DEFAULT_TARGET_DIAGONAL,
) -> CoordinateTransform:
    pts = np.asarray(points, dtype=np.float64)
    mn = pts.min(axis=0)
    mx = pts.max(axis=0)
    diagonal = float(np.linalg.norm(mx - mn))
    if diagonal <= 0 or target_diagonal <= 0:
        scale = 1.0
    else:
        scale = float(target_diagonal / diagonal)
    translation = (-scale * mn).tolist()
    return CoordinateTransform(
        source_bbox_min=mn.tolist(),
        source_bbox_max=mx.tolist(),
        source_diagonal=diagonal,
        target_diagonal=float(target_diagonal),
        scale=scale,
        translation=translation,
    )


def apply_points(
    points: np.ndarray, tf: CoordinateTransform, inverse: bool = False
) -> np.ndarray:
    pts = np.asarray(points, dtype=np.float64)
    if inverse:
        s, t = tf.inverse_params()
    else:
        s, t = tf.s, tf.t
    return (s * pts + t).astype(np.float64)


def canonicalize_features(
    features: np.ndarray,
    tf: CoordinateTransform,
) -> np.ndarray:
    """Scale/shift xyz only; normals and edge_score unchanged."""
    feats = np.asarray(features, dtype=np.float32).copy()
    feats[:, :3] = apply_points(feats[:, :3], tf, inverse=False).astype(np.float32)
    return feats


def _const_num(node: ast.AST) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _const_num(node.operand)
        return None if v is None else -v
    return None


def _make_num(x: float) -> ast.AST:
    # Keep training labels compact / stable (match deepcad_to_dsl style).
    x = float(f"{float(x):.6f}")
    if x < 0:
        return ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=float(-x)))
    return ast.Constant(value=float(x))


def _make_tuple(vals: list[float]) -> ast.Tuple:
    return ast.Tuple(elts=[_make_num(v) for v in vals], ctx=ast.Load())


def _scale_numeric_node(node: ast.AST, s: float) -> ast.AST:
    v = _const_num(node)
    if v is None:
        raise ValueError(f"expected numeric literal, got {ast.dump(node)}")
    return _make_num(s * v)


def _affine_vec_node(node: ast.AST, s: float, t: np.ndarray, dim: int) -> ast.AST:
    if not isinstance(node, (ast.Tuple, ast.List)) or len(node.elts) != dim:
        raise ValueError(f"expected {dim}-vector, got {ast.dump(node)}")
    out = []
    for i, elt in enumerate(node.elts):
        v = _const_num(elt)
        if v is None:
            raise ValueError(f"non-numeric vector component: {ast.dump(elt)}")
        if dim == 3:
            out.append(s * v + float(t[i]))
        else:
            out.append(s * v)
    if isinstance(node, ast.Tuple):
        return _make_tuple(out)
    return ast.List(elts=[_make_num(v) for v in out], ctx=ast.Load())


def _scale_points2d(node: ast.AST, s: float) -> ast.AST:
    if not isinstance(node, ast.List):
        raise ValueError(f"points must be a list, got {ast.dump(node)}")
    new_elts = []
    for elt in node.elts:
        if not isinstance(elt, (ast.Tuple, ast.List)) or len(elt.elts) != 2:
            raise ValueError(f"bad 2D point: {ast.dump(elt)}")
        xy = []
        for c in elt.elts:
            v = _const_num(c)
            if v is None:
                raise ValueError(f"non-numeric 2D point: {ast.dump(c)}")
            xy.append(s * v)
        if isinstance(elt, ast.Tuple):
            new_elts.append(
                ast.Tuple(elts=[_make_num(xy[0]), _make_num(xy[1])], ctx=ast.Load())
            )
        else:
            new_elts.append(
                ast.List(elts=[_make_num(xy[0]), _make_num(xy[1])], ctx=ast.Load())
            )
    return ast.List(elts=new_elts, ctx=ast.Load())


def _transform_call(node: ast.Call, s: float, t: np.ndarray) -> ast.Call:
    if not isinstance(node.func, ast.Name):
        raise ValueError("only simple calls supported")
    op = node.func.id

    new_args = [_transform_expr(a, s, t) for a in node.args]
    new_kwargs = [
        ast.keyword(arg=kw.arg, value=_transform_expr(kw.value, s, t))
        for kw in node.keywords
        if kw.arg is not None
    ]

    if op in {"Cut", "Union"}:
        return ast.Call(func=node.func, args=new_args, keywords=new_kwargs)

    if op == "Circle":
        if new_args:
            new_args[0] = _scale_numeric_node(new_args[0], s)
        for kw in new_kwargs:
            if kw.arg == "radius":
                kw.value = _scale_numeric_node(kw.value, s)
        return ast.Call(func=node.func, args=new_args, keywords=new_kwargs)

    if op == "Sketch":
        for kw in new_kwargs:
            if kw.arg in _LENGTH_KEYS:
                kw.value = _scale_numeric_node(kw.value, s)
        return ast.Call(func=node.func, args=new_args, keywords=new_kwargs)

    if op in {"Extrude", "Cylinder", "Revolve", "Box", "ExtrudePolygon"}:
        if op == "Extrude":
            if len(new_args) >= 2 and not isinstance(new_args[1], ast.Call):
                new_args[1] = _scale_numeric_node(new_args[1], s)
        elif op in {"Cylinder", "Revolve"}:
            for i in range(min(2, len(new_args))):
                if _const_num(new_args[i]) is not None:
                    new_args[i] = _scale_numeric_node(new_args[i], s)
            if len(new_args) >= 4:
                new_args[3] = _affine_vec_node(new_args[3], s, t, 3)
        elif op == "Box":
            for i in range(min(3, len(new_args))):
                if _const_num(new_args[i]) is not None:
                    new_args[i] = _scale_numeric_node(new_args[i], s)
            if len(new_args) >= 5:
                new_args[4] = _affine_vec_node(new_args[4], s, t, 3)
        elif op == "ExtrudePolygon":
            if new_args:
                new_args[0] = _scale_points2d(new_args[0], s)
            if len(new_args) >= 2 and _const_num(new_args[1]) is not None:
                new_args[1] = _scale_numeric_node(new_args[1], s)

        for kw in new_kwargs:
            key = kw.arg
            if key in _LENGTH_KEYS:
                kw.value = _scale_numeric_node(kw.value, s)
            elif key in _WORLD_KEYS:
                kw.value = _affine_vec_node(kw.value, s, t, 3)
            elif key in _LOCAL2D_KEYS:
                kw.value = _scale_points2d(kw.value, s)
            elif key in _DIR_KEYS or key == "symmetric":
                pass
        return ast.Call(func=node.func, args=new_args, keywords=new_kwargs)

    return ast.Call(func=node.func, args=new_args, keywords=new_kwargs)


def _transform_expr(node: ast.AST, s: float, t: np.ndarray) -> ast.AST:
    if isinstance(node, ast.Call):
        return _transform_call(node, s, t)
    if isinstance(node, (ast.Name, ast.Constant, ast.UnaryOp, ast.Tuple, ast.List)):
        return node
    if isinstance(node, ast.BinOp):
        return ast.BinOp(
            left=_transform_expr(node.left, s, t),
            op=node.op,
            right=_transform_expr(node.right, s, t),
        )
    raise ValueError(f"unsupported expr in DSL transform: {ast.dump(node)}")


def transform_dsl(
    code: str,
    tf: CoordinateTransform,
    inverse: bool = False,
) -> str:
    """Apply T (or T^-1) to DSL source text; return new DSL string."""
    import sys

    root = Path(__file__).resolve().parents[2]
    scripts = str(root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code

    if inverse:
        s, t = tf.inverse_params()
    else:
        s, t = tf.s, tf.t

    raw = extract_dsl_code(code)
    header_lines: list[str] = []
    for line in code.splitlines():
        if line.strip().startswith("#"):
            header_lines.append(line)
        elif line.strip():
            break
        else:
            header_lines.append(line)

    tree = ast.parse(raw, mode="exec")
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            stmt.value = _transform_expr(stmt.value, s, t)
        elif isinstance(stmt, ast.Expr):
            stmt.value = _transform_expr(stmt.value, s, t)
        else:
            raise ValueError(f"unsupported statement: {ast.dump(stmt)}")

    body = ast.unparse(tree)
    if not body.endswith("\n"):
        body += "\n"
    if header_lines:
        hdr = "\n".join(header_lines).rstrip()
        if hdr:
            tag = "# CAD canonical (same T as features_canonical.npy)"
            if "canonical" not in hdr.lower():
                hdr = hdr + "\n" + tag
            return hdr + "\n" + body
    return "# CAD canonical (same T as features_canonical.npy)\n" + body


def write_transform_json(path: Path, tf: CoordinateTransform) -> None:
    path.write_text(json.dumps(tf.to_json(), indent=2) + "\n", encoding="utf-8")


def load_transform_json(path: Path) -> CoordinateTransform:
    return CoordinateTransform.from_json(json.loads(path.read_text(encoding="utf-8")))


def build_sample_canonical(
    sample_dir: Path,
    target_diagonal: float = DEFAULT_TARGET_DIAGONAL,
    features_name: str = "features.npy",
    dsl_name: str = "program.dsl",
) -> dict[str, Any]:
    """Write features_canonical.npy, program_canonical.dsl, coordinate_transform.json."""
    sample_dir = Path(sample_dir)
    feats = np.load(sample_dir / features_name)
    dsl_text = (sample_dir / dsl_name).read_text(encoding="utf-8")

    tf = compute_transform(feats[:, :3], target_diagonal=target_diagonal)
    feats_c = canonicalize_features(feats, tf)
    dsl_c = transform_dsl(dsl_text, tf, inverse=False)

    out_feats = sample_dir / "features_canonical.npy"
    out_dsl = sample_dir / "program_canonical.dsl"
    out_tf = sample_dir / "coordinate_transform.json"
    np.save(out_feats, feats_c.astype(np.float32))
    out_dsl.write_text(dsl_c, encoding="utf-8")
    write_transform_json(out_tf, tf)

    xyz = feats_c[:, :3]
    np.save(
        sample_dir / "features_canonical_xyz_normal.npy",
        feats_c[:, :6].astype(np.float32),
    )
    return {
        "sample_id": sample_dir.name,
        "scale": tf.scale,
        "translation": tf.translation,
        "source_diagonal": tf.source_diagonal,
        "canonical_diagonal": float(np.linalg.norm(xyz.max(0) - xyz.min(0))),
        "canonical_min": xyz.min(0).tolist(),
        "canonical_max": xyz.max(0).tolist(),
        "features_canonical": str(out_feats),
        "program_canonical": str(out_dsl),
        "coordinate_transform": str(out_tf),
    }
