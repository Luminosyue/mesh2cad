#!/usr/bin/env python3
"""Build formal P1 detected-edge inputs from X-Part meshes only."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import trimesh

REPO = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(REPO / "scripts"), str(REPO / "scripts" / "geometry_pack_v1")]

from geometry_pack_v1.edge_sample import sample_edge_cloud
from geometry_pack_v1.mesh_edges import detect_sharp_edges, segment_face_pair_normals

OUT = REPO / "ours3" / "toaster_p1_edge_condition_ablation_v1"
P1 = REPO / "ours3" / "toaster_p1_xpart_v1"
XPART = REPO / "ours3" / "toaster_p3_xpart_cadfit_routea_v1" / "xpart"
DORA = REPO / "ours3" / "toaster_p3_xpart_cadfit_routea_v1" / "dora_ses"
PARTS = [f"PART_{i:03d}" for i in range(39)]
SHARP_DEG = 30.0
NUM_EDGE_POINTS = 1024
SEED = 20260916


def load_mesh(part_id: str):
    path = XPART / part_id / "generated_mesh.obj"
    if not path.is_file():
        path = XPART / part_id / f"complete_part_{part_id[-3:]}.obj"
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    mesh.remove_unreferenced_vertices()
    return mesh, path


def transform(raw: dict) -> tuple[float, np.ndarray]:
    t = raw["transform"] if "transform" in raw else raw
    return float(t["scale"]), np.asarray(t["translation"], dtype=np.float64)


def main() -> int:
    rows = []
    dora_rows = []
    for index, part_id in enumerate(PARTS):
        src = P1 / "inputs" / part_id
        dst = OUT / "inputs" / part_id
        dst.mkdir(parents=True, exist_ok=True)
        for name in ("surface_points.npy", "transform.json", "input_meta.json"):
            if (src / name).is_file():
                shutil.copy2(src / name, dst / name)

        mesh, mesh_path = load_mesh(part_id)
        scale, translation = transform(json.loads((src / "transform.json").read_text()))
        raw_transform = json.loads((src / "transform.json").read_text())
        flat_transform = raw_transform["transform"] if "transform" in raw_transform else raw_transform
        (dst / "coordinate_transform.json").write_text(
            json.dumps(flat_transform, indent=2) + "\n"
        )
        vertices = np.asarray(mesh.vertices, dtype=np.float64) * scale + translation
        faces = np.asarray(mesh.faces, dtype=np.int64)
        canonical = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        adjacency = np.asarray(canonical.face_adjacency, dtype=np.int64)
        adjacency_edges = np.asarray(canonical.face_adjacency_edges, dtype=np.int64)
        if len(adjacency):
            sharp = detect_sharp_edges(vertices, faces, adjacency, adjacency_edges, SHARP_DEG)
            normals = segment_face_pair_normals(vertices, faces, sharp["face_pairs"])
        else:
            sharp = {
                "v0": np.zeros((0, 3)), "v1": np.zeros((0, 3)),
                "face_pairs": np.zeros((0, 2), dtype=np.int64),
                "vertex_indices": np.zeros((0, 2), dtype=np.int64),
                "dihedral_deg": np.zeros((0,)), "num_segments": 0,
            }
            normals = np.zeros((0, 3))
        points, point_normals, seg_idx, stats = sample_edge_cloud(
            sharp["v0"], sharp["v1"], normals, NUM_EDGE_POINTS, SEED + index
        )
        edge = np.concatenate([points, point_normals], axis=1).astype(np.float32)
        if edge.shape != (NUM_EDGE_POINTS, 6):
            raise RuntimeError(f"{part_id}: invalid edge shape {edge.shape}")
        np.save(dst / "edge_points_detected.npy", edge)
        np.save(dst / "edge_segment_index_detected.npy", seg_idx)
        np.savez_compressed(
            dst / "mesh_sharp_edges.npz",
            v0=sharp["v0"].astype(np.float32), v1=sharp["v1"].astype(np.float32),
            vertex_indices=sharp["vertex_indices"],
            dihedral_deg=sharp["dihedral_deg"].astype(np.float32),
            face_pairs=sharp["face_pairs"],
        )
        row = {
            "part_id": part_id, "mesh_path": str(mesh_path),
            "surface_path_readonly_source": str(src / "surface_points.npy"),
            "edge_path": str(dst / "edge_points_detected.npy"),
            "edge_shape": list(edge.shape), "sharp_angle_deg": SHARP_DEG,
            "n_sharp_segments": int(sharp["num_segments"]),
            "empty_edge_padded": bool(stats["empty_padded"]),
            "gt_cad_or_brep_used": False, "method": "mesh_dihedral_angle",
        }
        (dst / "edge_meta.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append(row)
        print(part_id, row["n_sharp_segments"], edge.shape, flush=True)

        dora_src = DORA / "threshold_15" / "sample" / part_id / "dora_samples.npz"
        dora_tf_path = DORA / "normalized" / part_id / "transform.json"
        if dora_src.is_file() and dora_tf_path.is_file():
            raw = np.load(dora_src)["fps_sharp_surface"].reshape(-1, 6).astype(np.float64)
            dora_tf = json.loads(dora_tf_path.read_text())
            dora_scale = float(dora_tf["scale"])
            dora_center = np.asarray(dora_tf["center"], dtype=np.float64)
            xyz_xpart = raw[:, :3] / dora_scale + dora_center
            xyz_p1 = xyz_xpart * scale + translation
            converted = np.concatenate([xyz_p1, raw[:, 3:6]], axis=1)
            select = np.linspace(0, len(converted) - 1, NUM_EDGE_POINTS, dtype=np.int64)
            converted = converted[select].astype(np.float32)
            dora_dst = OUT / "inputs_dora" / part_id
            dora_dst.mkdir(parents=True, exist_ok=True)
            for name in ("surface_points.npy", "transform.json", "input_meta.json", "coordinate_transform.json"):
                if (dst / name).is_file():
                    shutil.copy2(dst / name, dora_dst / name)
            np.save(dora_dst / "edge_points_detected.npy", converted)
            dora_row = {
                "part_id": part_id, "source": str(dora_src),
                "edge_path": str(dora_dst / "edge_points_detected.npy"),
                "edge_shape": list(converted.shape), "method": "Dora-SES threshold_15",
                "coordinate_conversion": "Dora normalized -> X-Part -> P1 canonical",
                "gt_cad_or_brep_used": False,
            }
            (dora_dst / "edge_meta.json").write_text(json.dumps(dora_row, indent=2) + "\n")
            dora_rows.append(dora_row)

    (OUT / "manifest" / "edge_input_manifest.json").write_text(
        json.dumps({"n": len(rows), "interface": "xyz+normals (N,6)", "parts": rows}, indent=2) + "\n"
    )
    (OUT / "manifest" / "dora_edge_input_manifest.json").write_text(
        json.dumps({"n": len(dora_rows), "interface": "xyz+normals (N,6)", "parts": dora_rows}, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
