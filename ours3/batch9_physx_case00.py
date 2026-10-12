#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "batch9_fullstack_mesh2cad_mac_v6/01_upstream/CASE_00/physx"
OLD = ROOT / "fusion_pipeline/cases/REAL_03/physx"
REPO = ROOT / "external/PhysX-Omni"
CKPT = Path("/data/home/cuiyuehan/project/mesh2cad/PhysX-Omni/pretrain")
PROMPT = REPO / "dataset/example_64_finetune_rle.txt"
COMMIT = "46fa1cd0b6883d4d14431d51c3326ef80a85ef64"


def sha(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    import torch
    from PIL import Image
    from qwen_vl_utils import process_vision_info
    from transformers import AutoTokenizer, Qwen2VLImageProcessor, Qwen2VLVideoProcessor, Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLProcessor

    source_image = OLD / "render/REAL_03.png"
    dest = OUT / "input/CASE_00.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_image, dest)
    shutil.copy2(OLD / "render/render_metadata.json", OUT / "input/render_metadata.json")
    input_manifest = {"case": "CASE_00", "source_render": str(source_image), "copied_input": str(dest), "sha256": sha(dest), "bytes": dest.stat().st_size, "adapter": "PHYSX_SINGLE_VIEW_ISOMETRIC_V0_REUSE", "manual_view_crop_or_background_change": False}
    dump(OUT / "input/input_manifest.json", input_manifest)

    min_pixels, max_pixels = 65536, 262144
    tokenizer = AutoTokenizer.from_pretrained(CKPT, local_files_only=True)
    image_processor = Qwen2VLImageProcessor(size={"shortest_edge": min_pixels, "longest_edge": max_pixels})
    video_processor = Qwen2VLVideoProcessor(size={"shortest_edge": min_pixels, "longest_edge": max_pixels})
    processor = Qwen2_5_VLProcessor(image_processor=image_processor, tokenizer=tokenizer, video_processor=video_processor, chat_template=tokenizer.chat_template)
    processor_audit = {"construction": "OFFICIAL_CLASS_EXPLICIT_OFFLINE_CONSTRUCTION", "processor_class": type(processor).__name__, "tokenizer_class": type(tokenizer).__name__, "image_processor_class": type(image_processor).__name__, "video_processor_class": type(video_processor).__name__, "min_pixels": min_pixels, "max_pixels": max_pixels, "chat_template_nonempty": bool(processor.chat_template), "network_used": False, "transformers_version": __import__("transformers").__version__}
    started = time.time()
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(CKPT, torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2", device_map="auto", local_files_only=True)
    model.eval()
    image = Image.open(dest).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS)
    messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": PROMPT.read_text(encoding="utf-8")}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        ids = model.generate(**inputs, do_sample=False, max_new_tokens=2048)
    trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, ids)]
    raw = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    raw_path = OUT / "raw/basic_info.txt"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("run_physx", ROOT / "batch_real_mesh2cad_v1/scripts/run_physx.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    parsed = module.parse_basic(raw)
    dump(OUT / "understanding/physx_understanding.json", parsed)
    provenance = {"case": "CASE_00", "repo": str(REPO), "commit": COMMIT, "checkpoint": str(CKPT), "model_class": type(model).__name__, "processor_construction": processor_audit, "generation": {"do_sample": False, "max_new_tokens": 2048, "input_tokens": int(inputs.input_ids.shape[-1]), "output_tokens": int(trimmed[0].shape[-1])}, "raw_sha256": sha(raw_path), "input": input_manifest, "network_used": False, "mac_called": False, "p3_called": False, "geometry_or_class_modified": False, "elapsed_seconds": time.time() - started}
    dump(OUT / "provenance/provenance.json", provenance)
    dump(OUT / "run.log", {"case": "CASE_00", "attempted": True, "success": bool(raw.strip()) and parsed["PHYSX_OUTPUT_PARSED"], "parsed": parsed["PHYSX_OUTPUT_PARSED"], "object_name": parsed["object_name"], "object_category": parsed["object_category"], "part_count": len(parsed["parts"]), "group_count": len(parsed["group_info_raw"])})
    print(json.dumps({"PHYSX_RERUN": True, "PHYSX_OUTPUT_PARSED": parsed["PHYSX_OUTPUT_PARSED"], "object_name": parsed["object_name"], "part_count": len(parsed["parts"])}, indent=2))
    if not parsed["PHYSX_OUTPUT_PARSED"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
