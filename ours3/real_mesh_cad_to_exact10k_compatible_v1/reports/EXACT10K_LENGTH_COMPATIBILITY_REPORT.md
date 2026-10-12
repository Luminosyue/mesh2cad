# EXACT10K length compatibility report

Frozen EXACT10K train collator distribution for 8,000 examples:
- B0: mean 536, median 275, P95 1822, P99 3338, max 6998
- M2: mean 539, median 278, P95 1825, P99 3341, max 7001
- context limit: 8192; old train truncation count: 0

Direct raw split extraction reproduces B0-style full sequence lengths: min 129, median 275.0, P95 1822.0999999999985, P99 3338.0300000000007, max 6998. Per-sample source mask and supervised target/EOS accounting are in exact10k_audit/sample_dump/SELECTION_SUMMARY.json.

Airplane pilot lengths:

| Part | Raw CadQuery | Compact IR | EXACT10K target | Full sequence | 8192 |
|---|---:|---:|---:|---:|---|
| PART_000 | 5607 | 2810 | N/A | N/A | UNKNOWN |
| PART_001 | 12917 | 6596 | N/A | N/A | UNKNOWN |
| PART_005 | 25106 | 12850 | N/A | N/A | UNKNOWN |

8192_CONTEXT_COMPATIBILITY=UNDETERMINED_BECAUSE_CONVERSION_FAILED. Do not truncate to force a result.
