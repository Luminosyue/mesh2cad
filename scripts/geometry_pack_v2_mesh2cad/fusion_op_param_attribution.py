#!/usr/bin/env python3
"""Attribute Fusion360 602-label failures by CAD operation parameter type.

Does not repair the converter. Writes an isolated report under unit_audit_v2.
The 2x2 of circle/rectangle x one-side vs two-side/symmetric is the primary
control: pass/fail is sample-level, so we report both any-containment and
exclusive/pure partitions to avoid confounding sketch type with extent type.
"""
from __future__ import annotations

import ast
import collections
import json
import math
import pathlib
import re
from typing import Any

import numpy as np

ROOT = pathlib.Path("/data/home/cuiyuehan/project/mesh2cad")
AUDIT = ROOT / "cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v2"
OUT = AUDIT / "op_param_attribution"
ONE_SIDE = "OneSideFeatureExtentType"
TWO_SIDE = "TwoSidesFeatureExtentType"
SYMM = "SymmetricFeatureExtentType"
NON_ONE = {TWO_SIDE, SYMM}


def save(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def dist(entity: dict, key: str) -> float | None:
    raw = ((entity.get(key) or {}).get("distance") or {}).get("value")
    return None if raw is None else float(raw)


def vec3(obj: dict | None, default=(0.0, 0.0, 0.0)) -> tuple[float, float, float]:
    obj = obj or {}
    return (float(obj.get("x", default[0])), float(obj.get("y", default[1])), float(obj.get("z", default[2])))


def almost_unit(v: tuple[float, float, float], target: tuple[float, float, float], tol=1e-6) -> bool:
    a = np.asarray(v, dtype=float)
    b = np.asarray(target, dtype=float)
    na = float(np.linalg.norm(a))
    if na < 1e-12:
        return False
    return float(np.linalg.norm(a / na - b)) <= tol


def dsl_has_extent_kwargs(text: str) -> dict[str, bool]:
    return {
        "symmetric": bool(re.search(r"\bsymmetric\s*=", text)),
        "height_two": bool(re.search(r"\bheight_two\s*=", text)),
    }


def classify_ops(conv_ops: list[dict]) -> list[dict]:
    out = []
    for op in conv_ops:
        kind = op.get("profile_kind") or "unknown"
        extent = op.get("extent_type") or ONE_SIDE
        side = "one_side" if extent == ONE_SIDE else "two_side_or_symm" if extent in NON_ONE else f"other:{extent}"
        if extent == SYMM:
            side_fine = "symmetric"
        elif extent == TWO_SIDE:
            side_fine = "two_side"
        elif extent == ONE_SIDE:
            side_fine = "one_side"
        else:
            side_fine = extent or "missing"
        out.append(
            {
                "op_index": op.get("op_index"),
                "profile_kind": kind,
                "extent_type": extent,
                "side": side,
                "side_fine": side_fine,
                "operation": op.get("operation"),
            }
        )
    return out


def rate(n_pass: int, n: int) -> dict[str, Any]:
    return {
        "n": n,
        "pass": n_pass,
        "fail": n - n_pass,
        "pass_rate": (n_pass / n) if n else None,
        "fail_rate": ((n - n_pass) / n) if n else None,
    }


def summarize(rows: list[dict], pred) -> dict[str, Any]:
    hit = [r for r in rows if pred(r)]
    n_pass = sum(1 for r in hit if r["label_pass"] is True)
    out = rate(n_pass, len(hit))
    ch = [r["chamfer_rel"] for r in hit if r.get("chamfer_rel") is not None]
    cov = [r["coverage_02"] for r in hit if r.get("coverage_02") is not None]
    out["chamfer_median"] = float(np.median(ch)) if ch else None
    out["coverage_median"] = float(np.median(cov)) if cov else None
    out["geometry_measurable"] = len(ch)
    out["execution_ok"] = sum(1 for r in hit if r.get("execution_ok") is True)
    out["step_reload"] = sum(1 for r in hit if r.get("step_reload") is True)
    return out


def exclusive_cell(rows: list[dict], kind: str, two_side: bool) -> dict[str, Any]:
    """Samples whose converted bodies of `kind` are uniformly one-side or uniformly non-one-side.

    Other profile kinds may still exist on the sample; this only conditions on `kind`.
    """

    def pred(r):
        ops = [o for o in r["converted_ops"] if o["profile_kind"] == kind]
        if not ops:
            return False
        has_two = any(o["extent_type"] in NON_ONE for o in ops)
        has_one = any(o["extent_type"] == ONE_SIDE for o in ops)
        if two_side:
            return has_two and not has_one
        return has_one and not has_two

    return summarize(rows, pred)


def pure_cell(rows: list[dict], kind: str, two_side: bool) -> dict[str, Any]:
    """Samples whose non-hole converted bodies are exclusively `kind`, and extent is uniform."""

    def pred(r):
        bodies = [o for o in r["converted_ops"] if o["profile_kind"] != "hole"]
        if not bodies or any(o["profile_kind"] != kind for o in bodies):
            return False
        has_two = any(o["extent_type"] in NON_ONE for o in bodies)
        has_one = any(o["extent_type"] == ONE_SIDE for o in bodies)
        if two_side:
            return has_two and not has_one
        return has_one and not has_two

    return summarize(rows, pred)


def any_cell(rows: list[dict], kind: str, two_side: bool) -> dict[str, Any]:
    def pred(r):
        return any(
            o["profile_kind"] == kind and ((o["extent_type"] in NON_ONE) == two_side)
            for o in r["converted_ops"]
        )

    return summarize(rows, pred)


def main() -> None:
    results = json.loads((AUDIT / "results602.json").read_text())
    assert len(results) == 602
    rows = []
    timeline_counter = collections.Counter()
    start_extent_counter = collections.Counter()
    extent_type_counter = collections.Counter()
    boolean_counter = collections.Counter()

    for rec in results:
        parent = pathlib.Path(rec["source_step"]).parent
        src = json.loads((parent / "source.json").read_text())
        meta = json.loads((parent / "meta.json").read_text())
        dsl_path = parent / "program.dsl"
        dsl_text = dsl_path.read_text() if dsl_path.exists() else ""
        entities = src.get("entities") or {}
        timeline = src.get("timeline") or []
        types = [entities.get(t.get("entity"), {}).get("type", "MISSING") for t in timeline]
        timeline_counter.update(types)

        extrudes = []
        sketch_flags = []
        for step in sorted(timeline, key=lambda x: x.get("index", 0)):
            ent = entities.get(step.get("entity")) or {}
            if ent.get("type") != "ExtrudeFeature":
                continue
            start = (ent.get("start_extent") or {}).get("type") or "missing"
            start_extent_counter[start] += 1
            extent_type = ent.get("extent_type") or "missing"
            extent_type_counter[extent_type] += 1
            boolean_counter[ent.get("operation") or "missing"] += 1
            d1 = dist(ent, "extent_one")
            d2 = dist(ent, "extent_two")
            taper = float(((ent.get("extent_one") or {}).get("taper_angle") or {}).get("value") or 0.0)
            extrudes.append(
                {
                    "operation": ent.get("operation"),
                    "extent_type": extent_type,
                    "start_extent": start,
                    "extent_one": d1,
                    "extent_two": d2,
                    "negative_one": d1 is not None and d1 < 0,
                    "negative_two": d2 is not None and d2 < 0,
                    "taper": taper,
                    "n_profiles": len(ent.get("profiles") or []),
                }
            )
            for pref in ent.get("profiles") or []:
                sketch = entities.get(pref.get("sketch")) or {}
                tf = sketch.get("transform") or {}
                origin = vec3(tf.get("origin"))
                x_axis = vec3(tf.get("x_axis"), (1.0, 0.0, 0.0))
                z_axis = vec3(tf.get("z_axis"), (0.0, 0.0, 1.0))
                sketch_flags.append(
                    {
                        "origin_nonzero": math.hypot(*origin) > 1e-8,
                        "x_not_ex": not almost_unit(x_axis, (1.0, 0.0, 0.0)),
                        "z_not_ez": not almost_unit(z_axis, (0.0, 0.0, 1.0)),
                        "origin": origin,
                        "x_axis": x_axis,
                        "z_axis": z_axis,
                    }
                )

        conv_ops = classify_ops((meta.get("conversion") or {}).get("operations") or [])
        label_pass = rec.get("label_gate") is True
        rows.append(
            {
                "cad_id": rec["cad_id"],
                "label_pass": label_pass,
                "execution_ok": rec.get("execution_ok") is True,
                "step_reload": rec.get("step_reload") is True,
                "chamfer_rel": rec.get("chamfer_rel"),
                "coverage_02": rec.get("coverage_02"),
                "failure_stage": rec.get("failure_stage"),
                "timeline_types": dict(collections.Counter(types)),
                "converted_ops": conv_ops,
                "source_extrudes": extrudes,
                "sketch_flags": sketch_flags,
                "filtered_intersect": (meta.get("conversion") or {}).get("filtered_intersect", 0),
                "dsl_extent_kwargs": dsl_has_extent_kwargs(dsl_text),
                "dsl_ops": rec.get("operation_names") or [],
            }
        )

    n_pass = sum(1 for r in rows if r["label_pass"])
    overall = rate(n_pass, len(rows))

    two_by_two = {
        "any_containment": {
            "circle_one_side": any_cell(rows, "circle", False),
            "circle_two_side_or_symm": any_cell(rows, "circle", True),
            "rectangle_one_side": any_cell(rows, "rectangle", False),
            "rectangle_two_side_or_symm": any_cell(rows, "rectangle", True),
            "polygon_one_side": any_cell(rows, "polygon", False),
            "polygon_two_side_or_symm": any_cell(rows, "polygon", True),
        },
        "exclusive_within_profile": {
            "circle_one_side_only": exclusive_cell(rows, "circle", False),
            "circle_two_side_or_symm_only": exclusive_cell(rows, "circle", True),
            "rectangle_one_side_only": exclusive_cell(rows, "rectangle", False),
            "rectangle_two_side_or_symm_only": exclusive_cell(rows, "rectangle", True),
            "polygon_one_side_only": exclusive_cell(rows, "polygon", False),
            "polygon_two_side_or_symm_only": exclusive_cell(rows, "polygon", True),
        },
        "pure_profile_samples": {
            "only_circle_one_side": pure_cell(rows, "circle", False),
            "only_circle_two_side_or_symm": pure_cell(rows, "circle", True),
            "only_rectangle_one_side": pure_cell(rows, "rectangle", False),
            "only_rectangle_two_side_or_symm": pure_cell(rows, "rectangle", True),
            "only_polygon_one_side": pure_cell(rows, "polygon", False),
            "only_polygon_two_side_or_symm": pure_cell(rows, "polygon", True),
        },
    }

    def has_kind_side(r, kind, two):
        return any(
            o["profile_kind"] == kind and ((o["extent_type"] in NON_ONE) == two) for o in r["converted_ops"]
        )

    mixed_circle = summarize(
        rows, lambda r: has_kind_side(r, "circle", False) and has_kind_side(r, "circle", True)
    )
    mixed_rect = summarize(
        rows, lambda r: has_kind_side(r, "rectangle", False) and has_kind_side(r, "rectangle", True)
    )

    # Fine extent split for circle/rect shortcut vs polygon control.
    def cell_extent(kind: str, extent: str) -> dict[str, Any]:
        return summarize(
            rows,
            lambda r: any(o["profile_kind"] == kind and o["extent_type"] == extent for o in r["converted_ops"]),
        )

    fine_2x3 = {
        kind: {
            "OneSideFeatureExtentType": cell_extent(kind, ONE_SIDE),
            "TwoSidesFeatureExtentType": cell_extent(kind, TWO_SIDE),
            "SymmetricFeatureExtentType": cell_extent(kind, SYMM),
        }
        for kind in ("circle", "rectangle", "polygon", "hole")
    }

    # DSL emission check: did converted program actually carry extent kwargs?
    def dsl_kw_split(kind: str, two: bool) -> dict[str, Any]:
        hit = [r for r in rows if has_kind_side(r, kind, two)]
        with_kw = [r for r in hit if r["dsl_extent_kwargs"]["symmetric"] or r["dsl_extent_kwargs"]["height_two"]]
        without = [r for r in hit if r not in with_kw]
        return {
            "n": len(hit),
            "dsl_has_symmetric_or_height_two": len(with_kw),
            "dsl_missing_extent_kwargs": len(without),
            "pass_with_kwargs": sum(1 for r in with_kw if r["label_pass"]),
            "pass_without_kwargs": sum(1 for r in without if r["label_pass"]),
        }

    dsl_emission = {
        "circle_one_side": dsl_kw_split("circle", False),
        "circle_two_side_or_symm": dsl_kw_split("circle", True),
        "rectangle_one_side": dsl_kw_split("rectangle", False),
        "rectangle_two_side_or_symm": dsl_kw_split("rectangle", True),
        "polygon_one_side": dsl_kw_split("polygon", False),
        "polygon_two_side_or_symm": dsl_kw_split("polygon", True),
    }

    p0_extent = {
        "sample_has_any_two_side_or_symm": summarize(
            rows, lambda r: any(o["extent_type"] in NON_ONE for o in r["converted_ops"])
        ),
        "sample_all_one_side": summarize(
            rows,
            lambda r: bool(r["converted_ops"])
            and all(o["extent_type"] == ONE_SIDE for o in r["converted_ops"]),
        ),
        "source_extent_type_any": {
            et: summarize(rows, lambda r, e=et: any(x["extent_type"] == e for x in r["source_extrudes"]))
            for et in sorted(extent_type_counter)
        },
        "start_extent_any": {
            st: summarize(rows, lambda r, s=st: any(x["start_extent"] == s for x in r["source_extrudes"]))
            for st in sorted(start_extent_counter)
        },
        "any_negative_extent_one": summarize(
            rows, lambda r: any(x["negative_one"] for x in r["source_extrudes"])
        ),
        "any_negative_extent_two": summarize(
            rows, lambda r: any(x["negative_two"] for x in r["source_extrudes"])
        ),
        "any_negative_distance": summarize(
            rows, lambda r: any(x["negative_one"] or x["negative_two"] for x in r["source_extrudes"])
        ),
        "all_nonnegative_distance": summarize(
            rows,
            lambda r: bool(r["source_extrudes"])
            and not any(x["negative_one"] or x["negative_two"] for x in r["source_extrudes"]),
        ),
        "negative_one_AND_all_one_side": summarize(
            rows,
            lambda r: any(x["negative_one"] for x in r["source_extrudes"])
            and bool(r["converted_ops"])
            and all(o["extent_type"] == ONE_SIDE for o in r["converted_ops"]),
        ),
        "negative_one_AND_has_two_side": summarize(
            rows,
            lambda r: any(x["negative_one"] for x in r["source_extrudes"])
            and any(o["extent_type"] in NON_ONE for o in r["converted_ops"]),
        ),
    }

    p1 = {
        "timeline_feature_types": dict(timeline_counter),
        "revolve_present": summarize(rows, lambda r: any("Revolve" in k for k in r["timeline_types"])),
        "non_sketch_extrude_timeline": summarize(
            rows,
            lambda r: any(k not in ("Sketch", "ExtrudeFeature") for k in r["timeline_types"]),
        ),
        "any_sketch_origin_nonzero": summarize(
            rows, lambda r: any(s["origin_nonzero"] for s in r["sketch_flags"])
        ),
        "all_sketch_origin_zero": summarize(
            rows,
            lambda r: bool(r["sketch_flags"]) and not any(s["origin_nonzero"] for s in r["sketch_flags"]),
        ),
        "any_sketch_axis_noncanonical": summarize(
            rows, lambda r: any(s["x_not_ex"] or s["z_not_ez"] for s in r["sketch_flags"])
        ),
        "all_sketch_axis_canonical": summarize(
            rows,
            lambda r: bool(r["sketch_flags"])
            and not any(s["x_not_ex"] or s["z_not_ez"] for s in r["sketch_flags"]),
        ),
        "boolean_any": {
            op: summarize(rows, lambda r, o=op: any(x["operation"] == o for x in r["source_extrudes"]))
            for op in sorted(boolean_counter)
        },
        "only_newbody": summarize(
            rows,
            lambda r: bool(r["source_extrudes"])
            and all(x["operation"] == "NewBodyFeatureOperation" for x in r["source_extrudes"]),
        ),
        "has_cut": summarize(
            rows, lambda r: any(x["operation"] == "CutFeatureOperation" for x in r["source_extrudes"])
        ),
        "has_join": summarize(
            rows, lambda r: any(x["operation"] == "JoinFeatureOperation" for x in r["source_extrudes"])
        ),
        "filtered_intersect": summarize(rows, lambda r: int(r.get("filtered_intersect") or 0) > 0),
        "dsl_has_cut": summarize(rows, lambda r: "Cut" in r["dsl_ops"]),
        "dsl_has_union": summarize(rows, lambda r: "Union" in r["dsl_ops"]),
        "dsl_no_boolean": summarize(
            rows, lambda r: "Cut" not in r["dsl_ops"] and "Union" not in r["dsl_ops"]
        ),
    }

    p2 = {
        "has_circle_body": summarize(rows, lambda r: any(o["profile_kind"] == "circle" for o in r["converted_ops"])),
        "has_rectangle_body": summarize(
            rows, lambda r: any(o["profile_kind"] == "rectangle" for o in r["converted_ops"])
        ),
        "has_polygon_body": summarize(
            rows, lambda r: any(o["profile_kind"] == "polygon" for o in r["converted_ops"])
        ),
        "has_hole": summarize(rows, lambda r: any(o["profile_kind"] == "hole" for o in r["converted_ops"])),
        "only_circle_bodies": summarize(
            rows,
            lambda r: bool(r["converted_ops"])
            and all(o["profile_kind"] in ("circle", "hole") for o in r["converted_ops"])
            and any(o["profile_kind"] == "circle" for o in r["converted_ops"]),
        ),
        "only_rectangle_bodies": summarize(
            rows,
            lambda r: bool(r["converted_ops"])
            and all(o["profile_kind"] in ("rectangle", "hole") for o in r["converted_ops"])
            and any(o["profile_kind"] == "rectangle" for o in r["converted_ops"]),
        ),
        "fillet_chamfer_pattern_timeline": summarize(
            rows,
            lambda r: any(
                any(tok in k.lower() for tok in ("fillet", "chamfer", "pattern", "mirror", "circular"))
                for k in r["timeline_types"]
            ),
        ),
    }

    # Residual after removing the 2x2 smoking-gun set.
    smoking = [
        r
        for r in rows
        if any(
            o["profile_kind"] in ("circle", "rectangle") and o["extent_type"] in NON_ONE for o in r["converted_ops"]
        )
    ]
    residual = [r for r in rows if r not in smoking]
    residual_fail = [r for r in residual if not r["label_pass"]]

    # Overlap of remaining P0/P1 flags among residual failures.
    def flag_set(r: dict) -> list[str]:
        flags = []
        if any(x["negative_one"] or x["negative_two"] for x in r["source_extrudes"]):
            flags.append("negative_extent_distance")
        if any(x["start_extent"] not in (None, "ProfilePlaneStartDefinition") for x in r["source_extrudes"]):
            flags.append("non_profile_plane_start")
        if any(s["origin_nonzero"] or s["x_not_ex"] or s["z_not_ez"] for s in r["sketch_flags"]):
            flags.append("noncanonical_sketch_frame")
        if any(x["operation"] in ("CutFeatureOperation", "JoinFeatureOperation", "IntersectFeatureOperation") for x in r["source_extrudes"]):
            flags.append("boolean_cut_join_intersect")
        if any(o["profile_kind"] == "polygon" for o in r["converted_ops"]):
            flags.append("polygon_profile")
        if any(o["profile_kind"] == "hole" for o in r["converted_ops"]):
            flags.append("hole")
        if int(r.get("filtered_intersect") or 0) > 0:
            flags.append("filtered_intersect")
        if not r.get("execution_ok"):
            flags.append("execution_fail")
        elif not r.get("step_reload"):
            flags.append("reload_fail")
        return flags or ["unflagged"]

    residual_flag_counts = collections.Counter()
    for r in residual_fail:
        residual_flag_counts.update(flag_set(r))

    examples = {}
    for key, pred in [
        ("circle_one_side_pass", lambda r: has_kind_side(r, "circle", False) and r["label_pass"]),
        ("circle_two_side_fail", lambda r: has_kind_side(r, "circle", True) and not r["label_pass"]),
        ("rectangle_one_side_pass", lambda r: has_kind_side(r, "rectangle", False) and r["label_pass"]),
        ("rectangle_two_side_fail", lambda r: has_kind_side(r, "rectangle", True) and not r["label_pass"]),
        ("polygon_two_side_pass", lambda r: has_kind_side(r, "polygon", True) and r["label_pass"]),
        ("polygon_two_side_fail", lambda r: has_kind_side(r, "polygon", True) and not r["label_pass"]),
        ("pure_circle_one_side_pass", lambda r: r["cad_id"] in {x["cad_id"] for x in rows} and False),
    ]:
        hit = [r for r in rows if pred(r)]
        examples[key] = [
            {
                "cad_id": r["cad_id"],
                "chamfer_rel": r["chamfer_rel"],
                "coverage_02": r["coverage_02"],
                "converted_ops": r["converted_ops"][:6],
                "dsl_extent_kwargs": r["dsl_extent_kwargs"],
            }
            for r in hit[:5]
        ]

    # Fill pure-circle examples from the pure-cell predicate.
    def dump_pred(pred, n=5):
        return [
            {
                "cad_id": r["cad_id"],
                "label_pass": r["label_pass"],
                "chamfer_rel": r["chamfer_rel"],
                "coverage_02": r["coverage_02"],
                "converted_ops": r["converted_ops"][:8],
                "source_extrudes": r["source_extrudes"][:4],
                "dsl_extent_kwargs": r["dsl_extent_kwargs"],
            }
            for r in rows
            if pred(r)
        ][:n]

    examples["pure_circle_one_side"] = dump_pred(
        lambda r: all(o["profile_kind"] == "circle" for o in r["converted_ops"])
        and bool(r["converted_ops"])
        and all(o["extent_type"] == ONE_SIDE for o in r["converted_ops"])
    )
    examples["pure_circle_two_side"] = dump_pred(
        lambda r: all(o["profile_kind"] == "circle" for o in r["converted_ops"])
        and bool(r["converted_ops"])
        and all(o["extent_type"] in NON_ONE for o in r["converted_ops"])
    )
    examples["pure_rectangle_one_side"] = dump_pred(
        lambda r: all(o["profile_kind"] == "rectangle" for o in r["converted_ops"])
        and bool(r["converted_ops"])
        and all(o["extent_type"] == ONE_SIDE for o in r["converted_ops"])
    )
    examples["pure_rectangle_two_side"] = dump_pred(
        lambda r: all(o["profile_kind"] == "rectangle" for o in r["converted_ops"])
        and bool(r["converted_ops"])
        and all(o["extent_type"] in NON_ONE for o in r["converted_ops"])
    )

    converter_evidence = {
        "circle_shortcut_drops_extent": "fusion360_to_dsl.py:_emit_extrude_body circle branch emits Extrude(Circle(...), height=extent_one) and never writes symmetric/height_two",
        "rectangle_shortcut_drops_extent": "same function Box(...) branch also omits symmetric/height_two",
        "polygon_and_hole_emit_extent": "ExtrudePolygon branch does append symmetric=True or height_two",
        "executor_circle_box_one_side_only": "cad_dsl.py Extrude/Box have no height_two/symmetric kwargs; ExtrudePolygon does",
        "negative_distance_abs": "_parse_extent uses abs(distance), dropping reverse direction",
        "start_extent_filtered": "only ProfilePlaneStartDefinition accepted; other start offsets raise filter or are absent in this 602",
    }

    report = {
        "n": 602,
        "overall": overall,
        "thresholds": {"chamfer_rel_max": 0.01, "coverage_02_min": 0.98},
        "primary_2x2": two_by_two,
        "mixed_within_profile": {"circle_has_both_sides": mixed_circle, "rectangle_has_both_sides": mixed_rect},
        "fine_profile_x_extent_type": fine_2x3,
        "dsl_extent_kwarg_emission": dsl_emission,
        "P0_extent_start_direction": p0_extent,
        "P1_revolve_transform_boolean": p1,
        "P2_sketch_and_local_ops": p2,
        "smoking_gun_circle_rect_non_one_side": {
            "n": len(smoking),
            "pass": sum(1 for r in smoking if r["label_pass"]),
            "fail": sum(1 for r in smoking if not r["label_pass"]),
        },
        "residual_after_removing_smoking_gun": {
            "n": len(residual),
            "pass": sum(1 for r in residual if r["label_pass"]),
            "fail": len(residual_fail),
            "fail_flag_counts": dict(residual_flag_counts),
        },
        "source_counters": {
            "timeline": dict(timeline_counter),
            "extent_type": dict(extent_type_counter),
            "start_extent": dict(start_extent_counter),
            "boolean": dict(boolean_counter),
        },
        "converter_code_evidence": converter_evidence,
        "examples": examples,
        "interpretation": {
            "do_not_blame_circle_rectangle_sketch": None,
            "blame_extrude_extent_on_circle_rect_shortcut": None,
        },
    }

    # Interpretation filled from the exclusive/pure numbers.
    c1 = two_by_two["exclusive_within_profile"]["circle_one_side_only"]
    c2 = two_by_two["exclusive_within_profile"]["circle_two_side_or_symm_only"]
    r1 = two_by_two["exclusive_within_profile"]["rectangle_one_side_only"]
    r2 = two_by_two["exclusive_within_profile"]["rectangle_two_side_or_symm_only"]
    p1c = two_by_two["exclusive_within_profile"]["polygon_one_side_only"]
    p2c = two_by_two["exclusive_within_profile"]["polygon_two_side_or_symm_only"]
    report["interpretation"] = {
        "circle_one_side_pass_rate": c1["pass_rate"],
        "circle_two_side_pass_rate": c2["pass_rate"],
        "rectangle_one_side_pass_rate": r1["pass_rate"],
        "rectangle_two_side_pass_rate": r2["pass_rate"],
        "polygon_one_side_pass_rate": p1c["pass_rate"],
        "polygon_two_side_pass_rate": p2c["pass_rate"],
        "pattern_matches_extent_not_sketch": (
            (c1["pass_rate"] or 0) > 0
            and (c2["n"] and c2["pass"] == 0)
            and (r1["pass_rate"] or 0) > 0
            and (r2["n"] and r2["pass"] == 0)
        ),
        "polygon_control_not_zero": (p2c["pass"] or 0) > 0,
        "note": (
            "If circle/rect one-side pass and two-side/symm fail, while polygon two-side is not 0/N, "
            "the failure is the Extrude/Box shortcut dropping extent kwargs, not circle/rectangle sketch parameterization."
        ),
    }

    save(OUT / "op_param_attribution.json", report)

    def pct(cell):
        if not cell["n"]:
            return "n=0"
        return f"{cell['pass']}/{cell['n']} = {100 * cell['pass_rate']:.1f}%"

    lines = [
        "# Fusion360 602：按 CAD operation 参数类型的失败归因",
        "",
        "单位合同已修；本报告只诊断 residual label geometry，不改转换器。通过定义与 602 复测相同：Chamfer≤0.01 且 coverage≥0.98。",
        "",
        f"总体：{overall['pass']}/{overall['n']} = {100 * overall['pass_rate']:.2f}% 通过。",
        "",
        "## 主对照：不要把根因归到圆/矩形 sketch",
        "",
        "圆/矩形快捷分支（`Extrude(Circle)` / `Box`）不写 `symmetric` / `height_two`；polygon 分支会写。因此必须拆开 profile × extent。",
        "",
        "### 2×2（样本含该类操作，可重叠）",
        "",
        "| profile | one-side | two-side / symmetric |",
        "|---|---:|---:|",
        f"| circle | {pct(two_by_two['any_containment']['circle_one_side'])} | {pct(two_by_two['any_containment']['circle_two_side_or_symm'])} |",
        f"| rectangle | {pct(two_by_two['any_containment']['rectangle_one_side'])} | {pct(two_by_two['any_containment']['rectangle_two_side_or_symm'])} |",
        f"| polygon（对照） | {pct(two_by_two['any_containment']['polygon_one_side'])} | {pct(two_by_two['any_containment']['polygon_two_side_or_symm'])} |",
        "",
        "### 2×2（同一 profile 的 extent 类型互斥：只有 one-side，或只有 two-side/symm）",
        "",
        "| profile | only one-side | only two-side / symmetric |",
        "|---|---:|---:|",
        f"| circle | {pct(c1)} | {pct(c2)} |",
        f"| rectangle | {pct(r1)} | {pct(r2)} |",
        f"| polygon（对照） | {pct(p1c)} | {pct(p2c)} |",
        "",
        "### 2×2（纯样本：转换结果里非 hole body 全是该 profile）",
        "",
        "| profile | only one-side | only two-side / symmetric |",
        "|---|---:|---:|",
        f"| circle | {pct(two_by_two['pure_profile_samples']['only_circle_one_side'])} | {pct(two_by_two['pure_profile_samples']['only_circle_two_side_or_symm'])} |",
        f"| rectangle | {pct(two_by_two['pure_profile_samples']['only_rectangle_one_side'])} | {pct(two_by_two['pure_profile_samples']['only_rectangle_two_side_or_symm'])} |",
        f"| polygon（对照） | {pct(two_by_two['pure_profile_samples']['only_polygon_one_side'])} | {pct(two_by_two['pure_profile_samples']['only_polygon_two_side_or_symm'])} |",
        "",
        "### DSL 是否真的写出了 extent kwargs",
        "",
        "| 集合 | n | DSL 含 symmetric/height_two | 其中通过 | DSL 无 kwargs 且通过 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, cell in dsl_emission.items():
        lines.append(
            f"| {name} | {cell['n']} | {cell['dsl_has_symmetric_or_height_two']} | {cell['pass_with_kwargs']} | {cell['pass_without_kwargs']} |"
        )

    lines += [
        "",
        f"同一 profile 同时含 one-side 与 two-side 的样本：circle {mixed_circle['n']}，rectangle {mixed_rect['n']}。",
        "",
        "## P0 其余：extent type / start offset / direction",
        "",
        f"- 全部 one-side：{pct(p0_extent['sample_all_one_side'])}",
        f"- 含 two-side 或 symmetric：{pct(p0_extent['sample_has_any_two_side_or_symm'])}",
        f"- 含负 extent 距离：{pct(p0_extent['any_negative_distance'])}",
        f"- 全部非负距离：{pct(p0_extent['all_nonnegative_distance'])}",
        f"- 负 extent_one 且全部 one-side：{pct(p0_extent['negative_one_AND_all_one_side'])}",
        f"- 负距离且含 two-side：{pct(p0_extent['negative_one_AND_has_two_side'])}",
        "",
        "源 extent_type 样本通过率：",
    ]
    for et, cell in p0_extent["source_extent_type_any"].items():
        lines.append(f"- `{et}`: {pct(cell)}")
    lines.append("")
    lines.append("start_extent 样本通过率：")
    for st, cell in p0_extent["start_extent_any"].items():
        lines.append(f"- `{st}`: {pct(cell)}")

    lines += [
        "",
        "## P1：revolve / sketch frame / boolean",
        "",
        f"- timeline 类型计数：{dict(timeline_counter)}",
        f"- 含 Revolve：{pct(p1['revolve_present'])}",
        f"- timeline 出现 Sketch/Extrude 以外类型：{pct(p1['non_sketch_extrude_timeline'])}",
        f"- sketch origin 非零：{pct(p1['any_sketch_origin_nonzero'])}",
        f"- sketch origin 全为零：{pct(p1['all_sketch_origin_zero'])}",
        f"- sketch 轴非 canonical：{pct(p1['any_sketch_axis_noncanonical'])}",
        f"- sketch 轴全 canonical：{pct(p1['all_sketch_axis_canonical'])}",
        f"- 仅 NewBody：{pct(p1['only_newbody'])}",
        f"- 含 Cut：{pct(p1['has_cut'])}",
        f"- 含 Join：{pct(p1['has_join'])}",
        f"- 被过滤的 Intersect：{pct(p1['filtered_intersect'])}",
        f"- DSL 无 Cut/Union：{pct(p1['dsl_no_boolean'])}",
        "",
        "## P2：circle/rectangle 参数化与局部操作",
        "",
        f"- 含 circle body：{pct(p2['has_circle_body'])}",
        f"- 含 rectangle body：{pct(p2['has_rectangle_body'])}",
        f"- 含 polygon body：{pct(p2['has_polygon_body'])}",
        f"- 含 hole：{pct(p2['has_hole'])}",
        f"- fillet/chamfer/pattern timeline：{pct(p2['fillet_chamfer_pattern_timeline'])}",
        "",
        "## 吸烟枪集合拿掉之后还剩什么",
        "",
        f"圆/矩形非单侧拉伸：{report['smoking_gun_circle_rect_non_one_side']['fail']}/{report['smoking_gun_circle_rect_non_one_side']['n']} 失败。",
        f"去掉这 {report['smoking_gun_circle_rect_non_one_side']['n']} 条后：通过 {report['residual_after_removing_smoking_gun']['pass']}/{report['residual_after_removing_smoking_gun']['n']}，失败 {report['residual_after_removing_smoking_gun']['fail']}。",
        f"剩余失败上的共存标记（可重叠）：{report['residual_after_removing_smoking_gun']['fail_flag_counts']}",
        "",
        "## 结论",
        "",
        f"- circle one-side {pct(c1)} vs two-side/symm {pct(c2)}",
        f"- rectangle one-side {pct(r1)} vs two-side/symm {pct(r2)}",
        f"- polygon 对照 one-side {pct(p1c)} vs two-side/symm {pct(p2c)}",
        f"- 模式是否符合“extent converter 而非 sketch converter”：{report['interpretation']['pattern_matches_extent_not_sketch']}",
        f"- polygon two-side 是否并非全灭（说明 DSL 执行器能处理双侧，问题在圆/矩形快捷分支丢参数）：{report['interpretation']['polygon_control_not_zero']}",
        "",
        "下一步应修 `fusion360_to_dsl.py` 的 circle/rectangle 快捷分支，把 symmetric/height_two 传下去；并让 `cad_dsl.py` 的 Extrude/Box 接受这两类 extent。负距离方向与 polygon 残差是第二优先级，本报告不修代码。",
        "",
    ]
    with (OUT / "OP_PARAM_ATTRIBUTION.md").open("x") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({"out": str(OUT), "overall": overall, "interpretation": report["interpretation"]}, indent=2))


if __name__ == "__main__":
    main()
