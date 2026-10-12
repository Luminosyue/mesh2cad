from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
REPO = ROOT / "PhysX-Omni"
CKPT = ROOT / "PhysX-Omni/pretrain"
PROMPT = REPO / "dataset/example_64_finetune_rle.txt"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return None if not value or value.lower() in {"n/a", "none", "null", "unknown"} else value


def parse(text: str) -> dict:
    def field(name: str) -> str | None:
        match = re.search(rf"(?im)^\s*{re.escape(name)}\s*:\s*(.*?)\s*$", text)
        return clean(match.group(1)) if match else None

    parts: list[dict] = []
    groups: list[dict] = []
    section = None
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
                values = [clean(item) for item in match.group(2).split("|")]
                values += [None] * (7 - len(values))
                parts.append({
                    "part_id": match.group(1),
                    "part_name": values[0],
                    "description": values[6],
                    "raw": match.group(2),
                })
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
        "semantic_prior_is_soft": True,
        "measured_dimensions_modified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", nargs="+", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    import torch
    from PIL import Image
    from qwen_vl_utils import process_vision_info
    from transformers import (
        AutoTokenizer,
        Qwen2VLImageProcessor,
        Qwen2VLVideoProcessor,
        Qwen2_5_VLForConditionalGeneration,
        Qwen2_5_VLProcessor,
    )

    started = time.time()
    images = [path.resolve() for path in args.images]
    if any(not path.is_file() for path in images):
        raise FileNotFoundError([str(path) for path in images if not path.is_file()])
    tokenizer = AutoTokenizer.from_pretrained(CKPT, local_files_only=True)
    processor = Qwen2_5_VLProcessor(
        image_processor=Qwen2VLImageProcessor(size={"shortest_edge": 65536, "longest_edge": 262144}),
        tokenizer=tokenizer,
        video_processor=Qwen2VLVideoProcessor(size={"shortest_edge": 65536, "longest_edge": 262144}),
        chat_template=tokenizer.chat_template,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        CKPT,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
        device_map="auto",
        local_files_only=True,
    )
    model.eval()
    loaded = [Image.open(path).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS) for path in images]
    prompt = PROMPT.read_text(encoding="utf-8")
    content = [{"type": "image", "image": image} for image in loaded]
    content.append({"type": "text", "text": prompt})
    messages = [{"role": "user", "content": content}]
    chat = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[chat], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        ids = model.generate(**inputs, do_sample=False, max_new_tokens=2048)
    trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, ids)]
    raw = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    raw_path = args.output_dir / "raw/basic_info.txt"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw, encoding="utf-8")
    parsed = parse(raw)
    dump(args.output_dir / "physx_global.json", parsed)
    dump(args.output_dir / "physx_part_hypotheses.json", {"hypotheses": parsed["parts"], "soft_prior_only": True})
    provenance = {
        "PHYSX_RAN": True,
        "success": bool(raw.strip()) and parsed["PHYSX_OUTPUT_PARSED"],
        "repo": str(REPO),
        "checkpoint": str(CKPT),
        "input_images": [str(path) for path in images],
        "input_sha256_list": [sha(path) for path in images],
        "source_obj_directly_read_by_physx": False,
        "network_used": False,
        "semantic_prior_is_soft": True,
        "elapsed_seconds": time.time() - started,
    }
    dump(args.output_dir / "provenance.json", provenance)
    print(json.dumps(provenance, indent=2))
    return 0 if provenance["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
