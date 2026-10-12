#!/usr/bin/env python3
"""ShareGPT records pointing at the separate_edge_tokens_v1 cache.

`point_clouds` entries reference `surface_points.npy`; the mm_plugin resolves
`edge_points.npy` from the same directory. This lets the experiment run through
the repository's normal LlamaFactory training path in addition to the
standalone trainer.

Existing dataset json files and `dataset_info.json` entries are left untouched;
only new `deepcad_cad_sepedge_*` names are added.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT / "cad_spatial_dataset/DeepCAD/separate_edge_tokens_v1"
TRAIN_DIR = ROOT / "cad_spatial_dataset/DeepCAD/train"
OUTPUT_DIR = ROOT / "cad_spatial_dataset/DeepCAD"

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""
POINT_CLOUD_PLACEHOLDER = "<point_cloud>"


def load_dsl(sample_id: str) -> str:
    text = (TRAIN_DIR / sample_id / "program_canonical.dsl").read_text(encoding="utf-8").strip()
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    return "\n".join(lines).strip() + "\n"


def build_records(sample_ids: list[str]) -> list[dict]:
    records = []
    for sid in sample_ids:
        surface = CACHE_DIR / sid / "surface_points.npy"
        edge = CACHE_DIR / sid / "edge_points.npy"
        dsl = TRAIN_DIR / sid / "program_canonical.dsl"
        if not (surface.is_file() and edge.is_file() and dsl.is_file()):
            continue
        records.append(
            {
                "id": sid,
                "conversations": [
                    {
                        "from": "human",
                        "value": f"{POINT_CLOUD_PLACEHOLDER}\n{CAD_INSTRUCTION.strip()}",
                    },
                    {"from": "gpt", "value": load_dsl(sid)},
                ],
                "point_clouds": [f"separate_edge_tokens_v1/{sid}/surface_points.npy"],
            }
        )
    return records


def update_dataset_info(output_dir: Path, names: list[str]) -> None:
    path = output_dir / "dataset_info.json"
    info = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    for name in names:
        info[name] = {
            "file_name": f"{name}.json",
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "point_clouds": "point_clouds"},
        }
    path.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train-ids", type=Path, required=True)
    ap.add_argument("--val-ids", type=Path, default=None)
    ap.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    ap.add_argument("--name-suffix", type=str, default="overfit100")
    args = ap.parse_args()

    def read_ids(p: Path) -> list[str]:
        return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]

    written = {}
    names = []
    train_name = f"deepcad_cad_sepedge_{args.name_suffix}_train"
    train_records = build_records(read_ids(args.train_ids))
    (args.output_dir / f"{train_name}.json").write_text(
        json.dumps(train_records, indent=2) + "\n", encoding="utf-8"
    )
    written[train_name] = len(train_records)
    names.append(train_name)

    if args.val_ids and args.val_ids.is_file():
        val_name = f"deepcad_cad_sepedge_{args.name_suffix}_val"
        val_records = build_records(read_ids(args.val_ids))
        (args.output_dir / f"{val_name}.json").write_text(
            json.dumps(val_records, indent=2) + "\n", encoding="utf-8"
        )
        written[val_name] = len(val_records)
        names.append(val_name)

    update_dataset_info(args.output_dir, names)
    print(json.dumps({"written": written, "dataset_info_updated": names}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
