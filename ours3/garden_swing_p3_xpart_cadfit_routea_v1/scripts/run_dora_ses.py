#!/usr/bin/env python3
"""Dora SES on X-Part watertight meshes. Stops at salient-edge prior. No CAD."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import BLENDER_PY, CASE, DORA_DIR, XPART_DIR  # noqa: E402

SHARP_SAMPLE = DORA_DIR / "vendor/sharp_sample.py"
THRESHOLDS = (15, 25, 35, 45)
POINT_NUMBER = 65536


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


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


def stage_normalize(out: Path, xpart_input: Path, part_ids: list[str]) -> dict[str, dict]:
    transforms = {}
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        src = xpart_input / pid / f"complete_part_{idx:03d}.obj"
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
        str(BLENDER_PY),
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


def stage_postprocess(
    out: Path,
    xpart_input: Path,
    threshold: int,
    part_ids: list[str],
    transforms: dict[str, dict],
    skip_edge_json: bool = False,
) -> list[dict]:
    th_dir = out / f"threshold_{threshold}"
    rows = []
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        src_mesh_path = xpart_input / pid / f"complete_part_{idx:03d}.obj"
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
        write_json(part_out / "dora_salient_edge_manifest.json", row)
        if not skip_edge_json and edge_src.is_file():
            edge_data = np.load(part_out / "salient_edges_source_space.npz")
            edge_records = []
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
            write_json(part_out / "dora_salient_edges.json", edge_records)
        rows.append(row)
    return rows


def write_report(out: Path, meta: dict, all_rows: list[dict]) -> None:
    lines = [
        "# Dora SES on X-Part watertight meshes\n",
        "## Pipeline Flags",
        f"- P3_REEXECUTED: `{meta['P3_REEXECUTED']}`",
        f"- XPART_REEXECUTED: `{meta['XPART_REEXECUTED']}`",
        f"- DORA_VAE_USED: `{meta['DORA_VAE_USED']}`",
        f"- DORA_SES_USED: `{meta['DORA_SES_USED']}`",
        "",
        "## Input",
        f"- X-Part root: `{meta['XPART_INPUT']}`",
        f"- Parts: {', '.join(meta['CANARY_PARTS'])}",
        f"- Thresholds: {meta['THRESHOLDS']}",
        "",
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
            "Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.",
            "Route A CADFit does not read these files.",
        ]
    )
    (out / "report/report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DORA_DIR)
    parser.add_argument("--xpart-input", type=Path, default=XPART_DIR)
    parser.add_argument("--all-parts", action="store_true")
    parser.add_argument("--thresholds", type=int, nargs="+", default=list(THRESHOLDS))
    parser.add_argument("--parts", type=str, nargs="+")
    parser.add_argument("--skip-edge-json", action="store_true")
    args = parser.parse_args()

    out = args.output_dir
    xpart_input = Path(args.xpart_input)
    out.mkdir(parents=True, exist_ok=True)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    if not SHARP_SAMPLE.is_file():
        raise FileNotFoundError(SHARP_SAMPLE)
    if not BLENDER_PY.is_file():
        raise FileNotFoundError(BLENDER_PY)

    summary_path = CASE / "artifacts/xpart_summary.json"
    if summary_path.is_file():
        part_rows = json.loads(summary_path.read_text(encoding="utf-8"))["parts"]
        all_ids = [r["part_id"] for r in part_rows]
    else:
        all_ids = [p.name for p in sorted(xpart_input.glob("PART_*")) if p.is_dir()]

    if args.parts:
        part_ids = args.parts
    else:
        part_ids = all_ids

    meta = {
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "DORA_VAE_USED": False,
        "DORA_SES_USED": True,
        "CADFIT_USED": False,
        "XPART_INPUT": str(xpart_input),
        "CANARY_PARTS": part_ids,
        "THRESHOLDS": args.thresholds,
        "POINT_NUMBER": POINT_NUMBER,
        "BLENDER_PYTHON": str(BLENDER_PY),
        "SHARP_SAMPLE": str(SHARP_SAMPLE),
    }
    write_json(out / "pipeline_manifest.json", meta)

    t0 = time.time()
    transforms = stage_normalize(out, xpart_input, part_ids)
    all_rows = []
    for threshold in args.thresholds:
        print(f"[dora] threshold={threshold} parts={len(part_ids)}", flush=True)
        run_sharp_sample(out, threshold, part_ids)
        rows = stage_postprocess(
            out, xpart_input, threshold, part_ids, transforms, skip_edge_json=args.skip_edge_json
        )
        all_rows.extend(rows)
        write_json(out / f"threshold_{threshold}/summary.json", rows)

    meta["runtime_seconds"] = time.time() - t0
    meta["parts_processed"] = len(part_ids)
    meta["threshold_runs"] = len(args.thresholds)
    write_json(out / "pipeline_manifest.json", meta)
    (out / "report").mkdir(parents=True, exist_ok=True)
    write_json(out / "report/summary.json", all_rows)
    write_report(out, meta, all_rows)
    print(f"Done. Output: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
