"""CADFS FeatureScript operation audit + lossless V4 DSL conversion.

Advanced operations are NEVER approximated as Extrude. They are marked
`unsupported_operation` and kept for a future DSL expansion.
"""

from __future__ import annotations

import re
from typing import Any

# FeatureScript call names we care about.
OP_PATTERNS: dict[str, re.Pattern[str]] = {
    "sketch": re.compile(r"\bnewSketch\s*\("),
    "circle": re.compile(r"\bskCircle\s*\("),
    "line": re.compile(r"\bskLine(?:Segment)?\s*\("),
    "arc": re.compile(r"\bskArc\s*\("),
    "ellipse": re.compile(r"\bskEllipse\s*\("),
    "bspline": re.compile(r"\bsk(?:Spline|Nurbs)\s*\("),
    "rectangle": re.compile(r"\bskRectangle\s*\("),
    "polygon": re.compile(r"\bskPolygon\s*\("),
    "extrude": re.compile(r"\bextrude\s*\("),
    "revolve": re.compile(r"\brevolve\s*\("),
    "loft": re.compile(r"\bloft\s*\("),
    "sweep": re.compile(r"\bsweep\s*\("),
    "fillet": re.compile(r"\b(?:opFillet|fillet)\s*\("),
    "chamfer": re.compile(r"\b(?:opChamfer|chamfer)\s*\("),
    "shell": re.compile(r"\b(?:opShell|shell)\s*\("),
    "mirror": re.compile(r"\b(?:opMirror|mirror)\s*\("),
    "pattern": re.compile(r"\b(?:circularPattern|linearPattern|opPattern)\s*\("),
    "boolean": re.compile(r"\b(?:opBoolean)\s*\("),
    "cut": re.compile(r"NewBodyOperation|AddOperation|RemoveOperation|IntersectOperation"),
}

UNSUPPORTED_FOR_V4 = (
    "revolve",
    "loft",
    "sweep",
    "fillet",
    "chamfer",
    "shell",
    "mirror",
    "pattern",
    "arc",
    "ellipse",
    "bspline",
)

LOSSLESS_OK = ("sketch", "circle", "line", "rectangle", "polygon", "extrude", "boolean", "cut")

PLANE_FRAMES = {
    "Top.planeOp": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0)),
    "Front.planeOp": ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0)),
    "Right.planeOp": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
}

_SKETCH_PLANE = re.compile(r'makeId\("([^"]+\.planeOp)"\)')
_SK_CIRCLE = re.compile(
    r'skCircle\s*\(\s*sketch\s*,\s*"[^"]+"\s*,\s*\{[^}]*?"center"\s*:\s*v\(\s*([^,]+)\s*,\s*([^)]+)\)\s*\*\s*mm\s*,\s*"radius"\s*:\s*([^ *]+)\s*\*\s*mm',
    re.S,
)
_SK_LINE = re.compile(
    r'skLineSegment\s*\(\s*sketch\s*,\s*"[^"]+"\s*,\s*\{([^}]*)\}',
    re.S,
)
_PT = re.compile(r'"(?:start|end)"\s*:\s*v\(\s*([^,]+)\s*,\s*([^)]+)\)\s*\*\s*mm')
_CONSTRUCTION = re.compile(r'"construction"\s*:\s*true')
_EXTRUDE = re.compile(r"extrude\s*\(\s*context\s*,\s*id\s*\+\s*\"([^\"]+)\"\s*,\s*\{([^}]*)\}", re.S)
_DEPTH = re.compile(r'"depth"\s*:\s*([^ *]+)\s*\*\s*mm')
_OP = re.compile(r'"operation"\s*:\s*([A-Za-z]+)')
_BLOCK = re.compile(r"\{\s*var Q0;", re.S)


def _count(pat: re.Pattern[str], text: str) -> int:
    return len(pat.findall(text))


def audit_featurescript(text: str) -> dict[str, Any]:
    counts = {name: _count(pat, text) for name, pat in OP_PATTERNS.items()}
    present = [k for k, v in counts.items() if v > 0]
    unsupported = [k for k in UNSUPPORTED_FOR_V4 if counts.get(k, 0) > 0]
    n_features = text.count("newSketch") + text.count("extrude(") + text.count("revolve(")
    n_features += text.count("loft(") + text.count("sweep(") + text.count("opBoolean")
    n_features += text.count("fillet(") + text.count("chamfer(") + text.count("opShell")
    lossless = (
        counts.get("extrude", 0) > 0
        and not unsupported
        and (counts.get("circle", 0) + counts.get("line", 0) + counts.get("rectangle", 0)) > 0
    )
    stratum = "mixed-complex"
    if lossless and counts.get("boolean", 0) == 0 and counts.get("extrude", 0) <= 2:
        stratum = "basic_sketch_extrude"
    elif counts.get("boolean", 0) > 0 and not any(
        counts.get(k, 0) for k in ("revolve", "loft", "sweep", "fillet", "chamfer", "shell", "pattern")
    ):
        stratum = "boolean"
    elif counts.get("revolve", 0) > 0 and counts.get("loft", 0) == 0 and counts.get("sweep", 0) == 0:
        stratum = "revolve"
    elif counts.get("loft", 0) > 0:
        stratum = "loft"
    elif counts.get("sweep", 0) > 0:
        stratum = "sweep"
    elif counts.get("fillet", 0) > 0:
        stratum = "fillet"
    elif counts.get("chamfer", 0) > 0:
        stratum = "chamfer"
    elif counts.get("shell", 0) > 0:
        stratum = "shell"
    elif counts.get("pattern", 0) > 0:
        stratum = "pattern"
    return {
        "counts": counts,
        "present": present,
        "unsupported": unsupported,
        "lossless_candidate": lossless,
        "stratum": stratum,
        "n_features": n_features,
        "program_chars": len(text),
        "program_lines": text.count("\n") + 1,
    }


