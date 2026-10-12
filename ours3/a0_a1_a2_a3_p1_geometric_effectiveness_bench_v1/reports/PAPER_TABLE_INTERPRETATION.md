# Paper Table Interpretation

- `IoU` is `OUR_BREP_IOU`, not a paper-compatible IoU unless the target evaluator is later confirmed.
- `Mean CD` and `Med. CD` are `OUR_STANDARDIZED_CD`, using identical OCC tessellation tolerance and deterministic 8192-point surface sampling.
- `GED` is intentionally blank because `GED_STATUS=DEFERRED_UNDEFINED`.
- All five arms are evaluated together on the same VAL1000 IDs with explicit valid N and full-denominator success-weighted IoU.
- Cross-paper numeric comparison is `NO` until dataset, split, normalization, sampling, CD, IoU, and failure handling are independently confirmed identical.
