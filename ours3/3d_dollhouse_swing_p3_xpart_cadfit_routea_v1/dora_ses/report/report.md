# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/3d_dollhouse_swing_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 3581 | 39.98124694824219 | 0.01176416288536078 |
| PART_000 | 25 | 931 | 44.646629333496094 | 0.011079204584533046 |
| PART_000 | 35 | 332 | 45.20714569091797 | 0.009879478036667397 |
| PART_000 | 45 | 28 | 46.16531753540039 | 0.009864139922690484 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