def _fmt_float(x: float) -> str:
    return f"{float(x):.6f}".rstrip("0").rstrip(".")


def _fmt_vec3(v: tuple[float, float, float]) -> str:
    return f"({_fmt_float(v[0])}, {_fmt_float(v[1])}, {_fmt_float(v[2])})"


def _fmt_points(points: list[tuple[float, float]]) -> str:
    inner = ", ".join(f"({_fmt_float(x)}, {_fmt_float(y)})" for x, y in points)
    return f"[{inner}]"


def _local_to_world(
    xy: tuple[float, float],
    origin: tuple[float, float, float],
    axis: tuple[float, float, float],
    x_axis: tuple[float, float, float],
) -> tuple[float, float, float]:
    import numpy as np

    o = np.asarray(origin, dtype=float)
    n = np.asarray(axis, dtype=float)
    x = np.asarray(x_axis, dtype=float)
    y = np.cross(n / (np.linalg.norm(n) + 1e-12), x / (np.linalg.norm(x) + 1e-12))
    p = o + xy[0] * x + xy[1] * y
    return float(p[0]), float(p[1]), float(p[2])


def _parse_plane(block: str) -> str | None:
    m = _SKETCH_PLANE.search(block)
    return m.group(1) if m else None


def _parse_lines(block: str) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    segs = []
    for m in _SK_LINE.finditer(block):
        body = m.group(1)
        if _CONSTRUCTION.search(body):
            continue
        pts = _PT.findall(body)
        if len(pts) >= 2:
            a = (float(pts[0][0]), float(pts[0][1]))
            b = (float(pts[1][0]), float(pts[1][1]))
            segs.append((a, b))
    return segs


def _chain_polygon(segs: list[tuple[tuple[float, float], tuple[float, float]]], tol: float = 1e-4):
    if not segs:
        return []
    unused = list(segs)
    pts = [unused[0][0], unused[0][1]]
    unused.pop(0)
    while unused:
        last = pts[-1]
        found = None
        for i, (a, b) in enumerate(unused):
            if abs(a[0] - last[0]) <= tol and abs(a[1] - last[1]) <= tol:
                found = i
                pts.append(b)
                break
            if abs(b[0] - last[0]) <= tol and abs(b[1] - last[1]) <= tol:
                found = i
                pts.append(a)
                break
        if found is None:
            return []
        unused.pop(found)
    if len(pts) >= 2 and abs(pts[0][0] - pts[-1][0]) <= tol and abs(pts[0][1] - pts[-1][1]) <= tol:
        pts = pts[:-1]
    return pts if len(pts) >= 3 else []


