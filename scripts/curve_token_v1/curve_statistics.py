#!/usr/bin/env python3
"""Dataset-wide statistics for the Track B curve dataset."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .config import CURVE_TYPE_IDS, SPLITS, STATS_DIR, cad_dir, split_dir


def _pct(values: np.ndarray, q: float) -> float:
    return float(np.percentile(values, q)) if values.size else 0.0


def _dist(values, name: str = "") -> dict:
    a = np.asarray(values, dtype=np.float64)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return {"n": 0}
    return {
        "n": int(a.size),
        "mean": float(a.mean()),
        "std": float(a.std()),
        "min": float(a.min()),
        "median": float(np.median(a)),
        "p90": _pct(a, 90),
        "p95": _pct(a, 95),
        "p99": _pct(a, 99),
        "max": float(a.max()),
    }


def _collect_one(job: tuple[str, str]) -> dict | None:
    split, cad_id = job
    d = cad_dir(split, cad_id)
    cj, tj = d / "curves.json", d / "topology.json"
    if not cj.is_file():
        return None
    try:
        data = json.loads(cj.read_text(encoding="utf-8"))
        topo = json.loads(tj.read_text(encoding="utf-8")) if tj.is_file() else {"stats": {}}
    except Exception as exc:  # noqa: BLE001
        return {"split": split, "cad_id": cad_id, "load_error": f"{type(exc).__name__}: {exc}"}

    curves = data["curves"]
    out: dict = {
        "split": split,
        "cad_id": cad_id,
        "num_curves": len(curves),
        "num_faces": data["num_faces"],
        "num_vertices": data["num_vertices"],
        "num_skipped_edges": data["num_skipped_edges"],
        "skipped_reasons": [s.get("reason", "?").split(":")[0] for s in data["skipped_edges"]],
        "type_counts": data["curve_type_counts"],
        "lengths": [c["length"] for c in curves],
        "closed": [bool(c["is_closed"]) for c in curves],
        "n_faces_per_curve": [int(c["n_faces"]) for c in curves],
        "param_ok": sum(1 for c in curves if c["extraction"]["parameter_extraction_ok"]),
        "geom_ok": sum(1 for c in curves if c["extraction"]["geometry_reconstruction_ok"]),
        "sampling_modes": [c.get("sampling", {}).get("mode", "?") for c in curves],
        "recon_backends": [c["extraction"].get("recon_backend") or "none" for c in curves],
        "topology_stats": topo.get("stats", {}),
        "topology_valid": bool(topo.get("topology_valid", False)),
        "normalization_source": "track_a" if "track_a" in str(
            (d / "normalization.json").read_text(encoding="utf-8") if (d / "normalization.json").is_file() else ""
        ) else "fallback",
        "bspline": [],
        "other_types": [],
    }
    for c in curves:
        if c["curve_type"] in ("BSPLINE", "BEZIER"):
            p = c.get("world_parameters", {})
            if not p:
                continue
            out["bspline"].append(
                {
                    "type": c["curve_type"],
                    "degree": int(p["degree"]),
                    "n_cp": int(p["num_control_points"]),
                    "n_knots": int(p["num_knots"]),
                    "rational": bool(p["is_rational"]),
                    "periodic": bool(p["is_periodic"]),
                    "closed": bool(c["is_closed"]),
                    "length": float(c["length"]),
                }
            )
        if c["curve_type"] not in ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE"):
            out["other_types"].append(
                {
                    "curve_type": c["curve_type"],
                    "occ_geomabs_type": c["occ_geomabs_type"],
                    "cad_id": cad_id,
                    "edge_id": c["edge_id"],
                    "has_parameters": bool(c.get("world_parameters")),
                }
            )
    return out


def collect(jobs: list[tuple[str, str]], workers: int = 16) -> list[dict]:
    from concurrent.futures import ProcessPoolExecutor

    if workers <= 1:
        rows = [_collect_one(j) for j in jobs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_collect_one, jobs, chunksize=8))
    return [r for r in rows if r is not None]


def compute(rows: list[dict], attempted: int, failed: list[dict]) -> dict:
    ok = [r for r in rows if "load_error" not in r]
    type_counts: Counter[str] = Counter()
    for r in ok:
        type_counts.update(r["type_counts"])
    total_curves = int(sum(type_counts.values()))

    curves_per_cad = np.array([r["num_curves"] for r in ok], dtype=np.float64)
    lengths = np.concatenate([np.asarray(r["lengths"]) for r in ok]) if ok else np.zeros(0)
    closed = np.concatenate([np.asarray(r["closed"]) for r in ok]) if ok else np.zeros(0, bool)
    faces_per_edge = (
        np.concatenate([np.asarray(r["n_faces_per_curve"]) for r in ok]) if ok else np.zeros(0)
    )

    sampling_modes: Counter[str] = Counter()
    skipped_reasons: Counter[str] = Counter()
    recon_backends: Counter[str] = Counter()
    for r in ok:
        sampling_modes.update(r["sampling_modes"])
        skipped_reasons.update(r["skipped_reasons"])
        recon_backends.update(r.get("recon_backends", []))

    bs = [b for r in ok for b in r["bspline"]]
    bs_deg = Counter(b["degree"] for b in bs)
    bs_cp = np.array([b["n_cp"] for b in bs], dtype=np.float64)
    bs_kn = np.array([b["n_knots"] for b in bs], dtype=np.float64)
    n_bs = max(len(bs), 1)

    edges_per_face = np.array(
        [r["topology_stats"].get("edges_per_face_mean", 0.0) for r in ok], dtype=np.float64
    )
    n_boundary_edges = sum(r["topology_stats"].get("boundary_edges", 0) for r in ok)
    n_manifold_edges = sum(r["topology_stats"].get("manifold_two_face_edges", 0) for r in ok)
    n_nonmanifold_edges = sum(r["topology_stats"].get("non_manifold_edges", 0) for r in ok)
    n_free_edges = sum(r["topology_stats"].get("free_edges", 0) for r in ok)
    n_topo_valid = sum(1 for r in ok if r["topology_valid"])
    n_manifold_cad = sum(1 for r in ok if r["topology_stats"].get("is_manifold"))

    other = [o for r in ok for o in r["other_types"]]
    other_counter = Counter(
        f"{o['curve_type']}(geomabs={o['occ_geomabs_type']})" for o in other
    )

    denom_c = max(total_curves, 1)
    denom_cad = max(len(ok), 1)

    complex_bsplines = sorted(
        (b for b in bs),
        key=lambda b: (b["n_cp"], b["degree"]),
        reverse=True,
    )[:15]

    return {
        "TOTAL_CAD": attempted,
        "VALID_CAD": len(ok),
        "FAILED_CAD": len(failed) + sum(1 for r in rows if "load_error" in r),
        "TOTAL_CURVES": total_curves,
        "failed_cad_detail": failed[:200],
        "curve_type_counts": dict(type_counts),
        "curve_type_pct": {k: 100.0 * v / denom_c for k, v in type_counts.items()},
        "curve_type_ids": CURVE_TYPE_IDS,
        "curves_per_cad": _dist(curves_per_cad),
        "curve_length_world": _dist(lengths),
        "faces_per_edge": _dist(faces_per_edge),
        "edges_per_face_per_cad_mean": _dist(edges_per_face),
        "closed_curves": int(closed.sum()) if closed.size else 0,
        "open_curves": int((~closed).sum()) if closed.size else 0,
        "closed_curves_pct": 100.0 * float(closed.sum()) / denom_c if closed.size else 0.0,
        "open_curves_pct": 100.0 * float((~closed).sum()) / denom_c if closed.size else 0.0,
        "topology": {
            "boundary_edges": n_boundary_edges,
            "manifold_two_face_edges": n_manifold_edges,
            "non_manifold_edges": n_nonmanifold_edges,
            "free_edges": n_free_edges,
            "boundary_edge_pct": 100.0 * n_boundary_edges / denom_c,
            "manifold_two_face_edge_pct": 100.0 * n_manifold_edges / denom_c,
            "non_manifold_edge_pct": 100.0 * n_nonmanifold_edges / denom_c,
            "free_edge_pct": 100.0 * n_free_edges / denom_c,
            "cad_with_valid_topology": n_topo_valid,
            "topology_valid_rate_pct": 100.0 * n_topo_valid / denom_cad,
            "cad_fully_manifold": n_manifold_cad,
            "manifold_cad_rate_pct": 100.0 * n_manifold_cad / denom_cad,
        },
        "bspline": {
            "count": len(bs),
            "degree_distribution": {str(k): v for k, v in sorted(bs_deg.items())},
            "control_points": _dist(bs_cp),
            "knot_count": _dist(bs_kn),
            "rational_count": sum(1 for b in bs if b["rational"]),
            "rational_pct": 100.0 * sum(1 for b in bs if b["rational"]) / n_bs,
            "periodic_count": sum(1 for b in bs if b["periodic"]),
            "periodic_pct": 100.0 * sum(1 for b in bs if b["periodic"]) / n_bs,
            "closed_count": sum(1 for b in bs if b["closed"]),
            "closed_pct": 100.0 * sum(1 for b in bs if b["closed"]) / n_bs,
            "most_complex": complex_bsplines,
        },
        "other_curve_types": dict(other_counter),
        "other_curve_examples": other[:50],
        "sampling_modes": dict(sampling_modes),
        "recon_backends": dict(recon_backends),
        "skipped_edge_reasons": dict(skipped_reasons),
        "total_skipped_edges": sum(r["num_skipped_edges"] for r in ok),
        "parameter_extraction_ok_curves": sum(r["param_ok"] for r in ok),
        "geometry_reconstruction_ok_curves": sum(r["geom_ok"] for r in ok),
        "normalization_from_track_a": sum(
            1 for r in ok if r["normalization_source"] == "track_a"
        ),
        "per_split": {
            sp: {
                "cad": sum(1 for r in ok if r["split"] == sp),
                "curves": sum(r["num_curves"] for r in ok if r["split"] == sp),
            }
            for sp in SPLITS
        },
    }


def _dist_row(name: str, d: dict) -> str:
    if not d.get("n"):
        return f"| {name} | 0 | - | - | - | - | - | - |"
    return (
        f"| {name} | {d['n']} | {d['mean']:.4g} | {d['median']:.4g} | {d['p90']:.4g} | "
        f"{d['p95']:.4g} | {d['p99']:.4g} | {d['max']:.4g} |"
    )


def write_reports(stats: dict, tag: str) -> tuple[Path, Path]:
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    jpath = STATS_DIR / f"curve_statistics_{tag}.json"
    mpath = STATS_DIR / f"curve_statistics_{tag}.md"
    jpath.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    tc, tp = stats["curve_type_counts"], stats["curve_type_pct"]
    order = ["LINE", "CIRCLE", "ELLIPSE", "BSPLINE", "BEZIER", "HYPERBOLA", "PARABOLA", "OFFSET", "OTHER"]
    lines = [
        f"# Track B curve dataset statistics ({tag})",
        "",
        "```text",
        f"TOTAL_CAD={stats['TOTAL_CAD']}",
        f"VALID_CAD={stats['VALID_CAD']}",
        f"FAILED_CAD={stats['FAILED_CAD']}",
        f"TOTAL_CURVES={stats['TOTAL_CURVES']}",
        "```",
        "",
        "## Curve type distribution",
        "",
        "| curve type | count | % of curves |",
        "|---|---|---|",
    ]
    for k in order:
        if k in tc:
            lines.append(f"| {k} | {tc[k]} | {tp[k]:.4f}% |")
    for k in sorted(set(tc) - set(order)):
        lines.append(f"| {k} | {tc[k]} | {tp[k]:.4f}% |")

    lines += [
        "",
        "## Distributions",
        "",
        "| quantity | n | mean | median | P90 | P95 | P99 | max |",
        "|---|---|---|---|---|---|---|---|",
        _dist_row("curves per CAD", stats["curves_per_cad"]),
        _dist_row("curve length (world units)", stats["curve_length_world"]),
        _dist_row("faces per edge", stats["faces_per_edge"]),
        _dist_row("edges per face (per-CAD mean)", stats["edges_per_face_per_cad_mean"]),
        "",
        "## B-Spline complexity",
        "",
        f"- instances: {stats['bspline']['count']}",
        f"- degree distribution: `{stats['bspline']['degree_distribution']}`",
        f"- rational: {stats['bspline']['rational_count']} ({stats['bspline']['rational_pct']:.3f}%)",
        f"- periodic: {stats['bspline']['periodic_count']} ({stats['bspline']['periodic_pct']:.3f}%)",
        f"- closed: {stats['bspline']['closed_count']} ({stats['bspline']['closed_pct']:.3f}%)",
        "",
        "| quantity | n | mean | median | P90 | P95 | P99 | max |",
        "|---|---|---|---|---|---|---|---|",
        _dist_row("control points", stats["bspline"]["control_points"]),
        _dist_row("knot count", stats["bspline"]["knot_count"]),
        "",
        "### Most complex B-Spline instances",
        "",
        "| degree | control points | knots | rational | periodic |",
        "|---|---|---|---|---|",
    ]
    for b in stats["bspline"]["most_complex"][:10]:
        lines.append(
            f"| {b['degree']} | {b['n_cp']} | {b['n_knots']} | {b['rational']} | {b['periodic']} |"
        )

    t = stats["topology"]
    lines += [
        "",
        "## Topology",
        "",
        "| quantity | count | % of curves |",
        "|---|---|---|",
        f"| boundary edges (1 face) | {t['boundary_edges']} | {t['boundary_edge_pct']:.4f}% |",
        f"| manifold edges (2 faces) | {t['manifold_two_face_edges']} | {t['manifold_two_face_edge_pct']:.4f}% |",
        f"| non-manifold edges (>2 faces) | {t['non_manifold_edges']} | {t['non_manifold_edge_pct']:.4f}% |",
        f"| free edges (0 faces) | {t['free_edges']} | {t['free_edge_pct']:.4f}% |",
        f"| closed curves | {stats['closed_curves']} | {stats['closed_curves_pct']:.4f}% |",
        f"| open curves | {stats['open_curves']} | {stats['open_curves_pct']:.4f}% |",
        "",
        f"- CAD with self-consistent topology: {t['cad_with_valid_topology']} "
        f"({t['topology_valid_rate_pct']:.4f}%)",
        f"- CAD that are fully manifold: {t['cad_fully_manifold']} "
        f"({t['manifold_cad_rate_pct']:.4f}%)",
        "",
        "Non-manifold edges (>2 adjacent faces) occur in solids built by unioning bodies",
        "that touch along an edge. They are extracted faithfully (the curve simply carries",
        "3+ face ids) and are reported here rather than treated as an extraction failure.",
        "",
        "## Extraction health",
        "",
        f"- curves with exact parameters extracted: {stats['parameter_extraction_ok_curves']}",
        f"- curves whose parameters reproduce the OCC curve: {stats['geometry_reconstruction_ok_curves']}",
        f"- skipped topological edges: {stats['total_skipped_edges']} `{stats['skipped_edge_reasons']}`",
        f"- sampling strategy used: `{stats['sampling_modes']}`",
        f"- reconstruction backend used for verification: `{stats['recon_backends']}`"
        " (`numpy` = parameters are consumable without OCC)",
        f"- CAD reusing the Track A normalization transform: {stats['normalization_from_track_a']}",
        f"- non-primary curve types encountered: `{stats['other_curve_types'] or 'none'}`",
        "",
        "## Per split",
        "",
        "| split | CAD | curves |",
        "|---|---|---|",
    ]
    for sp, v in stats["per_split"].items():
        lines.append(f"| {sp} | {v['cad']} | {v['curves']} |")
    lines.append("")
    mpath.write_text("\n".join(lines), encoding="utf-8")
    return jpath, mpath


def main() -> int:
    ap = argparse.ArgumentParser(description="Track B curve dataset statistics")
    ap.add_argument("--split", action="append", default=None)
    ap.add_argument("--tag", default="all")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    jobs: list[tuple[str, str]] = []
    for sp in args.split or list(SPLITS):
        root = split_dir(sp)
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if (d / "curves.json").is_file():
                jobs.append((sp, d.name))

    rows = collect(jobs, args.workers)
    stats = compute(rows, attempted=len(jobs), failed=[])
    jp, mp = write_reports(stats, args.tag)
    print(json.dumps({k: stats[k] for k in stats if k.isupper()}, indent=2))
    print(f"-> {jp}\n-> {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
