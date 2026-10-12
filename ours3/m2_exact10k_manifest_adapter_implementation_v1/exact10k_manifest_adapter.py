"""Thin EXACT10K -> official SpatialLM Dataset/Collator adapter.

This module does not tokenize, build labels, or implement geometry splicing.
It only converts frozen manifest rows into the ShareGPT descriptor consumed by
the official HuggingFace Dataset alignment and the official collator.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
FREEZE = ROOT / "ours3/clean10k_pool_merge_and_freeze_v1"
TARGETED = ROOT / "ours3/deepcad_official_targeted_full_clean_build_v1/shards"
PACK = ROOT / "cad_spatial_dataset"
CURVE_ROOT = ROOT / "ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2"


@dataclass(frozen=True)
class Exact10KRecord:
    cad_id: str
    dataset: str
    source_id: str
    split: str
    surface_path: Path
    target_path: Path
    curve_path: Path

    def descriptor(self, prompt: str) -> dict[str, Any]:
        return {
            "id": self.cad_id,
            "dataset": self.dataset.lower(),
            "sample_id": self.source_id,
            "conversations": [
                {"from": "human", "value": prompt},
                {"from": "gpt", "value": self.target_path.read_text()},
            ],
            "point_clouds": [str(self.surface_path)],
        }


class Exact10KManifestIndex:
    def __init__(self, manifest_dir: Path = FREEZE):
        self.manifest_dir = Path(manifest_dir)
        self.rows = [json.loads(x) for x in (self.manifest_dir / "EXACT10K_MANIFEST.jsonl").read_text().splitlines()]
        self.by_id = {r["cad_id"]: r for r in self.rows}
        if len(self.rows) != 10000 or len(self.by_id) != 10000:
            raise ValueError("EXACT10K manifest is not exactly 10000 unique rows")

    def split(self, name: str) -> list[Exact10KRecord]:
        return [self.resolve(r) for r in self.rows if r["split"] == name]

    def resolve(self, row: dict[str, Any]) -> Exact10KRecord:
        sid, dataset = row["source_id"], row["dataset"]
        if row["pool_origin"].startswith("targeted"):
            surface = TARGETED / "DeepCAD" / sid / "features_canonical.npy"
            target = TARGETED / "DeepCAD" / sid / "program_canonical.dsl"
            curve = TARGETED / "curve_tokens" / "deepcad" / sid / "curve_tokens.npy"
        else:
            pack = PACK / dataset / "geometry_pack_v1" / sid
            surface = pack / "surface_points.npy"
            target = pack / "cad_target.dsl"
            curve = CURVE_ROOT / dataset.lower() / sid / "curve_tokens.npy"
        return Exact10KRecord(row["cad_id"], dataset, sid, row["split"], surface, target, curve)

    def validate(self) -> dict[str, Any]:
        missing, schema_fail = [], []
        for row in self.rows:
            rec = self.resolve(row)
            for kind, path in (("surface", rec.surface_path), ("target", rec.target_path), ("curve", rec.curve_path)):
                if not path.is_file():
                    missing.append({"cad_id": rec.cad_id, "kind": kind, "path": str(path)})
            if rec.target_path.is_file() and "result" not in rec.target_path.read_text():
                schema_fail.append({"cad_id": rec.cad_id, "kind": "target_result_missing"})
        return {"total": len(self.rows), "resolved": len(self.rows) - len({x["cad_id"] for x in missing}), "missing": len(missing), "schema_fail": len(schema_fail), "missing_rows": missing[:20], "schema_rows": schema_fail[:20]}


def official_aligned_dataset(
    records: list[Exact10KRecord],
    prompt: str,
    template_name: str = "spatiallm_cad_llama_baseline",
):
    from datasets import Dataset
    from spatiallm.tuner.data.converter import align_dataset
    from spatiallm.tuner.data.loader import DatasetAttr
    from spatiallm.tuner.hparams.data_args import DataArguments

    raw = Dataset.from_list([r.descriptor(prompt) for r in records])
    attr = DatasetAttr("file", "exact10k", formatting="sharegpt", point_clouds="point_clouds", messages="conversations")
    args = DataArguments(template=template_name, cutoff_len=8192, media_dir=str(ROOT))
    training_args = SimpleNamespace(local_process_index=0)
    return align_dataset(raw, attr, args, training_args)


def official_collator(tokenizer, template, model=None, compute_dtype=None):
    import torch
    from spatiallm.tuner.data.collator import SFTDataCollatorWith4DAttentionMask
    if compute_dtype is None:
        compute_dtype = torch.float32
    return SFTDataCollatorWith4DAttentionMask(
        template=template,
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        compute_dtype=compute_dtype,
    )
