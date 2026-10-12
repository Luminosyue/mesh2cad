# PAPER_STYLE_BREP_RENDERER_V1

## Outcome

- Gate: `PAPER_STYLE_BREP_RENDERER_V1_PASS`
- Backend: `OCP_7_8_PLUS_PYVISTA_0_48_XVFB_OFFSCREEN`

## Provenance

- Mesh panels use source OBJ triangle faces and edges.
- Split panels use frozen P3 triangle labels with a 0.04 bbox-diagonal explosion.
- BRep panels use only freshly reloaded STEP topology: independently tessellated faces, unique TopoDS edges, and TopoDS vertices.
- No CAD recovery, P3, PhysX, MAC, or LLM was rerun; STEP geometry was not modified.

## CASE_05

- Faces / edges / vertices: `34196 / 68992 / 34816`
- Faceted wrapped audit: `False`
- Comparison: `/data/home/cuiyuehan/project/mesh2cad/ours3/paper_style_brep_render_v1/case05/comparison_figure.png`

## REAL_03

- Faces / edges / vertices: `83495 / 187226 / 111663`
- Faceted wrapped audit: `False`
- Comparison: `/data/home/cuiyuehan/project/mesh2cad/ours3/paper_style_brep_render_v1/real03/comparison_figure.png`
