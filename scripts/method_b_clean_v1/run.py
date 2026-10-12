#!/usr/bin/env python3
"""Method-B data clean entrypoint.

Stages:
  1) harvest DeepCAD/Fusion existing curves.json (Method B GT already extracted)
  2) select CADFS STEP+annotation candidates
  3) build CADFS method_b_pack_v1 samples
  4) write scale manifests + stats

Sources stay in separate buckets — never shuffle-merged.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from method_b_clean_v1.build_one import build_one  # noqa: E402
from method_b_clean_v1.constants import MANIFEST_ROOT, OUTPUT_ROOT  # noqa: E402
from method_b_clean_v1.harvest_existing import write_harvest  # noqa: E402
from method_b_clean_v1.select_cadfs import select_cadfs  # noqa: E402
from method_b_clean_v1.stats import write_scale_manifest, write_stats_report  # noqa: E402


def _build_worker(payload: dict) -> dict:
    return build_one(
        step_path=Path(payload["step_path"]),
        out_dir=OUTPUT_ROOT / "cadfs" / payload["sample_id"],
        sample_id=payload["sample_id"],
        dataset="cadfs",
        seed=int(payload.get("seed", 0)),
        overwrite=bool(payload.get("overwrite", False)),
        annotation_path=Path(payload["annotation_path"])
        if payload.get("annotation_path")
        else None,
    )


def run_cadfs_build(records: list[dict], *, workers: int, overwrite: bool, seed: int) -> list[dict]:
    payloads = []
    for i, r in enumerate(records):
        payloads.append(
            {
                "sample_id": r["sample_id"],
                "step_path": r["step_path"],
                "annotation_path": r.get("annotation_path"),
                "seed": seed + i,
                "overwrite": overwrite,
            }
        )
    results = []
    if workers <= 1:
        for p in payloads:
            results.append(_build_worker(p))
            status = "ok" if results[-1].get("ok") else "FAIL"
            print(f"[{status}] {p['sample_id']} {results[-1].get('error', '')}", flush=True)
        return results

    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_build_worker, p): p for p in payloads}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                meta = fut.result()
            except Exception as exc:  # noqa: BLE001
                meta = {"sample_id": p["sample_id"], "ok": False, "qa_pass": False, "error": str(exc)}
            results.append(meta)
            status = "ok" if meta.get("ok") and meta.get("qa_pass", True) else "FAIL"
            print(f"[{status}] {p['sample_id']} {meta.get('error', '')}", flush=True)
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--stage",
        choices=["harvest", "select", "build", "stats", "all"],
        default="all",
    )
    ap.add_argument("--cadfs-n", type=int, default=50, help="CADFS candidates to build this round")
    ap.add_argument("--cadfs-pool", type=int, default=500, help="candidate pool size before build")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--scale", default="overfit100", choices=["overfit100", "mid1k", "full10k"])
    args = ap.parse_args()

    t0 = time.time()
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    (MANIFEST_ROOT / "manifests").mkdir(parents=True, exist_ok=True)

    if args.stage in ("harvest", "all"):
        for ds in ("deepcad", "fusion360"):
            path = write_harvest(ds)
            data = json.loads(path.read_text(encoding="utf-8"))
            print(f"[harvest] {ds}: pass={data['n_pass']}/{data['n_scanned']}")

    cand_path = MANIFEST_ROOT / "manifests" / f"cadfs_candidates_{args.cadfs_pool}.json"
    if args.stage in ("select", "all"):
        selected = select_cadfs(n=args.cadfs_pool, seed=args.seed)
        obj = {
            "dataset": "cadfs",
            "n_requested": args.cadfs_pool,
            "n_selected": len(selected),
            "seed": args.seed,
            "sample_ids": [r["sample_id"] for r in selected],
            "records": selected,
        }
        cand_path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        print(f"[select] CADFS candidates={len(selected)} -> {cand_path}")

    if args.stage in ("build", "all"):
        if not cand_path.is_file():
            raise SystemExit(f"missing candidates manifest: {cand_path}; run --stage select first")
        pool = json.loads(cand_path.read_text(encoding="utf-8"))["records"]
        to_build = pool[: args.cadfs_n]
        print(f"[build] CADFS building {len(to_build)} packs with workers={args.workers}")
        results = run_cadfs_build(to_build, workers=args.workers, overwrite=args.overwrite, seed=args.seed)
        summary = {
            "n": len(results),
            "ok": sum(1 for r in results if r.get("ok")),
            "qa_pass": sum(1 for r in results if r.get("qa_pass")),
            "results": results,
        }
        out = MANIFEST_ROOT / "runs" / f"cadfs_build_n{args.cadfs_n}_seed{args.seed}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
        print(f"[build] ok={summary['ok']} qa_pass={summary['qa_pass']} -> {out}")

    if args.stage in ("stats", "all"):
        man = write_scale_manifest(args.scale, args.seed)
        md = write_stats_report()
        print(f"[stats] {man}")
        print(f"[stats] {md}")

    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
