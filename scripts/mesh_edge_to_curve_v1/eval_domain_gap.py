#!/usr/bin/env python3
"""Steps 6.1A / 6.2 / 6.3: paired B-Rep vs mesh-edge evaluation of a frozen model.

Both arms use the *same* curves and the *same* checkpoint; only the 32 input points
differ (exact B-Rep samples vs oracle-grouped mesh sharp-edge samples). Parameter
targets are rebuilt in each arm's own curve-local frame, so the errors are
comparable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_token_head_v1.config import EXPERIMENTS, PRIMARY_TYPES  # noqa: E402
from curve_token_head_v1.metrics import _stats, evaluate_model  # noqa: E402
from curve_token_head_v1.models import build_model  # noqa: E402
from mesh_edge_to_curve_v1.config import (  # noqa: E402
    CACHE_DIR,
    HEAD_RUNS,
    RUNS_DIR,
    SCHEMA_VERSION,
    SPLIT_NAME,
)


# Three arms isolate the two sources of mesh degradation:
#   brep     exact B-Rep points + exact OCC tangents  (training distribution)
#   brep_fd  exact B-Rep points + finite-difference tangents  (tangent estimation only)
#   mesh     mesh sharp-edge points + finite-difference tangents  (full mesh path)
ARMS = {
    "brep": ("brep", "brep_tangent_occ"),
    "brep_fd": ("brep", "brep_tangent_fd"),
    "mesh": ("mesh", "mesh_tangent_fd"),
}


class ArmDataset(torch.utils.data.Dataset):
    """One arm of the paired cache, shaped like a curve_token_head_v1 batch."""

    def __init__(self, npz: dict, arm: str):
        self.arm = arm
        prefix, tan_key = ARMS[arm]
        self.xyz = npz[f"{prefix}_xyz_local"]
        self.tan = npz[tan_key]
        self.log_len = npz[f"{prefix}_log_len"]
        self.s = npz[f"{prefix}_s"]
        self.type_id = npz["type_id"]
        self.line = npz[f"{prefix}_line_param"]
        self.circle = npz[f"{prefix}_circle_param"]
        self.ellipse = npz[f"{prefix}_ellipse_param"]
        self.deg = npz[f"{prefix}_bspline_degree"]
        self.ncp = npz[f"{prefix}_bspline_logncp"]
        self.poly_len = np.exp(self.log_len[:, 0]).astype(np.float32)
        line_lens = self.poly_len[self.type_id == 0]
        self.line_length_p90 = float(np.percentile(line_lens, 90)) if line_lens.size else 0.0

    def __len__(self) -> int:
        return len(self.type_id)

    def __getitem__(self, i: int) -> dict:
        feats = np.concatenate([self.xyz[i], self.tan[i], self.s[i]], axis=-1).astype(
            np.float32
        )
        return {
            "shape_feats": torch.from_numpy(feats),
            "scale_feat": torch.from_numpy(self.log_len[i]),
            "xyz_target": torch.from_numpy(self.xyz[i]),
            "type_id": torch.tensor(int(self.type_id[i]), dtype=torch.long),
            "poly_len": torch.tensor(self.poly_len[i], dtype=torch.float32),
            "line_param": torch.from_numpy(self.line[i]),
            "circle_param": torch.from_numpy(self.circle[i]),
            "ellipse_param": torch.from_numpy(self.ellipse[i]),
            "bspline_degree": torch.tensor(int(self.deg[i]), dtype=torch.long),
            "bspline_logncp": torch.from_numpy(self.ncp[i]),
        }


def collate(batch: list[dict]) -> dict:
    return {k: torch.stack([b[k] for b in batch], 0) for k in batch[0]}


def input_difference(npz: dict) -> dict:
    """Step 6.2: how the mesh input differs from the exact B-Rep input."""
    g = npz["brep_xyz_canon"].astype(np.float64)
    q = npz["mesh_xyz_canon"].astype(np.float64)
    t = npz["type_id"]
    gt_tan = npz["brep_tangent_occ"].astype(np.float64)
    mesh_tan = npz["mesh_tangent_fd"].astype(np.float64)

    def spacing_cv(p: np.ndarray) -> np.ndarray:
        seg = np.linalg.norm(np.diff(p, axis=1), axis=-1)
        mean = seg.mean(axis=1)
        return seg.std(axis=1) / np.where(mean < 1e-12, 1.0, mean)

    # position: distance from each mesh point to the exact GT polyline
    a, b = g[:, :-1, :], g[:, 1:, :]
    ab = b - a
    denom = (ab * ab).sum(-1)
    denom = np.where(denom < 1e-18, 1.0, denom)
    ap = q[:, :, None, :] - a[:, None, :, :]
    tt = np.clip((ap * ab[:, None, :, :]).sum(-1) / denom[:, None, :], 0.0, 1.0)
    proj = a[:, None, :, :] + tt[..., None] * ab[:, None, :, :]
    dev = np.linalg.norm(q[:, :, None, :] - proj, axis=-1).min(axis=-1)

    cos = np.abs((gt_tan * mesh_tan).sum(-1)).clip(0.0, 1.0)
    ang = np.degrees(np.arccos(cos))

    out = {}
    for tid, name in enumerate(PRIMARY_TYPES):
        m = t == tid
        if not m.any():
            continue
        out[name] = {
            "n": int(m.sum()),
            "position_dev_canonical": _stats(dev[m].max(axis=1)),
            "tangent_angle_deg": _stats(ang[m].mean(axis=1)),
            "spacing_cv_gt": _stats(spacing_cv(g[m])),
            "spacing_cv_mesh": _stats(spacing_cv(q[m])),
            "n_mesh_points": _stats(npz["n_mesh_points"][m].astype(np.float64)),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split", default="test")
    ap.add_argument("--exp", default="D1", choices=sorted(EXPERIMENTS))
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--batch-size", type=int, default=256)
    args = ap.parse_args()

    npz_path = CACHE_DIR / f"{SPLIT_NAME}_{args.split}_mesh_oracle.npz"
    meta_path = CACHE_DIR / f"{SPLIT_NAME}_{args.split}_mesh_oracle_meta.json"
    if not npz_path.is_file():
        raise SystemExit(f"missing {npz_path}; run build_oracle_dataset.py first")
    npz = dict(np.load(npz_path))
    build_meta = json.loads(meta_path.read_text(encoding="utf-8"))

    spec = EXPERIMENTS[args.exp]
    device = torch.device(args.device)
    arms = {a: ArmDataset(npz, a) for a in ARMS}
    loaders = {
        a: torch.utils.data.DataLoader(
            d, batch_size=args.batch_size, shuffle=False, collate_fn=collate
        )
        for a, d in arms.items()
    }

    per_seed: dict[int, dict] = {}
    for seed in args.seeds:
        ckpt_path = HEAD_RUNS / f"{args.exp}_{SPLIT_NAME}_seed{seed}" / "best.pt"
        if not ckpt_path.is_file():
            print(f"[skip] no checkpoint {ckpt_path}", flush=True)
            continue
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
        model = build_model(spec).to(device)
        model.load_state_dict(ckpt["model"])
        res = {}
        for arm, loader in loaders.items():
            res[arm] = evaluate_model(
                model, loader, device, spec, arms[arm].line_length_p90
            )
        per_seed[seed] = res
        print(
            f"[{args.exp} seed{seed}] macroF1 "
            + " ".join(f"{a}={res[a]['macro_f1']:.4f}" for a in ARMS),
            flush=True,
        )
    if not per_seed:
        raise SystemExit("no checkpoints evaluated")

    def agg(arm: str, path: tuple[str, ...]):
        vals = []
        for r in per_seed.values():
            cur = r[arm]
            for p in path:
                cur = (cur or {}).get(p) if isinstance(cur, dict) else None
            if cur is not None:
                vals.append(float(cur))
        if not vals:
            return None
        return {"mean": float(np.mean(vals)), "std": float(np.std(vals)), "n_seeds": len(vals)}

    cls_keys = ["macro_f1", "balanced_accuracy"] + [f"{t}_f1" for t in PRIMARY_TYPES]
    param_keys = [
        ("recon_chamfer", "median"),
        ("params", "line_dir_deg", "median"),
        ("params", "line_len_rel", "median"),
        ("params", "circle_normal_deg", "median"),
        ("params", "circle_radius_rel", "median"),
        ("params", "ellipse_major_axis_deg", "median"),
        ("params", "bspline_degree_correct", "mean"),
        ("params", "bspline_ncp_rel", "median"),
    ]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "split": args.split,
        "exp": args.exp,
        "seeds": sorted(per_seed),
        "n_curves_evaluated": int(len(arms["mesh"])),
        "build_meta": {
            k: build_meta[k]
            for k in ("oracle", "mesh_derived", "totals", "n_curves_total",
                      "n_curves_recovered", "coverage_by_type")
        },
        "input_difference": input_difference(npz),
        "arms": {a: {"xyz": v[0], "tangent": v[1]} for a, v in ARMS.items()},
        "classification": {k: {arm: agg(arm, (k,)) for arm in ARMS} for k in cls_keys},
        "geometry": {"/".join(p): {arm: agg(arm, p) for arm in ARMS} for p in param_keys},
        "per_seed": {
            str(s): {arm: {k: r[arm][k] for k in cls_keys} for arm in ARMS}
            for s, r in per_seed.items()
        },
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    out = RUNS_DIR / f"domain_gap_{args.exp}_{args.split}.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"[eval] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
