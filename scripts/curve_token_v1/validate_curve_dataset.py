#!/usr/bin/env python3
"""Geometry-level validation of the Track B curve dataset.

This does not merely check that the JSON parses. For every curve it re-opens the
original STEP, rebuilds the curve from the *stored parameters* (both through the
CAD kernel and through the OCC-free numpy evaluator), and measures the deviation
from OCC's own evaluation of the original edge.

Checks per curve:
  - parameter-level: type-specific errors vs freshly re-extracted OCC parameters
  - geometry-level : OCC-rebuild point error, numpy-rebuild point error,
                     endpoint error, tangent angular error, Chamfer distance
  - sampled arrays : npz xyz vs OCC evaluation at the stored parameters,
                     normalized arrays vs the stored normalization transform
Any NaN / Inf is reported with its cad_id and edge_id; nothing is silently skipped.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from .config import (
    RECON_ABS_TOL_MIN,
    RECON_REL_TOL,
    SPLITS,
    STEP_FILENAME,
    TANGENT_ANGLE_TOL_DEG,
    VALIDATION_DIR,
    cad_dir,
    split_dir,
)
from .curve_eval import UnsupportedCurve, evaluate
from .extract_brep_curves import _extract_type_params
from .occ_curve_v1 import (
    eval_point,
    eval_point_tangent,
    load_step_shape,
    make_adaptor,
    pnt_to_np,
    rebuild_occ_curve,
)

N_CHECK = 32
N_DENSE = 256
EPS32 = float(np.finfo(np.float32).eps)


def _finite(x) -> bool:
    a = np.asarray(x, dtype=np.float64)
    return bool(a.size) and bool(np.all(np.isfinite(a)))


def _angle_deg(a, b) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return float("nan")
    c = float(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0))
    return math.degrees(math.acos(c))


def _axis_angle_deg(a, b) -> float:
    """Angle between undirected axes: a and -a are the same axis."""
    ang = _angle_deg(a, b)
    return float(min(ang, 180.0 - ang)) if np.isfinite(ang) else ang


def _chamfer(a: np.ndarray, b: np.ndarray) -> float:
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    return float(0.5 * (d.min(axis=1).mean() + d.min(axis=0).mean()))


def _eval_geom(geom, u: float, periodic: bool, lo: float, hi: float) -> np.ndarray:
    if not periodic:
        u = float(np.clip(u, lo, hi))
    return pnt_to_np(geom.Value(float(u)))


def _geom_tangent(geom, u: float, periodic: bool, lo: float, hi: float) -> np.ndarray:
    from OCP.gp import gp_Pnt, gp_Vec

    if not periodic:
        u = float(np.clip(u, lo, hi))
    p, v = gp_Pnt(), gp_Vec()
    geom.D1(float(u), p, v)
    t = np.array([v.X(), v.Y(), v.Z()], dtype=np.float64)
    n = float(np.linalg.norm(t))
    return t / n if n > 1e-12 else np.zeros(3)


# --------------------------------------------------- type-specific checks ----
def _param_level_errors(curve_type: str, stored: dict, fresh: dict) -> dict:
    """Compare stored parameters against parameters re-extracted from OCC now."""
    out: dict = {}
    if not stored or not fresh:
        return out
    try:
        if curve_type == "LINE":
            out["direction_angle_err_deg"] = _angle_deg(stored["direction"], fresh["direction"])
            out["origin_err"] = float(
                np.linalg.norm(np.asarray(stored["origin"]) - np.asarray(fresh["origin"]))
            )
        elif curve_type == "CIRCLE":
            out["center_err"] = float(
                np.linalg.norm(np.asarray(stored["center"]) - np.asarray(fresh["center"]))
            )
            out["radius_err"] = abs(float(stored["radius"]) - float(fresh["radius"]))
            out["normal_angle_err_deg"] = _axis_angle_deg(stored["normal"], fresh["normal"])
            out["x_axis_angle_err_deg"] = _angle_deg(stored["x_axis"], fresh["x_axis"])
            # y_axis must equal normal x x_axis for the stored frame to be usable
            out["frame_handedness_err"] = float(
                np.linalg.norm(
                    np.cross(np.asarray(stored["normal"]), np.asarray(stored["x_axis"]))
                    - np.asarray(stored["y_axis"])
                )
            )
        elif curve_type == "ELLIPSE":
            out["center_err"] = float(
                np.linalg.norm(np.asarray(stored["center"]) - np.asarray(fresh["center"]))
            )
            out["major_radius_err"] = abs(
                float(stored["major_radius"]) - float(fresh["major_radius"])
            )
            out["minor_radius_err"] = abs(
                float(stored["minor_radius"]) - float(fresh["minor_radius"])
            )
            out["normal_angle_err_deg"] = _axis_angle_deg(stored["normal"], fresh["normal"])
            out["major_axis_angle_err_deg"] = _axis_angle_deg(
                stored["major_axis"], fresh["major_axis"]
            )
            out["frame_handedness_err"] = float(
                np.linalg.norm(
                    np.cross(np.asarray(stored["normal"]), np.asarray(stored["major_axis"]))
                    - np.asarray(stored["minor_axis"])
                )
            )
        elif curve_type in ("BSPLINE", "BEZIER"):
            out["degree_match"] = int(stored["degree"]) == int(fresh["degree"])
            out["n_control_points_match"] = int(stored["num_control_points"]) == int(
                fresh["num_control_points"]
            )
            out["control_point_max_err"] = float(
                np.abs(
                    np.asarray(stored["control_points"]) - np.asarray(fresh["control_points"])
                ).max()
            )
            out["knot_max_err"] = float(
                np.abs(np.asarray(stored["knots"]) - np.asarray(fresh["knots"])).max()
            )
            out["multiplicity_match"] = list(map(int, stored["multiplicities"])) == list(
                map(int, fresh["multiplicities"])
            )
            out["weight_max_err"] = float(
                np.abs(np.asarray(stored["weights"]) - np.asarray(fresh["weights"])).max()
            )
            # A non-periodic B-spline needs sum(mults) == n_ctrl + degree + 1 to be
            # reconstructible; record it explicitly rather than trusting OCC.
            out["knot_vector_consistent"] = bool(
                stored["is_periodic"]
                or int(stored["knot_multiplicity_sum"])
                == int(stored["num_control_points"]) + int(stored["degree"]) + 1
            )
    except Exception as exc:  # noqa: BLE001
        out["param_compare_error"] = f"{type(exc).__name__}: {exc}"
    return out


def validate_one(split: str, cad_id: str) -> dict:
    out_dir = cad_dir(split, cad_id)
    cj = out_dir / "curves.json"
    if not cj.is_file():
        return {"cad_id": cad_id, "split": split, "ok": False, "error": "missing curves.json"}

    data = json.loads(cj.read_text(encoding="utf-8"))
    topology = json.loads((out_dir / "topology.json").read_text(encoding="utf-8"))
    nz = json.loads((out_dir / "normalization.json").read_text(encoding="utf-8"))
    npz = np.load(out_dir / "curve_samples.npz", allow_pickle=False)

    step_path = SPLITS[split]["step_root"] / cad_id / STEP_FILENAME
    shape = load_step_shape(step_path)

    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp
    from OCP.TopoDS import TopoDS
    from OCP.TopTools import TopTools_IndexedMapOfShape

    emap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, emap)

    diag = float(data["source_diagonal"])
    tol = max(RECON_REL_TOL * diag, RECON_ABS_TOL_MIN)
    s, t = float(nz["scale"]), np.asarray(nz["translation"], dtype=np.float64)

    records = data["curves"]
    per_curve: list[dict] = []
    failures: list[dict] = []
    nan_reports: list[dict] = []

    # --- npz <-> curves.json consistency -------------------------------------
    struct_issues: list[str] = []
    if int(npz["num_curves"][0]) != len(records):
        struct_issues.append(f"npz num_curves={int(npz['num_curves'][0])} != json {len(records)}")
    if npz["curve_xyz"].shape[0] != len(records):
        struct_issues.append(f"curve_xyz rows={npz['curve_xyz'].shape[0]} != {len(records)}")
    if not np.array_equal(npz["curve_edge_id"], np.array([r["edge_id"] for r in records], np.int32)):
        struct_issues.append("curve_edge_id order mismatch vs curves.json")

    xyz = npz["curve_xyz"].astype(np.float64)
    xyz_n = npz["curve_xyz_normalized"].astype(np.float64)
    tangents = npz["curve_tangent"].astype(np.float64)
    us = npz["curve_u"].astype(np.float64)

    if xyz.size:
        # both arrays are float32, so the transform can only be reproduced to
        # float32 precision at the magnitude of the larger of the two
        norm_err = float(np.abs((s * xyz + t) - xyz_n).max())
        budget = 8 * EPS32 * max(float(np.abs(xyz).max()) * abs(s), float(np.abs(xyz_n).max()), 1.0)
        if not np.isfinite(norm_err) or norm_err > max(budget, tol):
            struct_issues.append(
                f"normalized array mismatch: max err {norm_err:.3e} > budget {budget:.3e}"
            )
    else:
        norm_err = 0.0

    tan_norms = np.linalg.norm(tangents, axis=2)
    valid_mask = npz["curve_mask"]
    bad_tan = int(((np.abs(tan_norms - 1.0) > 1e-3) & valid_mask).sum())
    if bad_tan:
        struct_issues.append(f"{bad_tan} sampled tangents are not unit length")

    for idx, rec in enumerate(records):
        eid = int(rec["edge_id"])
        ctype = rec["curve_type"]
        stored = rec.get("world_parameters", {})
        entry: dict = {"edge_id": eid, "curve_type": ctype}
        problems: list[str] = []

        adaptor = make_adaptor(TopoDS.Edge_s(emap.FindKey(eid + 1)))
        u0, u1 = float(rec["u_start"]), float(rec["u_end"])
        check_us = np.linspace(u0, u1, N_CHECK)
        occ_pts = np.array([eval_point(adaptor, float(u)) for u in check_us])

        # --- parameter level --------------------------------------------------
        fresh, fresh_err = _extract_type_params(adaptor, ctype)
        entry.update(_param_level_errors(ctype, stored, fresh))
        if fresh_err and stored:
            problems.append(f"reextract_failed: {fresh_err}")

        param_ok = bool(rec["extraction"]["parameter_extraction_ok"])
        if param_ok:
            numeric = [v for k, v in entry.items() if isinstance(v, float)]
            if any(not math.isfinite(v) for v in numeric):
                problems.append("non-finite parameter-level error")
            for key, val in entry.items():
                if key.endswith("_err") and isinstance(val, float) and val > tol:
                    problems.append(f"{key}={val:.3e} > tol {tol:.3e}")
                if key.endswith("_angle_err_deg") and isinstance(val, float) and val > TANGENT_ANGLE_TOL_DEG:
                    problems.append(f"{key}={val:.4f}deg")
                if key.endswith("_match") and val is False:
                    problems.append(f"{key}=False")
                if key == "knot_vector_consistent" and val is False:
                    problems.append("knot_vector_inconsistent")

        # --- endpoints --------------------------------------------------------
        entry["endpoint_err"] = max(
            float(np.linalg.norm(np.asarray(rec["start_point"]) - eval_point(adaptor, u0))),
            float(np.linalg.norm(np.asarray(rec["end_point"]) - eval_point(adaptor, u1))),
        )
        if entry["endpoint_err"] > tol:
            problems.append(f"endpoint_err={entry['endpoint_err']:.3e}")

        # --- OCC rebuild from stored parameters --------------------------------
        entry["occ_rebuild_max_err"] = None
        entry["tangent_angle_err_max_deg"] = None
        entry["chamfer"] = None
        if stored:
            try:
                geom = rebuild_occ_curve(ctype, stored)
                periodic = bool(stored.get("is_periodic", False)) or ctype in ("CIRCLE", "ELLIPSE")
                lo, hi = float(geom.FirstParameter()), float(geom.LastParameter())
                if not np.isfinite(lo) or not np.isfinite(hi):
                    lo, hi = u0, u1
                rb = np.array([_eval_geom(geom, float(u), periodic, lo, hi) for u in check_us])
                err = np.linalg.norm(rb - occ_pts, axis=1)
                entry["occ_rebuild_max_err"] = float(err.max())
                entry["occ_rebuild_mean_err"] = float(err.mean())

                ang = []
                for u in check_us:
                    t_ref = eval_point_tangent(adaptor, float(u))[1]
                    t_rb = _geom_tangent(geom, float(u), periodic, lo, hi)
                    a = _angle_deg(t_ref, t_rb)
                    if np.isfinite(a):
                        ang.append(min(a, 180.0 - a) if a > 90.0 else a)
                entry["tangent_angle_err_max_deg"] = float(max(ang)) if ang else float("nan")

                dense_u = np.linspace(u0, u1, N_DENSE)
                dense_occ = np.array([eval_point(adaptor, float(u)) for u in dense_u])
                dense_rb = np.array([_eval_geom(geom, float(u), periodic, lo, hi) for u in dense_u])
                entry["chamfer"] = _chamfer(dense_rb, dense_occ)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"occ_rebuild_failed: {type(exc).__name__}: {exc}")

        # --- numpy (OCC-free) rebuild ------------------------------------------
        entry["numpy_rebuild_max_err"] = None
        if stored:
            try:
                np_pts = evaluate(ctype, stored, check_us)
                entry["numpy_rebuild_max_err"] = float(
                    np.linalg.norm(np_pts - occ_pts, axis=1).max()
                )
            except UnsupportedCurve as exc:
                entry["numpy_rebuild_note"] = str(exc)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"numpy_rebuild_failed: {type(exc).__name__}: {exc}")

        # --- sampled arrays ----------------------------------------------------
        # curve_xyz / curve_xyz_normalized are stored as float32, so the achievable
        # accuracy is set by the *magnitude* of the coordinates, not by the bbox
        # size: a small part located far from the origin loses precision in world
        # space while its normalized copy does not.
        m = valid_mask[idx]
        if m.any():
            samp_occ = np.array([eval_point(adaptor, float(u)) for u in us[idx][m]])
            entry["sample_xyz_max_err"] = float(
                np.linalg.norm(xyz[idx][m] - samp_occ, axis=1).max()
            )
            entry["sample_xyz_normalized_max_err"] = float(
                np.linalg.norm(xyz_n[idx][m] - (s * samp_occ + t), axis=1).max()
            )
            world_mag = float(np.abs(samp_occ).max())
            norm_mag = float(np.abs(s * samp_occ + t).max())
            entry["sample_world_float32_budget"] = max(tol, 8 * EPS32 * max(world_mag, 1.0))
            entry["sample_normalized_float32_budget"] = max(tol, 8 * EPS32 * max(norm_mag, 1.0))
            if entry["sample_xyz_max_err"] > entry["sample_world_float32_budget"]:
                problems.append(
                    f"sample_xyz_max_err={entry['sample_xyz_max_err']:.3e} exceeds "
                    f"float32 budget {entry['sample_world_float32_budget']:.3e}"
                )
            if (
                entry["sample_xyz_normalized_max_err"]
                > entry["sample_normalized_float32_budget"]
            ):
                problems.append(
                    f"sample_xyz_normalized_max_err="
                    f"{entry['sample_xyz_normalized_max_err']:.3e} exceeds float32 budget "
                    f"{entry['sample_normalized_float32_budget']:.3e}"
                )
        else:
            entry["sample_xyz_max_err"] = float("nan")
            entry["sample_xyz_normalized_max_err"] = float("nan")
            problems.append("no valid samples")

        exact_len = float(rec["length"])
        poly_len = float(npz["curve_polyline_length"][idx])
        entry["sampled_length_rel_err"] = (
            abs(poly_len - exact_len) / exact_len if exact_len > 0 else float("nan")
        )

        # --- NaN / Inf sweep ---------------------------------------------------
        for name, arr in (
            ("curve_xyz", xyz[idx]),
            ("curve_xyz_normalized", xyz_n[idx]),
            ("curve_tangent", tangents[idx]),
            ("curve_u", us[idx]),
            ("start_point", rec["start_point"]),
            ("end_point", rec["end_point"]),
        ):
            if not _finite(arr):
                nan_reports.append(
                    {"split": split, "cad_id": cad_id, "edge_id": eid, "field": name}
                )
                problems.append(f"non_finite:{name}")
        for key in ("control_points", "knots", "weights", "center", "origin", "normal"):
            if key in stored and not _finite(stored[key]):
                nan_reports.append(
                    {"split": split, "cad_id": cad_id, "edge_id": eid, "field": f"world_parameters.{key}"}
                )
                problems.append(f"non_finite:{key}")

        # --- verdicts ----------------------------------------------------------
        geom_tol_ok = (
            entry["occ_rebuild_max_err"] is not None
            and math.isfinite(entry["occ_rebuild_max_err"])
            and entry["occ_rebuild_max_err"] <= tol
        )
        tan_ok = entry["tangent_angle_err_max_deg"] is None or (
            math.isfinite(entry["tangent_angle_err_max_deg"])
            and entry["tangent_angle_err_max_deg"] <= TANGENT_ANGLE_TOL_DEG
        )
        entry["param_pass"] = bool(param_ok and not problems)
        entry["geom_pass"] = bool(geom_tol_ok and tan_ok and not problems)
        entry["problems"] = problems
        per_curve.append(entry)
        if problems:
            failures.append(
                {"split": split, "cad_id": cad_id, "edge_id": eid, "curve_type": ctype,
                 "problems": problems}
            )

    n = max(len(per_curve), 1)
    summary = {
        "cad_id": cad_id,
        "split": split,
        "ok": True,
        "num_curves": len(per_curve),
        "structural_issues": struct_issues,
        "normalized_array_max_err": norm_err,
        "n_param_pass": sum(1 for e in per_curve if e["param_pass"]),
        "n_geom_pass": sum(1 for e in per_curve if e["geom_pass"]),
        "topology_valid": bool(topology["topology_valid"]) and not struct_issues,
        "topology_consistency_issues": topology["stats"].get("consistency_issues", []),
        "is_manifold": bool(topology["stats"].get("is_manifold", False)),
        "non_manifold_edges": int(topology["stats"].get("non_manifold_edges", 0)),
        "max_occ_rebuild_err": max(
            (e["occ_rebuild_max_err"] for e in per_curve if e["occ_rebuild_max_err"] is not None),
            default=0.0,
        ),
        "max_numpy_rebuild_err": max(
            (e["numpy_rebuild_max_err"] for e in per_curve if e["numpy_rebuild_max_err"] is not None),
            default=0.0,
        ),
        "max_endpoint_err": max((e["endpoint_err"] for e in per_curve), default=0.0),
        "max_tangent_angle_err_deg": max(
            (
                e["tangent_angle_err_max_deg"]
                for e in per_curve
                if e["tangent_angle_err_max_deg"] is not None
                and math.isfinite(e["tangent_angle_err_max_deg"])
            ),
            default=0.0,
        ),
        "max_chamfer": max(
            (e["chamfer"] for e in per_curve if e["chamfer"] is not None), default=0.0
        ),
        "max_sampled_length_rel_err": max(
            (
                e["sampled_length_rel_err"]
                for e in per_curve
                if math.isfinite(e.get("sampled_length_rel_err", float("nan")))
            ),
            default=0.0,
        ),
        "max_sample_xyz_err_world": max(
            (e["sample_xyz_max_err"] for e in per_curve
             if math.isfinite(e.get("sample_xyz_max_err", float("nan")))),
            default=0.0,
        ),
        "max_sample_xyz_err_normalized": max(
            (e["sample_xyz_normalized_max_err"] for e in per_curve
             if math.isfinite(e.get("sample_xyz_normalized_max_err", float("nan")))),
            default=0.0,
        ),
        "max_abs_world_coord": float(np.abs(xyz).max()) if xyz.size else 0.0,
        "tolerance": tol,
        "failures": failures,
        "nan_reports": nan_reports,
        "per_type_max_err": {},
    }
    for ct in sorted({e["curve_type"] for e in per_curve}):
        errs = [
            e["occ_rebuild_max_err"]
            for e in per_curve
            if e["curve_type"] == ct and e["occ_rebuild_max_err"] is not None
        ]
        summary["per_type_max_err"][ct] = max(errs) if errs else None
    return summary


def _worker(job: tuple[str, str]) -> dict:
    split, cad_id = job
    try:
        return validate_one(split, cad_id)
    except Exception as exc:  # noqa: BLE001
        import traceback

        return {
            "cad_id": cad_id,
            "split": split,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(limit=6),
        }


def validate_many(jobs: list[tuple[str, str]], workers: int = 16) -> list[dict]:
    from concurrent.futures import ProcessPoolExecutor

    if workers <= 1:
        return [_worker(j) for j in jobs]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_worker, jobs, chunksize=1))


def aggregate(results: list[dict]) -> dict:
    ok = [r for r in results if r.get("ok")]
    bad = [r for r in results if not r.get("ok")]
    total_curves = sum(r["num_curves"] for r in ok)
    param_pass = sum(r["n_param_pass"] for r in ok)
    geom_pass = sum(r["n_geom_pass"] for r in ok)
    topo_ok = sum(1 for r in ok if r["topology_valid"])
    all_failures = [f for r in ok for f in r["failures"]]
    all_nan = [f for r in ok for f in r["nan_reports"]]

    per_type: dict[str, float] = {}
    for r in ok:
        for ct, v in (r.get("per_type_max_err") or {}).items():
            if v is None:
                continue
            per_type[ct] = max(per_type.get(ct, 0.0), float(v))

    denom_c = max(total_curves, 1)
    denom_o = max(len(ok), 1)
    return {
        "CAD_VALIDATED": len(ok),
        "CAD_VALIDATION_ERRORS": len(bad),
        "TOTAL_CURVES": total_curves,
        "PARAMETER_EXTRACTION_PASS_RATE": 100.0 * param_pass / denom_c,
        "GEOMETRY_RECONSTRUCTION_PASS_RATE": 100.0 * geom_pass / denom_c,
        "TOPOLOGY_VALID_RATE": 100.0 * topo_ok / denom_o,
        "MANIFOLD_CAD_RATE": 100.0 * sum(1 for r in ok if r["is_manifold"]) / denom_o,
        "n_param_pass": param_pass,
        "n_geom_pass": geom_pass,
        "n_topology_valid": topo_ok,
        "n_manifold": sum(1 for r in ok if r["is_manifold"]),
        "n_non_manifold_edges": sum(r["non_manifold_edges"] for r in ok),
        "topology_consistency_failures": [
            {"cad_id": r["cad_id"], "split": r["split"], "issues": r["topology_consistency_issues"]}
            for r in ok
            if r["topology_consistency_issues"]
        ][:100],
        "max_occ_rebuild_err": max((r["max_occ_rebuild_err"] for r in ok), default=0.0),
        "max_numpy_rebuild_err": max((r["max_numpy_rebuild_err"] for r in ok), default=0.0),
        "max_endpoint_err": max((r["max_endpoint_err"] for r in ok), default=0.0),
        "max_tangent_angle_err_deg": max((r["max_tangent_angle_err_deg"] for r in ok), default=0.0),
        "max_chamfer": max((r["max_chamfer"] for r in ok), default=0.0),
        "max_sampled_length_rel_err": max((r["max_sampled_length_rel_err"] for r in ok), default=0.0),
        "max_sample_xyz_err_world": max((r["max_sample_xyz_err_world"] for r in ok), default=0.0),
        "max_sample_xyz_err_normalized": max(
            (r["max_sample_xyz_err_normalized"] for r in ok), default=0.0
        ),
        "max_abs_world_coord": max((r["max_abs_world_coord"] for r in ok), default=0.0),
        "per_type_max_occ_rebuild_err": per_type,
        "n_curve_failures": len(all_failures),
        "n_nan_inf": len(all_nan),
        "nan_inf_reports": all_nan[:500],
        "cad_errors": [{"cad_id": r["cad_id"], "split": r["split"], "error": r.get("error")} for r in bad],
        "structural_issues": [
            {"cad_id": r["cad_id"], "issues": r["structural_issues"]}
            for r in ok
            if r["structural_issues"]
        ][:200],
    }


def write_reports(agg: dict, results: list[dict], tag: str) -> tuple[Path, Path]:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    jpath = VALIDATION_DIR / f"validation_report_{tag}.json"
    mpath = VALIDATION_DIR / f"validation_report_{tag}.md"
    fpath = VALIDATION_DIR / f"failures_{tag}.jsonl"

    jpath.write_text(json.dumps(agg, indent=2), encoding="utf-8")
    with fpath.open("w", encoding="utf-8") as fh:
        for r in results:
            if not r.get("ok"):
                fh.write(json.dumps({"cad_id": r["cad_id"], "split": r["split"],
                                     "error": r.get("error")}) + "\n")
                continue
            for f in r["failures"]:
                fh.write(json.dumps(f) + "\n")

    lines = [
        f"# Curve dataset validation ({tag})",
        "",
        "```text",
        f"PARAMETER_EXTRACTION_PASS_RATE={agg['PARAMETER_EXTRACTION_PASS_RATE']:.4f}%",
        f"GEOMETRY_RECONSTRUCTION_PASS_RATE={agg['GEOMETRY_RECONSTRUCTION_PASS_RATE']:.4f}%",
        f"TOPOLOGY_VALID_RATE={agg['TOPOLOGY_VALID_RATE']:.4f}%",
        "```",
        "",
        "`TOPOLOGY_VALID_RATE` measures whether the extracted incidence relations are",
        "mutually consistent and every curve is bounded. Non-manifoldness is a property of",
        "the source solid, not an extraction failure, so it is reported separately.",
        "",
        "## Scope",
        "",
        f"- CAD validated: {agg['CAD_VALIDATED']}",
        f"- CAD validation errors: {agg['CAD_VALIDATION_ERRORS']}",
        f"- curves checked: {agg['TOTAL_CURVES']}",
        f"- curve-level failures: {agg['n_curve_failures']}",
        f"- NaN/Inf occurrences: {agg['n_nan_inf']}",
        f"- fully manifold CAD: {agg['n_manifold']} ({agg['MANIFOLD_CAD_RATE']:.4f}%)",
        f"- non-manifold edges (>2 faces), extracted with all face ids: "
        f"{agg['n_non_manifold_edges']}",
        "",
        "## Worst-case geometry errors (absolute, model units)",
        "",
        "| metric | value |",
        "|---|---|",
        f"| OCC rebuild point error (max) | {agg['max_occ_rebuild_err']:.3e} |",
        f"| numpy (OCC-free) rebuild point error (max) | {agg['max_numpy_rebuild_err']:.3e} |",
        f"| endpoint error (max) | {agg['max_endpoint_err']:.3e} |",
        f"| tangent angular error (max) | {agg['max_tangent_angle_err_deg']:.3e} deg |",
        f"| Chamfer, rebuilt vs OCC (max) | {agg['max_chamfer']:.3e} |",
        f"| sampled-polyline vs exact length (max rel) | {agg['max_sampled_length_rel_err']:.3e} |",
        "",
        "The rows above measure the **exact float64 parameters** in `curves.json`.",
        "",
        "## float32 sampled arrays",
        "",
        "`curve_xyz` / `curve_xyz_normalized` are stored as float32, so their accuracy is",
        "bounded by coordinate *magnitude*, not by part size. Some Fusion360 parts sit far",
        "from the origin (world coordinates in the thousands with a small bbox), which costs",
        "world-space precision that the recentred normalized copy does not pay.",
        "",
        "| metric | value |",
        "|---|---|",
        f"| sampled xyz vs OCC, world (max) | {agg['max_sample_xyz_err_world']:.3e} |",
        f"| sampled xyz vs OCC, normalized (max) | {agg['max_sample_xyz_err_normalized']:.3e} |",
        f"| largest absolute world coordinate | {agg['max_abs_world_coord']:.4g} |",
        "",
        "## Max OCC rebuild error by curve type",
        "",
        "| curve type | max error |",
        "|---|---|",
    ]
    for ct, v in sorted(agg["per_type_max_occ_rebuild_err"].items()):
        lines.append(f"| {ct} | {v:.3e} |")
    lines.append("")
    if agg["cad_errors"]:
        lines += ["## CAD-level errors", ""]
        lines += [f"- `{e['split']}/{e['cad_id']}`: {e['error']}" for e in agg["cad_errors"][:100]]
        lines.append("")
    if agg["nan_inf_reports"]:
        lines += ["## NaN / Inf occurrences", ""]
        lines += [
            f"- `{r['split']}/{r['cad_id']}` edge {r['edge_id']} field `{r['field']}`"
            for r in agg["nan_inf_reports"][:100]
        ]
        lines.append("")
    if agg["structural_issues"]:
        lines += ["## Structural issues", ""]
        lines += [f"- `{r['cad_id']}`: {r['issues']}" for r in agg["structural_issues"][:100]]
        lines.append("")
    mpath.write_text("\n".join(lines), encoding="utf-8")
    return jpath, mpath


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate the Track B curve dataset")
    ap.add_argument("--split", action="append", default=None)
    ap.add_argument("--tag", default="all")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    splits = args.split or list(SPLITS)
    jobs: list[tuple[str, str]] = []
    for sp in splits:
        root = split_dir(sp)
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if (d / "curves.json").is_file():
                jobs.append((sp, d.name))
    if args.limit:
        jobs = jobs[: args.limit]

    results = validate_many(jobs, args.workers)
    agg = aggregate(results)
    jp, mp = write_reports(agg, results, args.tag)
    print(json.dumps({k: agg[k] for k in agg if k.isupper()}, indent=2))
    print(f"-> {jp}\n-> {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
