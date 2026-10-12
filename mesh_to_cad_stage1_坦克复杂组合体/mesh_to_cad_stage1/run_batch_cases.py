from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import trimesh
from scipy.optimize import linear_sum_assignment

from run_mvp import (
    classify_and_fit,
    render_preview,
    simplify_by_component,
    symmetric_metrics,
    write_scad,
    rotation_from_z,
    subdivide_mesh,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs_batch_cases"
OUT.mkdir(parents=True, exist_ok=True)


@dataclass
class PartSpec:
    name: str
    expected_type: str
    mesh: trimesh.Trimesh


def transform_matrix(translation=(0.0, 0.0, 0.0), rotation_axis=None, angle_deg=0.0) -> np.ndarray:
    m = np.eye(4)
    if rotation_axis is not None and abs(angle_deg) > 1e-12:
        r = trimesh.transformations.rotation_matrix(math.radians(angle_deg), rotation_axis)
        m[:3, :3] = r[:3, :3]
    m[:3, 3] = np.asarray(translation, dtype=float)
    return m


def box_part(name: str, extents, center, rotation_axis=None, angle_deg=0.0, subdivisions=4) -> PartSpec:
    mesh = trimesh.creation.box(extents=extents)
    if subdivisions:
        mesh = subdivide_mesh(mesh, subdivisions)
    mesh.apply_transform(transform_matrix(center, rotation_axis, angle_deg))
    return PartSpec(name, "box", mesh)


def cylinder_part(name: str, radius: float, height: float, center, axis=(0.0, 0.0, 1.0), sections=192) -> PartSpec:
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    t = np.eye(4)
    t[:3, :3] = rotation_from_z(axis)
    t[:3, 3] = np.asarray(center, dtype=float)
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections, transform=t)
    return PartSpec(name, "cylinder", mesh)


def sphere_part(name: str, radius: float, center, subdivisions=5) -> PartSpec:
    mesh = trimesh.creation.icosphere(subdivisions=subdivisions, radius=radius)
    mesh.apply_translation(center)
    return PartSpec(name, "sphere", mesh)


def cone_part(name: str, radius: float, height: float, center, axis=(0.0, 0.0, 1.0), sections=192) -> PartSpec:
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    t = np.eye(4)
    t[:3, :3] = rotation_from_z(axis)
    t[:3, 3] = np.asarray(center, dtype=float)
    mesh = trimesh.creation.cone(radius=radius, height=height, sections=sections, transform=t)
    return PartSpec(name, "cone", mesh)


def case_rotated_shelf() -> list[PartSpec]:
    return [
        box_part("left_side", [0.25, 1.4, 3.6], [-1.55, 0.0, 1.8], subdivisions=5),
        box_part("right_side", [0.25, 1.4, 3.6], [1.55, 0.0, 1.8], subdivisions=5),
        box_part("bottom", [3.2, 1.4, 0.22], [0.0, 0.0, 0.15], subdivisions=5),
        box_part("middle", [2.9, 1.25, 0.18], [0.0, 0.0, 1.75], rotation_axis=[0, 1, 0], angle_deg=7, subdivisions=5),
        box_part("top", [3.2, 1.4, 0.22], [0.0, 0.0, 3.45], subdivisions=5),
    ]


def case_tilted_stool() -> list[PartSpec]:
    parts = [box_part("seat", [2.4, 2.0, 0.28], [0.0, 0.0, 2.65], subdivisions=5)]
    axes = [(-0.18, -0.12, 1.0), (0.18, -0.12, 1.0), (0.0, 0.20, 1.0)]
    centers = [(-0.75, -0.55, 1.3), (0.75, -0.55, 1.3), (0.0, 0.7, 1.3)]
    for i, (a, c) in enumerate(zip(axes, centers), 1):
        parts.append(cylinder_part(f"leg_{i}", 0.16, 2.65, c, axis=a, sections=224))
    return parts


def case_pipe_rack() -> list[PartSpec]:
    return [
        box_part("base", [4.2, 2.2, 0.3], [0.0, 0.0, 0.15], subdivisions=5),
        box_part("back", [4.2, 0.25, 2.2], [0.0, 0.95, 1.25], subdivisions=5),
        cylinder_part("pipe_x", 0.18, 3.5, [0.0, -0.55, 0.9], axis=[1, 0, 0], sections=224),
        cylinder_part("pipe_y", 0.16, 1.5, [-1.4, 0.0, 1.55], axis=[0, 1, 0], sections=224),
        cylinder_part("pipe_diag", 0.14, 2.8, [1.05, -0.1, 1.35], axis=[0.55, 0.25, 0.80], sections=224),
    ]


def case_wheeled_cart() -> list[PartSpec]:
    parts = [
        box_part("body", [3.8, 2.0, 0.55], [0.0, 0.0, 1.35], subdivisions=5),
        box_part("handle", [0.25, 1.8, 1.8], [-2.0, 0.0, 2.0], rotation_axis=[0, 1, 0], angle_deg=-12, subdivisions=5),
    ]
    # Short, wide cylinders: intentionally difficult for the current elongated-cylinder PCA rule.
    for i, (x, y) in enumerate([(-1.25, -1.05), (-1.25, 1.05), (1.25, -1.05), (1.25, 1.05)], 1):
        parts.append(cylinder_part(f"wheel_{i}", 0.48, 0.30, [x, y, 0.65], axis=[0, 1, 0], sections=256))
    return parts


