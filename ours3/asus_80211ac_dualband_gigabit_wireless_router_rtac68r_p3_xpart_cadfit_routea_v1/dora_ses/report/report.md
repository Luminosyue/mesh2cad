# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/asus_80211ac_dualband_gigabit_wireless_router_rtac68r_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_005
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_005 | 15 | 7277 | 69.04362487792969 | 0.006773448968890788 |
| PART_005 | 25 | 3680 | 111.41913604736328 | 0.005850946302635711 |
| PART_005 | 35 | 1695 | 136.1932373046875 | 0.005712387537698837 |
| PART_005 | 45 | 985 | 145.15020751953125 | 0.005632348958309224 |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit consumes `salient_edges_source_space.npz` as planar-contour seeds.
