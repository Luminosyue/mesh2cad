#!/usr/bin/env python3
"""End-to-end: CADFS FeatureScript → DSL → STEP → tessellate → Dora spatial pack.

Same 7-channel contract as DeepCAD / Fusion360 cad_spatial samples:
  JSON/FS → DSL → STEP → mesh.obj/stl → Dora SES (dihedral > 45°)
  → 8192 pts xyz+normal+edge_score (features.npy).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CADFS_FS = ROOT / "CADFS" / "featurescript_rp"
CADFS_STEP = ROOT / "CADFS" / "step"


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def resolve_cadfs_paths(sample_id: str, fs_path: Path | None = None) -> tuple[Path, Path]:
    sid = sample_id
    bucket = sid[:4] if len(sid) >= 4 else sid
    if fs_path is None:
        fs_path = CADFS_FS / bucket / f"{sid}.txt"
    step = CADFS_STEP / bucket / f"{sid}.step"
    if not step.exists():
        step = CADFS_STEP / bucket / f"{sid}.STEP"
    if not fs_path.exists():
        raise FileNotFoundError(f"missing FeatureScript: {fs_path}")
    if not step.exists():
        raise FileNotFoundError(f"missing official STEP: {step}")
    return Path(fs_path), Path(step)


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
    sample_id: str,
    output_root: Path,
    fs_path: Path | None = None,
    num_points: int = 8192,
    no_vis: bool = False,
    run_qa: bool = True,
) -> dict:
    fs_path, official_step = resolve_cadfs_paths(sample_id, fs_path)
    sample_dir = output_root / "CADFS" / "train" / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    source_fs = sample_dir / "source.featurescript.txt"
    if fs_path.resolve() != source_fs.resolve():
        shutil.copy2(fs_path, source_fs)

    dsl_path = sample_dir / "program.dsl"
    step_path = sample_dir / "model.step"
    stl_path = sample_dir / "model.stl"
    obj_path = sample_dir / "model.obj"
    meta_path = sample_dir / "meta.json"

    report: dict = {
        "sample_id": sample_id,
        "sample_dir": str(sample_dir),
        "source_featurescript": str(source_fs),
        "official_step": str(official_step),
        "pipeline": [],
    }

    sys.path.insert(0, str(SCRIPTS))
    from canonical_cad_data_v4.converters.cadfs_to_dsl import CadfsUnsupported, cadfs_to_dsl

    text = source_fs.read_text(encoding="utf-8", errors="replace")
    try:
        dsl_text, dsl_report = cadfs_to_dsl(text)
    except CadfsUnsupported as exc:
        report["ok"] = False
        report["filter_reason"] = exc.reason
        _write_json(meta_path, report)
        return report

    dsl_path.write_text(dsl_text, encoding="utf-8")
    report["pipeline"].append({"step": "cadfs_to_dsl", **dsl_report})

    sys.path.insert(0, str(SCRIPTS / "deepcad"))
    from dsl_to_occ import run_dsl_to_occ

    occ_report = run_dsl_to_occ(dsl_path, step_path, stl_path, source_json=None)
    report["pipeline"].append({"step": "dsl_to_occ", **occ_report})

    from step_to_mesh import step_to_mesh

    mesh_report = step_to_mesh(step_path, obj_path, stl_path=stl_path)
    report["pipeline"].append({"step": "step_to_mesh", **mesh_report})

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
        "CADFS",
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
    proc = subprocess.run(spatial_cmd, capture_output=True, text=True)
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

    report.update(
        {
            "program_dsl": str(dsl_path),
            "model_step": str(step_path),
            "model_obj": str(obj_path),
            "ok": True,
        }
    )

    meta = {
        "sample_id": sample_id,
        "source": "CADFS",
        "cadfs_featurescript": str(source_fs),
        "official_step": str(official_step),
        "program_dsl": str(dsl_path),
        "model_step": str(step_path),
        "model_obj": str(obj_path),
        "geometry_source": "dsl_reconstructed",
        "conversion": dsl_report,
        "occ": occ_report,
        "mesh": mesh_report,
        "spatial": spatial_meta,
    }

    try:
        from cad_canonical import build_sample_canonical

        canon = build_sample_canonical(sample_dir)
        report["canonical"] = canon
        meta["canonical"] = canon
    except Exception as exc:
        report["canonical_error"] = str(exc)

    if run_qa:
        # Same contract as DeepCAD: Dora points come from DSL-reconstructed
        # tessellation, QA re-executes DSL against that stored mesh.
        sys.path.insert(0, str(SCRIPTS / "cad_spatial"))
        from qa_sample import run_sample_qa

        qa = run_sample_qa(sample_dir, reference_mesh=obj_path, write=True)
        report["qa"] = qa
        meta["qa"] = qa
        report["ok"] = bool(qa.get("passed"))

    _cleanup_sample_staging(sample_dir, sample_id)
    _write_json(meta_path, meta)
    report["meta_json"] = str(meta_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one CADFS spatial sample")
    parser.add_argument("--sample-id", type=str, required=True)
    parser.add_argument("--featurescript", type=Path, default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "cad_spatial_dataset",
        help="Dataset root (sample goes under CADFS/train/)",
    )
    parser.add_argument("--num-points", type=int, default=8192)
    parser.add_argument("--no-vis", action="store_true")
    parser.add_argument("--no-qa", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(SCRIPTS / "deepcad"))
    report = build_sample(
        args.sample_id,
        args.output,
        fs_path=args.featurescript,
        num_points=args.num_points,
        no_vis=args.no_vis,
        run_qa=not args.no_qa,
    )
    print(json.dumps(report, indent=2))
    if report.get("filter_reason"):
        return 2
    if report.get("qa") and not report["qa"].get("passed"):
        return 3
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
