# CAD_STYLE_RENDER_UPGRADE_V1 Report

## Backend

- Rendering backend: **matplotlib** (Agg) + **OCP/OpenCascade** + **trimesh** + **numpy**
- Open3D OffscreenRenderer unavailable in this environment (EGL segfault), so headless matplotlib painter was used.

## STEP → BRep → tessellation

1. `STEPControl_Reader` fresh reload of assembly STEP
2. `BRepMesh_IncrementalMesh` with linear + angular deflection
3. Face triangulation extracted to triangle mesh
4. CAD panel never loads source OBJ geometry

## Source vs CAD rendering differences

- Source: light-gray triangle shaded mesh, optional weak wire hints
- CAD: industrial light blue-gray shaded STEP tessellation + sharp/silhouette edge overlay
- Same camera / same world bbox for side-by-side and four-view sheets

## Edge overlay

- Mode: `SHARP_EDGE+SILHOUETTE` from tessellated mesh adjacency
- Reason: dense loft BReps contain tens of thousands of raw BRep edges; drawing all of them looks like a mesh cage
- Sharp dihedral edges + view-dependent silhouette approximate FreeCAD/SolidWorks shaded-with-edges look

## Exploded / section / provenance

- Exploded: each SOLID/SHELL component translated outward from assembly centroid
- Section: plane cut through bbox center; source vs CAD half-models + cut outline
- Provenance panel: explicit STEP→BRep→tessellation caption and `RIGHT_RENDER_USES_SOURCE_MESH=false`

## Per-case outputs

### CASE05

- source_shaded: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/source_shaded.png`
- cad_shaded_edges: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/cad_shaded_edges.png`
- main: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_source_vs_cad_shaded_edges.png`
- overlay: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_overlay_transparent.png`
- exploded: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_exploded_assembly.png`
- part_colored: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_part_colored_assembly.png`
- section: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_section_view.png`
- feature_closeups: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_feature_closeups.png`
- four_view: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_four_view_render_sheet.png`
- provenance: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/case05/artifacts/CASE05_provenance_panel.png`
- CAD triangles: `169164`
- Components: `10`

### REAL03

- source_shaded: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/source_shaded.png`
- cad_shaded_edges: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/cad_shaded_edges.png`
- main: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_source_vs_cad_shaded_edges.png`
- overlay: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_overlay_transparent.png`
- exploded: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_exploded_assembly.png`
- part_colored: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_part_colored_assembly.png`
- section: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_section_view.png`
- feature_closeups: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_feature_closeups.png`
- four_view: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_four_view_render_sheet.png`
- provenance: `/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1/real03/artifacts/REAL03_provenance_panel.png`
- CAD triangles: `667155`
- Components: `27`

## Known limitations

- REAL03 hole close-ups use per-part STEP meshes from assembly manifest + measured hole rings (red) for feature clarity.

- CASE_05 geometry is largely multi-section loft BRep; shaded+edges helps, but it is not sparse parametric feature CAD.
- REAL_03 STEP is large; first run caches tessellation under `real03/cache/`.
- Edge overlay is sharp/silhouette approximation (not every raw BRep edge).

