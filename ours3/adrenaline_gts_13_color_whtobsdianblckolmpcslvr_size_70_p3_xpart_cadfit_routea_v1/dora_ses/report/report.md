# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/adrenaline_gts_13_color_whtobsdianblckolmpcslvr_size_70_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_002
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_002 | 15 | 17696 | 46.65462875366211 | 0.014356255553505556 |
| PART_002 | 25 | 5501 | 64.57786560058594 | 0.014333867979809204 |
| PART_002 | 35 | 2250 | 80.82626342773438 | 0.014388883351661446 |
| PART_002 | 45 | 1004 | 91.9417724609375 | 0.014426123786924995 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
