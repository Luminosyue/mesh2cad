#!/usr/bin/env python3
"""Create an immutable filename-normalized view of the official Llama base."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib

ROOT = pathlib.Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE = ROOT / "SpatialLM/models/Llama-3.2-1B-Instruct"
OUT = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/official_llama_base"
FILES = {
    "config.json": "config (2).json",
    "generation_config.json": "generation_config (2).json",
    "model.safetensors": "model (2).safetensors",
    "special_tokens_map.json": "special_tokens_map (2).json",
    "tokenizer.json": "tokenizer (2).json",
    "tokenizer_config.json": "tokenizer_config (2).json",
}


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    manifest = {"source": str(SOURCE), "files": {}, "status": "OFFICIAL_ORIGINAL_FILENAME_NORMALIZED_SYMLINK_VIEW"}
    for canonical, original in FILES.items():
        src = SOURCE / original
        dst = OUT / canonical
        if not src.is_file():
            raise FileNotFoundError(src)
        os.symlink(src, dst)
        manifest["files"][canonical] = {"source_name": original, "size": src.stat().st_size, "sha256": sha(src)}
    (OUT / "OFFICIAL_BASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
