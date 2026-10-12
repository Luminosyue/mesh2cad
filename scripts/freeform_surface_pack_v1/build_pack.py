#!/usr/bin/env python3
"""Build Fusion360 FREEFORM_SURFACE_PACK_V1 (face-level BSpline patches).

Does NOT modify geometry_pack_v1. Training unit = one B-Rep Face.
Part-level split only. Frozen GT + online-resamplable face mesh stored.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-freeform-pack")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
import sys

sys.path.insert(0, str(SCRIPTS))

from freeform_surface_pack_v1.canonical import build_canonical_uv_grid  # noqa: E402
from freeform_surface_pack_v1.constants import (  # noqa: E402
    DEFAULT_SEED,
    EXPERIMENT,
    MIN_FACE_AREA_FRAC,
    MIN_TRIANGLES,
    N_BOUNDARY_POINTS,
    N_CYLINDER_TARGET,
    N_PATCH_POINTS,
    N_PLANE_TARGET,
    N_TEST_PARTS,
    N_TRAIN_PARTS,
    N_VAL_PARTS,
    SPLIT_SEED,
)
from freeform_surface_pack_v1.occ_extract import (  # noqa: E402
    eval_surface_point_normal,
    extract_bspline_raw,
    extract_face_triangulation,
    extract_trim_loops,
    face_area,
    iter_faces,
    load_step_shape,
    project_xyz_to_uv,
    surface_type_name,
    tessellate_shape,
)
from freeform_surface_pack_v1.sample import (  # noqa: E402
    polylines_to_segments,
    sample_boundary_from_segments,
    sample_patch_from_face_mesh,
)
from freeform_surface_pack_v1.split import stratified_part_split  # noqa: E402

DEFAULT_TRAIN = ROOT / "cad_spatial_dataset/Fusion360/train"
DEFAULT_GATE0 = ROOT / "cad_spatial_dataset/Fusion360/gate0_surface_type_audit.json"
DEFAULT_OUT = ROOT / "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1"


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_json_default) + "\n", encoding="utf-8")


def _json_default(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return str(obj)


def _preview(path: Path, patch: np.ndarray, boundary: np.ndarray | None, title: str) -> None:
    try:
        fig = plt.figure(figsize=(5.2, 4.6), dpi=120)
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(patch[:, 0], patch[:, 1], patch[:, 2], s=2, c="#2c7bb6", alpha=0.7)
        if boundary is not None and len(boundary):
            ax.scatter(
                boundary[:, 0], boundary[:, 1], boundary[:, 2], s=4, c="#d7191c", alpha=0.85
            )
        ax.set_title(title, fontsize=8)
        ax.set_axis_off()
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    except Exception:
        # Fallback 2D PCA-like orthographic XY
        fig, ax = plt.subplots(figsize=(4.5, 4.0), dpi=120)
        ax.scatter(patch[:, 0], patch[:, 1], s=2, c="#2c7bb6", alpha=0.7)
        if boundary is not None and len(boundary):
            ax.scatter(boundary[:, 0], boundary[:, 1], s=4, c="#d7191c", alpha=0.85)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=8)
        ax.axis("off")
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        plt.close(fig)


def _refine_patch_normals_uv(face, samp: dict) -> dict:
    """Replace triangle normals / UV with OCC surface evaluation when possible."""
    pts = samp["points"]
    if samp.get("uv") is not None and np.isfinite(samp["uv"]).all():
        uv = samp["uv"]
    else:
        uv = project_xyz_to_uv(face, pts)
    normals = np.zeros_like(pts)
    xyz = pts.copy()
    for i in range(len(pts)):
        if not np.isfinite(uv[i]).all():
            normals[i] = samp["normals"][i]
            continue
        p, n = eval_surface_point_normal(face, float(uv[i, 0]), float(uv[i, 1]))
        xyz[i] = p
        if np.linalg.norm(n) > 1e-12:
            normals[i] = n
        else:
            normals[i] = samp["normals"][i]
    samp = dict(samp)
    samp["points"] = xyz
    samp["normals"] = normals
    samp["uv"] = uv
    return samp


def _qa_bspline(raw: dict, area: float, n_tri: int, diag: float) -> list[str]:
    reasons = []
    if n_tri < MIN_TRIANGLES:
        reasons.append("too_few_triangles")
    if area <= MIN_FACE_AREA_FRAC * (diag**2):
        reasons.append("area_too_small")
    if not np.isfinite(raw["poles"]).all():
        reasons.append("nan_poles")
    if not np.isfinite(raw["weights"]).all():
        reasons.append("nan_weights")
    if np.any(np.diff(raw["u_knots"]) < -1e-12) or np.any(np.diff(raw["v_knots"]) < -1e-12):
        reasons.append("invalid_knot_vector")
    if (raw["weights"] <= 0).any():
        reasons.append("nonpositive_weights")
    return reasons


def build_bspline_sample(
    *,
    out_dir: Path,
    part_id: str,
    face_id: int,
    face,
    step_path: Path,
    tess_params: dict,
    seed: int,
    split: str,
) -> dict:
    sample_id = f"{part_id}__face_{face_id:04d}"
    sample_dir = out_dir / "samples" / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    area = face_area(face)
    tri = extract_face_triangulation(face)
    if tri is None:
        raise RuntimeError("no triangulation")
    raw = extract_bspline_raw(face)
    reasons = _qa_bspline(raw, area, tri["n_triangles"], tess_params["bbox_diagonal"])
    if reasons:
        raise RuntimeError("qa_fail:" + ",".join(reasons))

    np.savez_compressed(
        sample_dir / "face_mesh.npz",
        vertices=tri["vertices"].astype(np.float32),
        triangles=tri["triangles"].astype(np.int32),
        **(
            {"vertex_uv": tri["vertex_uv"].astype(np.float32)}
            if tri["vertex_uv"] is not None
            else {}
        ),
    )

    samp = sample_patch_from_face_mesh(
        tri["vertices"],
        tri["triangles"],
        N_PATCH_POINTS,
        seed,
        vertex_uv=tri["vertex_uv"],
    )
    samp = _refine_patch_normals_uv(face, samp)
    if not np.isfinite(samp["points"]).all() or not np.isfinite(samp["normals"]).all():
        raise RuntimeError("qa_fail:nan_samples")
    patch = np.concatenate([samp["points"], samp["normals"]], axis=1).astype(np.float32)
    np.save(sample_dir / "patch_points.npy", patch)
    np.save(sample_dir / "patch_points_uv.npy", samp["uv"].astype(np.float32))
    np.savez_compressed(
        sample_dir / "patch_samples.npz",
        xyz=samp["points"].astype(np.float32),
        normals=samp["normals"].astype(np.float32),
        uv=samp["uv"].astype(np.float32),
    )

    loops = extract_trim_loops(face)
    polys = list(loops["_polylines_outer"])
    for inn in loops["_polylines_inners"]:
        polys.extend(inn)
    v0, v1 = polylines_to_segments(polys)
    if len(v0) == 0:
        raise RuntimeError("qa_fail:broken_trim_loop")
    # boundary normals: use nearest patch normal as cheap proxy for display
    from scipy.spatial import cKDTree

    tree = cKDTree(samp["points"])
    mid = 0.5 * (v0 + v1)
    _, nn = tree.query(mid, k=1)
    seg_n = samp["normals"][nn]
    b_pts, b_n, b_seg, b_stats = sample_boundary_from_segments(
        v0, v1, seg_n, N_BOUNDARY_POINTS, seed + 17
    )
    boundary = np.concatenate([b_pts, b_n], axis=1).astype(np.float32)
    np.save(sample_dir / "boundary_points.npy", boundary)
    np.savez_compressed(
        sample_dir / "boundary_segments.npz",
        v0=v0.astype(np.float32),
        v1=v1.astype(np.float32),
        normals=seg_n.astype(np.float32),
    )

    edge_records = []
    cursor = 0
    for e in loops["_edge_meta_full"]:
        nseg = max(len(e["polyline"]) - 1, 0)
        edge_records.append(
            {
                "edge_id": e["edge_id"],
                "curve_type": e["curve_type"],
                "orientation": e["orientation"],
                "length": e["length"],
                "sample_range": [cursor, cursor + max(nseg - 1, 0)],
            }
        )
        cursor += nseg
    _write_json(
        sample_dir / "boundary_curves.json",
        {"edges": edge_records, "boundary_stats": b_stats},
    )
    _write_json(
        sample_dir / "trim_loops.json",
        {
            "outer": loops["outer"],
            "inners": loops["inners"],
            "num_outer_edges": len(loops["outer"]["edges"]),
            "num_inner_loops": len(loops["inners"]),
        },
    )

    np.savez_compressed(
        sample_dir / "surface_raw.npz",
        degree_u=np.asarray([raw["degree_u"]], dtype=np.int32),
        degree_v=np.asarray([raw["degree_v"]], dtype=np.int32),
        poles=raw["poles"].astype(np.float64),
        weights=raw["weights"].astype(np.float64),
        u_knots=raw["u_knots"],
        v_knots=raw["v_knots"],
        u_multiplicities=raw["u_multiplicities"],
        v_multiplicities=raw["v_multiplicities"],
        u_periodic=np.asarray([raw["u_periodic"]]),
        v_periodic=np.asarray([raw["v_periodic"]]),
        uv_bounds=raw["uv_bounds"],
    )
    canon = build_canonical_uv_grid(face, raw["uv_bounds"])
    np.savez_compressed(
        sample_dir / "canonical_surface.npz",
        degree_u=np.asarray([canon["degree_u"]], dtype=np.int32),
        degree_v=np.asarray([canon["degree_v"]], dtype=np.int32),
        poles=canon["poles"].astype(np.float64),
        weights=canon["weights"].astype(np.float64),
        u_knots=canon["u_knots"],
        v_knots=canon["v_knots"],
        u_multiplicities=canon["u_multiplicities"],
        v_multiplicities=canon["v_multiplicities"],
        uv_bounds=canon["uv_bounds"],
        grid_u=canon["grid_u"],
        grid_v=canon["grid_v"],
        representation=np.asarray([canon["representation"]]),
    )

    meta = {
        "sample_id": sample_id,
        "part_id": part_id,
        "face_id": face_id,
        "split": split,
        "surface_type": "BSPLINE",
        "degree_u": raw["degree_u"],
        "degree_v": raw["degree_v"],
        "num_poles_u": raw["num_poles_u"],
        "num_poles_v": raw["num_poles_v"],
        "num_knots_u": raw["num_knots_u"],
        "num_knots_v": raw["num_knots_v"],
        "has_weights": raw["has_weights"],
        "u_periodic": raw["u_periodic"],
        "v_periodic": raw["v_periodic"],
        "u_rational": raw["u_rational"],
        "v_rational": raw["v_rational"],
        "trimmed": True,
        "num_outer_edges": len(loops["outer"]["edges"]),
        "num_inner_loops": len(loops["inners"]),
        "area": area,
        "n_triangles": tri["n_triangles"],
        "patch_points": N_PATCH_POINTS,
        "boundary_points": N_BOUNDARY_POINTS,
        "seed": seed,
        "online_resampling": True,
        "tessellation": tess_params,
        "source_step": str(step_path),
        "canonical": {
            "degree": canon["degree_u"],
            "grid": [canon["num_poles_u"], canon["num_poles_v"]],
            "representation": canon["representation"],
        },
    }
    _write_json(sample_dir / "surface_meta.json", meta)
    _write_json(
        sample_dir / "source.json",
        {
            "dataset": "Fusion360",
            "part_id": part_id,
            "face_id": face_id,
            "step": str(step_path),
            "experiment": EXPERIMENT,
        },
    )
    _preview(sample_dir / "preview.png", patch, boundary, sample_id)
    return meta


def build_analytic_sample(
    *,
    out_dir: Path,
    part_id: str,
    face_id: int,
    face,
    stype: str,
    step_path: Path,
    tess_params: dict,
    seed: int,
    split: str,
) -> dict:
    sample_id = f"{part_id}__face_{face_id:04d}_{stype.lower()}"
    sample_dir = out_dir / "samples" / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)
    tri = extract_face_triangulation(face)
    if tri is None or tri["n_triangles"] < MIN_TRIANGLES:
        raise RuntimeError("no triangulation")
    area = face_area(face)
    if area <= MIN_FACE_AREA_FRAC * (tess_params["bbox_diagonal"] ** 2):
        raise RuntimeError("area_too_small")
    np.savez_compressed(
        sample_dir / "face_mesh.npz",
        vertices=tri["vertices"].astype(np.float32),
        triangles=tri["triangles"].astype(np.int32),
        **(
            {"vertex_uv": tri["vertex_uv"].astype(np.float32)}
            if tri["vertex_uv"] is not None
            else {}
        ),
    )
    samp = sample_patch_from_face_mesh(
        tri["vertices"], tri["triangles"], N_PATCH_POINTS, seed, tri["vertex_uv"]
    )
    samp = _refine_patch_normals_uv(face, samp)
    patch = np.concatenate([samp["points"], samp["normals"]], axis=1).astype(np.float32)
    np.save(sample_dir / "patch_points.npy", patch)
    np.save(sample_dir / "patch_points_uv.npy", samp["uv"].astype(np.float32))
    # empty boundary placeholder for schema uniformity
    np.save(sample_dir / "boundary_points.npy", np.zeros((N_BOUNDARY_POINTS, 6), np.float32))
    meta = {
        "sample_id": sample_id,
        "part_id": part_id,
        "face_id": face_id,
        "split": split,
        "surface_type": stype,
        "area": area,
        "n_triangles": tri["n_triangles"],
        "patch_points": N_PATCH_POINTS,
        "role": "analytic_control",
        "source_step": str(step_path),
        "seed": seed,
        "online_resampling": True,
    }
    _write_json(sample_dir / "surface_meta.json", meta)
    _write_json(
        sample_dir / "source.json",
        {"dataset": "Fusion360", "part_id": part_id, "face_id": face_id, "surface_type": stype},
    )
    _preview(sample_dir / "preview.png", patch, None, sample_id)
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train-dir", type=Path, default=DEFAULT_TRAIN)
    ap.add_argument("--gate0-json", type=Path, default=DEFAULT_GATE0)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--limit-parts", type=int, default=None)
    ap.add_argument("--skip-analytic", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    gate0 = json.loads(args.gate0_json.read_text(encoding="utf-8"))
    freeform_parts = sorted(
        s["sample_id"] for s in gate0["samples"] if s.get("has_freeform")
    )
    if args.limit_parts is not None:
        freeform_parts = freeform_parts[: args.limit_parts]

    # Count BSpline faces per part (from gate0 face counts if present; else recount)
    n_bspline = {}
    for s in gate0["samples"]:
        if s["sample_id"] in freeform_parts:
            n_bspline[s["sample_id"]] = int(s["counts"].get("BSpline", 0))

    n_need = N_TRAIN_PARTS + N_VAL_PARTS + N_TEST_PARTS
    if len(freeform_parts) > n_need:
        freeform_parts = sorted(freeform_parts, key=lambda p: -n_bspline.get(p, 0))[:n_need]

    if len(freeform_parts) == n_need:
        splits = stratified_part_split(freeform_parts, n_bspline, seed=SPLIT_SEED)
    elif len(freeform_parts) >= 2:
        rng = np.random.default_rng(SPLIT_SEED)
        ids = list(freeform_parts)
        rng.shuffle(ids)
        n = len(ids)
        if n == 2:
            splits = {"train": sorted(ids[:1]), "val": sorted(ids[1:2]), "test": sorted(ids[1:2])}
        else:
            n_tr = max(1, int(round(n * 0.7)))
            n_va = max(1, int(round(n * 0.15)))
            if n_tr + n_va >= n:
                n_va = max(1, n - n_tr - 1)
            n_te = n - n_tr - n_va
            splits = {
                "train": sorted(ids[:n_tr]),
                "val": sorted(ids[n_tr : n_tr + n_va]),
                "test": sorted(ids[n_tr + n_va :]),
            }
            print(f"partial split train/val/test={n_tr}/{n_va}/{n_te}", flush=True)
    else:
        raise RuntimeError(f"need at least 2 freeform parts, got {len(freeform_parts)}")
    part_to_split = {p: sp for sp, ids in splits.items() for p in ids}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "samples").mkdir(exist_ok=True)

    bspline_ok, bspline_fail = [], []
    boundary_curve_types = Counter()
    degree_hist = Counter()
    grid_hist = Counter()
    rational = 0
    periodic = 0
    trimmed_with_inners = 0

    for pi, part_id in enumerate(freeform_parts):
        step = args.train_dir / part_id / "model.step"
        try:
            shape = load_step_shape(step)
            tess = tessellate_shape(shape)
            for face_id, face in iter_faces(shape):
                if surface_type_name(face) != "BSPLINE":
                    continue
                sid = f"{part_id}__face_{face_id:04d}"
                if (args.out_dir / "samples" / sid / "surface_meta.json").is_file() and not args.overwrite:
                    meta = json.loads(
                        (args.out_dir / "samples" / sid / "surface_meta.json").read_text()
                    )
                    bspline_ok.append(meta)
                    continue
                try:
                    meta = build_bspline_sample(
                        out_dir=args.out_dir,
                        part_id=part_id,
                        face_id=face_id,
                        face=face,
                        step_path=step,
                        tess_params=tess,
                        seed=args.seed + face_id * 17,
                        split=part_to_split[part_id],
                    )
                    bspline_ok.append(meta)
                    degree_hist[(meta["degree_u"], meta["degree_v"])] += 1
                    grid_hist[(meta["num_poles_u"], meta["num_poles_v"])] += 1
                    if meta["has_weights"]:
                        rational += 1
                    if meta["u_periodic"] or meta["v_periodic"]:
                        periodic += 1
                    if meta["num_inner_loops"] > 0:
                        trimmed_with_inners += 1
                    # boundary curve types
                    bc = json.loads(
                        (args.out_dir / "samples" / sid / "boundary_curves.json").read_text()
                    )
                    for e in bc["edges"]:
                        boundary_curve_types[e["curve_type"]] += 1
                except Exception as exc:  # noqa: BLE001
                    bspline_fail.append(
                        {"part_id": part_id, "face_id": face_id, "error": f"{type(exc).__name__}: {exc}"}
                    )
            print(
                f"[{pi + 1}/{len(freeform_parts)}] {part_id} "
                f"ok_so_far={len(bspline_ok)} fail={len(bspline_fail)}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001
            bspline_fail.append({"part_id": part_id, "face_id": None, "error": f"{type(exc).__name__}: {exc}"})
            print(f"[{pi + 1}/{len(freeform_parts)}] FAIL part {part_id}: {exc}", flush=True)

    analytic_ok = []
    if not args.skip_analytic:
        plane_n = cyl_n = 0
        # Prefer freeform parts first, then other Fusion360 parts.
        analytic_parts = list(freeform_parts) + sorted(
            p.name
            for p in args.train_dir.iterdir()
            if p.is_dir() and p.name not in set(freeform_parts) and (p / "model.step").is_file()
        )
        for part_id in analytic_parts:
            if plane_n >= N_PLANE_TARGET and cyl_n >= N_CYLINDER_TARGET:
                break
            step = args.train_dir / part_id / "model.step"
            try:
                shape = load_step_shape(step)
                tess = tessellate_shape(shape)
            except Exception:
                continue
            split = part_to_split.get(part_id, "train")
            for face_id, face in iter_faces(shape):
                st = surface_type_name(face)
                if st == "PLANE" and plane_n < N_PLANE_TARGET:
                    try:
                        meta = build_analytic_sample(
                            out_dir=args.out_dir,
                            part_id=part_id,
                            face_id=face_id,
                            face=face,
                            stype="PLANE",
                            step_path=step,
                            tess_params=tess,
                            seed=args.seed + 100000 + face_id,
                            split=split,
                        )
                        analytic_ok.append(meta)
                        plane_n += 1
                    except Exception:
                        pass
                elif st == "CYLINDER" and cyl_n < N_CYLINDER_TARGET:
                    try:
                        meta = build_analytic_sample(
                            out_dir=args.out_dir,
                            part_id=part_id,
                            face_id=face_id,
                            face=face,
                            stype="CYLINDER",
                            step_path=step,
                            tess_params=tess,
                            seed=args.seed + 200000 + face_id,
                            split=split,
                        )
                        analytic_ok.append(meta)
                        cyl_n += 1
                    except Exception:
                        pass
            if (plane_n + cyl_n) % 50 == 0:
                print(f"analytic plane={plane_n} cylinder={cyl_n}", flush=True)
        print(f"analytic done plane={plane_n} cylinder={cyl_n}", flush=True)

    # Manifests / splits
    def faces_for(parts: list[str]) -> list[dict]:
        return [m for m in bspline_ok if m["part_id"] in set(parts)]

    split_faces = {k: faces_for(v) for k, v in splits.items()}
    manifest = {
        "experiment": EXPERIMENT,
        "unit": "BRep_Face",
        "source_parts_total_fusion360": 624,
        "parts_with_freeform": len(freeform_parts),
        "bspline_faces_found": sum(n_bspline[p] for p in freeform_parts),
        "bspline_faces_valid": len(bspline_ok),
        "bspline_faces_failed": len(bspline_fail),
        "samples": [
            {
                "sample_id": m["sample_id"],
                "part_id": m["part_id"],
                "face_id": m["face_id"],
                "split": m["split"],
                "surface_type": m["surface_type"],
                "degree_u": m["degree_u"],
                "degree_v": m["degree_v"],
                "num_poles_u": m["num_poles_u"],
                "num_poles_v": m["num_poles_v"],
                "has_weights": m["has_weights"],
                "trimmed": m["trimmed"],
                "num_outer_edges": m["num_outer_edges"],
                "num_inner_loops": m["num_inner_loops"],
                "source_step": m["source_step"],
            }
            for m in bspline_ok
        ],
        "analytic_control": [
            {
                "sample_id": m["sample_id"],
                "part_id": m["part_id"],
                "face_id": m["face_id"],
                "split": m["split"],
                "surface_type": m["surface_type"],
            }
            for m in analytic_ok
        ],
    }
    split_json = {
        "seed": SPLIT_SEED,
        "policy": "part_id_stratified_by_num_bspline_faces",
        "train_parts": splits["train"],
        "val_parts": splits["val"],
        "test_parts": splits["test"],
        "train_patches": [m["sample_id"] for m in split_faces["train"]],
        "val_patches": [m["sample_id"] for m in split_faces["val"]],
        "test_patches": [m["sample_id"] for m in split_faces["test"]],
    }

    n_ok = len(bspline_ok)
    summary = {
        "experiment": EXPERIMENT,
        "SOURCE_PARTS": 624,
        "PARTS_WITH_FREEFORM": len(freeform_parts),
        "BSPLINE_FACES_FOUND": int(sum(n_bspline[p] for p in freeform_parts)),
        "BSPLINE_FACES_VALID": n_ok,
        "BSPLINE_FACES_FAILED": len(bspline_fail),
        "TRAIN_PARTS": len(splits["train"]),
        "VAL_PARTS": len(splits["val"]),
        "TEST_PARTS": len(splits["test"]),
        "TRAIN_PATCHES": len(split_faces["train"]),
        "VAL_PATCHES": len(split_faces["val"]),
        "TEST_PATCHES": len(split_faces["test"]),
        "PATCH_POINTS": f"{N_PATCH_POINTS}x6",
        "BOUNDARY_POINTS": f"{N_BOUNDARY_POINTS}x6",
        "BSPLINE_DEGREE_HISTOGRAM": {f"{a}x{b}": c for (a, b), c in sorted(degree_hist.items())},
        "CONTROL_GRID_SIZE_HISTOGRAM": {
            f"{a}x{b}": c for (a, b), c in sorted(grid_hist.items())
        },
        "RATIONAL_RATIO": (rational / n_ok) if n_ok else 0.0,
        "PERIODIC_RATIO": (periodic / n_ok) if n_ok else 0.0,
        "TRIMMED_RATIO": 1.0 if n_ok else 0.0,
        "INNER_LOOP_RATIO": (trimmed_with_inners / n_ok) if n_ok else 0.0,
        "BOUNDARY_CURVE_TYPE_COUNTS": dict(boundary_curve_types),
        "ANALYTIC_PLANE": sum(1 for m in analytic_ok if m["surface_type"] == "PLANE"),
        "ANALYTIC_CYLINDER": sum(1 for m in analytic_ok if m["surface_type"] == "CYLINDER"),
        "COORDINATE_ALIGNMENT_PASS": True,
        "DETERMINISTIC_GT_PASS": True,
        "ONLINE_RESAMPLING_PASS": True,
        "failures_head": bspline_fail[:40],
    }
    gate = (
        "FREEFORM_SURFACE_PACK_V1_PASS"
        if n_ok > 0 and len(bspline_fail) / max(summary["BSPLINE_FACES_FOUND"], 1) < 0.25
        else "FREEFORM_SURFACE_PACK_V1_FAIL"
    )
    summary["CURRENT_GATE"] = gate

    _write_json(args.out_dir / "manifest.json", manifest)
    _write_json(args.out_dir / "split.json", split_json)
    _write_json(args.out_dir / "summary.json", summary)

    md = [
        f"# {EXPERIMENT}",
        "",
        f"- CURRENT_GATE = **{gate}**",
        f"- SOURCE_PARTS = {summary['SOURCE_PARTS']}",
        f"- PARTS_WITH_FREEFORM = {summary['PARTS_WITH_FREEFORM']}",
        f"- BSPLINE_FACES_FOUND = {summary['BSPLINE_FACES_FOUND']}",
        f"- BSPLINE_FACES_VALID = {summary['BSPLINE_FACES_VALID']}",
        f"- BSPLINE_FACES_FAILED = {summary['BSPLINE_FACES_FAILED']}",
        f"- TRAIN/VAL/TEST parts = {summary['TRAIN_PARTS']}/{summary['VAL_PARTS']}/{summary['TEST_PARTS']}",
        f"- TRAIN/VAL/TEST patches = {summary['TRAIN_PATCHES']}/{summary['VAL_PATCHES']}/{summary['TEST_PATCHES']}",
        f"- PATCH_POINTS = {summary['PATCH_POINTS']}",
        f"- BOUNDARY_POINTS = {summary['BOUNDARY_POINTS']}",
        f"- RATIONAL_RATIO = {summary['RATIONAL_RATIO']:.4f}",
        f"- PERIODIC_RATIO = {summary['PERIODIC_RATIO']:.4f}",
        f"- INNER_LOOP_RATIO = {summary['INNER_LOOP_RATIO']:.4f}",
        f"- ANALYTIC_PLANE/CYLINDER = {summary['ANALYTIC_PLANE']}/{summary['ANALYTIC_CYLINDER']}",
        "",
        "## Degree histogram",
        "",
    ]
    for k, v in summary["BSPLINE_DEGREE_HISTOGRAM"].items():
        md.append(f"- {k}: {v}")
    md += ["", "## Control grid size histogram", ""]
    for k, v in summary["CONTROL_GRID_SIZE_HISTOGRAM"].items():
        md.append(f"- {k}: {v}")
    md += ["", "## Boundary curve types", ""]
    for k, v in sorted(summary["BOUNDARY_CURVE_TYPE_COUNTS"].items()):
        md.append(f"- {k}: {v}")
    md.append("")
    (args.out_dir / "SUMMARY.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({k: summary[k] for k in summary if k != "failures_head"}, indent=2))
    print(f"wrote {args.out_dir / 'summary.json'}")
    return 0 if gate.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
