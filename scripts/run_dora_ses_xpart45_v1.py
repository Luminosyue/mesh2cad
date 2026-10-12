#!/usr/bin/env python3
"""Dora SES adapter on frozen X-Part 45 watertight meshes (canary v1)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART_INPUT = ROOT / "ours3/p3_xpart_frozen45_v1/xpart"
OUT_ROOT = ROOT / "ours3/dora_ses_xpart45_v1"
SHARP_SAMPLE = OUT_ROOT / "vendor/sharp_sample.py"
BLENDER_PYTHON = Path("/data/home/hhfzhang/.conda/envs/blender/bin/python")
THRESHOLDS = (15, 25, 35, 45)
POINT_NUMBER = 65536


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def pca_shape_stats(mesh: trimesh.Trimesh) -> dict:
    verts = mesh.vertices - mesh.vertices.mean(axis=0)
    cov = np.cov(verts.T)
    s = np.linalg.eigvalsh(cov)
    s = np.sort(s)[::-1]
    s = s / (s.sum() + 1e-12)
    bounds = mesh.bounds
    ext = bounds[1] - bounds[0]
    aspect = float(ext.max() / (ext.min() + 1e-12))
    return {"pca_ratios": s.tolist(), "aspect_ratio": aspect}


def select_canaries(part_rows: list[dict], xpart_dir: Path, count: int = 5) -> dict:
    scored = []
    for row in part_rows:
        pid = row["part_id"]
        mesh_path = xpart_dir / pid / f"complete_part_{int(pid.split('_')[1]):03d}.obj"
        if not mesh_path.is_file():
            mesh_path = xpart_dir / pid / "generated_mesh.obj"
        if not mesh_path.is_file():
            continue
        mesh = trimesh.load(mesh_path, force="mesh", process=False)
        stats = pca_shape_stats(mesh)
        scored.append({**row, **stats, "mesh_path": str(mesh_path)})
    if not scored:
        return {"selected": [], "details": {}}

    planar = max(scored, key=lambda r: (1.0 - r["pca_ratios"][2]) * r["surface_area"])
    rotational = max(
        scored,
        key=lambda r: (1.0 - abs(r["pca_ratios"][0] - r["pca_ratios"][1]))
        * (1.0 / (r["aspect_ratio"] + 1e-6)),
    )
    thin = max(scored, key=lambda r: r["pca_ratios"][0] / (r["pca_ratios"][2] + 1e-6))
    largest = max(scored, key=lambda r: r["surface_area"])
    smallest = min(scored, key=lambda r: r["surface_area"])

    picks = {
        "CANARY_A_PLANAR": planar,
        "CANARY_B_ROTATIONAL": rotational,
        "CANARY_C_THIN": thin,
        "CANARY_D_LARGEST": largest,
        "CANARY_E_SMALLEST": smallest,
    }
    selected = []
    seen = set()
    for label, row in picks.items():
        pid = row["part_id"]
        if pid in seen:
            continue
        seen.add(pid)
        selected.append({"label": label, "part_id": pid, **row})
    if len(selected) < count:
        extras = sorted(
            [r for r in scored if r["part_id"] not in seen],
            key=lambda r: -r["surface_area"],
        )
        for row in extras:
            if len(selected) >= count:
                break
            seen.add(row["part_id"])
            selected.append({"label": "CANARY_EXTRA", "part_id": row["part_id"], **row})
    return {"selected": selected[:count], "details": picks}


def normalize_mesh(mesh: trimesh.Trimesh, part_id: str) -> tuple[trimesh.Trimesh, dict]:
    bbox_min, bbox_max = mesh.bounds
    center = (bbox_min + bbox_max) / 2.0
    extent = bbox_max - bbox_min
    scale = 2.0 / float(np.max(extent))
    verts = (mesh.vertices - center) * scale
    norm_mesh = trimesh.Trimesh(vertices=verts, faces=mesh.faces, process=False)
    transform = {
        "part_id": part_id,
        "center": center.tolist(),
        "scale": scale,
        "T_xpart_to_dora": {"subtract_center": center.tolist(), "multiply_scale": scale},
        "T_dora_to_xpart": {"divide_scale": scale, "add_center": center.tolist()},
    }
    return norm_mesh, transform


def stage_normalize(out: Path, part_ids: list[str]) -> dict[str, dict]:
    transforms = {}
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        src = XPART_INPUT / pid / f"complete_part_{idx:03d}.obj"
        mesh = trimesh.load(src, force="mesh", process=False)
        norm_mesh, transform = normalize_mesh(mesh, pid)
        norm_path = out / "normalized" / f"{pid}.obj"
        norm_path.parent.mkdir(parents=True, exist_ok=True)
        norm_mesh.export(norm_path)
        write_json(out / "normalized" / pid / "transform.json", transform)
        transforms[pid] = transform
    write_json(out / "normalized/manifest.json", transforms)
    return transforms


def run_sharp_sample(out: Path, threshold: int, part_ids: list[str]) -> None:
    th_dir = out / f"threshold_{threshold}"
    json_path = th_dir / "watertight_path.json"
    mesh_paths = [str((out / "normalized" / f"{pid}.obj").resolve()) for pid in part_ids]
    write_json(json_path, mesh_paths)

    sharp_point_path = th_dir / "sharp_point_ply"
    sample_path = th_dir / "sample"
    edge_path = th_dir / "parts"
    sharp_point_path.mkdir(parents=True, exist_ok=True)
    sample_path.mkdir(parents=True, exist_ok=True)
    edge_path.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(BLENDER_PYTHON),
        str(SHARP_SAMPLE),
        "--json_file_path",
        str(json_path),
        "--point_number",
        str(POINT_NUMBER),
        "--angle_threshold",
        str(threshold),
        "--sharp_point_path",
        str(sharp_point_path),
        "--sample_path",
        str(sample_path),
        "--edge_path",
        str(edge_path),
    ]
    log_path = out / "logs" / f"sharp_sample_{threshold}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"sharp_sample failed for threshold {threshold}, see {log_path}")


def inverse_transform_points(points: np.ndarray, transform: dict) -> np.ndarray:
    scale = transform["scale"]
    center = np.asarray(transform["center"], dtype=np.float64)
    return points / scale + center


def stage_postprocess(out: Path, threshold: int, part_ids: list[str], transforms: dict[str, dict], skip_edge_json: bool = False) -> list[dict]:
    th_dir = out / f"threshold_{threshold}"
    rows = []
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        src_mesh_path = XPART_INPUT / pid / f"complete_part_{idx:03d}.obj"
        mesh = trimesh.load(src_mesh_path, force="mesh", process=False)
        transform = transforms[pid]

        part_out = th_dir / pid
        part_out.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out / "normalized" / pid / "transform.json", part_out / "transform.json")

        edge_src = th_dir / "parts" / pid / "salient_edges.npz"
        sample_src = th_dir / "sample" / pid / "dora_samples.npz"
        ply_src = th_dir / "sharp_point_ply" / pid / "salient_points.ply"

        if edge_src.is_file():
            shutil.copy2(edge_src, part_out / "salient_edges.npz")
        if sample_src.is_file():
            shutil.copy2(sample_src, part_out / "dora_samples.npz")
        if ply_src.is_file():
            shutil.copy2(ply_src, part_out / "salient_points.ply")

        row = {
            "part_id": pid,
            "threshold_deg": threshold,
            "source": "DORA_SES",
            "cad_edge": None,
            "has_salient_edges": edge_src.is_file(),
            "has_dora_samples": sample_src.is_file(),
            "has_salient_points_ply": ply_src.is_file(),
        }

        if edge_src.is_file():
            edge_data = np.load(edge_src)
            edge_idx = edge_data["edge_vertex_indices"]
            dihedral = edge_data["edge_dihedral_deg"]
            v0 = mesh.vertices[edge_idx[:, 0]]
            v1 = mesh.vertices[edge_idx[:, 1]]
            edge_length = np.linalg.norm(v1 - v0, axis=1)
            np.savez(
                part_out / "salient_edges_source_space.npz",
                edge_vertex_indices=edge_idx.astype(np.int32),
                edge_xyz0=v0.astype(np.float32),
                edge_xyz1=v1.astype(np.float32),
                dihedral_deg=dihedral.astype(np.float32),
                edge_length=edge_length.astype(np.float32),
                source=np.array(["DORA_SES"] * len(edge_idx)),
            )
            row.update(
                {
                    "num_salient_edges": int(len(edge_idx)),
                    "dihedral_deg_mean": float(np.mean(dihedral)),
                    "dihedral_deg_p95": float(np.percentile(dihedral, 95)),
                    "edge_length_mean": float(np.mean(edge_length)),
                    "edge_length_p95": float(np.percentile(edge_length, 95)),
                }
            )
        else:
            row["num_salient_edges"] = 0

        if sample_src.is_file():
            sample = np.load(sample_src)
            if "fps_sharp_surface" in sample:
                sharp_pts = sample["fps_sharp_surface"].reshape(-1, 6)[:, :3]
                sharp_src = inverse_transform_points(sharp_pts, transform)
                np.savez(
                    part_out / "dora_samples_source_space.npz",
                    fps_sharp_surface=sharp_src.astype(np.float32),
                    transform=transform,
                )
                row["num_fps_sharp_points"] = int(len(sharp_src))

        edge_records = []
        if edge_src.is_file() and not skip_edge_json:
            edge_data = np.load(part_out / "salient_edges_source_space.npz")
            for i in range(len(edge_data["edge_vertex_indices"])):
                edge_records.append(
                    {
                        "edge_id": i,
                        "v0": int(edge_data["edge_vertex_indices"][i, 0]),
                        "v1": int(edge_data["edge_vertex_indices"][i, 1]),
                        "dihedral_deg": float(edge_data["dihedral_deg"][i]),
                        "length": float(edge_data["edge_length"][i]),
                        "source": "DORA_SES",
                        "cad_edge": None,
                    }
                )
        write_json(part_out / "dora_salient_edge_manifest.json", row)
        if not skip_edge_json:
            write_json(part_out / "dora_salient_edges.json", edge_records)
        rows.append(row)
    return rows


def write_report(out: Path, meta: dict, all_rows: list[dict]) -> None:
    lines = [
        "# Dora SES on X-Part 45 Watertight Meshes (Canary V1)\n",
        "## Pipeline Flags",
        f"- P3_REEXECUTED: `{meta['P3_REEXECUTED']}`",
        f"- XPART_REEXECUTED: `{meta['XPART_REEXECUTED']}`",
        f"- DORA_VAE_USED: `{meta['DORA_VAE_USED']}`",
        f"- DORA_SES_USED: `{meta['DORA_SES_USED']}`",
        "",
        "## Input",
        f"- X-Part root: `{meta['XPART_INPUT']}`",
        f"- Canary parts: {', '.join(meta['CANARY_PARTS'])}",
        f"- Thresholds: {meta['THRESHOLDS']}",
        "",
        "## Per-part Summary",
        "| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in all_rows:
        lines.append(
            f"| {row['part_id']} | {row['threshold_deg']} | {row.get('num_salient_edges', 0)} | "
            f"{row.get('dihedral_deg_p95', 'n/a')} | {row.get('edge_length_p95', 'n/a')} |"
        )
    lines.extend(
        [
            "",
            "## Output Layout",
            "- `normalized/PART_XXX.obj` + `transform.json`",
            "- `threshold_*/PART_XXX/salient_edges.npz` (Dora norm space)",
            "- `threshold_*/PART_XXX/salient_edges_source_space.npz` (X-Part space)",
            "- `threshold_*/PART_XXX/dora_samples.npz` (official Dora SES)",
            "- `threshold_*/PART_XXX/salient_points.ply`",
            "",
            "## Note",
            "Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.",
        ]
    )
    (out / "report/report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    global XPART_INPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT_ROOT)
    parser.add_argument("--xpart-input", type=Path, default=XPART_INPUT)
    parser.add_argument("--xpart-summary", type=Path, default=None)
    parser.add_argument("--all-parts", action="store_true", help="Run all 45 parts instead of 5 canaries")
    parser.add_argument("--thresholds", type=int, nargs="+", default=list(THRESHOLDS))
    parser.add_argument("--parts", type=str, nargs="+", help="Explicit part IDs to process")
    parser.add_argument("--skip-edge-json", action="store_true", help="Skip bulky per-edge JSON (V1 default writes it)")
    args = parser.parse_args()

    out = args.output_dir
    xpart_input = Path(args.xpart_input)
    out.mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    (out / "vendor").mkdir(parents=True, exist_ok=True)
    if not SHARP_SAMPLE.is_file():
        raise FileNotFoundError(SHARP_SAMPLE)
    if not BLENDER_PYTHON.is_file():
        raise FileNotFoundError(f"Blender python not found: {BLENDER_PYTHON}")

    summary_path = args.xpart_summary or (ROOT / "ours3/p3_xpart_frozen45_v1/artifacts/xpart_summary.json")
    if Path(summary_path).is_file():
        part_rows = json.loads(Path(summary_path).read_text(encoding="utf-8"))["parts"]
    else:
        part_rows = [{"part_id": p.name} for p in sorted(xpart_input.glob("PART_*")) if p.is_dir()]

    if args.parts:
        part_ids = args.parts
        canary_info = {"selected": [{"part_id": pid} for pid in part_ids], "details": {}}
        append_mode = True
    elif args.all_parts:
        append_mode = False
        part_ids = [r["part_id"] for r in part_rows]
        canary_info = {"selected": [{"part_id": pid} for pid in part_ids], "details": {}}
    else:
        append_mode = False
        canary_info = select_canaries(part_rows, xpart_input, count=5)
        part_ids = [item["part_id"] for item in canary_info["selected"]]

    meta = {
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "DORA_VAE_USED": False,
        "DORA_SES_USED": True,
        "XPART_INPUT": str(xpart_input),
        "CANARY_PARTS": part_ids,
        "THRESHOLDS": args.thresholds,
        "POINT_NUMBER": POINT_NUMBER,
        "BLENDER_PYTHON": str(BLENDER_PYTHON),
        "SHARP_SAMPLE": str(SHARP_SAMPLE),
    }
    write_json(out / "canary_selection.json", canary_info)
    write_json(out / "pipeline_manifest.json", meta)

    t0 = time.time()
    XPART_INPUT = xpart_input
    transforms = stage_normalize(out, part_ids)
    all_rows = []
    for threshold in args.thresholds:
        run_sharp_sample(out, threshold, part_ids)
        rows = stage_postprocess(out, threshold, part_ids, transforms, skip_edge_json=args.skip_edge_json)
        all_rows.extend(rows)
        write_json(out / f"threshold_{threshold}/summary.json", rows)

    meta["runtime_seconds"] = time.time() - t0
    meta["parts_processed"] = len(part_ids)
    meta["threshold_runs"] = len(args.thresholds)
    write_json(out / "pipeline_manifest.json", meta)
    write_json(out / "report/summary.json", all_rows)
    write_report(out, meta, all_rows)
    print(f"Done. Output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
