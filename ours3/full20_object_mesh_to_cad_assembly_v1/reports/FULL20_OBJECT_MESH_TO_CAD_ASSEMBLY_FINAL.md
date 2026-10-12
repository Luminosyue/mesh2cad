# FULL20 Object Mesh to CAD Assembly — Final Report

ROOT: `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1`

**Complete full assemblies: 7/20. FULL20_OBJECT_CAD_ASSEMBLY_PASS = FALSE.**

Frozen selection contains 20 full source meshes and all 304 X-Part parts. No failed object was replaced and no part was deleted.

Existing CAD reused/read back: 254/304; new CAD programs generated: 0. New work completes common-frame q14/V3 artifacts, compilation, assembly and rendering.

Valid complete part chain: 221/304; q14: 235/304; V3: 235/304.

Tank: 45 parts; complete assembly: False; assembly type: COMPOUND_MULTI_BODY. PART_029 reuses the exact frozen generated q stream and STEP; source SHA256 checks preserved. Only that part is marked strict model-generated.

## Objects

| Object | Parts | Valid parts | Full assembly | CD | Surface IoU64 | Failure |
|---|---:|---:|---|---:|---:|---|
| tank | 45 | 33 | False | None | None | FAILED_PARTS: PART_004,PART_010,PART_012,PART_013,PART_015,PART_017,PART_019,PART_024,PART_025,PART_027,PART_037,PART_044 |
| airplane | 9 | 5 | False | None | None | FAILED_PARTS: PART_000,PART_002,PART_003,PART_008 |
| robot | 17 | 15 | False | None | None | FAILED_PARTS: PART_006,PART_009 |
| toaster | 39 | 37 | False | None | None | FAILED_PARTS: PART_020,PART_035 |
| android_figure_orange | 5 | 5 | True | 0.010216184212848908 | 0.5339290146438322 |  |
| 3d_dollhouse_sofa | 8 | 3 | False | None | None | FAILED_PARTS: PART_000,PART_001,PART_003,PART_004,PART_006 |
| winerack | 34 | 4 | False | None | None | FAILED_PARTS: PART_004,PART_005,PART_006,PART_007,PART_008,PART_009,PART_010,PART_011,PART_012,PART_013,PART_014,PART_015,PART_016,PART_017,PART_018,PART_019,PART_020,PART_021,PART_022,PART_023,PART_024,PART_025,PART_026,PART_027,PART_028,PART_029,PART_030,PART_031,PART_032,PART_033 |
| pottery_large | 3 | 3 | True | 0.008020924757990551 | 0.5795135569818077 |  |
| mini_fire_engine | 16 | 7 | False | None | None | FAILED_PARTS: PART_004,PART_005,PART_006,PART_007,PART_009,PART_010,PART_011,PART_012,PART_013 |
| fire_truck | 8 | 8 | True | 0.006898626185753436 | 0.6324755346139905 |  |
| mini_excavator | 10 | 10 | True | 0.008962746421634981 | 0.6624253075571177 |  |
| pressure_cooker | 13 | 11 | False | None | None | FAILED_PARTS: PART_003,PART_006 |
| speaker_big | 12 | 10 | False | None | None | FAILED_PARTS: PART_000,PART_005 |
| dvd_player | 7 | 6 | False | None | None | FAILED_PARTS: PART_001 |
| cube | 7 | 7 | True | 0.007667643859989498 | 0.5946782475166754 |  |
| 2_of_jenga_classic_game | 13 | 11 | False | None | None | FAILED_PARTS: PART_003,PART_011 |
| assorted_vegetable_set | 11 | 5 | False | None | None | FAILED_PARTS: PART_004,PART_005,PART_006,PART_007,PART_008,PART_010 |
| baby_car | 7 | 7 | True | 0.008372537287411925 | 0.5630081300813008 |  |
| birdhouse | 36 | 30 | False | None | None | FAILED_PARTS: PART_008,PART_009,PART_020,PART_021,PART_028,PART_029 |
| aroma_stainless_steel_milk_frother_2_cup | 4 | 4 | True | 0.006878842726856556 | 0.5682166581502299 |  |

## Initial completeness audit correction

The initial audit incorrectly used successful X-Part count instead of original P3 part count. The 20 object identities were retained; counts were explicitly corrected, the initial manifest/hash preserved, and no failed object was replaced. Only 15/20 selected objects satisfy the full input gate. The selected objects require 304 parts, of which 50 X-Part meshes are absent across five objects. Historical object-specific folders were searched without recovering those assets. Initial partial Winerack PASS was invalidated. See INVENTORY_CORRECTION.json and MISSING_XPART_HISTORY_SEARCH.json.

## Evaluation and provenance

CD uses the existing unified CAD benchmark: 20,000 area-weighted surface samples, seed 0, symmetric mean Euclidean nearest-neighbor distance divided by full source mesh bbox diagonal. The existing P3 surface voxel IoU at resolution 64 is reported explicitly as surface IoU64. It must not be interpreted as solid Boolean volume IoU. Open full meshes have undefined volume error. No ICP or prediction-derived alignment was used.

Part geometry gates compare original reconstructed CAD against q14/V3 CAD; tolerance values were recorded in EXECUTION_CONTRACT.json before the production batch. Historical reconstruction NEEDS_REFINEMENT flags are retained. Passing execution/assembly is not a claim of exact source-mesh reconstruction.

Compact IR V3 in this project relies on the source semantic parameter template and compiler. The V3 file is delivered with its q14 metadata, source program/template, compiler and transform metadata. No V4 or new grammar was introduced.

