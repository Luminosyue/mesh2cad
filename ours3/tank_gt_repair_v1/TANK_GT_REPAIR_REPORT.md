# TANK GT REPAIR REPORT

INITIAL_VALID_N=38/45
INITIAL_INVALID_N=7/45

PART_023_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT
PART_028_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT
PART_031_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT
PART_035_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT
PART_037_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT
PART_040_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT
PART_041_ROOT_CAUSE=RESOURCE_TIMEOUT_OR_PARALLEL_EXECUTION_LIMIT

EXECUTOR_BUG_N=0
TIMEOUT_N=7 (initial concurrent run; all passed isolated retry)
GT_INTRINSIC_INVALID_N=0
STEP_EXPORT_BUG_N=0
STEP_READBACK_BUG_N=0
REPAIRED_N=7 (resource policy only; GT frozen)

FINAL_VALID_N=45/45
FINAL_DATA_GATE=PASS

## Frozen data and staged result

Original mesh, target CAD programs, serialized tokens, curve inputs, and surface inputs were preserved under `original_gt/` and hashed in the evidence. The seven initial failures had no reproducible syntax or CAD operation failure when rerun individually. With the same GT and the same executor, a single-process retry using CPU timeout 1900 seconds, 24 GiB address-space limit, and one BLAS/OpenMP thread completed all seven. No GT, denominator, tolerance, or serializer was changed.

Stage A read, Stage B parse, Stage C block execution, Stage D final BRep validity, Stage E STEP export, Stage F STEP readback, and Stage G readback BRep validity passed for all 45 parts in `final_audit.json`.

Training has not started. The next step is the separate P1 Tank all-parts overfit from the recorded shared base checkpoint.
