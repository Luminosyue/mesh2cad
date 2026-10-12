# P1 Structure-Correct / Geometry-Bad Parameter Bottleneck Audit

CURRENT_GATE = COMPLETE

TEST_TOUCHED = NO

## Structure
- Geometry-valid: 239
- S1 sequence exact: 161
- S2 AST/dependency exact: 137
- S3 Op-F1 perfect: 142

## Core cohort
- S1 structure-correct + geometry-bad: 54 (33.5% of S1; 22.6% of geometry-valid)

## Primary root causes
- SCALE_ERROR: 18
- MULTIPLE_PARAMETER_ERRORS: 14
- UNRESOLVED: 14
- ORIGIN_ERROR: 5
- DIMENSION_ERROR: 3

## Decision
- P2_STATUS = JUSTIFIED
- RECOMMENDED_P2_TARGET = SIZE
- This is an association-based post-hoc diagnostic, not a causal claim. No P2 training was started.
