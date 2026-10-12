# P1_NATIVE_RUNTIME_CURVE_AND_OPERATION_LOSS_TRACE_V1

CURRENT_GATE = CHAMFER_NATIVE_BRIDGE_BLOCKED

The native P1 runtime was traced on canonical checkpoint-8000 using GPU 3 in eval/no_grad mode. `edge_clouds` is the native second-stream input and is consumed by `curve_token_injector`; cached curve tokens are loaded from the frozen registry, projected by the original CurveProjector, and injected at embedding level. No `curve_tokens` batch key is expected.

Observed: edge_clouds `[1, 12, 256]` -> projected `[1, 12, 2048]`, NaN=0, Inf=0. The collator generated operation_mask before `compute_loss` (`operation_mask_n=1`); `p1_operation_loss_runtime` then popped it, computed base CE `0.05462271347641945`, op CE `0.0007333449902944267`, and eval total equals base because eval lambda is zero. The prior 0.054622 loss is BASE_MODEL_LOSS / eval total, not a train-time L_total with op lambda.

Native reference model forward: PASS. Canonical source/runtime semantics are recovered. Synthetic CANARY4 bridge and FULL64 runtime were not run because synthetic cases do not have entries in the original dataset/curve-token registry and no compatibility adapter was executed in this read-only trace.

P1_CHAMFER_TRAINING_STARTED = NO
NEXT_ALLOWED_STAGE = BUILD_READ_ONLY_SYNTHETIC_SCHEMA_COMPATIBILITY_ADAPTER
