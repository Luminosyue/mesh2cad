#!/usr/bin/env python3
"""End-to-end: Fusion360 JSON → DSL → official STEP/OBJ → Dora → canonical + QA."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
RECON_DIR = ROOT / "cad_spatial_dataset/Fusion360/reconstruction/reconstruction"


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def _resolve_source_paths(sample_id: str, json_path: Path | None) -> tuple[Path, Path, Path, Path]:
    if json_path is None:
        json_path = RECON_DIR / f"{sample_id}.json"
    step_path = RECON_DIR / f"{sample_id}.step"
    obj_path = RECON_DIR / f"{sample_id}.obj"
    if not json_path.exists():
        raise FileNotFoundError(f"missing source JSON: {json_path}")
    if not step_path.exists():
        raise FileNotFoundError(f"missing official STEP: {step_path}")
    if not obj_path.exists():
        raise FileNotFoundError(f"missing official OBJ: {obj_path}")
    return json_path, step_path, obj_path, json_path


def _cleanup_sample_staging(sample_dir: Path, sample_id: str) -> None:
    """Remove staging artifacts not required by the unified dataset layout."""
    for rel in (
        "_spatial",
        "vis",
        "_qa_dsl.step",
        "_qa_dsl.stl",
        f"{sample_id}.stl",
        "mesh.obj",
        "points.npy",
        "normals.npy",
        "edge_score.npy",
    ):
        path = sample_dir / rel
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()


def build_sample(
    sample_id: str,
    output_root: Path,
    json_path: Path | None = None,
    num_points: int = 8192,
    run_qa: bool = True,
    no_vis: bool = False,
) -> dict:
    json_path, official_step, official_obj, _ = _resolve_source_paths(sample_id, json_path)
    sample_dir = output_root / "Fusion360" / "train" / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    source_json = sample_dir / "source.json"
    if json_path != source_json:
        shutil.copy2(json_path, source_json)

    dsl_path = sample_dir / "program.dsl"
    step_path = sample_dir / "model.step"
    obj_path = sample_dir / "model.obj"
    stl_path = sample_dir / "model.stl"
    meta_path = sample_dir / "meta.json"

    report: dict = {
        "sample_id": sample_id,
        "sample_dir": str(sample_dir),
        "pipeline": [],
    }

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fusion360_to_dsl import Fusion360FilterError, convert_file

    try:
        dsl_report = convert_file(source_json, dsl_path)
        report["pipeline"].append({"step": "fusion360_to_dsl", **dsl_report})
    except Fusion360FilterError as exc:
        report["ok"] = False
        report["filter_reason"] = exc.reason
        _write_json(meta_path, report)
        return report

    # Prefer official Fusion360 geometry (no DSL remesh for training mesh).
    shutil.copy2(official_step, step_path)
    shutil.copy2(official_obj, obj_path)
    report["pipeline"].append(
        {
            "step": "official_geometry",
            "step_src": str(official_step),
            "obj_src": str(official_obj),
        }
    )

    # STL for Dora front-end
    import trimesh

    mesh = trimesh.load(str(obj_path), force="mesh", process=True)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    mesh.export(stl_path)
    report["pipeline"].append({"step": "obj_to_stl", "vertices": len(mesh.vertices), "faces": len(mesh.faces)})

    # Verify DSL executes (QA mesh), but do not replace official STEP/OBJ.
    sys.path.insert(0, str(SCRIPTS / "deepcad"))
    from dsl_to_occ import run_dsl_to_occ

    dsl_step = sample_dir / "_qa_dsl.step"
    dsl_stl = sample_dir / "_qa_dsl.stl"
    occ_report = run_dsl_to_occ(dsl_path, dsl_step, dsl_stl, source_json=None)
    report["pipeline"].append({"step": "dsl_to_occ_qa", **occ_report})

    spatial_stl = sample_dir / f"{sample_id}.stl"
    shutil.copy2(stl_path, spatial_stl)
    spatial_dir = sample_dir / "_spatial"
    spatial_cmd = [
        sys.executable,
        str(SCRIPTS / "build_cad_spatial_part.py"),
        "--mesh",
        str(spatial_stl),
        "--part-id",
        sample_id,
        "--source",
        "Fusion360",
        "--output",
        str(spatial_dir),
        "--num-points",
        str(num_points),
        "--no-adaptive",
        "--threshold",
        "45",
    ]
    if no_vis:
        spatial_cmd.append("--no-vis")
    proc = subprocess.run(
        spatial_cmd,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"build_cad_spatial_part failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
        )
    report["pipeline"].append({"step": "dora_spatial", "stdout_tail": proc.stdout[-2000:]})

    part_spatial = spatial_dir / sample_id
    for name in ("points.npy", "normals.npy", "edge_score.npy", "features.npy", "mesh.obj"):
        src = part_spatial / name
        if src.exists():
            shutil.copy2(src, sample_dir / name)

    dora_src = part_spatial / "dora"
    dora_dst = sample_dir / "dora"
    if dora_src.exists():
        if dora_dst.exists():
            shutil.rmtree(dora_dst)
        shutil.copytree(dora_src, dora_dst)

    vis_src = part_spatial / "vis"
    if vis_src.exists():
        vis_dst = sample_dir / "vis"
        if vis_dst.exists():
            shutil.rmtree(vis_dst)
        shutil.copytree(vis_src, vis_dst)

    spatial_meta = {}
    spatial_meta_path = part_spatial / "meta.json"
    if spatial_meta_path.exists():
        spatial_meta = json.loads(spatial_meta_path.read_text(encoding="utf-8"))

    meta = {
        "sample_id": sample_id,
        "source": "Fusion360",
        "fusion360_json": str(source_json),
        "program_dsl": str(dsl_path),
        "model_step": str(step_path),
        "model_obj": str(obj_path),
        "geometry_source": "official",
        "conversion": dsl_report,
        "occ_qa": occ_report,
        "spatial": spatial_meta,
    }

    try:
        from cad_canonical import build_sample_canonical

        canon = build_sample_canonical(sample_dir)
        meta["canonical"] = canon
        report["canonical"] = canon
    except Exception as exc:
        report["canonical_error"] = str(exc)

    report.update(
        {
            "program_dsl": str(dsl_path),
            "model_step": str(step_path),
            "model_obj": str(obj_path),
            "ok": True,
        }
    )

    if run_qa:
        sys.path.insert(0, str(SCRIPTS / "cad_spatial"))
        from qa_sample import run_sample_qa

        qa = run_sample_qa(sample_dir, reference_mesh=stl_path, write=True)
        report["qa"] = qa
        meta["qa"] = qa
        report["ok"] = bool(qa.get("passed"))

    _cleanup_sample_staging(sample_dir, sample_id)

    _write_json(meta_path, meta)
    report["meta_json"] = str(meta_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one Fusion360 spatial sample")
    parser.add_argument("--sample-id", type=str, required=True)
    parser.add_argument("--json", type=Path, default=None, help="Override source JSON path")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "cad_spatial_dataset",
        help="Dataset root (sample goes under Fusion360/train/)",
    )
    parser.add_argument("--num-points", type=int, default=8192)
    parser.add_argument("--no-vis", action="store_true")
    parser.add_argument("--no-qa", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(SCRIPTS / "deepcad"))
    report = build_sample(
        args.sample_id,
        args.output,
        json_path=args.json,
        num_points=args.num_points,
        run_qa=not args.no_qa,
        no_vis=args.no_vis,
    )
    print(json.dumps(report, indent=2))
    if report.get("filter_reason"):
        return 2
    if report.get("qa") and not report["qa"].get("passed"):
        return 3
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
