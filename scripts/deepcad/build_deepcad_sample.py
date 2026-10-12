#!/usr/bin/env python3
"""End-to-end: DeepCAD JSON → DSL → STEP → mesh → Dora spatial pack."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def _cleanup_sample_staging(sample_dir: Path, sample_id: str) -> None:
    for rel in (
        "_spatial",
        "vis",
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
    json_path: Path,
    output_root: Path,
    sample_id: str | None = None,
    num_points: int = 8192,
    allow_occ_fallback: bool = True,
    no_vis: bool = False,
) -> dict:
    json_path = json_path.resolve()
    sample_id = sample_id or json_path.stem.replace("/", "_")
    sample_dir = output_root / "DeepCAD" / "train" / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    source_json = sample_dir / "source.json"
    if json_path != source_json:
        shutil.copy2(json_path, source_json)

    dsl_path = sample_dir / "program.dsl"
    step_path = sample_dir / "model.step"
    stl_path = sample_dir / "model.stl"
    obj_path = sample_dir / "model.obj"
    meta_path = sample_dir / "meta.json"

    report: dict = {
        "sample_id": sample_id,
        "sample_dir": str(sample_dir),
        "source_json": str(source_json),
        "pipeline": [],
    }

    # Step 1-2: DeepCAD JSON → DSL
    from deepcad_to_dsl import convert_file

    dsl_report = convert_file(source_json, dsl_path)
    report["pipeline"].append({"step": "deepcad_to_dsl", **dsl_report})

    # Step 3: DSL → STEP
    from dsl_to_occ import run_dsl_to_occ

    occ_report = run_dsl_to_occ(
        dsl_path,
        step_path,
        stl_path,
        source_json=source_json if allow_occ_fallback else None,
    )
    report["pipeline"].append({"step": "dsl_to_occ", **occ_report})

    # Step 4: STEP → OBJ (also keep STL)
    from step_to_mesh import step_to_mesh

    mesh_report = step_to_mesh(step_path, obj_path, stl_path=stl_path)
    report["pipeline"].append({"step": "step_to_mesh", **mesh_report})

    # Step 5: OBJ → Dora → xyz+normal+edge_score
    # build_cad_spatial_part rewrites non-PART_* ids to mesh stem; stage a named STL first.
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
        "DeepCAD",
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
    report["pipeline"].append(
        {
            "step": "dora_spatial",
            "stdout_tail": proc.stdout[-2000:],
        }
    )

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

    spatial_meta_path = part_spatial / "meta.json"
    spatial_meta = {}
    if spatial_meta_path.exists():
        spatial_meta = json.loads(spatial_meta_path.read_text(encoding="utf-8"))

    report.update(
        {
            "program_dsl": str(dsl_path),
            "model_step": str(step_path),
            "model_obj": str(obj_path),
            "points_npy": str(sample_dir / "points.npy"),
            "normals_npy": str(sample_dir / "normals.npy"),
            "edge_score_npy": str(sample_dir / "edge_score.npy"),
            "ok": True,
        }
    )

    meta = {
        "sample_id": sample_id,
        "source": "DeepCAD",
        "deepcad_json": str(source_json),
        "program_dsl": str(dsl_path),
        "model_step": str(step_path),
        "model_obj": str(obj_path),
        "conversion": dsl_report,
        "occ": occ_report,
        "mesh": mesh_report,
        "spatial": spatial_meta,
    }
    _write_json(meta_path, meta)

    # Offline CAD canonical contract (same T for points + DSL)
    try:
        from cad_canonical import build_sample_canonical

        canon = build_sample_canonical(sample_dir)
        report["canonical"] = canon
        meta["canonical"] = canon
        _write_json(meta_path, meta)
    except Exception as e:
        report["canonical_error"] = str(e)

    try:
        sys.path.insert(0, str(SCRIPTS / "cad_spatial"))
        from qa_sample import run_sample_qa

        qa = run_sample_qa(sample_dir, source_json=source_json, write=True)
        report["qa"] = qa
        meta["qa"] = qa
        _write_json(meta_path, meta)
    except Exception as e:
        report["qa_error"] = str(e)

    _cleanup_sample_staging(sample_dir, sample_id)

    report["meta_json"] = str(meta_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one DeepCAD spatial sample")
    parser.add_argument("--json", type=Path, required=True, help="DeepCAD source JSON")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "cad_spatial_dataset",
        help="Dataset root (sample goes under DeepCAD/train/)",
    )
    parser.add_argument("--sample-id", type=str, default=None)
    parser.add_argument("--num-points", type=int, default=8192)
    parser.add_argument(
        "--no-vis",
        action="store_true",
        help="Skip visualization PNG generation (faster)",
    )
    parser.add_argument(
        "--no-occ-fallback",
        action="store_true",
        help="Do not fall back to DeepCAD pythonocc if DSL execution fails",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    report = build_sample(
        args.json,
        args.output,
        sample_id=args.sample_id,
        num_points=args.num_points,
        allow_occ_fallback=not args.no_occ_fallback,
        no_vis=args.no_vis,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
