# TANK_FROZEN_P3_TO_CADFIT_V1

FINAL_GATE=`TANK_FROZEN_P3_TO_CADFIT_V1_COMPLETE`

This experiment reuses the frozen tank P3 segmentation and sends each component mesh to the real CADFit pipeline. No existing experiment files were rewritten. P3, PhysX, MAC, SuperFit, and Point2CAD were not re-run.

## Provenance

- SOURCE_TANK_OBJ: `/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj`
- FROZEN_P3_SOURCE: `/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_rerun_v1/p3_max_367k_4000`
- P3_REEXECUTED: `False`
- P3_SOURCE_FILES_MODIFIED: `0`
- CADFit repo: `/data/home/cuiyuehan/project/mesh2cad/CADFit`
- CADFit commit: `fb31f63b79805fff4c5a5c6fa5f8b2f00fe86536`

## Totals

- P3_PARTS_TOTAL: 45
- WATERTIGHT_PARTS: 0
- NON_WATERTIGHT_PARTS: 45
- REPAIRED_PARTS: 0
- watertight class A/B/C: {'A': 0, 'B': 0, 'C': 45}
- CADFIT_ATTEMPTED: 45
- CADFIT_PROGRAM_SUCCESS: 30
- CADFIT_STEP_SUCCESS: 30
- CAD_NATIVE_PARTS: 30
- FACETED_BREP_PARTS: 0
- QA_PASS_PARTS: 4
- CAD_NATIVE_RATE: 0.666667
- QA_PASS_RATE: 0.088889

## Method notes

- OBJ→STL conversion is a direct triangle dump. No remesh, voxelization, smoothing, or simplification is applied in this experiment.
- Class B repair is `trimesh.repair.fill_holes` only, and only when the close is trivial. Class C parts are not aggressively rebuilt; they are still sent to CADFit because the real CADFit pipeline accepts open meshes and internally alpha-wraps them for IoU.
- CAD-native requires an executable CadQuery construction program plus analytic (non-faceted) BRep after OpenCascade reload.

## Per-part

| part | tris | class | attempted | program | step | native | faceted | chamfer | coverage | fail |
|---|---:|---|---|---|---|---|---|---:|---:|---|
| part_000 | 1902 | C | True | True | True | True | False | 0.00287493 | 0.9143 |  |
| part_001 | 2751 | C | True | False | False | False | False |  |  | TIMEOUT |
| part_002 | 3550 | C | True | True | True | True | False | 0.0199389 | 0.1384 | GEOMETRY_QA_FAIL |
| part_003 | 2018 | C | True | True | True | True | False | 0.00524133 | 0.7937 |  |
| part_004 | 4308 | C | True | True | True | True | False | 0.0339412 | 0.0806 | GEOMETRY_QA_FAIL |
| part_005 | 3946 | C | True | True | True | True | False | 0.0319995 | 0.1370 | GEOMETRY_QA_FAIL |
| part_006 | 4258 | C | True | True | True | True | False | 0.0320679 | 0.1362 | GEOMETRY_QA_FAIL |
| part_007 | 1690 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_008 | 1741 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_009 | 4337 | C | True | True | True | True | False | 0.0326845 | 0.1272 | GEOMETRY_QA_FAIL |
| part_010 | 5733 | C | True | True | True | True | False | 0.025598 | 0.1851 | GEOMETRY_QA_FAIL |
| part_011 | 2436 | C | True | True | True | True | False | 0.0507139 | 0.0254 | GEOMETRY_QA_FAIL |
| part_012 | 1750 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_013 | 2685 | C | True | False | False | False | False |  |  | TIMEOUT |
| part_014 | 2856 | C | True | True | True | True | False | 0.0467291 | 0.0315 | GEOMETRY_QA_FAIL |
| part_015 | 2170 | C | True | True | True | True | False | 0.0522026 | 0.0139 | GEOMETRY_QA_FAIL |
| part_016 | 2537 | C | True | True | True | True | False | 0.0480877 | 0.0383 | GEOMETRY_QA_FAIL |
| part_017 | 4108 | C | True | True | True | True | False | 0.0159814 | 0.2998 | GEOMETRY_QA_FAIL |
| part_018 | 2637 | C | True | False | False | False | False |  |  | TIMEOUT |
| part_019 | 1637 | C | True | True | True | True | False | 0.0386351 | 0.0339 | GEOMETRY_QA_FAIL |
| part_020 | 2234 | C | True | True | True | True | False | 0.0486979 | 0.0481 | GEOMETRY_QA_FAIL |
| part_021 | 2617 | C | True | True | True | True | False | 0.01785 | 0.0630 | GEOMETRY_QA_FAIL |
| part_022 | 2371 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_023 | 7921 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_024 | 2783 | C | True | True | True | True | False | 0.0167831 | 0.0876 | GEOMETRY_QA_FAIL |
| part_025 | 15540 | C | True | False | False | False | False |  |  | TIMEOUT |
| part_026 | 2361 | C | True | True | True | True | False | 0.0231393 | 0.0530 | GEOMETRY_QA_FAIL |
| part_027 | 2297 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_028 | 2600 | C | True | True | True | True | False | 0.0241883 | 0.0344 | GEOMETRY_QA_FAIL |
| part_029 | 6750 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_030 | 2391 | C | True | True | True | True | False | 0.0151646 | 0.1440 | GEOMETRY_QA_FAIL |
| part_031 | 3867 | C | True | True | True | True | False | 0.0352589 | 0.0435 | GEOMETRY_QA_FAIL |
| part_032 | 2364 | C | True | True | True | True | False | 0.0486759 | 0.0457 | GEOMETRY_QA_FAIL |
| part_033 | 2061 | C | True | False | False | False | False |  |  | TIMEOUT |
| part_034 | 1787 | C | True | True | True | True | False | 0.0497425 | 0.0481 | GEOMETRY_QA_FAIL |
| part_035 | 8016 | C | True | True | True | True | False | 0.0276718 | 0.1421 | GEOMETRY_QA_FAIL |
| part_036 | 2887 | C | True | False | False | False | False |  |  | TIMEOUT |
| part_037 | 7408 | C | True | True | True | True | False | 0.0584493 | 0.0620 | GEOMETRY_QA_FAIL |
| part_038 | 12978 | C | True | True | True | True | False | 0.0114975 | 0.7131 |  |
| part_039 | 14377 | C | True | True | True | True | False | 0.017023 | 0.7607 |  |
| part_040 | 10111 | C | True | True | True | True | False | 0.0441101 | 0.2043 | GEOMETRY_QA_FAIL |
| part_041 | 10803 | C | True | False | False | False | False |  |  | CADFIT_NO_PROGRAM |
| part_042 | 168880 | C | True | True | True | True | False | 0.462683 | 0.0149 | GEOMETRY_QA_FAIL |
| part_043 | 7373 | C | True | True | True | True | False | 0.0795008 | 0.0244 | GEOMETRY_QA_FAIL |
| part_044 | 5639 | C | True | False | False | False | False |  |  | TIMEOUT |

## Failure counts

{
  "NONE": 4,
  "TIMEOUT": 7,
  "GEOMETRY_QA_FAIL": 26,
  "CADFIT_NO_PROGRAM": 8
}

BEST_PART=part_000

