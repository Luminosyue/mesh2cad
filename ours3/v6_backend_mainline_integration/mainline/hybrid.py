from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

from .common import sha256, write_step


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V7D3 = ROOT / "v7d3_vertical_tail_geometry_preserving_refit"
V7D = ROOT / "v7d_common_boundary_control_net"
RESTORE = ROOT / "v6_geometry_backend_restore"
sys.path[:0] = [str(V7D3), str(V7D), str(RESTORE)]

from geometry_preserving_refit.local_refitter import apply
from geometry_preserving_refit.master_compatibility import curve_from_three_poles, make_compatible
from geometry_preserving_refit.topology_identity import build as build_topology
from backends.v6_backend_safety_wrapper import reload_shape, signature, topology_metrics, verify


def _bspline_surfaces(shape: Any) -> list[Any]:
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    result = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        if "BSplineSurface" in str(BRepAdaptor_Surface(face).GetType()):
            surface = BRep_Tool.Surface_s(face)
            if hasattr(surface, "NbUPoles"):
                result.append(surface)
        explorer.Next()
    if len(result) != 2:
        raise RuntimeError(f"HYBRID_EXPECTED_TWO_BSPLINE_SUPPORTS:{len(result)}")
    return result


def _curve_points(surface: Any, side: str, count: int = 96) -> np.ndarray:
    u0, u1, v0, v1 = surface.Bounds()
    curve = surface.VIso(v0 if side == "V_MIN" else v1)
    values = np.linspace(curve.FirstParameter(), curve.LastParameter(), count)
    return np.asarray([[curve.Value(float(value)).X(), curve.Value(float(value)).Y(), curve.Value(float(value)).Z()] for value in values])


