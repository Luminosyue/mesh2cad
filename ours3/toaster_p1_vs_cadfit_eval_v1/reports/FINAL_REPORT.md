# Toaster P1 vs CADFit: strict read-only comparison

CURRENT_GATE=P1_VS_CADFIT_TOASTER_COMMON_CASE_EVAL_COMPLETE
COMPARISON_CASE=TOASTER
DENOMINATOR_39=39
P1_VALID_N=39
CADFIT_VALID_N=39
COMMON_VALID_N=39
P1_INVALID_RATE=0.0
CADFIT_INVALID_RATE=0.0
P1_CD_GLOBAL_MEAN=0.28738920275531166
CADFIT_CD_GLOBAL_MEAN=0.00894972462202212
COMMON_VALID_CD_GLOBAL_MEAN_P1=0.28738920275531166
COMMON_VALID_CD_GLOBAL_MEAN_CADFIT=0.00894972462202212
P1_CENTROID_ERROR_MEAN=0.45258605353372305
CADFIT_CENTROID_ERROR_MEAN=3.860849307600196e-16
P1_ASSEMBLY_STATUS=FULL_39_PART_ASSEMBLY
CADFIT_ASSEMBLY_STATUS=FULL_39_PART_ASSEMBLY
P1_ASSEMBLY_CD_XPART=0.09760440685833827
CADFIT_ASSEMBLY_CD_XPART=0.02286403339704552
P1_ASSEMBLY_CD_OBJ=0.0993876241353334
CADFIT_ASSEMBLY_CD_OBJ=0.023477315084543034
FINAL_REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p1_vs_cadfit_eval_v1/reports/FINAL_REPORT.md
NEXT_ALLOWED_STAGE=RESULT_REVIEW_OR_ADDITIONAL_READONLY_DIAGNOSTICS

## Scope and evaluator
Both historical branches were read-only. Denominator is fixed at 39. Geometry means use the strict common-valid set, which is all 39 parts. Both methods use the same X-Part GT meshes, 4096 deterministic surface samples per part, seed 20260916, and symmetric mean nearest-neighbor Chamfer distance. Whole assemblies use 16000 samples. IoU is `NOT_EVALUABLE` because no reliable common frozen solid-Boolean evaluator is available.

## CAD validity
P1 and CADFit each have 39/39 BRep-valid, STEP-reloadable parts and full 39-part assemblies. Invalid rates tie at 0.0. Neither method has a validity/completeness advantage on this case.

## Per-part geometry
CADFit wins global CD on 39/39 common-valid parts; P1 wins 0/39. Mean CD is 0.287389 for P1 versus 0.008950 for CADFit. Mean centroid error is 0.452586 versus 3.86085e-16. Mean bbox extent error is 8.462862 versus 0.244256. This is decisive geometry evidence for CADFit.

P1 best 10 by CD: PART_027, PART_000, PART_007, PART_032, PART_030, PART_012, PART_011, PART_028, PART_020, PART_033.

CADFit best 10 by CD: PART_002, PART_006, PART_005, PART_010, PART_032, PART_031, PART_030, PART_009, PART_000, PART_022.

Largest P1-over-CADFit gains: none. The ranking table retains the ten numerically least-negative deltas for audit: PART_027, PART_000, PART_007, PART_032, PART_030, PART_012, PART_011, PART_028, PART_020, PART_033.

Largest CADFit-over-P1 gains: PART_009, PART_008, PART_005, PART_004, PART_002, PART_006, PART_023, PART_034, PART_013, PART_010.

## Assembly reconstruction
Both assemblies are complete and reload successfully. Against the X-Part assembly, P1 CD is 0.097604, CADFit CD is 0.022864. Against the original high-poly OBJ, P1 CD is 0.099388, CADFit CD is 0.023477. CADFit also has much lower assembly centroid, bbox-center, and bbox-extent errors. CADFit is stronger in assembly fidelity; completeness is tied.

## Requested interpretation
1. Effective parts: P1 39, CADFit 39.
2. Invalid rate: tied at zero.
3. Per-part geometry: CADFit is better on every part under unified global CD.
4. Assembly: both are complete; CADFit is substantially closer to both references.
5. P1 shows strong validity but weak geometry fidelity: yes. It consistently emits valid CAD, but mean CD, centroid, and extent errors are much larger.
6. “CADFit individual parts more accurate but assembly weaker”: no. CADFit is more accurate per part and at assembly level.
7. P1-suited part types: this toaster case supplies no supported class-level advantage because P1 wins no part. Any stronger claim would exceed the evidence.
8. CADFit-suited parts: all 39 observed toaster X-Parts, including both small detail pieces and large body pieces, under this metric protocol.
9. Final conclusion: validity and assembly completeness are tied; geometry fidelity and assembly placement decisively favor CADFit. P1 demonstrates robust executable CAD generation, not competitive toaster reconstruction accuracy in this run.

## Visual evidence
`gallery/whole_toaster_comparison.png` uses one XZ camera, identical bounds, background, and point-render style. Per-part panels cover the largest CADFit gains, closest outcomes, and cases where both errors are relatively high. No P1-better or validity-exclusive gallery exists because those categories are empty; `eval/representative_selection.json` records this explicitly.

## Files
- `manifest/comparison_manifest.json`: frozen paths, source hashes, validity scope, evaluator definition.
- `eval/p1_vs_cadfit_per_part.csv`: strict 39-row comparison.
- `eval/p1_vs_cadfit_summary.json`: aggregate and assembly metrics.
- `eval/rankings.csv`: four requested ranking tables.
- `gallery/`: whole-object and representative per-part comparisons.

## Integrity
P1 and CADFit were not run, modified, or overwritten. CADFit was not rerun. Dora outputs were not used. Comparison artifacts exist only under `ours3/toaster_p1_vs_cadfit_eval_v1`.
