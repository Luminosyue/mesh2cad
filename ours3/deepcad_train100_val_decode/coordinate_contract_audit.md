# Coordinate contract audit

**Verdict:** `FAIL: point input scaled+shifted; DSL label NOT synced`

- n=20, desync=20/20
- features↔mesh match: 20/20
- features↔DSL-exec match: 20/20
- scale_factor range: [2.433, 21.542] (mean 6.008)
- features diagonal range: [0.279, 2.466]
- preprocess diagonal mean: 6.000 (target=6.0)

## Per-sample

| sample_id | feat_diag | dsl_diag | scale | shift | preprocess_diag | desync | feat≈mesh | feat≈dsl |
|---|---:|---:|---:|---|---:|:---:|:---:|:---:|
| 0049_00493110 | 0.7502 | 0.7502 | 7.998 | `(-0.094,-0.047,0.000)` | 6.000 | Y | Y | Y |
| 0079_00793608 | 0.7575 | 0.7575 | 7.921 | `(-0.297,-0.594,-2.970)` | 6.000 | Y | Y | Y |
| 0024_00240625 | 1.0054 | 1.0054 | 5.968 | `(-6.808,-1.333,-1.999)` | 6.000 | Y | Y | Y |
| 0005_00058615 | 0.7504 | 0.7504 | 7.995 | `(-0.073,-5.996,-0.073)` | 6.000 | Y | Y | Y |
| 0006_00062190 | 1.2179 | 1.2182 | 4.927 | `(-1.671,-3.695,-1.672)` | 6.000 | Y | Y | Y |
| 0027_00271614 | 1.1562 | 1.1562 | 5.190 | `(-1.058,-3.892,-0.981)` | 6.000 | Y | Y | Y |
| 0098_00981499 | 0.8706 | 0.8712 | 6.892 | `(-1.075,-1.074,0.000)` | 6.000 | Y | Y | Y |
| 0014_00143027 | 2.1428 | 2.1430 | 2.800 | `(-4.200,-2.100,0.000)` | 6.000 | Y | Y | Y |
| 0016_00161900 | 1.1816 | 1.1816 | 5.078 | `(-1.949,-1.994,-3.808)` | 6.000 | Y | Y | Y |
| 0051_00519077 | 0.7014 | 0.7014 | 8.555 | `(-1.530,-4.168,2.510)` | 6.000 | Y | Y | Y |
| 0026_00266321 | 1.6951 | 1.6951 | 3.540 | `(-2.794,-5.309,0.000)` | 6.000 | Y | Y | Y |
| 0039_00396640 | 2.4662 | 2.4662 | 2.433 | `(-2.737,-1.369,-2.281)` | 6.000 | Y | Y | Y |
| 0039_00394584 | 1.8306 | 1.8306 | 3.278 | `(-3.409,-4.916,0.000)` | 6.000 | Y | Y | Y |
| 0065_00655843 | 1.9272 | 1.9272 | 3.113 | `(0.000,-4.670,-3.726)` | 6.000 | Y | Y | Y |
| 0008_00087197 | 0.2785 | 0.2785 | 21.542 | `(-16.157,-0.269,2.273)` | 6.000 | Y | Y | Y |
| 0043_00435622 | 0.7870 | 0.7870 | 7.624 | `(-0.860,-0.594,-2.859)` | 6.000 | Y | Y | Y |
| 0032_00321447 | 1.7309 | 1.7309 | 3.466 | `(-5.199,-0.371,-2.971)` | 6.000 | Y | Y | Y |
| 0086_00868338 | 1.5937 | 1.5937 | 3.765 | `(-0.941,-2.824,0.000)` | 6.000 | Y | Y | Y |
| 0083_00838161 | 1.5349 | 1.5349 | 3.909 | `(-2.928,-0.652,0.000)` | 6.000 | Y | Y | Y |
| 0047_00478049 | 1.4386 | 1.4386 | 4.171 | `(-0.536,-0.123,-6.127)` | 6.000 | Y | Y | Y |

## Explanation

DeepCAD cad.normalize() → DSL/STEP/mesh/features share DeepCAD unit-cube space (features ≈ mesh ≈ DSL-exec). This layer is OK.

SpatialLMPlugin._load_cad_npy scales xyz by (cad_target_diagonal / bbox_diagonal) then PositiveShift (coord -= min). Labels from create_spatiallm_cad_dataset are raw program.dsl with NO inverse transform. cad_mode transformations dict hardcodes scaling=1.0 and never rewrites DSL. Absolute scale of features is erased to ~constant diagonal; model must emit original DeepCAD numbers.

Code:

- `SpatialLM/spatiallm/tuner/data/mm_plugin.py::_load_cad_npy`
- `scripts/spatiallm_cad_frontend.py::preprocess_cad_point_cloud`
- `scripts/deepcad/create_spatiallm_cad_dataset.py::_load_dsl_label`
