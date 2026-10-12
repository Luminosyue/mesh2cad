#!/usr/bin/env python3
"""Official Point2CAD reconstruction backend (surface fit / intersect / clip / topo).

Must be executed with point2cad/.venv/bin/python.
Does not replace ParseNet; input must already be (x,y,z,s).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import trimesh

P2C = Path("/data/home/cuiyuehan/project/mesh2cad/point2cad")
sys.path.insert(0, str(P2C))

from point2cad.io_utils import save_clipped_meshes, save_topology, save_unclipped_meshes
from point2cad.main import process_singleprocessing
from point2cad.utils import EPS, continuous_labels, make_colormap_optimal, pca_numpy, rotation_matrix_a_to_b, seed_everything


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def world_to_p2c_transform(points: np.ndarray) -> dict:
    mean = np.mean(points, 0)
    X = points - mean
    S, U = pca_numpy(X)
    smallest_ev = U[:, np.argmin(S)]
    R = rotation_matrix_a_to_b(smallest_ev, np.array([1.0, 0.0, 0.0]))
    Xr = (R @ X.T).T
    std = np.max(Xr, 0) - np.min(Xr, 0)
    scale = float(np.max(std) + EPS)
    return {"mean": mean.astype(float).tolist(), "R": np.asarray(R, dtype=float).tolist(), "scale": scale}


def unnormalize(pts: np.ndarray, tf: dict) -> np.ndarray:
    mean = np.asarray(tf["mean"], dtype=float)
    R = np.asarray(tf["R"], dtype=float)
    scale = float(tf["scale"])
    return (np.linalg.inv(R) @ (np.asarray(pts, dtype=float) * scale).T).T + mean


def rewrite_ply_world(src: Path, dst: Path, tf: dict) -> bool:
    if not src.is_file():
        return False
    mesh = trimesh.load(str(src), force="mesh", process=False)
    mesh.vertices = unnormalize(np.asarray(mesh.vertices, dtype=float), tf)
    dst.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(str(dst))
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_in", required=True)
    parser.add_argument("--path_out", required=True)
    parser.add_argument("--seed", type=int, default=2023)
    args = parser.parse_args()
    path_in = Path(args.path_in)
    path_out = Path(args.path_out)
    path_out.mkdir(parents=True, exist_ok=True)
    os.chdir(str(path_out))
    seed_everything(args.seed)

    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    color_list = make_colormap_optimal()
    points_labels = np.loadtxt(str(path_in)).astype(np.float32)
    assert points_labels.shape[1] == 4, "expected (x,y,z,s)"
    points = points_labels[:, :3]
    labels = continuous_labels(points_labels[:, 3].astype(np.int32))
    tf = world_to_p2c_transform(points)
    dump_json(path_out / "p2c_normalize_transform.json", tf)

    from point2cad.utils import normalize_points

    points_n = normalize_points(points)
    uniq = np.unique(labels)
    class Cfg:
        silent = True
        seed = args.seed
        max_parallel_surfaces = 1
        num_inr_fit_attempts = 1
        validate_checkpoint_path = None

    cfg = Cfg()
    print(f"[p2c] device={device} patches={len(uniq)} points={len(points)}", flush=True)
    out_meshes = process_singleprocessing(cfg, uniq, points_n, labels, device)
    fits = []
    kept_meshes = []
    for m in out_meshes:
        if not isinstance(m, dict) or m.get("mesh") is None:
            continue
        kept_meshes.append(m)
        info = dict(m.get("info") or {})
        inp = m.get("inpoints")
        info["n_inpoints"] = int(len(inp)) if inp is not None else 0
        fits.append(info)
    out_meshes = kept_meshes
    dump_json(path_out / "surface_fits.json", {"n": len(fits), "fits": fits})

    (path_out / "unclipped").mkdir(exist_ok=True)
    (path_out / "clipped").mkdir(exist_ok=True)
    (path_out / "topo").mkdir(exist_ok=True)
    unclipped_ok = clipped_ok = topo_ok = False
    n_curves = n_corners = 0
    try:
        print("Saving unclipped meshes...", flush=True)
        pm_meshes = save_unclipped_meshes(out_meshes, color_list, str(path_out / "unclipped/mesh.ply"))
        unclipped_ok = (path_out / "unclipped/mesh.ply").is_file()
    except Exception as exc:
        dump_json(path_out / "unclipped_error.json", {"error": str(exc)})
        pm_meshes = None
    try:
        print("Saving clipped meshes...", flush=True)
        if pm_meshes is not None and out_meshes:
            clipped_meshes = save_clipped_meshes(pm_meshes, out_meshes, color_list, str(path_out / "clipped/mesh.ply"))
        else:
            clipped_meshes = []
        clipped_ok = (path_out / "clipped/mesh.ply").is_file()
    except Exception as exc:
        dump_json(path_out / "clipped_error.json", {"error": str(exc)})
        clipped_meshes = []
        if unclipped_ok:
            (path_out / "clipped").mkdir(exist_ok=True)
            (path_out / "clipped/mesh.ply").write_bytes((path_out / "unclipped/mesh.ply").read_bytes())
            clipped_ok = True
            clipped_meshes = []
    try:
        print("Saving topology...", flush=True)
        if clipped_meshes:
            save_topology(clipped_meshes, str(path_out / "topo/topo.json"))
        topo_ok = (path_out / "topo/topo.json").is_file()
        if topo_ok:
            topo = json.loads((path_out / "topo/topo.json").read_text())
            n_curves = len(topo.get("curves") or [])
            n_corners = len(topo.get("corners") or [])
    except Exception as exc:
        dump_json(path_out / "topo_error.json", {"error": str(exc)})

    rewrite_ply_world(path_out / "unclipped/mesh.ply", path_out / "unclipped/mesh_world.ply", tf)
    rewrite_ply_world(path_out / "clipped/mesh.ply", path_out / "clipped/mesh_world.ply", tf)
    if topo_ok:
        topo = json.loads((path_out / "topo/topo.json").read_text())
        for curve in topo.get("curves") or []:
            pts = np.asarray(curve.get("pv_points") or [], dtype=float)
            if len(pts):
                curve["pv_points_world"] = unnormalize(pts, tf).tolist()
        corners = np.asarray(topo.get("corners") or [], dtype=float)
        if len(corners):
            topo["corners_world"] = unnormalize(corners, tf).tolist()
        dump_json(path_out / "topo/topo_world.json", topo)

    types = [f.get("type") for f in fits]
    result = {
        "POINT2CAD_OFFICIAL": True,
        "PARSE_NET_USED": False,
        "device": str(device),
        "n_input_points": int(len(points)),
        "n_input_patches": int(len(uniq)),
        "n_fitted_surfaces": len(fits),
        "surface_types": types,
        "unclipped_ok": unclipped_ok,
        "clipped_ok": clipped_ok,
        "topology_ok": topo_ok,
        "TOPO_CURVES": n_curves,
        "TOPO_CORNERS": n_corners,
        "surface_success": bool(unclipped_ok or clipped_ok),
        "topology_success": bool(topo_ok),
    }
    dump_json(path_out / "point2cad_result.json", result)
    print(json.dumps(result), flush=True)
    return 0 if result["surface_success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
