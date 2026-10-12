# V7B Face Topology Audit

This is a pre-sewing audit. No V7B file was modified.

## FUSELAGE (CADPART_000)

- STEP: `/data/home/cuiyuehan/project/mesh2cad/ours3/v7b_profile_type_aware_open_shell_reconstruction/06_candidates/CADPART_000/PRIMARY/candidate.step`
- OCC valid: `True`
- Face count: `2`
- Free edges: `8`

### CADPART_000_FACE_00

Surface=BSPLINE; orientation=0; wires=1; edges=4; valid=True

| Boundary | Semantic | Curve | Length | Pcurve |
|---|---|---:|---:|---:|
| CADPART_000_FACE_00_BND_00 | ROOT_BOUNDARY | BSPLINE | 0.631174547 | True |
| CADPART_000_FACE_00_BND_01 | SIDE_BOUNDARY | BSPLINE | 1.59212599 | True |
| CADPART_000_FACE_00_BND_02 | TIP_BOUNDARY | BSPLINE | 0.106659266 | True |
| CADPART_000_FACE_00_BND_03 | SIDE_BOUNDARY | BSPLINE | 1.58386377 | True |

### CADPART_000_FACE_01

Surface=BSPLINE; orientation=0; wires=1; edges=4; valid=True

| Boundary | Semantic | Curve | Length | Pcurve |
|---|---|---:|---:|---:|
| CADPART_000_FACE_01_BND_00 | ROOT_BOUNDARY | BSPLINE | 0.0328192782 | True |
| CADPART_000_FACE_01_BND_01 | SIDE_BOUNDARY | BSPLINE | 0.623464216 | True |
| CADPART_000_FACE_01_BND_02 | TIP_BOUNDARY | BSPLINE | 0.106359081 | True |
| CADPART_000_FACE_01_BND_03 | SIDE_BOUNDARY | BSPLINE | 0.65867269 | True |

### Shared-boundary decision

Expected shared design boundaries: `2`
Accepted matches: `0`
Status: `UNRESOLVED`

- CADPART_000_FACE_00_BND_02 ↔ CADPART_000_FACE_01_BND_02: mean=0.776619297, p95=0.788614549, length_ratio=0.997186, score=0.438262, status=UNRESOLVED
- CADPART_000_FACE_00_BND_00 ↔ CADPART_000_FACE_01_BND_01: mean=0.302181286, p95=0.54476699, length_ratio=0.987784, score=0.426885, status=UNRESOLVED
- CADPART_000_FACE_00_BND_00 ↔ CADPART_000_FACE_01_BND_03: mean=0.295357847, p95=0.540378974, length_ratio=0.958252, score=0.407904, status=UNRESOLVED
- CADPART_000_FACE_00_BND_03 ↔ CADPART_000_FACE_01_BND_03: mean=0.204481831, p95=0.650667315, length_ratio=0.415864, score=0.358287, status=UNRESOLVED
- CADPART_000_FACE_00_BND_03 ↔ CADPART_000_FACE_01_BND_01: mean=0.224835723, p95=0.626431483, length_ratio=0.393635, score=0.355399, status=UNRESOLVED
- CADPART_000_FACE_00_BND_00 ↔ CADPART_000_FACE_01_BND_02: mean=0.614396874, p95=0.637518131, length_ratio=0.168510, score=0.324899, status=UNRESOLVED

## VERTICAL_TAIL (CADPART_005)

- STEP: `/data/home/cuiyuehan/project/mesh2cad/ours3/v7b_profile_type_aware_open_shell_reconstruction/06_candidates/CADPART_005/PRIMARY/candidate.step`
- OCC valid: `True`
- Face count: `2`
- Free edges: `8`

### CADPART_005_FACE_00

Surface=BSPLINE; orientation=0; wires=1; edges=4; valid=True

| Boundary | Semantic | Curve | Length | Pcurve |
|---|---|---:|---:|---:|
| CADPART_005_FACE_00_BND_00 | ROOT_BOUNDARY | BSPLINE | 0.0121352166 | True |
| CADPART_005_FACE_00_BND_01 | SIDE_BOUNDARY | BSPLINE | 2.28460365 | True |
| CADPART_005_FACE_00_BND_02 | TIP_BOUNDARY | BSPLINE | 1.04274176 | True |
| CADPART_005_FACE_00_BND_03 | SIDE_BOUNDARY | BSPLINE | 2.54303876 | True |

### CADPART_005_FACE_01

Surface=BSPLINE; orientation=0; wires=1; edges=4; valid=True

| Boundary | Semantic | Curve | Length | Pcurve |
|---|---|---:|---:|---:|
| CADPART_005_FACE_01_BND_00 | ROOT_BOUNDARY | BSPLINE | 0.0317334339 | True |
| CADPART_005_FACE_01_BND_01 | SIDE_BOUNDARY | BSPLINE | 1.09565691 | True |
| CADPART_005_FACE_01_BND_02 | TIP_BOUNDARY | BSPLINE | 0.0035137925 | True |
| CADPART_005_FACE_01_BND_03 | SIDE_BOUNDARY | BSPLINE | 1.1941025 | True |

### Shared-boundary decision

Expected shared design boundaries: `2`
Accepted matches: `0`
Status: `UNRESOLVED`

- CADPART_005_FACE_00_BND_02 ↔ CADPART_005_FACE_01_BND_01: mean=0.181188782, p95=0.351309538, length_ratio=0.951705, score=0.406098, status=UNRESOLVED
- CADPART_005_FACE_00_BND_02 ↔ CADPART_005_FACE_01_BND_03: mean=0.195743924, p95=0.382859022, length_ratio=0.873243, score=0.377494, status=UNRESOLVED
- CADPART_005_FACE_00_BND_01 ↔ CADPART_005_FACE_01_BND_03: mean=0.0248624609, p95=0.09831562, length_ratio=0.522674, score=0.375140, status=UNRESOLVED
- CADPART_005_FACE_00_BND_01 ↔ CADPART_005_FACE_01_BND_01: mean=0.0292599722, p95=0.114451518, length_ratio=0.479583, score=0.369837, status=UNRESOLVED
- CADPART_005_FACE_00_BND_03 ↔ CADPART_005_FACE_01_BND_03: mean=0.0314233282, p95=0.185107538, length_ratio=0.469557, score=0.363713, status=UNRESOLVED
- CADPART_005_FACE_00_BND_03 ↔ CADPART_005_FACE_01_BND_01: mean=0.0327288044, p95=0.170872716, length_ratio=0.430846, score=0.358667, status=UNRESOLVED

