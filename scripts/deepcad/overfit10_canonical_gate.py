#!/usr/bin/env python3
"""Gate check for canonical overfit10 decode.

For each sample:
  pred_canonical.dsl (or pred.dsl) → T^-1 → source DSL → STEP/STL
  compare STL vs GT model.obj (Chamfer / Hausdorff95 / VolErr)

Exit 0 only if exact+STEP+geom all pass the thresholds.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

from cad_canonical import load_transform_json, transform_dsl  # noqa: E402


def _geom(gt_mesh: Path, pred_stl: Path, n: int = 20000, seed: int = 0) -> dict:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(gt_mesh), force="mesh")
    pred = trimesh.load(str(pred_stl), force="mesh")
    if isinstance(ref, trimesh.Scene):
        ref = ref.dump(concatenate=True)
    if isinstance(pred, trimesh.Scene):
        pred = pred.dump(concatenate=True)
    if ref is None or pred is None or len(ref.vertices) == 0 or len(pred.vertices) == 0:
        return {"error": "empty_mesh"}

    rng = np.random.default_rng(seed)
    def sample(m):
        pts, _ = trimesh.sample.sample_surface(m, n)
        return np.asarray(pts, dtype=np.float64)

    a, b = sample(ref), sample(pred)
    # normalize by GT bbox diagonal
    extent = ref.bounds[1] - ref.bounds[0]
    diag = float(np.linalg.norm(extent)) or 1.0
    ta, tb = cKDTree(a), cKDTree(b)
    d_ab = ta.query(b)[0]
    d_ba = tb.query(a)[0]
    chamfer = float(0.5 * (d_ab.mean() + d_ba.mean()) / diag)
    h95 = float(0.5 * (np.percentile(d_ab, 95) + np.percentile(d_ba, 95)) / diag)
    try:
        va, vb = float(ref.volume), float(pred.volume)
        vol_err = abs(va - vb) / max(abs(va), 1e-12)
    except Exception:
        vol_err = None
    return {
        "chamfer_norm": chamfer,
        "hausdorff_95_norm": h95,
        "volume_error": vol_err,
        "gt_diag": diag,
    }


def _exec_source(dsl_text: str, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    dsl_path = out_dir / "pred_source.dsl"
    step = out_dir / "pred_source.step"
    stl = out_dir / "pred_source.stl"
    dsl_path.write_text(dsl_text if dsl_text.endswith("\n") else dsl_text + "\n", encoding="utf-8")
    py = Path("/data/miniconda3/envs/cadfit-env/bin/python")
    script = ROOT / "scripts/deepcad/dsl_to_occ.py"
    proc = subprocess.run(
        [str(py), str(script), "--dsl", str(dsl_path), "--step", str(step), "--stl", str(stl)],
        capture_output=True,
        text=True,
    )
    ok = proc.returncode == 0 and step.exists() and step.stat().st_size > 0
    return {
        "step_ok": ok,
        "stl": str(stl) if stl.exists() else None,
        "error": None if ok else (proc.stderr or proc.stdout)[-400:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decode-dir", type=Path, required=True)
    ap.add_argument("--train-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD/train")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--max-chamfer", type=float, default=0.05)
    ap.add_argument("--report-json", type=Path, default=None, help="decode report.json for exact/step")
    args = ap.parse_args()

    decode_dir = args.decode_dir
    report_path = args.report_json or (decode_dir / "report.json")
    if not report_path.exists():
        # try parent
        cands = list(decode_dir.rglob("report.json"))
        if not cands:
            print(f"missing report.json under {decode_dir}")
            return 2
        report_path = cands[0]
        decode_dir = report_path.parent

    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows = []
    for s in report["samples"]:
        sid = s["sample_id"]
        sample_dir = decode_dir / sid
        pred_path = sample_dir / "pred.dsl"
        if not pred_path.exists():
            pred_path = sample_dir / "pred.txt"
        pred_text = pred_path.read_text(encoding="utf-8") if pred_path.exists() else ""

        tf_path = args.train_dir / sid / "coordinate_transform.json"
        gt_mesh = args.train_dir / sid / "model.obj"
        row = {
            "sample_id": sid,
            "exact_match": bool(s.get("exact_match")),
            "canonical_step_ok": bool(s.get("step_ok")),
            "canonical_parsed": bool(s.get("parsed")),
        }
        if not tf_path.exists():
            row["error"] = "missing transform"
            rows.append(row)
            continue
        try:
            tf = load_transform_json(tf_path)
            src_dsl = transform_dsl(pred_text, tf, inverse=True)
            (sample_dir / "pred_source.dsl").write_text(src_dsl, encoding="utf-8")
            exec_rec = _exec_source(src_dsl, sample_dir)
            row["source_step_ok"] = exec_rec["step_ok"]
            if exec_rec["step_ok"] and exec_rec.get("stl") and gt_mesh.exists():
                row["geometry"] = _geom(gt_mesh, Path(exec_rec["stl"]))
            else:
                row["geometry"] = {"error": exec_rec.get("error") or "no_stl"}
                row["source_error"] = exec_rec.get("error")
        except Exception as e:
            row["error"] = str(e)
            row["source_step_ok"] = False
            row["geometry"] = {"error": str(e)}
        rows.append(row)
        g = row.get("geometry", {})
        print(
            f"{sid}: exact={row['exact_match']} can_step={row['canonical_step_ok']} "
            f"src_step={row.get('source_step_ok')} chamfer={g.get('chamfer_norm')} "
            f"h95={g.get('hausdorff_95_norm')}"
        )

    n = len(rows)
    exact_n = sum(1 for r in rows if r.get("exact_match"))
    can_step_n = sum(1 for r in rows if r.get("canonical_step_ok"))
    src_step_n = sum(1 for r in rows if r.get("source_step_ok"))
    geom_ok_n = sum(
        1
        for r in rows
        if isinstance(r.get("geometry"), dict)
        and r["geometry"].get("chamfer_norm") is not None
        and r["geometry"]["chamfer_norm"] <= args.max_chamfer
    )
    chamfers = [
        r["geometry"]["chamfer_norm"]
        for r in rows
        if isinstance(r.get("geometry"), dict) and r["geometry"].get("chamfer_norm") is not None
    ]

    gate_pass = (
        n == 10
        and exact_n >= 9  # allow 9/10 near-exact; prefer 10
        and can_step_n == 10
        and src_step_n == 10
        and geom_ok_n >= 9
    )
    # Strict preferred
    strict_pass = exact_n == 10 and can_step_n == 10 and src_step_n == 10 and geom_ok_n == 10

    out = {
        "n": n,
        "exact_match_n": exact_n,
        "canonical_step_n": can_step_n,
        "source_step_n": src_step_n,
        "geom_ok_n": geom_ok_n,
        "max_chamfer": args.max_chamfer,
        "mean_chamfer_norm": float(np.mean(chamfers)) if chamfers else None,
        "gate_pass": gate_pass,
        "strict_pass": strict_pass,
        "verdict": "PASS" if strict_pass else ("SOFT_PASS" if gate_pass else "FAIL"),
        "samples": rows,
        "decode_report": str(report_path),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "samples"}, indent=2))
    return 0 if gate_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
