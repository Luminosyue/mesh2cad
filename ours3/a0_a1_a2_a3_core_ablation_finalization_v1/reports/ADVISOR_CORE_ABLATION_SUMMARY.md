# EXACT9998 A0-A3 Curve Modality Ablation

Formal VAL1000 post-hoc finalization. TEST remained blind and no checkpoint, prediction, evaluator, parser, executor, or geometry metric was modified.

## Core Table

| Input | CE | Exact | Op-F1 | Op Recall | Parse | STEP Export | STEP Reload | Geometry-valid | Chamfer | H95 | Volume error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Surface | 0.5021 | 0.047 | 0.6318 | 0.6685 | 0.882 | 0.874 | 0.862 | 0.223 (223) | 0.06393 | 0.16751 | 0.53331 |
| Surface + GT-BRep-Line | 0.4954 | 0.052 | 0.7578 | 0.7889 | 0.941 | 0.929 | 0.901 | 0.234 (234) | 0.07225 | 0.19632 | 0.49101 |
| Surface + GT-BRep-Nonline | 0.4982 | 0.041 | 0.6842 | 0.7152 | 0.875 | 0.868 | 0.850 | 0.211 (211) | 0.05272 | 0.15164 | 0.61007 |
| Surface + GT-BRep-All-Curves | 0.4923 | 0.046 | 0.7390 | 0.7766 | 0.904 | 0.894 | 0.869 | 0.211 (211) | 0.05359 | 0.15940 | 0.99295 |

## Interpretation

- A1 is the strongest arm on program structure: Op-F1, Parse, and STEP export.
- A2 is the geometry-distance leader in the original valid-only table, but this must be checked against paired/common-valid coverage.
- A3 is not called globally best unless the paired/common-valid audit supports it.
- STEP Export and STEP Reload are reported separately. Reload headline denominator is all 1000 VAL cases.
- Volume error is valid-only and its mean is sensitive to extreme outliers; the distribution and top-20 audit are included.

## Integrity

- TEST_TOUCHED: `NO`
- RESULT_PATTERN: `ASYMMETRIC_MODALITY_BENEFITS_WITH_NAIVE_FUSION_INTERFERENCE`
- P1 training alive at audit time: `True`
