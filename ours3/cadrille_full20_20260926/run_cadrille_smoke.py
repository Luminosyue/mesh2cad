import json
import os
import sys
from functools import partial
from pathlib import Path

import numpy as np
import torch
import trimesh
from torch.utils.data import DataLoader
from transformers import AutoProcessor


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_full20_20260926')
REPO = ROOT / 'repo'
MODEL = ROOT / 'model'
sys.path.insert(0, str(REPO))
from cadrille import Cadrille, collate  # noqa: E402
from dataset import CadRecodeDataset  # noqa: E402


def normalize_mesh(source: Path, target: Path):
    loaded = trimesh.load(source, force='scene')
    mesh = trimesh.util.concatenate(tuple(g for g in loaded.geometry.values())) if isinstance(loaded, trimesh.Scene) else loaded
    mesh = mesh.copy()
    low = mesh.vertices.min(axis=0)
    high = mesh.vertices.max(axis=0)
    scale = float(np.max(high - low))
    if scale <= 0:
        raise ValueError(f'empty or degenerate mesh: {source}')
    mesh.vertices = (mesh.vertices - low) / scale
    mesh.export(target)
    return low.tolist(), scale


def main():
    source = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    data_root = out_dir / 'dataset'
    custom = data_root / 'custom'
    custom.mkdir(parents=True, exist_ok=True)
    normalized = custom / 'part_000.stl'
    low, scale = normalize_mesh(source, normalized)

    model = Cadrille.from_pretrained(
        str(MODEL), torch_dtype=torch.bfloat16,
        attn_implementation='eager', device_map={'': 'cuda:0'})
    processor = AutoProcessor.from_pretrained(
        str(MODEL), min_pixels=256 * 28 * 28,
        max_pixels=1280 * 28 * 28, padding_side='left')
    dataset = CadRecodeDataset(
        root_dir=str(data_root), split='custom', n_points=256,
        normalize_std_pc=100, noise_scale_pc=None, img_size=128,
        normalize_std_img=200, noise_scale_img=-1, num_imgs=4, mode='pc')
    loader = DataLoader(
        dataset, batch_size=1, num_workers=0,
        collate_fn=partial(collate, processor=processor, n_points=256, eval=True))
    batch = next(iter(loader))
    device = model.device
    generated = model.generate(
        input_ids=batch['input_ids'].to(device),
        attention_mask=batch['attention_mask'].to(device),
        point_clouds=batch['point_clouds'].to(device),
        is_pc=batch['is_pc'].to(device),
        is_img=batch['is_img'].to(device),
        max_new_tokens=768)
    trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(batch.input_ids, generated)]
    text = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    (out_dir / 'part_000.py').write_text(text, encoding='utf-8')
    (out_dir / 'TRANSFORM.json').write_text(json.dumps({
        'source': str(source), 'normalized_mesh': str(normalized),
        'bbox_min': low, 'uniform_scale': scale,
        'normalization': 'p_normalized=(p-bbox_min)/uniform_scale',
        'reassembly': 'p_world=uniform_scale*p_normalized+bbox_min'
    }, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'source': str(source), 'output': str(out_dir / 'part_000.py')}))


if __name__ == '__main__':
    main()
