import json
import os
import runpy
import sys
import traceback
from functools import partial
from pathlib import Path

import numpy as np
import torch
import trimesh
import cadquery as cq
from torch.utils.data import DataLoader
from transformers import AutoProcessor

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_full20_20260926')
REPO = ROOT / 'repo'
MODEL = ROOT / 'model'
SOURCE_ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
sys.path.insert(0, str(REPO))
from cadrille import Cadrille, collate  # noqa: E402

CASES = [
    '2_of_jenga_classic_game', '3d_dollhouse_sofa', 'android_figure_orange',
    'aroma_stainless_steel_milk_frother_2_cup', 'assorted_vegetable_set',
    'baby_car', 'birdhouse', 'cube', 'dvd_player', 'fire_truck',
    'mini_excavator', 'mini_fire_engine', 'paintmaker', 'pottery_large',
    'pressure_cooker', 'robot', 'speaker_big', 'tank', 'toaster', 'winerack',
    'airplane',
]


def input_dir(case):
    if case == 'tank':
        return SOURCE_ROOT / 'cadfit_xpart45_routea_v1' / 'input_stl'
    return SOURCE_ROOT / f'{case}_p3_xpart_cadfit_routea_v1' / 'cadfit_routea' / 'input_stl'


def load_mesh(path):
    loaded = trimesh.load(path, force='scene')
    if isinstance(loaded, trimesh.Scene):
        loaded = trimesh.util.concatenate(tuple(g for g in loaded.geometry.values()))
    return loaded.copy()


def farthest(points, k):
    if len(points) <= k:
        idx = np.arange(len(points))
        return points[idx]
    chosen = np.zeros(k, dtype=np.int64)
    dist = np.full(len(points), np.inf, dtype=np.float64)
    for i in range(k):
        if i:
            delta = points - points[chosen[i - 1]]
            dist = np.minimum(dist, np.einsum('ij,ij->i', delta, delta))
        chosen[i] = int(np.argmax(dist))
    return points[chosen]


def normalize_part(source, normalized):
    mesh = load_mesh(source)
    low = mesh.vertices.min(axis=0).astype(float)
    high = mesh.vertices.max(axis=0).astype(float)
    extent = high - low
    unit = float(np.max(extent))
    if unit <= 0:
        raise ValueError('degenerate input mesh')
    mesh.vertices = (mesh.vertices - low) / unit
    mesh.export(normalized)
    return low, high, unit


def point_cloud(normalized):
    mesh = load_mesh(normalized)
    points, _ = trimesh.sample.sample_surface(mesh, 4096)
    points = farthest(np.asarray(points), 256)
    return (points - 0.5) * 2.0


def execute_and_place(py_path, source, world_step):
    ns = runpy.run_path(str(py_path))
    obj = ns.get('r') or ns.get('result') or ns.get('shape')
    if obj is None:
        raise RuntimeError('generated code has no r/result/shape')
    shape = obj.val() if hasattr(obj, 'val') else obj
    if not hasattr(shape, 'BoundingBox'):
        raise RuntimeError(f'generated object is not a CAD shape: {type(shape)}')
    src = load_mesh(source)
    src_low = src.vertices.min(axis=0).astype(float)
    src_high = src.vertices.max(axis=0).astype(float)
    src_extent = src_high - src_low
    box = shape.BoundingBox()
    out_low = np.array([box.xmin, box.ymin, box.zmin], dtype=float)
    out_high = np.array([box.xmax, box.ymax, box.zmax], dtype=float)
    out_extent = out_high - out_low
    out_unit = float(np.max(out_extent))
    if out_unit <= 1e-12:
        raise RuntimeError('generated shape is degenerate')
    scale = float(np.max(src_extent)) / out_unit
    shift = src_low - scale * out_low
    placed = shape.scale(scale).moved(cq.Location(cq.Vector(*shift)))
    cq.exporters.export(placed, str(world_step))
    return placed


