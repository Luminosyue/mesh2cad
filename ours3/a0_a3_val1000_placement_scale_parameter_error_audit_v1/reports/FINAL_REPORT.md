# A0 vs A3 VAL1000 Placement / Scale Parameter Error Audit V1

CURRENT_GATE = A0_A3_VAL1000_PLACEMENT_SCALE_PARAMETER_ERROR_AUDIT_COMPLETE

RESULT_PATTERN = STRUCTURE_GAIN_PARAMETER_BOTTLENECK

TEST_TOUCHED = NO

## Valid counts

- A0_GEOMETRY_VALID_N = 223
- A3_GEOMETRY_VALID_N = 211
- BOTH_VALID_N = 189

## Center

- A0_CENTER_MEAN = 0.26103371; A3_CENTER_MEAN = 0.11801006
- A0_CENTER_MEDIAN = 0.03428533; A3_CENTER_MEDIAN = 0.01850900
- PAIRED_DELTA_MEAN = -0.00460382; A3_BETTER_N = 76; A0_BETTER_N = 71

## Extent

- A0_EXTENT_MEAN = 0.29373567; A3_EXTENT_MEAN = 0.21944881
- A0_EXTENT_MEDIAN = 0.07030008; A3_EXTENT_MEDIAN = 0.03605235
- PAIRED_DELTA_MEAN = -0.01721796; A3_BETTER_N = 76; A0_BETTER_N = 69

## Scale

- A0_DIAG_RATIO_MEDIAN = 0.99997794; A3_DIAG_RATIO_MEDIAN = 0.99995970
- A0_SCALE_LOG_ERROR_MEAN = 0.50815951; A3_SCALE_LOG_ERROR_MEAN = 0.33712554; PAIRED_DELTA_MEAN = 0.02113560
- A0_SCALE_COLLAPSE_N = 24; A3_SCALE_COLLAPSE_N = 26

## Centroid

- A0_CENTROID_ERROR = 0.26544421
- A3_CENTROID_ERROR = 0.12805899

## Correlation (Spearman)

- A0/A3 Chamfer vs Center = 0.82822097 / 0.80806554
- A0/A3 Chamfer vs Extent = 0.86380832 / 0.81144385
- A0/A3 Chamfer vs Scale = 0.69006000 / 0.72731363

## Taxonomy

- A0/A3 SCALE_COLLAPSE = 24 / 26
- A0/A3 SCALE_EXPANSION = 0 / 0
- A0/A3 PLACEMENT_SHIFT = 27 / 27
- A0/A3 EXTENT_DISTORTION = 53 / 48
- A3 STRUCTURE_CORRECT_PARAMETER_WRONG = 23

## Q1-Q4

1. Q1: Paired center, extent and scale results above determine whether A3's geometry gain comes from better parameter recovery; this is not inferred from Chamfer alone.
2. Q2: Tiny predictions have genuinely small `pred_diag / gt_diag` in the frozen world coordinate system. They are scale-collapse failures, not per-object camera-fit artifacts.
3. Q3: A3 has 23 diagnostic cases with high structure score but poor geometry/parameter measurements.
4. Q4: The observed outcome is classified as `STRUCTURE_GAIN_PARAMETER_BOTTLENECK`; parameter/placement recovery remains a bottleneck whenever the error tails and failure counts remain material.

## Integrity

MODEL_CHANGED = NO; CHECKPOINT_CHANGED = NO; PREDICTIONS_CHANGED = NO; EVALUATOR_CHANGED = NO; EXACT9998_CHANGED = NO; TEST_TOUCHED = NO.
