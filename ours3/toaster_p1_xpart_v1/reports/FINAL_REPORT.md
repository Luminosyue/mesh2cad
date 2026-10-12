# FINAL_REPORT

CURRENT_GATE=P1_TOASTER_FULL39_GLOBAL_ASSEMBLY_EVAL_COMPLETE
P1_PIPELINE=P1_OPERATION_AWARE_STRUCTURE_LOSS_V1
P1_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_operation_aware_structure_loss_v1/runs/p1
SOURCE_CASE=TOASTER
SOURCE_PART_N=39
XPART_INPUT_N=39
GLOBAL_TRANSFORM_SMOKE=PASS
FULL39_RAN=YES
P1_INFERENCE_PASS_N=39
DSL_PARSE_PASS_N=39
CAD_EXEC_PASS_N=39
BREP_VALID_N=39
STEP_RELOAD_PASS_N=39
GLOBAL_STEP_RELOAD_PASS_N=39
INVALID_N=0
INVALID_RATE=0.0
CD_LOCAL_VALID_N=39
CD_LOCAL_MEAN=1.6623956619546105
CD_LOCAL_MEDIAN=1.6476796095883681
CD_GLOBAL_VALID_N=39
CD_GLOBAL_MEAN=0.28812131733507884
CD_GLOBAL_MEDIAN=0.2626899218682227
IOU_VALID_N=0
IOU_MEAN=NA
IOU_MEDIAN=NA
CENTROID_ERROR_MEAN=0.452586053533723
BBOX_EXTENT_ERROR_MEAN=8.462862235544423
ASSEMBLED_PART_N=39
ASSEMBLY_STATUS=FULL_39_PART_ASSEMBLY
ASSEMBLY_STEP_EXPORT=PASS
ASSEMBLY_STEP_RELOAD=PASS
ASSEMBLY_XPART_CD=0.10014943394628352
ASSEMBLY_ORIGINAL_OBJ_CD=0.10119371656472664
ASSEMBLY_IOU=NOT_EVALUABLE
FINAL_P1_STEP=/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p1_xpart_v1/assembly/toaster_p1_native.step
FINAL_REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p1_xpart_v1/reports/FINAL_REPORT.md
CADFIT_TOUCHED=NO
NEXT_ALLOWED_STAGE=P1_VS_CADFIT_TOASTER_COMMON_CASE_EVAL_V1

## 1. Input / pipeline audit
39/39 X-Part meshes were consumed from the existing toaster X-Part output. Frozen P1 checkpoint, tokenizer, decoder, executor, and canonical normalization were reused. Per-part canonical inputs and inverse transforms are in `inputs/PART_xxx/`.

## 2. 3-part smoke
Automatic bbox-volume stratification selected PART_032, PART_000, PART_018. Local parse/execute/STEP reload and inverse-transform/global STEP reload all passed. Predictions show shape error, but no systematic origin collapse or axis flip.

## 3. Full39 inference
All PART_000...PART_038 were run independently. Every part has raw prediction, DSL, metadata, local STEP, global STEP, and row-level status. Failures, if any, would remain in the denominator; observed invalid count is zero.

## 4. CAD validity
BRepCheck analyzer returned valid for all 39 reloaded global STEP shapes. Solid count total is 40 (compound/part topology accounting).

## 5. Per-part geometry
See `eval/per_part_metrics.csv` and `eval/summary.json`. Local/global CD and centroid/bbox errors are computed against the corresponding X-Part mesh. IoU is `NOT_EVALUABLE` because no reliable frozen solid-Boolean evaluator is available for this case.

## 6. Global coordinate restoration
Global STEP files were generated solely by applying the stored inverse transform from each `inputs/PART_xxx/transform.json`; no ICP or recalibration was used.

## 7. Whole toaster assembly
The assembly uses only `steps_global/PART_xxx.step`, with independent parts retained and no Boolean fuse. Native STEP export and reload passed for all 39 parts. A tessellated STL is provided for visualization only.

## 8. Whole-object geometry
Assembly CD against the 39-part X-Part reference is 0.10014943394628352. Assembly CD against the original high-poly toaster OBJ is 0.10119371656472664. These are reported separately.

## 9. Failure taxonomy
`eval/per_part_metrics.csv` contains the required status columns and failure reason. Current invalid rate is 0/39. Structural operation breakdown is in `eval/operation_breakdown.csv`.

## 10. Representative cases
Gallery files: `gallery/best_cd_PART_*.png`, `gallery/median_cd_PART_*.png`, and `gallery/worst_cd_PART_*.png`, each showing X-Part GT, P1 global CAD, and overlay.

## 11. Limitations
The generic P1 evaluator has no toaster-specific GT DSL record, so exact/op-F1 and solid IoU are not meaningful here. BRep validity and mesh-level geometry metrics are reported independently.

## 12. Next allowed stage
The next permitted stage is a separate common-case comparison branch `toaster_p1_vs_cadfit_eval_v1`. CADFit history remains read-only and untouched.
