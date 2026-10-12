"""Run Point2CAD fitting pipeline with diagnostics hooks."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


def _ensure_point2cad_path(repo_point2cad: Path):
    p = str(repo_point2cad)
    if p not in sys.path:
        sys.path.insert(0, p)


def run_point2cad_on_xyzc(
    xyzc_path: Path,
    out_dir: Path,
    point2cad_root: Path,
    seed: int = 2023,
    save_fit_details: bool = True,
) -> Dict:
    """
    Execute Point2CAD main pipeline on an xyzc file.
    Records normalization metadata and per-surface fit summaries.
    """
    _ensure_point2cad_path(point2cad_root)
    from point2cad.fitting_one_surface import process_one_surface
    from point2cad.io_utils import save_clipped_meshes, save_topology, save_unclipped_meshes
    from point2cad.utils import continuous_labels, make_colormap_optimal, seed_everything
    import torch
    from tqdm import tqdm

    from point2cad_diag.normalize_tracked import bbox_stats, inverse_normalize_points, normalize_points_tracked

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "unclipped").mkdir(exist_ok=True)
    (out_dir / "clipped").mkdir(exist_ok=True)
    (out_dir / "topo").mkdir(exist_ok=True)

    seed_everything(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data = np.loadtxt(xyzc_path).astype(np.float32)
    assert data.shape[1] == 4, "expected xyzc"
    points_raw = data[:, :3]
    labels = continuous_labels(data[:, 3].astype(np.int32))
    uniq = np.unique(labels)
    # Point2CAD colormap requires a perfect square size (default 64). GT face
    # counts can exceed that (71/101) → IndexError in save_unclipped_meshes.
    n_need = int(len(uniq))
    side = int(np.ceil(np.sqrt(max(64, n_need))))
    color_list = make_colormap_optimal(num_colors=side * side)

    points_norm, norm_meta = normalize_points_tracked(points_raw)
    # round-trip check
    recon = inverse_normalize_points(points_norm, norm_meta)
    rt_err = float(np.max(np.linalg.norm(recon - points_raw.astype(np.float64), axis=1)))

    class Cfg:
        pass

    cfg = Cfg()
    cfg.validate_checkpoint_path = None
    cfg.silent = True
    cfg.seed = seed
    cfg.num_inr_fit_attempts = 1
    out_meshes: List[dict] = []
    fit_rows = []
    failed = 0
    nan_inf = 0
    for idx in tqdm(uniq, desc=f"fit:{out_dir.name}"):
        surf = process_one_surface(int(idx), points_norm, labels, cfg, device)
        if surf is None:
            failed += 1
            fit_rows.append({"label": int(idx), "failed": True})
            continue
        info = surf.get("info") or {}
        err = info.get("err")
        if err is not None and (not np.isfinite(err)):
            nan_inf += 1
        mesh = surf["mesh"]
        pts = np.asarray(mesh.points)
        fit_rows.append(
            {
                "label": int(idx),
                "failed": False,
                "type": info.get("type"),
                "err": None if err is None else float(err) if np.isfinite(err) else None,
                "inpoints": int(len(surf.get("inpoints", []))),
                "mesh_points": int(len(pts)),
                "mesh_faces": int(len(np.asarray(mesh.faces).reshape(-1, 4))) if hasattr(mesh, "faces") else None,
                "bbox": bbox_stats(pts),
            }
        )
        out_meshes.append(surf)

    type_counts: Dict[str, int] = {}
    for r in fit_rows:
        if r.get("failed"):
            continue
        t = r.get("type") or "unknown"
        type_counts[t] = type_counts.get(t, 0) + 1

    unclipped_path = out_dir / "unclipped" / "mesh.ply"
    clipped_path = out_dir / "clipped" / "mesh.ply"
    topo_path = out_dir / "topo" / "topo.json"

    pm_meshes = save_unclipped_meshes(out_meshes, color_list, str(unclipped_path))
    n_before_clip = len(out_meshes)
    clipped_meshes = save_clipped_meshes(pm_meshes, out_meshes, color_list, str(clipped_path))
    n_after_clip = len(clipped_meshes)
    save_topology(clipped_meshes, str(topo_path))

    topo = json.loads(topo_path.read_text())
    curves = topo.get("curves", [])
    corners = topo.get("corners", [])

    # pairwise candidates = C(n,2); intersecting = len(curves)
    nsurf = n_after_clip
    candidates = nsurf * (nsurf - 1) // 2

    diag = {
        "input_xyzc": str(xyzc_path),
        "point_count": int(len(points_raw)),
        "cluster_count": int(len(uniq)),
        "normalization": norm_meta,
        "normalization_bbox_raw": bbox_stats(points_raw),
        "normalization_bbox_norm": bbox_stats(points_norm),
        "coordinate_roundtrip_max_error": rt_err,
        "coordinate_roundtrip_pass": bool(rt_err <= 1e-5),
        "device": str(device),
        "fit_surfaces": fit_rows,
        "fit_type_counts": type_counts,
        "fit_failed_clusters": failed,
        "fit_nan_inf_count": nan_inf,
        "surfaces_before_clip": n_before_clip,
        "clipped_surface_count": n_after_clip,
        "surfaces_removed_by_clipping": int(max(0, n_before_clip - n_after_clip)),
        "topology": {
            "candidate_adjacent_surface_pairs": int(candidates),
            "actual_intersecting_pairs": int(len(curves)),
            "intersection_polyline_count": int(len(curves)),
            "empty_intersection_count": int(max(0, candidates - len(curves))),
            "edge_count": int(len(curves)),
            "corner_count": int(len(corners)),
        },
        "artifacts": {
            "unclipped": str(unclipped_path),
            "clipped": str(clipped_path),
            "topo": str(topo_path),
        },
        "final_brep_generated": False,
        "final_reconstruction_note": "Point2CAD OSS pipeline ends at clipped meshes + topo.json; no B-Rep/solid sew.",
        "pymesh_backend": "shim_or_unknown",
    }

    # detect pymesh shim
    try:
        import pymesh

        diag["pymesh_backend"] = getattr(pymesh, "__file__", "unknown")
        # probe no-op
        import pymesh as pm

        if "pymesh_shim" in open(pm.__file__, "r", errors="ignore").read(200):
            diag["pymesh_is_shim"] = True
        else:
            # check detect returns empty always for trivial mesh
            diag["pymesh_is_shim"] = "shim" in str(pm.__file__) or "site-packages/pymesh/__init__.py" in str(pm.__file__)
    except Exception as e:
        diag["pymesh_backend"] = f"import_failed:{e}"

    if save_fit_details:
        with open(out_dir / "fit_diagnostics.json", "w") as f:
            json.dump(diag, f, indent=2)
        np.save(out_dir / "points_raw.npy", points_raw)
        np.save(out_dir / "points_norm.npy", points_norm)
        np.save(out_dir / "labels.npy", labels)
        with open(out_dir / "normalization.json", "w") as f:
            json.dump(norm_meta, f, indent=2)

    return diag
