# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/b00d448iik_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 4099 | 58.071990966796875 | 0.004932986314317096 |
| PART_001 | 15 | 2587 | 31.967262268066406 | 0.004937464535201983 |
| PART_000 | 25 | 1680 | 59.43737030029297 | 0.004932344827130858 |
| PART_001 | 25 | 273 | 40.38399124145508 | 0.005113229282527656 |
| PART_000 | 35 | 833 | 59.962398529052734 | 0.004932302126684679 |
| PART_001 | 35 | 91 | 41.48777389526367 | 0.004939757010720223 |
| PART_000 | 45 | 780 | 59.99003219604492 | 0.004932295654149798 |
| PART_001 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
