"""Rule-based CAD Feature Planner.

Geometry summary → CAD operation plan (feature reasoning).
LLM only translates the plan into executable DSL — it does not invent strategy.
"""

from __future__ import annotations

from typing import Any


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _outer_inner_radii(summary: dict[str, Any]) -> tuple[float | None, float | None, list[float]]:
    """Prefer Dora meta radius_clusters for outer/inner; candidates fill mid list."""
    clusters = (summary.get("edge_information") or {}).get("radius_clusters") or []
    cluster_rs = [_f(c.get("radius_mean")) for c in clusters if _f(c.get("radius_mean")) > 0]
    cand_rs = [
        _f(c.get("radius"))
        for c in (summary.get("closed_feature_candidates") or [])
        if _f(c.get("radius")) > 0
    ]
    # unique descending merge
    merged: list[float] = []
    for r in sorted(cluster_rs + cand_rs, reverse=True):
        if not merged or abs(r - merged[-1]) / max(merged[-1], 1e-8) > 0.06:
            merged.append(r)

    outer = cluster_rs[0] if cluster_rs else (merged[0] if merged else None)
    inner = None
    if len(cluster_rs) >= 2:
        inner = cluster_rs[-1]
    elif len(merged) >= 2 and outer is not None:
        # pick smallest that is still a plausible bore (>= 25% outer, avoid noise crumbs)
        for r in sorted(merged):
            if 0.25 * outer <= r < 0.92 * outer:
                inner = r
                break
    return outer, inner, merged


def _axis_pack(summary: dict[str, Any]) -> dict[str, Any]:
    ax = summary.get("axis_extent") or {}
    return {
        "axis": ax.get("axis"),
        "height": ax.get("height"),
        "center": ax.get("center"),
        "bottom_origin": ax.get("bottom_origin"),
    }