def _master_boundary(surface_a: Any, surface_b: Any) -> tuple[Any, Any, str, str, dict[str, Any]]:
    candidates = []
    for side_a in ("V_MIN", "V_MAX"):
        points_a = _curve_points(surface_a, side_a)
        for side_b in ("V_MIN", "V_MAX"):
            points_b = _curve_points(surface_b, side_b)
            for reverse_b in (False, True):
                aligned_b = points_b[::-1] if reverse_b else points_b
                distances = np.linalg.norm(points_a - aligned_b, axis=1)
                candidates.append((float(distances.mean()), float(np.quantile(distances, 0.95)), side_a, side_b, reverse_b, points_a, aligned_b))
    mean, p95, side_a, side_b, reverse_b, points_a, points_b = min(candidates, key=lambda row: (row[0], row[1]))
    a = surface_a.Copy()
    b = surface_b.Copy()
    if reverse_b:
        b.UReverse()
    master_points = 0.5 * (points_a + points_b)
    # The existing V7D3 compatibility mechanism requires a two-knot master
    # curve. Three source-derived poles preserve the authoritative boundary
    # evidence while avoiding a multi-knot interpolation curve that cannot be
    # normalized by make_compatible().
    poles = master_points[[0, len(master_points) // 2, -1]]
    curve = curve_from_three_poles(poles)
    fit_distances = np.linalg.norm(master_points - np.asarray([[curve.Value(float(t)).X(), curve.Value(float(t)).Y(), curve.Value(float(t)).Z()] for t in np.linspace(curve.FirstParameter(), curve.LastParameter(), len(master_points))]), axis=1)
    fit_metrics = {
        "CURVE_DEGREE": int(curve.Degree()),
        "CONTROL_POINT_COUNT": int(curve.NbPoles()),
        "FIT_MEAN_ERROR": float(fit_distances.mean()),
        "FIT_P95_ERROR": float(np.quantile(fit_distances, 0.95)),
        "FIT_MAX_ERROR": float(fit_distances.max()),
    }
    evidence = {
        "surface_pair_mean_deviation": mean,
        "surface_pair_p95_deviation": p95,
        "side_a": side_a,
        "side_b": side_b,
        "surface_b_u_reversed": reverse_b,
        "master_boundary_sample_count": len(master_points),
        "master_boundary_fit": fit_metrics,
    }
    return a, b, side_a, side_b, {"curve": curve, "evidence": evidence}


def _compound(shapes: list[Any]) -> Any:
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Shell

    # A shell preserves the shared TShape edge through STEP transfer.  This is
    # the existing V7D3 topology mechanism's container-level contract; no
    # historical STEP is sewn or copied here.
    result = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(result)
    for shape in shapes:
        builder.Add(result, shape)
    return result


def build(pure_v6_step: Path, source_mesh: Path, output_step: Path) -> dict[str, Any]:
    import trimesh
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.BRepCheck import BRepCheck_Analyzer

    pure_shape = reload_shape(pure_v6_step)
    surface_a, surface_b = _bspline_surfaces(pure_shape)
    source_diag = float(np.linalg.norm(trimesh.load(source_mesh, force="mesh", process=False).extents))
    surface_a, surface_b, side_a, side_b, master = _master_boundary(surface_a, surface_b)
    compatible_a, compatible_b, _, master_poles = make_compatible(surface_a, surface_b, master["curve"])
    changed_a, metrics_a, original_a, final_a = apply(compatible_a, master_poles, side_a, 2, True)
    changed_b, metrics_b, original_b, final_b = apply(compatible_b, master_poles, side_b, 2, True)
    face_a = BRepBuilderAPI_MakeFace(changed_a, 1e-8).Face()
    face_b = BRepBuilderAPI_MakeFace(changed_b, 1e-8).Face()
    topology = build_topology(changed_a, face_a, changed_b, face_b, side_a, side_b, max(source_diag * 1e-7, 1e-9))
    shape = _compound([topology["trimmed_face_a"], topology["trimmed_face_b"]])
    pre_signature = signature(shape)
    pre_topology = topology_metrics(shape, source_diag)
    write_step(shape, output_step)
    reloaded = reload_shape(output_step)
    post_signature = signature(reloaded)
    post_topology = topology_metrics(reloaded, source_diag)
    source = trimesh.load(source_mesh, force="mesh", process=False)
    qa = verify(source, reloaded, {})
    topology_match = all(pre_topology[key] == post_topology[key] for key in ("shared_edge_count", "pcurve_count", "trimmed_face_count"))
    topology_pass = post_topology["shared_edge_count"] >= 1 and post_topology["pcurve_count"] >= 2 and post_topology["trimmed_face_count"] >= 2
    pcurve_errors = [topology["PCURVE_A_ERROR"], topology["PCURVE_B_ERROR"]]
    result = {
        "candidate_source": "V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID",
        "candidate_kind": "AUDITED_EXTERNAL_GEOMETRY_BACKEND",
        "builder": "SHARED_BOUNDARY_FREEFORM_OPEN_SHELL",
        "fresh_step_path": str(output_step),
        "fresh_step_sha256": sha256(output_step),
        "pure_v6_step_sha256": sha256(pure_v6_step),
        "historical_step_reused": False,
        "v7d3_historical_final_step_reused": False,
        "pre_export_shape_signature": pre_signature,
        "reload_shape_signature": post_signature,
        "pre_export_topology": pre_topology,
        "post_reload_topology": post_topology,
        "pre_export_post_reload_topology_match": topology_match,
        "topology_pass": topology_pass,
        "brep_valid": bool(BRepCheck_Analyzer(reloaded).IsValid()),
        "master_boundary": master["evidence"],
        "surface_a_refit": metrics_a,
        "surface_b_refit": metrics_b,
        "boundary_deviation_max": max(topology["PCURVE_A_ERROR"]["max"], topology["PCURVE_B_ERROR"]["max"]),
        "boundary_deviation_p95": max(topology["PCURVE_A_ERROR"]["p95"], topology["PCURVE_B_ERROR"]["p95"]),
        "interior_deviation_max": float(max(np.linalg.norm(final_a[:, 2:] - original_a[:, 2:], axis=2).max(initial=0.0), np.linalg.norm(final_b[:, 2:] - original_b[:, 2:], axis=2).max(initial=0.0))),
        "qa": qa,
    }
    result["freshness_pass"] = result["fresh_step_sha256"] != result["pure_v6_step_sha256"]
    result["nativeness_pass"] = qa["nativeness_status"] == "PASS" and qa["structural_class"] != "V6_MESH_WRAPPED_BREP"
    result["safety_pass"] = bool(result["brep_valid"] and qa["reload_valid"] if "reload_valid" in qa else result["brep_valid"])
    return result