class CadfsUnsupported(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def cadfs_to_dsl(text: str) -> tuple[str, dict[str, Any]]:
    audit = audit_featurescript(text)
    if audit["unsupported"]:
        raise CadfsUnsupported("unsupported_operation:" + ",".join(audit["unsupported"]))
    if not audit["lossless_candidate"]:
        raise CadfsUnsupported("not_lossless_candidate")

    # Split feature blocks after the FeatureScript header.
    body_m = re.search(r"precondition\{\}\s*\{(.*)\}\s*\)\s*;\s*$", text, re.S)
    if not body_m:
        raise CadfsUnsupported("unparseable_featurescript_body")
    body = body_m.group(1)
    blocks = re.findall(r"\{\s*(?:var Q0;|var sketch)[\s\S]*?\}(?=\s*\{|\s*$)", body)
    if not blocks:
        # fallback: split on extrude / newSketch chunks
        blocks = re.split(r"\n\s*\n", body)

    sketches: list[dict[str, Any]] = []
    extrudes: list[dict[str, Any]] = []
    for block in blocks:
        if "newSketch" in block:
            plane = _parse_plane(block)
            if plane not in PLANE_FRAMES:
                raise CadfsUnsupported(f"unsupported_sketch_plane:{plane}")
            circles = [
                (float(m.group(1)), float(m.group(2)), float(m.group(3)))
                for m in _SK_CIRCLE.finditer(block)
            ]
            lines = _parse_lines(block)
            sketches.append({"plane": plane, "circles": circles, "lines": lines})
        if "extrude(" in block:
            em = _EXTRUDE.search(block)
            payload = em.group(2) if em else block
            dm = _DEPTH.search(payload)
            if not dm:
                raise CadfsUnsupported("extrude_missing_depth")
            depth = float(dm.group(1))
            om = _OP.search(payload)
            operation = om.group(1) if om else "NewBodyOperation"
            if operation == "IntersectOperation":
                raise CadfsUnsupported("unsupported_operation:IntersectOperation")
            extrudes.append({"depth": depth, "operation": operation})

    if not sketches or not extrudes:
        raise CadfsUnsupported("missing_sketch_or_extrude")
    if len(extrudes) != len(sketches):
        # Common CADFS pattern is 1 sketch → 1 extrude. Anything else is not lossless here.
        raise CadfsUnsupported(f"sketch_extrude_count_mismatch:{len(sketches)}:{len(extrudes)}")

    lines_out = ["# CADFS FeatureScript → V4 canonical CAD DSL (lossless subset)"]
    op_meta: list[dict[str, Any]] = []
    result_expr: str | None = None
    for i, (sk, ex) in enumerate(zip(sketches, extrudes)):
        origin, axis, x_axis = PLANE_FRAMES[sk["plane"]]
        name = f"body_{i}"
        if len(sk["circles"]) == 1 and not sk["lines"]:
            cx, cy, r = sk["circles"][0]
            world = _local_to_world((cx, cy), origin, axis, x_axis)
            line = (
                f"{name} = Extrude(Circle(radius={_fmt_float(r)}), "
                f"height={_fmt_float(ex['depth'])}, axis={_fmt_vec3(axis)}, origin={_fmt_vec3(world)})"
            )
            kind = "circle"
        elif sk["lines"] and not sk["circles"]:
            poly = _chain_polygon(sk["lines"])
            if len(poly) < 3:
                raise CadfsUnsupported("degenerate_line_polygon")
            line = (
                f"{name} = ExtrudePolygon(points={_fmt_points(poly)}, "
                f"height={_fmt_float(ex['depth'])}, axis={_fmt_vec3(axis)}, "
                f"origin={_fmt_vec3(origin)}, x_axis={_fmt_vec3(x_axis)})"
            )
            kind = "polygon"
        elif len(sk["circles"]) == 1 and sk["lines"]:
            raise CadfsUnsupported("mixed_circle_line_profile_not_lossless")
        elif len(sk["circles"]) > 1:
            raise CadfsUnsupported("multi_circle_profile_not_lossless")
        else:
            raise CadfsUnsupported("empty_or_unknown_profile")
        lines_out.append(line)
        op_meta.append(
            {
                "op_index": name,
                "profile_kind": kind,
                "operation": ex["operation"],
                "plane": sk["plane"],
            }
        )
        opname = ex["operation"]
        if opname in ("NewBodyOperation", "NewBodyFeatureOperation", ""):
            result_expr = name if result_expr is None else f"Union({result_expr}, {name})"
        elif opname in ("AddOperation", "JoinFeatureOperation"):
            result_expr = name if result_expr is None else f"Union({result_expr}, {name})"
        elif opname in ("RemoveOperation", "CutFeatureOperation"):
            if result_expr is None:
                result_expr = name
            else:
                result_expr = f"Cut({result_expr}, {name})"
        else:
            raise CadfsUnsupported(f"unsupported_operation:{opname}")

    if result_expr is None:
        raise CadfsUnsupported("empty_result")
    lines_out.append(f"result = {result_expr}")
    report = {"operations": op_meta, "audit": audit, "n_extrude": len(extrudes)}
    return "\n".join(lines_out) + "\n", report


def apply_audit_flags(rec: dict, audit: dict) -> dict:
    rec = dict(rec)
    rec["has_sketch"] = audit["counts"].get("sketch", 0) > 0
    rec["has_extrude"] = audit["counts"].get("extrude", 0) > 0
    rec["has_cut"] = "RemoveOperation" in (audit.get("present") or [])
    rec["has_join"] = audit["counts"].get("boolean", 0) > 0
    rec["has_revolve"] = audit["counts"].get("revolve", 0) > 0
    rec["has_loft"] = audit["counts"].get("loft", 0) > 0
    rec["has_sweep"] = audit["counts"].get("sweep", 0) > 0
    rec["has_fillet"] = audit["counts"].get("fillet", 0) > 0
    rec["has_chamfer"] = audit["counts"].get("chamfer", 0) > 0
    rec["has_shell"] = audit["counts"].get("shell", 0) > 0
    rec["has_mirror"] = audit["counts"].get("mirror", 0) > 0
    rec["has_pattern"] = audit["counts"].get("pattern", 0) > 0
    rec["num_circle"] = audit["counts"].get("circle", 0)
    rec["num_line"] = audit["counts"].get("line", 0)
    rec["num_arc"] = audit["counts"].get("arc", 0)
    rec["num_ellipse"] = audit["counts"].get("ellipse", 0)
    rec["num_bspline"] = audit["counts"].get("bspline", 0)
    rec["num_operations"] = audit.get("n_features") or 0
    rec["operations"] = audit.get("present") or []
    return rec
