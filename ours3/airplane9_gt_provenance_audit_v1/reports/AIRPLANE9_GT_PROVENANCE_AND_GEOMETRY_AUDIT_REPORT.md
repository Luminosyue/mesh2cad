# AIRPLANE9_GT_PROVENANCE_AND_GEOMETRY_AUDIT_V1

AIRPLANE_PART_N=9
FROZEN_HASH_N=0/9
CURRENT_HASH_N=9/9
FROZEN_EXEC_PASS_N=9/9
CURRENT_EXEC_PASS_N=9/9
DUAL_VALID_N=9/9

VERSION_CLASSIFICATION=CURRENT_IS_CANONICAL; RAW_VERBOSE_GT vs CURRENT_GT are different geometry representations
CANONICAL_GT_VERSION=CURRENT
CANONICAL_GT_RESOLVED=YES
FREEZE_INTEGRITY_GATE_V2=PASS
NEXT_ACTION=STOP_BEFORE_QUANTIZATION

Evidence: frozen PART_000 is 148562 bytes with 65 spline calls; current PART_000 is 11486 bytes with 9 spline calls. Dual execution passed for all 18 files, but bounding-box/volume probes show materially different geometry, so they are not equivalent compression variants. Prior P1 training manifest and target token counts point to CURRENT. The old V1 frozen files remain untouched as RAW_VERBOSE_GT evidence.
