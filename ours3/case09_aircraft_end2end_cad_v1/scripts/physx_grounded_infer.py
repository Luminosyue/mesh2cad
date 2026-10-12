#!/usr/bin/env python3
"""Run PhysX-Omni on CASE09 grounded views without touching the frozen audit.

Whole-object: three camera-orbit images together.
Each P3 part: whole isometric + context + close-up, answer stored under that p3_part_id.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
OUT = OURS3 / "case09_aircraft_end2end_cad_v1"
DEST = OUT / "01_part_discovery/physx_grounded"
REPO = ROOT / "PhysX-Omni"
CKPT = REPO / "pretrain"
PROMPT = REPO / "dataset/example_64_finetune_rle.txt"
sys.path.insert(0, str(REPO / "qwen-vl-utils/src"))

WHOLE_PREFIX = (
    "The following images show the SAME manufactured object from different camera "
    "viewpoints. Only the camera moved; the object was not rotated. Prefer manufactured "
    "product / toy / vehicle categories over animals when the silhouette is ambiguous. "
    "Use all views together.\n\n"
)
PART_PREFIX = (
    "The first image is the complete manufactured object. The second image highlights ONE "
    "P3-SAM segment in place (orange) against a ghost of the whole object. The third image "
    "is that same segment isolated. The object was not rotated. Describe THIS segment only "
    "as a single part l_0. Keep the object Name/Category consistent with the whole object.\n\n"
)


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def clean(value):
    if value is None:
        return None
    value = value.strip()
    return None if not value or value.lower() in {"n/a", "none", "null", "unknown"} else value


def parse(text: str) -> dict:
    def field(name):
        match = re.search(rf"(?im)^\s*{re.escape(name)}\s*:\s*(.*?)\s*$", text)
        return clean(match.group(1)) if match else None

    parts, groups, section = [], [], None
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r"(?i)^parts\s*:", line):
            section = "parts"
            continue
        if re.match(r"(?i)^group_info\s*:", line):
            section = "groups"
            continue
        if section == "parts":
            match = re.match(r"^(l_\d+)\s*:\s*(.+)$", line, re.I)
            if match:
                values = [clean(x) for x in match.group(2).split("|")] + [None] * 7
                parts.append(
                    {
                        "part_id": match.group(1),
                        "part_name": values[0],
                        "affordance_rank": values[1],
                        "material_name": values[2],
                        "description": values[6],
                        "raw": match.group(2),
                    }
                )
        elif section == "groups":
            match = re.match(r"^(group_\d+)\s*:\s*(.+)$", line, re.I)
            if match:
                groups.append({"group_id": match.group(1), "raw": match.group(2)})
    return {
        "PHYSX_OUTPUT_PARSED": bool(field("Name") or field("Category") or parts or groups),
        "object_name": field("Name"),
        "object_category": field("Category"),
        "dimension_raw": field("Dimension"),
        "parts": parts,
        "group_info_raw": groups,
        "confidence": None,
        "semantic_prior_is_soft": True,
        "measured_dimensions_modified": False,
        "physical_scale_used_as_hard_constraint": False,
    }


def generate(model, processor, image_paths: list[Path], prefix: str) -> tuple[str, int, int]:
    from PIL import Image
    from qwen_vl_utils import process_vision_info

    loaded = [Image.open(path).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS) for path in image_paths]
    prompt = prefix + PROMPT.read_text()
    content = [{"type": "image", "image": image} for image in loaded]
    content.append({"type": "text", "text": prompt})
    messages = [{"role": "user", "content": content}]
    chat = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[chat], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(model.device)
    with __import__("torch").inference_mode():
        ids = model.generate(**inputs, do_sample=False, max_new_tokens=2048)
    trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, ids)]
    raw = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    return raw, int(inputs.input_ids.shape[-1]), int(trimmed[0].shape[-1])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEST / "artifacts/view_manifest.json")
    parser.add_argument("--skip-parts", action="store_true")
    args = parser.parse_args()
    manifest = load(args.manifest)

    import torch
    from transformers import AutoTokenizer, Qwen2VLImageProcessor, Qwen2VLVideoProcessor, Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLProcessor

    started = time.time()
    min_pixels, max_pixels = 65536, 262144
    tokenizer = AutoTokenizer.from_pretrained(CKPT, local_files_only=True)
    processor = Qwen2_5_VLProcessor(
        image_processor=Qwen2VLImageProcessor(size={"shortest_edge": min_pixels, "longest_edge": max_pixels}),
        tokenizer=tokenizer,
        video_processor=Qwen2VLVideoProcessor(size={"shortest_edge": min_pixels, "longest_edge": max_pixels}),
        chat_template=tokenizer.chat_template,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        CKPT, torch_dtype=torch.bfloat16, attn_implementation="sdpa", device_map="auto", local_files_only=True
    )
    model.eval()

    whole_paths = [Path(path) for path in manifest["whole_object_prompt_images"]]
    raw, in_tokens, out_tokens = generate(model, processor, whole_paths, WHOLE_PREFIX)
    (DEST / "raw").mkdir(parents=True, exist_ok=True)
    (DEST / "raw/whole_basic_info.txt").write_text(raw, encoding="utf-8")
    parsed = parse(raw)
    dump(DEST / "physx_global.json", parsed)

    part_rows = []
    if not args.skip_parts:
        for row in manifest["parts"]:
            part_id = int(row["p3_part_id"])
            part_raw, _, _ = generate(model, processor, [Path(path) for path in row["prompt_images"]], PART_PREFIX)
            (DEST / f"raw/part_{part_id:03d}.txt").write_text(part_raw, encoding="utf-8")
            part_parsed = parse(part_raw)
            names = [item.get("part_name") for item in part_parsed.get("parts", []) if item.get("part_name")]
            part_rows.append(
                {
                    "p3_part_id": part_id,
                    "triangle_count": row["triangle_count"],
                    "object_name": part_parsed.get("object_name"),
                    "object_category": part_parsed.get("object_category"),
                    "part_name": names[0] if names else None,
                    "parts": part_parsed.get("parts", []),
                    "raw_path": str(DEST / f"raw/part_{part_id:03d}.txt"),
                    "closeup": row["closeup"],
                    "context": row["context"],
                    "semantic_prior_is_soft": True,
                }
            )
            dump(DEST / f"parts/part_{part_id:03d}_hypothesis.json", part_rows[-1])

    dump(
        DEST / "physx_part_hypotheses.json",
        {
            "schema": "CASE09_PHYSX_P3_ALIGNED_HYPOTHESES_V1",
            "soft_prior_only": True,
            "physical_scale_used_as_hard_constraint": False,
            "object_rotation": "NONE",
            "whole_object": parsed,
            "p3_parts": part_rows,
        },
    )
    provenance = {
        "PHYSX_RAN": True,
        "success": bool(parsed["PHYSX_OUTPUT_PARSED"]),
        "repo": str(REPO),
        "checkpoint": str(CKPT),
        "checkpoint_index_sha256": sha(CKPT / "model.safetensors.index.json"),
        "input_images": [str(path) for path in whole_paths],
        "input_sha256_list": [sha(path) for path in whole_paths],
        "source_obj_directly_read_by_physx": False,
        "object_rotated": False,
        "geometry_modified": False,
        "semantic_prior_is_soft": True,
        "p3_part_count": len(part_rows),
        "input_tokens": in_tokens,
        "output_tokens": out_tokens,
        "elapsed_seconds": time.time() - started,
        "network_used": False,
        "frozen_physx_dir_overwritten": False,
    }
    dump(DEST / "provenance.json", provenance)
    print(json.dumps({"object_name": parsed.get("object_name"), "object_category": parsed.get("object_category"), "p3_named": len(part_rows), "DEST": str(DEST)}, indent=2))
    return 0 if provenance["success"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        path = DEST / "logs/physx_grounded_exception.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(traceback.format_exc(), encoding="utf-8")
        raise
