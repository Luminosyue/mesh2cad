#!/usr/bin/env python3
"""Step 5: export the canonical Curve Token training format.

Record schema (see ``schema.json``)::

    {
      "curve_token_input": {"xyz_local": [32,3], "tangent": [32,3],
                            "s": [32], "log_length": float},
      "supervision": {"type": "CIRCLE",
                      "params": {...type-specific, curve-local...},
                      "samples": [32,3]},
      "ref": {"dataset": ..., "sample_id": ..., "edge_id": ...}
    }

Bulk storage is npz (float32) because JSON for 172k curves is ~1 GB; the
``*_preview.jsonl`` files carry the literal nested form for inspection and for
downstream LLM prompt construction.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_token_head_v1.config import (  # noqa: E402
    BACKBONE,
    BSPLINE_DEGREES,
    CACHE_DIR,
    EXPORT_DIR,
    ID_TO_TYPE,
    SCHEMA_VERSION,
    SPLIT_NAME,
)
from curve_token_head_v1.dataset import CurveTokenDataset  # noqa: E402

SPLITS = ("train", "val", "test")


def _params_dict(ctype: str, ds: CurveTokenDataset, i: int) -> dict:
    if ctype == "LINE":
        v = ds.line[i]
        return {
            "origin": v[0:3].round(6).tolist(),
            "direction": v[3:6].round(6).tolist(),
            "length": float(round(float(v[6]), 6)),
        }
    if ctype == "CIRCLE":
        v = ds.circle[i]
        return {
            "center": v[0:3].round(6).tolist(),
            "normal": v[3:6].round(6).tolist(),
            "radius": float(round(float(v[6]), 6)),
            "start_angle_cos_sin": v[7:9].round(6).tolist(),
            "end_angle_cos_sin": v[9:11].round(6).tolist(),
            "span_frac": float(round(float(v[11]), 6)),
        }
    if ctype == "ELLIPSE":
        v = ds.ellipse[i]
        return {
            "center": v[0:3].round(6).tolist(),
            "major_axis": v[3:6].round(6).tolist(),
            "minor_axis": v[6:9].round(6).tolist(),
            "normal": v[9:12].round(6).tolist(),
            "major_radius": float(round(float(v[12]), 6)),
            "minor_radius": float(round(float(v[13]), 6)),
            "start_angle_cos_sin": v[14:16].round(6).tolist(),
            "span_frac": float(round(float(v[16]), 6)),
        }
    if ctype == "BSPLINE":
        cls = int(ds.bs_degree[i])
        return {
            "degree": BSPLINE_DEGREES[cls] if cls >= 0 else None,
            "num_control_points": int(round(float(np.exp(ds.bs_logncp[i, 0])))),
            "control_points": "not_regressed (variable length, P95=34, max=95)",
        }
    raise ValueError(ctype)


def export_split(split: str, n_preview: int) -> dict:
    ds = CurveTokenDataset(split)
    base = ds.base
    n = len(ds)
    refs = base.meta["refs"]
    assert len(refs) == n, f"{len(refs)} refs vs {n} curves"

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    npz_path = EXPORT_DIR / f"{SPLIT_NAME}_{split}_curve_tokens.npz"
    np.savez_compressed(
        npz_path,
        xyz_local=base.xyz_local.astype(np.float32),
        tangent=base.tangent.astype(np.float32),
        s=base.s.astype(np.float32),
        log_length=base.log_len.astype(np.float32),
        curve_scale=base.curve_scale.astype(np.float32),
        type_id=base.type_id.astype(np.int64),
        samples=base.xyz_local.astype(np.float32),
        line_param=ds.line,
        circle_param=ds.circle,
        ellipse_param=ds.ellipse,
        bspline_degree_class=ds.bs_degree,
        bspline_logncp=ds.bs_logncp,
    )

    preview_path = EXPORT_DIR / f"{SPLIT_NAME}_{split}_preview.jsonl"
    # stratified preview: cycle through the four types
    by_type: dict[int, list[int]] = {}
    for i, t in enumerate(base.type_id.tolist()):
        by_type.setdefault(int(t), []).append(i)
    picks: list[int] = []
    per = max(n_preview // max(len(by_type), 1), 1)
    for t in sorted(by_type):
        picks.extend(by_type[t][:per])

    with preview_path.open("w", encoding="utf-8") as fh:
        for i in picks:
            ctype = ID_TO_TYPE[int(base.type_id[i])]
            rec = {
                "curve_token_input": {
                    "xyz_local": base.xyz_local[i].round(6).tolist(),
                    "tangent": base.tangent[i].round(6).tolist(),
                    "s": base.s[i].reshape(-1).round(6).tolist(),
                    "log_length": float(round(float(base.log_len[i, 0]), 6)),
                },
                "supervision": {
                    "type": ctype,
                    "params": _params_dict(ctype, ds, i),
                    "samples": base.xyz_local[i].round(6).tolist(),
                },
                "ref": {
                    "dataset": refs[i]["dataset"],
                    "sample_id": refs[i]["sample_id"],
                    "edge_id": refs[i]["edge_id"],
                    "curve_scale": float(round(float(base.curve_scale[i]), 6)),
                },
            }
            fh.write(json.dumps(rec) + "\n")

    stat = {
        "split": split,
        "n_curves": n,
        "n_cad": base.meta["n_cad"],
        "type_counts": base.type_counts,
        "npz": str(npz_path.relative_to(ROOT)),
        "preview_jsonl": str(preview_path.relative_to(ROOT)),
        "n_preview": len(picks),
    }
    print(f"[export] {split}: {n} curves → {npz_path.name}", flush=True)
    return stat


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--splits", nargs="+", default=list(SPLITS))
    ap.add_argument("--n-preview", type=int, default=64)
    args = ap.parse_args()

    if not (CACHE_DIR / f"frozen_v1_train.npz").is_file():
        raise SystemExit(f"missing baseline cache under {CACHE_DIR}")

    stats = [export_split(s, args.n_preview) for s in args.splits]
    schema = {
        "schema_version": SCHEMA_VERSION,
        "split": SPLIT_NAME,
        "backbone": BACKBONE,
        "frame": "curve-local: p_local = (p_object_normalized - centroid) / max_bbox_extent",
        "curve_token_input": {
            "xyz_local": "[32,3] curve-local sampled points",
            "tangent": "[32,3] unit tangents",
            "s": "[32] normalized arc-length progress in [0,1]",
            "log_length": "log(polyline length in object-normalized units + 1e-6)",
        },
        "supervision": {
            "type": ["LINE", "CIRCLE", "ELLIPSE", "BSPLINE"],
            "params_frame": "curve-local (centers/radii divided by curve_scale, "
            "directions unchanged, angles as cos/sin pairs)",
            "LINE": ["origin[3]", "direction[3]", "length"],
            "CIRCLE": [
                "center[3]",
                "normal[3]",
                "radius",
                "start_angle_cos_sin[2]",
                "end_angle_cos_sin[2]",
                "span_frac",
            ],
            "ELLIPSE": [
                "center[3]",
                "major_axis[3]",
                "minor_axis[3]",
                "normal[3]",
                "major_radius",
                "minor_radius",
                "start_angle_cos_sin[2]",
                "span_frac",
            ],
            "BSPLINE": ["degree (6-way class over 3..8)", "num_control_points (log-regressed)"],
            "samples": "[32,3] curve-local points = Chamfer reconstruction target",
        },
        "splits": stats,
    }
    out = EXPORT_DIR / "schema.json"
    out.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"[export] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
