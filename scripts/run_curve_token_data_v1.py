#!/usr/bin/env python3
"""Track B / Method 2 (Parametric Curve Token) -- data foundation entry point.

Stages, in order:

    audit  -> guard-snapshot -> build -> validate -> statistics -> visual QA
           -> fitting baseline -> guard-verify

Track A is read-only throughout. The guard brackets the whole run with a
sha256 audit of every Track A file, and a single byte of difference aborts with
CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION.

Usage:
    python3 scripts/run_curve_token_data_v1.py --stage canary10
    python3 scripts/run_curve_token_data_v1.py --stage canary100
    python3 scripts/run_curve_token_data_v1.py --stage full
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.curve_token_v1 import track_a_guard  # noqa: E402
from scripts.curve_token_v1.build_dataset import build_many, list_cad_ids  # noqa: E402
from scripts.curve_token_v1.config import (  # noqa: E402
    N_SAMPLE_DEFAULT,
    N_SAMPLE_EXTRA,
    OUTPUT_ROOT,
    RUNS_DIR,
    SPLITS,
    VISUAL_QA_DIR,
    cad_dir,
)

STAGE_LIMITS = {"canary10": 10, "canary100": 100, "full": None}


def _select_ids(stage: str, seed: int) -> dict[str, list[str]]:
    """Pick cad_ids per split.

    Canary stages are biased towards curve-type coverage rather than being purely
    random: a uniform sample of DeepCAD is almost all LINE, which would not
    exercise the ELLIPSE / BSPLINE paths at all.
    """
    limit = STAGE_LIMITS[stage]
    out: dict[str, list[str]] = {}
    if limit is None:
        for sp in SPLITS:
            out[sp] = list_cad_ids(sp)
        return out

    import numpy as np

    from scripts.curve_token_v1.config import SPLITS as S

    for sp in SPLITS:
        all_ids = list_cad_ids(sp)
        pack = S[sp]["track_a_pack"]
        # Rank by how many distinct curve types Track A already reports, so the
        # canary covers LINE / CIRCLE / ELLIPSE / BSPLINE.
        scored: list[tuple[int, int, str]] = []
        for cid in all_ids:
            f = pack / cid / "brep_edges.json"
            types: set[str] = set()
            n_rare = 0
            if f.is_file():
                try:
                    for e in json.loads(f.read_text(encoding="utf-8")).get("edges", []):
                        ct = e.get("curve_type", "?")
                        types.add(ct)
                        if ct in ("BSpline", "Ellipse", "Bezier"):
                            n_rare += 1
                except Exception:  # noqa: BLE001
                    pass
            scored.append((len(types), n_rare, cid))
        scored.sort(key=lambda x: (-x[0], -x[1], x[2]))

        per_split = max(1, limit // len(SPLITS))
        n_diverse = max(1, int(per_split * 0.6))
        picked = [c for _, _, c in scored[:n_diverse]]
        rest = [c for c in all_ids if c not in set(picked)]
        rng = np.random.default_rng(seed)
        if rest and per_split - len(picked) > 0:
            k = min(per_split - len(picked), len(rest))
            picked += [rest[i] for i in sorted(rng.choice(len(rest), size=k, replace=False))]
        out[sp] = picked
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Track B curve-token data foundation")
    ap.add_argument("--stage", choices=list(STAGE_LIMITS), default="canary10")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--n-sample", type=int, default=N_SAMPLE_DEFAULT)
    ap.add_argument("--skip-guard", action="store_true", help="debug only; skips the Track A audit")
    ap.add_argument("--skip-visual-qa", action="store_true")
    ap.add_argument("--visual-qa-count", type=int, default=5)
    args = ap.parse_args()

    tag = args.stage
    t_start = time.time()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_log: dict = {"stage": tag, "workers": args.workers, "seed": args.seed, "stages": {}}

    def emit(name: str, payload: dict) -> None:
        run_log["stages"][name] = payload
        (RUNS_DIR / f"run_{tag}.json").write_text(json.dumps(run_log, indent=2, default=str), encoding="utf-8")

    # ---------------------------------------------------------- 0. audit ----
    print("=" * 78)
    print("[0/7] audit existing Track A data (read-only)")
    from scripts.curve_token_v1.audit_existing_data import build_audit, write_md
    from scripts.curve_token_v1.config import AUDIT_MD

    audit = build_audit(limit=250)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "audit_existing_data.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    write_md(audit, AUDIT_MD)
    print(f"      -> {AUDIT_MD}")
    emit("audit", {"path": str(AUDIT_MD)})

    # ------------------------------------------------ 1. guard snapshot -----
    scope = track_a_guard.assert_write_scope_disjoint()
    print(f"      Track B write root: {scope['track_b_write_root']} (disjoint from Track A)")
    if not args.skip_guard:
        print(f"[1/7] Track A guard snapshot (sha256)")
        t0 = time.time()
        snap = track_a_guard.build_snapshot(min(args.workers, 64))
        (track_a_guard.GUARD_DIR).mkdir(parents=True, exist_ok=True)
        (track_a_guard.GUARD_DIR / f"snapshot_before_{tag}.json").write_text(
            json.dumps(snap), encoding="utf-8"
        )
        print(f"      {snap['n_hashed']} hashed + {snap['n_stated']} stat in {time.time() - t0:.1f}s")
        n_live = len(snap.get("live_track_a_processes", []))
        if n_live:
            print(f"      note: {n_live} Track A process(es) already running; their logs may grow")
        emit("guard_snapshot", {"n_hashed": snap["n_hashed"], "n_stated": snap["n_stated"],
                                "live_track_a_processes": n_live,
                                "write_scope": scope, "seconds": time.time() - t0})
    else:
        snap = None

    # ---------------------------------------------------------- 2. build ----
    print(f"[2/7] build curve dataset (stage={tag})")
    selected = _select_ids(tag, args.seed)
    build_results: list[dict] = []
    for sp, ids in selected.items():
        print(f"      {sp}: {len(ids)} CAD")
        t0 = time.time()
        res = build_many(
            sp, ids, n_sample=args.n_sample, extra_samples=N_SAMPLE_EXTRA, workers=args.workers
        )
        build_results += res
        ok = sum(1 for r in res if r.get("ok"))
        print(f"      {sp}: {ok}/{len(res)} ok in {time.time() - t0:.1f}s")

    failed = [r for r in build_results if not r.get("ok")]
    n_ok = len(build_results) - len(failed)
    print(f"      built {n_ok} / {len(build_results)} CAD ({len(failed)} failed)")
    emit("build", {"attempted": len(build_results), "ok": n_ok, "failed": len(failed),
                   "failures": failed[:100]})

    # ------------------------------------------------------- 3. validate ----
    print("[3/7] geometry-level validation")
    from scripts.curve_token_v1.validate_curve_dataset import (
        aggregate,
        validate_many,
        write_reports as write_val,
    )

    jobs = [(r["split"], r["cad_id"]) for r in build_results if r.get("ok")]
    t0 = time.time()
    val_results = validate_many(jobs, args.workers)
    agg = aggregate(val_results)
    vjson, vmd = write_val(agg, val_results, tag)
    print(f"      PARAMETER_EXTRACTION_PASS_RATE={agg['PARAMETER_EXTRACTION_PASS_RATE']:.4f}%")
    print(f"      GEOMETRY_RECONSTRUCTION_PASS_RATE={agg['GEOMETRY_RECONSTRUCTION_PASS_RATE']:.4f}%")
    print(f"      TOPOLOGY_VALID_RATE={agg['TOPOLOGY_VALID_RATE']:.4f}%  ({time.time() - t0:.1f}s)")
    emit("validate", {k: agg[k] for k in agg if k.isupper()} | {"report": str(vmd)})

    # ----------------------------------------------------- 4. statistics ----
    print("[4/7] statistics")
    from scripts.curve_token_v1.curve_statistics import collect, compute, write_reports as write_stats

    rows = collect(jobs, args.workers)
    stats = compute(rows, attempted=len(build_results), failed=failed)
    sjson, smd = write_stats(stats, tag)
    print(f"      TOTAL_CURVES={stats['TOTAL_CURVES']}  types={stats['curve_type_counts']}")
    emit("statistics", {k: stats[k] for k in stats if k.isupper()} | {"report": str(smd)})

    # ------------------------------------------------------ 5. visual QA ----
    vq_dir = VISUAL_QA_DIR / tag
    if not args.skip_visual_qa:
        print("[5/7] visual QA")
        from scripts.curve_token_v1.visual_qa import render_cad

        # prefer CAD covering the widest set of curve types
        ranked = sorted(
            (r for r in build_results if r.get("ok")),
            key=lambda r: (-len(r.get("type_counts", {})),
                           -sum(v for k, v in r.get("type_counts", {}).items()
                                if k in ("BSPLINE", "ELLIPSE", "BEZIER"))),
        )[: args.visual_qa_count]
        infos = []
        for r in ranked:
            try:
                infos.append(render_cad(r["split"], r["cad_id"], vq_dir))
                print(f"      {r['split']}/{r['cad_id']} ok")
            except Exception as exc:  # noqa: BLE001
                print(f"      {r['split']}/{r['cad_id']} FAILED: {type(exc).__name__}: {exc}")
        vq_dir.mkdir(parents=True, exist_ok=True)
        (vq_dir / "index.json").write_text(json.dumps(infos, indent=2), encoding="utf-8")
        emit("visual_qa", {"dir": str(vq_dir), "n": len(infos)})

    # ------------------------------------------------ 6. fitting baseline ---
    print("[6/7] curve fitting baseline (points -> curve, benchmark only)")
    from scripts.curve_token_v1.fit_curves_from_points import (
        benchmark_cad,
        summarize,
        write_report as write_fit,
    )

    fit_jobs = jobs[: min(len(jobs), 60)]
    reports = []
    for sp, cid in fit_jobs:
        try:
            reports.append(benchmark_cad(sp, cid))
        except Exception as exc:  # noqa: BLE001
            print(f"      fit failed {sp}/{cid}: {type(exc).__name__}: {exc}")
    fit_summary = summarize(reports)
    fjson, fmd = write_fit(fit_summary, reports, tag)
    emit("fitting_baseline", {"report": str(fmd),
                              "types": {k: v["fit_success_rate_pct"] for k, v in fit_summary.items()}})

    # -------------------------------------------------- 7. guard verify -----
    gate = "CURVE_TOKEN_DATA_V1_PASS"
    guard_report: dict = {}
    if not args.skip_guard:
        print("[7/7] Track A guard verify")
        after = track_a_guard.build_snapshot(min(args.workers, 64))
        (track_a_guard.GUARD_DIR / f"snapshot_after_{tag}.json").write_text(
            json.dumps(after), encoding="utf-8"
        )
        guard_report = track_a_guard.compare(snap, after)
        (track_a_guard.GUARD_DIR / f"guard_report_{tag}.json").write_text(
            json.dumps(guard_report, indent=2), encoding="utf-8"
        )
        track_a_guard.write_report(
            guard_report, snap, after, track_a_guard.GUARD_DIR / f"guard_report_{tag}.md"
        )
        if not guard_report["clean"]:
            gate = "CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION"
        print(f"      TRACK_A_MODIFIED={guard_report['TRACK_A_MODIFIED']}")
        n_ext = guard_report.get("TRACK_A_EXTERNAL_LOG_APPENDS", 0)
        if n_ext:
            print(f"      {n_ext} Track A log(s) appended by the concurrent Track A job "
                  f"(verified pure append, not Track B)")
        emit("guard_verify", {k: guard_report[k] for k in guard_report if k.isupper()})

    # ------------------------------------------------------------ gate ------
    if gate != "CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION":
        unsupported = [
            k for k in stats["curve_type_counts"]
            if k not in ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
            and stats["curve_type_counts"][k] > 0
        ]
        thresholds_ok = (
            agg["PARAMETER_EXTRACTION_PASS_RATE"] >= 99.9
            and agg["GEOMETRY_RECONSTRUCTION_PASS_RATE"] >= 99.9
            and agg["TOPOLOGY_VALID_RATE"] >= 99.0
            and len(failed) == 0
        )
        if not thresholds_ok or unsupported:
            gate = "CURVE_TOKEN_DATA_V1_PARTIAL_PASS"

    summary = {
        "CURRENT_GATE": gate,
        "STAGE": tag,
        "TRACK_A_MODIFIED": guard_report.get("TRACK_A_MODIFIED") if guard_report else "not_checked",
        "TRACK_A_REEXECUTED": False,
        "TRACK_A_EXTERNAL_LOG_APPENDS": guard_report.get("TRACK_A_EXTERNAL_LOG_APPENDS", 0)
        if guard_report
        else "not_checked",
        "CAD_TOTAL": len(build_results),
        "CAD_VALID": n_ok,
        "CAD_FAILED": len(failed),
        "TOTAL_CURVES": stats["TOTAL_CURVES"],
        "CURVE_TYPES": stats["curve_type_counts"],
        "PARAMETER_EXTRACTION_PASS_RATE": agg["PARAMETER_EXTRACTION_PASS_RATE"],
        "GEOMETRY_RECONSTRUCTION_PASS_RATE": agg["GEOMETRY_RECONSTRUCTION_PASS_RATE"],
        "TOPOLOGY_VALID_RATE": agg["TOPOLOGY_VALID_RATE"],
        "OUTPUT_ROOT": str(OUTPUT_ROOT),
        "STATISTICS_JSON": str(sjson),
        "STATISTICS_MD": str(smd),
        "VALIDATION_REPORT": str(vmd),
        "VISUAL_QA_DIR": str(vq_dir),
        "FITTING_BASELINE": str(fmd),
        "TOTAL_SECONDS": time.time() - t_start,
    }
    emit("summary", summary)
    (RUNS_DIR / f"summary_{tag}.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    print("=" * 78)
    for k, v in summary.items():
        print(f"{k}={v}")
    print("=" * 78)
    return 0 if gate != "CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
