#!/usr/bin/env python3
"""Exact parametric curve extraction from the CAD kernel.

    STEP -> TopoDS_Edge -> BRepAdaptor_Curve -> Geom_Curve -> exact parameters

No point sampling is involved in producing the ground truth. Every extracted
block is immediately verified against OCC's own evaluation of the same edge, so
a curve is only reported as extracted if its parameters actually reproduce it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .config import (
    CURVE_TYPE_IDS,
    DEGENERATE_LENGTH_REL,
    GEOMABS_TO_NAME,
    RECON_ABS_TOL_MIN,
    RECON_REL_TOL,
    SCHEMA_VERSION,
)
from .curve_eval import UnsupportedCurve, evaluate
from .occ_curve_v1 import (
    curve_length,
    eval_point,
    eval_point_tangent,
    load_step_shape,
    make_adaptor,
    pnt_to_np,
    shape_bbox,
)

N_VERIFY = 32


def _unit(v: np.ndarray) -> list[float]:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    return (v / n).tolist() if n > 1e-15 else v.tolist()


def _l(v) -> list[float]:
    return [float(x) for x in np.asarray(v, dtype=np.float64).ravel()]


# ------------------------------------------------------ per-type extraction --
def _line_params(adaptor) -> dict:
    lin = adaptor.Line()
    return {
        "origin": _l(pnt_to_np(lin.Location())),
        "direction": _unit(pnt_to_np(lin.Direction())),
    }


def _circle_params(adaptor) -> dict:
    circ = adaptor.Circle()
    ax2 = circ.Position()
    normal = np.asarray(_unit(pnt_to_np(ax2.Direction())), dtype=np.float64)
    x_axis = np.asarray(_unit(pnt_to_np(ax2.XDirection())), dtype=np.float64)
    # y_axis is stored explicitly (rather than left implicit) so a consumer never
    # has to guess the handedness of the local frame.
    y_axis = np.asarray(_unit(pnt_to_np(ax2.YDirection())), dtype=np.float64)
    return {
        "center": _l(pnt_to_np(ax2.Location())),
        "normal": normal.tolist(),
        "x_axis": x_axis.tolist(),
        "y_axis": y_axis.tolist(),
        "y_axis_from_cross": _unit(np.cross(normal, x_axis)),
        "radius": float(circ.Radius()),
    }


def _ellipse_params(adaptor) -> dict:
    ell = adaptor.Ellipse()
    ax2 = ell.Position()
    normal = np.asarray(_unit(pnt_to_np(ax2.Direction())), dtype=np.float64)
    major = np.asarray(_unit(pnt_to_np(ax2.XDirection())), dtype=np.float64)
    minor = np.asarray(_unit(pnt_to_np(ax2.YDirection())), dtype=np.float64)
    return {
        "center": _l(pnt_to_np(ax2.Location())),
        "normal": normal.tolist(),
        "major_axis": major.tolist(),
        "minor_axis": minor.tolist(),
        "minor_axis_from_cross": _unit(np.cross(normal, major)),
        "major_radius": float(ell.MajorRadius()),
        "minor_radius": float(ell.MinorRadius()),
    }


def _bspline_params(geom) -> dict:
    npoles = int(geom.NbPoles())
    nknots = int(geom.NbKnots())
    ctrl = np.array([pnt_to_np(geom.Pole(i)) for i in range(1, npoles + 1)])
    knots = np.array([float(geom.Knot(i)) for i in range(1, nknots + 1)])
    mults = np.array([int(geom.Multiplicity(i)) for i in range(1, nknots + 1)], dtype=np.int64)
    rational = bool(geom.IsRational())
    weights = np.array([float(geom.Weight(i)) for i in range(1, npoles + 1)])
    return {
        "degree": int(geom.Degree()),
        "control_points": ctrl.tolist(),
        "num_control_points": npoles,
        "knots": knots.tolist(),
        "multiplicities": mults.tolist(),
        "num_knots": nknots,
        "knot_multiplicity_sum": int(mults.sum()),
        "weights": weights.tolist(),
        "is_rational": rational,
        "is_periodic": bool(geom.IsPeriodic()),
        "is_closed_geom": bool(geom.IsClosed()),
        "geom_u_start": float(geom.FirstParameter()),
        "geom_u_end": float(geom.LastParameter()),
    }


def _bezier_params(geom) -> dict:
    """A Bezier is stored as an equivalent clamped B-spline so the same
    reconstruction path works, plus its native pole list."""
    npoles = int(geom.NbPoles())
    degree = int(geom.Degree())
    ctrl = np.array([pnt_to_np(geom.Pole(i)) for i in range(1, npoles + 1)])
    rational = bool(geom.IsRational())
    weights = np.array([float(geom.Weight(i)) for i in range(1, npoles + 1)])
    return {
        "degree": degree,
        "control_points": ctrl.tolist(),
        "num_control_points": npoles,
        "knots": [0.0, 1.0],
        "multiplicities": [degree + 1, degree + 1],
        "num_knots": 2,
        "knot_multiplicity_sum": 2 * (degree + 1),
        "weights": weights.tolist(),
        "is_rational": rational,
        "is_periodic": False,
        "is_closed_geom": bool(geom.IsClosed()),
        "geom_u_start": float(geom.FirstParameter()),
        "geom_u_end": float(geom.LastParameter()),
        "native_form": "bezier",
    }


def _extract_type_params(adaptor, curve_type: str) -> tuple[dict, str | None]:
    try:
        if curve_type == "LINE":
            return _line_params(adaptor), None
        if curve_type == "CIRCLE":
            return _circle_params(adaptor), None
        if curve_type == "ELLIPSE":
            return _ellipse_params(adaptor), None
        if curve_type == "BSPLINE":
            return _bspline_params(adaptor.BSpline()), None
        if curve_type == "BEZIER":
            return _bezier_params(adaptor.Bezier()), None
        # HYPERBOLA / PARABOLA / OFFSET / OTHER: no analytic block this version.
        return {}, f"no_parameter_extractor_for_{curve_type}"
    except Exception as exc:  # noqa: BLE001
        return {}, f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------- verification -----
def _verify_against_occ(adaptor, curve_type: str, params: dict, u0: float, u1: float) -> dict:
    """Reconstruct from `params` and compare to OCC's own evaluation of the edge.

    Uses the OCC-free numpy evaluator when it supports the curve, and otherwise
    rebuilds the curve through the CAD kernel (periodic B-splines). Either way the
    reported error is measured, never assumed.
    """
    us = np.linspace(u0, u1, N_VERIFY)
    occ_pts = np.array([eval_point(adaptor, float(u)) for u in us])
    out: dict = {
        "numpy_evaluable": False,
        "recon_max_err": None,
        "recon_mean_err": None,
        "recon_backend": None,
    }

    def _record(rec: np.ndarray, backend: str) -> None:
        err = np.linalg.norm(rec - occ_pts, axis=1)
        out["recon_max_err"] = float(err.max())
        out["recon_mean_err"] = float(err.mean())
        out["recon_backend"] = backend

    try:
        _record(evaluate(curve_type, params, us), "numpy")
        out["numpy_evaluable"] = True
        return out
    except UnsupportedCurve as exc:
        out["numpy_eval_note"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        out["numpy_eval_note"] = f"{type(exc).__name__}: {exc}"

    try:
        from .occ_curve_v1 import rebuild_occ_curve

        geom = rebuild_occ_curve(curve_type, params)
        periodic = bool(params.get("is_periodic", False)) or curve_type in ("CIRCLE", "ELLIPSE")
        lo, hi = float(geom.FirstParameter()), float(geom.LastParameter())
        rec = np.array(
            [
                pnt_to_np(geom.Value(float(u) if periodic else float(np.clip(u, lo, hi))))
                for u in us
            ]
        )
        _record(rec, "occ_rebuild")
    except Exception as exc:  # noqa: BLE001
        out["recon_note"] = f"occ_rebuild_failed: {type(exc).__name__}: {exc}"
    return out


# --------------------------------------------------------------- main API ----
def extract_curves_from_shape(shape, cad_id: str = "") -> dict:
    """Extract exact parametric curves for every non-degenerate TopoDS_Edge."""
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
    from OCP.TopExp import TopExp
    from OCP.TopoDS import TopoDS
    from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape

    bb_min, bb_max = shape_bbox(shape)
    diag = float(np.linalg.norm(bb_max - bb_min))
    tol = max(RECON_REL_TOL * diag, RECON_ABS_TOL_MIN)
    degen_len = max(DEGENERATE_LENGTH_REL * diag, 1e-12)

    edge_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, edge_map)
    vert_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_VERTEX, vert_map)
    face_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_FACE, face_map)

    edge_faces = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, edge_faces)

    curves: list[dict] = []
    skipped: list[dict] = []
    n_topo_edges = int(edge_map.Size())

    for i in range(1, n_topo_edges + 1):
        edge = TopoDS.Edge_s(edge_map.FindKey(i))
        edge_id = i - 1

        if BRep_Tool.Degenerated_s(edge):
            skipped.append({"edge_id": edge_id, "reason": "degenerate_edge"})
            continue

        try:
            adaptor = make_adaptor(edge)
            u0 = float(adaptor.FirstParameter())
            u1 = float(adaptor.LastParameter())
        except Exception as exc:  # noqa: BLE001
            skipped.append({"edge_id": edge_id, "reason": f"adaptor_failed: {type(exc).__name__}: {exc}"})
            continue

        if not (np.isfinite(u0) and np.isfinite(u1)) or u1 <= u0:
            skipped.append({"edge_id": edge_id, "reason": f"bad_parameter_range: [{u0}, {u1}]"})
            continue

        geomabs = int(adaptor.GetType())
        curve_type = GEOMABS_TO_NAME.get(geomabs, "OTHER")
        length = curve_length(adaptor, u0, u1)
        if not np.isfinite(length) or length <= degen_len:
            skipped.append(
                {"edge_id": edge_id, "reason": f"zero_length", "curve_type": curve_type, "length": length}
            )
            continue

        start_pt, start_tan = eval_point_tangent(adaptor, u0)
        end_pt, end_tan = eval_point_tangent(adaptor, u1)
        try:
            is_closed = bool(adaptor.IsClosed())
        except Exception:  # noqa: BLE001
            is_closed = bool(np.linalg.norm(end_pt - start_pt) <= tol)

        params, param_err = _extract_type_params(adaptor, curve_type)
        verify = _verify_against_occ(adaptor, curve_type, params, u0, u1) if params else {
            "numpy_evaluable": False,
            "recon_max_err": None,
            "recon_mean_err": None,
        }

        faces = []
        if edge_faces.Contains(edge):
            for f in edge_faces.FindFromKey(edge):
                idx = face_map.FindIndex(f)
                if idx > 0:
                    faces.append(int(idx) - 1)
        faces = sorted(set(faces))

        verts: list[int] = []
        try:
            from OCP.TopoDS import TopoDS_Vertex

            va, vb = TopoDS_Vertex(), TopoDS_Vertex()
            TopExp.Vertices_s(edge, va, vb)
            for v in (va, vb):
                if v.IsNull():
                    continue
                idx = vert_map.FindIndex(v)
                verts.append(int(idx) - 1 if idx > 0 else -1)
        except Exception:  # noqa: BLE001
            verts = []

        recon_err = verify.get("recon_max_err")
        param_ok = bool(params) and param_err is None
        geom_ok = bool(
            param_ok
            and recon_err is not None
            and np.isfinite(recon_err)
            and recon_err <= tol
        )

        record = {
            "edge_id": edge_id,
            "curve_type": curve_type,
            "curve_type_id": CURVE_TYPE_IDS.get(curve_type, CURVE_TYPE_IDS["OTHER"]),
            "occ_geomabs_type": geomabs,
            "start_point": _l(start_pt),
            "end_point": _l(end_pt),
            "start_tangent": _unit(start_tan),
            "end_tangent": _unit(end_tan),
            "u_start": u0,
            "u_end": u1,
            "length": float(length),
            "is_closed": is_closed,
            "face_ids": faces,
            "vertex_ids": verts,
            "n_faces": len(faces),
            "world_parameters": params,
            "normalized_parameters": {},
            "extraction": {
                "parameter_extraction_ok": param_ok,
                "geometry_reconstruction_ok": geom_ok,
                "recon_max_err": recon_err,
                "recon_mean_err": verify.get("recon_mean_err"),
                "recon_tolerance": tol,
                "recon_backend": verify.get("recon_backend"),
                "numpy_evaluable": bool(verify.get("numpy_evaluable", False)),
                "note": param_err or verify.get("recon_note") or verify.get("numpy_eval_note"),
            },
        }
        if curve_type == "LINE":
            # Endpoints from origin+u*direction must agree with OCC's evaluation;
            # LINE parameters are arc length, so u_end-u_start == length.
            record["extraction"]["line_param_is_arclength_err"] = float(
                abs((u1 - u0) - length)
            )
        curves.append(record)

    return {
        "schema_version": SCHEMA_VERSION,
        "cad_id": cad_id,
        "num_curves": len(curves),
        "num_topo_edges": n_topo_edges,
        "num_vertices": int(vert_map.Size()),
        "num_faces": int(face_map.Size()),
        "num_skipped_edges": len(skipped),
        "skipped_edges": skipped,
        "source_bbox_min": _l(bb_min),
        "source_bbox_max": _l(bb_max),
        "source_diagonal": diag,
        "recon_tolerance": tol,
        "curves": curves,
    }


def extract_curves_from_step(step_path: Path, cad_id: str = "") -> dict:
    shape = load_step_shape(Path(step_path))
    out = extract_curves_from_shape(shape, cad_id=cad_id or Path(step_path).parent.name)
    out["source_step"] = str(step_path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract exact B-Rep parametric curves from a STEP file")
    ap.add_argument("step", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    data = extract_curves_from_step(args.step)
    counts: dict[str, int] = {}
    for c in data["curves"]:
        counts[c["curve_type"]] = counts.get(c["curve_type"], 0) + 1
    print(json.dumps({"num_curves": data["num_curves"], "types": counts,
                      "skipped": data["num_skipped_edges"]}, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
