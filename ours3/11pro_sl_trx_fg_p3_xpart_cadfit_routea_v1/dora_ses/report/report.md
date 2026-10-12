# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/11pro_sl_trx_fg_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 1514 | 29.904537200927734 | 0.006700799566880663 |
| PART_001 | 15 | 9564 | 39.15989685058594 | 0.006997004633899385 |
| PART_000 | 25 | 214 | 41.19660186767578 | 0.005992772433804641 |
| PART_001 | 25 | 1920 | 62.66953659057617 | 0.006989372394460305 |
| PART_000 | 35 | 23 | 58.57380676269531 | 0.0056552740534603725 |
| PART_001 | 35 | 699 | 79.40542602539062 | 0.006974760527548151 |
| PART_000 | 45 | 6 | 65.80152130126953 | 0.005154894640275154 |
| PART_001 | 45 | 300 | 97.96238708496094 | 0.006862513481640256 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
