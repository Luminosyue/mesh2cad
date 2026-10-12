#!/usr/bin/env python3
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

os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OURS3 = ROOT / 'ours3'
OUT = OURS3 / 'case09_aircraft_end2end_cad_v1'
REPO = ROOT / 'PhysX-Omni'
CKPT = REPO / 'pretrain'
PROMPT = REPO / 'dataset/example_64_finetune_rle.txt'
IMAGE = OUT / '01_part_discovery/physx/input/CASE_09_AIRCRAFT_REBUILD.png'
MULTI_VIEW_PREFIX = (
    'The following images show the SAME manufactured object from different camera '
    'viewpoints. Only the camera moved; the object was not rotated. Use all views together.\n\n'
)
sys.path.insert(0, str(REPO / 'qwen-vl-utils/src'))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def clean(value):
    if value is None:
        return None
    value = value.strip()
    return None if not value or value.lower() in {'n/a', 'none', 'null', 'unknown'} else value


def parse(text: str) -> dict:
    def field(name):
        match = re.search(rf'(?im)^\s*{re.escape(name)}\s*:\s*(.*?)\s*$', text)
        return clean(match.group(1)) if match else None
    parts, groups, section = [], [], None
    for raw in text.splitlines():
        line = raw.strip()
        if re.match(r'(?i)^parts\s*:', line):
            section = 'parts'; continue
        if re.match(r'(?i)^group_info\s*:', line):
            section = 'groups'; continue
        if section == 'parts':
            match = re.match(r'^(l_\d+)\s*:\s*(.+)$', line, re.I)
            if match:
                values = [clean(x) for x in match.group(2).split('|')] + [None] * 7
                parts.append({'part_id': match.group(1), 'part_name': values[0], 'affordance_rank': values[1], 'material_name': values[2], 'description': values[6], 'raw': match.group(2)})
        elif section == 'groups':
            match = re.match(r'^(group_\d+)\s*:\s*(.+)$', line, re.I)
            if match:
                groups.append({'group_id': match.group(1), 'raw': match.group(2)})
    return {
        'PHYSX_OUTPUT_PARSED': bool(field('Name') or field('Category') or parts or groups),
        'object_name': field('Name'), 'object_category': field('Category'),
        'dimension_raw': field('Dimension'), 'parts': parts,
        'group_info_raw': groups, 'confidence': None,
        'semantic_prior_is_soft': True, 'measured_dimensions_modified': False,
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--images', nargs='+', type=Path, default=[IMAGE], help='one or more camera-orbit PNGs; object must not be rotated')
    parser.add_argument('--output-dir', type=Path, default=OUT / '01_part_discovery/physx', help='write parsed PhysX outputs here; use a new folder to avoid overwriting the frozen CASE09 audit')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    import torch
    from PIL import Image
    from qwen_vl_utils import process_vision_info
    from transformers import AutoTokenizer, Qwen2VLImageProcessor, Qwen2VLVideoProcessor, Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLProcessor

    images = [path.resolve() for path in args.images]
    missing = [str(path) for path in images if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing)
    out_dir = args.output_dir
    started = time.time()
    min_pixels, max_pixels = 65536, 262144
    tokenizer = AutoTokenizer.from_pretrained(CKPT, local_files_only=True)
    processor = Qwen2_5_VLProcessor(
        image_processor=Qwen2VLImageProcessor(size={'shortest_edge': min_pixels, 'longest_edge': max_pixels}),
        tokenizer=tokenizer,
        video_processor=Qwen2VLVideoProcessor(size={'shortest_edge': min_pixels, 'longest_edge': max_pixels}),
        chat_template=tokenizer.chat_template,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        CKPT, torch_dtype=torch.bfloat16, attn_implementation='sdpa',
        device_map='auto', local_files_only=True,
    )
    model.eval()
    loaded = [Image.open(path).convert('RGB').resize((512, 512), Image.Resampling.LANCZOS) for path in images]
    prompt = PROMPT.read_text()
    if len(loaded) > 1:
        prompt = MULTI_VIEW_PREFIX + prompt
    content = [{'type': 'image', 'image': image} for image in loaded]
    content.append({'type': 'text', 'text': prompt})
    messages = [{'role': 'user', 'content': content}]
    chat = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[chat], images=image_inputs, videos=video_inputs, padding=True, return_tensors='pt').to(model.device)
    with torch.inference_mode():
        ids = model.generate(**inputs, do_sample=False, max_new_tokens=2048)
    trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, ids)]
    raw = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    raw_path = out_dir / 'raw/basic_info.txt'
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw, encoding='utf-8')
    parsed = parse(raw)
    dump(out_dir / 'physx_global.json', parsed)
    dump(out_dir / 'physx_part_hypotheses.json', {'hypotheses': parsed['parts'], 'group_hypotheses': parsed['group_info_raw'], 'soft_prior_only': True})
    provenance = {
        'PHYSX_RAN': True, 'success': bool(raw.strip()) and parsed['PHYSX_OUTPUT_PARSED'],
        'repo': str(REPO), 'checkpoint': str(CKPT), 'checkpoint_index_sha256': sha(CKPT / 'model.safetensors.index.json'),
        'input_image': str(images[0]), 'input_images': [str(path) for path in images],
        'input_sha256': sha(images[0]), 'input_sha256_list': [sha(path) for path in images],
        'source_obj_directly_read_by_physx': False,
        'model_class': type(model).__name__, 'processor_class': type(processor).__name__,
        'do_sample': False, 'input_tokens': int(inputs.input_ids.shape[-1]),
        'output_tokens': int(trimmed[0].shape[-1]), 'elapsed_seconds': time.time() - started,
        'network_used': False, 'geometry_modified': False, 'object_rotated': False,
        'semantic_prior_is_soft': True,
    }
    dump(out_dir / 'provenance.json', provenance)
    print(json.dumps(provenance, indent=2))
    return 0 if provenance['success'] else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        path = OUT / 'logs/physx_exception.txt'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(traceback.format_exc(), encoding='utf-8')
        raise
