# Demo5 Generated CAD Visualization V1

All generated CAD panels were rendered from the frozen model free-generation artifacts and freshly reloaded generated STEP files. No canonical STEP was used as generated output.

| Case | Object | Generated faces | Generated edges | Surface types | Display triangles | FREE_EXACT | STEP_READBACK |
|---|---|---:|---:|---|---:|---|---|
| case_018 | b015ipnvfw | 14 | 36 | GeomAbs_SurfaceType.GeomAbs_Plane: 14 | 44 | TRUE | TRUE |
| case_009 | construction_60 | 56 | 162 | GeomAbs_SurfaceType.GeomAbs_Plane: 54, GeomAbs_SurfaceType.GeomAbs_Cylinder: 2 | 388 | TRUE | TRUE |
| case_014 | tank | 778 | 2256 | GeomAbs_SurfaceType.GeomAbs_Plane: 778 | 3004 | TRUE | TRUE |
| case_010 | vase | 648 | 1986 | GeomAbs_SurfaceType.GeomAbs_Plane: 648 | 2696 | TRUE | TRUE |
| case_005 | azure_snake_tieks_leather_snake_print_ballet_flats | 22 | 41 | GeomAbs_SurfaceType.GeomAbs_BSplineSurface: 20, GeomAbs_SurfaceType.GeomAbs_Plane: 2 | 1224 | TRUE | TRUE |

## Render contract

- Input Mesh: source OBJ with triangle edges.
- Generated CAD: generated STEP BRep tessellation, no triangle wireframe and no tessellation edges.
- Canonical CAD: canonical STEP BRep tessellation, no triangle wireframe and no tessellation edges.
- Overlay: generated and canonical in the original shared coordinates, without ICP, scaling, or re-alignment.
- Camera: shared union-bbox orthographic camera, azimuth 35 degrees, elevation 24 degrees, 1600x1200 per case.

## Key files

- `DEMO5_GENERATED_CAD_GRID.png`
- `DEMO5_GENERATED_ONLY.png`
- `ARTIFACT_PATH_TABLE.json`
- `ARTIFACT_PATH_TABLE.csv`
