"""Deterministic DSL emitter that follows the CAD Feature Planner operation plan."""

from __future__ import annotations

from typing import Any


def _fmt_vec(v) -> str:
    return f"({float(v[0]):.6f}, {float(v[1]):.6f}, {float(v[2]):.6f})"


def plan_rule_dsl(summary: dict[str, Any], feature_plan: dict[str, Any] | None = None) -> dict[str, Any]:
    """Emit DSL from feature operation plan (preferred) or simple outer cylinder fallback."""
    if feature_plan is None:
        from .cad_feature_planner import plan_cad_features

        feature_plan = plan_cad_features(summary)

    ops = feature_plan.get("operation_plan") or []
    ctype = feature_plan.get("component_type", "GENERIC_SOLID")
    lines: list[str] = []
    body_name = None
    cut_name = None

    for step in ops:
        role = step.get("role")
        op = str(step.get("op") or "")
        required = bool(step.get("required", False))
        if not required and role in {"groove_or_waist", "optional_inner"}:
            # v1 rule coder: skip optional groove (needs richer DSL later)
            continue

        radius = step.get("radius")
        height = step.get("height")
        axis = step.get("axis")
        origin = step.get("origin")
        if radius is None or height is None or axis is None or origin is None:
            continue

        if role in {"outer_body", "primary_body", "plate_body"} or (
            body_name is None and "Cut" not in op
        ):
            body_name = "body_0"
            # Extrude/Revolve both lower to Cylinder in current DSL executor
            lines.append(
                f"{body_name} = Cylinder(radius={float(radius):.6f}, height={float(height):.6f}, "
                f"axis={_fmt_vec(axis)}, origin={_fmt_vec(origin)})"
            )
        elif role in {"inner_bore", "optional_inner"} or "Cut" in op:
            cut_name = "cut_0"
            lines.append(
                f"{cut_name} = Cylinder(radius={float(radius):.6f}, height={float(height):.6f}, "
                f"axis={_fmt_vec(axis)}, origin={_fmt_vec(origin)})"
            )

    if body_name and cut_name and "Cut" in (feature_plan.get("allowed_operations") or []):
        lines.append(f"result = Cut({body_name}, {cut_name})")
        strategy = f"{ctype.lower()}_with_cut"
    elif body_name:
        lines.append(f"result = {body_name}")
        strategy = f"{ctype.lower()}_body_only"
    else:
        # absolute fallback
        ax = summary["axis_extent"]
        r = (feature_plan.get("evidence") or {}).get("outer_radius") or 0.05
        lines = [
            f"body_0 = Cylinder(radius={float(r):.6f}, height={float(ax['height']):.6f}, "
            f"axis={_fmt_vec(ax['axis'])}, origin={_fmt_vec(ax['bottom_origin'])})",
            "result = body_0",
        ]
        strategy = "fallback_outer_cylinder"

    dsl = "\n".join(lines) + "\n"
    return {
        "planner": "rule",
        "strategy": strategy,
        "component_type": ctype,
        "dsl": dsl,
        "feature_plan_ref": ctype,
        "params": {
            "outer_radius": (feature_plan.get("evidence") or {}).get("outer_radius"),
            "inner_radius": (feature_plan.get("evidence") or {}).get("inner_radius"),
            "height": (feature_plan.get("axis") or {}).get("height"),
        },
    }