def run_case(case, model, processor, out_root):
    sources = sorted(input_dir(case).glob('PART_*.stl'))
    case_out = out_root / case
    case_out.mkdir(parents=True, exist_ok=True)
    if not sources:
        (case_out / 'STATUS.json').write_text(json.dumps({'case': case, 'status': 'MISSING_INPUT', 'input_dir': str(input_dir(case))}, indent=2))
        return
    records = []
    world_shapes = []
    for source in sources:
        part = source.stem
        part_out = case_out / part
        part_out.mkdir(parents=True, exist_ok=True)
        status_path = part_out / 'STATUS.json'
        if status_path.exists():
            try:
                old = json.loads(status_path.read_text())
                if old.get('status') == 'PASS' and (part_out / 'world.step').exists():
                    world_shapes.append(cq.importers.importStep(str(part_out / 'world.step')).val())
                    records.append(old)
                    continue
            except Exception:
                pass
        rec = {'case': case, 'part': part, 'source': str(source), 'status': 'FAIL'}
        try:
            normalized = part_out / 'normalized.stl'
            low, high, unit = normalize_part(source, normalized)
            pc = point_cloud(normalized)
            item = {'point_cloud': pc, 'description': 'Generate cadquery code', 'file_name': part}
            batch = collate([item], processor=processor, n_points=256, eval=True)
            device = model.device
            with torch.inference_mode():
                generated = model.generate(
                    input_ids=batch['input_ids'].to(device),
                    attention_mask=batch['attention_mask'].to(device),
                    point_clouds=batch['point_clouds'].to(device),
                    is_pc=batch['is_pc'].to(device),
                    is_img=batch['is_img'].to(device),
                    max_new_tokens=768)
            trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(batch.input_ids, generated)]
            text = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
            if '```' in text:
                text = text.replace('```python', '').replace('```', '').strip()
            py_path = part_out / 'cadquery.py'
            py_path.write_text(text, encoding='utf-8')
            world_step = part_out / 'world.step'
            placed = execute_and_place(py_path, source, world_step)
            b = placed.BoundingBox()
            rec.update({'status': 'PASS', 'normalized': str(normalized), 'cadquery': str(py_path), 'world_step': str(world_step), 'bbox_min': low.tolist(), 'bbox_max': high.tolist(), 'uniform_scale': unit, 'output_bbox': [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]})
            world_shapes.append(placed)
        except Exception:
            rec['error'] = traceback.format_exc()
        status_path.write_text(json.dumps(rec, indent=2), encoding='utf-8')
        records.append(rec)
        torch.cuda.empty_cache()
    assembly = case_out / 'assembled.step'
    if world_shapes:
        cq.exporters.export(cq.Compound.makeCompound(world_shapes), str(assembly))
    summary = {'case': case, 'status': 'PASS' if world_shapes and len(world_shapes) == len(sources) else 'PARTIAL', 'required_parts': len(sources), 'pass_parts': len(world_shapes), 'assembled_step': str(assembly) if assembly.exists() else None, 'parts': records}
    (case_out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')


def main():
    shard = int(sys.argv[1])
    shard_count = int(sys.argv[2])
    out_root = ROOT / 'results'
    out_root.mkdir(parents=True, exist_ok=True)
    selected = [case for i, case in enumerate(CASES) if i % shard_count == shard]
    model = Cadrille.from_pretrained(str(MODEL), torch_dtype=torch.bfloat16, attn_implementation='eager', device_map={'': 'cuda:0'})
    processor = AutoProcessor.from_pretrained(str(MODEL), min_pixels=256 * 28 * 28, max_pixels=1280 * 28 * 28, padding_side='left')
    for case in selected:
        run_case(case, model, processor, out_root)
    (out_root / f'SHARD_{shard}.DONE').write_text(json.dumps({'shard': shard, 'cases': selected}, indent=2))


if __name__ == '__main__':
    main()
