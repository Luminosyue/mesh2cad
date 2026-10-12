#!/usr/bin/env python3
"""Experiment 4: which route gets closer to the real part, geometry summary or point tokens?

Three routes produce a CAD DSL program for the same part and each program is
executed and measured against the source mesh:

    route_A_blind   bounding box only, with every edge-derived line (rings,
                    radius clusters, circle fits, detected features) stripped
                    from the brief. Isolates what the edge evidence buys.
    route_A_min     full geometry_summary brief + the minimal "generate a CAD
                    construction sequence" prompt -> Qwen API. Same instruction
                    the SpatialLM probe received, so the only difference is
                    whether the model reads a symbolic brief or point tokens.
    route_A_full    the existing edge-aware planner (brief -> rule/LLM feature
                    plan -> DSL). This is the current system, kept as an upper
                    reference rather than an ablation.
    route_B         frozen SpatialLM consuming edge-aware point tokens, read
                    from the zero-shot probe output.

Metrics are computed on 100k surface samples and normalized by the source bbox
diagonal, so chamfer numbers are comparable across parts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from edge_aware_cad_planner_v1.cad_dsl import execute_dsl, extract_dsl_code, parse_dsl  # noqa: E402
from edge_aware_cad_planner_v1.geometry_summary import build_geometry_summary, render_cad_brief  # noqa: E402
from edge_aware_cad_planner_v1.llm_planner import chat_completions, text_model  # noqa: E402

DEFAULT_OUT = ROOT / "ours3/spatiallm_oracle_compare_v1"
PLANNER_OUT = ROOT / "ours3/edge_aware_cad_planner_v1"
PROBE_OUT = ROOT / "ours3/spatiallm_zeroshot_probe_v1"

# Byte-for-byte the instruction the SpatialLM probe was given, so route_A_min and
# route_B differ only in how the geometry reaches the model.
CAD_DSL_TASK = """Generate CAD construction sequence.

Allowed operations:
Sketch
Circle
Extrude
Revolve
Cut

