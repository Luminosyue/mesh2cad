#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
sys.path.insert(0, str(ROOT))
from case09_edge_audit import FRESH, OUT, mesh_from_shape, read_step

step = FRESH / 'final/CASE09_full_e2e_assembly.step'
output = OUT / 'artifacts/case09_fresh_e2e_3d_view.glb'
shape, _ = read_step(step)
mesh = mesh_from_shape(shape)
output.parent.mkdir(parents=True, exist_ok=True)
mesh.export(output)

html = output.with_suffix('.html')
html.write_text(f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>CASE09 3D View</title>
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"></script>
<style>html,body{{margin:0;height:100%;background:#eef2f6}} model-viewer{{width:100%;height:100%}}</style>
</head><body><model-viewer src="{output.name}" camera-controls auto-rotate shadow-intensity="0.35" exposure="1.1" interaction-prompt="none" alt="CASE09 fresh E2E CAD assembly"></model-viewer></body></html>
''', encoding='utf-8')
print(output)
print(html)