def case_dumbbell() -> list[PartSpec]:
    return [
        cylinder_part("bar", 0.12, 3.4, [0.0, 0.0, 0.0], axis=[1, 0, 0], sections=224),
        cylinder_part("left_plate", 0.72, 0.34, [-1.85, 0.0, 0.0], axis=[1, 0, 0], sections=256),
        cylinder_part("right_plate", 0.72, 0.34, [1.85, 0.0, 0.0], axis=[1, 0, 0], sections=256),
    ]



def case_controlled_tank() -> list[PartSpec]:
    """A more complex multi-part tank stress test.

    The shape is still controlled/synthetic and built from boxes/cylinders so that
    the expected primitive type of every part is known. Short, wide cylinders
    (road wheels, hatch, muzzle brake) intentionally expose the current PCA
    recognizer's limitation.
    """
    parts = [
        box_part("lower_hull", [6.0, 3.4, 1.0], [0.0, 0.0, 1.25], subdivisions=5),
        box_part("upper_hull", [4.8, 3.0, 0.8], [-0.15, 0.0, 2.05], rotation_axis=[0, 1, 0], angle_deg=-4, subdivisions=5),
        box_part("turret_base", [2.5, 2.2, 0.72], [0.35, 0.0, 2.85], rotation_axis=[0, 0, 1], angle_deg=8, subdivisions=5),
        box_part("turret_top", [1.9, 1.65, 0.48], [0.50, 0.0, 3.42], rotation_axis=[0, 0, 1], angle_deg=8, subdivisions=5),
        box_part("left_track", [5.8, 0.50, 0.78], [0.0, -1.95, 0.70], subdivisions=4),
        box_part("right_track", [5.8, 0.50, 0.78], [0.0, 1.95, 0.70], subdivisions=4),
        cylinder_part("main_gun", 0.22, 4.8, [3.10, 0.0, 3.45], axis=[1, 0, 0], sections=256),
        cylinder_part("muzzle_brake", 0.38, 0.58, [5.78, 0.0, 3.45], axis=[1, 0, 0], sections=256),
        cylinder_part("commander_hatch", 0.45, 0.20, [0.25, 0.0, 3.82], axis=[0, 0, 1], sections=256),
        cylinder_part("antenna", 0.055, 2.0, [-0.55, 0.65, 4.45], axis=[0, 0, 1], sections=192),
    ]

    wheel_x = [-2.15, -1.30, -0.45, 0.40, 1.25, 2.10]
    for side_name, y in [("left", -1.95), ("right", 1.95)]:
        for i, x in enumerate(wheel_x, 1):
            parts.append(
                cylinder_part(
                    f"{side_name}_road_wheel_{i}",
                    0.48,
                    0.36,
                    [x, y, 0.72],
                    axis=[0, 1, 0],
                    sections=256,
                )
            )
    return parts

def case_unsupported_mixed() -> list[PartSpec]:
    return [
        box_part("base", [2.7, 2.0, 0.30], [0.0, 0.0, 0.15], subdivisions=5),
        cylinder_part("stem", 0.16, 2.2, [0.0, 0.0, 1.55], axis=[0, 0, 1], sections=224),
        sphere_part("globe", 0.72, [0.0, 0.0, 3.25], subdivisions=5),
        cone_part("shade", 0.85, 1.10, [2.0, 0.0, 2.7], axis=[0, 0, 1], sections=224),
    ]


CASES: dict[str, Callable[[], list[PartSpec]]] = {
    "rotated_shelf": case_rotated_shelf,
    "tilted_stool": case_tilted_stool,
    "pipe_rack": case_pipe_rack,
    "wheeled_cart": case_wheeled_cart,
    "dumbbell": case_dumbbell,
    "unsupported_mixed": case_unsupported_mixed,
    "controlled_tank": case_controlled_tank,
}


def match_components(components: list[trimesh.Trimesh], specs: list[PartSpec]) -> list[tuple[int, int]]:
    comp_centers = np.array([c.centroid for c in components])
    spec_centers = np.array([s.mesh.centroid for s in specs])
    costs = np.linalg.norm(comp_centers[:, None, :] - spec_centers[None, :, :], axis=2)
    rows, cols = linear_sum_assignment(costs)
    return list(zip(rows.tolist(), cols.tolist()))


