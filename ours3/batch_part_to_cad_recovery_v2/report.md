# BATCH_PART_TO_CAD_RECOVERY_V2

Status: **BATCH_PART_TO_CAD_RECOVERY_V2_PASS**. All 48 meaningful Parts across the seven target cases entered the five-slot cascade; 48 were accepted and every new case reached source-area coverage 1.0 with frozen Q1 geometry thresholds. Geometry success and structured CAD success remain separate: the new batch has 7 Q1 cases but only 1 structural-PASS case.

The endpoint probe reached the configured MAC service but received HTTP 403 `Free quota exhausted`; no Part-level MAC run or token-bearing LLM call was made. All 48 Parts record the skip and continue through deterministic/hybrid/freeform/fallback routes.

Best-result preservation selected the new batch only for CASE05, where Q1 coverage improved from 0.9561 to 1.0. Historical bests remain selected for CASE00 (negative-feature topology and hole recall), CASE02 (feature-complete Q1 beats the new low-feature analytic box), CASE03 (6-face analytic control), CASE04 (322-face feature-preserving V2), CASE08 (feature-complete Q1), and CASE09 (8-component, 92-face structured Q1). CASE01/06/07 are referenced unchanged.

The new fallback results are honest surface BReps: a fallback Part may have Q1 geometry while `CAD_STRUCTURE_Q=FAIL`. No old STEP was used as reconstruction geometry, no P3/PhysX rerun was needed, no unrestricted ICP or whole-assembly refit ran, and all historical hashes remained unchanged.
