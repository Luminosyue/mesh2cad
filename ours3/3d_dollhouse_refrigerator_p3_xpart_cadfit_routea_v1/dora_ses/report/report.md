# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/3d_dollhouse_refrigerator_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 1224 | 38.01077651977539 | 0.010303262655079705 |
| PART_000 | 25 | 314 | 44.189815521240234 | 0.010499088012936121 |
| PART_000 | 35 | 83 | 59.37074279785156 | 0.010521661896642288 |
| PART_000 | 45 | 14 | 73.28075408935547 | 0.010543001150049185 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
