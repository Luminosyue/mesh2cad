# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asus_sabertooth_990fx_20_motherboard_atx_socket_am3_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001, PART_002, PART_003, PART_004
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 1169 | 21.265804290771484 | 0.004941909631110211 |
| PART_001 | 15 | 3987 | 41.29867935180664 | 0.004946712342475225 |
| PART_002 | 15 | 1250 | 20.82732391357422 | 0.0049414053033107665 |
| PART_003 | 15 | 10414 | 42.97349166870117 | 0.0049454135743541815 |
| PART_004 | 15 | 4227 | 26.24886131286621 | 0.0049377358165844515 |
| PART_000 | 25 | 20 | 29.56282615661621 | 0.00494421809478901 |
| PART_001 | 25 | 1823 | 43.617576599121094 | 0.004941181521174725 |
| PART_002 | 25 | 2 | 29.30118751525879 | 0.004935915572831369 |
| PART_003 | 25 | 4190 | 48.83778762817383 | 0.004944879135223822 |
| PART_004 | 25 | 311 | 32.195716857910156 | 0.004938076417265538 |
| PART_000 | 35 | 0 | n/a | n/a |
| PART_001 | 35 | 714 | 45.305694580078125 | 0.004940021381491096 |
| PART_002 | 35 | 0 | n/a | n/a |
| PART_003 | 35 | 1421 | 53.17107391357422 | 0.0049441513528005925 |
| PART_004 | 35 | 0 | n/a | n/a |
| PART_000 | 45 | 0 | n/a | n/a |
| PART_001 | 45 | 42 | 52.27312088012695 | 0.0049410341789925824 |
| PART_002 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 405 | 57.186614990234375 | 0.004949208692318071 |
| PART_004 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
