# Airplane P3 + X-Part + CADFit Route A V1

Independent Route A experiment. No Dora / MAC / Point2CAD. No reuse of previous airplane CAD or STEP.

```text
CURRENT_GATE=AIRPLANE_P3_XPART_CADFIT_ROUTE_A_V1
SOURCE_CASE=Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj
SOURCE_TRIANGLES=140164

P3_REEXECUTED=True
P3_PART_COUNT=9
P3_WATERTIGHT_PARTS=0
P3_WATERTIGHT_RATE=0.0

XPART_REEXECUTED=True
XPART_ATTEMPTED_PARTS=9
XPART_SUCCESSFUL_PARTS=9
XPART_WATERTIGHT_PARTS=9
XPART_WATERTIGHT_RATE=1.0
XPART_CAD_READY_PARTS=9

CADFIT_USED=True
CADFIT_FILTER_SKETCHES_USED=True
CADFIT_ATTEMPTED_PARTS=9
CADFIT_SUCCESSFUL_PARTS=9
CADQUERY_EXECUTABLE_PARTS=9

TOTAL_OPS=189
TOTAL_EXTRUDES=66
TOTAL_REVOLVES=0
TOTAL_CUTS=0
TOTAL_UNIONS=123

BREP_VALID_PARTS=9
STEP_RELOAD_VALID_PARTS=9
CAD_NATIVE_PARTS=9
CAD_NATIVE_PART_COVERAGE=1.0
CAD_NATIVE_TRIANGLE_COVERAGE=1.0

MEAN_CADFIT_IOU=0.6594
MEAN_CHAMFER=0.7433
MEAN_HAUSDORFF=1.1234
MEAN_COVERAGE=0.0550
MEAN_FP_OCCUPANCY=None

ASSEMBLY_STEP_RELOAD_VALID=None
FINAL_ASSEMBLY_STEP=None
ARTIFACT_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1
NEXT_PRIMARY_BLOCKER=No revolve recovered; PART_003 IoU=0.28 is Route B candidate
```

## Method

- Official P3-SAM (`p3_fresh_v6.py`) re-executed on GPU 5 with `--prompt-bs 16` after GPU 3 OOM.
- Official X-Part (`hy3d` env, whole-airplane object condition, batch size 9).
- OBJ→STL format conversion only. Triangle counts unchanged. No remesh / smooth / decimate before CADFit.
- Official CADFit `run_pipeline.py`: `--max-iterations 1`, fillet/chamfer OFF, `--keep-history`, `--skip-existing`, `--filter-sketches`.
- STEP from CadQuery program execution, not faceted STL→STEP.

## Per-part CADFit

| part | likely role | iou | extrude | revolve | union | cut | step | cad_native |
|---|---|---:|---:|---:|---:|---:|:---:|:---:|
| PART_000 | vertical tail | 0.8019 | 11 | 0 | 21 | 0 | Y | Y |
| PART_001 | left wing | 0.5705 | 4 | 0 | 7 | 0 | Y | Y |
| PART_002 | left propeller | 0.7271 | 19 | 0 | 37 | 0 | Y | Y |
| PART_003 | right propeller | 0.2826 | 1 | 0 | 1 | 0 | Y | Y |
| PART_004 | right wing | 0.7732 | 6 | 0 | 11 | 0 | Y | Y |
| PART_005 | fuselage | 0.7862 | 17 | 0 | 33 | 0 | Y | Y |
| PART_006 | right tailplane | 0.6949 | 1 | 0 | 1 | 0 | Y | Y |
| PART_007 | left tailplane | 0.6933 | 1 | 0 | 1 | 0 | Y | Y |
| PART_008 | dorsal feature | 0.6053 | 6 | 0 | 11 | 0 | Y | Y |

## Q1 — Meaningful P3 parts?

P3 produced 9 parts with triangle coverage 1.0. Geometrically they correspond to fuselage, two wings, two tailplanes, vertical tail, two propeller blades, and one dorsal feature. No tiny fragments. This is a cleaner, more CAD-like split than the tank 45-part run.

## Q2 — Open vs watertight?

All 9 P3 parts are open (`P3_WATERTIGHT_RATE=0.0`). After X-Part, all 9 complete parts are watertight, manifold, winding-consistent (`XPART_WATERTIGHT_RATE=1.0`). Open→watertight: 9. Still open: 0.

## Q3 — How many X-Part parts became CAD-native?

All 9 CAD-ready X-Part meshes entered CADFit. All 9 produced executable CadQuery programs, valid STEP reload, and `CAD_NATIVE=True`. Coverage of original P3 triangles is 1.0.

## Q4 — Construction operations?

CADFit used extrude + union only. `TOTAL_REVOLVES=0`, `TOTAL_CUTS=0`, fillet/chamfer OFF as configured. Yes, this round degenerated into extrude/union fitting; propeller / fuselage revolution was not recovered.

## Q5 — Best / worst parts?

- Best IoU: PART_000 (vertical tail) 0.802, then PART_005 (fuselage) 0.786 and PART_004 (right wing) 0.773.
- Best geometry residual: PART_005 chamfer 0.053.
- Worst: PART_003 (right propeller) IoU 0.283, 1 extrude only. Filter sketches dropped all loops (`FILTERED_LOOPS=0`). This is the primary Route B case.
- Wings: left 0.571 vs right 0.773 — asymmetric CADFit quality.

## Q6 — CAD-native assembly coverage?

All 9 parts are CAD-native, so part coverage and P3 triangle ownership coverage are both 1.0. A combined assembly STEP was not written in this pass (`FINAL_ASSEMBLY_STEP=None`). Per-part STEP files exist under `cadfit_routea/step/PART_XXX/`.

## Q7 — Airplane vs Tank for CADFit?

The airplane is a better *frontend* case: 9 semantic parts vs 45, 100% X-Part watertight, 100% CADFit CadQuery/STEP success. Geometry quality is mixed. Mean IoU 0.66 is lower than the tank 5-part canary mean 0.79, and again no revolve recovery. So: easier to complete the pipeline, not automatically easier to recover intended CAD ops. Hard leftover: PART_003 propeller (and possibly PART_001 left wing).

## Artifacts

- P3: `p3/part_metadata.json`, `p3/triangle_part_id.npy`
- X-Part: `xpart/PART_XXX/complete_part_XXX.obj`
- CADFit: `cadfit_routea/cadfit_raw/PART_XXX/`
- STEP: `cadfit_routea/step/PART_XXX/PART_XXX.step`
- QA: `cadfit_routea/qa/`
- Renders: `cadfit_routea/renders/PART_XXX/{01_source_xpart,02_cadfit_recon,03_overlay_projection,04_cad_feature_edges}.png`
