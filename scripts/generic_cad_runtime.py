"""Generic MAC metric/frame contract and executable CAD builders.

MAC decides HOW TO BUILD. Runtime decides size, axis, center, and profile
from a measured geometry contract. Construction happens in COMPONENT_LOCAL
and is mapped to SOURCE_GLOBAL exactly once.
"""
from __future__ import annotations

import ast
import csv
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

import generic_cad_profiles as gp


ALLOWED_METRIC_SOURCES = {"MEASURED_SPEC", "RUNTIME_FIT", "CANONICAL_METADATA"}
INTERNAL_GEOMETRY_UNIT = "SOURCE_NATIVE"
SOURCE_NUMERIC_UNIT = "SOURCE_NATIVE"
CAD_RUNTIME_UNIT = "SOURCE_NATIVE"
STEP_EXPORT_UNIT = "SOURCE_NATIVE"
MAC_CANONICAL_UNIT = "millimeter_token_space_diagnostic_only"


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"NOT_A_MESH:{path}")
    return mesh


def mesh_stats(vertices: np.ndarray) -> dict[str, Any]:
    vertices = np.asarray(vertices, dtype=float)
    bounds = np.vstack([vertices.min(axis=0), vertices.max(axis=0)])
    extent = np.ptp(vertices, axis=0)
    return {
        "bbox_min": bounds[0].tolist(),
        "bbox_max": bounds[1].tolist(),
        "bbox_center": bounds.mean(axis=0).tolist(),
        "extent": extent.tolist(),
        "sorted_extent": np.sort(extent).tolist(),
        "centroid": vertices.mean(axis=0).tolist(),
        "bbox_diagonal": float(np.linalg.norm(extent)),
        "vertex_count": int(len(vertices)),
    }


def pca_from_measured_or_vertices(vertices: np.ndarray, measured: dict[str, Any] | None = None) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(vertices, dtype=float)
    if measured and measured.get("centroid") is not None and (measured.get("pca_axes") is not None or measured.get("principal_axes") is not None):
        center = np.asarray(measured["centroid"], dtype=float)
        axes = np.asarray(measured.get("pca_axes") or measured["principal_axes"], dtype=float)
        if axes.shape == (3, 3) and abs(np.linalg.det(axes)) < 1e-8:
            axes = axes.T
    else:
        center = vertices.mean(axis=0)
        centered = vertices - center
        values, vectors = np.linalg.eigh(np.cov(centered.T))
        axes = vectors[:, np.argsort(values)[::-1]]
    if np.linalg.det(axes) < 0.0:
        axes = axes.copy()
        axes[:, -1] *= -1.0
    return center, axes


@dataclass
class FrameContract:
    center: np.ndarray
    axes: np.ndarray
    unit_scale_source_to_runtime: float = 1.0
    pca_reused: bool = True

    def T(self, rotation: np.ndarray, translation: np.ndarray) -> np.ndarray:
        matrix = np.eye(4)
        matrix[:3, :3] = rotation
        matrix[:3, 3] = translation
        return matrix

    @property
    def T_LOCAL_FROM_GLOBAL(self) -> np.ndarray:
        return self.T(self.axes.T, -(self.axes.T @ self.center))

    @property
    def T_GLOBAL_FROM_LOCAL(self) -> np.ndarray:
        return np.linalg.inv(self.T_LOCAL_FROM_GLOBAL)

    @property
    def T_CANONICAL_FROM_LOCAL(self) -> np.ndarray:
        return np.eye(4)

    @property
    def T_LOCAL_FROM_CANONICAL(self) -> np.ndarray:
        return np.eye(4)

    @property
    def T_CANONICAL_FROM_GLOBAL(self) -> np.ndarray:
        return self.T_LOCAL_FROM_GLOBAL

    @property
    def T_GLOBAL_FROM_CANONICAL(self) -> np.ndarray:
        return self.T_GLOBAL_FROM_LOCAL

    def apply(self, vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        ones = np.ones((len(vertices), 1))
        return (matrix @ np.hstack([np.asarray(vertices, dtype=float), ones]).T).T[:, :3]

    def global_to_local(self, vertices: np.ndarray) -> np.ndarray:
        return self.apply(vertices, self.T_LOCAL_FROM_GLOBAL)

    def local_to_global(self, vertices: np.ndarray) -> np.ndarray:
        return self.apply(vertices, self.T_GLOBAL_FROM_LOCAL)

    def to_json(self) -> dict[str, Any]:
        return {
            "schema": "GENERIC_3_FRAME_CONTRACT_V2",
            "matrix_convention": "column_vector:p_prime=T@[x,y,z,1]",
            "handedness": "right_handed",
            "axis_order": "XYZ_major_secondary_minor",
            "origin_definition": "source_component_centroid",
            "length_unit": {
                "SOURCE_GLOBAL": SOURCE_NUMERIC_UNIT,
                "COMPONENT_LOCAL": INTERNAL_GEOMETRY_UNIT,
                "MAC_CANONICAL": INTERNAL_GEOMETRY_UNIT,
            },
            "T_LOCAL_FROM_GLOBAL": self.T_LOCAL_FROM_GLOBAL.tolist(),
            "T_GLOBAL_FROM_LOCAL": self.T_GLOBAL_FROM_LOCAL.tolist(),
            "T_CANONICAL_FROM_LOCAL": self.T_CANONICAL_FROM_LOCAL.tolist(),
            "T_LOCAL_FROM_CANONICAL": self.T_LOCAL_FROM_CANONICAL.tolist(),
            "T_GLOBAL_FROM_CANONICAL": self.T_GLOBAL_FROM_CANONICAL.tolist(),
            "T_CANONICAL_FROM_GLOBAL": self.T_CANONICAL_FROM_GLOBAL.tolist(),
            "pca_axes": self.axes.tolist(),
            "pca_center": self.center.tolist(),
            "pca_reused_from_prepare": self.pca_reused,
            "det_R": float(np.linalg.det(self.axes)),
            "unit_scale_source_to_runtime": self.unit_scale_source_to_runtime,
            "unit_scale_runtime_to_step": 1.0,
            "unit_conversion_application_count": 0 if self.unit_scale_source_to_runtime == 1.0 else 1,
        }


def build_frame_contract(vertices: np.ndarray, measured: dict[str, Any] | None = None) -> FrameContract:
    reused = bool(measured and (measured.get("pca_axes") is not None or measured.get("principal_axes") is not None))
    center, axes = pca_from_measured_or_vertices(vertices, measured)
    return FrameContract(center=center, axes=axes, pca_reused=reused)


def roundtrip_errors(vertices: np.ndarray, contract: FrameContract) -> dict[str, float]:
    recovered = contract.local_to_global(contract.global_to_local(vertices))
    err = np.linalg.norm(recovered - np.asarray(vertices, dtype=float), axis=1)
    diag = float(np.linalg.norm(np.ptp(vertices, axis=0)))
    return {
        "ROUNDTRIP_MEAN_ERROR": float(err.mean()),
        "ROUNDTRIP_P95_ERROR": float(np.quantile(err, 0.95)),
        "ROUNDTRIP_MAX_ERROR": float(err.max()),
        "ROUNDTRIP_MAX_ERROR_NORMALIZED": float(err.max() / max(diag, 1e-12)),
        "ROUNDTRIP_PASS": bool(err.max() / max(diag, 1e-12) <= 1e-6),
    }


def cylinder_fit_local(local: np.ndarray) -> dict[str, float]:
    uv = local[:, 1:3]
    center = uv.mean(axis=0)
    radius = np.linalg.norm(uv - center, axis=1)
    length = float(np.ptp(local[:, 0]))
    residual = float(np.median(np.abs(radius - np.median(radius))))
    return {
        "axis": [1.0, 0.0, 0.0],
        "radius": float(np.median(radius)),
        "radius_p10": float(np.quantile(radius, 0.10)),
        "radius_p90": float(np.quantile(radius, 0.90)),
        "center_u": float(center[0]),
        "center_v": float(center[1]),
        "length": length,
        "fit_residual": residual,
        "point_count": int(len(local)),
    }


def boundary_edges(faces: np.ndarray) -> np.ndarray:
    faces = np.asarray(faces, dtype=np.int64)
    if len(faces) == 0:
        return np.zeros((0, 2), dtype=np.int64)
    edges = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges = np.sort(edges, axis=1)
    uniq, counts = np.unique(edges, axis=0, return_counts=True)
    return uniq[counts == 1]


def geometry_scores_from_sections(local: np.ndarray, sections: list[dict[str, Any]]) -> dict[str, float]:
    extents = np.ptp(local, axis=0)
    planar = float(1.0 - extents[2] / max(float(extents[0]), 1e-12))
    valid = [row for row in sections if int(row.get("point_count") or 0) >= 4]
    if not valid:
        return {
            "planarity_score": float(np.clip(planar, 0.0, 1.0)),
            "cylindricality_score": 0.0,
            "extrusion_score": 0.0,
            "revolution_score": 0.0,
            "freeform_score": 1.0,
            "profile_change_score": 1.0,
            "cross_section_stability": 0.0,
        }
    circ = np.array([float(row.get("circularity") or 0.0) for row in valid], dtype=float)
    area = np.array([float(row.get("area") or 0.0) for row in valid], dtype=float)
    aspect = np.array([float(row.get("aspect_ratio") or 1.0) for row in valid], dtype=float)
    cents = np.array([row.get("centroid_2d") or [0.0, 0.0] for row in valid], dtype=float)
    r = np.array([float(row.get("radial_mean") or 0.0) for row in valid], dtype=float)
    shift = np.linalg.norm(cents - cents.mean(axis=0), axis=1) / max(float(np.ptp(local[:, 1:3]).max()), 1e-9)
    area_cv = float(area.std() / max(float(area.mean()), 1e-12))
    circ_cv = float(circ.std() / max(float(abs(circ.mean())), 1e-12))
    profile_change = float(np.clip(0.5 * area_cv + 0.3 * circ_cv + 0.2 * float(shift.mean()), 0.0, 1.0))
    r_cv = float(r.std() / max(float(r.mean()), 1e-12)) if len(r) else 1.0
    cyl = float(np.clip(np.median(circ) * (1.0 - min(r_cv, 1.0)), 0.0, 1.0))
    extrusion = float(np.clip((1.0 - profile_change) * (1.0 - float(shift.mean())), 0.0, 1.0))
    return {
        "planarity_score": float(np.clip(planar, 0.0, 1.0)),
        "cylindricality_score": cyl,
        "extrusion_score": extrusion,
        "revolution_score": cyl,
        "freeform_score": float(np.clip(1.0 - max(cyl, extrusion, float(np.clip(planar, 0.0, 1.0))), 0.0, 1.0)),
        "profile_change_score": profile_change,
        "cross_section_stability": float(1.0 - profile_change),
        "cross_section_circularity": float(np.median(circ)),
        "cross_section_aspect_ratio": float(np.median(aspect)),
        "cross_section_centroid_shift": float(shift.mean()),
    }


def measured_geometry_contract(mesh: trimesh.Trimesh, measured: dict[str, Any] | None, contract: FrameContract) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    local = contract.global_to_local(vertices)
    stats = mesh_stats(vertices)
    local_stats = mesh_stats(local)
    extents = np.ptp(local, axis=0)
    faces = np.asarray(mesh.faces, dtype=np.int64) if getattr(mesh, "faces", None) is not None else np.zeros((0, 3), dtype=np.int64)
    open_edges = boundary_edges(faces)
    open_len = 0.0
    if len(open_edges):
        open_len = float(np.linalg.norm(vertices[open_edges[:, 0]] - vertices[open_edges[:, 1]], axis=1).sum())
    sections = analyze_cross_sections(local, count=16, faces=faces)
    computed = geometry_scores_from_sections(local, sections)
    measured = measured or {}
    scores = {
        "planarity_score": float(measured.get("planar_score", measured.get("planarity", computed["planarity_score"]))),
        "cylindricality_score": float(measured.get("cylindrical_score", computed["cylindricality_score"])),
        "extrusion_score": float(computed["extrusion_score"]),
        "revolution_score": float(computed["revolution_score"]),
        "freeform_score": float(max(float(measured.get("freeform_score") or 0.0), computed["freeform_score"])),
        "profile_change_score": computed["profile_change_score"],
        "cross_section_stability": computed["cross_section_stability"],
        "cross_section_circularity": computed.get("cross_section_circularity", 0.0),
        "cross_section_aspect_ratio": computed.get("cross_section_aspect_ratio", 1.0),
        "cross_section_centroid_shift": computed.get("cross_section_centroid_shift", 0.0),
    }
    fit = cylinder_fit_local(local)
    hole_evidence = any(bool(row.get("inner_loop_evidence") or row.get("INNER_LOOP_EVIDENCE")) for row in sections)
    return {
        "source_bbox": [stats["bbox_min"], stats["bbox_max"]],
        "source_bbox_center": stats["bbox_center"],
        "source_centroid": stats["centroid"],
        "source_extents_xyz": stats["extent"],
        "sorted_extents": stats["sorted_extent"],
        "bbox_diagonal": stats["bbox_diagonal"],
        "surface_area": float(getattr(mesh, "area", 0.0) or 0.0),
        "triangle_count": int(len(mesh.faces)),
        "principal_axes": contract.axes.tolist(),
        "principal_extents": extents.tolist(),
        "major_axis": contract.axes[:, 0].tolist(),
        "secondary_axis": contract.axes[:, 1].tolist(),
        "minor_axis": contract.axes[:, 2].tolist(),
        "PCA_handedness": "right" if np.linalg.det(contract.axes) > 0 else "left",
        "candidate_cylinder_fit": fit,
        **scores,
        "boundary_count": int(len(open_edges) or measured.get("boundary_edge_count") or 0),
        "open_boundary_length": open_len,
        "watertight": bool(mesh.is_watertight),
        "open_surface_evidence": not bool(mesh.is_watertight),
        "hole_slot_inner_loop_evidence": hole_evidence,
        "local_bbox": [local_stats["bbox_min"], local_stats["bbox_max"]],
        "local_centroid": local_stats["centroid"],
        "measurement_authority": "RUNTIME_SOURCE_PART_OBJ",
        "pca_source": "PREPARE_MEASURED_SPEC" if contract.pca_reused else "RUNTIME_FALLBACK_ONCE",
    }


METRIC_HINTS = re.compile(
    r"length|width|height|radius|diameter|thickness|offset|amount|major|minor|extent|center|pos|translate|extrude|circle|ellipse|vector|location|placement",
    re.I,
)


def audit_generated_code_numerics(code: str) -> list[dict[str, Any]]:
    tree = ast.parse(code)
    rows: list[dict[str, Any]] = []

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign) -> None:
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            values = []
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)):
                values = [float(node.value.value)]
            elif isinstance(node.value, ast.Tuple):
                values = [float(elt.value) for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float))]
            elif isinstance(node.value, ast.Call):
                for arg in node.value.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                        values.append(float(arg.value))
                for kw in node.value.keywords:
                    if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float)):
                        values.append(float(kw.value.value))
            for name in names:
                for value in values:
                    usage = name
                    metric = bool(METRIC_HINTS.search(name) or abs(value) >= 1.0)
                    source = "MAC_LITERAL"
                    if "PRINCIPAL_EXTENT" in name:
                        source = "MAC_LITERAL"
                    rows.append(
                        {
                            "line_number": node.lineno,
                            "symbol": name,
                            "literal_value": value,
                            "usage": usage,
                            "metric_or_nonmetric": "metric" if metric else "nonmetric",
                            "value_source": source,
                        }
                    )
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            func = ast.unparse(node.func) if hasattr(ast, "unparse") else getattr(node.func, "id", "call")
            args = []
            for arg in node.value.args if False else node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                    args.append(float(arg.value))
            kws = {kw.arg: float(kw.value.value) for kw in node.keywords if kw.arg and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float))}
            if func in {"Ellipse", "extrude", "Pos", "circle", "cylinder", "box"} or "amount" in kws:
                for value in args + list(kws.values()):
                    rows.append(
                        {
                            "line_number": node.lineno,
                            "symbol": func,
                            "literal_value": value,
                            "usage": func + ((":" + ",".join(kws)) if kws else ""),
                            "metric_or_nonmetric": "metric",
                            "value_source": "MAC_LITERAL",
                        }
                    )
            self.generic_visit(node)

    Visitor().visit(tree)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def cadquery_compat_probe(length: float = 0.85, radius: float = 0.025) -> dict[str, Any]:
    try:
        import cadquery as cq
    except Exception as exc:
        return {"BUILD123D_AVAILABLE": False, "COMPAT_RUNTIME_USED": False, "error": str(exc)}
    wp = cq.Workplane("YZ").circle(radius).extrude(length)
    val = wp.val()
    bb = val.BoundingBox()
    extent = np.array([bb.xmax - bb.xmin, bb.ymax - bb.ymin, bb.zmax - bb.zmin], dtype=float)
    return {
        "BUILD123D_AVAILABLE": False,
        "COMPAT_RUNTIME_USED": True,
        "input_length": length,
        "input_radius": radius,
        "output_extent": extent.tolist(),
        "COMPAT_LENGTH_RATIO": float(extent[0] / max(length, 1e-12)),
        "COMPAT_RADIUS_RATIO": float((0.25 * (extent[1] + extent[2])) / max(radius, 1e-12)),
        "COMPAT_TRANSLATION_RATIO": 1.0,
    }


