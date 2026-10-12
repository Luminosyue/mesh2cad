#!/usr/bin/env python3
"""Exp1 post-hoc audits: per-part metrics, control-grid UV symmetry, worst-20, OOD.

Does NOT retrain. Loads best.pt from exp1_pointnet_recon/.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from freeform_patch_reconstruction_v1.exp1_pointnet_recon import (  # noqa: E402
    BSplineDataset,
    GRID,
    ReconModel,
    _basis_cache,
    collate,
    densify_poles,
    invert_norm,
)
from freeform_patch_reconstruction_v1.geom import chamfer_l1  # noqa: E402

DEFAULT_PACK = ROOT / "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1"
DEFAULT_EXP = ROOT / "ours3/freeform_patch_reconstruction_v1/exp1_pointnet_recon"

ORIENT_NAMES = (
    "identity",
    "flip_u",
    "flip_v",
    "flip_uv",
    "transpose",
    "transpose_flip_u",
    "transpose_flip_v",
    "transpose_flip_uv",
)


def orient_poles(poles: np.ndarray, name: str) -> np.ndarray:
    """poles: (4,4,3) → oriented copy."""
    p = poles
    if name == "identity":
        return p.copy()
    if name == "flip_u":
        return p[::-1, :, :].copy()
    if name == "flip_v":
        return p[:, ::-1, :].copy()
    if name == "flip_uv":
        return p[::-1, ::-1, :].copy()
    if name == "transpose":
        return np.transpose(p, (1, 0, 2)).copy()
    if name == "transpose_flip_u":
        return np.transpose(p, (1, 0, 2))[::-1, :, :].copy()
    if name == "transpose_flip_v":
        return np.transpose(p, (1, 0, 2))[:, ::-1, :].copy()
    if name == "transpose_flip_uv":
        return np.transpose(p, (1, 0, 2))[::-1, ::-1, :].copy()
    raise ValueError(name)


def ctrl_l1(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a - b).mean())


def symmetry_min_ctrl(pred: np.ndarray, gt: np.ndarray) -> tuple[float, float, str]:
    raw = ctrl_l1(pred, gt)
    best_name = "identity"
    best = raw
    for name in ORIENT_NAMES:
        v = ctrl_l1(pred, orient_poles(gt, name))
        if v < best:
            best = v
            best_name = name
    return raw, best, best_name


def patch_geometry_stats(sample_dir: Path) -> dict:
    meta = json.loads((sample_dir / "surface_meta.json").read_text())
    pts = np.load(sample_dir / "patch_points.npy").astype(np.float64)
    xyz = pts[:, :3]
    nrm = pts[:, 3:6]
    # PCA aspect: length/width of point cloud
    c = xyz.mean(0)
    X = xyz - c
    # covariance eig
    cov = X.T @ X / max(len(X), 1)
    eig = np.sort(np.linalg.eigvalsh(cov))[::-1]
    eig = np.maximum(eig, 1e-18)
    aspect = float(np.sqrt(eig[0] / eig[1]))  # length / width
    bbox = xyz.max(0) - xyz.min(0)
    bbox_sorted = np.sort(bbox)[::-1]
    bbox_aspect = float(bbox_sorted[0] / max(bbox_sorted[1], 1e-12))
    diag = float(np.linalg.norm(bbox))
    # normal variation: 1 - mean |n·mean_n|
    n = nrm / np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    mean_n = n.mean(0)
    mean_n = mean_n / max(np.linalg.norm(mean_n), 1e-12)
    normal_var = float(1.0 - np.mean(np.abs(n @ mean_n)))
    # boundary length approx
    bpath = sample_dir / "boundary_points.npy"
    if bpath.is_file():
        b = np.load(bpath)[:, :3]
        blen = float(np.linalg.norm(np.diff(b, axis=0), axis=1).sum())
    else:
        blen = float("nan")
    # curvature proxy: mean angle between neighbor normals in kNN-ish random pairs
    # use variance of normals as proxy already; also mean |cross|
    return {
        "degree_u": int(meta["degree_u"]),
        "degree_v": int(meta["degree_v"]),
        "num_poles_u": int(meta["num_poles_u"]),
        "num_poles_v": int(meta["num_poles_v"]),
        "area": float(meta.get("area", float("nan"))),
        "pca_aspect": aspect,
        "bbox_aspect": bbox_aspect,
        "diag": diag,
        "normal_var": normal_var,
        "boundary_length": blen,
        "canonical_fit_cd_rel": float(meta.get("canonical", {}).get("chamfer_rel", float("nan"))),
    }


def classify_failure(row: dict) -> str:
    """Heuristic failure labels for worst patches."""
    cd = row["chamfer_rel"]
    raw = row["ctrl_l1_raw"]
    sym = row["ctrl_l1_sym"]
    best_orient = row["best_orient"]
    pred_span = row.get("pred_span_rel", 1.0)
    gt_span = row.get("gt_span_rel", 1.0)
    center_err = row.get("center_err_rel", 0.0)
    scale_ratio = row.get("scale_ratio", 1.0)

    if cd < 0.05 and sym < 0.5 * raw and best_orient != "identity":
        if "transpose" in best_orient:
            return "U_V_SWAP"
        return "ORIENTATION_FLIP"
    if pred_span < 0.15 * max(gt_span, 1e-12) or pred_span < 0.05:
        return "SURFACE_COLLAPSE"
    if center_err > 0.35 and cd > 0.2:
        return "TRANSLATION_ERROR"
    if scale_ratio > 2.5 or scale_ratio < 0.4:
        return "SCALE_ERROR"
    # strip-like: high aspect + bad CD
    if row.get("pca_aspect", 1.0) > 30 and cd > 0.2:
        return "STRIP_DIRECTION_ERROR"
    if row.get("normal_var", 0.0) > 0.25 and cd > 0.2:
        return "HIGH_CURVATURE"
    if cd > 0.5 and raw > 1.0 and sym > 0.8 * raw:
        return "OUT_OF_DISTRIBUTION_SHAPE"
    # normal flip: CD medium but normal inconsistency already baked; keep OTHER if CD ok-ish
    if cd < 0.05 and raw > 2.0 and sym < 0.35 * raw:
        return "ORIENTATION_FLIP"
    if cd > 0.2:
        return "OUT_OF_DISTRIBUTION_SHAPE"
    return "OTHER"


def part_id_of(sid: str) -> str:
    return sid.split("__", 1)[0]


def summarize_group(vals: list[float]) -> dict:
    a = np.asarray(vals, dtype=np.float64)
    return {
        "n": int(len(a)),
        "mean": float(a.mean()) if len(a) else None,
        "median": float(np.median(a)) if len(a) else None,
        "p90": float(np.percentile(a, 90)) if len(a) else None,
        "p95": float(np.percentile(a, 95)) if len(a) else None,
        "max": float(a.max()) if len(a) else None,
    }


@torch.no_grad()
def run_inference(pack_dir: Path, ckpt_path: Path, device: torch.device):
    ds = BSplineDataset(pack_dir, "test", online=False, seed=0)
    loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0, collate_fn=collate)
    ckpt = torch.load(ckpt_path, map_location="cpu")
    model = ReconModel().to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    A = _basis_cache(device)

    rows = []
    for batch in loader:
        feats = batch["feats"].to(device)
        poles_gt = batch["poles"].to(device)
        gt_dense = batch["gt_dense"].to(device)
        centers = batch["center"].numpy()
        scales = batch["scale"].numpy()
        pred = model(feats)
        pred_dense = densify_poles(pred, A)
        for i, sid in enumerate(batch["sample_id"]):
            pg = poles_gt[i].cpu().numpy()
            pp = pred[i].cpu().numpy()
            gd = gt_dense[i].cpu().numpy()
            pd = pred_dense[i].cpu().numpy()
            c, s = centers[i], float(scales[i])
            gd_w = invert_norm(gd, c, s)
            pd_w = invert_norm(pd, c, s)
            diag = float(np.linalg.norm(gd_w.max(0) - gd_w.min(0)))
            cd = chamfer_l1(pd_w, gd_w)
            raw, sym, best_orient = symmetry_min_ctrl(pp, pg)
            # span / center / scale diagnostics in local frame
            gt_span = float(np.linalg.norm(gd.max(0) - gd.min(0)))
            pred_span = float(np.linalg.norm(pd.max(0) - pd.min(0)))
            center_err = float(np.linalg.norm(pd.mean(0) - gd.mean(0)))
            scale_ratio = pred_span / max(gt_span, 1e-12)
            gstats = patch_geometry_stats(pack_dir / "samples" / sid)
            row = {
                "sample_id": sid,
                "part_id": part_id_of(sid),
                "ctrl_l1_raw": raw,
                "ctrl_l1_sym": sym,
                "best_orient": best_orient,
                "chamfer_rel": cd / max(diag, 1e-12),
                "pred_span_rel": pred_span,
                "gt_span_rel": gt_span,
                "center_err_rel": center_err,
                "scale_ratio": scale_ratio,
                **gstats,
            }
            row["failure_type"] = classify_failure(row)
            rows.append(row)
    return rows


def per_part_table(rows: list[dict]) -> list[dict]:
    by = defaultdict(list)
    for r in rows:
        by[r["part_id"]].append(r)
    out = []
    for pid, xs in by.items():
        cds = np.array([x["chamfer_rel"] for x in xs])
        hds = np.array([x.get("hausdorff95_rel", np.nan) for x in xs])  # may be missing
        # recompute HD not stored; use placeholder from report if needed
        ctr = np.array([x["ctrl_l1_raw"] for x in xs])
        ctrs = np.array([x["ctrl_l1_sym"] for x in xs])
        out.append(
            {
                "part_id": pid,
                "n_patches": len(xs),
                "cd_mean": float(cds.mean()),
                "cd_median": float(np.median(cds)),
                "ctrl_l1_mean": float(ctr.mean()),
                "ctrl_l1_sym_mean": float(ctrs.mean()),
                "worst_cd": float(cds.max()),
                "worst_sample": xs[int(np.argmax(cds))]["sample_id"],
            }
        )
    out.sort(key=lambda x: -x["cd_mean"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK)
    ap.add_argument("--exp-dir", type=Path, default=DEFAULT_EXP)
    ap.add_argument("--device", type=str, default=None)
    args = ap.parse_args()

    device = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    out_dir = args.exp_dir / "audits"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Prefer re-inference for symmetry; also merge HD from report.json if present
    report = json.loads((args.exp_dir / "report.json").read_text())
    hd_map = {r["sample_id"]: r for r in report.get("per_sample_test", [])}

    print(f"device={device} loading {args.exp_dir / 'best.pt'}", flush=True)
    rows = run_inference(args.pack_dir, args.exp_dir / "best.pt", device)
    for r in rows:
        if r["sample_id"] in hd_map:
            r["hausdorff95_rel"] = hd_map[r["sample_id"]]["hausdorff95_rel"]
            r["ctrl_l1_report"] = hd_map[r["sample_id"]]["ctrl_l1"]

    # --- 1) per-part ---
    parts = []
    by = defaultdict(list)
    for r in rows:
        by[r["part_id"]].append(r)
    for pid, xs in by.items():
        cds = np.array([x["chamfer_rel"] for x in xs])
        hds = np.array([x["hausdorff95_rel"] for x in xs])
        ctr = np.array([x["ctrl_l1_raw"] for x in xs])
        parts.append(
            {
                "part_id": pid,
                "n_patches": len(xs),
                "cd_mean": float(cds.mean()),
                "cd_median": float(np.median(cds)),
                "hd95_median": float(np.median(hds)),
                "ctrl_l1_mean": float(ctr.mean()),
                "ctrl_l1_sym_mean": float(np.mean([x["ctrl_l1_sym"] for x in xs])),
                "worst_cd": float(cds.max()),
            }
        )
    parts.sort(key=lambda x: -x["cd_mean"])

    print("\n=== PER-PART TEST ===")
    print(f"{'part_id':<32} {'#patches':>8} {'CD_mean':>10} {'CD_med':>10} {'HD95':>10} {'ctrl_L1':>10} {'worst_CD':>10}")
    for p in parts:
        print(
            f"{p['part_id']:<32} {p['n_patches']:8d} {p['cd_mean']:10.4e} {p['cd_median']:10.4e} "
            f"{p['hd95_median']:10.4e} {p['ctrl_l1_mean']:10.4e} {p['worst_cd']:10.4e}"
        )

    # --- 2) symmetry audit ---
    raws = np.array([r["ctrl_l1_raw"] for r in rows])
    syms = np.array([r["ctrl_l1_sym"] for r in rows])
    orients = Counter(r["best_orient"] for r in rows)
    # among good-geometry patches
    good = [r for r in rows if r["chamfer_rel"] < 0.02]
    good_raw = np.array([r["ctrl_l1_raw"] for r in good]) if good else np.array([])
    good_sym = np.array([r["ctrl_l1_sym"] for r in good]) if good else np.array([])

    sym_audit = {
        "n": len(rows),
        "CTRL_L1_RAW_mean": float(raws.mean()),
        "CTRL_L1_RAW_median": float(np.median(raws)),
        "CTRL_L1_SYMMETRY_MIN_mean": float(syms.mean()),
        "CTRL_L1_SYMMETRY_MIN_median": float(np.median(syms)),
        "raw_over_sym_ratio_mean": float((raws / np.maximum(syms, 1e-12)).mean()),
        "best_orient_counts": dict(orients),
        "frac_non_identity_best": float(np.mean([r["best_orient"] != "identity" for r in rows])),
        "good_cd_lt_0.02": {
            "n": len(good),
            "CTRL_L1_RAW_mean": float(good_raw.mean()) if len(good_raw) else None,
            "CTRL_L1_SYMMETRY_MIN_mean": float(good_sym.mean()) if len(good_sym) else None,
        },
    }
    print("\n=== CONTROL-GRID SYMMETRY ===")
    print(json.dumps(sym_audit, indent=2))

    # --- 3) worst 20 ---
    worst = sorted(rows, key=lambda r: -r["chamfer_rel"])[:20]
    fail_counts = Counter(r["failure_type"] for r in worst)
    print("\n=== WORST 20 ===")
    for r in worst:
        print(
            f"{r['chamfer_rel']:.4e}  {r['failure_type']:<24} raw={r['ctrl_l1_raw']:.3f} "
            f"sym={r['ctrl_l1_sym']:.3f} orient={r['best_orient']:<18} "
            f"aspect={r['pca_aspect']:.1f}  {r['sample_id']}"
        )
    print("failure_type counts:", dict(fail_counts))

    # --- 4) OOD: train vs catastrophic test parts ---
    man = json.loads((args.pack_dir / "manifest.json").read_text())
    train_ids = [s["sample_id"] for s in man["samples"] if s["split"] == "train"]
    train_stats = [patch_geometry_stats(args.pack_dir / "samples" / sid) for sid in train_ids]
    bad_parts = {p["part_id"] for p in parts if p["cd_mean"] > 0.1}
    good_parts = {p["part_id"] for p in parts if p["cd_mean"] <= 0.1}
    bad_rows = [r for r in rows if r["part_id"] in bad_parts]
    good_rows = [r for r in rows if r["part_id"] in good_parts]

    def feat_summary(items, key):
        return summarize_group([float(x[key]) for x in items])

    ood = {
        "train": {k: feat_summary(train_stats, k) for k in (
            "pca_aspect", "bbox_aspect", "area", "normal_var", "boundary_length",
            "num_poles_u", "num_poles_v", "degree_u", "degree_v",
        )},
        "test_good_parts": {k: feat_summary(good_rows, k) for k in (
            "pca_aspect", "bbox_aspect", "area", "normal_var", "boundary_length",
            "num_poles_u", "num_poles_v", "degree_u", "degree_v", "chamfer_rel",
        )},
        "test_bad_parts": {k: feat_summary(bad_rows, k) for k in (
            "pca_aspect", "bbox_aspect", "area", "normal_var", "boundary_length",
            "num_poles_u", "num_poles_v", "degree_u", "degree_v", "chamfer_rel",
        )},
        "bad_part_ids": sorted(bad_parts),
        "good_part_ids": sorted(good_parts),
        "degree_uv_train": {
            f"{a}x{b}": c for (a, b), c in Counter((s["degree_u"], s["degree_v"]) for s in train_stats).items()
        },
        "degree_uv_bad": {
            f"{a}x{b}": c for (a, b), c in Counter((r["degree_u"], r["degree_v"]) for r in bad_rows).items()
        },
        "degree_uv_good": {
            f"{a}x{b}": c for (a, b), c in Counter((r["degree_u"], r["degree_v"]) for r in good_rows).items()
        },
        "poles_uv_train": {
            f"{a}x{b}": c
            for (a, b), c in Counter((s["num_poles_u"], s["num_poles_v"]) for s in train_stats).items()
        },
        "poles_uv_bad": {
            f"{a}x{b}": c
            for (a, b), c in Counter((r["num_poles_u"], r["num_poles_v"]) for r in bad_rows).items()
        },
        "poles_uv_good": {
            f"{a}x{b}": c
            for (a, b), c in Counter((r["num_poles_u"], r["num_poles_v"]) for r in good_rows).items()
        },
    }
    print("\n=== OOD ASPECT (median) ===")
    print(
        "train pca_aspect median:", ood["train"]["pca_aspect"]["median"],
        "p95:", ood["train"]["pca_aspect"]["p95"],
    )
    print(
        "test_good pca_aspect median:", ood["test_good_parts"]["pca_aspect"]["median"],
        "p95:", ood["test_good_parts"]["pca_aspect"]["p95"],
    )
    print(
        "test_bad  pca_aspect median:", ood["test_bad_parts"]["pca_aspect"]["median"],
        "p95:", ood["test_bad_parts"]["pca_aspect"]["p95"],
        "max:", ood["test_bad_parts"]["pca_aspect"]["max"],
    )

    # --- gates rename ---
    test_cd_mean = float(np.mean([r["chamfer_rel"] for r in rows]))
    test_cd_med = float(np.median([r["chamfer_rel"] for r in rows]))
    base = report["test"].get("baseline_mean_chamfer_rel_mean", 1.0)
    vs = test_cd_mean / max(base, 1e-12)
    part_macro = float(np.mean([p["cd_mean"] for p in parts]))
    gates = {
        "EXP1_RECON_MECHANISM": "PASS" if vs < 0.5 else "FAIL",
        "EXP1_MEDIAN_GEOMETRY": "PASS" if test_cd_med < 0.02 else "FAIL",
        "EXP1_BASELINE_IMPROVEMENT": "PASS" if vs < 0.85 else "FAIL",
        "EXP1_PART_GENERALIZATION": "PASS" if part_macro < 0.05 and max(p["cd_mean"] for p in parts) < 0.2 else "FAIL",
    }
    current = (
        "EXP1_PART_LEVEL_GENERALIZATION_FAIL"
        if gates["EXP1_PART_GENERALIZATION"] == "FAIL"
        and gates["EXP1_RECON_MECHANISM"] == "PASS"
        else ("EXP1_RECON_PASS" if all(v == "PASS" for v in gates.values()) else "EXP1_RECON_FAIL")
    )
    gates["CURRENT_GATE"] = current
    print("\n=== GATES ===")
    print(json.dumps(gates, indent=2))

    # write artifacts
    (out_dir / "per_part_test.json").write_text(json.dumps(parts, indent=2) + "\n")
    (out_dir / "symmetry_audit.json").write_text(json.dumps(sym_audit, indent=2) + "\n")
    (out_dir / "worst20.json").write_text(json.dumps(worst, indent=2) + "\n")
    (out_dir / "ood_distribution.json").write_text(json.dumps(ood, indent=2) + "\n")
    (out_dir / "per_sample_audit.json").write_text(json.dumps(rows, indent=2) + "\n")

    lines = [
        "# Exp1 Failure / Symmetry / Part Audit",
        "",
        "## CURRENT_GATE",
        f"- **{current}**",
        "",
        "### Sub-gates",
        *[f"- {k} = **{v}**" for k, v in gates.items() if k != "CURRENT_GATE"],
        "",
        f"- test CD mean/median = `{test_cd_mean:.4e}` / `{test_cd_med:.4e}`",
        f"- part-macro CD = `{part_macro:.4e}`",
        f"- vs mean-baseline = `{vs:.4f}`",
        "",
        "## 1. Per-part test metrics",
        "",
        "| part_id | #patches | CD mean | CD median | HD95 | ctrl L1 | worst CD |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for p in parts:
        lines.append(
            f"| `{p['part_id']}` | {p['n_patches']} | {p['cd_mean']:.4e} | {p['cd_median']:.4e} | "
            f"{p['hd95_median']:.4e} | {p['ctrl_l1_mean']:.4e} | {p['worst_cd']:.4e} |"
        )
    lines += [
        "",
        "## 2. Control-grid symmetry",
        "",
        f"- CTRL_L1_RAW mean/median = **{sym_audit['CTRL_L1_RAW_mean']:.4f}** / **{sym_audit['CTRL_L1_RAW_median']:.4f}**",
        f"- CTRL_L1_SYMMETRY_MIN mean/median = **{sym_audit['CTRL_L1_SYMMETRY_MIN_mean']:.4f}** / **{sym_audit['CTRL_L1_SYMMETRY_MIN_median']:.4f}**",
        f"- frac best≠identity = **{sym_audit['frac_non_identity_best']:.3f}**",
        f"- among CD<0.02: raw={sym_audit['good_cd_lt_0.02']['CTRL_L1_RAW_mean']}, "
        f"sym={sym_audit['good_cd_lt_0.02']['CTRL_L1_SYMMETRY_MIN_mean']}",
        f"- best_orient_counts = `{json.dumps(sym_audit['best_orient_counts'])}`",
        "",
        "## 3. Worst-20 failure types",
        "",
        f"- counts = `{json.dumps(dict(fail_counts))}`",
        "",
        "| CD_rel | type | raw | sym | orient | aspect | sample |",
        "|---:|---|---:|---:|---|---:|---|",
    ]
    for r in worst:
        lines.append(
            f"| {r['chamfer_rel']:.4e} | {r['failure_type']} | {r['ctrl_l1_raw']:.3f} | "
            f"{r['ctrl_l1_sym']:.3f} | {r['best_orient']} | {r['pca_aspect']:.1f} | `{r['sample_id']}` |"
        )
    lines += [
        "",
        "## 4. Train vs bad-part distribution (PCA aspect = length/width)",
        "",
        f"- train median/p95 aspect = **{ood['train']['pca_aspect']['median']:.2f}** / "
        f"**{ood['train']['pca_aspect']['p95']:.2f}**",
        f"- test good-parts median/p95 = **{ood['test_good_parts']['pca_aspect']['median']:.2f}** / "
        f"**{ood['test_good_parts']['pca_aspect']['p95']:.2f}**",
        f"- test bad-parts median/p95/max = **{ood['test_bad_parts']['pca_aspect']['median']:.2f}** / "
        f"**{ood['test_bad_parts']['pca_aspect']['p95']:.2f}** / **{ood['test_bad_parts']['pca_aspect']['max']:.2f}**",
        f"- bad parts = `{ood['bad_part_ids']}`",
        f"- degree_uv train = `{ood['degree_uv_train']}`",
        f"- degree_uv bad = `{ood['degree_uv_bad']}`",
        f"- poles_uv train top = `{dict(sorted(ood['poles_uv_train'].items(), key=lambda kv: -kv[1])[:5])}`",
        f"- poles_uv bad = `{ood['poles_uv_bad']}`",
        "",
        "Interpretation: reconstruction mechanism works on the dominant strip mass; "
        "held-out small parts catastrophically fail and dominate part-macro. "
        "High raw ctrl L1 with good median CD is consistent with UV orientation ambiguity.",
        "",
    ]
    (out_dir / "AUDIT.md").write_text("\n".join(lines) + "\n")

    # update top-level REPORT.md gates
    report_md = args.exp_dir / "REPORT.md"
    report_md.write_text(
        "\n".join(
            [
                "# Exp1 PointNet Surface-only Reconstruction (4×4 LSQ)",
                "",
                f"- CURRENT_GATE = **{current}**",
                f"- EXP1_RECON_MECHANISM = **{gates['EXP1_RECON_MECHANISM']}**",
                f"- EXP1_MEDIAN_GEOMETRY = **{gates['EXP1_MEDIAN_GEOMETRY']}**",
                f"- EXP1_BASELINE_IMPROVEMENT = **{gates['EXP1_BASELINE_IMPROVEMENT']}**",
                f"- EXP1_PART_GENERALIZATION = **{gates['EXP1_PART_GENERALIZATION']}**",
                f"- test chamfer_rel mean/median = **{test_cd_mean:.4e}** / **{test_cd_med:.4e}**",
                f"- test part-macro chamfer_rel = **{part_macro:.4e}**",
                f"- CTRL_L1_RAW mean = **{sym_audit['CTRL_L1_RAW_mean']:.4f}**",
                f"- CTRL_L1_SYMMETRY_MIN mean = **{sym_audit['CTRL_L1_SYMMETRY_MIN_mean']:.4f}**",
                f"- vs mean-baseline ratio = **{vs:.4f}**",
                "",
                "See `audits/AUDIT.md` for per-part / symmetry / worst-20 / OOD.",
                "",
            ]
        )
    )
    # patch report.json gates
    report["CURRENT_GATE"] = current
    report["sub_gates"] = {k: v for k, v in gates.items() if k != "CURRENT_GATE"}
    report["symmetry_audit_summary"] = {
        "CTRL_L1_RAW_mean": sym_audit["CTRL_L1_RAW_mean"],
        "CTRL_L1_SYMMETRY_MIN_mean": sym_audit["CTRL_L1_SYMMETRY_MIN_mean"],
    }
    (args.exp_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nwrote {out_dir / 'AUDIT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
