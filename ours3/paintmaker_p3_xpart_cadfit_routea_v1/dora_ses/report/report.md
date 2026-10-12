# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/paintmaker_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_001
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 4441 | 24.839262008666992 | 0.004940927923477484 |
| PART_001 | 15 | 6470 | 26.067293167114258 | 0.004938960461065322 |
| PART_000 | 25 | 214 | 29.980899810791016 | 0.004937744906603271 |
| PART_001 | 25 | 446 | 31.71776580810547 | 0.004938355584467931 |
| PART_000 | 35 | 0 | n/a | n/a |
| PART_001 | 35 | 1 | 35.090476989746094 | 0.00493318188468655 |
| PART_000 | 45 | 0 | n/a | n/a |
| PART_001 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit does not read these files.
