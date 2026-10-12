# AST-aligned Parameter Error Audit V1

CURRENT_GATE = A0_A3_VAL1000_AST_ALIGNED_PARAMETER_ERROR_AUDIT_COMPLETE  
RESULT_PATTERN = ALIGNED_PARAMETER_GAIN_WITH_RESIDUAL_LOCAL_SCALE_FAILURES  
NEXT_METHOD_DIRECTION = MIXED_PARAMETER_MODELING  
TEST_TOUCHED = NO

## Alignment

- VAL_N = 1000
- GT/A0/A3 AST parse = 1000 / 882 / 904
- Unambiguous arm-operation alignments = 2850
- Ambiguous alignments = 0
- Strict paired numeric parameters = 3920

## Q1-Q5

1. Top A3 structure gains: Cut (+0.2242), ExtrudePolygon (+0.1883), Extrude (+0.0376), Union (-0.0191), Box (-0.0855).
2. Supported paired-N>=20 regressions: none. Largest residual A3 fields are listed in JSON.
3. A3 scale-collapse root causes: {'UNRESOLVED': 10, 'OPERATION_LOCAL_PARAMETER_ERROR': 15, 'MULTIPLE_SCALE_PARAMETERS': 1}.
4. A3 improves all supported comparable fields at paired N>=20 in mean; remaining failures are concentrated in local/unresolved and structurally unaligned cases.
5. Recommended next direction: `MIXED_PARAMETER_MODELING`. No method was implemented.

## Integrity

MODEL_CHANGED = NO; CHECKPOINT_CHANGED = NO; PREDICTIONS_CHANGED = NO; PARSER_CHANGED = NO; EXECUTOR_CHANGED = NO; EVALUATOR_CHANGED = NO; EXACT9998_CHANGED = NO; TEST_TOUCHED = NO.
