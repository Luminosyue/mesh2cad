#!/usr/bin/env python3
"""Step 6.1A: build the oracle-grouped mesh-edge Curve Token dataset.

For every B-Rep curve in a split, gather the mesh sharp-edge segments that belong
to it (oracle assignment), order them along the curve, resample to 32 points, and
store both the mesh-derived and the B-Rep inputs in the same canonical frame so
the two can be compared pairwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_encoder_baseline_v1.dataset import _normalized_s  # noqa: E402
from curve_encoder_scale_curvature_v1.dataset import curve_local_frame  # noqa: E402
from curve_token_head_v1.config import (  # noqa: E402
    CIRCLE_DIM,
    ELLIPSE_DIM,
    LINE_DIM,
    TYPE_TO_ID,
)
from curve_token_head_v1.dataset import pack_params  # noqa: E402
from mesh_edge_to_curve_v1.config import (  # noqa: E402
    ASSIGN_TOL_FRAC,
    CACHE_DIR,
    CANON_DIAGONAL,
    CURVE_DATA_ROOT,
    N_POINTS,
    PACK_ROOT,
    SCHEMA_VERSION,
    SPLIT_DIR,
    SPLIT_NAME,
)
from mesh_edge_to_curve_v1.grouping import (  # noqa: E402
    assign_segments,
    build_curve_polyline,
    resample_polyline,
    tangents_from_points,
)

# curve_samples.npz stores the OCC curve-type id; map it to our 4 primary types.
OCC_ID_TO_TYPE = {0: "LINE", 1: "CIRCLE", 2: "ELLIPSE", 3: "BSPLINE"}


def _canonical(sample_dir: Path) -> tuple[float, np.ndarray]:
    meta = json.loads((sample_dir / "metadata.json").read_text(encoding="utf-8"))
    c = meta["canonical"]
    return float(c["scale"]), np.asarray(c["translation"], dtype=np.float64)


def process_cad(row: dict) -> tuple[list[dict], dict]:
    pack_dir = PACK_ROOT[row["dataset"]] / row["sample_id"]
    curve_dir = CURVE_DATA_ROOT / row["cad_dir"]
    mesh_npz = pack_dir / "mesh_sharp_edges.npz"
    if not mesh_npz.is_file():
        return [], {"missing_mesh": 1}

    scale_c, trans_c = _canonical(pack_dir)
    mz = np.load(mesh_npz)
    seg_v0 = mz["v0"].astype(np.float64)
    seg_v1 = mz["v1"].astype(np.float64)

    z32 = np.load(curve_dir / "curve_samples.npz")
    z64 = np.load(curve_dir / "curve_samples_64.npz")
    curves = json.loads((curve_dir / "curves.json").read_text(encoding="utf-8"))["curves"]
    by_edge = {int(c["edge_id"]): c for c in curves}
    n_curves = int(z32["num_curves"][0])

    # B-Rep dihedral per topo edge: an edge below the sharp threshold cannot appear
    # in the mesh sharp-edge set at all, so it must not count as a detection miss.
    brep = json.loads((pack_dir / "brep_edges.json").read_text(encoding="utf-8"))
    is_sharp = {int(e["edge_index"]): bool(e.get("is_sharp", False)) for e in brep["edges"]}

    # GT reference polylines in WORLD coords (mesh segments are world too)
    gt_world = [np.asarray(z64["curve_xyz"][i], dtype=np.float64) for i in range(n_curves)]
    tol_world = ASSIGN_TOL_FRAC * CANON_DIAGONAL / scale_c
    owner = assign_segments(seg_v0, seg_v1, gt_world, tol_world)

    records = []
    stats = {"n_curves": n_curves, "n_segments": int(len(seg_v0)),
             "n_segments_assigned": int((owner >= 0).sum()), "recovered": 0}
    for i in range(n_curves):
        occ_id = int(z32["curve_type_id"][i])
        ctype = OCC_ID_TO_TYPE.get(occ_id)
        if ctype not in TYPE_TO_ID:
            continue
        sel = owner == i
        gt_xyz = np.asarray(z32["curve_xyz_normalized"][i], dtype=np.float64)
        rec = {
            "dataset": row["dataset"],
            "sample_id": row["sample_id"],
            "edge_id": int(z32["curve_edge_id"][i]),
            "local_index": i,
            "type": ctype,
            "brep_sharp": is_sharp.get(int(z32["curve_edge_id"][i]), False),
            "gt_xyz": gt_xyz,
            "gt_tangent": np.asarray(z32["curve_tangent"][i], dtype=np.float64),
            "n_mesh_segments": int(sel.sum()),
            "mesh_xyz": None,
        }
        poly = None
        if sel.any():
            poly = build_curve_polyline(
                seg_v0[sel], seg_v1[sel], gt_world[i], bool(z32["curve_is_closed"][i])
            )
        if poly is not None:
            mesh_canon = poly * scale_c + trans_c
            rec["mesh_xyz"] = resample_polyline(mesh_canon, N_POINTS)
            rec["n_mesh_points"] = int(len(poly))
            stats["recovered"] += 1
        rec["params"] = by_edge[rec["edge_id"]]
        records.append(rec)
    return records, stats


def _frame_targets(rec: dict, xyz: np.ndarray) -> dict:
    """Curve-local frame + per-type parameter targets for one input polyline."""
    local, centroid, scale = curve_local_frame(xyz)
    seg_len = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
    c = rec["params"]
    vec, deg_cls, log_ncp = pack_params(
        rec["type"],
        c["normalized_parameters"],
        np.asarray(xyz, dtype=np.float64).mean(axis=0),
        scale,
        seg_len,
        float(c["u_start"]),
        float(c["u_end"]),
    )
    return {
        "xyz_local": local.astype(np.float32),
        "log_len": np.float32(np.log(seg_len + 1e-6)),
        "param": vec,
        "degree_class": deg_cls,
        "log_ncp": np.float32(log_ncp),
        "curve_scale": np.float32(scale),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split", default="test", choices=["train", "val", "test"])
    ap.add_argument("--limit", type=int, default=0, help="debug: first N CADs only")
    args = ap.parse_args()

    rows = json.loads((SPLIT_DIR / f"{args.split}.json").read_text(encoding="utf-8"))
    if args.limit:
        rows = rows[: args.limit]

    all_recs: list[dict] = []
    agg = {"n_cad": 0, "n_curves": 0, "n_segments": 0, "n_segments_assigned": 0,
           "recovered": 0, "missing_mesh": 0}
    for n, row in enumerate(rows, 1):
        recs, st = process_cad(row)
        all_recs.extend(recs)
        agg["missing_mesh"] += st.get("missing_mesh", 0)
        for k in ("n_curves", "n_segments", "n_segments_assigned", "recovered"):
            agg[k] += st.get(k, 0)
        agg["n_cad"] += 1
        if n % 50 == 0 or n == len(rows):
            print(f"[build] {n}/{len(rows)} CADs, {len(all_recs)} curves, "
                  f"recovered={agg['recovered']}", flush=True)

    keep = [r for r in all_recs if r["mesh_xyz"] is not None]
    print(f"[build] recovered {len(keep)}/{len(all_recs)} curves", flush=True)

    def stack(key: str, recs: list[dict]) -> np.ndarray:
        return np.stack([r[key] for r in recs], 0).astype(np.float32)

    out: dict[str, np.ndarray] = {
        "type_id": np.asarray([TYPE_TO_ID[r["type"]] for r in keep], dtype=np.int64),
        "n_mesh_segments": np.asarray([r["n_mesh_segments"] for r in keep], dtype=np.int64),
        "n_mesh_points": np.asarray([r["n_mesh_points"] for r in keep], dtype=np.int64),
        "brep_xyz_canon": stack("gt_xyz", keep),
        # exact OCC tangent: what the model was trained on
        "brep_tangent_occ": stack("gt_tangent", keep),
        "mesh_xyz_canon": stack("mesh_xyz", keep),
    }
    for tag, src in (("brep", "gt_xyz"), ("mesh", "mesh_xyz")):
        frames = [_frame_targets(r, r[src]) for r in keep]
        out[f"{tag}_xyz_local"] = np.stack([f["xyz_local"] for f in frames], 0)
        out[f"{tag}_log_len"] = np.asarray(
            [[f["log_len"]] for f in frames], dtype=np.float32
        )
        out[f"{tag}_curve_scale"] = np.asarray(
            [f["curve_scale"] for f in frames], dtype=np.float32
        )
        # finite-difference tangent: what a mesh polyline can actually provide
        out[f"{tag}_tangent_fd"] = np.stack(
            [
                tangents_from_points(np.asarray(r[src], dtype=np.float64)).astype(np.float32)
                for r in keep
            ],
            0,
        )
        out[f"{tag}_s"] = np.stack(
            [
                _normalized_s(np.asarray(r[src], dtype=np.float32), "uniform_abscissa")
                for r in keep
            ],
            0,
        )
        for name, dim in (("line", LINE_DIM), ("circle", CIRCLE_DIM), ("ellipse", ELLIPSE_DIM)):
            arr = np.zeros((len(keep), dim), dtype=np.float32)
            for j, (r, f) in enumerate(zip(keep, frames)):
                if r["type"].lower() == name:
                    arr[j] = f["param"]
            out[f"{tag}_{name}_param"] = arr
        out[f"{tag}_bspline_degree"] = np.asarray(
            [f["degree_class"] for f in frames], dtype=np.int64
        )
        out[f"{tag}_bspline_logncp"] = np.asarray(
            [[f["log_ncp"]] for f in frames], dtype=np.float32
        )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    npz_path = CACHE_DIR / f"{SPLIT_NAME}_{args.split}_mesh_oracle.npz"
    np.savez_compressed(npz_path, **out)

    coverage = {}
    for t in sorted({r["type"] for r in all_recs}):
        of_type = [r for r in all_recs if r["type"] == t]
        sharp = [r for r in of_type if r["brep_sharp"]]
        rec_sharp = [r for r in sharp if r["mesh_xyz"] is not None]
        rec_all = [r for r in of_type if r["mesh_xyz"] is not None]
        coverage[t] = {
            "gt": len(of_type),
            "gt_brep_sharp": len(sharp),
            "recovered": len(rec_all),
            "rate_of_all": len(rec_all) / max(len(of_type), 1),
            # only B-Rep-sharp edges can appear in the mesh sharp set at all
            "rate_of_brep_sharp": len(rec_sharp) / max(len(sharp), 1),
            "recovered_but_not_brep_sharp": len(rec_all) - len(rec_sharp),
        }
    meta = {
        "schema_version": SCHEMA_VERSION,
        "split": args.split,
        "oracle": ["grouping (which curve a mesh segment belongs to)",
                   "ordering (projection onto the GT polyline)"],
        "mesh_derived": ["point positions", "point spacing", "tangents"],
        "assign_tol_canonical": ASSIGN_TOL_FRAC * CANON_DIAGONAL,
        "totals": agg,
        "n_curves_total": len(all_recs),
        "n_curves_recovered": len(keep),
        "coverage_by_type": coverage,
        "refs": [
            {k: r[k] for k in ("dataset", "sample_id", "edge_id", "local_index", "type")}
            for r in keep
        ],
        "npz": str(npz_path.relative_to(ROOT)),
    }
    meta_path = CACHE_DIR / f"{SPLIT_NAME}_{args.split}_mesh_oracle_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("totals", "n_curves_total",
                                           "n_curves_recovered", "coverage_by_type")},
                     indent=2))
    print(f"[build] wrote {npz_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