def plan_cad_features(summary: dict[str, Any]) -> dict[str, Any]:
    """Emit a CAD operation plan from geometry evidence (rules first, no LLM)."""
    g = summary.get("geometry") or {}
    e = summary.get("edge_information") or {}
    rings = int(e.get("circular_ring_count") or 0)
    groups = int(e.get("concentric_radius_groups") or 0)
    cyl = _f(g.get("cylindrical_ratio"))
    planar = _f(g.get("planar_ratio"))
    outer_r, inner_r, radii = _outer_inner_radii(summary)
    axis = _axis_pack(summary)

    # --- rule table (ordered, first match wins for component_type) ---
    rules_fired: list[str] = []
    component_type = "GENERIC_SOLID"
    ops: list[dict[str, Any]] = []
    allow = ["Cylinder", "Sketch", "Extrude", "Revolve"]
    must_follow: list[str] = []

    if rings >= 3 and cyl > 0.4:
        component_type = "REVOLVED_COMPONENT"
        rules_fired.append("circular_ring_count>=3 AND cylindrical_ratio>0.4 → REVOLVED_COMPONENT")
        ops.append(
            {
                "step": 1,
                "op": "Cylinder|Revolve",
                "role": "outer_body",
                "radius": outer_r,
                "height": axis.get("height"),
                "axis": axis.get("axis"),
                "origin": axis.get("bottom_origin"),
                "required": True,
            }
        )
        if groups >= 2 and inner_r is not None and outer_r is not None and inner_r / outer_r < 0.92:
            allow.append("Cut")
            ops.append(
                {
                    "step": 2,
                    "op": "Cut",
                    "role": "inner_bore",
                    "tool": "Cylinder",
                    "radius": inner_r,
                    "height": axis.get("height"),
                    "axis": axis.get("axis"),
                    "origin": axis.get("bottom_origin"),
                    "required": True,
                    "note": "confirmed concentric inner radius — emit Cut",
                }
            )
            must_follow.append("MUST emit Cut for inner_bore; do not stop at outer cylinder only")
        if rings >= 4:
            ops.append(
                {
                    "step": 3,
                    "op": "Revolve|Cut",
                    "role": "groove_or_waist",
                    "required": False,
                    "note": "multiple rings suggest groove/waist; approximate if mid radii exist",
                    "mid_radii": radii[1:-1] if len(radii) > 2 else [],
                }
            )
            must_follow.append("Prefer a revolved / multi-radius construction over a single plain cylinder")

    elif rings >= 2 and groups >= 2 and cyl >= 0.45:
        component_type = "HOLLOW_CYLINDER"
        rules_fired.append("rings>=2 AND concentric_radius_groups>=2 AND cylindrical_ratio>=0.45 → HOLLOW_CYLINDER")
        allow.append("Cut")
        ops.extend(
            [
                {
                    "step": 1,
                    "op": "Cylinder",
                    "role": "outer_body",
                    "radius": outer_r,
                    "height": axis.get("height"),
                    "axis": axis.get("axis"),
                    "origin": axis.get("bottom_origin"),
                    "required": True,
                },
                {
                    "step": 2,
                    "op": "Cut",
                    "role": "inner_bore",
                    "tool": "Cylinder",
                    "radius": inner_r,
                    "height": axis.get("height"),
                    "axis": axis.get("axis"),
                    "origin": axis.get("bottom_origin"),
                    "required": True,
                },
            ]
        )
        must_follow.append("MUST emit outer Cylinder + Cut(inner); single Cylinder alone is invalid")

    elif rings == 1 and cyl >= 0.55:
        component_type = "OUTER_CYLINDER"
        rules_fired.append("circular_ring_count==1 AND cylindrical_ratio>=0.55 → OUTER_CYLINDER")
        ops.append(
            {
                "step": 1,
                "op": "Cylinder",
                "role": "outer_body",
                "radius": outer_r,
                "height": axis.get("height"),
                "axis": axis.get("axis"),
                "origin": axis.get("bottom_origin"),
                "required": True,
            }
        )
        must_follow.append("Inner hole NOT confirmed — do NOT invent Cut")

    elif planar >= 0.55 and cyl < 0.45:
        component_type = "EXTRUDED_PLATE"
        rules_fired.append("planar_ratio>=0.55 AND cylindrical_ratio<0.45 → EXTRUDED_PLATE")
        ops.append(
            {
                "step": 1,
                "op": "Extrude",
                "role": "plate_body",
                "height": axis.get("height"),
                "axis": axis.get("axis"),
                "origin": axis.get("bottom_origin"),
                "required": True,
                "note": "use dominant planar extent; Circle sketch only if circular rim exists",
            }
        )

    else:
        component_type = "GENERIC_SOLID"
        rules_fired.append("fallback → GENERIC_SOLID")
        ops.append(
            {
                "step": 1,
                "op": "Cylinder|Extrude",
                "role": "primary_body",
                "radius": outer_r,
                "height": axis.get("height"),
                "axis": axis.get("axis"),
                "origin": axis.get("bottom_origin"),
                "required": True,
            }
        )
        if groups >= 2 and rings >= 2 and inner_r is not None:
            allow.append("Cut")
            ops.append(
                {
                    "step": 2,
                    "op": "Cut",
                    "role": "optional_inner",
                    "radius": inner_r,
                    "required": False,
                }
            )

    # de-dup allow list preserving order
    seen = set()
    allow_u = []
    for a in allow:
        if a not in seen:
            seen.add(a)
            allow_u.append(a)

    plan = {
        "component_type": component_type,
        "rules_fired": rules_fired,
        "evidence": {
            "circular_ring_count": rings,
            "concentric_radius_groups": groups,
            "cylindrical_ratio": cyl,
            "planar_ratio": planar,
            "radii_desc": radii[:6],
            "outer_radius": outer_r,
            "inner_radius": inner_r,
        },
        "operation_plan": ops,
        "allowed_operations": allow_u,
        "must_follow": must_follow,
        "units": "SOURCE_NATIVE",
        "axis": axis,
    }
    return plan


def render_operation_plan(plan: dict[str, Any]) -> str:
    """Human/LLM-readable CAD operation plan block."""
    lines = [
        "CAD operation plan (from Feature Planner — follow this):",
        f"- component_type: {plan.get('component_type')}",
        f"- rules_fired: {'; '.join(plan.get('rules_fired') or [])}",
        f"- allowed_operations: {', '.join(plan.get('allowed_operations') or [])}",
        f"- units: {plan.get('units')}",
        "",
        "Steps:",
    ]
    for step in plan.get("operation_plan") or []:
        bits = [
            f"step={step.get('step')}",
            f"op={step.get('op')}",
            f"role={step.get('role')}",
            f"required={step.get('required')}",
        ]
        if step.get("radius") is not None:
            bits.append(f"radius={step.get('radius')}")
        if step.get("height") is not None:
            bits.append(f"height={step.get('height')}")
        if step.get("origin") is not None:
            bits.append(f"origin={step.get('origin')}")
        if step.get("axis") is not None:
            bits.append(f"axis={step.get('axis')}")
        if step.get("note"):
            bits.append(f"note={step.get('note')}")
        if step.get("mid_radii"):
            bits.append(f"mid_radii={step.get('mid_radii')}")
        lines.append("- " + ", ".join(bits))

    mf = plan.get("must_follow") or []
    if mf:
        lines.append("")
        lines.append("Must follow:")
        for m in mf:
            lines.append(f"- {m}")
    return "\n".join(lines) + "\n"
