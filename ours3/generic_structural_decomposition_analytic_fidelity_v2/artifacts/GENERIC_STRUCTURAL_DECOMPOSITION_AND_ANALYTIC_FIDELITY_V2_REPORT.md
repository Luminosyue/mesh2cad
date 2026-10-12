# GENERIC STRUCTURAL DECOMPOSITION AND ANALYTIC FIDELITY V2

CURRENT_GATE=GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_FAIL
PASS=False

## Core Findings

- V1 refined parts: `15`; V2 refined parts: `27`.
- Structural split decisions: `10`.
- Analytic selected: `0`.
- Analytic over-simplification rejects: `15`.
- Negative-space hard rejects: `5`.
- V1/V2 false-positive occupancy: `0.9131260319166229` / `0.8176182235392793`.
- V1/V2 whole Chamfer: `0.029824532695428844` / `inf`.
- V1/V2 source coverage: `0.9303790477215502` / `0.0`.

## Required Answers

1. V1 selected analytic candidates are not accepted solely because they reload as valid BReps; V2 adds representation, occupancy, negative-space, section, topology, and builder-capability checks.
2. Filled-block candidates for sparse/open source regions are rejected by negative-space and occupancy QA.
3. Mixed/sparse structural regions are routed to recursive decomposition and are never sent directly to V6.
4. Single analytic construction is accepted only when all explainability and capability checks pass.
5. Coherent freeform regions remain V6-eligible and are not over-split.
6. No Building-, 5iHumo-, CADPART-, category-, or semantic-role-specific geometry rule is used.
7. NEXT_PRIMARY_BLOCKER=`ANALYTIC_BUILDER_COVERAGE`.
8. MAC next: `NO`.
