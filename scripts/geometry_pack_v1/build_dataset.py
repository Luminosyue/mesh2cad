#!/usr/bin/env python3
"""Build geometry_pack_v1 for DeepCAD or Fusion360.

CAD target is copied from train/<id>/program_canonical.dsl and is never
recomputed from mesh or sampled points. All ablation branches must point at
the same cad_target.dsl.

Input contract is frozen (same for both datasets):
  surface_points.npy  [8192, 6]  xyz+normal
  edge_points_*.npy   [1024, 6]
Do not change N, channels, or add UV / face-id to the training tensors.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from geometry_pack_v1.constants import (  # noqa: E402
    DEFAULT_SEED,
    EXPERIMENT,
    NUM_EDGE_POINTS,
    NUM_SURFACE_POINTS,
    SHARP_ANGLE_DEG,
)
from geometry_pack_v1.pack import build_one  # noqa: E402

REQUIRED_SOURCE_FILES = (
    "model.step",
    "program_canonical.dsl",
    "coordinate_transform.json",
    "source.json",
)

DATASETS = {
    "deepcad": {
        "train_dir": ROOT / "cad_spatial_dataset/DeepCAD/train",
        "out_dir": ROOT / "cad_spatial_dataset/DeepCAD/geometry_pack_v1",
        "sharegpt_stem": "deepcad_cad_geometry_pack_v1_surface",
    },
    "fusion360": {
        "train_dir": ROOT / "cad_spatial_dataset/Fusion360/train",
        "out_dir": ROOT / "cad_spatial_dataset/Fusion360/geometry_pack_v1",
        "sharegpt_stem": "fusion360_cad_geometry_pack_v1_surface",
    },
}

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""


def scan_source_ids(train_dir: Path) -> tuple[list[str], list[dict]]:
    """Return complete sample ids and incomplete records."""
    complete, missing = [], []
    if not train_dir.is_dir():
        return [], [{"error": f"missing train dir {train_dir}"}]
    for p in sorted(train_dir.iterdir()):
        if not p.is_dir():
            continue
        miss = [f for f in REQUIRED_SOURCE_FILES if not (p / f).is_file()]
        if miss:
            missing.append({"sample_id": p.name, "missing": miss})
        else:
            complete.append(p.name)
    return complete, missing


def write_manifest(path: Path, *, split: str, train_dir: Path) -> dict:
    ids, missing = scan_source_ids(train_dir)
    obj = {
        "split": split,
        "train_dir": str(train_dir),
        "required_files": list(REQUIRED_SOURCE_FILES),
        "selected": len(ids),
        "missing_geometry": missing,
        "sample_ids": ids,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return obj


def _ids_from_manifest(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [sid.replace("/", "_") for sid in data.get("sample_ids", [])]


def _dsl_label(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    return "\n".join(lines).strip() + "\n"


def write_sharegpt(out_root: Path, metas: list[dict], dest: Path) -> Path:
    """Surface-only ShareGPT that still uses the frozen CAD target."""
    records = []
    for m in metas:
        sid = m["sample_id"]
        dsl = out_root / sid / "cad_target.dsl"
        surf = out_root / sid / "surface_points.npy"
        if not dsl.is_file() or not surf.is_file():
            continue
        records.append(
            {
                "id": sid,
                "conversations": [
                    {
                        "from": "human",
                        "value": f"<point_cloud>\n{CAD_INSTRUCTION.strip()}",
                    },
                    {"from": "gpt", "value": _dsl_label(dsl)},
                ],
                "point_clouds": [f"{EXPERIMENT}/{sid}/surface_points.npy"],
            }
        )
    dest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return dest


def _build_job(payload: dict) -> dict:
    """Process-pool worker. Re-imports so spawn/fork both work."""
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, payload["scripts"])
    from geometry_pack_v1.pack import build_one as _build_one

    sid = payload["sid"]
    try:
        meta = _build_one(
            _Path(payload["sample_dir"]),
            _Path(payload["out_root"]),
            num_surface=payload["num_surface"],
            num_edge=payload["num_edge"],
            sharp_angle_deg=payload["sharp_angle_deg"],
            seed=payload["seed"],
            overwrite=payload["overwrite"],
        )
        return {"status": "ok", "sample_id": sid, "meta": meta}
    except Exception as exc:  # noqa: BLE001
        return {"status": "fail", "sample_id": sid, "error": f"{type(exc).__name__}: {exc}"}


def _summarize(ok: list[dict], failed: list[dict], ids: list[str], args, out_dir: Path) -> dict:
    hashes = [m["cad_target"]["cad_target_sha256"] for m in ok]
    summary = {
        "experiment": EXPERIMENT,
        "dataset": args.dataset,
        "out_dir": str(out_dir),
        "train_dir": str(args.train_dir),
        "requested": len(ids),
        "built": len(ok),
        "failed": len(failed),
        "num_surface": args.num_surface,
        "num_edge": args.num_edge,
        "surface_channels": 6,
        "edge_channels": 6,
        "sharp_angle_deg": args.sharp_angle_deg,
        "seed": args.seed,
        "tessellation_frozen": True,
        "cad_target_unique_hashes": len(set(hashes)),
        "failures": failed,
        "contract": {
            "surface_points": [args.num_surface, 6],
            "edge_points": [args.num_edge, 6],
            "no_uv_on_surface": True,
            "no_face_id_on_surface": True,
        },
    }
    if ok:
        summary["surface_shape"] = ok[0]["surface_shape"]
        summary["mesh_verts_median"] = float(np.median([m["mesh"]["vertices"] for m in ok]))
        summary["mesh_sharp_segments_median"] = float(
            np.median([m["mesh_sharp_edge"]["num_segments"] for m in ok])
        )
        summary["brep_topo_all_median"] = float(
            np.median([m["brep_gt_edge_all"]["num_topo_edges"] for m in ok])
        )
        summary["brep_topo_sharp_median"] = float(
            np.median([m["brep_gt_edge_sharp"]["num_topo_edges_sharp"] for m in ok])
        )
        summary["method1_oracle_default"] = "edge_points_gt_sharp.npy"
        summary["method1_detected_default"] = "edge_points_detected.npy"
        summary["sharp_predicate"] = "dihedral_deg > sharp_angle_deg"
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", choices=sorted(DATASETS), default=None,
                    help="Preset train-dir / output-root (deepcad | fusion360).")
    ap.add_argument("--train-dir", type=Path, default=None)
    ap.add_argument("--out-dir", "--output-root", dest="out_dir", type=Path, default=None)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--write-manifest", type=Path, default=None,
                    help="Scan train-dir and write a full manifest, then exit.")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--num-surface", type=int, default=NUM_SURFACE_POINTS)
    ap.add_argument("--num-edge", type=int, default=NUM_EDGE_POINTS)
    ap.add_argument("--sharp-angle-deg", type=float, default=SHARP_ANGLE_DEG)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--write-sharegpt", action="store_true")
    ap.add_argument("--sharegpt-name", type=str, default=None)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    if args.dataset is None:
        blob = " ".join(str(x) for x in (args.out_dir, args.train_dir, args.manifest) if x)
        args.dataset = "fusion360" if "Fusion360" in blob else "deepcad"
    preset = DATASETS[args.dataset]
    args.train_dir = args.train_dir or preset["train_dir"]
    args.out_dir = args.out_dir or preset["out_dir"]

    if args.num_surface != NUM_SURFACE_POINTS or args.num_edge != NUM_EDGE_POINTS:
        raise SystemExit(
            f"Refusing to change frozen contract: surface={NUM_SURFACE_POINTS}x6 "
            f"edge={NUM_EDGE_POINTS}x6 (got {args.num_surface}/{args.num_edge})"
        )

    if args.write_manifest is not None:
        obj = write_manifest(args.write_manifest, split="train", train_dir=args.train_dir)
        print(json.dumps({k: obj[k] for k in obj if k != "sample_ids"}, indent=2))
        print(f"wrote {args.write_manifest} n={obj['selected']}")
        return 0

    if args.manifest is not None and args.manifest.is_file():
        ids = _ids_from_manifest(args.manifest)
    else:
        ids, _miss = scan_source_ids(args.train_dir)
    if args.limit is not None:
        ids = ids[: args.limit]

    args.out_dir.mkdir(parents=True, exist_ok=True)

    payloads = [
        {
            "sid": sid,
            "sample_dir": str(args.train_dir / sid),
            "out_root": str(args.out_dir),
            "scripts": str(SCRIPTS),
            "num_surface": args.num_surface,
            "num_edge": args.num_edge,
            "sharp_angle_deg": args.sharp_angle_deg,
            "seed": args.seed,
            "overwrite": args.overwrite,
        }
        for sid in ids
    ]

    ok, failed = [], []
    workers = max(1, int(args.workers))
    if workers == 1 or len(payloads) <= 1:
        for i, payload in enumerate(payloads):
            rec = _build_job(payload)
            if rec["status"] == "ok":
                ok.append(rec["meta"])
                m = rec["meta"]
                print(
                    f"[{i + 1}/{len(ids)}] ok {rec['sample_id']} "
                    f"V={m['mesh']['vertices']} F={m['mesh']['faces']} "
                    f"mesh_sharp={m['mesh_sharp_edge']['num_segments']} "
                    f"brep_all={m['brep_gt_edge_all']['num_topo_edges']} "
                    f"brep_sharp={m['brep_gt_edge_sharp']['num_topo_edges_sharp']}",
                    flush=True,
                )
            else:
                failed.append({"sample_id": rec["sample_id"], "error": rec["error"]})
                print(f"[{i + 1}/{len(ids)}] FAIL {rec['sample_id']}: {rec['error']}", flush=True)
    else:
        done = 0
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_build_job, p): p["sid"] for p in payloads}
            for fut in as_completed(futs):
                done += 1
                rec = fut.result()
                if rec["status"] == "ok":
                    ok.append(rec["meta"])
                    m = rec["meta"]
                    print(
                        f"[{done}/{len(ids)}] ok {rec['sample_id']} "
                        f"V={m['mesh']['vertices']} F={m['mesh']['faces']} "
                        f"mesh_sharp={m['mesh_sharp_edge']['num_segments']} "
                        f"brep_all={m['brep_gt_edge_all']['num_topo_edges']} "
                        f"brep_sharp={m['brep_gt_edge_sharp']['num_topo_edges_sharp']}",
                        flush=True,
                    )
                else:
                    failed.append({"sample_id": rec["sample_id"], "error": rec["error"]})
                    print(f"[{done}/{len(ids)}] FAIL {rec['sample_id']}: {rec['error']}", flush=True)

    summary = _summarize(ok, failed, ids, args, args.out_dir)
    (args.out_dir / "build_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    if args.write_sharegpt and ok:
        stem = args.sharegpt_name or preset["sharegpt_stem"]
        sp = write_sharegpt(args.out_dir, ok, args.out_dir.parent / f"{stem}.json")
        summary["sharegpt"] = str(sp)
        print(f"sharegpt: {sp}", flush=True)
        (args.out_dir / "build_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({k: summary[k] for k in summary if k != "failures"}, indent=2))
    if failed:
        print(json.dumps({"failures": failed[:20], "n_failures": len(failed)}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
