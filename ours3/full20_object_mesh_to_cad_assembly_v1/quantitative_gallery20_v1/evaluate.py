#!/usr/bin/env python3
"""Evaluate the 20-object qualitative gallery with the frozen object protocol.

The script is intentionally read-only with respect to the source experiments.  It
rebuilds CADFit's displayed native-STL assembly in a separate evaluation folder.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
EXP = OURS3 / "full20_object_mesh_to_cad_assembly_v1"
OUT = EXP / "quantitative_gallery20_v1"
SAMPLE_N = 20_000
SEED = 0
IOU_RESOLUTION = 64

CASES = [
    ("Jenga Classic", "2_of_jenga_classic_game", "2_of_jenga_classic_game_p3_xpart_cadfit_routea_v1"),
    ("Dollhouse Sofa", "3d_dollhouse_sofa", "3d_dollhouse_sofa_p3_xpart_cadfit_routea_v1"),
    ("Android Figure", "android_figure_orange", "android_figure_orange_p3_xpart_cadfit_routea_v1"),
    ("Milk Frother", "aroma_stainless_steel_milk_frother_2_cup", "aroma_stainless_steel_milk_frother_2_cup_p3_xpart_cadfit_routea_v1"),
    ("Vegetable Set", "assorted_vegetable_set", "assorted_vegetable_set_p3_xpart_cadfit_routea_v1"),
    ("Baby Car", "baby_car", "baby_car_p3_xpart_cadfit_routea_v1"),
    ("Birdhouse", "birdhouse", "birdhouse_p3_xpart_cadfit_routea_v1"),
    ("Cube", "cube", "cube_p3_xpart_cadfit_routea_v1"),
    ("DVD Player", "dvd_player", "dvd_player_p3_xpart_cadfit_routea_v1"),
    ("Fire Truck", "fire_truck", "fire_truck_p3_xpart_cadfit_routea_v1"),
    ("Mini Excavator", "mini_excavator", "mini_excavator_p3_xpart_cadfit_routea_v1"),
    ("Mini Fire Engine", "mini_fire_engine", "mini_fire_engine_p3_xpart_cadfit_routea_v1"),
    ("Paintmaker", "paintmaker", "paintmaker_p3_xpart_cadfit_routea_v1"),
    ("Pottery Large", "pottery_large", "pottery_large_p3_xpart_cadfit_routea_v1"),
    ("Pressure Cooker", "pressure_cooker", "pressure_cooker_p3_xpart_cadfit_routea_v1"),
    ("Robot", "robot", "robot_p3_xpart_cadfit_routea_v1"),
    ("Speaker Big", "speaker_big", "speaker_big_p3_xpart_cadfit_routea_v1"),
    ("Tank", "tank", "tank_frozen_p3_to_cadfit_v1"),
    ("Toaster", "toaster", "toaster_p3_xpart_cadfit_routea_v1"),
    ("Winerack", "winerack", "winerack_p3_xpart_cadfit_routea_v1"),
]


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
        raise ValueError(f"empty mesh: {path}")
    return mesh


def step_mesh(path: Path) -> trimesh.Trimesh:
    import cadquery as cq

    shape = cq.importers.importStep(str(path)).val()
    if not shape.isValid():
        raise ValueError(f"invalid STEP: {path}")
    vertices, faces = shape.tessellate(0.0005, 0.1)
    return trimesh.Trimesh(
        np.asarray([[v.x, v.y, v.z] for v in vertices], dtype=float),
        np.asarray(faces, dtype=np.int64),
        process=False,
    )


def sample_surface(mesh: trimesh.Trimesh, n: int = SAMPLE_N, seed: int = SEED) -> np.ndarray:
    sys.path.insert(0, str(ROOT / "scripts"))
    from geometry_pack_v1.surface import sample_surface_uniform

    return sample_surface_uniform(mesh.vertices, mesh.faces, n, seed)[0]


def surface_iou(a: trimesh.Trimesh, b: trimesh.Trimesh, resolution: int = IOU_RESOLUTION):
    bounds = np.vstack([a.bounds, b.bounds])
    pitch = float(np.ptp(bounds, axis=0).max() / resolution)
    if not math.isfinite(pitch) or pitch <= 0:
        raise ValueError("invalid common voxel pitch")

    def occupied(mesh):
        indices = np.rint(mesh.voxelized(pitch).points / pitch).astype("int64")
        return set(map(tuple, indices.tolist()))

    sa, sb = occupied(a), occupied(b)
    union = len(sa | sb)
    if not union:
        raise ValueError("empty voxel union")
    return len(sa & sb) / union, pitch, len(sa), len(sb)


def metrics(reference: trimesh.Trimesh, prediction: trimesh.Trimesh) -> dict:
    pa = sample_surface(reference)
    pb = sample_surface(prediction)
    da = cKDTree(pb).query(pa, workers=1)[0]
    db = cKDTree(pa).query(pb, workers=1)[0]
    diag = float(np.linalg.norm(reference.extents))
    iou, pitch, n_ref, n_pred = surface_iou(reference, prediction)
    return {
        "CD": float((da.mean() + db.mean()) * 0.5 / diag),
        "H95": float(np.percentile(np.r_[da, db], 95) / diag),
        "IOU64": float(iou),
        "BBOX_ERROR": float(np.max(np.abs(reference.bounds - prediction.bounds)) / diag),
        "CENTROID_ERROR": float(np.linalg.norm(reference.centroid - prediction.centroid) / diag),
        "IOU_PITCH": pitch,
        "REFERENCE_SURFACE_VOXELS": n_ref,
        "PREDICTION_SURFACE_VOXELS": n_pred,
    }


def object_manifest() -> dict[str, dict]:
    with (EXP / "manifests/FULL20_OBJECT_MANIFEST.csv").open(newline="") as handle:
        return {row["OBJECT_ID"]: row for row in csv.DictReader(handle)}


def select_ours_gate(object_id: str) -> tuple[Path, Path, dict]:
    candidates = []
    base = EXP / "model_v1/generated" / object_id
    for gate_path in base.rglob("OBJECT_GATE.json"):
        try:
            gate = json.loads(gate_path.read_text())
        except Exception:
            continue
        step = Path(gate.get("step") or "")
        if gate.get("FULL_MODEL_ASSEMBLY_PASS") is True and step.is_file():
            candidates.append((gate_path.stat().st_mtime, gate_path, step, gate))
    if not candidates:
        raise FileNotFoundError(f"no complete model-generated assembly for {object_id}")
    _, gate_path, step, gate = max(candidates, key=lambda item: item[0])
    return gate_path, step, gate


def cadfit_native_assembly(route_dir: Path, object_id: str) -> tuple[trimesh.Trimesh, list[dict]]:
    parts = []
    for native_path in sorted((route_dir / "cadfit_routea/cadfit_raw").glob("PART_*/best_greedy_parallel_iterative.stl")):
        part_id = native_path.parent.name
        try:
            idx = int(part_id.split("_")[-1])
        except ValueError:
            continue
        source_path = route_dir / "xpart" / part_id / f"complete_part_{idx:03d}.obj"
        if not source_path.is_file():
            continue
        source = load_mesh(source_path)
        native = load_mesh(native_path)
        src_extent = float(np.max(source.extents))
        native_extent = float(np.max(native.extents))
        if native_extent <= 1e-12:
            continue
        scale = src_extent / native_extent
        translation = np.asarray(source.centroid) - scale * np.asarray(native.centroid)
        transform = np.eye(4)
        transform[:3, :3] *= scale
        transform[:3, 3] = translation
        placed = native.copy()
        placed.apply_transform(transform)
        parts.append(
            {
                "part_id": part_id,
                "source_path": str(source_path),
                "source_sha256": sha256(source_path),
                "native_stl_path": str(native_path),
                "native_stl_sha256": sha256(native_path),
                "scale": scale,
                "translation": translation.tolist(),
                "mesh": placed,
            }
        )
    if not parts:
        raise FileNotFoundError(f"no evaluable CADFit native parts for {object_id}")
    return trimesh.util.concatenate([part.pop("mesh") for part in parts]), parts


def mean(rows: list[dict], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) not in (None, "")]
    return float(np.mean(values)) if values else None


def median(rows: list[dict], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) not in (None, "")]
    return float(np.median(values)) if values else None


def main() -> int:
    start = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = object_manifest()
    rows = []
    provenance = []

    for index, (display_name, object_id, route_name) in enumerate(CASES, 1):
        total_parts = int(manifest[object_id]["PART_N"])
        reference_path = Path(manifest[object_id]["FULL_MESH_PATH"])
        reference = load_mesh(reference_path)
        print(f"[{index:02d}/20] {display_name}", flush=True)

        # The supplied figure explicitly marks Tank input/Ours as unavailable.
        if object_id != "tank":
            try:
                gate_path, step_path, gate = select_ours_gate(object_id)
                pred = step_mesh(step_path)
                rec = {
                    "case_index": index,
                    "display_name": display_name,
                    "object_id": object_id,
                    "method": "Ours",
                    "status": "COMPLETE",
                    "assembled_parts": total_parts,
                    "total_parts": total_parts,
                    "coverage": 1.0,
                    **metrics(reference, pred),
                    "reference_path": str(reference_path),
                    "prediction_path": str(step_path),
                    "gate_path": str(gate_path),
                    "failure_reason": "",
                }
                rows.append(rec)
                provenance.append(
                    {
                        "object_id": object_id,
                        "method": "Ours",
                        "reference_sha256": sha256(reference_path),
                        "prediction_sha256": sha256(step_path),
                        "gate_sha256": sha256(gate_path),
                        "gate_metrics": gate.get("metrics"),
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "case_index": index,
                        "display_name": display_name,
                        "object_id": object_id,
                        "method": "Ours",
                        "status": "UNAVAILABLE",
                        "assembled_parts": 0,
                        "total_parts": total_parts,
                        "coverage": 0.0,
                        "failure_reason": f"{type(exc).__name__}: {exc}",
                    }
                )

        route_dir = OURS3 / route_name
        try:
            cadfit, part_provenance = cadfit_native_assembly(route_dir, object_id)
            assembled_parts = len(part_provenance)
            out_mesh = OUT / "cadfit_native_assemblies" / f"{object_id}.stl"
            out_mesh.parent.mkdir(parents=True, exist_ok=True)
            cadfit.export(out_mesh)
            rec = {
                "case_index": index,
                "display_name": display_name,
                "object_id": object_id,
                "method": "CADFit",
                "status": "COMPLETE" if assembled_parts == total_parts else "PARTIAL",
                "assembled_parts": assembled_parts,
                "total_parts": total_parts,
                "coverage": assembled_parts / total_parts,
                **metrics(reference, cadfit),
                "reference_path": str(reference_path),
                "prediction_path": str(out_mesh),
                "route_dir": str(route_dir),
                "failure_reason": "",
            }
            rows.append(rec)
            provenance.append(
                {
                    "object_id": object_id,
                    "method": "CADFit",
                    "reference_sha256": sha256(reference_path),
                    "rebuilt_assembly_sha256": sha256(out_mesh),
                    "parts": part_provenance,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "case_index": index,
                    "display_name": display_name,
                    "object_id": object_id,
                    "method": "CADFit",
                    "status": "UNAVAILABLE",
                    "assembled_parts": 0,
                    "total_parts": total_parts,
                    "coverage": 0.0,
                    "failure_reason": f"{type(exc).__name__}: {exc}",
                }
            )

        with (OUT / "PER_CASE.csv").open("w", newline="") as handle:
            keys = list(dict.fromkeys(key for row in rows for key in row))
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        dump(OUT / "PROVENANCE.json", provenance)

    ours_complete = [row for row in rows if row["method"] == "Ours" and row["status"] == "COMPLETE"]
    cadfit_complete = [row for row in rows if row["method"] == "CADFit" and row["status"] == "COMPLETE"]
    complete_ids = {row["object_id"] for row in cadfit_complete} & {row["object_id"] for row in ours_complete}
    paired = [row for row in rows if row["object_id"] in complete_ids]
    paired_ours = [row for row in paired if row["method"] == "Ours"]
    paired_cadfit = [row for row in paired if row["method"] == "CADFit"]
    by_key = {(row["object_id"], row["method"]): row for row in paired}

    wins = {}
    for key, lower_better in [("CD", True), ("H95", True), ("IOU64", False)]:
        ours_wins = cadfit_wins = ties = 0
        for object_id in sorted(complete_ids):
            a = float(by_key[(object_id, "Ours")][key])
            b = float(by_key[(object_id, "CADFit")][key])
            if math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12):
                ties += 1
            elif (a < b) == lower_better:
                ours_wins += 1
            else:
                cadfit_wins += 1
        wins[key] = {"ours": ours_wins, "cadfit": cadfit_wins, "ties": ties}

    def stats(group):
        return {
            "N": len(group),
            "CD_mean": mean(group, "CD"),
            "CD_median": median(group, "CD"),
            "H95_mean": mean(group, "H95"),
            "H95_median": median(group, "H95"),
            "IOU64_mean": mean(group, "IOU64"),
            "IOU64_median": median(group, "IOU64"),
        }

    summary = {
        "protocol": {
            "surface_samples": SAMPLE_N,
            "seed": SEED,
            "CD": "symmetric mean nearest-neighbor distance / full input bbox diagonal",
            "H95": "95th percentile of bidirectional nearest-neighbor distances / full input bbox diagonal",
            "IOU64": "world-aligned surface voxel IoU; 64 cells along longest union-bounds axis",
            "registration": "NONE",
            "cadfit_placement": "per-part uniform max-extent scale + centroid translation, frozen Route A",
        },
        "all_available": {"Ours": stats(ours_complete), "CADFit_complete_only": stats(cadfit_complete)},
        "strict_complete_pair": {
            "case_ids": sorted(complete_ids),
            "Ours": stats(paired_ours),
            "CADFit": stats(paired_cadfit),
            "wins": wins,
        },
        "partial_cadfit_cases": [
            {
                "object_id": row["object_id"],
                "assembled_parts": row["assembled_parts"],
                "total_parts": row["total_parts"],
                "coverage": row["coverage"],
                "CD": row.get("CD"),
                "H95": row.get("H95"),
                "IOU64": row.get("IOU64"),
            }
            for row in rows
            if row["method"] == "CADFit" and row["status"] == "PARTIAL"
        ],
        "unavailable": [row for row in rows if row["status"] == "UNAVAILABLE"],
        "elapsed_sec": time.time() - start,
    }
    dump(OUT / "SUMMARY.json", summary)

    report = [
        "# Gallery-20 quantitative evaluation",
        "",
        "Protocol: 20,000 deterministic surface samples (seed 0), normalized symmetric CD, normalized H95, surface voxel IoU64, no registration.",
        "",
        f"Strict complete paired subset: N={len(complete_ids)}.",
        "",
        "| Method | N | CD mean | H95 mean | IoU64 mean |",
        "|---|---:|---:|---:|---:|",
        f"| Ours | {len(paired_ours)} | {mean(paired_ours, 'CD'):.6f} | {mean(paired_ours, 'H95'):.6f} | {mean(paired_ours, 'IOU64'):.6f} |",
        f"| CADFit | {len(paired_cadfit)} | {mean(paired_cadfit, 'CD'):.6f} | {mean(paired_cadfit, 'H95'):.6f} | {mean(paired_cadfit, 'IOU64'):.6f} |",
        "",
        "Partial CADFit assemblies are diagnostics against the full input and are excluded from the strict aggregate.",
    ]
    (OUT / "FINAL_REPORT.md").write_text("\n".join(report) + "\n")
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
