# CASE09 ALL-PART MAC + FutureCAD-compatible grounding V2

Gate: `CASE09_ALL_PARTS_MAC_FUTURECAD_V2_PASS`

## Provenance

- Frozen V1: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1`
- Source SHA256: `ec3b6fb83ce405bd4c6cd41bb506ef9e5a8995919fb32ab9c40411f400e823cd`
- P3 and PhysX were reused after provenance verification; neither was rerun.
- Every final STEP is the direct execution output of a saved MAC-generated program over frozen measured specs.

## MAC audit

- 8/8 parts attempted and succeeded; 91 real provider calls.
- Input tokens: 347079; output tokens: 92068.
- No deterministic debug fallback replaced a selected MAC result.

## FutureCAD audit

- The official repository was found, but it does not publish runnable BRepGround code, weights, or inference.
- Mode is explicitly FUTURECAD_COMPATIBLE_GROUNDING_PROXY; official FutureCAD was not claimed as used.
- No final operation targets a local face/edge, so grounding is correctly recorded as not required instead of fabricating queries.

## Final aircraft

- Geometry: Q1; Chamfer=0.004335041; P95=0.010386289; Coverage02=1.000000000.
- BRep: valid; components=8; faces=158; edges=414.
- Sharp-edge recall improved from 0.8381348381 to 0.9456489456.
- Feature-boundary recall improved from 0.9830899308 to 0.9961568025.
- Structure Q: PASS; strip edges=10 (0.024155).

## Human semantic review

- Wings and tails are global measured-profile loft features, not independent transverse strip faces.
- Propeller uses two measured blade lofts organized by a measured instance pattern; no unmeasured hub or forced symmetry was invented.
- All selected programs avoid fixed face/edge array indices.

## Artifacts

- Final STEP: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2/06_assembly/CASE09_all_parts_mac_futurecad_v2.step`
- Main comparison: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2/artifacts/source_v1_v2_true_edges.png`
- True edges: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2/artifacts/freecad_like_true_edge_comparison.png`
- Grounding debug: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2/artifacts/grounding_debug.png`

## Verification

- 36 tests passed; 0 failed.
- Test log: `/data/home/cuiyuehan/project/mesh2cad/ours3/case09_all_parts_mac_futurecad_v2/metrics/pytest.log`
