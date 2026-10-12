#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import importlib.util
from PIL import Image, ImageDraw

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
FRESH = ROOT / 'case09_full_pipeline_fresh_e2e_v1'
OUT = ROOT / 'case09_brep_edge_provenance_fix_and_mac_incremental_ablation'
ART = OUT / 'artifacts'
sys.path.insert(0, str(ROOT))
from case09_edge_audit import mesh_from_shape, read_step

render_spec = importlib.util.spec_from_file_location('render_3d', ROOT / 'case09_render_3d_png.py')
render_mod = importlib.util.module_from_spec(render_spec)
assert render_spec and render_spec.loader
render_spec.loader.exec_module(render_mod)

sys.path.insert(0, str(ROOT / 'v13_transform_restore_and_xcaf_assembly'))
from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step

roles = {
    'CADPART_000': 'FUSELAGE', 'CADPART_001': 'MAIN_WING_LEFT',
    'CADPART_002': 'MAIN_WING_RIGHT', 'CADPART_003': 'TAILPLANE_LEFT',
    'CADPART_004': 'TAILPLANE_RIGHT', 'CADPART_005': 'VERTICAL_TAIL',
    'CADPART_006': 'PROPELLER_PATTERN', 'CADPART_007': 'DORSAL_FEATURES',
}

manifest = json.loads((FRESH / 'final/CASE09_full_e2e_assembly_manifest.json').read_text())
entries = []
part_images = []
for item in manifest['components']:
    part_id = item['part_id']
    mac_step = OUT / 'mac_candidates' / part_id / 'candidate.step'
    use_mac = mac_step.is_file()
    selected_step = mac_step if use_mac else Path(item['fresh_step_path'])
    shape, _ = read_step(selected_step)
    entries.append({**item, 'fresh_step_path': str(selected_step), 'candidate_source': 'MAC_PLAN_PREVIEW' if use_mac else 'BASELINE_FALLBACK', 'builder': 'MAC_V11_PREVIEW' if use_mac else item.get('builder')})
    part_path = ART / 'mac_candidate_preview_parts' / f'{part_id}.png'
    part_path.parent.mkdir(parents=True, exist_ok=True)
    render_mod.render(mesh_from_shape(shape), part_path, size=(480, 340), supersample=1)
    part_images.append((part_id, roles[part_id], part_path, use_mac))

preview_step = OUT / 'mac_candidate_preview_assembly.step'
built = build_xcaf_assembly('CASE09_MAC_CANDIDATE_PREVIEW_NOT_SELECTED', entries)
export_xcaf_step(built.doc, preview_step, 'CASE09_MAC_CANDIDATE_PREVIEW_NOT_SELECTED')
preview_shape, _ = read_step(preview_step)
render_mod.render(mesh_from_shape(preview_shape), ART / 'case09_mac_candidate_preview_3d.png', size=(1400, 1000), supersample=2)

cell_w, cell_h = 490, 380
sheet = Image.new('RGB', (cell_w * 4, cell_h * 2), (242, 245, 248))
draw = ImageDraw.Draw(sheet)
for i, (part_id, role, path, use_mac) in enumerate(part_images):
    x, y = (i % 4) * cell_w, (i // 4) * cell_h
    sheet.paste(Image.open(path).convert('RGB').resize((cell_w, cell_h - 36)), (x, y + 30))
    label = f'{part_id} {role} | ' + ('MAC CANDIDATE' if use_mac else 'BASELINE FALLBACK')
    draw.text((x + 8, y + 8), label, fill=(20, 30, 45))
sheet.save(ART / 'case09_mac_candidate_preview_parts.png')
print(preview_step)
print(ART / 'case09_mac_candidate_preview_3d.png')
print(ART / 'case09_mac_candidate_preview_parts.png')