def run_case(case_id: str, specs: list[PartSpec]) -> dict[str, Any]:
    case_dir = OUT / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    high = trimesh.util.concatenate([s.mesh for s in specs])
    high.export(case_dir / "01_input_highpoly.ply")
    high.export(case_dir / "01_input_highpoly.obj")

    low = simplify_by_component(high, target_cells_across_diag=65)
    low.export(case_dir / "02_lowpoly.ply")
    low.export(case_dir / "02_lowpoly.obj")

    components = list(low.split(only_watertight=False))
    matching = match_components(components, specs)

    primitive_records: list[dict[str, Any]] = []
    fitted_meshes: list[trimesh.Trimesh] = []
    part_results: list[dict[str, Any]] = []

    for component_idx, spec_idx in matching:
        comp = components[component_idx]
        spec = specs[spec_idx]
        params, fitted = classify_and_fit(comp)
        params["component_id"] = len(primitive_records)
        params["source_part_name"] = spec.name
        params["expected_type"] = spec.expected_type
        primitive_records.append(params)
        fitted_meshes.append(fitted)
        comp.export(case_dir / f"part_{len(part_results):02d}_{spec.name}.ply")

        pm = symmetric_metrics(spec.mesh, fitted, samples=8000)
        part_results.append({
            "part_name": spec.name,
            "expected_type": spec.expected_type,
            "detected_type": params["type"],
            "type_correct": params["type"] == spec.expected_type,
            "input_faces": int(len(spec.mesh.faces)),
            "lowpoly_faces": int(len(comp.faces)),
            **pm,
        })

    reconstructed = trimesh.util.concatenate(fitted_meshes)
    reconstructed.export(case_dir / "03_parametric_reconstruction.ply")
    reconstructed.export(case_dir / "03_parametric_reconstruction.obj")
    write_scad(primitive_records, case_dir / "03_parametric_reconstruction.scad")

    overall = symmetric_metrics(high, reconstructed, samples=30000)
    supported_expected = sum(1 for s in specs if s.expected_type in {"box", "cylinder"})
    correct = sum(int(r["type_correct"]) for r in part_results)
    supported_correct = sum(
        int(r["type_correct"])
        for r in part_results
        if r["expected_type"] in {"box", "cylinder"}
    )

    result = {
        "case_id": case_id,
        "input": {
            "vertices": int(len(high.vertices)),
            "faces": int(len(high.faces)),
            "parts": len(specs),
            "bbox_extents": [float(x) for x in high.extents],
            "watertight": bool(high.is_watertight),
        },
        "lowpoly": {
            "vertices": int(len(low.vertices)),
            "faces": int(len(low.faces)),
            "parts": len(components),
            "face_reduction": float(1.0 - len(low.faces) / len(high.faces)),
        },
        "recognition": {
            "correct_types_all": correct,
            "total_parts": len(specs),
            "type_accuracy_all": correct / len(specs),
            "supported_expected_parts": supported_expected,
            "supported_correct": supported_correct,
            "supported_type_accuracy": supported_correct / max(supported_expected, 1),
            "detected_types": [p["type"] for p in primitive_records],
        },
        "reconstruction": {
            "vertices": int(len(reconstructed.vertices)),
            "faces": int(len(reconstructed.faces)),
            **overall,
        },
        "parts": part_results,
        "scope_note": "Current recognizer supports only box and elongated cylinder. Squat cylinders, spheres and cones are intentional stress/failure cases.",
    }

    (case_dir / "primitives.json").write_text(json.dumps(primitive_records, indent=2), encoding="utf-8")
    (case_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    render_preview(high, case_dir / "preview_input.png", f"{case_id}: input high-poly")
    render_preview(low, case_dir / "preview_lowpoly.png", f"{case_id}: low-poly")
    render_preview(reconstructed, case_dir / "preview_reconstructed.png", f"{case_id}: recovered primitives")
    return result


def main() -> None:
    summaries = []
    for case_id, builder in CASES.items():
        print(f"Running {case_id} ...", flush=True)
        result = run_case(case_id, builder())
        summaries.append(result)
        print(
            f"  types={result['recognition']['correct_types_all']}/{result['recognition']['total_parts']} "
            f"chamfer_n={result['reconstruction']['chamfer_normalized_by_bbox_diag']:.6f} "
            f"hausdorff_n={result['reconstruction']['hausdorff_normalized_by_bbox_diag']:.6f}",
            flush=True,
        )

    summary_json = OUT / "batch_summary.json"
    summary_json.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    fields = [
        "case_id", "input_faces", "lowpoly_faces", "face_reduction", "parts",
        "type_correct", "type_accuracy", "supported_type_accuracy",
        "reconstructed_faces", "chamfer_normalized", "hausdorff_normalized",
    ]
    with (OUT / "batch_summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in summaries:
            writer.writerow({
                "case_id": r["case_id"],
                "input_faces": r["input"]["faces"],
                "lowpoly_faces": r["lowpoly"]["faces"],
                "face_reduction": r["lowpoly"]["face_reduction"],
                "parts": r["recognition"]["total_parts"],
                "type_correct": r["recognition"]["correct_types_all"],
                "type_accuracy": r["recognition"]["type_accuracy_all"],
                "supported_type_accuracy": r["recognition"]["supported_type_accuracy"],
                "reconstructed_faces": r["reconstruction"]["faces"],
                "chamfer_normalized": r["reconstruction"]["chamfer_normalized_by_bbox_diag"],
                "hausdorff_normalized": r["reconstruction"]["hausdorff_normalized_by_bbox_diag"],
            })
    print(f"Wrote {summary_json}")


if __name__ == "__main__":
    main()
