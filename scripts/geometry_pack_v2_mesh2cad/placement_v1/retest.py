#!/usr/bin/env python3
"""Retest the 53 circle/rect non-one-side samples and the 182 negative-extent samples.

Reconvert from source.json with the repaired extent converter, apply the same
cm→mm factor 10, then freeze the old Chamfer/coverage thresholds.
Does not write into unit_audit_v2 sample trees and does not start training.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

import numpy as np

ROOT = pathlib.Path("/data/home/cuiyuehan/project/mesh2cad")
AUDIT = ROOT / "cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v2"
OUT = ROOT / "cad_spatial_dataset/geometry_pack_v2_mesh2cad/placement_fix_retest_v1"
sys.path[:0] = [
    str(ROOT / "scripts"),
    str(ROOT / "scripts/fusion360"),
    str(ROOT / "scripts/geometry_pack_v2_mesh2cad"),
    str(ROOT / "scripts/deepcad"),
]
sys.path.insert(0, str(pathlib.Path(__file__).parent))


def save(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def mesh(path: pathlib.Path):
    from geometry_pack_v1.occ import load_step_shape, tessellate_shape, triangulation_to_arrays

    shape = load_step_shape(path)
    tessellate_shape(shape)
    v, f = triangulation_to_arrays(shape)
    if not len(f):
        raise ValueError("empty triangulation")
    return v, f


def geom_compare(src_step: pathlib.Path, pred_step: pathlib.Path, cad_id: str) -> dict:
    from geometry_pack_v1.surface import sample_surface_uniform
    from scipy.spatial import cKDTree

    vg, fg = mesh(src_step)
    vp, fp = mesh(pred_step)
    diag = float(np.linalg.norm(vg.max(0) - vg.min(0)))
    seed = int(hashlib.sha256(cad_id.encode()).hexdigest()[:8], 16)
    a, _, _ = sample_surface_uniform(vg, fg, 20000, seed)
    b, _, _ = sample_surface_uniform(vp, fp, 20000, seed ^ 0x5A5A5A5A)
    ab = cKDTree(b).query(a, workers=1)[0] / diag
    ba = cKDTree(a).query(b, workers=1)[0] / diag
    ch = float((ab.mean() + ba.mean()) / 2)
    cov = float((ab <= 0.02).mean())
    return {
        "chamfer_rel": ch,
        "coverage_02": cov,
        "chamfer_pass": ch <= 0.01,
        "coverage_pass": cov >= 0.98,
        "gt_bbox_diag": diag,
        "label_gate": bool(ch <= 0.01 and cov >= 0.98),
    }


def selected_ids() -> dict:
    risks = json.loads((AUDIT / "residual_conversion_risks.json").read_text())
    rows = json.loads((AUDIT / "results602.json").read_text())
    smoking = [r["cad_id"] for r in risks if r.get("circle_rectangle_non_one_side")]
    negative = [r["cad_id"] for r in risks if r.get("negative_extent_distances")]
    passing = [r["cad_id"] for r in rows if r.get("label_gate") is True]
    union = list(dict.fromkeys(smoking + negative))
    canary = [c for c in passing if c not in set(union)][:20]
    return {
        "smoking_circle_rect_non_one_side": smoking,
        "negative_extent_distance": negative,
        "union": union,
        "canary_previous_pass": canary,
        "all": [r['cad_id'] for r in rows],
    }


def worker(cad_id: str) -> dict:
    from fusion360_to_dsl import fusion360_json_to_dsl
    from fusion_unit_contract import transform
    from cad_dsl import execute_dsl, parse_dsl

    before = next(r for r in json.loads((AUDIT / "results602.json").read_text()) if r["cad_id"] == cad_id)
    src_step = pathlib.Path(before["source_step"])
    src_json = src_step.parent / "source.json"
    d = OUT / "samples" / cad_id
    d.mkdir(parents=True, exist_ok=False)
    ans = {
        "cad_id": cad_id,
        "before_label_gate": before.get("label_gate"),
        "before_chamfer": before.get("chamfer_rel"),
        "before_coverage": before.get("coverage_02"),
        "parsed": False,
        "execution_ok": False,
        "step_reload": False,
        "label_gate": False,
    }
    stage = "convert"
    t0 = time.time()
    try:
        dsl_cm, report = fusion360_json_to_dsl(json.loads(src_json.read_text()))
        (d / "program_cm.dsl").write_text(dsl_cm)
        save(d / "conversion.json", report)
        ans["dsl_has_symmetric"] = "symmetric=" in dsl_cm
        ans["dsl_has_height_two"] = "height_two=" in dsl_cm
        ans["dsl_has_negative_height"] = "height=-" in dsl_cm
        stage = "unit_conversion"
        dsl_mm = transform(dsl_cm, 10.0)
        (d / "program_mm.dsl").write_text(dsl_mm)
        stage = "parse"
        parse_dsl(dsl_mm)
        ans["parsed"] = True
        stage = "execute"
        execute_dsl(dsl_mm, d / "reconstructed.step")
        ans["execution_ok"] = True
        stage = "geometry"
        ans.update(geom_compare(src_step, d / "reconstructed.step", cad_id))
        ans["step_reload"] = True
        ans["chamfer_delta"] = (ans["chamfer_rel"] - before["chamfer_rel"]) if before.get("chamfer_rel") is not None else None
        ans["coverage_delta"] = (ans["coverage_02"] - before["coverage_02"]) if before.get("coverage_02") is not None else None
    except Exception as e:
        ans.update(failure_stage=stage, error=repr(e))
    ans["elapsed_s"] = time.time() - t0
    save(d / "audit.json", ans)
    return ans


def launch(cad_id: str) -> dict:
    timeout = 150
    env = os.environ.copy()
    env.update(
        OPENBLAS_NUM_THREADS="1",
        OMP_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        CUDA_VISIBLE_DEVICES="",
        PYTHONDONTWRITEBYTECODE="1",
    )
    log = OUT / "logs" / f"{cad_id}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("x") as f:
        try:
            p = subprocess.run(
                [sys.executable, "-B", __file__, "--worker", cad_id],
                env=env,
                stdout=f,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return dict(cad_id=cad_id, failure_stage="timeout", timeout_s=timeout, label_gate=None)
    pth = OUT / "samples" / cad_id / "audit.json"
    if pth.exists():
        return json.loads(pth.read_text())
    return dict(cad_id=cad_id, failure_stage="worker_exit", returncode=p.returncode, label_gate=None)


def summarize(rows: list[dict], ids: list[str], before_map: dict) -> dict:
    hit = [r for r in rows if r["cad_id"] in set(ids)]
    n = len(hit)
    n_pass = sum(1 for r in hit if r.get("label_gate") is True)
    before_pass = sum(1 for i in ids if before_map.get(i, {}).get("label_gate") is True)
    gained = [r["cad_id"] for r in hit if r.get("label_gate") is True and before_map.get(r["cad_id"], {}).get("label_gate") is not True]
    lost = [r["cad_id"] for r in hit if r.get("label_gate") is not True and before_map.get(r["cad_id"], {}).get("label_gate") is True]
    return {
        "n": n,
        "before_pass": before_pass,
        "after_pass": n_pass,
        "gained": len(gained),
        "lost": len(lost),
        "gained_ids": gained[:20],
        "lost_ids": lost[:20],
        "execution_ok": sum(1 for r in hit if r.get("execution_ok") is True),
        "step_reload": sum(1 for r in hit if r.get("step_reload") is True),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", type=str)
    args = ap.parse_args()
    if args.worker:
        worker(args.worker)
        return
    OUT.mkdir(parents=True, exist_ok=False)
    frozen_path=ROOT/'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/V1_FROZEN_SHA256.json'
    original=json.loads(frozen_path.read_text())
    frozen={p:digest(pathlib.Path(p)) for p in original}
    save(OUT/'ENTRY_FROZEN_HASHES.json',frozen)
    save(OUT/'PREEXISTING_HASH_DRIFT.json',{p:{'original':h,'entry':frozen[p]} for p,h in original.items() if frozen[p]!=h})
    ids = selected_ids()
    save(OUT / "subset.json", ids)
    before = {r["cad_id"]: r for r in json.loads((AUDIT / "results602.json").read_text())}
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
        futs = [pool.submit(launch, cid) for cid in ids["all"]]
        for i, f in enumerate(concurrent.futures.as_completed(futs), 1):
            rows.append(f.result())
            if i % 10 == 0 or i == len(ids["all"]):
                print(
                    json.dumps(
                        dict(
                            completed=i,
                            total=len(ids["all"]),
                            label_pass=sum(r.get("label_gate") is True for r in rows),
                        )
                    ),
                    flush=True,
                )
    rows = sorted(rows, key=lambda r: r["cad_id"])
    save(OUT / "results.json", rows)
    summary = {
        "smoking_circle_rect_non_one_side": summarize(rows, ids["smoking_circle_rect_non_one_side"], before),
        "negative_extent_distance": summarize(rows, ids["negative_extent_distance"], before),
        "union": summarize(rows, ids["union"], before),
        "canary_previous_pass": summarize(rows, ids["canary_previous_pass"], before),
        "thresholds": {"chamfer_rel_max": 0.01, "coverage_02_min": 0.98},
        "n_retested": len(rows),
        "converter": "scripts/fusion360/fusion360_to_dsl.py",
        "executor": "scripts/edge_aware_cad_planner_v1/cad_dsl.py",
        "V2_100_STARTED": False,
        "NEW_TRAINING_STARTED": False,
    }
    save(OUT / "SUMMARY.json", summary)
    changed=[p for p,h in frozen.items() if digest(pathlib.Path(p))!=h]
    save(OUT/'EXIT_FROZEN_CHECK.json',{'checked':len(frozen),'changed':changed,'pass':not changed})
    lines = [
        "# Fusion360 extent converter 复测",
        "",
        "只修圆/矩形快捷分支的 symmetric/height_two，以及负距离符号；按原阈值 Chamfer≤0.01 且 coverage≥0.98。",
        "",
        f"- 圆/矩形非单侧：{summary['smoking_circle_rect_non_one_side']}",
        f"- 负 extent 距离：{summary['negative_extent_distance']}",
        f"- 并集：{summary['union']}",
        f"- 此前已通过的对照 20 条：{summary['canary_previous_pass']}",
        "",
    ]
    (OUT / "EXTENT_FIX_RETEST.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
