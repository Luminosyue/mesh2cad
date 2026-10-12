# REAL_MESH to EXACT10K pilot report

The pilot stopped at semantic conversion. Existing Airplane Compact IR was not regenerated or simplified.

| Part | Raw tokens | Compact tokens | EXACT10K target tokens | Full sequence tokens | Dataset | Collator | Execution | STEP | Geometry |
|---|---:|---:|---:|---:|---|---|---|---|---|
| PART_000 | 5607 | 2810 | N/A | N/A | FAIL | FAIL | NOT_RUN | NOT_RUN | NOT_RUN |
| PART_001 | 12917 | 6596 | N/A | N/A | FAIL | FAIL | NOT_RUN | NOT_RUN | NOT_RUN |
| PART_005 | 25106 | 12850 | N/A | N/A | FAIL | FAIL | NOT_RUN | NOT_RUN | NOT_RUN |

PART_000_CONVERSION=FAIL; PART_001_CONVERSION=FAIL; PART_005_CONVERSION=FAIL.
PILOT_EXACT10K_COMPATIBILITY_GATE=FAIL.

Reason: all three parts contain periodic spline sections and ruled loft semantics that cannot be represented losslessly by the frozen Canonical CAD DSL v1 serializer. No fake targets were generated.
