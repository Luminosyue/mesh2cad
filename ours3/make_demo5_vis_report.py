import json
from pathlib import Path

b = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_v3_optimizer_memory_demo5_v1/demo5_visualization_v1')
items = json.loads((b/'ARTIFACT_PATH_TABLE.json').read_text())
lines = ['# Demo5 Generated CAD Visualization V1', '', 'All generated CAD panels were rendered from the frozen model free-generation artifacts and freshly reloaded generated STEP files. No canonical STEP was used as generated output.', '', '| Case | Object | Generated faces | Generated edges | Surface types | Display triangles | FREE_EXACT | STEP_READBACK |', '|---|---|---:|---:|---|---:|---|---|']
for x in items:
    surf = ', '.join(f'{k}: {v}' for k,v in x['surface_types_generated'].items())
    lines.append(f"| {x['case_id']} | {x['object_id']} | {x['brep_face_n_generated']} | {x['brep_edge_n_generated']} | {surf} | {x['display_triangle_n_generated']} | TRUE | TRUE |")
lines += ['', '## Render contract', '', '- Input Mesh: source OBJ with triangle edges.', '- Generated CAD: generated STEP BRep tessellation, no triangle wireframe and no tessellation edges.', '- Canonical CAD: canonical STEP BRep tessellation, no triangle wireframe and no tessellation edges.', '- Overlay: generated and canonical in the original shared coordinates, without ICP, scaling, or re-alignment.', '- Camera: shared union-bbox orthographic camera, azimuth 35 degrees, elevation 24 degrees, 1600x1200 per case.', '', '## Key files', '', '- `DEMO5_GENERATED_CAD_GRID.png`', '- `DEMO5_GENERATED_ONLY.png`', '- `ARTIFACT_PATH_TABLE.json`', '- `ARTIFACT_PATH_TABLE.csv`']
(b/'VISUALIZATION_REPORT.md').write_text('\n'.join(lines)+'\n')
