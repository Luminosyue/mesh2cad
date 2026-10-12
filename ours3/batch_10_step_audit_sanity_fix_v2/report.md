# BATCH_10_STEP_AUDIT_SANITY_FIX_V2

Gate: `BATCH_10_STEP_AUDIT_SANITY_FIX_V2_PASS`

CASE_00 was incorrectly overridden by the external REAL_03 full assembly in generate_per_case_summary.py. Its batch-native latest STEP is the internal partial assembly referenced by the CASE_00 assembly manifest.

The V1 geometry audit compared canonical STEP coordinates directly with source coordinates for cases carrying a CANONICAL_TO_SOURCE ledger. V2 reuses cached tessellations, applies the saved matrix, and uses no ICP.

Targeted equal-count cases are `SAME_TOPOLOGY_DIFFERENT_GEOMETRY`: their topology histograms match, but STEP hashes and vertex-coordinate hashes differ.

Representation quality and geometry fidelity remain separate: CASE_03 is compact but its V1 untransformed geometry score was inaccurate; CASE_05 has high geometric fidelity but remains over-fragmented.
