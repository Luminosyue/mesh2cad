# A1/A3/P1 VAL-to-TEST generalization and A1 residual audit

This was a post-hoc read-only audit. P1 VAL success and TEST non-confirmation are both retained.

- A1 is the strongest and most stable curve ablation on final TEST for structural/execution metrics.
- A3 has the highest strict Exact but weaker structural/execution metrics.
- P1's strong VAL improvement did not replicate on TEST; operation-aware all-curve supervision therefore does not provide robust final-test gains.
- The P1 pattern is classified as MULTIFACTOR_GENERALIZATION_FAILURE, with EXECUTION_STABILITY_REGRESSION secondary. Associations with high K, operation count, source and generation completeness are reported without causal claims.
- A1 VAL residual decision: A1_SIZE_STATUS=JUSTIFIED; recommended target=SIZE.

No training, decode, checkpoint selection, TEST retuning, or holdout prediction was performed.
