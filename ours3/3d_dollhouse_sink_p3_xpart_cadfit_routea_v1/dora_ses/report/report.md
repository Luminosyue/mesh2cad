# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/3d_dollhouse_sink_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_002, PART_003
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_002 | 15 | 1294 | 26.6643009185791 | 0.005061822354193179 |
| PART_003 | 15 | 4694 | 32.22609329223633 | 0.004958512226703885 |
| PART_002 | 25 | 110 | 36.51154708862305 | 0.005005410486068688 |
| PART_003 | 25 | 944 | 39.49998474121094 | 0.0049573541561799515 |
| PART_002 | 35 | 15 | 38.07173156738281 | 0.004933387655211891 |
| PART_003 | 35 | 131 | 41.84648132324219 | 0.004951039693152699 |
| PART_002 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
