"""Pack all Track-B curves into a single cache for fast encoder training.

Reads ours3/curve_token_data_v1 (read-only). Writes only under ENCODER_OUTPUT_ROOT/cache.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .config import (
    CACHE_DIR,
    CURVE_TYPE_IDS,
    DATA_ROOT,
    N_SAMPLE,
    PARAM_DIM,
    SPLITS_DIR,
)


def _arc_deg(curve: dict) -> float:
    if curve.get("is_closed"):
        return 360.0
    u0, u1 = float(curve["u_start"]), float(curve["u_end"])
    du = abs(u1 - u0)
    ct = curve["curve_type"]
    if ct in ("CIRCLE", "ELLIPSE"):
        return float(np.degrees(du) % 360.0)
    # For LINE/BSPLINE store NaN; buckets only apply to circular types.
    return float("nan")


def _pack_params(curve: dict) -> tuple[np.ndarray, np.ndarray]:
    """Return (param_vec[PARAM_DIM], param_mask[PARAM_DIM]) in normalized space."""
    vec = np.zeros(PARAM_DIM, dtype=np.float32)
    mask = np.zeros(PARAM_DIM, dtype=np.float32)
    p = curve["normalized_parameters"]
    ct = curve["curve_type"]
    if ct == "LINE":
        vec[0:3] = np.asarray(p["origin"], dtype=np.float32)
        vec[3:6] = np.asarray(p["direction"], dtype=np.float32)
        mask[0:6] = 1.0
    elif ct == "CIRCLE":
        vec[0:3] = np.asarray(p["center"], dtype=np.float32)
        vec[3:6] = np.asarray(p["normal"], dtype=np.float32)
        vec[6] = float(p["radius"])
        mask[0:7] = 1.0
    elif ct == "ELLIPSE":
        vec[0:3] = np.asarray(p["center"], dtype=np.float32)
        vec[3:6] = np.asarray(p["normal"], dtype=np.float32)
        vec[6:9] = np.asarray(p["major_axis"], dtype=np.float32)
        vec[9] = float(p["major_radius"])
        vec[10] = float(p["minor_radius"])
        mask[0:11] = 1.0
    # BSPLINE: param head unused in V1 (recon + type only)
    return vec, mask


def build_cache(splits_path: Path | None = None) -> Path:
    splits_path = splits_path or (SPLITS_DIR / "cad_level_splits.json")
    manifest = json.loads(splits_path.read_text())
    cads = manifest["cads"]

    xyz_list, tan_list = [], []
    type_ids, lengths, closed = [], [], []
    params, param_masks, arc_degs = [], [], []
    cad_indices, edge_ids, enc_splits, src_ids = [], [], [], []
    cad_keys = []

    split_to_id = {"train": 0, "val": 1, "test": 2}
    src_to_id = {"deepcad_train": 0, "fusion360_train": 1}

    for ci, cad in enumerate(cads):
        d = Path(cad["path"])
        z = np.load(d / "curve_samples.npz")
        curves = json.loads((d / "curves.json").read_text())["curves"]
        assert len(curves) == int(z["num_curves"][0])
        xyz = z["curve_xyz_normalized"].astype(np.float32)
        tan = z["curve_tangent"].astype(np.float32)
        if xyz.shape[1] != N_SAMPLE:
            raise RuntimeError(f"{d}: expected N_SAMPLE={N_SAMPLE}, got {xyz.shape}")
        n = xyz.shape[0]
        xyz_list.append(xyz)
        tan_list.append(tan)
        type_ids.append(z["curve_type_id"].astype(np.int32))
        lengths.append(z["curve_length_normalized"].astype(np.float32))
        closed.append(z["curve_is_closed"].astype(bool))
        for j, cu in enumerate(curves):
            vec, mask = _pack_params(cu)
            params.append(vec)
            param_masks.append(mask)
            arc_degs.append(_arc_deg(cu))
            cad_indices.append(ci)
            edge_ids.append(int(cu["edge_id"]))
            enc_splits.append(split_to_id[cad["encoder_split"]])
            src_ids.append(src_to_id[cad["split_source"]])
        cad_keys.append(f"{cad['split_source']}/{cad['cad_id']}")
        if (ci + 1) % 200 == 0:
            print(f"  cached {ci+1}/{len(cads)} CADs", flush=True)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / "curves_cache.npz"
    np.savez_compressed(
        out,
        xyz_n=np.concatenate(xyz_list, axis=0),
        tangent=np.concatenate(tan_list, axis=0),
        type_id=np.concatenate(type_ids, axis=0),
        length_n=np.concatenate(lengths, axis=0),
        is_closed=np.concatenate(closed, axis=0),
        params=np.stack(params, axis=0),
        param_mask=np.stack(param_masks, axis=0),
        arc_deg=np.asarray(arc_degs, dtype=np.float32),
        cad_index=np.asarray(cad_indices, dtype=np.int32),
        edge_id=np.asarray(edge_ids, dtype=np.int32),
        encoder_split=np.asarray(enc_splits, dtype=np.int32),
        source_id=np.asarray(src_ids, dtype=np.int32),
        n_sample=np.asarray([N_SAMPLE], dtype=np.int64),
        type_name_to_id=np.asarray(list(CURVE_TYPE_IDS.items()), dtype=object),
    )
    meta = {
        "n_curves": int(np.concatenate(type_ids).shape[0]),
        "n_cads": len(cads),
        "cad_keys": cad_keys,
        "split_to_id": split_to_id,
        "source_to_id": src_to_id,
        "data_root": str(DATA_ROOT),
        "splits_path": str(splits_path),
    }
    (CACHE_DIR / "curves_cache_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {out}  n_curves={meta['n_curves']}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=Path, default=None)
    args = ap.parse_args()
    build_cache(args.splits)


if __name__ == "__main__":
    main()
