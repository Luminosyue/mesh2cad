#!/usr/bin/env python3
"""Step 4: audit current V4 CAD DSL capability. Do not assume Loft/Sweep exist."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from canonical_cad_data_v4.config import HASHES_DIR, REPORTS_DIR  # noqa: E402
from canonical_cad_data_v4.converters import cad_dsl as v4_dsl  # noqa: E402
from canonical_cad_data_v4.hashutil import file_manifest_entry, write_json  # noqa: E402

OPS = [
    "Sketch",
    "Line",
    "Circle",
    "Arc",
    "Ellipse",
    "BSpline",
    "Polygon",
    "Rectangle",
    "Extrude",
    "ExtrudePolygon",
    "Box",
    "Cylinder",
    "Cut",
    "Join",
    "Union",
    "Revolve",
    "Loft",
    "Sweep",
    "Fillet",
    "Chamfer",
    "Shell",
    "Mirror",
    "Pattern",
]


def _src() -> str:
    return Path(inspect.getfile(v4_dsl)).read_text(encoding="utf-8")


def _allowed() -> set[str]:
    return set(getattr(v4_dsl, "ALLOWED_FUNCS", set()))


def _executor_handles(src: str, name: str) -> bool:
    return f'if op == "{name}"' in src or f"if op == '{name}'" in src


def audit_op(name: str, allowed: set[str], src: str) -> dict:
    parser = name in allowed
    executor = _executor_handles(src, name)
    # STEP generation is via execute_dsl → STEPControl_Writer for any built solid.
    step = executor and parser
    known_bugs: list[str] = []
    completeness = "none"
    support = "UNSUPPORTED"

    if name in {"Sketch", "Circle"}:
        completeness = "radius_only"
        support = "SUPPORTED" if parser and executor else "PARTIAL"
        known_bugs.append("Sketch is a circle helper only; no multi-entity sketch graph")
    elif name == "Extrude":
        completeness = "circle_profile + signed height + symmetric + height_two"
        support = "SUPPORTED" if parser and executor else "PARTIAL"
        known_bugs.append("Extrude accepts Circle only; polygon uses ExtrudePolygon")
    elif name in {"ExtrudePolygon", "Box", "Cylinder", "Union", "Cut"}:
        completeness = "full_for_v1_vocab"
        support = "SUPPORTED" if parser and executor else "PARTIAL"
        if name == "Box":
            known_bugs.append("Box is the Rectangle-extrude alias")
    elif name in {"Join"}:
        completeness = "alias_of_Union"
        parser = "Union" in allowed
        executor = _executor_handles(src, "Union")
        support = "PARTIAL"
        known_bugs.append("No Join() token; converters emit Union()")
        step = executor
    elif name == "Rectangle":
        completeness = "emitted_as_Box"
        parser = "Box" in allowed
        executor = _executor_handles(src, "Box")
        support = "PARTIAL"
        step = executor
    elif name in {"Line", "Polygon"}:
        completeness = "polygon_polyline_only"
        parser = "ExtrudePolygon" in allowed
        executor = _executor_handles(src, "ExtrudePolygon")
        support = "PARTIAL"
        step = executor
        known_bugs.append("No first-class Line/Polygon ops; baked into ExtrudePolygon.points")
    elif name == "Revolve":
        parser = name in allowed
        executor = _executor_handles(src, name)
        completeness = "legacy_cylinder_equivalent_only"
        support = "PARTIAL" if parser else "UNSUPPORTED"
        known_bugs.append(
            "Revolve(outer_r, height, ...) is implemented as a cylinder, NOT a true revolve of an arbitrary profile. "
            "CADFS revolve must stay unsupported_operation."
        )
        step = False
    elif name in {"Arc", "Ellipse", "BSpline"}:
        completeness = "not_in_dsl"
        support = "UNSUPPORTED"
        known_bugs.append(
            "Sketch arcs/splines are sampled to polygons in DeepCAD/Fusion converters; "
            "CADFS forbids that silent approximation."
        )
    elif name in {"Loft", "Sweep", "Fillet", "Chamfer", "Shell", "Mirror", "Pattern"}:
        completeness = "not_in_dsl"
        support = "UNSUPPORTED"
        known_bugs.append("If a source CAD uses this op, status=unsupported_operation; do not degrade to Extrude.")
        parser = False
        executor = False
        step = False

    return {
        "name": name,
        "support": support,
        "parser_support": bool(parser),
        "executor_support": bool(executor),
        "step_generation_support": bool(step),
        "parameter_completeness": completeness,
        "known_bugs": known_bugs,
    }


def run_dsl_audit() -> dict:
    src = _src()
    allowed = _allowed()
    rows = [audit_op(name, allowed, src) for name in OPS]
    by = {"SUPPORTED": [], "PARTIAL": [], "UNSUPPORTED": []}
    for r in rows:
        by[r["support"]].append(r["name"])
    policy = {
        "cadfs_advanced_ops": "never_degrade_to_extrude",
        "unsupported_status": "unsupported_operation",
        "silent_skip_forbidden": True,
        "intersect_forbidden": True,
        "revolve_is_not_true_revolve": True,
    }
    report = {
        "pipeline_version": "canonical_cad_data_v4",
        "dsl_module": str(Path(inspect.getfile(v4_dsl))),
        "ALLOWED_FUNCS": sorted(allowed),
        "ops": rows,
        "SUPPORTED": by["SUPPORTED"],
        "PARTIAL": by["PARTIAL"],
        "UNSUPPORTED": by["UNSUPPORTED"],
        "policy": policy,
        "notes": [
            "V4 executor is the placement_v3 cad_dsl copy (signed extent / symmetric / height_two).",
            "Legacy edge_aware_cad_planner_v1/cad_dsl.py lacks extent kwargs on Extrude/Box; not used by V4.",
        ],
    }
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    HASHES_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / "02_dsl_capability_audit.json"
    write_json(out, report)
    write_json(HASHES_DIR / "02_dsl_capability_audit_sha256.json", file_manifest_entry(out))
    return report


def main() -> int:
    r = run_dsl_audit()
    print("SUPPORTED:", r["SUPPORTED"])
    print("PARTIAL:", r["PARTIAL"])
    print("UNSUPPORTED:", r["UNSUPPORTED"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
