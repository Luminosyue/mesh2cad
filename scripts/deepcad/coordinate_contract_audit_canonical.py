#!/usr/bin/env python3
"""Verify offline CAD canonical contract: features_canonical ↔ program_canonical.

Also checks that mm_plugin CAD path does not re-scale when already_canonical.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

from cad_canonical import (  # noqa: E402
    DEFAULT_TARGET_DIAGONAL,
    load_transform_json,
    transform_dsl,
)


def _bbox(pts: np.ndarray) -> dict:
    pts = np.asarray(pts, dtype=np.float64)
    mn, mx = pts.min(0), pts.max(0)
    return {
        "min": mn.tolist(),
        "max": mx.tolist(),
        "diagonal": float(np.linalg.norm(mx - mn)),
        "center": ((mn + mx) / 2).tolist(),
    }


def _mesh_bbox_from_dsl(dsl_text: str) -> dict | None:
    from edge_aware_cad_planner_v1.cad_dsl import execute_dsl
    import trimesh

    with tempfile.TemporaryDirectory(prefix="canon_audit_") as td:
        td = Path(td)
        step, stl = td / "t.step", td / "t.stl"
        try:
            execute_dsl(dsl_text, step, stl)
        except Exception as e:
            return {"error": str(e)}
        m = trimesh.load(str(stl), force="mesh")
        if isinstance(m, trimesh.Scene):
            m = m.dump(concatenate=True)
        if m is None or len(m.vertices) == 0:
            return {"error": "empty"}
        return _bbox(np.asarray(m.vertices))


def audit_one(sample_dir: Path, target_diagonal: float) -> dict:
    sid = sample_dir.name
    feats_c = np.load(sample_dir / "features_canonical.npy")
    dsl_c = (sample_dir / "program_canonical.dsl").read_text(encoding="utf-8")
    tf = load_transform_json(sample_dir / "coordinate_transform.json")

    feat_bb = _bbox(feats_c[:, :3])
    dsl_bb = _mesh_bbox_from_dsl(dsl_c)

    # round-trip DSL: T then T^-1 ≈ source
    src_dsl = (sample_dir / "program.dsl").read_text(encoding="utf-8")
    roundtrip = transform_dsl(transform_dsl(src_dsl, tf, inverse=False), tf, inverse=True)
    src_bb = _mesh_bbox_from_dsl(src_dsl)
    rt_bb = _mesh_bbox_from_dsl(roundtrip)

    min_abs = float(np.max(np.abs(feats_c[:, :3].min(0))))
    diag_err = abs(feat_bb["diagonal"] - target_diagonal) / target_diagonal
    feat_dsl_ok = False
    if dsl_bb and "diagonal" in dsl_bb and not dsl_bb.get("error"):
        feat_dsl_ok = abs(feat_bb["diagonal"] - dsl_bb["diagonal"]) / max(
            feat_bb["diagonal"], 1e-9
        ) < 0.03 and np.allclose(
            feat_bb["center"], dsl_bb["center"], atol=0.05 * target_diagonal
        )

    rt_ok = False
    if src_bb and rt_bb and "diagonal" in src_bb and "diagonal" in rt_bb:
        if not src_bb.get("error") and not rt_bb.get("error"):
            rt_ok = abs(src_bb["diagonal"] - rt_bb["diagonal"]) / max(
                src_bb["diagonal"], 1e-9
            ) < 0.02

    # Simulate mm_plugin: already_canonical → no extra scale
    extent = feats_c[:, :3].max(0) - feats_c[:, :3].min(0)
    would_be_scale = target_diagonal / float(np.linalg.norm(extent))
    plugin_no_rescale = abs(would_be_scale - 1.0) < 0.05  # diag already ~target

    return {
        "sample_id": sid,
        "scale": tf.scale,
        "translation": tf.translation,
        "features_canonical_bbox": feat_bb,
        "program_canonical_exec_bbox": dsl_bb,
        "features_min_abs_max": min_abs,
        "diag_err_vs_target": diag_err,
        "features_vs_dsl_canonical": feat_dsl_ok,
        "dsl_roundtrip_ok": rt_ok,
        "plugin_would_not_need_rescale": plugin_no_rescale,
        "pass": bool(
            feat_dsl_ok and rt_ok and min_abs < 1e-3 and diag_err < 0.05 and plugin_no_rescale
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--train-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/train",
    )
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--target-diagonal", type=float, default=DEFAULT_TARGET_DIAGONAL)
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT
        / "ours3/deepcad_train100_val_decode/coordinate_contract_audit_canonical.json",
    )
    args = ap.parse_args()

    dirs = [
        p
        for p in sorted(args.train_dir.iterdir())
        if (p / "features_canonical.npy").exists()
        and (p / "program_canonical.dsl").exists()
        and (p / "coordinate_transform.json").exists()
    ]
    rng = random.Random(args.seed)
    rng.shuffle(dirs)
    dirs = dirs[: args.n]

    rows = []
    for d in dirs:
        print(f"audit {d.name} ...", flush=True)
        rows.append(audit_one(d, args.target_diagonal))

    n_pass = sum(1 for r in rows if r["pass"])
    summary = {
        "n": len(rows),
        "n_pass": n_pass,
        "contract_verdict": "PASS" if n_pass == len(rows) and rows else "FAIL",
        "target_diagonal": args.target_diagonal,
        "note": (
            "Offline T applied to both features and DSL; mm_plugin must not re-scale. "
            "PASS requires features_canonical bbox ≈ program_canonical exec bbox, "
            "min≈0, diag≈target, and DSL T∘T^-1 roundtrip."
        ),
    }
    out = {"summary": summary, "per_sample": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    md = args.out.with_suffix(".md")
    lines = [
        "# Canonical coordinate contract audit",
        "",
        f"**Verdict:** `{summary['contract_verdict']}` ({n_pass}/{len(rows)} pass)",
        "",
        "| sample_id | scale | feat_diag | dsl_diag | min≈0 | feat≈dsl | roundtrip | pass |",
        "|---|---:|---:|---:|:---:|:---:|:---:|:---:|",
    ]
    for r in rows:
        dsl_d = r["program_canonical_exec_bbox"].get("diagonal")
        dsl_s = f"{dsl_d:.4f}" if isinstance(dsl_d, float) else "ERR"
        lines.append(
            f"| {r['sample_id']} | {r['scale']:.3f} | {r['features_canonical_bbox']['diagonal']:.4f} | "
            f"{dsl_s} | {'Y' if r['features_min_abs_max'] < 1e-3 else 'n'} | "
            f"{'Y' if r['features_vs_dsl_canonical'] else 'n'} | "
            f"{'Y' if r['dsl_roundtrip_ok'] else 'n'} | "
            f"{'Y' if r['pass'] else 'n'} |"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {args.out}\nwrote {md}")
    return 0 if summary["contract_verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
