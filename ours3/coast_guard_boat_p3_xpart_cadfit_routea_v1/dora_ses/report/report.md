# Dora SES on X-Part watertight meshes

## Pipeline Flags
- P3_REEXECUTED: `False`
- XPART_REEXECUTED: `False`
- DORA_VAE_USED: `False`
- DORA_SES_USED: `True`

## Input
- X-Part root: `/data/home/cuiyuehan/project/mesh2cad/ours3/coast_guard_boat_p3_xpart_cadfit_routea_v1/xpart`
- Parts: PART_000, PART_003
- Thresholds: [15, 25, 35, 45]

| part | threshold | salient_edges | dihedral_p95 | edge_len_p95 |
|---|---:|---:|---:|---:|
| PART_000 | 15 | 13 | 17.028221130371094 | 0.007533500003184992 |
| PART_003 | 15 | 821 | 24.75043296813965 | 0.005499876580906159 |
| PART_000 | 25 | 0 | n/a | n/a |
| PART_003 | 25 | 39 | 34.45838165283203 | 0.006254736798342834 |
| PART_000 | 35 | 0 | n/a | n/a |
| PART_003 | 35 | 1 | 35.46002197265625 | 0.001743495976307374 |
| PART_000 | 45 | 0 | n/a | n/a |
| PART_003 | 45 | 0 | n/a | n/a |

Salient edges are `DORA_SALIENT_EDGE` priors, not final CAD edges.
Route A CADFit does not read these files.