All new q14 parts use the same full-object normalization matrix and inverse. Historical q14 artifacts retain their original frames and explicit inverse mapping. STEP is a compound of all part solids, with part identities and body counts retained in assembly_manifest.json; no boolean union.

Tank generated output includes a tokenizer <|eot_id|> suffix after the grammar E. It is removed only at the parser input transport boundary; the frozen file and q stream remain byte-identical.

## Paper demo selection

android_figure_orange, pottery_large, aroma_stainless_steel_milk_frother_2_cup, fire_truck, cube, baby_car

Tank main figure: not generated because the full-object gate failed. Galleries retain every frozen object; incomplete objects have explicit failure cards.

## Failed parts

- tank/PART_004: AssertionError: Q14_BREP_INVALID
- tank/PART_010: AssertionError: Q14_BREP_INVALID
- tank/PART_012: AssertionError: Q14_BREP_INVALID
- tank/PART_013: AssertionError: Q14_BREP_INVALID
- tank/PART_015: AssertionError: Q14_BREP_INVALID
- tank/PART_017: AssertionError: Q14_BREP_INVALID
- tank/PART_019: AssertionError: Q14_BREP_INVALID
- tank/PART_024: RAW_VS_Q14_GEOMETRY_TOLERANCE
- tank/PART_025: AssertionError: Q14_BREP_INVALID
- tank/PART_027: RAW_VS_Q14_GEOMETRY_TOLERANCE
- tank/PART_037: AssertionError: Q14_BREP_INVALID
- tank/PART_044: AssertionError: Q14_BREP_INVALID
- airplane/PART_000: AssertionError: Q14_BREP_INVALID
- airplane/PART_002: AssertionError: Q14_BREP_INVALID
- airplane/PART_003: AssertionError: Q14_BREP_INVALID
- airplane/PART_008: AssertionError: Q14_BREP_INVALID
- robot/PART_006: RAW_VS_Q14_GEOMETRY_TOLERANCE
- robot/PART_009: AssertionError: Q14_BREP_INVALID
- toaster/PART_020: RAW_VS_Q14_GEOMETRY_TOLERANCE
- toaster/PART_035: RAW_VS_Q14_GEOMETRY_TOLERANCE
- 3d_dollhouse_sofa/PART_000: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- 3d_dollhouse_sofa/PART_001: RAW_VS_Q14_GEOMETRY_TOLERANCE
- 3d_dollhouse_sofa/PART_003: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- 3d_dollhouse_sofa/PART_004: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- 3d_dollhouse_sofa/PART_006: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_004: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_005: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_006: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_007: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_008: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_009: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_010: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_011: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_012: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_013: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_014: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_015: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_016: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_017: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_018: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_019: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_020: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_021: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_022: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_023: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_024: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_025: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_026: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_027: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_028: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_029: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_030: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_031: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_032: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- winerack/PART_033: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_004: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_005: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_006: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_007: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_009: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_010: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_011: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_012: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- mini_fire_engine/PART_013: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- pressure_cooker/PART_003: AssertionError: Q14_BREP_INVALID
- pressure_cooker/PART_006: AssertionError: Q14_BREP_INVALID
- speaker_big/PART_000: RAW_VS_Q14_GEOMETRY_TOLERANCE
- speaker_big/PART_005: RAW_VS_Q14_GEOMETRY_TOLERANCE
- dvd_player/PART_001: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- 2_of_jenga_classic_game/PART_003: RAW_VS_Q14_GEOMETRY_TOLERANCE
- 2_of_jenga_classic_game/PART_011: RAW_VS_Q14_GEOMETRY_TOLERANCE
- assorted_vegetable_set/PART_004: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- assorted_vegetable_set/PART_005: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- assorted_vegetable_set/PART_006: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- assorted_vegetable_set/PART_007: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- assorted_vegetable_set/PART_008: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- assorted_vegetable_set/PART_010: MISSING_XPART_FROM_ORIGINAL_FULL_PART_SET
- birdhouse/PART_008: AssertionError: Q14_BREP_INVALID
- birdhouse/PART_009: RAW_VS_Q14_GEOMETRY_TOLERANCE
- birdhouse/PART_020: AssertionError: Q14_BREP_INVALID
- birdhouse/PART_021: RAW_VS_Q14_GEOMETRY_TOLERANCE
- birdhouse/PART_028: RAW_VS_Q14_GEOMETRY_TOLERANCE
- birdhouse/PART_029: RAW_VS_Q14_GEOMETRY_TOLERANCE

## Reproduction

Run `xvfb-run -a python3 code/pipeline.py run` to resume. Existing terminal part results and DONE objects are reused. Individual part repair histories are in cad_parts/<part>/repairs.json. No model training was launched.

## Deliverables

- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/manifests/FULL20_OBJECT_MANIFEST.csv`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/tables/FULL20_OBJECT_RESULTS.csv`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/tables/FULL20_ALL_PART_RESULTS.csv`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/reports/FULL20_OBJECT_MESH_TO_CAD_ASSEMBLY_FINAL.md`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/paper_demo/FULL20_ASSEMBLED_CAD_GALLERY.png`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/paper_demo/FULL20_MESH_TO_CAD_GALLERY.png`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/paper_demo/PAPER_MAIN_FULL_OBJECT_DEMO.png`
- `/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/paper_demo/TANK_FULL_DEMO.png` (not produced: full-object gate failed)
