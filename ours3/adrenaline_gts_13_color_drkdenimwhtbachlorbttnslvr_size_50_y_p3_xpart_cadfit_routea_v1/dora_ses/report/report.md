# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/adrenaline_gts_13_color_drkdenimwhtbachlorbttnslvr_size_50_y_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 844 | 32.186073303222656 | 0.007006566274758955 |
| PART_000 | 25 | 158 | 40.87531280517578 | 0.006987951694114968 |
| PART_000 | 35 | 28 | 45.454010009765625 | 0.005705150379969487 |
| PART_000 | 45 | 2 | 47.620426177978516 | 0.003969870034714667 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