Output only DSL.
"""


def sample_surface(mesh, n: int, seed: int) -> np.ndarray:
    import trimesh

    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    rng = np.random.default_rng(seed)
    pts, _ = trimesh.sample.sample_surface(mesh, n, seed=int(rng.integers(1 << 30)))
    return np.asarray(pts, dtype=np.float64)


def compare_meshes(source_path: Path, pred_path: Path, n: int = 100_000, seed: int = 0) -> dict:
    import trimesh
    from scipy.spatial import cKDTree

    src = trimesh.load(str(source_path), force="mesh")
    pred = trimesh.load(str(pred_path), force="mesh")
    diag = float(np.linalg.norm(src.bounds[1] - src.bounds[0]))

    a = sample_surface(src, n, seed)
    b = sample_surface(pred, n, seed + 1)
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]

    src_vol = float(abs(src.volume))
    pred_vol = float(abs(pred.volume))
    return {
        "bbox_diagonal_source": diag,
        "chamfer_l1_normalized": float((d_ab.mean() + d_ba.mean()) / 2 / diag),
        "hausdorff_95_normalized": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag),
        "coverage_frac_within_1pct_diag": float((d_ab < 0.01 * diag).mean()),
        "precision_frac_within_1pct_diag": float((d_ba < 0.01 * diag).mean()),
        "volume_source": src_vol,
        "volume_pred": pred_vol,
        "volume_ratio": pred_vol / src_vol if src_vol > 0 else None,
        "bbox_extent_source": (src.bounds[1] - src.bounds[0]).tolist(),
        "bbox_extent_pred": (pred.bounds[1] - pred.bounds[0]).tolist(),
    }


def build_and_score(name: str, raw_text: str, out_dir: Path, source_mesh: Path) -> dict:
    """Parse a DSL candidate, execute it, and measure it against the source mesh."""
    record = {"route": name, "raw": raw_text}
    route_dir = out_dir / name
    route_dir.mkdir(parents=True, exist_ok=True)
    (route_dir / "raw.txt").write_text(raw_text, encoding="utf-8")

    try:
        code = extract_dsl_code(raw_text)
        if not code.strip():
            raise ValueError("no DSL assignments found in output")
        program = parse_dsl(code)
    except Exception as exc:
        record["parsed"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
        return record
    record["parsed"] = True
    record["dsl"] = program.raw
    record["ops"] = sorted(
        {v["op"] for v in program.assignments.values() if isinstance(v, dict) and "op" in v}
    )
    (route_dir / "program.dsl").write_text(program.raw + "\n", encoding="utf-8")

    try:
        export = execute_dsl(program, route_dir / "result.step", route_dir / "result.stl")
    except Exception as exc:
        record["executed"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
        return record
    record["executed"] = True
    record["export"] = export

    try:
        record["metrics"] = compare_meshes(source_mesh, Path(export["stl"]))
    except Exception as exc:
        record["metrics_error"] = f"{type(exc).__name__}: {exc}"
    return record


def strip_edge_evidence(brief: str) -> str:
    """Keep bbox and PCA axis, drop everything derived from the edge field."""
    keep, dropping = [], False
    drop_sections = ("Edge information:", "Closed feature candidates", "Detected features:")
    for line in brief.splitlines():
        if any(line.startswith(s) for s in drop_sections):
            dropping = True
            continue
        if dropping:
            if line and not line.startswith((" ", "-")):
                dropping = False
            else:
                continue
        if "cylindrical ratio" in line or "planar ratio" in line or "dominant surface" in line:
            continue
        keep.append(line)
    return "\n".join(keep)


def route_a_min(brief: str) -> str:
    system = (
        "You are a CAD program generator. You receive geometry evidence extracted "
        "from a 3D scan of a mechanical part, not a point cloud. Emit only DSL, no prose.\n"
        "DSL ops:\n"
        "  Cylinder(radius=..., height=..., axis=(ax,ay,az), origin=(x,y,z))\n"
        "  Extrude(Circle(radius=...), height=..., axis=..., origin=...)\n"
        "  Revolve(radius=..., height=..., axis=..., origin=...)\n"
        "  Cut(a, b)\n"
        "End with `result = ...`. Units are SOURCE_NATIVE."
    )
    user = f"Geometry evidence:\n{brief.rstrip()}\n\n{CAD_DSL_TASK}"
    return chat_completions(
        [{"role": "system", "content": system}, {"role": "user", "content": user}]
    )


def load_route_b(part_id: str, model: str, variant: str) -> tuple[str, dict]:
    path = PROBE_OUT / part_id / model / "report.json"
    report = json.loads(path.read_text())
    for run in report["runs"]:
        if run["variant"] == variant and run["prompt_kind"] == "cad_dsl":
            return run["output"], {"source": str(path), "variant": variant, "model": model}
    raise SystemExit(f"no cad_dsl run for variant {variant} in {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part", default="PART_005")
    parser.add_argument("--dataset", type=Path, default=ROOT / "cad_spatial_dataset")
    parser.add_argument("--spatiallm-model", default="qwen0.5b")
    parser.add_argument("--spatiallm-variant", default="B_ours")
    parser.add_argument("--skip-api", action="store_true", help="reuse a previously saved route_A_min output")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    part_id = args.part
    part_dir = args.dataset / part_id
    out_dir = args.out / part_id
    out_dir.mkdir(parents=True, exist_ok=True)
    source_mesh = part_dir / "mesh.obj"

    summary = build_geometry_summary(part_dir)
    brief = render_cad_brief(summary)
    (out_dir / "cad_brief.txt").write_text(brief, encoding="utf-8")

    blind_brief = strip_edge_evidence(brief)
    (out_dir / "cad_brief_blind.txt").write_text(blind_brief, encoding="utf-8")

    candidates = {}
    for name, text in (("route_A_blind", blind_brief), ("route_A_min", brief)):
        cached = out_dir / name / "raw.txt"
        if args.skip_api and cached.is_file():
            candidates[name] = cached.read_text()
            continue
        try:
            candidates[name] = route_a_min(text)
        except Exception as exc:
            candidates[name] = ""
            print(f"{name} API call failed: {type(exc).__name__}: {exc}")

    planner_dsl = PLANNER_OUT / part_id / "program.dsl"
    if planner_dsl.is_file():
        candidates["route_A_full"] = planner_dsl.read_text()

    route_b_text, route_b_meta = load_route_b(part_id, args.spatiallm_model, args.spatiallm_variant)
    candidates["route_B"] = route_b_text

    results = [build_and_score(name, text, out_dir, source_mesh) for name, text in candidates.items()]

    report = {
        "part_id": part_id,
        "source_mesh": str(source_mesh),
        "cad_dsl_task": CAD_DSL_TASK,
        "route_A_min_model": text_model(),
        "route_B": route_b_meta,
        "detected_features": summary.get("detected_features"),
        "results": results,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")

    print(f"\npart {part_id}  source={source_mesh.name}")
    header = f"{'route':14s} {'parsed':>7s} {'exec':>6s} {'chamfer':>9s} {'hd95':>8s} {'vol_ratio':>10s}  ops"
    print(header)
    print("-" * len(header))
    for r in results:
        m = r.get("metrics") or {}
        print(
            f"{r['route']:14s} {str(r.get('parsed', False)):>7s} {str(r.get('executed', False)):>6s} "
            f"{m.get('chamfer_l1_normalized', float('nan')):9.5f} "
            f"{m.get('hausdorff_95_normalized', float('nan')):8.5f} "
            f"{(m.get('volume_ratio') if m.get('volume_ratio') is not None else float('nan')):10.4f}  "
            f"{','.join(r.get('ops', [])) or r.get('error', '')[:60]}"
        )
    print(f"\nwrote {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
