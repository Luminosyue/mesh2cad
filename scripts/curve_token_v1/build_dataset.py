#!/usr/bin/env python3
"""Per-CAD Track B builder: STEP -> curves.json / curve_samples.npz / topology.json.

Writes only under `ours3/curve_token_data_v1/`. Track A is opened read-only, and
only for the cad_id whitelist and the frozen `coordinate_transform.json`.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from .canonicalize_curves import resolve_normalization
from .config import (
    CURVE_TYPE_IDS,
    N_SAMPLE_DEFAULT,
    N_SAMPLE_EXTRA,
    SCHEMA_VERSION,
    SPLITS,
    STEP_FILENAME,
    cad_dir,
)
from .extract_brep_curves import extract_curves_from_shape
from .extract_topology import extract_topology, topology_arrays
from .occ_curve_v1 import load_step_shape, make_adaptor
from .sample_curves import build_sample_arrays

# Ablation levels this data format is designed to support (section 20 of the spec).
ABLATION_SUPPORT = {
    "A0_surface_points_only": "track_a_only",
    "A1_surface_plus_edge_score": "track_a_only",
    "B0_sampled_edge_points": True,
    "B1_exact_parametric_curve": True,
    "B2_sampled_curve_geometry": True,
    "B3_parametric_plus_sampled": True,
    "B4_parametric_plus_sampled_plus_topology": True,
    "final_surface_tokens_plus_curve_tokens": "requires_curve_encoder",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def list_cad_ids(split: str, limit: int | None = None, seed: int = 0) -> list[str]:
    """cad_ids that have BOTH a STEP source and a Track A pack.

    Restricting to the Track A whitelist is what makes Track B a valid ablation
    arm against A0/A1 rather than a differently-scoped dataset.
    """
    cfg = SPLITS[split]
    step_root: Path = cfg["step_root"]
    pack_root: Path = cfg["track_a_pack"]
    ids = []
    for d in sorted(step_root.iterdir()):
        if not d.is_dir():
            continue
        if not (d / STEP_FILENAME).is_file():
            continue
        if not (pack_root / d.name).is_dir():
            continue
        ids.append(d.name)
    if limit is not None and limit < len(ids):
        rng = np.random.default_rng(seed)
        ids = [ids[i] for i in sorted(rng.choice(len(ids), size=limit, replace=False))]
    return ids


def build_one(
    split: str,
    cad_id: str,
    n_sample: int = N_SAMPLE_DEFAULT,
    extra_samples: tuple[int, ...] = N_SAMPLE_EXTRA,
    overwrite: bool = True,
) -> dict:
    t0 = time.time()
    cfg = SPLITS[split]
    step_path: Path = cfg["step_root"] / cad_id / STEP_FILENAME
    pack_dir: Path = cfg["track_a_pack"] / cad_id
    out_dir = cad_dir(split, cad_id)

    if not step_path.is_file():
        return {"cad_id": cad_id, "split": split, "ok": False, "error": f"missing STEP: {step_path}"}
    if out_dir.exists() and not overwrite and (out_dir / "curves.json").is_file():
        return {"cad_id": cad_id, "split": split, "ok": True, "skipped": "exists"}

    shape = load_step_shape(step_path)
    data = extract_curves_from_shape(shape, cad_id=cad_id)
    records = data["curves"]
    if not records:
        return {
            "cad_id": cad_id,
            "split": split,
            "ok": False,
            "error": "no usable curves",
            "num_skipped_edges": data["num_skipped_edges"],
        }

    # Normalization: reuse Track A's frozen transform when present so Curve
    # Tokens land in the same frame as the existing Surface/Edge tokens.
    ta_transform = pack_dir / "coordinate_transform.json"
    nz = resolve_normalization(
        ta_transform if ta_transform.is_file() else None,
        data["source_bbox_min"],
        data["source_bbox_max"],
    )

    from .canonicalize_curves import canonicalize_curves

    data = canonicalize_curves(data, nz)

    # Adaptors are rebuilt in the same IndexedMap order used by the extractor.
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp
    from OCP.TopoDS import TopoDS
    from OCP.TopTools import TopTools_IndexedMapOfShape

    emap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, emap)
    adaptors = [make_adaptor(TopoDS.Edge_s(emap.FindKey(r["edge_id"] + 1))) for r in records]

    topology = extract_topology(shape, records)
    arrays = build_sample_arrays(adaptors, records, n_sample, nz)
    arrays.update(topology_arrays(topology, records))

    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_dir / "curve_samples.npz", **arrays)

    for n_extra in extra_samples:
        if n_extra == n_sample:
            continue
        extra = build_sample_arrays(adaptors, [dict(r) for r in records], n_extra, nz)
        np.savez_compressed(
            out_dir / f"curve_samples_{n_extra}.npz",
            **{
                k: v
                for k, v in extra.items()
                if k
                in {
                    "curve_xyz",
                    "curve_xyz_normalized",
                    "curve_tangent",
                    "curve_mask",
                    "curve_u",
                    "curve_polyline_length",
                    "curve_type_id",
                    "curve_edge_id",
                    "n_sample",
                    "num_curves",
                    "sampling_mode",
                }
            },
        )

    type_counts: dict[str, int] = {}
    for r in records:
        type_counts[r["curve_type"]] = type_counts.get(r["curve_type"], 0) + 1

    n_param_ok = sum(1 for r in records if r["extraction"]["parameter_extraction_ok"])
    n_geom_ok = sum(1 for r in records if r["extraction"]["geometry_reconstruction_ok"])

    curves_json = {
        "schema_version": SCHEMA_VERSION,
        "cad_id": cad_id,
        "split": split,
        "dataset": cfg["dataset"],
        "num_curves": data["num_curves"],
        "num_topo_edges": data["num_topo_edges"],
        "num_vertices": data["num_vertices"],
        "num_faces": data["num_faces"],
        "num_skipped_edges": data["num_skipped_edges"],
        "skipped_edges": data["skipped_edges"],
        "curve_type_counts": type_counts,
        "curve_type_ids": CURVE_TYPE_IDS,
        "source_bbox_min": data["source_bbox_min"],
        "source_bbox_max": data["source_bbox_max"],
        "source_diagonal": data["source_diagonal"],
        "recon_tolerance": data["recon_tolerance"],
        "curves": records,
    }
    _write_json(out_dir / "curves.json", curves_json)
    _write_json(out_dir / "topology.json", topology)
    _write_json(out_dir / "normalization.json", nz.to_json())

    elapsed = time.time() - t0
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "cad_id": cad_id,
        "split": split,
        "dataset": cfg["dataset"],
        "track": "B",
        "method": "parametric_curve_token",
        "data_source": "exact_brep_curve_from_cad_kernel",
        "source_step": str(step_path),
        "source_step_sha256": _sha256(step_path),
        "track_a_pack_dir": str(pack_dir),
        "track_a_access": "read_only",
        "track_a_reused_files": ["coordinate_transform.json"] if ta_transform.is_file() else [],
        "normalization_source": nz.source,
        "normalization_version": nz.normalization_version,
        "num_curves": data["num_curves"],
        "num_vertices": data["num_vertices"],
        "num_faces": data["num_faces"],
        "curve_type_counts": type_counts,
        "n_sample": int(n_sample),
        "extra_sample_counts": [int(x) for x in extra_samples if x != n_sample],
        "precision": {
            "curves_json_dtype": "float64 (exact parameters)",
            "curve_samples_xyz_dtype": "float32",
            "curve_u_dtype": "float64",
            "max_abs_world_coord": float(np.abs(arrays["curve_xyz"]).max()),
            # float32 precision follows coordinate magnitude, so a small part far
            # from the origin is more accurate in the recentred normalized frame
            "world_float32_resolution": float(
                np.abs(arrays["curve_xyz"]).max() * np.finfo(np.float32).eps
            ),
            "normalized_float32_resolution": float(
                np.abs(arrays["curve_xyz_normalized"]).max() * np.finfo(np.float32).eps
            ),
            "prefer_normalized_for_training": bool(
                np.abs(arrays["curve_xyz"]).max() > np.abs(arrays["curve_xyz_normalized"]).max()
            ),
        },
        "parameter_extraction_ok": n_param_ok,
        "geometry_reconstruction_ok": n_geom_ok,
        "topology_valid": topology["topology_valid"],
        "ablation_support": ABLATION_SUPPORT,
        "occ_backend": "OCP (cadquery-ocp) 7.8.1.1",
        "build_seconds": elapsed,
    }
    _write_json(out_dir / "metadata.json", metadata)

    return {
        "cad_id": cad_id,
        "split": split,
        "ok": True,
        "num_curves": data["num_curves"],
        "num_skipped_edges": data["num_skipped_edges"],
        "type_counts": type_counts,
        "param_ok": n_param_ok,
        "geom_ok": n_geom_ok,
        "topology_valid": topology["topology_valid"],
        "seconds": elapsed,
    }


def _worker(job: tuple[str, str, int, tuple[int, ...], bool]) -> dict:
    split, cad_id, n_sample, extra, overwrite = job
    try:
        return build_one(split, cad_id, n_sample, extra, overwrite)
    except Exception as exc:  # noqa: BLE001
        import traceback

        return {
            "cad_id": cad_id,
            "split": split,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(limit=6),
        }


def build_many(
    split: str,
    cad_ids: list[str],
    n_sample: int = N_SAMPLE_DEFAULT,
    extra_samples: tuple[int, ...] = N_SAMPLE_EXTRA,
    workers: int = 16,
    overwrite: bool = True,
) -> list[dict]:
    from concurrent.futures import ProcessPoolExecutor

    jobs = [(split, cid, n_sample, extra_samples, overwrite) for cid in cad_ids]
    if workers <= 1:
        return [_worker(j) for j in jobs]
    results: list[dict] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for res in pool.map(_worker, jobs, chunksize=1):
            results.append(res)
    return results