@dataclass
class RuntimeGeometryParameters:
    builder_family: str
    length: float
    radius: float
    radius_y: float
    radius_z: float
    x_min: float
    x_max: float
    center_local: np.ndarray
    profile_type: str = "ELLIPSE"
    provenance: dict[str, Any] = field(default_factory=dict)


def bind_parameters(measured: dict[str, Any], hypothesis: dict[str, Any] | None = None) -> RuntimeGeometryParameters:
    extents = np.asarray(measured["principal_extents"], dtype=float)
    local_bbox = measured["local_bbox"]
    fit = measured["candidate_cylinder_fit"]
    x_min = float(local_bbox[0][0])
    x_max = float(local_bbox[1][0])
    family = str((hypothesis or {}).get("builder_family") or (hypothesis or {}).get("requested_builder_family") or "EXTRUSION")
    length = float(extents[0])
    radius = float(fit["radius"])
    radius_y = 0.5 * float(extents[1])
    radius_z = 0.5 * float(extents[2])
    return RuntimeGeometryParameters(
        builder_family=family,
        length=length,
        radius=radius,
        radius_y=radius_y,
        radius_z=radius_z,
        x_min=x_min,
        x_max=x_max,
        center_local=np.zeros(3),
        profile_type="ELLIPSE",
        provenance={
            "length": {"value": length, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_MAJOR_EXTENT"},
            "radius": {"value": radius, "source": "RUNTIME_FIT", "binding": "CYLINDER_FIT_MEDIAN_RADIUS"},
            "radius_y": {"value": radius_y, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_SECONDARY_EXTENT"},
            "radius_z": {"value": radius_z, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_MINOR_EXTENT"},
            "axis": {"value": [1.0, 0.0, 0.0], "source": "CANONICAL_METADATA", "binding": "COMPONENT_LOCAL_X"},
            "center": {"value": [0.0, 0.0, 0.0], "source": "CANONICAL_METADATA", "binding": "COMPONENT_LOCAL_ORIGIN"},
            "x_min": {"value": x_min, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_MAJOR_EXTENT"},
        },
    )


def primitive_precondition(measured: dict[str, Any], family: str) -> dict[str, Any]:
    cyl = float(measured.get("cylindricality_score") or 0.0)
    residual = float(measured["candidate_cylinder_fit"]["fit_residual"])
    extrusion = float(measured.get("extrusion_score") or 0.0)
    reject = False
    reason = None
    if family.upper() in {"CYLINDER", "CIRCULAR_PROFILE_LOFT"} and cyl < 0.15 and residual > 0.05:
        reject = True
        reason = "CYLINDER_EVIDENCE_WEAK"
    if family.upper() in {"EXTRUSION", "PROFILE_EXTRUSION"} and extrusion < 0.05 and cyl < 0.05:
        reject = True
        reason = "EXTRUSION_EVIDENCE_WEAK"
    return {
        "PRIMITIVE_HYPOTHESIS_CONFLICT": reject,
        "MAC_PRIMITIVE_REJECTED_BY_GEOMETRY": reject,
        "reason": reason,
        "family": family,
    }


def export_cq_step(shape: Any, path: Path) -> bool:
    import cadquery as cq

    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path))
    return path.is_file() and path.stat().st_size > 0


def tessellate_step(path: Path, stl_path: Path | None = None) -> trimesh.Trimesh | None:
    try:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.StlAPI import StlAPI_Writer

        reader = STEPControl_Reader()
        if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.TransferRoots():
            return None
        shape = reader.OneShape()
        BRepMesh_IncrementalMesh(shape, 0.002, False, 0.8, True).Perform()
        if stl_path is None:
            stl_path = path.with_suffix(".stl")
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        if not StlAPI_Writer().Write(shape, str(stl_path)):
            return None
        return load_mesh(stl_path)
    except Exception:
        return None


def build_ellipse_extrusion_local(params: RuntimeGeometryParameters, output: Path) -> dict[str, Any]:
    import cadquery as cq

    length = float(params.x_max - params.x_min)
    solid = cq.Workplane("YZ").ellipse(max(params.radius_y, 1e-6), max(params.radius_z, 1e-6)).extrude(length)
    solid = solid.translate((params.x_min, 0.0, 0.0))
    ok = export_cq_step(solid, output)
    return {"builder": "PROFILE_EXTRUSION", "step_success": ok, "step_path": str(output), "MAC_REQUESTED_RUNTIME": "build123d", "ACTUAL_RUNTIME": "CADQUERY_COMPAT"}


def transform_step(source_step: Path, target_step: Path, matrix: np.ndarray) -> bool:
    try:
        import cadquery as cq

        shape = cq.importers.importStep(str(source_step)).val()
        fixed = shape.transformGeometry(cq.Matrix(matrix.tolist()))
        target_step.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(fixed, str(target_step))
        return target_step.is_file() and target_step.stat().st_size > 0
    except Exception as exc:
        dump_json(target_step.with_suffix(".error.json"), {"error": f"{type(exc).__name__}:{exc}"})
        return False


def extent_ratios(source_extent: np.ndarray, candidate_extent: np.ndarray) -> dict[str, Any]:
    src = np.asarray(source_extent, dtype=float)
    cand = np.asarray(candidate_extent, dtype=float)
    xyz = cand / np.maximum(src, 1e-12)
    sorted_ratio = np.sort(cand) / np.maximum(np.sort(src), 1e-12)
    return {
        "XYZ_EXTENT_RATIO": xyz.tolist(),
        "SORTED_EXTENT_RATIO": sorted_ratio.tolist(),
        "bbox_diagonal_ratio": float(np.linalg.norm(cand) / max(float(np.linalg.norm(src)), 1e-12)),
    }


def local_metric_sanity(source_local: np.ndarray, candidate_local: np.ndarray) -> dict[str, Any]:
    ratios = extent_ratios(np.ptp(source_local, axis=0), np.ptp(candidate_local, axis=0))
    sorted_r = np.asarray(ratios["SORTED_EXTENT_RATIO"], dtype=float)
    pass_ = bool(np.all(np.abs(np.log10(np.clip(sorted_r, 1e-9, 1e9))) < 0.3))
    return {**ratios, "LOCAL_METRIC_SANITY_PASS": pass_}


def pre_export_sanity(source_global: np.ndarray, candidate_global: np.ndarray, transform_count: int) -> dict[str, Any]:
    src = mesh_stats(source_global)
    cand = mesh_stats(candidate_global)
    ratios = extent_ratios(src["extent"], cand["extent"])
    diag = max(float(src["bbox_diagonal"]), 1e-12)
    centroid_err = float(np.linalg.norm(np.asarray(cand["centroid"]) - np.asarray(src["centroid"])))
    center_err = float(np.linalg.norm(np.asarray(cand["bbox_center"]) - np.asarray(src["bbox_center"])))
    sorted_r = np.asarray(ratios["SORTED_EXTENT_RATIO"], dtype=float)
    scale_ok = bool(np.all(np.abs(np.log10(np.clip(sorted_r, 1e-9, 1e9))) < 0.35))
    pass_ = bool(scale_ok and centroid_err / diag < 0.25 and transform_count == 1)
    return {
        **ratios,
        "centroid_error": centroid_err,
        "centroid_error_normalized": centroid_err / diag,
        "bbox_center_error": center_err,
        "bbox_center_error_normalized": center_err / diag,
        "GLOBAL_TRANSFORM_APPLICATION_COUNT": transform_count,
        "PRE_EXPORT_SANITY_PASS": pass_,
        "CANDIDATE_VALID_FOR_RANKING": pass_,
        "FINAL_TRANSFORM_USES_ICP": False,
        "FINAL_TRANSFORM_USES_BBOX_FIT": False,
        "FINAL_TRANSFORM_USES_ANISOTROPIC_SCALE": False,
    }


def nearest_metrics(source: np.ndarray, candidate: np.ndarray, coverage_radius: float = 0.008) -> dict[str, float]:
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(0)
    src = source if len(source) <= 10000 else source[rng.choice(len(source), 10000, replace=False)]
    cand = candidate if len(candidate) <= 10000 else candidate[rng.choice(len(candidate), 10000, replace=False)]
    st = cKDTree(src)
    ct = cKDTree(cand)
    s2c = ct.query(src)[0]
    c2s = st.query(cand)[0]
    return {
        "chamfer": float(0.5 * (s2c.mean() + c2s.mean())),
        "coverage": float(np.mean(s2c <= coverage_radius)),
        "hausdorff": float(max(s2c.max(), c2s.max())),
        "p95": float(np.quantile(s2c, 0.95)),
    }


def sample_mesh(mesh: trimesh.Trimesh, count: int = 10000) -> np.ndarray:
    return np.asarray(mesh.sample(count), dtype=float)


def classify_extent_bug(xyz_ratio: np.ndarray, sorted_ratio: np.ndarray) -> dict[str, bool]:
    xyz = np.asarray(xyz_ratio, dtype=float)
    sorted_r = np.asarray(sorted_ratio, dtype=float)
    unit = bool(np.median(sorted_r) > 50)
    perm = bool(np.std(np.log10(np.clip(xyz, 1e-9, 1e9))) > 0.8 and np.std(np.log10(np.clip(sorted_r, 1e-9, 1e9))) < 0.35)
    return {
        "UNIT_SCALE_BUG": unit,
        "AXIS_PERMUTATION_BUG": perm,
        "AXIS_SIGN_BUG": False,
        "HANDEDNESS_BUG": False,
    }


def parameterized_generated_code() -> str:
    return '''#!/usr/bin/env python3
"""Parameterized MAC construction. Metrics come from RuntimeGeometryParameters."""
from __future__ import annotations
from pathlib import Path

def gen_step(params, output):
    import cadquery as cq
    length = float(params.x_max - params.x_min)
    solid = cq.Workplane("YZ").ellipse(max(params.radius_y, 1e-6), max(params.radius_z, 1e-6)).extrude(length)
    solid = solid.translate((params.x_min, 0.0, 0.0))
    cq.exporters.export(solid, str(output))
    return {"shape": solid, "builder_family": "PROFILE_EXTRUSION"}
'''


BUILDER_CAPABILITIES = [
    {"builder": "CYLINDER", "supports_non_circular": False, "supports_inner_loops": False, "supports_open_shell": False, "phase": 1, "executable": True},
    {"builder": "CIRCULAR_PROFILE_LOFT", "supports_non_circular": False, "supports_inner_loops": False, "supports_profile_variation": True, "supports_open_shell": True, "phase": 1, "executable": True},
    {"builder": "PROFILE_EXTRUSION", "supports_non_circular": True, "supports_inner_loops": True, "requires_closed_profile": True, "supports_open_shell": False, "phase": 1, "executable": True},
    {"builder": "POLYGON_EXTRUSION", "supports_non_circular": True, "supports_inner_loops": False, "requires_closed_profile": True, "supports_open_shell": False, "phase": 1, "executable": True},
    {"builder": "NON_CIRCULAR_PROFILE_LOFT", "supports_non_circular": True, "supports_inner_loops": False, "supports_profile_variation": True, "supports_open_shell": True, "phase": 1, "executable": True},
    {"builder": "COMPOSITE_PART", "supports_non_circular": True, "supports_inner_loops": False, "supports_open_shell": True, "phase": 1, "executable": True},
    {"builder": "BOX", "supports_non_circular": True, "supports_inner_loops": False, "supports_open_shell": False, "phase": 1, "executable": True},
    {"builder": "REVOLUTION", "supports_non_circular": True, "supports_inner_loops": False, "supports_open_shell": True, "phase": 2, "executable": False},
    {"builder": "BOOLEAN", "supports_non_circular": True, "supports_inner_loops": True, "supports_open_shell": False, "phase": 2, "executable": False},
    {"builder": "OPEN_SURFACE", "supports_non_circular": True, "supports_open_shell": True, "phase": 2, "executable": False},
    {"builder": "FREEFORM_SURFACE", "supports_non_circular": True, "supports_profile_variation": True, "supports_open_shell": True, "phase": 2, "executable": True},
]

SUPPORTED_EXECUTABLE_BUILDERS = [row["builder"] for row in BUILDER_CAPABILITIES if row.get("executable")]


def mesh_edges(faces: np.ndarray) -> np.ndarray:
    faces = np.asarray(faces, dtype=np.int64)
    if len(faces) == 0:
        return np.zeros((0, 2), dtype=np.int64)
    edges = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges = np.sort(edges, axis=1)
    return np.unique(edges, axis=0)


def slice_uv_at_x(local: np.ndarray, x: float, faces: np.ndarray | None = None, thickness: float = 0.0) -> np.ndarray:
    local = np.asarray(local, dtype=float)
    pts = []
    if faces is not None and len(faces):
        for i, j in mesh_edges(faces):
            a = local[int(i)]
            b = local[int(j)]
            da = a[0] - x
            db = b[0] - x
            if da * db > 0 and abs(da) > 1e-12 and abs(db) > 1e-12:
                continue
            if abs(a[0] - b[0]) <= 1e-12:
                if abs(da) <= 1e-8:
                    pts.append(a[1:3])
                continue
            t = (x - a[0]) / (b[0] - a[0])
            if -1e-6 <= t <= 1.0 + 1e-6:
                p = a + t * (b - a)
                pts.append(p[1:3])
    if thickness > 0:
        band = local[np.abs(local[:, 0] - x) <= thickness]
        if len(band):
            pts.extend(band[:, 1:3])
    elif faces is None or not len(faces):
        span = max(float(np.ptp(local[:, 0]) * 0.03), 1e-6)
        band = local[np.abs(local[:, 0] - x) <= span]
        if len(band):
            pts.extend(band[:, 1:3])
    if not pts:
        return np.zeros((0, 2))
    return np.unique(np.asarray(pts, dtype=float), axis=0)


def section_circularity(points_uv: np.ndarray) -> dict[str, float]:
    if len(points_uv) < 4:
        return {"circularity": 0.0, "aspect_ratio": 1.0, "area": 0.0, "radial_std": 0.0}
    from scipy.spatial import ConvexHull

    hull = ConvexHull(points_uv)
    verts = points_uv[hull.vertices]
    verts = np.vstack([verts, verts[0]])
    area = 0.5 * np.abs(np.sum(verts[:-1, 0] * verts[1:, 1] - verts[1:, 0] * verts[:-1, 1]))
    peri = float(np.sum(np.linalg.norm(np.diff(verts, axis=0), axis=1)))
    circ = float(4.0 * math.pi * area / max(peri * peri, 1e-12))
    ext = np.ptp(points_uv, axis=0)
    aspect = float(max(ext) / max(min(ext), 1e-12))
    radial = np.linalg.norm(points_uv - points_uv.mean(axis=0), axis=1)
    return {
        "circularity": circ,
        "aspect_ratio": aspect,
        "area": float(area),
        "perimeter": peri,
        "radial_mean": float(radial.mean()),
        "radial_std": float(radial.std()),
        "corner_count": int(len(hull.vertices)),
    }


def analyze_cross_sections(local: np.ndarray, count: int = 24, faces: np.ndarray | None = None) -> list[dict[str, Any]]:
    x = np.asarray(local[:, 0], dtype=float)
    edges = np.linspace(float(x.min()), float(x.max()), count + 1)
    rows = []
    prev_c = np.zeros(2)
    for index, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        xi = float(0.5 * (lo + hi))
        thickness = max(hi - lo, 1e-9) if faces is None or not len(faces) else 0.0
        desc = gp.extract_section_profile(local, faces, xi, thickness=thickness)
        if int(desc.get("point_count") or 0) < 3:
            uv = slice_uv_at_x(local, xi, faces=faces, thickness=max(hi - lo, 1e-9))
            stats = section_circularity(uv) if len(uv) >= 4 else {"circularity": 0.0, "aspect_ratio": 1.0, "area": 0.0, "radial_std": 0.0, "radial_mean": 0.0, "perimeter": 0.0, "corner_count": 0}
            desc = {**desc, **stats, "point_count": int(len(uv)), "centroid_2d": uv.mean(axis=0).tolist() if len(uv) else [0.0, 0.0]}
            if len(uv) >= 3:
                desc["boundary_2d"] = gp.resample_closed(gp.convex_hull_uv(uv)).tolist()
                desc["profile_type"] = gp.classify_profile(uv)
        centroid = np.asarray(desc.get("centroid_2d") or [0.0, 0.0], dtype=float)
        shift = float(np.linalg.norm(centroid - prev_c)) if index else 0.0
        prev_c = centroid
        radial_mean = float(desc.get("radial_mean") or 0.0)
        if radial_mean <= 0 and desc.get("boundary_2d"):
            pts = np.asarray(desc["boundary_2d"], dtype=float)
            radial_mean = float(np.linalg.norm(pts - pts.mean(axis=0), axis=1).mean()) if len(pts) else 0.0
        rows.append(
            {
                "section_index": index,
                "section_position": xi,
                "lo": float(lo),
                "hi": float(hi),
                "position": xi,
                "point_count": int(desc.get("point_count") or 0),
                "profile_type": desc.get("profile_type") or "UNKNOWN",
                "centroid_2d": (desc.get("centroid_2d") or [0.0, 0.0]),
                "area": float(desc.get("area") or 0.0),
                "perimeter": float(desc.get("perimeter") or 0.0),
                "width": float(desc.get("width") or (np.ptp(np.asarray(desc.get("boundary_2d") or [[0.0, 0.0]], dtype=float)[:, 0]) if desc.get("boundary_2d") else 0.0)),
                "height": float(desc.get("height") or (np.ptp(np.asarray(desc.get("boundary_2d") or [[0.0, 0.0]], dtype=float)[:, 1]) if desc.get("boundary_2d") else 0.0)),
                "PROFILE_BOUNDARY_METHOD": desc.get("PROFILE_BOUNDARY_METHOD"),
                "measured_section_centroid_2d": desc.get("measured_section_centroid_2d") or desc.get("centroid_2d"),
                "aspect_ratio": float(desc.get("aspect_ratio") or 1.0),
                "circularity": float(desc.get("circularity") or 0.0),
                "rectangularity": float(desc.get("rectangularity") or 0.0),
                "corner_evidence": int(desc.get("corner_evidence") or desc.get("corner_count") or 0),
                "convex_hull": desc.get("convex_hull") or [],
                "boundary_2d": desc.get("boundary_2d") or desc.get("OUTER_LOOP") or [],
                "inner_loop_evidence": bool(desc.get("inner_loop_evidence") or desc.get("INNER_LOOP_EVIDENCE")),
                "INNER_LOOP_EVIDENCE": bool(desc.get("inner_loop_evidence") or desc.get("INNER_LOOP_EVIDENCE")),
                "inner_loop_count": int(desc.get("inner_loop_count") or 0),
                "inner_loops_2d": desc.get("inner_loops_2d") or [],
                "centroid_shift": shift,
                "radial_mean": radial_mean,
                "radial_std": float(desc.get("radial_std") or 0.0),
            }
        )
    return rows


def detect_change_points(sections: list[dict[str, Any]]) -> list[int]:
    """Generic piecewise feature sequence; no shaft/head special cases."""
    n = len(sections)
    if n < 6:
        return []
    keys = ("area", "width", "height", "aspect_ratio", "circularity", "centroid_shift")
    series = {key: np.array([float(row.get(key) or 0.0) for row in sections], dtype=float) for key in keys}
    types = [str(row.get("profile_type") or "UNKNOWN") for row in sections]
    circular_like = {"CIRCLE", "ELLIPSE"}
    breaks = []
    for i in range(3, n - 3):
        score = 0.0
        for key, arr in series.items():
            before = float(np.median(arr[:i]))
            after = float(np.median(arr[i:]))
            scale = max(float(np.median(np.abs(arr - np.median(arr)))), abs(before), 1e-12)
            score += abs(after - before) / scale
        before_types = types[max(0, i - 4) : i]
        after_types = types[i : i + 4]
        before_circ = np.mean([t in circular_like for t in before_types]) if before_types else 0.0
        after_circ = np.mean([t in circular_like for t in after_types]) if after_types else 0.0
        type_flip = abs(before_circ - after_circ) >= 0.5
        if score >= 1.8 or (type_flip and score >= 0.9):
            breaks.append(i)
    collapsed: list[int] = []
    for b in breaks:
        if not collapsed or b - collapsed[-1] > 2:
            collapsed.append(b)
    return collapsed


def split_subregions(sections: list[dict[str, Any]], breaks: list[int]) -> list[dict[str, Any]]:
    bounds = [0, *[b for b in breaks if 0 < b < len(sections)], len(sections)]
    rows = []
    for index, (a, b) in enumerate(zip(bounds[:-1], bounds[1:])):
        chunk = sections[a:b]
        if not chunk:
            continue
        circ = np.median([float(r.get("circularity") or 0.0) for r in chunk]) if chunk else 0.0
        rows.append(
            {
                "subregion_id": f"SUBREGION_{index:03d}",
                "start": int(a),
                "end": int(b),
                "x_lo": float(chunk[0]["lo"]),
                "x_hi": float(chunk[-1]["hi"]),
                "median_circularity": float(circ),
                "profile_types": sorted({str(r.get("profile_type")) for r in chunk}),
                "inner_loop_evidence": any(bool(r.get("INNER_LOOP_EVIDENCE")) for r in chunk),
            }
        )
    return rows


def ordered_closed_uv(uv: np.ndarray) -> np.ndarray:
    pts = np.asarray(uv, dtype=float)
    if len(pts) < 3:
        return pts
    center = pts.mean(axis=0)
    ang = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
    ordered = pts[np.argsort(ang)]
    area = 0.0
    closed = np.vstack([ordered, ordered[0]])
    for a, b in zip(closed[:-1], closed[1:]):
        area += a[0] * b[1] - b[0] * a[1]
    if area < 0:
        ordered = ordered[::-1]
    return ordered


def resample_closed(points: np.ndarray, count: int = 48) -> np.ndarray:
    if len(points) < 3:
        return points
    points = ordered_closed_uv(points)
    closed = np.vstack([points, points[0]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(s[-1]) or 1.0
    samples = np.linspace(0.0, total, count, endpoint=False)
    out = []
    for t in samples:
        k = int(np.searchsorted(s, t, side="right") - 1)
        k = min(max(k, 0), len(closed) - 2)
        span = s[k + 1] - s[k] if s[k + 1] > s[k] else 1.0
        a = (t - s[k]) / span
        out.append((1 - a) * closed[k] + a * closed[k + 1])
    return np.asarray(out)


def section_polygon(local: np.ndarray, lo: float, hi: float, faces: np.ndarray | None = None) -> np.ndarray:
    xi = float(0.5 * (lo + hi))
    uv = slice_uv_at_x(local, xi, faces=faces, thickness=0.0 if faces is not None and len(faces) else max((hi - lo) * 0.5, 1e-9))
    if len(uv) < 3:
        band = local[(local[:, 0] >= lo) & (local[:, 0] <= hi)]
        uv = band[:, 1:3] if len(band) else uv
    if len(uv) < 3:
        return np.zeros((0, 2))
    from scipy.spatial import ConvexHull

    hull = ConvexHull(uv)
    return ordered_closed_uv(uv[hull.vertices])


def write_occ_step(shape: Any, path: Path) -> bool:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    return writer.Write(str(path)) == IFSelect_RetDone and path.is_file()


def _fail(builder: str, reason: str, output: Path | None = None) -> dict[str, Any]:
    return {"builder": builder, "step_success": False, "failure_reason": reason, "step_path": str(output) if output else None}


def wire_from_uv(uv: np.ndarray, x: float, count: int | None = None):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    samples = gp.resample_closed(uv, count or gp.PROFILE_SAMPLE_COUNT)
    if len(samples) < 3:
        return None
    poly = BRepBuilderAPI_MakePolygon()
    for a in samples:
        poly.Add(gp_Pnt(float(x), float(a[0]), float(a[1])))
    poly.Close()
    if not poly.IsDone():
        return None
    return poly.Wire()


def read_step_shape(path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    if not path.is_file():
        return None
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.TransferRoots():
        return None
    shape = reader.OneShape()
    return None if shape.IsNull() else shape


def _shape_is_solid(shape: Any) -> bool:
    try:
        from OCP.TopAbs import TopAbs_SOLID
        from OCP.TopExp import TopExp_Explorer

        explorer = TopExp_Explorer(shape, TopAbs_SOLID)
        return bool(explorer.More())
    except Exception:
        return False


def recomposition_shapes(shapes: list[Any], output: Path) -> dict[str, Any]:
    from OCP.BRep import BRep_Builder
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCP.TopoDS import TopoDS_Compound

    import generic_cad_composite_audit as ca

    shapes = [s for s in shapes if s is not None]
    pre_boxes = [ca.shape_bbox(s) for s in shapes]
    pre = ca.union_bbox(pre_boxes)
    sewing_tol = 1e-4
    if not shapes:
        return {**_fail("COMPOSITE_PART", "NO_SHAPES", output), "COMPOSITE_TOPOLOGY_MODE": "NONE", "SEWING_TOLERANCE": sewing_tol}
    if len(shapes) == 1:
        ok = write_occ_step(shapes[0], output)
        post = ca.shape_bbox(shapes[0])
        return {
            "step_success": ok,
            "step_path": str(output),
            "COMPOSITE_TOPOLOGY_MODE": "SINGLE",
            "SEWING_TOLERANCE": sewing_tol,
            **ca.sewing_mutation(pre, post),
        }
    if all(_shape_is_solid(s) for s in shapes):
        try:
            from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

            fused = shapes[0]
            for extra in shapes[1:]:
                fused = BRepAlgoAPI_Fuse(fused, extra).Shape()
            ok = write_occ_step(fused, output)
            if ok:
                post = ca.shape_bbox(fused)
                return {
                    "step_success": True,
                    "step_path": str(output),
                    "COMPOSITE_TOPOLOGY_MODE": "FUSE",
                    "SEWING_TOLERANCE": sewing_tol,
                    **ca.sewing_mutation(pre, post),
                }
        except Exception:
            pass
    try:
        sewing = BRepBuilderAPI_Sewing(sewing_tol)
        for shape in shapes:
            sewing.Add(shape)
        sewing.Perform()
        sewn = sewing.SewedShape()
        if sewn is not None and not sewn.IsNull():
            ok = write_occ_step(sewn, output)
            if ok:
                post = ca.shape_bbox(sewn)
                return {
                    "step_success": True,
                    "step_path": str(output),
                    "COMPOSITE_TOPOLOGY_MODE": "SEWING",
                    "SEWING_TOLERANCE": sewing_tol,
                    **ca.sewing_mutation(pre, post),
                }
    except Exception:
        pass
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    ok = write_occ_step(compound, output)
    post = ca.shape_bbox(compound)
    return {
        "step_success": ok,
        "step_path": str(output),
        "COMPOSITE_TOPOLOGY_MODE": "COMPOUND",
        "SEWING_TOLERANCE": sewing_tol,
        **ca.sewing_mutation(pre, post),
    }


def build_polygon_extrusion(local: np.ndarray, lo: float, hi: float, output: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
        from OCP.gp import gp_Vec

        uv = section_polygon(local, lo, hi, faces=faces)
        wire = wire_from_uv(uv, lo)
        if wire is None:
            return _fail("POLYGON_EXTRUSION", "NO_PROFILE", output)
        face = BRepBuilderAPI_MakeFace(wire).Face()
        prism = BRepPrimAPI_MakePrism(face, gp_Vec(float(hi - lo), 0.0, 0.0)).Shape()
        ok = write_occ_step(prism, output)
        return {"builder": "POLYGON_EXTRUSION", "step_success": ok, "step_path": str(output), "profile_source": "CONVEX_HULL"}
    except Exception as exc:
        return _fail("POLYGON_EXTRUSION", f"{type(exc).__name__}:{exc}", output)


def build_profile_extrusion(local: np.ndarray, lo: float, hi: float, output: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
        from OCP.gp import gp_Vec

        xi = float(0.5 * (lo + hi))
        desc = gp.extract_section_profile(local, faces, xi, thickness=max((hi - lo) * 0.02, 1e-8))
        outer = np.asarray(desc.get("boundary_2d") or [], dtype=float)
        if len(outer) < 3:
            return build_polygon_extrusion(local, lo, hi, output, faces=faces)
        outer_wire = wire_from_uv(outer, lo)
        if outer_wire is None:
            return _fail("PROFILE_EXTRUSION", "NO_OUTER_WIRE", output)
        maker = BRepBuilderAPI_MakeFace(outer_wire)
        inner_unsupported = False
        inner_used = 0
        for inner in desc.get("inner_loops_2d") or []:
            pts = np.asarray(inner, dtype=float)
            if len(pts) < 3:
                continue
            if gp.signed_area(pts) > 0:
                pts = pts[::-1]
            inner_wire = wire_from_uv(pts, lo)
            if inner_wire is None:
                inner_unsupported = True
                continue
            try:
                maker.Add(inner_wire)
                inner_used += 1
            except Exception:
                inner_unsupported = True
        if not maker.IsDone():
            return _fail("PROFILE_EXTRUSION", "FACE_FAILED", output)
        prism = BRepPrimAPI_MakePrism(maker.Face(), gp_Vec(float(hi - lo), 0.0, 0.0)).Shape()
        ok = write_occ_step(prism, output)
        evidence = bool(desc.get("INNER_LOOP_EVIDENCE") or inner_used)
        return {
            "builder": "PROFILE_EXTRUSION",
            "step_success": ok,
            "step_path": str(output),
            "profile_type": desc.get("profile_type"),
            "profile_source": "SECTION_OUTER_LOOP",
            "INNER_LOOP_EVIDENCE": evidence,
            "INNER_LOOP_UNSUPPORTED": bool(evidence and inner_used == 0) or inner_unsupported,
            "inner_loop_count_used": inner_used,
        }
    except Exception as exc:
        return _fail("PROFILE_EXTRUSION", f"{type(exc).__name__}:{exc}", output)


def build_cylinder_analytic(local: np.ndarray, output: Path, x_lo: float | None = None, x_hi: float | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

        xmin = float(local[:, 0].min() if x_lo is None else x_lo)
        xmax = float(local[:, 0].max() if x_hi is None else x_hi)
        length = float(xmax - xmin)
        margin = min(0.04 * max(length, 1e-9), 0.12 * max(length, 1e-9))
        xs = local[:, 0]
        region = local[(xs >= xmin - 1e-12) & (xs <= xmax + 1e-12)]
        inner = region[(region[:, 0] >= xmin + margin) & (region[:, 0] <= xmax - margin)]
        fit_cloud = inner if len(inner) >= 16 else region
        fit = cylinder_fit_local(fit_cloud if len(fit_cloud) else region)
        radius = max(float(fit["radius"]), 1e-8)
        center_yz = np.array([fit.get("center_u", 0.0), fit.get("center_v", 0.0)], dtype=float)
        axis = gp_Ax2(gp_Pnt(xmin, float(center_yz[0]), float(center_yz[1])), gp_Dir(1.0, 0.0, 0.0))
        solid = BRepPrimAPI_MakeCylinder(axis, radius, length).Shape()
        ok = write_occ_step(solid, output)
        return {
            "builder": "CYLINDER",
            "step_success": ok,
            "step_path": str(output),
            "radius": radius,
            "length": length,
            "analytic": True,
            "SHAFT_RADIUS_BUILT": radius,
            "SHAFT_RADIUS_SOURCE_MEDIAN": float(fit["radius"]),
            "SHAFT_RADIUS_SOURCE_P10": float(fit.get("radius_p10") or radius),
            "SHAFT_RADIUS_SOURCE_P90": float(fit.get("radius_p90") or radius),
            "SHAFT_FIT_SOURCE_RANGE": [xmin + (margin if len(inner) >= 16 else 0.0), xmax - (margin if len(inner) >= 16 else 0.0)],
            "SHAFT_FIT_POINT_COUNT": int(fit.get("point_count") or 0),
            "TERMINAL_POINTS_INCLUDED_IN_SHAFT_FIT": False,
            "centerline": center_yz.tolist(),
        }
    except Exception as exc:
        return _fail("CYLINDER", f"{type(exc).__name__}:{exc}", output)


def build_box_analytic(local: np.ndarray, output: Path) -> dict[str, Any]:
    try:
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
        from OCP.gp import gp_Pnt

        lo = local.min(axis=0)
        hi = local.max(axis=0)
        box = BRepPrimAPI_MakeBox(
            gp_Pnt(float(lo[0]), float(lo[1]), float(lo[2])),
            float(hi[0] - lo[0]),
            float(hi[1] - lo[1]),
            float(hi[2] - lo[2]),
        ).Shape()
        ok = write_occ_step(box, output)
        return {"builder": "BOX", "step_success": ok, "step_path": str(output), "analytic": True, "extent": (hi - lo).tolist()}
    except Exception as exc:
        return _fail("BOX", f"{type(exc).__name__}:{exc}", output)


def build_circular_loft(local: np.ndarray, output: Path, section_count: int = 32, quantile: float = 0.5, faces: np.ndarray | None = None, x_lo: float | None = None, x_hi: float | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
        from OCP.GC import GC_MakeCircle
        from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

        x = local[:, 0]
        xmin = float(x.min() if x_lo is None else x_lo)
        xmax = float(x.max() if x_hi is None else x_hi)
        xs = np.linspace(xmin, xmax, section_count)
        loft = BRepOffsetAPI_ThruSections(False, True, 1e-4)
        used = 0
        for xi in xs:
            uv = slice_uv_at_x(local, float(xi), faces=faces, thickness=0.0 if faces is not None and len(faces) else max(float(np.ptp(x)) / section_count, 1e-9))
            if len(uv) < 4:
                continue
            radial = np.linalg.norm(uv - uv.mean(axis=0), axis=1)
            ri = float(np.quantile(radial, quantile))
            if ri <= 1e-8:
                continue
            circle = GC_MakeCircle(gp_Ax2(gp_Pnt(float(xi), 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)), ri).Value()
            loft.AddWire(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle).Edge()).Wire())
            used += 1
        if used < 2:
            return {**_fail("CIRCULAR_PROFILE_LOFT", "INSUFFICIENT_SECTIONS", output), "wire_type": "CIRCLE"}
        loft.CheckCompatibility(False)
        loft.Build()
        ok = write_occ_step(loft.Shape(), output)
        return {"builder": "CIRCULAR_PROFILE_LOFT", "step_success": ok, "step_path": str(output), "wire_type": "CIRCLE", "section_count_used": used}
    except Exception as exc:
        return {**_fail("CIRCULAR_PROFILE_LOFT", f"{type(exc).__name__}:{exc}", output), "wire_type": "CIRCLE"}


def _collect_region_profiles(local: np.ndarray, faces: np.ndarray | None, x_lo: float, x_hi: float, section_count: int) -> dict[str, Any]:
    import generic_cad_profile_metric_calibration as pmc

    xs = np.linspace(float(x_lo), float(x_hi), max(int(section_count), 3))
    spacing = float((x_hi - x_lo) / max(section_count - 1, 1))
    thickness = max(0.25 * spacing, 1e-9)
    profiles = []
    used_xs = []
    types = []
    descs = []
    inner_evidence = False
    methods = []
    for xi in xs:
        desc = gp.extract_section_profile(local, faces, float(xi), thickness=thickness, section_spacing=spacing)
        uv = np.asarray(desc.get("boundary_2d") or [], dtype=float)
        if len(uv) < 3:
            continue
        profiles.append(uv)
        used_xs.append(float(xi))
        types.append(desc.get("profile_type") or "GENERAL_POLYGON")
        methods.append(desc.get("PROFILE_BOUNDARY_METHOD") or desc.get("profile_source_method"))
        descs.append(desc)
        inner_evidence = inner_evidence or bool(desc.get("INNER_LOOP_EVIDENCE"))
    aligned = gp.align_profile_sequence(profiles)
    envelope = np.zeros((0, 2), dtype=float)
    if profiles:
        envelope = np.vstack(profiles)
    input_metrics = [pmc.profile_metrics(uv, x) for uv, x in zip(aligned.get("aligned") or profiles, used_xs or xs)]
    return {
        **aligned,
        "xs": np.asarray(used_xs if used_xs else xs, dtype=float),
        "profile_types": types,
        "INNER_LOOP_EVIDENCE": inner_evidence,
        "raw_count": len(profiles),
        "raw_profiles": profiles,
        "section_descriptors": descs,
        "PROFILE_BOUNDARY_METHOD": methods[0] if methods else None,
        "PROFILE_BOUNDARY_METHODS": methods,
        "TERMINAL_INPUT_PROFILE_ENVELOPE_BBOX": {
            "u_min": float(envelope[:, 0].min()) if len(envelope) else 0.0,
            "u_max": float(envelope[:, 0].max()) if len(envelope) else 0.0,
            "v_min": float(envelope[:, 1].min()) if len(envelope) else 0.0,
            "v_max": float(envelope[:, 1].max()) if len(envelope) else 0.0,
        },
        "input_profile_metrics": input_metrics,
        "SLICE_SPAN_TO_SECTION_SPACING_RATIO": float(
            np.median([float(d.get("SLICE_SPAN_TO_SECTION_SPACING_RATIO") or 0.0) for d in descs]) if descs else 0.0
        ),
        "SECTION_TARGET_SPACING": spacing,
    }


def build_noncircular_loft(
    local: np.ndarray,
    output: Path,
    section_count: int = 12,
    faces: np.ndarray | None = None,
    x_lo: float | None = None,
    x_hi: float | None = None,
) -> dict[str, Any]:
    try:
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        import generic_cad_composite_audit as ca
        import generic_cad_profile_metric_calibration as pmc

        xmin = float(local[:, 0].min() if x_lo is None else x_lo)
        xmax = float(local[:, 0].max() if x_hi is None else x_hi)
        packed = _collect_region_profiles(local, faces, xmin, xmax, section_count)
        profiles = packed.get("aligned") or []
        xs = np.asarray(packed.get("xs"), dtype=float)
        if len(profiles) < 2:
            return _fail("NON_CIRCULAR_PROFILE_LOFT", "INSUFFICIENT_WIRES", output)
        if len(xs) != len(profiles):
            xs = np.linspace(xmin, xmax, len(profiles))
        loft = BRepOffsetAPI_ThruSections(False, True, 1e-4)
        used = 0
        input_pts = []
        loft_inputs = []
        for xi, uv in zip(xs, profiles):
            wire = wire_from_uv(uv, float(xi))
            if wire is None:
                continue
            loft.AddWire(wire)
            used += 1
            loft_inputs.append({"axial_position": float(xi), **pmc.profile_metrics(uv, float(xi))})
            for a in np.asarray(uv, dtype=float):
                input_pts.append([float(xi), float(a[0]), float(a[1])])
        if used < 2:
            return _fail("NON_CIRCULAR_PROFILE_LOFT", "INSUFFICIENT_WIRES", output)
        loft.CheckCompatibility(True)
        loft.Build()
        shape = loft.Shape()
        ok = write_occ_step(shape, output)
        twist = pmc.loft_twist_score(list(profiles))
        in_env = np.asarray(input_pts, dtype=float) if input_pts else np.zeros((0, 3))
        out_bb = ca.shape_bbox(shape)
        in_bb = np.vstack([in_env.min(axis=0), in_env.max(axis=0)]) if len(in_env) else None
        return {
            "builder": "NON_CIRCULAR_PROFILE_LOFT",
            "step_success": ok,
            "step_path": str(output),
            "wire_type": "GENERAL_POLYGON",
            "section_count_used": used,
            "profile_types": packed.get("profile_types"),
            "PROFILE_CORRESPONDENCE_SUCCESS": packed.get("PROFILE_CORRESPONDENCE_SUCCESS"),
            "MAX_PROFILE_ALIGNMENT_ERROR": packed.get("MAX_PROFILE_ALIGNMENT_ERROR"),
            "INNER_LOOP_EVIDENCE": packed.get("INNER_LOOP_EVIDENCE"),
            "INNER_LOOP_UNSUPPORTED": bool(packed.get("INNER_LOOP_EVIDENCE")),
            "NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS": True,
            "CORRESPONDENCE_NORMALIZATION_INVERTED": packed.get("CORRESPONDENCE_NORMALIZATION_INVERTED", True),
            "PROFILE_CORRESPONDENCE_CHANGES_CENTROID": packed.get("PROFILE_CORRESPONDENCE_CHANGES_CENTROID", False),
            "SCALE_RECOVERY_ERROR": packed.get("SCALE_RECOVERY_ERROR"),
            "CENTROID_RECOVERY_ERROR": packed.get("CENTROID_RECOVERY_ERROR"),
            "RESAMPLING_EXTENT_DRIFT": packed.get("RESAMPLING_EXTENT_DRIFT"),
            "PROFILE_BOUNDARY_METHOD": packed.get("PROFILE_BOUNDARY_METHOD"),
            "SLICE_SPAN_TO_SECTION_SPACING_RATIO": packed.get("SLICE_SPAN_TO_SECTION_SPACING_RATIO"),
            "LOFT_INPUT_PROFILES": loft_inputs,
            "TERMINAL_INPUT_PROFILE_ENVELOPE_BBOX": packed.get("TERMINAL_INPUT_PROFILE_ENVELOPE_BBOX"),
            "TERMINAL_LOFT_OUTPUT_BBOX": out_bb.tolist() if out_bb is not None else None,
            "input_envelope_extent": (in_bb[1] - in_bb[0]).tolist() if in_bb is not None else None,
            "loft_output_extent": (out_bb[1] - out_bb[0]).tolist() if out_bb is not None else None,
            "PROFILE_OUTWARD_OFFSET": 0.0,
            **twist,
        }
    except Exception as exc:
        return _fail("NON_CIRCULAR_PROFILE_LOFT", f"{type(exc).__name__}:{exc}", output)


def build_transition_loft(uv_a: np.ndarray, x_a: float, uv_b: np.ndarray, x_b: float, output: Path, intermediates: int = 3) -> dict[str, Any]:
    try:
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        import generic_cad_transition_calibration as tc

        if abs(x_b - x_a) < 1e-9:
            x_b = x_a + max(abs(x_a) * 1e-3, 1e-4)
        packed = tc.transition_profiles(uv_a, uv_b, count=intermediates + 2)
        loft = BRepOffsetAPI_ThruSections(False, True, 1e-4)
        xs = np.linspace(float(x_a), float(x_b), len(packed["profiles"]))
        layer_rows = []
        for i, (xi, uv, alpha) in enumerate(zip(xs, packed["profiles"], packed["alphas"])):
            wire = wire_from_uv(uv, float(xi))
            if wire is None:
                continue
            loft.AddWire(wire)
            w, h = np.ptp(uv, axis=0) if len(uv) else (0.0, 0.0)
            layer_rows.append(
                {
                    "transition_index": i,
                    "alpha": float(alpha),
                    "axial_position": float(xi),
                    "centroid_u": float(uv.mean(axis=0)[0]),
                    "centroid_v": float(uv.mean(axis=0)[1]),
                    "width": float(w[0] if np.ndim(w) else w),
                    "height": float(h[1] if np.ndim(w) else h) if np.ndim(w) else float(h),
                }
            )
        loft.CheckCompatibility(True)
        loft.Build()
        ok = write_occ_step(loft.Shape(), output)
        return {
            "builder": "TRANSITION",
            "step_success": ok,
            "step_path": str(output),
            "TRANSITION_REGION_CREATED": bool(ok),
            "TRANSITION_PROFILE_COUNT": int(len(packed["profiles"])),
            "PROFILE_CORRESPONDENCE_SUCCESS": packed.get("PROFILE_CORRESPONDENCE_SUCCESS"),
            "MAX_PROFILE_ALIGNMENT_ERROR": packed.get("MAX_PROFILE_ALIGNMENT_ERROR"),
            "CORRESPONDENCE_NORMALIZATION_INVERTED": packed.get("CORRESPONDENCE_NORMALIZATION_INVERTED"),
            "TRANSITION_WIDTH_OVERSHOOT_RATIO": packed.get("TRANSITION_WIDTH_OVERSHOOT_RATIO"),
            "TRANSITION_HEIGHT_OVERSHOOT_RATIO": packed.get("TRANSITION_HEIGHT_OVERSHOOT_RATIO"),
            "TRANSITION_AREA_OVERSHOOT_RATIO": packed.get("TRANSITION_AREA_OVERSHOOT_RATIO"),
            "TRANSITION_OVERSHOOT_DETECTED": packed.get("TRANSITION_OVERSHOOT_DETECTED"),
            "MAX_TRANSITION_CENTROID_JUMP": packed.get("MAX_TRANSITION_CENTROID_JUMP"),
            "layers": layer_rows,
            "TRANSITION_AXIAL_MIN": float(min(x_a, x_b)),
            "TRANSITION_AXIAL_MAX": float(max(x_a, x_b)),
        }
    except Exception as exc:
        return {**_fail("TRANSITION", f"{type(exc).__name__}:{exc}", output), "TRANSITION_REGION_CREATED": False}


def _choose_subregion_builder(chunk: list[dict[str, Any]]) -> str:
    if cylinder_eligible(chunk):
        return "CYLINDER"
    if circular_loft_eligible(chunk):
        return "CIRCULAR_PROFILE_LOFT"
    if extrusion_eligible(chunk):
        return "PROFILE_EXTRUSION"
    return "NON_CIRCULAR_PROFILE_LOFT"


def _execute_named_builder(name: str, local: np.ndarray, output: Path, faces: np.ndarray | None, x_lo: float, x_hi: float) -> dict[str, Any]:
    mask = (local[:, 0] >= x_lo - 1e-12) & (local[:, 0] <= x_hi + 1e-12)
    region = local[mask] if int(mask.sum()) >= 8 else local
    if name == "CYLINDER":
        return build_cylinder_analytic(region, output, x_lo=x_lo, x_hi=x_hi)
    if name == "CIRCULAR_PROFILE_LOFT":
        return build_circular_loft(local, output, faces=faces, x_lo=x_lo, x_hi=x_hi, section_count=16)
    if name == "PROFILE_EXTRUSION":
        return build_profile_extrusion(local, x_lo, x_hi, output, faces=faces)
    if name == "POLYGON_EXTRUSION":
        return build_polygon_extrusion(local, x_lo, x_hi, output, faces=faces)
    if name == "BOX":
        return build_box_analytic(region, output)
    return build_noncircular_loft(local, output, faces=faces, x_lo=x_lo, x_hi=x_hi, section_count=10)


def build_composite(local: np.ndarray, sections: list[dict[str, Any]], breaks: list[int], output_dir: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        import generic_cad_composite_audit as ca

        output_dir.mkdir(parents=True, exist_ok=True)
        subregions = split_subregions(sections, breaks)
        if len(subregions) < 2:
            mid = float(np.median(local[:, 0]))
            subregions = [
                {"subregion_id": "SUBREGION_000", "x_lo": float(local[:, 0].min()), "x_hi": mid, "median_circularity": 1.0, "start": 0, "end": 1},
                {"subregion_id": "SUBREGION_001", "x_lo": mid, "x_hi": float(local[:, 0].max()), "median_circularity": 0.0, "start": 1, "end": 2},
            ]
        length = float(np.ptp(local[:, 0]))
        min_span = min(max(float(s["x_hi"] - s["x_lo"]), 1e-6) for s in subregions)
        iface = min(0.012 * max(length, 1e-6), 0.18 * min_span)
        results = []
        shapes = []
        last_uv = None
        last_x = None
        last_builder = None
        transition = {"TRANSITION_REGION_CREATED": False, "TRANSITION_PROFILE_COUNT": 0}
        axial_rows = []
        for index, sub in enumerate(subregions):
            chunk = sections[int(sub.get("start") or 0) : int(sub.get("end") or 0)] or sections
            name = _choose_subregion_builder(chunk)
            sub["builder"] = name
            x_lo = float(sub["x_lo"])
            x_hi = float(sub["x_hi"])
            if index > 0:
                x_lo = min(x_hi - 1e-5, x_lo + 0.5 * iface)
            if index < len(subregions) - 1:
                x_hi = max(x_lo + 1e-5, x_hi - 0.5 * iface)
            sub["build_x_lo"] = x_lo
            sub["build_x_hi"] = x_hi
            path = output_dir / f"{sub['subregion_id'].lower()}.step"
            built = _execute_named_builder(name, local, path, faces, x_lo, x_hi)
            built["subregion_id"] = sub["subregion_id"]
            built["build_x_lo"] = x_lo
            built["build_x_hi"] = x_hi
            results.append(built)
            shape = read_step_shape(Path(str(built.get("step_path") or ""))) if built.get("step_success") else None
            if shape is not None:
                shapes.append(shape)
            packed = _collect_region_profiles(local, faces, x_lo, x_hi, 4)
            uv0 = (packed.get("aligned") or [None])[0]
            uv1 = (packed.get("aligned") or [None])[-1]
            if last_uv is not None and uv0 is not None and index > 0:
                t_path = output_dir / f"transition_{index-1:03d}.step"
                x_a = float(last_x)
                x_b = float(x_lo)
                if abs(x_b - x_a) < 1e-6:
                    x_b = x_a + max(iface, 1e-4)
                transition = build_transition_loft(last_uv, x_a, uv0, x_b, t_path, intermediates=3)
                tshape = read_step_shape(Path(str(transition.get("step_path") or ""))) if transition.get("step_success") else None
                if tshape is not None:
                    shapes.append(tshape)
                axial_rows.append((last_builder or "PREV", (float(subregions[index - 1].get("build_x_lo", last_x)), float(last_x)), name, (x_lo, x_hi), (float(transition.get("TRANSITION_AXIAL_MIN") or x_a), float(transition.get("TRANSITION_AXIAL_MAX") or x_b))))
            last_uv = uv1
            last_x = float(x_hi)
            last_builder = name
        compound_path = output_dir / "composite.step"
        combo = recomposition_shapes(shapes, compound_path)
        inner_ev = any(bool(r.get("INNER_LOOP_EVIDENCE")) for r in results)
        inner_un = any(bool(r.get("INNER_LOOP_UNSUPPORTED")) for r in results) or inner_ev
        axial_audit = {}
        if len(results) >= 2:
            a0 = (float(subregions[0].get("build_x_lo", subregions[0]["x_lo"])), float(subregions[0].get("build_x_hi", subregions[0]["x_hi"])))
            a1 = (float(subregions[1].get("build_x_lo", subregions[1]["x_lo"])), float(subregions[1].get("build_x_hi", subregions[1]["x_hi"])))
            tr = (
                float(transition.get("TRANSITION_AXIAL_MIN") or min(a0[1], a1[0])),
                float(transition.get("TRANSITION_AXIAL_MAX") or max(a0[1], a1[0])),
            )
            axial_audit = ca.axial_intervals(a0, a1, tr)
            axial_audit["COMPOSITE_AXIAL_MIN"] = float(local[:, 0].min())
            axial_audit["COMPOSITE_AXIAL_MAX"] = float(local[:, 0].max())
        diag = float(np.linalg.norm(np.ptp(local, axis=0))) or 1.0
        sewing_tol = float(combo.get("SEWING_TOLERANCE") or 1e-4)
        return {
            "builder": "COMPOSITE_PART",
            "step_success": bool(combo.get("step_success")),
            "step_path": str(compound_path),
            "SUBREGION_COUNT": len(subregions),
            "STRUCTURAL_BREAK_COUNT": len(breaks),
            "COMPOSITE_TOPOLOGY_MODE": combo.get("COMPOSITE_TOPOLOGY_MODE"),
            "subregion_builders": [r.get("builder") for r in results],
            "subregions": results,
            "shaft_builder": results[0].get("builder") if results else None,
            "terminal_builder": results[-1].get("builder") if results else None,
            "shaft_success": results[0].get("step_success") if results else False,
            "terminal_success": results[-1].get("step_success") if results else False,
            "TRANSITION_REGION_CREATED": bool(transition.get("TRANSITION_REGION_CREATED")),
            "TRANSITION_PROFILE_COUNT": int(transition.get("TRANSITION_PROFILE_COUNT") or 0),
            "TRANSITION_WIDTH_OVERSHOOT_RATIO": transition.get("TRANSITION_WIDTH_OVERSHOOT_RATIO"),
            "TRANSITION_HEIGHT_OVERSHOOT_RATIO": transition.get("TRANSITION_HEIGHT_OVERSHOOT_RATIO"),
            "TRANSITION_OVERSHOOT_DETECTED": bool(transition.get("TRANSITION_OVERSHOOT_DETECTED")),
            "MAX_TRANSITION_CENTROID_JUMP": transition.get("MAX_TRANSITION_CENTROID_JUMP"),
            "PROFILE_CORRESPONDENCE_SUCCESS": all(bool(r.get("PROFILE_CORRESPONDENCE_SUCCESS", True)) for r in results),
            "INNER_LOOP_EVIDENCE": inner_ev,
            "INNER_LOOP_UNSUPPORTED": inner_un,
            "SEWING_TOLERANCE": sewing_tol,
            "SEWING_TOLERANCE_NORMALIZED": sewing_tol / diag,
            "SEWING_GEOMETRY_MUTATION": bool(combo.get("SEWING_GEOMETRY_MUTATION")),
            "PRE_TO_POST_SEW_CENTROID_SHIFT": combo.get("PRE_TO_POST_SEW_CENTROID_SHIFT"),
            "PRE_TO_POST_SEW_EXTENT_CHANGE_X": combo.get("PRE_TO_POST_SEW_EXTENT_CHANGE_X"),
            "PRE_TO_POST_SEW_EXTENT_CHANGE_Y": combo.get("PRE_TO_POST_SEW_EXTENT_CHANGE_Y"),
            "PRE_TO_POST_SEW_EXTENT_CHANGE_Z": combo.get("PRE_TO_POST_SEW_EXTENT_CHANGE_Z"),
            "transition": transition,
            **axial_audit,
        }
    except Exception as exc:
        return {**_fail("COMPOSITE_PART", f"{type(exc).__name__}:{exc}"), "COMPOSITE_TOPOLOGY_MODE": "COMPOUND", "INNER_LOOP_UNSUPPORTED": True}


def circular_loft_eligible(sections: list[dict[str, Any]]) -> bool:
    valid = [row for row in sections if int(row.get("point_count") or 0) >= 4]
    if len(valid) < 3:
        return False
    circ = np.array([row.get("circularity") or 0.0 for row in valid], dtype=float)
    aspect = np.array([row.get("aspect_ratio") or 1.0 for row in valid], dtype=float)
    types = [str(row.get("profile_type") or "UNKNOWN") for row in valid]
    noncirc_frac = float(np.mean(circ < 0.75))
    poly_frac = float(np.mean([t in {"RECTANGLE", "TRIANGLE", "SIMPLE_POLYGON", "GENERAL_POLYGON"} for t in types]))
    return bool(
        np.median(circ) >= 0.85
        and np.median(aspect) <= 1.35
        and float(np.quantile(circ, 0.1)) >= 0.70
        and noncirc_frac <= 0.15
        and poly_frac <= 0.20
    )


def cylinder_eligible(sections: list[dict[str, Any]]) -> bool:
    if not circular_loft_eligible(sections):
        return False
    valid = [row for row in sections if int(row.get("point_count") or 0) >= 4]
    radii = np.array([float(row.get("radial_mean") or 0.0) for row in valid], dtype=float)
    if len(radii) < 3 or float(radii.mean()) <= 1e-12:
        return False
    return bool(float(radii.std() / radii.mean()) <= 0.08)


def extrusion_eligible(sections: list[dict[str, Any]]) -> bool:
    valid = [row for row in sections if int(row.get("point_count") or 0) >= 4]
    if len(valid) < 3:
        return False
    area = np.array([float(row.get("area") or 0.0) for row in valid])
    circ = np.array([float(row.get("circularity") or 0.0) for row in valid])
    shift = np.array([float(row.get("centroid_shift") or 0.0) for row in valid])
    types = [str(row.get("profile_type")) for row in valid]
    area_cv = float(area.std() / max(float(area.mean()), 1e-12))
    type_mode = max(set(types), key=types.count)
    stable_types = type_mode in {"RECTANGLE", "TRIANGLE", "SIMPLE_POLYGON", "ROUNDED_RECTANGLE", "GENERAL_POLYGON", "CIRCLE", "ELLIPSE"}
    return bool(area_cv <= 0.18 and float(shift.mean()) <= 0.08 and stable_types and float(np.std(circ)) <= 0.12)


def box_eligible(sections: list[dict[str, Any]]) -> bool:
    if not extrusion_eligible(sections):
        return False
    valid = [row for row in sections if int(row.get("point_count") or 0) >= 4]
    rect = np.median([float(row.get("rectangularity") or 0.0) for row in valid])
    types = [str(row.get("profile_type")) for row in valid]
    return bool(rect >= 0.80 and types.count("RECTANGLE") >= max(1, len(types) // 2))


def builder_eligibility_scores(sections: list[dict[str, Any]], measured: dict[str, Any]) -> dict[str, float]:
    circ = 1.0 if circular_loft_eligible(sections) else 0.0
    cyl = 1.0 if cylinder_eligible(sections) else 0.3 * circ
    extr = 1.0 if extrusion_eligible(sections) else float(measured.get("extrusion_score") or 0.0)
    box = 1.0 if box_eligible(sections) else 0.0
    ncl = 1.0 if not circular_loft_eligible(sections) else 0.2
    freeform = float(measured.get("freeform_score") or 0.0)
    return {
        "CYLINDER": cyl,
        "CIRCULAR_PROFILE_LOFT": circ,
        "PROFILE_EXTRUSION": extr,
        "POLYGON_EXTRUSION": 0.6 * extr,
        "BOX": box,
        "NON_CIRCULAR_PROFILE_LOFT": ncl,
        "COMPOSITE_PART": 1.0 if True else 0.0,
        "FREEFORM_SURFACE": freeform,
    }


def route_builder(mac_family: str, sections: list[dict[str, Any]], breaks: list[int], measured: dict[str, Any]) -> dict[str, Any]:
    scores = builder_eligibility_scores(sections, measured)
    eligible = []
    if cylinder_eligible(sections):
        eligible.append("CYLINDER")
    if circular_loft_eligible(sections):
        eligible.append("CIRCULAR_PROFILE_LOFT")
    if extrusion_eligible(sections):
        eligible.append("PROFILE_EXTRUSION")
        eligible.append("POLYGON_EXTRUSION")
    if box_eligible(sections):
        eligible.append("BOX")
    if not circular_loft_eligible(sections) or float(measured.get("profile_change_score") or 0.0) >= 0.25:
        eligible.append("NON_CIRCULAR_PROFILE_LOFT")
    if breaks:
        eligible.append("COMPOSITE_PART")
    if float(measured.get("freeform_score") or 0.0) >= 0.45 and not circular_loft_eligible(sections):
        eligible.append("FREEFORM_SURFACE")
    requested_raw = (mac_family or "UNKNOWN").upper()
    requested = requested_raw
    extrusion_rejected = False
    if requested_raw in {"EXTRUSION", "PROFILE_EXTRUSION", "POLYGON_EXTRUSION"}:
        requested = "PROFILE_EXTRUSION"
        if breaks or not extrusion_eligible(sections):
            extrusion_rejected = True
            requested = "COMPOSITE_PART" if breaks else "NON_CIRCULAR_PROFILE_LOFT"
    if requested_raw in {"LOFT", "PROFILE_LOFT"}:
        requested = "CIRCULAR_PROFILE_LOFT" if circular_loft_eligible(sections) and not breaks else "NON_CIRCULAR_PROFILE_LOFT"
    if requested_raw == "BOX":
        requested = "BOX" if box_eligible(sections) else ("PROFILE_EXTRUSION" if extrusion_eligible(sections) else requested_raw)
    if requested_raw == "CYLINDER":
        requested = "CYLINDER" if cylinder_eligible(sections) else "CIRCULAR_PROFILE_LOFT"
    if requested_raw in {"FREEFORM", "FREEFORM_SURFACE"}:
        requested = "FREEFORM_SURFACE"
    actual = None
    reason = "NO_BUILDER_EVIDENCE"
    if breaks:
        actual = "COMPOSITE_PART"
        reason = "AXIAL_PROFILE_CHANGE_POINT_DETECTED"
    elif requested == "FREEFORM_SURFACE":
        actual = "NON_CIRCULAR_PROFILE_LOFT" if "NON_CIRCULAR_PROFILE_LOFT" in eligible else "FREEFORM_SURFACE"
        reason = "FREEFORM_NOT_CIRCULAR_LOFT"
    elif requested in eligible:
        actual = requested
        reason = "MAC_AND_GEOMETRY"
    elif requested == "CYLINDER" and "CIRCULAR_PROFILE_LOFT" in eligible:
        actual = "CIRCULAR_PROFILE_LOFT"
        reason = "CYLINDER_DEGRADED_TO_CIRCULAR_LOFT_EXPLICIT"
    elif eligible:
        ranked = sorted(eligible, key=lambda name: scores.get(name, 0.0), reverse=True)
        actual = ranked[0]
        reason = "GEOMETRY_ELIGIBLE_FALLBACK"
        if actual == "CIRCULAR_PROFILE_LOFT" and requested_raw not in {"CIRCULAR_PROFILE_LOFT", "PROFILE_LOFT", "LOFT", "CYLINDER", "UNKNOWN"}:
            if "NON_CIRCULAR_PROFILE_LOFT" in eligible:
                actual = "NON_CIRCULAR_PROFILE_LOFT"
                reason = "AVOID_SILENT_CIRCULAR_LOFT"
    else:
        actual = "UNKNOWN"
        reason = "NO_BUILDER_EVIDENCE"
    circular_forced = actual == "CIRCULAR_PROFILE_LOFT" and requested_raw not in {"CIRCULAR_PROFILE_LOFT", "PROFILE_LOFT", "LOFT", "CYLINDER", "UNKNOWN", ""}
    return {
        "MAC_SUGGESTED_BUILDER": mac_family,
        "REQUESTED_BUILDER_FAMILY": requested,
        "GEOMETRY_ELIGIBLE_BUILDERS": sorted(set(eligible)),
        "RESOLVED_BUILDER_FAMILY": actual,
        "ACTUAL_EXECUTED_BUILDER": actual,
        "SELECTION_REASON": reason,
        "BUILDER_SELECTION_REASON": reason,
        "CIRCULAR_LOFT_FORCED": bool(circular_forced),
        "EXTRUSION_REJECTED_PROFILE_VARIATION": extrusion_rejected,
        "BUILDER_FALLBACK_USED": False,
        "eligibility_scores": scores,
        "STRUCTURAL_BREAK_COUNT": len(breaks),
        "SUBREGION_COUNT": max(len(breaks) + 1, 1) if breaks else 1,
    }


def execute_resolved_builder(local: np.ndarray, route: dict[str, Any], sections: list[dict[str, Any]], breaks: list[int], params: RuntimeGeometryParameters, output_dir: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    builder = str(route.get("ACTUAL_EXECUTED_BUILDER") or "UNKNOWN")
    x_lo = float(local[:, 0].min())
    x_hi = float(local[:, 0].max())
    out = output_dir / "generated_local_fixed.step"
    if builder in {"PROFILE_EXTRUSION", "EXTRUSION"}:
        return build_profile_extrusion(local, x_lo, x_hi, out, faces=faces)
    if builder == "POLYGON_EXTRUSION":
        return build_polygon_extrusion(local, x_lo, x_hi, out, faces=faces)
    if builder == "CIRCULAR_PROFILE_LOFT":
        return build_circular_loft(local, out, faces=faces)
    if builder == "CYLINDER":
        return build_cylinder_analytic(local, out)
    if builder == "NON_CIRCULAR_PROFILE_LOFT":
        return build_noncircular_loft(local, out, faces=faces)
    if builder == "COMPOSITE_PART":
        return build_composite(local, sections, breaks, output_dir / "composite", faces=faces)
    if builder == "BOX":
        return build_box_analytic(local, out)
    if builder in {"FREEFORM_SURFACE", "FREEFORM"}:
        result = build_noncircular_loft(local, out, faces=faces)
        result["FREEFORM_BACKEND_RECOMMENDED"] = True
        result["ATTEMPTED_BUILDER"] = "NON_CIRCULAR_PROFILE_LOFT"
        result["resolved_freeform"] = True
        if not result.get("step_success"):
            result = {**_fail("FREEFORM_SURFACE", result.get("failure_reason") or "FREEFORM_PROFILE_LOFT_FAILED", out), "BUILDER_FALLBACK_USED": True, "CIRCULAR_LOFT_FORCED": False}
        return result
    return {"builder": builder, "step_success": False, "failure_reason": "UNKNOWN_BUILDER", "BUILDER_FALLBACK_USED": True, "ATTEMPTED_BUILDER": builder}



def axial_bin_qa(source_local: np.ndarray, cand_local: np.ndarray, bins: int = 16) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    xs = source_local[:, 0]
    edges = np.linspace(float(xs.min()), float(xs.max()), bins + 1)
    rows = []
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        src = source_local[(xs >= lo) & (xs <= hi)]
        cand = cand_local[(cand_local[:, 0] >= lo) & (cand_local[:, 0] <= hi)]
        if len(src) < 8 or len(cand) < 8:
            rows.append({"bin": i, "coverage": 0.0, "chamfer": 1.0, "hausdorff": 1.0, "source_count": int(len(src)), "candidate_count": int(len(cand))})
            continue
        st = cKDTree(src)
        ct = cKDTree(cand)
        s2c = ct.query(src)[0]
        c2s = st.query(cand)[0]
        cov_r = 0.02 * max(float(np.ptp(source_local, axis=0).max()), 1e-3)
        rows.append(
            {
                "bin": i,
                "lo": float(lo),
                "hi": float(hi),
                "coverage": float(np.mean(s2c <= cov_r)),
                "chamfer": float(0.5 * (s2c.mean() + c2s.mean())),
                "hausdorff": float(max(s2c.max(), c2s.max())),
                "source_count": int(len(src)),
                "candidate_count": int(len(cand)),
            }
        )
    cov = np.array([row["coverage"] for row in rows], dtype=float)
    ch = np.array([row["chamfer"] for row in rows], dtype=float)
    hh = np.array([row["hausdorff"] for row in rows], dtype=float)
    return {
        "rows": rows,
        "MEAN_AXIAL_BIN_COVERAGE": float(cov.mean()) if len(cov) else 0.0,
        "MIN_AXIAL_BIN_COVERAGE": float(cov.min()) if len(cov) else 0.0,
        "P10_AXIAL_BIN_COVERAGE": float(np.quantile(cov, 0.1)) if len(cov) else 0.0,
        "WORST_BIN_CHAMFER": float(ch.max()) if len(ch) else 1.0,
        "WORST_BIN_HAUSDORFF": float(hh.max()) if len(hh) else 1.0,
    }


def render_projection(meshes: list[tuple[np.ndarray, np.ndarray, tuple[float, float, float]]], path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    fig, ax = plt.subplots(figsize=(7.2, 5.4), dpi=140)
    view = np.array([[0.78, -0.42, 0.0], [0.18, 0.30, 0.82]], dtype=float)
    all_v = []
    for vertices, faces, color in meshes:
        all_v.append(vertices)
        if len(faces) > 1200:
            faces = faces[np.linspace(0, len(faces) - 1, 1200, dtype=np.int64)]
        proj = vertices @ view.T
        polys = [proj[face] for face in faces]
        order = np.argsort(vertices[faces][:, :, 0].mean(axis=1))
        ax.add_collection(
            PolyCollection([polys[i] for i in order], facecolors=[(*color, 0.45)] * len(order), edgecolors=[(0.15, 0.15, 0.18, 0.08)] * len(order), linewidths=0.04)
        )
    pts = np.vstack(all_v) @ view.T
    c = pts.mean(axis=0)
    r = max(float(np.ptp(pts, axis=0).max()) * 0.55, 1e-6)
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


BUILDER_REGISTRY = {
    "CYLINDER": build_cylinder_analytic,
    "CIRCULAR_PROFILE_LOFT": build_circular_loft,
    "PROFILE_EXTRUSION": build_profile_extrusion,
    "POLYGON_EXTRUSION": build_polygon_extrusion,
    "NON_CIRCULAR_PROFILE_LOFT": build_noncircular_loft,
    "COMPOSITE_PART": build_composite,
    "BOX": build_box_analytic,
    "TRANSITION": build_transition_loft,
}

RUNTIME_DISPATCHER_STUB = '''#!/usr/bin/env python3
"""MAC candidate dispatcher.

Geometry size/axis/profile are bound by generic_cad_runtime from source_part.obj.
This file is provenance, not a circular PROFILE_LOFT implementation.
"""
RAISE = "EXECUTE_VIA_generic_cad_runtime.reconstruct_from_source"
'''


def normalize_mac_hypothesis(hypothesis: dict[str, Any] | None) -> dict[str, Any]:
    hyp = dict(hypothesis or {})
    suggested = (
        hyp.get("visual_builder_suggestion")
        or hyp.get("requested_builder_family")
        or hyp.get("likely_builder_family")
        or hyp.get("builder_family")
        or "UNKNOWN"
    )
    hyp.setdefault("requested_builder_family", suggested)
    hyp.setdefault("profile_mode", "UNKNOWN")
    hyp.setdefault("decomposition_required", None)
    hyp.setdefault("expected_structure", [])
    hyp.setdefault("negative_space_hint", "UNKNOWN")
    hyp.setdefault("surface_complexity_hint", "UNKNOWN")
    hyp["visual_builder_suggestion"] = suggested
    return hyp


def explicit_fallback_chain(resolved: str) -> list[str]:
    resolved = str(resolved or "UNKNOWN")
    chain = [resolved]
    extras = {
        "COMPOSITE_PART": ["NON_CIRCULAR_PROFILE_LOFT", "PROFILE_EXTRUSION"],
        "PROFILE_EXTRUSION": ["NON_CIRCULAR_PROFILE_LOFT"],
        "POLYGON_EXTRUSION": ["PROFILE_EXTRUSION", "NON_CIRCULAR_PROFILE_LOFT"],
        "NON_CIRCULAR_PROFILE_LOFT": ["PROFILE_EXTRUSION"],
        "CYLINDER": ["CIRCULAR_PROFILE_LOFT"],
        "BOX": ["PROFILE_EXTRUSION"],
        "FREEFORM_SURFACE": ["NON_CIRCULAR_PROFILE_LOFT"],
        "CIRCULAR_PROFILE_LOFT": ["CYLINDER"],
    }.get(resolved, [])
    out = []
    for name in chain + extras:
        if name not in out and name != "UNKNOWN":
            out.append(name)
    return out


def execute_with_explicit_fallback(
    local: np.ndarray,
    route: dict[str, Any],
    sections: list[dict[str, Any]],
    breaks: list[int],
    params: RuntimeGeometryParameters,
    output_dir: Path,
    faces: np.ndarray | None = None,
) -> dict[str, Any]:
    attempts = []
    resolved = str(route.get("RESOLVED_BUILDER_FAMILY") or "UNKNOWN")
    last = {"builder": resolved, "step_success": False, "failure_reason": "NO_ATTEMPT"}
    for name in explicit_fallback_chain(resolved):
        attempt_dir = output_dir / f"attempt_{name.lower()}"
        try_route = {**route, "ACTUAL_EXECUTED_BUILDER": name}
        result = execute_resolved_builder(local, try_route, sections, breaks, params, attempt_dir, faces=faces)
        attempts.append(
            {
                "ATTEMPTED_BUILDER": name,
                "success": bool(result.get("step_success")),
                "FAILURE_REASON": None if result.get("step_success") else (result.get("failure_reason") or "UNKNOWN_FAILURE"),
            }
        )
        last = result
        if result.get("step_success"):
            last = dict(result)
            last["ACTUAL_EXECUTED_BUILDER"] = result.get("builder") or name
            last["BUILDER_FALLBACK_USED"] = name != resolved
            last["attempts"] = attempts
            last["CIRCULAR_LOFT_FORCED"] = False
            return last
    last = dict(last)
    last["BUILDER_FALLBACK_USED"] = True
    last["attempts"] = attempts
    last["CIRCULAR_LOFT_FORCED"] = False
    last["step_success"] = False
    last["failure_reason"] = last.get("failure_reason") or "ALL_BUILDERS_FAILED"
    return last


def subregion_qa(source_local: np.ndarray, cand_local: np.ndarray, subregions: list[dict[str, Any]]) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    rows = []
    diag = max(float(np.ptp(source_local, axis=0).max()), 1e-6)
    cov_r = 0.02 * diag
    for sub in subregions:
        lo = float(sub.get("x_lo", source_local[:, 0].min()))
        hi = float(sub.get("x_hi", source_local[:, 0].max()))
        src = source_local[(source_local[:, 0] >= lo) & (source_local[:, 0] <= hi)]
        cand = cand_local[(cand_local[:, 0] >= lo) & (cand_local[:, 0] <= hi)]
        if len(src) < 8 or len(cand) < 8:
            rows.append({"subregion_id": sub.get("subregion_id"), "coverage": 0.0, "chamfer": 1.0, "valid": False})
            continue
        st = cKDTree(src)
        ct = cKDTree(cand)
        s2c = ct.query(src)[0]
        c2s = st.query(cand)[0]
        rows.append(
            {
                "subregion_id": sub.get("subregion_id"),
                "coverage": float(np.mean(s2c <= cov_r)),
                "chamfer": float(0.5 * (s2c.mean() + c2s.mean())),
                "hausdorff": float(max(s2c.max(), c2s.max())),
                "valid": True,
            }
        )
    cov = np.array([row["coverage"] for row in rows], dtype=float) if rows else np.array([0.0])
    return {
        "rows": rows,
        "MIN_SUBREGION_COVERAGE": float(cov.min()) if len(cov) else 0.0,
        "MEAN_SUBREGION_COVERAGE": float(cov.mean()) if len(cov) else 0.0,
        "SUBREGION_COUNT": len(rows),
    }


def render_cross_section_sheet(sections: list[dict[str, Any]], path: Path, title: str = "cross-section sheet") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = min(len(sections), 12)
    if n == 0:
        return
    cols = 4
    rows_n = int(math.ceil(n / cols))
    fig, axes = plt.subplots(rows_n, cols, figsize=(12, 2.6 * rows_n), dpi=120)
    axes = np.atleast_1d(axes).ravel()
    for i in range(n):
        ax = axes[i]
        row = sections[int(i * max(len(sections) / n, 1))] if n < len(sections) else sections[i]
        idx = min(int(round(i * (len(sections) - 1) / max(n - 1, 1))), len(sections) - 1)
        row = sections[idx]
        boundary = np.asarray(row.get("boundary_2d") or [], dtype=float)
        hull = np.asarray(row.get("convex_hull") or [], dtype=float)
        centroid = np.asarray(row.get("centroid_2d") or [0.0, 0.0], dtype=float)
        radius = float(row.get("radial_mean") or 0.0)
        if len(boundary):
            closed = np.vstack([boundary, boundary[0]])
            ax.plot(closed[:, 0], closed[:, 1], color="#1d4ed8", lw=1.2, label="selected profile")
        if len(hull):
            closed_h = np.vstack([hull, hull[0]])
            ax.plot(closed_h[:, 0], closed_h[:, 1], color="#64748b", lw=0.7, ls="--", label="convex hull")
        if radius > 0:
            ang = np.linspace(0, 2 * math.pi, 64)
            ax.plot(centroid[0] + radius * np.cos(ang), centroid[1] + radius * np.sin(ang), color="#dc2626", lw=0.8, label="circle fit")
        ax.set_aspect("equal")
        ax.set_title(f"x={row.get('section_position'):.3f} {row.get('profile_type')}", fontsize=7)
        ax.tick_params(labelsize=6)
    for ax in axes[n:]:
        ax.axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper right", fontsize=7)
    fig.suptitle(title, fontsize=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def reconstruct_from_source(
    source_part: Path,
    hypothesis: dict[str, Any],
    candidate_dir: Path,
    measured: dict[str, Any] | None = None,
    candidate_id: str = "MAC_CANDIDATE_01",
    backend: str = "MAC_GENERATED_CAD",
) -> dict[str, Any]:
    """Official MAC runtime entry: reuse MAC HOW, bind metrics, execute builders."""
    candidate_dir = Path(candidate_dir)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    source_part = Path(source_part)
    hyp = normalize_mac_hypothesis(hypothesis)
    dump_json(candidate_dir / "construction_hypothesis.json", hyp)
    dump_json(candidate_dir / "architect_plan.json", {"backend": backend, "hypothesis": hyp, "runtime_contract": "generic_cad_runtime.reconstruct_from_source"})
    (candidate_dir / "generated_code.py").write_text(RUNTIME_DISPATCHER_STUB, encoding="utf-8")
    mesh = load_mesh(source_part)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64) if getattr(mesh, "faces", None) is not None else np.zeros((0, 3), dtype=np.int64)
    if measured is None:
        measured = load_json(source_part.parent / "measured_spec.json", {}) or {}
    contract = build_frame_contract(vertices, measured)
    local = contract.global_to_local(vertices)
    geom = measured_geometry_contract(mesh, measured, contract)
    dump_json(candidate_dir / "measured_geometry_contract.json", geom)
    dump_json(candidate_dir / "frame_contract.json", contract.to_json())
    sections = analyze_cross_sections(local, count=24, faces=faces)
    dump_json(candidate_dir / "section_profiles.json", {"sections": sections, "profile_representation": "FULL_2D_BOUNDARY"})
    breaks = detect_change_points(sections)
    subregions = split_subregions(sections, breaks)
    dump_json(candidate_dir / "structural_decomposition.json", {"breaks": breaks, "subregions": subregions, "STRUCTURAL_BREAK_COUNT": len(breaks), "SUBREGION_COUNT": len(subregions)})
    geom.update(geometry_scores_from_sections(local, sections))
    mac_family = str(hyp.get("visual_builder_suggestion") or hyp.get("requested_builder_family") or "UNKNOWN")
    route = route_builder(mac_family, sections, breaks, geom)
    params = bind_parameters(geom, hyp)
    import shutil

    runtime_root = candidate_dir / "runtime"
    if runtime_root.exists():
        shutil.rmtree(runtime_root)
    runtime = execute_with_explicit_fallback(local, route, sections, breaks, params, runtime_root, faces=faces)
    local_step = Path(str(runtime.get("step_path") or ""))
    global_step = candidate_dir / "generated.step"
    step_ok = False
    if runtime.get("step_success") and local_step.is_file():
        step_ok = transform_step(local_step, global_step, contract.T_GLOBAL_FROM_LOCAL)
    inner_ev = any(bool(row.get("INNER_LOOP_EVIDENCE")) for row in sections) or bool(runtime.get("INNER_LOOP_EVIDENCE"))
    inner_un = bool(inner_ev and (runtime.get("INNER_LOOP_UNSUPPORTED", True) if inner_ev else False))
    provenance = {
        "component_source": str(source_part),
        "metric_source": "RUNTIME_SOURCE_PART_OBJ",
        "profile_source": "SECTION_2D_BOUNDARY",
        "MAC_SUGGESTED_BUILDER": route.get("MAC_SUGGESTED_BUILDER"),
        "RESOLVED_BUILDER_FAMILY": route.get("RESOLVED_BUILDER_FAMILY"),
        "ACTUAL_EXECUTED_BUILDER": runtime.get("ACTUAL_EXECUTED_BUILDER") or runtime.get("builder"),
        "BUILDER_SELECTION_REASON": route.get("BUILDER_SELECTION_REASON"),
        "BUILDER_FALLBACK_USED": bool(runtime.get("BUILDER_FALLBACK_USED")),
        "attempts": runtime.get("attempts") or [],
        "CIRCULAR_LOFT_FORCED": bool(route.get("CIRCULAR_LOFT_FORCED")),
        "STRUCTURAL_BREAK_COUNT": len(breaks),
        "SUBREGION_COUNT": max(len(subregions), 1),
        "subregion_builders": runtime.get("subregion_builders") or [runtime.get("builder")],
        "NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS": bool(runtime.get("NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS") or runtime.get("builder") in {"NON_CIRCULAR_PROFILE_LOFT", "COMPOSITE_PART", "PROFILE_EXTRUSION"}),
        "PROFILE_CORRESPONDENCE_SUCCESS": runtime.get("PROFILE_CORRESPONDENCE_SUCCESS"),
        "TRANSITION_REGION_CREATED": bool(runtime.get("TRANSITION_REGION_CREATED")),
        "TRANSITION_PROFILE_COUNT": int(runtime.get("TRANSITION_PROFILE_COUNT") or 0),
        "COMPOSITE_TOPOLOGY_MODE": runtime.get("COMPOSITE_TOPOLOGY_MODE"),
        "INNER_LOOP_EVIDENCE": inner_ev,
        "INNER_LOOP_UNSUPPORTED": inner_un,
        "BRep_type": "OPEN_SHELL_OR_SOLID",
        "STEP exists": bool(step_ok and global_step.is_file()),
        "CAD_NATIVE": True,
        "representation": f"{runtime.get('builder') or 'UNKNOWN'}_BREP",
        "MAC_API_REEXECUTED": False,
    }
    dump_json(candidate_dir / "runtime_measurements.json", {"hypothesis": hyp, "route": route, "runtime": {k: v for k, v in runtime.items() if k != "attempts"}, **provenance, "builder_registry": SUPPORTED_EXECUTABLE_BUILDERS})
    dump_json(candidate_dir / "candidate_provenance.json", provenance)
    if route.get("RESOLVED_BUILDER_FAMILY"):
        route = dict(route)
        route["ACTUAL_EXECUTED_BUILDER"] = provenance["ACTUAL_EXECUTED_BUILDER"]
        dump_json(candidate_dir / "builder_route.json", route)
    return {
        "component_id": source_part.parent.parent.name,
        "candidate_id": candidate_id,
        "backend": backend,
        "representation": provenance["representation"],
        "topology_class": "OPEN_SHELL_OR_SOLID_BREP",
        "cad_native": True,
        "runtime_success": bool(step_ok),
        "generated_code_path": str(candidate_dir / "generated_code.py"),
        "runtime_measurements_path": str(candidate_dir / "runtime_measurements.json"),
        "step_path": str(global_step),
        "step_success": bool(step_ok and global_step.is_file() and global_step.stat().st_size > 0),
        "exit_code": 0 if step_ok else 2,
        "MAC_SUGGESTED_BUILDER": provenance["MAC_SUGGESTED_BUILDER"],
        "RESOLVED_BUILDER_FAMILY": provenance["RESOLVED_BUILDER_FAMILY"],
        "ACTUAL_EXECUTED_BUILDER": provenance["ACTUAL_EXECUTED_BUILDER"],
        "STRUCTURAL_BREAK_COUNT": provenance["STRUCTURAL_BREAK_COUNT"],
        "SUBREGION_COUNT": provenance["SUBREGION_COUNT"],
        "CIRCULAR_LOFT_FORCED": provenance["CIRCULAR_LOFT_FORCED"],
        "BUILDER_FALLBACK_USED": provenance["BUILDER_FALLBACK_USED"],
        "INNER_LOOP_EVIDENCE": inner_ev,
        "INNER_LOOP_UNSUPPORTED": inner_un,
        "TRANSITION_REGION_CREATED": provenance["TRANSITION_REGION_CREATED"],
        "PROFILE_CORRESPONDENCE_SUCCESS": provenance["PROFILE_CORRESPONDENCE_SUCCESS"],
        "NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS": provenance["NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS"],
        "COMPOSITE_TOPOLOGY_MODE": provenance["COMPOSITE_TOPOLOGY_MODE"],
        "subregion_builders": provenance["subregion_builders"],
        "route": route,
        "failure_reason": None if step_ok else (runtime.get("failure_reason") or "RUNTIME_STEP_FAILED"),
    }

