# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asics_hyperrocketgirl_sp_5_whitemalibu_blueblack_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 6918 | 41.635223388671875 | 0.014286609897562917 |
| PART_001 | 15 | 1336 | 52.41343307495117 | 0.014106179701960006 |
| PART_002 | 15 | 149 | 26.771915435791016 | 0.01395033942867867 |
| PART_000 | 25 | 1971 | 54.870361328125 | 0.014470361405195295 |
| PART_001 | 25 | 960 | 53.8897705078125 | 0.01400262394744956 |
| PART_002 | 25 | 13 | 28.595306396484375 | 0.009904235485973254 |
| PART_000 | 35 | 641 | 63.15384292602539 | 0.014787378871936655 |
| PART_001 | 35 | 624 | 55.246280670166016 | 0.013949554255859746 |
| PART_002 | 35 | 0 | n/a | n/a |
| PART_000 | 45 | 253 | 72.9230728149414 | 0.014931019773341749 |
| PART_001 | 45 | 245 | 61.0281982421875 | 0.013824794639518736 |
| PART_002 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
